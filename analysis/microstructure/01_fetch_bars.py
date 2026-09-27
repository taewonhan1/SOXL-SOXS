"""Step 1: daily bars (adjusted + unadjusted), 1-minute bars (unadjusted), splits and ticker reference.

Outputs (cache): data/microstructure/bars/{T}_day_{adj|raw}.parquet, {T}_min_raw.parquet,
                 data/microstructure/ref/splits.json, tickers.json
Run: python3 01_fetch_bars.py
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from ms_common import DATA, ET, TICKERS, fetch_aggs, get_json, iter_pages, http_stats  # noqa: E402

BARS = DATA / "bars"
REF = DATA / "ref"
BARS.mkdir(parents=True, exist_ok=True)
REF.mkdir(parents=True, exist_ok=True)
DAY_FROM, MIN_FROM, TO = "2021-01-01", "2022-01-01", "2026-09-25"


def get_day(T):
    for adj in (True, False):
        f = BARS / f"{T}_day_{'adj' if adj else 'raw'}.parquet"
        if f.exists():
            continue
        df = fetch_aggs(T, 1, "day", DAY_FROM, TO, adj)
        df["date"] = pd.to_datetime(df["t"], unit="ms", utc=True).dt.tz_convert(ET).dt.strftime("%Y-%m-%d")
        df.to_parquet(f, index=False)
    return T


def get_min(T):
    f = BARS / f"{T}_min_raw.parquet"
    if f.exists():
        return T
    parts = []
    # yearly chunks keep each request's result set modest; pagination via next_url inside fetch_aggs
    for y in range(2022, 2027):
        frm, to = f"{y}-01-01", (f"{y}-12-31" if y < 2026 else TO)
        df = fetch_aggs(T, 1, "minute", frm, to, False)
        if len(df):
            parts.append(df)
    df = pd.concat(parts, ignore_index=True).drop_duplicates("t").sort_values("t")
    df.to_parquet(f, index=False)
    return T


if __name__ == "__main__":
    splits = {}
    tick = {}
    for T in TICKERS:
        rows = []
        for res in iter_pages("/v3/reference/splits", {"ticker": T, "limit": 1000}):
            rows.extend(res)
        splits[T] = rows
        tick[T] = get_json(f"/v3/reference/tickers/{T}").get("results")
    json.dump(splits, open(REF / "splits.json", "w"), indent=1)
    json.dump(tick, open(REF / "tickers.json", "w"), indent=1)
    with ThreadPoolExecutor(6) as ex:
        for T in ex.map(get_day, TICKERS):
            print("day", T, flush=True)
    with ThreadPoolExecutor(6) as ex:
        for T in ex.map(get_min, TICKERS):
            print("min", T, flush=True)
    print(http_stats())
