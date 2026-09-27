"""Download 1-minute (split-adjusted) and daily (adjusted + unadjusted) bars from Massive.

Minute bars are fetched in calendar-month chunks using ms-timestamp boundaries at 00:00 ET
(each chunk < 50k rows) with <= 4 concurrent requests; next_url pagination is followed anyway.
Output: data/dynamics/minute/{T}_adj.parquet, data/dynamics/daily/{T}_{adj,unadj}.parquet
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from common import DATA, DL_END, DL_START, TICKERS, TZ, api_get_all

MAXW = 4


def month_chunks(start: str, end: str):
    s = pd.Timestamp(start, tz=TZ)
    e = pd.Timestamp(end, tz=TZ) + pd.Timedelta(days=1)
    cur = s
    while cur < e:
        nxt = min((cur + pd.offsets.MonthBegin(1)).normalize(), e)
        yield int(cur.timestamp() * 1000), int(nxt.timestamp() * 1000) - 1
        cur = nxt


def fetch_minutes(ticker: str, a: int, b: int, adjusted: bool = True) -> pd.DataFrame:
    url = f"/v2/aggs/ticker/{ticker}/range/1/minute/{a}/{b}"
    res = api_get_all(url, {"adjusted": str(adjusted).lower(), "sort": "asc", "limit": 50000})
    return pd.DataFrame(res)


def main(tickers=TICKERS):
    (DATA / "minute").mkdir(parents=True, exist_ok=True)
    (DATA / "daily").mkdir(parents=True, exist_ok=True)
    # daily bars
    for t in tickers:
        for adj in (True, False):
            p = DATA / "daily" / f"{t}_{'adj' if adj else 'unadj'}.parquet"
            if p.exists():
                continue
            res = api_get_all(f"/v2/aggs/ticker/{t}/range/1/day/2021-10-01/{DL_END}",
                              {"adjusted": str(adj).lower(), "sort": "asc", "limit": 50000})
            pd.DataFrame(res).to_parquet(p)
            print("daily", t, adj, len(res), flush=True)
    # minute bars
    chunks = list(month_chunks(DL_START, DL_END))
    for t in tickers:
        p = DATA / "minute" / f"{t}_adj.parquet"
        if p.exists():
            print("have", p, flush=True)
            continue
        parts = []
        with ThreadPoolExecutor(MAXW) as ex:
            futs = {ex.submit(fetch_minutes, t, a, b): (a, b) for a, b in chunks}
            for f in as_completed(futs):
                parts.append(f.result())
        df = pd.concat([x for x in parts if len(x)], ignore_index=True)
        df = df.drop_duplicates("t").sort_values("t").reset_index(drop=True)
        cols = [c for c in ["t", "o", "h", "l", "c", "v", "vw", "n"] if c in df.columns]
        df[cols].to_parquet(p)
        print("minute", t, len(df), pd.to_datetime(df.t.min(), unit="ms"), pd.to_datetime(df.t.max(), unit="ms"), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or TICKERS)
