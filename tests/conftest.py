"""Synthetic fixtures (no network, no cache needed)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from soxlab import config  # noqa: E402
from soxlab.data import Panel  # noqa: E402


def make_panel(ticker="SYN", n_days=40, n_bars=config.N_RTH, seed=0, phi=0.0, sigma=0.001, start_price=50.0,
               half_days=(), gap_sigma=0.0, factor=1.0) -> Panel:
    """Random-walk (optionally AR(1)) minute panel. Opens equal the previous close (no intraday gaps).

    ``factor`` = unadjusted/adjusted price ratio (simulates a split-adjusted history).
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2023-01-02", periods=n_days)
    n_min = np.full(n_days, n_bars)
    for hd in half_days:
        n_min[hd] = 210
    c = np.full((n_days, n_bars), np.nan)
    o = np.full_like(c, np.nan)
    h = np.full_like(c, np.nan)
    l = np.full_like(c, np.nan)
    price = start_price
    for d in range(n_days):
        price *= np.exp(rng.normal(0, gap_sigma)) if gap_sigma else 1.0
        r_prev = 0.0
        for j in range(n_min[d]):
            r = phi * r_prev + rng.normal(0, sigma)
            op = price
            cl = op * np.exp(r)
            wig = abs(rng.normal(0, sigma / 2)) * op
            o[d, j], c[d, j] = op, cl
            h[d, j] = max(op, cl) + wig
            l[d, j] = min(op, cl) - wig
            price, r_prev = cl, r
    v = np.where(np.isnan(c), np.nan, rng.integers(100, 10_000, size=c.shape).astype(float))
    arrays = {"o": o, "h": h, "l": l, "c": c, "v": v, "vw": (h + l + c) / 3, "n": np.where(np.isnan(c), np.nan, 10.0),
              "c_unadj": c * factor, "o_unadj": o * factor, "present": ~np.isnan(c)}
    return Panel(ticker, pd.DatetimeIndex(dates), arrays, n_min)


def make_calendar(dates: pd.DatetimeIndex, half_days=()) -> pd.DataFrame:
    from soxlab.calendar import add_event_flags
    cal = pd.DataFrame(index=pd.DatetimeIndex(dates, name="date"))
    cal["is_half_day"] = False
    cal.iloc[list(half_days), 0] = True
    cal["n_rth_minutes"] = np.where(cal["is_half_day"], 210, 390)
    return add_event_flags(cal)


@pytest.fixture
def iid_panel():
    return make_panel(n_days=120, seed=1, phi=0.0)


@pytest.fixture
def ar_panel():
    return make_panel(n_days=120, seed=2, phi=0.3)
