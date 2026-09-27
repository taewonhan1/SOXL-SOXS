#!/usr/bin/env python3
"""Fallback half-spread estimate from a LIGHT NBBO sample (/v3/quotes).

Used only when analysis/microstructure/output/cost_model_halfspread.csv is absent.
Sample: 2 trading days per year 2022-2026 (10 days) x 5 five-minute windows per day x {SOXL, SOXS}.
Spreads are time-weighted within each window (each NBBO state weighted by how long it was in force);
locked/crossed (ask <= bid) and implausible (> 5% of mid) quotes are dropped.

Output (same columns as the microstructure file):
    analysis/backtests/output/halfspread_estimate_nbbo_sample.csv
        ticker, year, bucket_start_et, bucket_end_et, median_spread_cents, mean_spread_cents,
        median_half_spread_bps, mean_half_spread_bps, n_obs, n_windows, source
    data/soxlab/nbbo_sample/{T}_{date}_{HHMM}.parquet  raw quotes (gitignored)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soxlab import api, config  # noqa: E402
from soxlab import calendar as scal  # noqa: E402

TARGET_DAYS = ["2022-03-16", "2022-09-14", "2023-03-15", "2023-09-13", "2024-03-13", "2024-09-11",
               "2025-03-12", "2025-09-10", "2026-03-11", "2026-09-16"]
WINDOWS = ["09:30", "10:30", "12:30", "14:30", "15:50"]         # 5-minute windows starting here (ET)
BUCKETS = [("09:30", "10:00"), ("10:00", "15:30"), ("15:30", "16:00")]


def _snap_to_trading_days(days, cal):
    out = []
    for d in days:
        ts = pd.Timestamp(d)
        after = cal.index[(cal.index >= ts) & (~cal["is_half_day"])]
        out.append(after[0].strftime("%Y-%m-%d"))
    return out


def fetch_window(T: str, day: str, hhmm: str) -> pd.DataFrame:
    p = config.NBBO_DIR / f"{T}_{day}_{hhmm.replace(':', '')}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    t0 = pd.Timestamp(f"{day} {hhmm}", tz=config.TZ)
    t1 = t0 + pd.Timedelta(minutes=5)
    # include 60 s before the window so the NBBO in force at the window start is known
    params = {"timestamp.gte": int((t0 - pd.Timedelta(seconds=60)).value), "timestamp.lt": int(t1.value),
              "limit": 50000, "sort": "timestamp", "order": "asc"}
    res = api.get_all(f"/v3/quotes/{T}", params)
    df = pd.DataFrame(res)
    keep = [c for c in ("sip_timestamp", "bid_price", "ask_price", "bid_size", "ask_size") if c in df]
    df = df[keep] if len(df) else pd.DataFrame(columns=keep)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return df


def window_stats(df: pd.DataFrame, day: str, hhmm: str) -> pd.DataFrame:
    t0 = pd.Timestamp(f"{day} {hhmm}", tz=config.TZ).value
    t1 = t0 + 5 * 60 * 10**9
    if df.empty:
        return pd.DataFrame()
    q = df.sort_values("sip_timestamp")
    ts = q["sip_timestamp"].to_numpy(np.int64)
    nxt = np.append(ts[1:], t1)
    start = np.maximum(ts, t0)
    end = np.minimum(nxt, t1)
    w = (end - start).clip(min=0) / 1e9
    bid, ask = q["bid_price"].to_numpy(float), q["ask_price"].to_numpy(float)
    mid = (bid + ask) / 2
    spr = ask - bid
    ok = (w > 0) & (bid > 0) & (ask > bid) & (spr / mid < 0.05)
    return pd.DataFrame({"w": w[ok], "spread": spr[ok], "mid": mid[ok]})


def wquantile(x, w, q):
    o = np.argsort(x)
    x, w = x[o], w[o]
    cw = np.cumsum(w) / w.sum()
    return float(x[np.searchsorted(cw, q)])


def main() -> None:
    cal = scal.load_calendar()
    days = _snap_to_trading_days(TARGET_DAYS, cal)
    jobs = [(T, d, h) for T in config.TRADED for d in days for h in WINDOWS]
    frames = api.parallel_map(lambda j: (j, fetch_window(*j)), jobs, desc="nbbo")
    rows = []
    for (T, d, h), df in frames:
        st = window_stats(df, d, h)
        if st.empty:
            continue
        m = int(h[:2]) * 60 + int(h[3:])
        b = next(bk for bk in BUCKETS if int(bk[0][:2]) * 60 + int(bk[0][3:]) <= m < int(bk[1][:2]) * 60 + int(bk[1][3:]))
        st["ticker"], st["year"], st["bucket_start_et"], st["bucket_end_et"], st["window"] = T, int(d[:4]), b[0], b[1], f"{d} {h}"
        st["n_quotes"] = len(df)
        rows.append(st)
    allq = pd.concat(rows, ignore_index=True)
    out = []
    for (T, y, b0, b1), g in allq.groupby(["ticker", "year", "bucket_start_et", "bucket_end_et"]):
        cents = g["spread"].to_numpy() * 100
        hbps = (g["spread"] / 2 / g["mid"]).to_numpy() * 1e4
        w = g["w"].to_numpy()
        out.append({"ticker": T, "year": y, "bucket_start_et": b0, "bucket_end_et": b1,
                    "median_spread_cents": wquantile(cents, w, 0.5), "mean_spread_cents": float(np.average(cents, weights=w)),
                    "median_half_spread_bps": wquantile(hbps, w, 0.5), "mean_half_spread_bps": float(np.average(hbps, weights=w)),
                    "n_obs": int(len(g)), "n_windows": int(g["window"].nunique()),
                    "source": "soxlab NBBO sample (/v3/quotes), time-weighted, 2 days/yr"})
    res = pd.DataFrame(out).sort_values(["ticker", "year", "bucket_start_et"])
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dst = config.OUTPUT_DIR / "halfspread_estimate_nbbo_sample.csv"
    res.to_csv(dst, index=False)
    print(res.to_string())
    print(f"sampled days: {days}\nwrote {dst}")


if __name__ == "__main__":
    main()
