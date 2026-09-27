"""Trading calendar and event flags derived from data (no external calendar package needed).

* Trading days  = dates with a daily bar for the reference ticker (QQQ) in the requested range.
* Half-days     = days whose regular-session trading stops at 13:00 ET. Detected from QQQ minute
                  bars: volume in 13:00-15:59 ET below 10% of volume in 09:30-12:59 ET. (On early-close
                  days the 13:00-17:00 window is an extended-hours session with little volume.)
* Event flags   = rule-based (monthly options expiry, quad witching, month/quarter end, pre/post
                  holiday) plus data-based (split and dividend ex-dates from /v3/reference).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config
from . import data as sdata

REF_TICKER = "QQQ"


def third_friday(year: int, month: int) -> pd.Timestamp:
    d = pd.Timestamp(year=year, month=month, day=15)
    # 15th..21st contains the third Friday
    return d + pd.Timedelta(days=(4 - d.weekday()) % 7)


def detect_half_days(ref_bars: pd.DataFrame) -> pd.Series:
    """Boolean Series indexed by date: True when regular trading ended at 13:00 ET."""
    rth = ref_bars[(ref_bars["mod"] >= config.RTH_START_MIN) & (ref_bars["mod"] < config.RTH_END_MIN)]
    am = rth[rth["mod"] < config.HALF_DAY_END_MIN].groupby("date")["v"].sum()
    pm = rth[rth["mod"] >= config.HALF_DAY_END_MIN].groupby("date")["v"].sum()
    ratio = (pm.reindex(am.index).fillna(0.0) / am.replace(0, np.nan))
    return (ratio < 0.10).rename("is_half_day")


def build_calendar(start: str = config.HISTORY_START, end: str = config.HISTORY_END,
                   save: bool = True) -> pd.DataFrame:
    daily = sdata.load_daily(REF_TICKER, adjusted=False)
    days = daily.index[(daily.index >= pd.Timestamp(start)) & (daily.index <= pd.Timestamp(end))]
    cal = pd.DataFrame(index=pd.DatetimeIndex(days, name="date"))
    ref = sdata.load_minute_bars(REF_TICKER, False, start, end)
    hd = detect_half_days(ref)
    cal["is_half_day"] = hd.reindex(cal.index).fillna(False).astype(bool)
    cal["n_rth_minutes"] = np.where(cal["is_half_day"], config.HALF_DAY_END_MIN - config.RTH_START_MIN,
                                    config.N_RTH).astype(int)
    cal["session_close_et"] = np.where(cal["is_half_day"], "13:00", "16:00")
    cal = add_event_flags(cal)
    if save:
        config.REF_DIR.mkdir(parents=True, exist_ok=True)
        cal.to_parquet(config.REF_DIR / "calendar.parquet")
    return cal


def add_event_flags(cal: pd.DataFrame) -> pd.DataFrame:
    idx = cal.index
    cal = cal.copy()
    cal["dow"] = idx.dayofweek  # 0=Mon
    nxt = pd.Series(idx[1:].append(pd.DatetimeIndex([pd.NaT])), index=idx)
    prv = pd.Series(pd.DatetimeIndex([pd.NaT]).append(idx[:-1]), index=idx)
    bdays_to_next = [np.busday_count(a.date(), b.date()) if pd.notna(b) else 1 for a, b in zip(idx, nxt)]
    bdays_from_prev = [np.busday_count(b.date(), a.date()) if pd.notna(b) else 1 for a, b in zip(idx, prv)]
    cal["pre_holiday"] = np.array(bdays_to_next) > 1          # next weekday is a market holiday
    cal["post_holiday"] = np.array(bdays_from_prev) > 1       # previous weekday was a market holiday
    ym = idx.to_period("M")
    cal["month_end"] = pd.Series(ym, index=idx) != pd.Series(ym, index=idx).shift(-1)
    cal["month_start"] = pd.Series(ym, index=idx) != pd.Series(ym, index=idx).shift(1)
    cal["quarter_end"] = cal["month_end"] & idx.month.isin([3, 6, 9, 12])
    # monthly options expiry: third Friday, or the prior trading day when that Friday is a holiday
    opex = set()
    for y in range(idx.min().year, idx.max().year + 1):
        for m in range(1, 13):
            f = third_friday(y, m)
            prior = idx[idx <= f]
            if len(prior) and (f - prior[-1]).days <= 3:
                opex.add(prior[-1])
    cal["monthly_opex"] = idx.isin(sorted(opex))
    cal["quad_witching"] = cal["monthly_opex"] & idx.month.isin([3, 6, 9, 12])
    for tk in config.TRADED:
        sp = sdata.load_splits(tk)
        cal[f"split_{tk}"] = idx.isin(pd.DatetimeIndex(sp["execution_date"])) if len(sp) else False
        dv = sdata.load_dividends(tk)
        cal[f"exdiv_{tk}"] = idx.isin(pd.DatetimeIndex(dv["ex_dividend_date"])) if len(dv) else False
    return cal


def load_calendar() -> pd.DataFrame:
    p = config.REF_DIR / "calendar.parquet"
    if not p.exists():
        return build_calendar()
    return pd.read_parquet(p)
