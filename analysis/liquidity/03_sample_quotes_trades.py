"""Step 3 - windowed NBBO quote + trade sampling -> compact per-minute aggregates.

For each (ticker, day) we pull /v3/quotes and /v3/trades for a set of ET windows,
stream-convert pages to numpy, and keep ONLY aggregates (raw pages are never stored):

  quotes_min   : per-minute time-weighted NBBO stats (spread $, spread bps, sizes, $ depth,
                 locked/crossed/one-sided time, half-penny counts, LULD-pause quote flags)
  spread_hist  : per-minute {spread in $0.001 units -> time (ns)}  (for exact medians/p90/%1-tick)
  trades_min   : per-minute x venue(lit/TRF) trade stats: volume, odd lots, effective half-spread,
                 Lee-Ready signing, realized half-spread & price impact at +60s/+300s
  effhs_hist   : per-window x venue {|p-mid| in $0.00001 units -> n, shares, $}
  size_hist    : per-window x venue trade-size histogram

Modes:
  sample  : RTH 10-min windows starting 09:30,10:00,...,15:30 and 15:50 (->16:00);
            pre-market 04:30,06:00,07:00,08:00,09:00,09:20; after-hours 16:00,16:30,17:00,18:00,19:00,19:50
  fullday : consecutive 30-min chunks 04:00-20:00 (SOXL/SOXS on a few days)

Usage: python 03_sample_quotes_trades.py sample   |   python 03_sample_quotes_trades.py fullday
Outputs go to data/liquidity/agg/<mode>/ (gitignored); day list -> output/sample_days.csv
"""
from __future__ import annotations

import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from common import ALL, DATA, ET, OUT, TICKERS, aggs, et_to_ns, get_json, paginate, wquantile

NS = 1_000_000_000
MIN = 60 * NS
EXCL_EFF = {2, 7, 8, 9, 10, 13, 15, 16, 17, 18, 19, 20, 21, 22, 25, 28, 29, 30, 31, 32, 33, 35, 38, 52, 53, 55}
NONVOL = {15, 16, 38}
SIZE_EDGES = np.array([0, 1, 10, 40, 100, 101, 200, 500, 1000, 5000, 10000, np.inf])
SIZE_LABELS = ["<1", "1-9", "10-39", "40-99", "100", "101-199", "200-499", "500-999", "1000-4999", "5000-9999", ">=10000"]
HORIZONS = (60, 300)

RTH = ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "15:50"]
PRE = ["04:30", "06:00", "07:00", "08:00", "09:00", "09:20"]
POST = ["16:00", "16:30", "17:00", "18:00", "19:00", "19:50"]


def windows_for(mode: str):
    if mode == "sample":
        w = [(h, 10) for h in PRE + RTH + POST]
    else:  # fullday: 30-minute chunks 04:00-20:00
        w = []
        t = pd.Timestamp("2000-01-01 04:00")
        while t < pd.Timestamp("2000-01-01 20:00"):
            w.append((t.strftime("%H:%M"), 30))
            t += pd.Timedelta(minutes=30)
    return w


# ------------------------------------------------------------------ fetch helpers
def fetch_quotes(t: str, w0: int, w1: int):
    ts, bp, ap, bs, as_, c43, c16 = [], [], [], [], [], [], []
    for page in paginate(f"/v3/quotes/{t}", {"timestamp.gte": w0, "timestamp.lt": w1, "limit": 50000,
                                             "sort": "timestamp", "order": "asc"}):
        n = len(page)
        if not n:
            continue
        ts.append(np.fromiter((q["sip_timestamp"] for q in page), np.int64, n))
        bp.append(np.fromiter((q.get("bid_price", 0.0) for q in page), np.float64, n))
        ap.append(np.fromiter((q.get("ask_price", 0.0) for q in page), np.float64, n))
        bs.append(np.fromiter((q.get("bid_size", 0) for q in page), np.float64, n))
        as_.append(np.fromiter((q.get("ask_size", 0) for q in page), np.float64, n))
        c43.append(np.fromiter((43 in q.get("conditions", ()) for q in page), bool, n))
        c16.append(np.fromiter((16 in q.get("conditions", ()) for q in page), bool, n))
        del page
    if not ts:
        z = np.zeros(0)
        return dict(ts=np.zeros(0, np.int64), bid=z, ask=z, bsz=z, asz=z, c43=np.zeros(0, bool), c16=np.zeros(0, bool))
    return dict(ts=np.concatenate(ts), bid=np.concatenate(bp), ask=np.concatenate(ap), bsz=np.concatenate(bs),
                asz=np.concatenate(as_), c43=np.concatenate(c43), c16=np.concatenate(c16))


def prevailing_quote(t: str, w0: int, day_start: int):
    j = get_json(f"/v3/quotes/{t}", {"timestamp.lt": w0, "order": "desc", "sort": "timestamp", "limit": 1})
    r = (j.get("results") or [None])[0]
    if not r or r["sip_timestamp"] < day_start:
        return None
    return r


def fetch_trades(t: str, w0: int, w1: int):
    cols = {k: [] for k in ("ts", "pts", "px", "sz", "ex", "excl", "nonvol", "c37", "c14")}
    for page in paginate(f"/v3/trades/{t}", {"timestamp.gte": w0, "timestamp.lt": w1, "limit": 50000,
                                             "sort": "timestamp", "order": "asc"}):
        n = len(page)
        if not n:
            continue
        cols["ts"].append(np.fromiter((q["sip_timestamp"] for q in page), np.int64, n))
        cols["pts"].append(np.fromiter((q.get("participant_timestamp", q["sip_timestamp"]) for q in page), np.int64, n))
        cols["px"].append(np.fromiter((q.get("price", 0.0) for q in page), np.float64, n))
        cols["sz"].append(np.fromiter((float(q["decimal_size"]) if "decimal_size" in q else q.get("size", 0) for q in page), np.float64, n))
        cols["ex"].append(np.fromiter((q.get("exchange", 0) for q in page), np.int16, n))
        conds = [q.get("conditions", ()) for q in page]
        cols["excl"].append(np.fromiter((bool(EXCL_EFF.intersection(c)) for c in conds), bool, n))
        cols["nonvol"].append(np.fromiter((bool(NONVOL.intersection(c)) for c in conds), bool, n))
        cols["c37"].append(np.fromiter((37 in c for c in conds), bool, n))
        cols["c14"].append(np.fromiter((14 in c for c in conds), bool, n))
        del page, conds
    if not cols["ts"]:
        return None
    return {k: np.concatenate(v) for k, v in cols.items()}


# ------------------------------------------------------------------ aggregation
def quote_aggs(q, W0, W1, meta):
    """Exact time-weighting on breakpoints = quote updates U minute boundaries."""
    qts = q["ts"]
    mb = np.arange(W0, W1, MIN, dtype=np.int64)
    inwin = (qts >= W0) & (qts < W1)
    bp = np.union1d(qts[inwin], mb)
    ends = np.append(bp[1:], W1)
    dur = (ends - bp).astype(np.float64)
    idx = np.searchsorted(qts, bp, side="right") - 1
    has = idx >= 0
    idx = np.where(has, idx, 0)
    b, a = q["bid"][idx], q["ask"][idx]
    bs, as_ = q["bsz"][idx], q["asz"][idx]
    minute = ((bp - W0) // MIN).astype(np.int64)
    nmin = len(mb)
    one = has & ((b <= 0) | (a <= 0))
    crossed = has & ~one & (a < b - 1e-9)
    locked = has & ~one & (np.abs(a - b) <= 1e-9)
    valid = has & ~one & (a > b + 1e-9)
    mid = (a + b) / 2
    sp = a - b
    sp_bps = np.where(valid, sp / np.where(mid > 0, mid, 1) * 1e4, 0)

    def bc(wts, mask):
        return np.bincount(minute[mask], weights=wts[mask], minlength=nmin)

    rows = []
    d_all = np.bincount(minute, weights=dur, minlength=nmin)
    d_valid = bc(dur, valid)
    agg = dict(
        dur_all=d_all, dur_valid=d_valid, dur_locked=bc(dur, locked), dur_crossed=bc(dur, crossed),
        dur_onesided=bc(dur, one), dur_noquote=bc(dur, ~has),
        sum_sp=bc(sp * dur, valid), sum_sp_bps=bc(sp_bps * dur, valid), sum_mid=bc(mid * dur, valid),
        sum_bsz=bc(bs * dur, valid), sum_asz=bc(as_ * dur, valid),
        sum_bdol=bc(bs * b * dur, valid), sum_adol=bc(as_ * a * dur, valid),
    )
    # counts of quote messages per minute + tick-grid checks
    qm = ((qts[inwin] - W0) // MIN).astype(np.int64)
    qb, qa = q["bid"][inwin], q["ask"][inwin]
    bmod = np.round(qb * 10000).astype(np.int64) % 100
    amod = np.round(qa * 10000).astype(np.int64) % 100
    half = ((bmod == 50) & (qb >= 1)) | ((amod == 50) & (qa >= 1))
    other = (((bmod != 0) & (bmod != 50)) & (qb >= 1)) | (((amod != 0) & (amod != 50)) & (qa >= 1))
    agg["n_quotes"] = np.bincount(qm, minlength=nmin).astype(float)
    agg["n_halfpenny"] = np.bincount(qm, weights=half.astype(float), minlength=nmin)
    agg["n_othersub"] = np.bincount(qm, weights=other.astype(float), minlength=nmin)
    agg["n_c43"] = np.bincount(qm, weights=q["c43"][inwin].astype(float), minlength=nmin)
    agg["n_c16"] = np.bincount(qm, weights=q["c16"][inwin].astype(float), minlength=nmin)
    # per-minute exact time-weighted medians / p10 / p90 of size & $ depth
    med = {k: np.full(nmin, np.nan) for k in ("med_bsz", "med_asz", "med_mindepth", "med_bdol", "med_adol", "p10_mindepth", "med_sp_bps")}
    for m in range(nmin):
        mk = valid & (minute == m)
        if not mk.any():
            continue
        w = dur[mk]
        med["med_bsz"][m] = wquantile(bs[mk], w, [0.5])[0]
        med["med_asz"][m] = wquantile(as_[mk], w, [0.5])[0]
        md = np.minimum(bs[mk], as_[mk])
        med["med_mindepth"][m], med["p10_mindepth"][m] = wquantile(md, w, [0.5, 0.1])
        med["med_bdol"][m] = wquantile(bs[mk] * b[mk], w, [0.5])[0]
        med["med_adol"][m] = wquantile(as_[mk] * a[mk], w, [0.5])[0]
        med["med_sp_bps"][m] = wquantile(sp_bps[mk], w, [0.5])[0]
    agg.update(med)
    qdf = pd.DataFrame(agg)
    qdf.insert(0, "minute", [pd.Timestamp(x, tz="UTC").tz_convert(ET).strftime("%H:%M") for x in mb])
    # spread histogram (valid only), $0.001 units
    smil = np.round(sp[valid] * 1000).astype(np.int64)
    key = minute[valid] * 1_000_000 + smil
    uk, inv = np.unique(key, return_inverse=True)
    hdur = np.bincount(inv, weights=dur[valid])
    hist = pd.DataFrame({"minute_idx": uk // 1_000_000, "spread_milli": uk % 1_000_000, "dur": hdur})
    hist["minute"] = qdf["minute"].values[hist["minute_idx"].values]
    return qdf, hist.drop(columns="minute_idx")


def trade_aggs(tr, q, W0, W1, meta):
    rl = meta["round_lot"]
    ts, px, sz = tr["ts"], tr["px"], tr["sz"]
    nmin = int((W1 - W0) // MIN)
    minute = np.clip(((ts - W0) // MIN).astype(np.int64), 0, nmin - 1)
    venue = np.where(tr["ex"] == 4, 1, 0)  # 1 = FINRA TRF (off-exchange), 0 = lit exchange
    usd = px * sz
    vol_ok = ~tr["nonvol"] & (px > 0) & (sz > 0)
    # effective-spread sample
    eff_ok = vol_ok & ~tr["excl"]
    qts = q["ts"]
    j = np.searchsorted(qts, ts, side="left") - 1  # quote strictly before the trade (sip_timestamp)
    jv = j >= 0
    j0 = np.where(jv, j, 0)
    b, a = q["bid"][j0], q["ask"][j0]
    qok = jv & (b > 0) & (a >= b - 1e-9)
    m = (a + b) / 2
    eff = eff_ok & qok
    dev = px - m
    ehs_bps = np.where(eff, np.abs(dev) / np.where(m > 0, m, 1) * 1e4, 0)
    ehs_c = np.where(eff, np.abs(dev) * 100, 0)
    qhs_bps = np.where(eff, (a - b) / 2 / np.where(m > 0, m, 1) * 1e4, 0)
    tol = 1e-6
    at_mid = eff & (np.abs(dev) <= tol)
    at_q = eff & ((np.abs(px - b) <= tol) | (np.abs(px - a) <= tol)) & ~at_mid
    outside = eff & ((px < b - tol) | (px > a + tol))
    inside = eff & ~at_mid & ~at_q & ~outside
    # Lee-Ready: quote rule, tick test for midpoint trades (previous distinct price among eff trades)
    d = np.zeros(len(ts))
    d[eff] = np.sign(dev[eff])
    if eff.any():
        pe = pd.Series(px[eff])
        tick = np.sign(pe.diff().replace(0, np.nan).ffill().fillna(0).values)
        de = d[eff]
        de = np.where(np.abs(dev[eff]) <= tol, tick, de)
        d[eff] = de
    signed = eff & (d != 0)
    # alt effective spread using participant_timestamp
    j2 = np.searchsorted(qts, tr["pts"], side="left") - 1
    j2v = j2 >= 0
    j20 = np.where(j2v, j2, 0)
    b2, a2 = q["bid"][j20], q["ask"][j20]
    ok2 = eff_ok & j2v & (b2 > 0) & (a2 >= b2 - 1e-9)
    m2 = (a2 + b2) / 2
    ehs_alt = np.where(ok2, np.abs(px - m2) / np.where(m2 > 0, m2, 1) * 1e4, 0)
    # realized spread / price impact
    hz = {}
    for h in HORIZONS:
        th = ts + h * NS
        k = np.searchsorted(qts, th, side="right") - 1
        kv = (th < W1) & (k >= 0)
        k0 = np.where(kv, k, 0)
        bh, ah = q["bid"][k0], q["ask"][k0]
        okh = signed & kv & (bh > 0) & (ah >= bh - 1e-9)
        mh = (ah + bh) / 2
        mm = np.where(m > 0, m, 1)
        hz[h] = dict(ok=okh, es=np.where(okh, d * dev / mm * 1e4, 0), rs=np.where(okh, d * (px - mh) / mm * 1e4, 0),
                     pi=np.where(okh, d * (mh - m) / mm * 1e4, 0))
    grp = minute * 2 + venue
    G = nmin * 2

    def s(wts, mask):
        return np.bincount(grp[mask], weights=wts[mask], minlength=G)

    oddl = vol_ok & (sz < rl)
    one = np.ones(len(ts))
    out = dict(
        n_all=s(one, vol_ok), sh_all=s(sz, vol_ok), usd_all=s(usd, vol_ok),
        n_odd=s(one, oddl), sh_odd=s(sz, oddl), n_c37=s(one, vol_ok & tr["c37"]), sh_c37=s(sz, vol_ok & tr["c37"]),
        n_iso=s(one, vol_ok & tr["c14"]), sh_iso=s(sz, vol_ok & tr["c14"]),
        n_eff=s(one, eff), sh_eff=s(sz, eff), usd_eff=s(usd, eff),
        sum_ehs_bps=s(ehs_bps, eff), sum_ehs_bps_usd=s(ehs_bps * usd, eff),
        sum_ehs_c=s(ehs_c, eff), sum_ehs_c_sh=s(ehs_c * sz, eff),
        sum_qhs_bps=s(qhs_bps, eff), sum_qhs_bps_usd=s(qhs_bps * usd, eff),
        n_mid=s(one, at_mid), n_inside=s(one, inside), n_atq=s(one, at_q), n_outside=s(one, outside),
        usd_mid=s(usd, at_mid), usd_inside=s(usd, inside), usd_atq=s(usd, at_q), usd_outside=s(usd, outside),
        n_buy=s(one, eff & (d > 0)), n_sell=s(one, eff & (d < 0)), sh_buy=s(sz, eff & (d > 0)), sh_sell=s(sz, eff & (d < 0)),
        n_alt=s(one, ok2), sum_ehs_alt_bps=s(ehs_alt, ok2),
    )
    for h in HORIZONS:
        z = hz[h]
        out[f"n_h{h}"] = s(one, z["ok"])
        out[f"usd_h{h}"] = s(usd, z["ok"])
        for nm in ("es", "rs", "pi"):
            out[f"sum_{nm}{h}"] = s(z[nm], z["ok"])
            out[f"sum_{nm}{h}_usd"] = s(z[nm] * usd, z["ok"])
    tdf = pd.DataFrame(out)
    tdf.insert(0, "venue", np.tile(["lit", "trf"], nmin))
    tdf.insert(0, "minute", np.repeat([pd.Timestamp(W0 + i * MIN, tz="UTC").tz_convert(ET).strftime("%H:%M") for i in range(nmin)], 2))
    tdf = tdf[tdf["n_all"] > 0]
    # per-window histograms
    ev = np.round(np.abs(dev[eff]) * 1e5).astype(np.int64)
    key = venue[eff] * 10**9 + ev
    uk, inv = np.unique(key, return_inverse=True)
    eh = pd.DataFrame({"venue": np.where(uk // 10**9 == 1, "trf", "lit"), "absdev_1e5": uk % 10**9,
                       "n": np.bincount(inv), "sh": np.bincount(inv, weights=sz[eff]),
                       "usd": np.bincount(inv, weights=usd[eff]),
                       "sum_mid_usd": np.bincount(inv, weights=m[eff] * usd[eff])})
    sb = np.searchsorted(SIZE_EDGES, sz[vol_ok], side="right") - 1
    key = venue[vol_ok] * 100 + sb
    uk, inv = np.unique(key, return_inverse=True)
    sh = pd.DataFrame({"venue": np.where(uk // 100 == 1, "trf", "lit"), "size_bin": [SIZE_LABELS[i] for i in uk % 100],
                       "n": np.bincount(inv), "sh": np.bincount(inv, weights=sz[vol_ok])})
    return tdf, eh, sh


def process(task):
    t, day, mode = task
    outdir = DATA / "agg" / mode
    outdir.mkdir(parents=True, exist_ok=True)
    stem = outdir / f"{t}_{day}"
    if (stem.parent / (stem.name + "_quotes_min.parquet")).exists():
        return t, day, "cached", 0, 0, 0.0
    t0 = time.time()
    meta = TICKERS[t]
    day_start = et_to_ns(day, "04:00")
    Q, H, T, E, S = [], [], [], [], []
    nq = nt = 0
    for hh, length in windows_for(mode):
        W0 = et_to_ns(day, hh)
        W1 = W0 + length * MIN
        q = fetch_quotes(t, W0, W1)
        pq = prevailing_quote(t, W0, day_start)
        if pq is not None:
            for k, v in (("ts", W0 - 1), ("bid", pq.get("bid_price", 0.0)), ("ask", pq.get("ask_price", 0.0)),
                         ("bsz", pq.get("bid_size", 0)), ("asz", pq.get("ask_size", 0)), ("c43", False), ("c16", False)):
                q[k] = np.concatenate([np.array([v], dtype=q[k].dtype), q[k]])
        nq += len(q["ts"])
        qdf, hist = quote_aggs(q, W0, W1, meta)
        wl = f"{hh}+{length}"
        for df in (qdf, hist):
            df.insert(0, "window", wl)
        Q.append(qdf)
        H.append(hist)
        tr = fetch_trades(t, W0, W1)
        if tr is not None:
            nt += len(tr["ts"])
            tdf, eh, sh = trade_aggs(tr, q, W0, W1, meta)
            for df in (tdf, eh, sh):
                df.insert(0, "window", wl)
            T.append(tdf)
            E.append(eh)
            S.append(sh)
        del q, tr
    for name, lst in (("trades_min", T), ("effhs_hist", E), ("size_hist", S), ("spread_hist", H), ("quotes_min", Q)):
        df = pd.concat(lst, ignore_index=True) if lst else pd.DataFrame()
        df.insert(0, "day", day)
        df.insert(0, "ticker", t)
        df.to_parquet(stem.parent / (stem.name + f"_{name}.parquet"))  # quotes_min written last = completion marker
    return t, day, "ok", nq, nt, round(time.time() - t0, 1)


# ------------------------------------------------------------------ sample days
def choose_days():
    spy = pd.read_parquet(DATA / "daily" / "SPY_adj_2022-01-01.parquet")
    dates = list(spy["date"])
    last12 = [d for d in dates if "2025-09-26" <= d <= "2026-09-25"]
    last5 = [d for d in dates if "2026-09-21" <= d <= "2026-09-25"]
    stress = ["2025-04-03", "2025-04-04", "2025-04-07", "2025-04-09", "2025-11-20", "2026-06-05", "2026-06-09"]
    pool = [d for d in last12 if d not in last5 and d not in stress]
    idx = np.linspace(0, len(pool) - 1, 20).round().astype(int)
    chosen = []
    for i in idx:
        # skip early-close sessions (check SPY minute bars end before 15:59)
        for k in range(i, min(i + 5, len(pool))):
            d = pool[k]
            mb = aggs("SPY", 1, "minute", d, d, True)
            last_rth = mb[(mb.ts_et.dt.strftime("%H:%M") < "16:00")]["ts_et"].max().strftime("%H:%M")
            if last_rth >= "15:59" and d not in chosen:
                chosen.append(d)
                break
    rows = [dict(day=d, group="regular_12m") for d in chosen] + [dict(day=d, group="last5") for d in last5] + \
           [dict(day=d, group="stress") for d in stress]
    df = pd.DataFrame(rows).drop_duplicates("day").sort_values("day")
    df.to_csv(OUT / "sample_days.csv", index=False)
    return df


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    if mode == "sample":
        f = OUT / "sample_days.csv"
        days = pd.read_csv(f) if f.exists() else choose_days()
        tickers = ALL
        tasks = [(t, d, mode) for d in days["day"] for t in tickers]
    else:
        fdays = ["2026-09-25", "2026-09-24", "2026-06-05", "2025-04-09", "2026-01-15"]
        tasks = [(t, d, mode) for d in fdays for t in ("SOXL", "SOXS")]
    # heavy tickers first so the tail is short
    order = {"TQQQ": 0, "QQQ": 1, "SPY": 2, "NVDA": 3, "SQQQ": 4, "SOXS": 5, "SOXL": 6}
    tasks.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    print(f"{len(tasks)} tasks, {workers} workers", flush=True)
    t0 = time.time()
    done = 0
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(process, tk): tk for tk in tasks}
        for fu in as_completed(futs):
            done += 1
            try:
                r = fu.result()
                print(done, r, f"elapsed={time.time() - t0:.0f}s", flush=True)
            except Exception:
                print("FAILED", futs[fu], traceback.format_exc()[-1500:], flush=True)


if __name__ == "__main__":
    main()
