#!/usr/bin/env python3
"""Deep history for an independent test of the final strategy: 1-minute bars 2010-03 .. 2018-12 for the research
tickers (adjusted and unadjusted), then the trading calendar rebuilt from 2011-03-23 (QQQ's first session under
that ticker; it traded as QQQQ before). Nothing here is used for rule selection."""
from __future__ import annotations

from runlib import ROOT  # noqa: F401,I001
from soxlab import calendar as scal
from soxlab import config
from soxlab import data as sdata

TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "QQQ"]


def main() -> None:
    rec = sdata.download_minute_bars(TICKERS, start="2010-03-01", end="2018-12-31")
    print(f"downloaded {len(rec)} month files")
    cal = scal.build_calendar(start="2010-01-01", end=config.HISTORY_END)
    print(f"calendar {cal.index.min().date()} .. {cal.index.max().date()} ({len(cal)} sessions, "
          f"{int(cal['is_half_day'].sum())} half-days)")


if __name__ == "__main__":
    main()
