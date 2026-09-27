"""1-second aggregates (trade-based) and a small NBBO-midquote sample for lead-lag analysis.

  * /v2/aggs/ticker/{T}/range/1/second/{day}/{day}  for SOXL, SOXS, SOXX, SMH, NVDA on the
    20 most recent full sessions up to 2026-09-25  -> data/dynamics/seconds/{T}.parquet
  * /v3/quotes for SOXL, SOXX, NVDA, 10:00-11:30 ET on 2026-09-24 and 2026-09-25, reduced to
    1-second last-NBBO midquotes -> data/dynamics/midq/{T}_{day}.parquet
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from common import DATA, TZ, api_get_all, half_days, load_daily

SDIR = DATA / "seconds"
MDIR = DATA / "midq"
SDIR.mkdir(parents=True, exist_ok=True)
MDIR.mkdir(parents=True, exist_ok=True)


def days_recent(n=20):
    d = load_daily("QQQ", True)
    days = pd.to_datetime(d["t"], unit="ms", utc=True).dt.tz_convert(TZ).dt.date
    hd = half_days()
    days = [x for x in days if x not in hd and str(x) <= "2026-09-25"]
    return days[-n:]


def fetch_sec(t, day):
    res = api_get_all(f"/v2/aggs/ticker/{t}/range/1/second/{day}/{day}",
                      {"adjusted": "true", "sort": "asc", "limit": 50000})
    df = pd.DataFrame(res)
    df["ticker"] = t
    return df


def fetch_midq(t, day, a="10:00", b="11:30"):
    fn = MDIR / f"{t}_{day}.parquet"
    if fn.exists():
        return
    s = pd.Timestamp(f"{day} {a}", tz=TZ).tz_convert("UTC")
    e = pd.Timestamp(f"{day} {b}", tz=TZ).tz_convert("UTC")
    res = api_get_all(f"/v3/quotes/{t}", {"timestamp.gte": s.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                           "timestamp.lt": e.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                           "limit": 50000, "sort": "timestamp", "order": "asc"})
    df = pd.DataFrame(res)[["sip_timestamp", "bid_price", "ask_price"]]
    ok = (df.bid_price > 0) & (df.ask_price > df.bid_price)
    df = df[ok]
    sec = (df.sip_timestamp // 1_000_000_000).astype(np.int64)
    mid = (df.bid_price + df.ask_price) / 2
    out = pd.DataFrame({"sec": sec, "mid": mid, "spread": df.ask_price - df.bid_price}).groupby("sec").last()
    out.to_parquet(fn)
    print("midq", t, day, len(df), flush=True)


def main():
    days = days_recent(20)
    for t in ["SOXL", "SOXS", "SOXX", "SMH", "NVDA"]:
        fn = SDIR / f"{t}.parquet"
        if fn.exists():
            continue
        with ThreadPoolExecutor(4) as ex:
            parts = list(ex.map(lambda d: fetch_sec(t, d), days))
        df = pd.concat(parts, ignore_index=True)
        df.to_parquet(fn)
        print("sec", t, len(df), flush=True)
    for day in ["2026-09-24", "2026-09-25"]:
        for t in ["SOXL", "SOXX", "NVDA"]:
            fetch_midq(t, day)


if __name__ == "__main__":
    main()
