"""Step 2: windowed NBBO quotes + trades on the sample days (design: ms_common.sample_days / window_plan).

For every (ticker, day) this writes compact aggregates + enriched trades to
  data/microstructure/tick/{T}/{day}_qstats.parquet  one row per 5-min quote sub-window (time-weighted stats)
  data/microstructure/tick/{T}/{day}_shist.parquet   time-weighted spread histogram (half-cent units) per sub-window
  data/microstructure/tick/{T}/{day}_dhist.parquet   histogram of NBBO price-state durations (log bins) per sub-window
  data/microstructure/tick/{T}/{day}_snap.parquet    1-second NBBO snapshots inside every quote window
  data/microstructure/tick/{T}/{day}_trades.parquet  every trade in the trade windows + prevailing NBBO + NBBO mid 60 s / 300 s later
  data/microstructure/tick/{T}/{day}_wmeta.parquet   window list (written last = completion marker)
Raw quote messages are stream-processed page by page and not stored.

Usage: python3 02_tick_windows.py [--phase 1|2|all] [--tickers SOXL,SOXS] [--days 2026-09-25,...]
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from ms_common import (DATA, TICKERS, et_to_utc_ns, fetch_quotes, fetch_trades, get_json, http_stats,  # noqa: E402
                       ns_to_iso, sample_days, window_plan)

TICK = DATA / "tick"
LOGD = DATA / "logs"
LOGD.mkdir(parents=True, exist_ok=True)
NS = 1_000_000_000
DUR_EDGES_US = np.concatenate([[0.0], np.logspace(0, 9, 91)])  # 0, 1 us ... 1000 s (10 bins per decade)
SEED_MAX_AGE_NS = 30 * 60 * NS  # a seed quote older than 30 min is treated as stale (ignored)


def wquantile(v, w, qs):
    m = np.isfinite(v) & (w > 0)
    v, w = v[m], w[m]
    if len(v) == 0:
        return [np.nan] * len(qs)
    o = np.argsort(v, kind="stable")
    v, w = v[o], w[o]
    cw = np.cumsum(w)
    tot = cw[-1]
    return [float(v[min(np.searchsorted(cw, q * tot, side="left"), len(v) - 1)]) for q in qs]


def get_seed(T, start_ns):
    j = get_json(f"/v3/quotes/{T}", {"timestamp.lt": ns_to_iso(start_ns), "limit": 1,
                                     "sort": "timestamp", "order": "desc"})
    r = j.get("results") or []
    if not r:
        return None
    q = r[0]
    return {"t": int(q.get("sip_timestamp", 0)), "bid": q.get("bid_price") or np.nan,
            "ask": q.get("ask_price") or np.nan, "bsz": q.get("bid_size") or 0.0,
            "asz": q.get("ask_size") or 0.0, "bex": q.get("bid_exchange") or 0,
            "aex": q.get("ask_exchange") or 0, "cond": (q.get("conditions") or [0])[0]}


def subwindow_stats(t, st, en, bid, ask, bsz, asz, cond, is_seed, a, b):
    """Time-weighted stats of NBBO states in [a, b). st/en = state start/end (ns)."""
    d = (np.clip(en, a, b) - np.clip(st, a, b)).astype(np.float64) / NS  # seconds
    two = (bid > 0) & (ask > 0)
    spr = np.where(two, ask - bid, np.nan)
    mid = np.where(two, (ask + bid) / 2, np.nan)
    pos = two & (spr > 1e-9)
    locked = two & (np.abs(spr) <= 1e-9)
    crossed = two & (spr < -1e-9)
    Tt = (b - a) / NS
    Tpos = d[pos].sum()
    r = {"T_total": Tt, "T_covered": d.sum(), "T_twosided": d[two].sum(), "T_pos": Tpos,
         "T_locked": d[locked].sum(), "T_crossed": d[crossed].sum()}
    k = np.full(len(t), -999, dtype=np.int64)
    k[pos] = np.rint(spr[pos] / 0.005).astype(np.int64)
    bps = np.where(pos, spr / mid * 1e4, np.nan)
    if Tpos > 0:
        r["tw_spread_c"] = float((d[pos] * spr[pos]).sum() / Tpos * 100)
        r["tw_spread_bps"] = float((d[pos] * bps[pos]).sum() / Tpos)
        r["tw_mid"] = float((d[pos] * mid[pos]).sum() / Tpos)
        r["T_1tick"] = float(d[pos & (k == 2)].sum())
        r["T_halfpenny_spread"] = float(d[pos & (k % 2 == 1)].sum())
        bd, ad = bsz * bid, asz * ask
        for name, v in (("bsz", bsz), ("asz", asz), ("bdol", bd), ("adol", ad)):
            r[f"tw_mean_{name}"] = float((d[pos] * v[pos]).sum() / Tpos)
            r[f"tw_med_{name}"] = wquantile(v[pos], d[pos], [0.5])[0]
        tot = bsz + asz
        r["tw_med_totsz"] = wquantile(tot[pos], d[pos], [0.5])[0]
        q50, q90 = wquantile(spr[pos] * 100, d[pos], [0.5, 0.9])
        r["tw_med_spread_c"], r["tw_p90_spread_c"] = q50, q90
    # message / change counts for messages inside [a, b) (seed excluded)
    inwin = (t >= a) & (t < b) & (~is_seed)
    bi = np.rint(np.nan_to_num(bid) * 10000).astype(np.int64)
    ai = np.rint(np.nan_to_num(ask) * 10000).astype(np.int64)
    bch = np.r_[True, bi[1:] != bi[:-1]]
    ach = np.r_[True, ai[1:] != ai[:-1]]
    sch = np.r_[True, (bsz[1:] != bsz[:-1]) | (asz[1:] != asz[:-1])]
    pch = bch | ach
    r["n_msg"] = int(inwin.sum())
    r["n_px_chg"] = int((pch & inwin).sum())
    r["n_bid_px_chg"] = int((bch & inwin).sum())
    r["n_ask_px_chg"] = int((ach & inwin).sum())
    r["n_any_chg"] = int(((pch | sch) & inwin).sum())
    # sub-penny quote prices (bid or ask not on the $0.01 grid)
    def offgrid(p):
        pp = np.nan_to_num(p)
        return (pp > 0) & (np.abs(pp * 100 - np.rint(pp * 100)) > 1e-6)
    r["n_subpenny_quotes"] = int(((offgrid(bid) | offgrid(ask)) & inwin).sum())
    r["n_luld_quotes"] = int(((cond == 43) & inwin).sum())
    r["n_nonregular_quotes"] = int(((cond != 1) & inwin).sum())
    # durations of NBBO price states (complete states only: begin and end at a price change inside [a, b))
    tc = t[pch & inwin]
    durs_us = np.diff(tc).astype(np.float64) / 1000.0 if len(tc) > 1 else np.array([])
    r["n_states"] = int(len(durs_us))
    r["state_dur_med_ms"] = float(np.median(durs_us) / 1000) if len(durs_us) else np.nan
    r["state_dur_mean_ms"] = float(np.mean(durs_us) / 1000) if len(durs_us) else np.nan
    # spread histogram
    hist = None
    if Tpos > 0:
        kk = k[pos]
        dd = d[pos]
        bb = bps[pos]
        uk, inv = np.unique(kk, return_inverse=True)
        tsum = np.bincount(inv, weights=dd)
        bsum = np.bincount(inv, weights=dd * bb)
        hist = pd.DataFrame({"k_halfc": uk, "time_s": tsum, "time_x_bps": bsum})
        hist = hist[hist.time_s > 0]
    dh = None
    if len(durs_us):
        cnt, _ = np.histogram(durs_us, bins=DUR_EDGES_US)
        nz = np.nonzero(cnt)[0]
        dh = pd.DataFrame({"bin": nz, "count": cnt[nz]})
    return r, hist, dh


def process_unit(T: str, day: str, force: bool = False) -> str:
    odir = TICK / T
    odir.mkdir(parents=True, exist_ok=True)
    marker = odir / f"{day}_wmeta.parquet"
    if marker.exists() and not force:
        return f"{T} {day} cached"
    t0 = time.time()
    base = et_to_utc_ns(day, "00:00")
    Q, H, D, S, TR, WM = [], [], [], [], [], []
    nq_total = nt_total = 0
    for w in window_plan(day):
        wid = w["wid"]
        meta = {"wid": wid, "kind": w["kind"], "stratum_start": w["stratum"][0], "stratum_end": w["stratum"][1],
                "q0": w["q0"], "q1": w["q1"], "t0": w["t0"], "t1": w["t1"]}
        tq = None
        if w["q0"] is not None:
            qs = base + int(round(w["q0"] * 60 * NS))
            qe = base + int(round(w["q1"] * 60 * NS))
            seed = get_seed(T, qs)
            q = fetch_quotes(T, qs, qe)
            nq_total += len(q)
            meta["n_quotes"] = len(q)
            meta["seed_age_s"] = (qs - seed["t"]) / NS if seed else np.nan
            use_seed = seed is not None and (qs - seed["t"]) <= SEED_MAX_AGE_NS
            if use_seed:
                sd = pd.DataFrame([seed])[["t", "bid", "ask", "bsz", "asz", "bex", "aex", "cond"]]
                q = pd.concat([sd, q], ignore_index=True)
            is_seed = np.zeros(len(q), dtype=bool)
            if use_seed:
                is_seed[0] = True
            t = q["t"].to_numpy(np.int64)
            bid = q["bid"].to_numpy(np.float64)
            ask = q["ask"].to_numpy(np.float64)
            bsz = q["bsz"].to_numpy(np.float64)
            asz = q["asz"].to_numpy(np.float64)
            cond = q["cond"].to_numpy(np.int64)
            st = np.maximum(t, qs)
            en = np.append(t[1:], qe) if len(t) else np.array([], dtype=np.int64)
            en = np.maximum(en, st)
            tq = (t, bid, ask, bsz, asz, qe)
            nsub = int(round((w["q1"] - w["q0"]) / 5))
            for j in range(nsub):
                a = qs + j * 5 * 60 * NS
                b = a + 5 * 60 * NS
                sub0 = w["q0"] + 5 * j
                if len(t):
                    r, hist, dh = subwindow_stats(t, st, en, bid, ask, bsz, asz, cond, is_seed, a, b)
                else:
                    r, hist, dh = {"T_total": 300.0, "T_covered": 0.0, "n_msg": 0}, None, None
                r.update({"wid": wid, "kind": w["kind"], "stratum_start": w["stratum"][0],
                          "stratum_end": w["stratum"][1], "sub_start": sub0, "sub_end": sub0 + 5})
                Q.append(r)
                for df, L in ((hist, H), (dh, D)):
                    if df is not None and len(df):
                        df = df.copy()
                        df["wid"] = wid
                        df["sub_start"] = sub0
                        L.append(df)
            # 1-second snapshots of the NBBO state
            if len(t):
                grid = qs + np.arange(0, int((qe - qs) / NS) + 1, dtype=np.int64) * NS
                idx = np.searchsorted(t, grid, side="right") - 1
                ok = idx >= 0
                ii = np.where(ok, idx, 0)
                snap = pd.DataFrame({"wid": wid, "sec": np.arange(len(grid), dtype=np.int32),
                                     "bid": np.where(ok, bid[ii], np.nan), "ask": np.where(ok, ask[ii], np.nan),
                                     "bsz": np.where(ok, bsz[ii], np.nan).astype(np.float32),
                                     "asz": np.where(ok, asz[ii], np.nan).astype(np.float32)})
                S.append(snap)
        # trades
        ts = base + int(round(w["t0"] * 60 * NS))
        te = base + int(round(w["t1"] * 60 * NS))
        tr = fetch_trades(T, ts, te)
        nt_total += len(tr)
        meta["n_trades"] = len(tr)
        if len(tr):
            tt = tr["t"].to_numpy(np.int64)
            n = len(tr)
            qb = np.full(n, np.nan); qa = np.full(n, np.nan); qbs = np.full(n, np.nan); qas = np.full(n, np.nan)
            qage = np.full(n, -1, dtype=np.int64); m60 = np.full(n, np.nan); m300 = np.full(n, np.nan)
            if tq is not None and len(tq[0]):
                t, bid, ask, bsz, asz, qe = tq
                idx = np.searchsorted(t, tt, side="left") - 1  # quote strictly before the trade
                ok = idx >= 0
                ii = np.where(ok, idx, 0)
                qb = np.where(ok, bid[ii], np.nan); qa = np.where(ok, ask[ii], np.nan)
                qbs = np.where(ok, bsz[ii], np.nan); qas = np.where(ok, asz[ii], np.nan)
                qage = np.where(ok, tt - t[ii], -1)
                for H_ns, arr in ((60 * NS, m60), (300 * NS, m300)):
                    tf = tt + H_ns
                    j2 = np.searchsorted(t, tf, side="right") - 1
                    ok2 = (j2 >= 0) & (tf < qe)
                    jj = np.where(ok2, j2, 0)
                    mid_f = (bid[jj] + ask[jj]) / 2
                    arr[:] = np.where(ok2, mid_f, np.nan)
            tr = tr.assign(wid=np.int16(wid), bid=qb, ask=qa, bsz=qbs.astype(np.float32), asz=qas.astype(np.float32),
                           qage_ns=qage, mid60=m60, mid300=m300)
            TR.append(tr)
        WM.append(meta)
    # write
    def wr(frames, name):
        if frames:
            df = pd.concat(frames, ignore_index=True) if isinstance(frames, list) and isinstance(frames[0], pd.DataFrame) else pd.DataFrame(frames)
        else:
            df = pd.DataFrame()
        tmp = odir / f".{day}_{name}.tmp.parquet"
        df.to_parquet(tmp, index=False, compression="zstd")
        tmp.rename(odir / f"{day}_{name}.parquet")
    wr(Q, "qstats"); wr(H, "shist"); wr(D, "dhist"); wr(S, "snap"); wr(TR, "trades"); wr(WM, "wmeta")
    return f"{T} {day} quotes={nq_total} trades={nt_total} {time.time() - t0:.0f}s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    ap.add_argument("--tickers", default=",".join(TICKERS))
    ap.add_argument("--days", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    sd = sample_days()
    if a.days:
        days = a.days.split(",")
    elif a.phase == "all":
        days = sd.day.tolist()
    else:
        days = sd[sd.phase == int(a.phase)].day.tolist()
    tickers = a.tickers.split(",")
    units = [(T, d) for d in days for T in tickers]
    log = open(LOGD / "02_tick_windows.log", "a")
    print(f"{len(units)} units", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(process_unit, T, d, a.force): (T, d) for T, d in units}
        done = 0
        for f in as_completed(futs):
            done += 1
            try:
                msg = f.result()
            except Exception as e:  # keep going; failures are logged and can be re-run
                msg = f"FAILED {futs[f]}: {e!r}\n{traceback.format_exc()}"
            line = f"[{done}/{len(units)} {time.time() - t0:.0f}s] {msg} | {http_stats()}"
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()


if __name__ == "__main__":
    main()
    import os
    os._exit(0)
