#!/usr/bin/env python3
"""Download / incrementally update the soxlab cache from the Massive API.

Usage
-----
    python scripts/download_data.py                      # full build (idempotent; skips cached months)
    python scripts/download_data.py --update             # same, but extends END to the last weekday
    python scripts/download_data.py --tickers SOXL SOXS --start 2024-01-01 --end 2024-03-31
    python scripts/download_data.py --skip-minute        # daily bars / reference / calendar only

Writes only under data/soxlab/ (gitignored).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soxlab import calendar as scal  # noqa: E402
from soxlab import config  # noqa: E402
from soxlab import data as sdata  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tickers", nargs="+", default=config.TICKERS)
    ap.add_argument("--start", default=config.HISTORY_START)
    ap.add_argument("--end", default=config.HISTORY_END)
    ap.add_argument("--update", action="store_true", help="set --end to the most recent weekday (incremental)")
    ap.add_argument("--skip-minute", action="store_true")
    ap.add_argument("--workers", type=int, default=config.MAX_CONCURRENCY)
    args = ap.parse_args()
    if args.update:
        today = pd.Timestamp.now(tz=config.TZ).normalize().tz_localize(None)
        args.end = (today if today.weekday() < 5 else today - pd.offsets.BDay(1)).strftime("%Y-%m-%d")
    t0 = time.time()
    print(f"reference data (splits, dividends) for {args.tickers}")
    sdata.download_reference(args.tickers)
    print("daily bars (adjusted + unadjusted, full history)")
    sdata.download_daily(args.tickers, end=args.end)
    if not args.skip_minute:
        print(f"minute bars {args.start} -> {args.end}")
        rec = sdata.download_minute_bars(args.tickers, args.start, args.end, max_workers=min(6, args.workers))
        if len(rec):
            print(rec.groupby(["ticker", "adjusted"])["rows"].sum())
    if "QQQ" in args.tickers or (config.BARS_DIR / "unadjusted" / "QQQ").exists():
        cal = scal.build_calendar(config.HISTORY_START, args.end)
        print(f"calendar: {len(cal)} trading days, {int(cal['is_half_day'].sum())} half-days")
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
