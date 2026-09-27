"""Step 3: full-session (04:00-20:00 ET) NBBO quotes + trades for SOXL and SOXS on selected days.

Used for (a) exact whole-day statistics for the two focus tickers and (b) validating the windowed sampling of step 2.
Writes to data/microstructure/fullday/{T}/{day}_{minute|bucket|shist|dhist|trades}.parquet
Usage: python3 03_fullday.py [--tickers SOXL,SOXS] [--days ...] [--workers 2]
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
from ms_common import DATA, et_to_utc_ns, fetch_quotes, fetch_trades, http_stats  # noqa: E402

NS = 1_000_000_000
FD = DATA / "fullday"
LOGD = DATA / "logs"
DAYS = ["2022-09-14", "2023-09-13", "2024-09-12", "2025-08-25",
        "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25"]
DUR_EDGES_US = np.concatenate([[0.0], np.logspace(0, 9, 91)])
# buckets: pre-market strata, 13 RTH half hours, post-market strata (minutes after ET midnight)
BUCKETS = [(240, 420), (420, 480), (480, 540), (540, 570)] + [(570 + 30 * i, 600 + 30 * i) for i in range(13)] + \
          [(960, 1020), (1020, 1080), (1080, 1200)]


def wquantile(v, w, qs):
    m = np.isfinite(v) & (w > 0)
    v, w = v[m], w[m]
    if len(v) == 0:
        return [np.nan] * len(qs)
    o = np.argsort(v, kind="stable")
    v, w = v[o], w[o]
    cw = np.cumsum(w)
    return [float(v[min(np.searchsorted(cw, q * cw[-1], side="left"), len(v) - 1)]) for q in qs]


def fetch_day_quotes(T, day):
    parts = []
    for h in range(4, 20):
        s = et_to_utc_ns(day, f"{h:02d}:00")
        parts.append(fetch_quotes(T, s, s + 3600 * NS))
    q = pd.concat([p for p in parts if len(p)], ignore_index=True)
    return q


def fetch_day_trades(T, day):
    parts = []
    for h in range(4, 20):
        s = et_to_utc_ns(day, f"{h:02d}:00")
        parts.append(fetch_trades(T, s, s + 3600 * NS))
    return pd.concat([p for p in parts if len(p)], ignore_index=True)


def process(T, day, force=False):
    odir = FD / T
    odir.mkdir(parents=True, exist_ok=True)
    if (odir / f"{day}_trades.parquet").exists() and not force:
        return f"{T} {day} cached"
    t0 = time.time()
    base = et_to_utc_ns(day, "00:00")
    q = fetch_day_quotes(T, day)
    t = q.t.to_numpy(np.int64)
    bid = q.bid.to_numpy(float); ask = q.ask.to_numpy(float)
    bsz = q.bsz.to_numpy(float); asz = q.asz.to_numpy(float)
    # change flags on the real message stream
    bi = np.rint(np.nan_to_num(bid) * 1e4).astype(np.int64); ai = np.rint(np.nan_to_num(ask) * 1e4).astype(np.int64)
    pch = np.r_[True, (bi[1:] != bi[:-1]) | (ai[1:] != ai[:-1])]
    # insert synthetic continuation rows at every minute boundary so each state lies inside one minute
    s_all, e_all = base + 240 * 60 * NS, base + 1200 * 60 * NS
    grid = base + np.arange(240, 1201, dtype=np.int64) * 60 * NS
    gi = np.searchsorted(t, grid, side="right") - 1
    ok = gi >= 0
    gi2 = np.where(ok, gi, 0)
    tt = np.r_[t, grid[ok]]
    B = np.r_[bid, bid[gi2][ok]]; A = np.r_[ask, ask[gi2][ok]]
    BS = np.r_[bsz, bsz[gi2][ok]]; AS = np.r_[asz, asz[gi2][ok]]
    real = np.r_[np.ones(len(t), bool), np.zeros(ok.sum(), bool)]
    PCH = np.r_[pch, np.zeros(ok.sum(), bool)]
    o = np.lexsort((real, tt))  # synthetic row first when timestamps tie
    tt, B, A, BS, AS, real, PCH = tt[o], B[o], A[o], BS[o], AS[o], real[o], PCH[o]
    en = np.r_[tt[1:], e_all]
    d = (np.clip(en, s_all, e_all) - np.clip(tt, s_all, e_all)).astype(float) / NS
    minute = ((np.clip(tt, s_all, e_all - 1) - base) // (60 * NS)).astype(np.int64)
    two = (B > 0) & (A > 0)
    spr = np.where(two, A - B, np.nan)
    mid = np.where(two, (A + B) / 2, np.nan)
    pos = two & (spr > 1e-9)
    k = np.where(pos, np.rint(np.nan_to_num(spr) / 0.005), -999).astype(np.int64)
    bps = np.where(pos, spr / mid * 1e4, np.nan)
    M = 1200
    def bc(w):
        return np.bincount(minute, weights=w, minlength=M)[240:1200]
    dp = np.where(pos, d, 0.0)
    mins = pd.DataFrame({
        "minute": np.arange(240, 1200),
        "T_cov": bc(d), "T_pos": bc(dp),
        "T_locked": bc(np.where(two & (np.abs(np.nan_to_num(spr)) <= 1e-9), d, 0.0)),
        "T_crossed": bc(np.where(two & (np.nan_to_num(spr) < -1e-9), d, 0.0)),
        "T_1tick": bc(np.where(pos & (k == 2), d, 0.0)),
        "sd_spread_c": bc(dp * np.nan_to_num(spr) * 100), "sd_bps": bc(dp * np.nan_to_num(bps)),
        "sd_mid": bc(dp * np.nan_to_num(mid)),
        "sd_bsz": bc(dp * BS), "sd_asz": bc(dp * AS), "sd_bdol": bc(dp * BS * np.nan_to_num(B)),
        "sd_adol": bc(dp * AS * np.nan_to_num(A)),
        "n_msg": bc(real.astype(float)), "n_px_chg": bc((real & PCH).astype(float)),
    })
    # per-bucket spread histogram, depth quantiles, price-state durations
    SH, BK, DH = [], [], []
    tch = t[pch]
    for (a, b) in BUCKETS:
        sel = (minute >= a) & (minute < b) & pos & (d > 0)
        if sel.any():
            uk, inv = np.unique(k[sel], return_inverse=True)
            SH.append(pd.DataFrame({"b0": a, "b1": b, "k_halfc": uk, "time_s": np.bincount(inv, weights=d[sel]),
                                    "time_x_bps": np.bincount(inv, weights=d[sel] * bps[sel])}))
            r = {"b0": a, "b1": b, "T_pos": d[sel].sum()}
            for name, v in (("bsz", BS), ("asz", AS), ("bdol", BS * B), ("adol", AS * A)):
                r[f"tw_med_{name}"] = wquantile(v[sel], d[sel], [0.5])[0]
                r[f"tw_mean_{name}"] = float((v[sel] * d[sel]).sum() / d[sel].sum())
            BK.append(r)
        lo, hi = base + a * 60 * NS, base + b * 60 * NS
        tc = tch[(tch >= lo) & (tch < hi)]
        if len(tc) > 1:
            cnt, _ = np.histogram(np.diff(tc) / 1000.0, bins=DUR_EDGES_US)
            nz = np.nonzero(cnt)[0]
            DH.append(pd.DataFrame({"b0": a, "b1": b, "bin": nz, "count": cnt[nz]}))
    # trades with prevailing NBBO (strictly before) and future mids (+60 s, +300 s)
    tr = fetch_day_trades(T, day)
    ttr = tr.t.to_numpy(np.int64)
    idx = np.searchsorted(t, ttr, side="left") - 1
    okq = idx >= 0
    ii = np.where(okq, idx, 0)
    tr["bid"] = np.where(okq, bid[ii], np.nan); tr["ask"] = np.where(okq, ask[ii], np.nan)
    tr["bsz"] = np.where(okq, bsz[ii], np.nan).astype(np.float32); tr["asz"] = np.where(okq, asz[ii], np.nan).astype(np.float32)
    tr["qage_ns"] = np.where(okq, ttr - t[ii], -1)
    for H, name in ((60 * NS, "mid60"), (300 * NS, "mid300")):
        tf = ttr + H
        j = np.searchsorted(t, tf, side="right") - 1
        ok2 = (j >= 0) & (tf < e_all)
        jj = np.where(ok2, j, 0)
        tr[name] = np.where(ok2, (bid[jj] + ask[jj]) / 2, np.nan)
    for df, name in ((mins, "minute"), (pd.DataFrame(BK), "bucket"), (pd.concat(SH, ignore_index=True), "shist"),
                     (pd.concat(DH, ignore_index=True) if DH else pd.DataFrame(), "dhist"), (tr, "trades")):
        tmp = odir / f".{day}_{name}.tmp.parquet"
        df.to_parquet(tmp, index=False, compression="zstd")
        tmp.rename(odir / f"{day}_{name}.parquet")
    return f"{T} {day} quotes={len(q)} trades={len(tr)} {time.time() - t0:.0f}s"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", default="SOXL,SOXS")
    ap.add_argument("--days", default=",".join(DAYS))
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    units = [(T, d) for d in a.days.split(",") for T in a.tickers.split(",")]
    log = open(LOGD / "03_fullday.log", "a")
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(process, T, d): (T, d) for T, d in units}
        for f in as_completed(futs):
            try:
                msg = f.result()
            except Exception as e:
                msg = f"FAILED {futs[f]}: {e!r}\n{traceback.format_exc()}"
            line = f"[{time.time() - t0:.0f}s] {msg} | {http_stats()}"
            print(line, flush=True)
            log.write(line + "\n"); log.flush()
    import os
    os._exit(0)
