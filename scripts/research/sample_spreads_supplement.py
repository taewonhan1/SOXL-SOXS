#!/usr/bin/env python3
"""Supplementary half-spread table for periods/tickers the microstructure table does not cover.

The microstructure study's table (analysis/microstructure/output/cost_model_halfspread.csv) covers
2022-2026 for SOXL, SOXS, SOXX, SMH, NVDA, QQQ, TQQQ, SQQQ. The research plan also needs:
  * 2019-2021 for the pre-sample checks (SOXL traded at ~$100-600 before its 2021 15:1 split, with
    spreads of tens of cents, so 2022 cents cannot be reused), and
  * SPY 2019-2026 for the Study 4 sanity check.

Sample: 8 regular (non-half) trading days per year x 15 three-minute NBBO windows per day
(09:30, 09:45, 10:00, 10:30, ..., 15:00, 15:30, 15:50). Spreads are time-weighted within each
window; locked/crossed and >5%-of-mid quotes are dropped. Output uses the same schema as the
microstructure table so soxlab.costs can read it:
    analysis/strategies/output/cost_table_supplement.csv
Raw windows are cached under data/research/nbbo_windows/ (gitignored).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from soxlab import api, config  # noqa: E402
from soxlab import calendar as scal  # noqa: E402

OUT = config.REPO_ROOT / "analysis" / "strategies" / "output" / "cost_table_supplement.csv"
CACHE = config.REPO_ROOT / "data" / "research" / "nbbo_windows"
WIN_MIN = 3
WINDOWS = ["09:30", "09:45", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
           "14:00", "14:30", "15:00", "15:30", "15:50"]
TARGET_MD = ["01-15", "02-26", "04-15", "05-27", "07-15", "08-26", "10-15", "11-25"]
JOBS_SPEC = ([(t, y) for t in ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "QQQ", "TQQQ", "SPY"] for y in (2019, 2020, 2021)]
             + [("SPY", y) for y in (2022, 2023, 2024, 2025, 2026)])


def bucket_of(hhmm: str) -> tuple[str, str]:
    m = int(hhmm[:2]) * 60 + int(hhmm[3:])
    b0 = config.RTH_START_MIN + ((m - config.RTH_START_MIN) // 30) * 30
    b1 = b0 + 30
    f = lambda x: f"{x // 60:02d}:{x % 60:02d}"
    return f(b0), f(b1)


def trading_days(year: int, cal: pd.DataFrame) -> list[str]:
    out = []
    for md in TARGET_MD:
        ts = pd.Timestamp(f"{year}-{md}")
        if ts > pd.Timestamp(config.HISTORY_END):
            continue
        after = cal.index[(cal.index >= ts) & (~cal["is_half_day"])]
        if len(after):
            out.append(after[0].strftime("%Y-%m-%d"))
    return sorted(set(out))


def fetch_window(T: str, day: str, hhmm: str) -> pd.DataFrame:
    p = CACHE / f"{T}_{day}_{hhmm.replace(':', '')}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    t0 = pd.Timestamp(f"{day} {hhmm}", tz=config.TZ)
    t1 = t0 + pd.Timedelta(minutes=WIN_MIN)
    params = {"timestamp.gte": int((t0 - pd.Timedelta(seconds=60)).value), "timestamp.lt": int(t1.value),
              "limit": 50000, "sort": "timestamp", "order": "asc"}
    res = api.get_all(f"/v3/quotes/{T}", params)
    cols = ["sip_timestamp", "bid_price", "ask_price", "bid_size", "ask_size"]
    df = pd.DataFrame(res)
    df = df[[c for c in cols if c in df.columns]] if len(df) else pd.DataFrame(columns=cols)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return df


def window_stats(df: pd.DataFrame, day: str, hhmm: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    t0 = pd.Timestamp(f"{day} {hhmm}", tz=config.TZ).value
    t1 = t0 + WIN_MIN * 60 * 10**9
    q = df.sort_values("sip_timestamp")
    ts = q["sip_timestamp"].to_numpy(np.int64)
    nxt = np.append(ts[1:], t1)
    w = (np.minimum(nxt, t1) - np.maximum(ts, t0)).clip(min=0) / 1e9
    bid, ask = q["bid_price"].to_numpy(float), q["ask_price"].to_numpy(float)
    mid, spr = (bid + ask) / 2, ask - bid
    ok = (w > 0) & (bid > 0) & (ask > bid) & (spr / mid < 0.05)
    return pd.DataFrame({"w": w[ok], "spread": spr[ok], "mid": mid[ok]})


def wquantile(x, w, q):
    o = np.argsort(x)
    x, w = x[o], w[o]
    cw = np.cumsum(w) / w.sum()
    return float(x[min(np.searchsorted(cw, q), len(x) - 1)])


def main() -> None:
    cal = scal.load_calendar()
    jobs = [(T, d, h) for (T, y) in JOBS_SPEC for d in trading_days(y, cal) for h in WINDOWS]
    print(f"{len(jobs)} NBBO windows to sample", flush=True)
    frames = api.parallel_map(lambda j: (j, fetch_window(*j)), jobs, desc="nbbo-supp")
    rows = []
    for (T, d, h), df in frames:
        st = window_stats(df, d, h)
        if st.empty:
            continue
        b0, b1 = bucket_of(h)
        st["ticker"], st["year"], st["bucket_start_et"], st["bucket_end_et"] = T, int(d[:4]), b0, b1
        st["window"] = f"{d} {h}"
        rows.append(st)
    allq = pd.concat(rows, ignore_index=True)
    out = []
    for (T, y, b0, b1), g in allq.groupby(["ticker", "year", "bucket_start_et", "bucket_end_et"]):
        cents = g["spread"].to_numpy() * 100
        hbps = (g["spread"] / 2 / g["mid"]).to_numpy() * 1e4
        w = g["w"].to_numpy()
        out.append({"ticker": T, "year": int(y), "bucket_start_et": b0, "bucket_end_et": b1,
                    "median_spread_cents": wquantile(cents, w, 0.5),
                    "mean_spread_cents": float(np.average(cents, weights=w)),
                    "median_half_spread_bps": wquantile(hbps, w, 0.5),
                    "mean_half_spread_bps": float(np.average(hbps, weights=w)),
                    "n_obs": int(len(g)), "n_windows": int(g["window"].nunique()),
                    "source": f"research NBBO sample, {len(TARGET_MD)} days/yr x {WIN_MIN}-min windows"})
    res = pd.DataFrame(out).sort_values(["ticker", "year", "bucket_start_et"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT, index=False)
    print(res.groupby(["ticker", "year"])[["median_spread_cents", "median_half_spread_bps"]].median().round(2).to_string())
    print(f"wrote {OUT} ({len(res)} rows)")


if __name__ == "__main__":
    main()
