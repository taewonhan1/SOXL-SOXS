#!/usr/bin/env python3
"""Daily behavior tracker: one row per day per ticker.

Historical (from the cache; run scripts/download_data.py --update first for new days):
    python scripts/daily_tracker.py                              # SOXL + SOXS -> analysis/backtests/output/daily_tracker_SOXL_SOXS.csv
    python scripts/daily_tracker.py --tickers SOXL SOXS SOXX NVDA --out data/soxlab/cache/tracker.parquet

Live / intraday (REST polling of 1-minute aggregates + real-time snapshot):
    python scripts/daily_tracker.py --live                       # today so far, printed
    python scripts/daily_tracker.py --live --date 2026-09-25     # any single session via the API
    python scripts/daily_tracker.py --live --interval 60         # refresh every 60 s (Ctrl-C to stop)
For streaming instead of polling see soxlab/README.md (WebSocket channels AM.<T>, A.<T>, Q.<T>, T.<T>).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soxlab import config  # noqa: E402
from soxlab import tracker  # noqa: E402

COLS = ["date", "ticker", "open", "high", "low", "last_rth_close", "official_close", "prev_close", "gap_pct", "range_pct",
        "true_range_pct", "atr14_prev_pct", "tr_over_atr", "ret_oc_pct", "ret_cc_pct", "close_location", "or5_size_bps",
        "or15_size_bps", "or30_size_bps", "or30_first_break", "or30_break_time", "vwap_close", "close_vs_vwap_bps",
        "vwap_crosses", "trend_day", "trend_dir", "time_of_high", "time_of_low", "rth_volume", "daily_bar_volume",
        "rel_volume_20d", "pre_volume", "pre_high", "pre_low", "realized_vol_1m_ann_pct", "proxy_ret_pct",
        "implied_leverage_at_close", "tracking_gap_bps", "soxl_soxs_div_close_bps", "spread_cents_model",
        "half_spread_bps_at_close_model", "is_half_day"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tickers", nargs="+", default=config.TRADED)
    ap.add_argument("--start", default=config.HISTORY_START)
    ap.add_argument("--end", default=config.HISTORY_END)
    ap.add_argument("--out", default=None)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--date", default=None, help="session date for --live (default: today ET)")
    ap.add_argument("--interval", type=int, default=0, help="seconds between refreshes in --live mode")
    args = ap.parse_args()
    if args.live:
        while True:
            df = tracker.live_rows(args.tickers, args.date)
            with pd.option_context("display.width", 200, "display.max_columns", 60):
                print(df.T.to_string())
            if args.out:
                df.to_csv(args.out, mode="a", header=not Path(args.out).exists(), index=False)
            if args.interval <= 0:
                break
            time.sleep(args.interval)
        return
    t0 = time.time()
    df = tracker.build_history(args.tickers, start=args.start, end=args.end)
    cols = [c for c in COLS if c in df.columns]
    df = df[cols]
    out = Path(args.out) if args.out else config.OUTPUT_DIR / f"daily_tracker_{'_'.join(args.tickers)}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix == ".parquet":
        df.to_parquet(out, index=False)
    else:
        df.round(4).to_csv(out, index=False)
    print(f"wrote {out}: {len(df)} rows ({df['date'].min():%Y-%m-%d} -> {df['date'].max():%Y-%m-%d}) "
          f"in {time.time() - t0:.0f}s; spread source: {df.attrs.get('spread_source', 'n/a')}")
    last = df[df["date"] == df["date"].max()]
    with pd.option_context("display.width", 200):
        print(last.T.to_string())


if __name__ == "__main__":
    main()
