#!/usr/bin/env python3
"""Data for Study T1 (REGISTRY.md, registered before this ran).

1. Adjusted 1-minute bars 2010-06 .. 2026-09 for VIXY and the breadth member list (soxlab bar store).
2. SOXL trades 09:30:00 -> 10:00:00 ET for every session 2011-06-01 .. 2026-09-25, aggregated per minute on the
   fly (raw prints are not kept): trade count, shares, dollars, tick-rule signed shares and dollars, odd-lot shares,
   block (>= $250k) signed dollars, off-exchange shares. Tick rule: up-tick = buy, down-tick = sell, zero tick
   keeps the previous sign. Resumable: one parquet per year under data/research/flow/, sessions already present
   are skipped.

    python download_detector_data.py bars      # minute bars only
    python download_detector_data.py flow      # trade aggregates only
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab import api, config
from soxlab import data as sdata
from soxlab.research import common as C

MEMBERS = ["NVDA", "AVGO", "AMD", "INTC", "QCOM", "TXN", "MU", "AMAT", "LRCX", "KLAC", "ADI", "MRVL", "NXPI", "MCHP",
           "ON", "SWKS", "TER", "TSM", "ASML", "MPWR", "ENTG", "LSCC", "STM"]
EXTRA = ["VIXY"]
FLOW_DIR = ROOT / "data" / "research" / "flow"
START, END = "2011-06-01", "2026-09-25"
BLOCK_USD = 250_000
ODD_LOT = 37


def download_bars() -> None:
    tickers = [t for t in EXTRA + MEMBERS if t != "NVDA"]
    rec = sdata.download_minute_bars(tickers, start="2010-06-01", end=END, adjusted_flags=(True,))
    print(f"minute-bar month files downloaded: {len(rec)}")


def _session_flow(day: pd.Timestamp) -> pd.DataFrame:
    t0 = pd.Timestamp(f"{day.date()} 09:30:00", tz=config.TZ)
    t1 = t0 + pd.Timedelta(minutes=30)
    res = api.get_all("/v3/trades/SOXL", {"timestamp.gte": t0.value, "timestamp.lt": t1.value, "limit": 50000,
                                          "sort": "timestamp", "order": "asc"})
    if not res:
        return pd.DataFrame()
    df = pd.DataFrame(res)
    df = df.sort_values(["sip_timestamp", "sequence_number"] if "sequence_number" in df else ["sip_timestamp"])
    px = df["price"].to_numpy(float)
    sz = (df["decimal_size"] if "decimal_size" in df else df["size"]).to_numpy(float)
    d = np.sign(np.diff(px, prepend=px[0]))
    s = pd.Series(np.where(d == 0, np.nan, d)).ffill().fillna(0).to_numpy()      # zero tick keeps the last sign
    usd = px * sz
    conds = df["conditions"] if "conditions" in df else pd.Series([[]] * len(df))
    odd = conds.apply(lambda c: ODD_LOT in c if isinstance(c, (list, np.ndarray)) else False).to_numpy()
    offex = (df["exchange"].to_numpy() == 4) if "exchange" in df else np.zeros(len(df), bool)
    minute = ((df["sip_timestamp"].to_numpy(np.int64) - t0.value) // 60_000_000_000).clip(0, 29)
    out = pd.DataFrame({"minute": minute, "n": 1, "shares": sz, "dollars": usd, "signed_shares": s * sz,
                        "signed_dollars": s * usd, "oddlot_shares": np.where(odd, sz, 0.0),
                        "block_signed_dollars": np.where(usd >= BLOCK_USD, s * usd, 0.0),
                        "offex_shares": np.where(offex, sz, 0.0)})
    out = out.groupby("minute").sum().reset_index()
    out.insert(0, "date", day)
    return out


def download_flow() -> None:
    FLOW_DIR.mkdir(parents=True, exist_ok=True)
    dates = C.Context(start=START, end=END).dates
    for year in sorted(set(dates.year)):
        path = FLOW_DIR / f"soxl_flow_{year}.parquet"
        have = pd.read_parquet(path) if path.exists() else pd.DataFrame(columns=["date"])
        done = set(pd.to_datetime(have["date"]).dt.normalize()) if len(have) else set()
        todo = [d for d in dates[dates.year == year] if d not in done]
        if not todo:
            continue
        parts = []
        for i in range(0, len(todo), 40):                     # checkpoint every 40 sessions
            chunk = todo[i:i + 40]
            parts += [p for p in api.parallel_map(_session_flow, chunk, desc=f"flow {year}", verbose=False)
                      if p is not None and len(p)]
            frame = pd.concat([have] + parts, ignore_index=True) if len(have) else pd.concat(parts, ignore_index=True)
            frame.to_parquet(path, index=False)
            print(f"{year}: {i + len(chunk)}/{len(todo)} sessions", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("bars", "all"):
        download_bars()
    if what in ("flow", "all"):
        download_flow()
