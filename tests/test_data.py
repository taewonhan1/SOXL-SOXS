"""Data-layer tests: timestamp convention / DST, half-day detection, month planning, strategy wiring."""
from __future__ import annotations

import numpy as np
import pandas as pd

from conftest import make_panel
from soxlab import calendar as scal
from soxlab import config
from soxlab import data as sdata
from soxlab import strategies as st


def _ms(ts_utc: str) -> int:
    return int(pd.Timestamp(ts_utc, tz="UTC").value // 1_000_000)


def test_bar_start_utc_ms_to_et_across_dst():
    df = pd.DataFrame({"t": [_ms("2024-03-08 14:30"), _ms("2024-03-11 13:30"), _ms("2024-11-01 13:30"),
                             _ms("2024-11-04 14:30"), _ms("2024-07-01 08:00")]})
    out = sdata.add_time_columns(df)
    assert list(out["mod"]) == [570, 570, 570, 570, 240]     # all 09:30 ET except the 04:00 ET pre-market bar
    assert list(out["date"].dt.strftime("%Y-%m-%d")) == ["2024-03-08", "2024-03-11", "2024-11-01", "2024-11-04",
                                                         "2024-07-01"]


def test_half_day_detection():
    rows = []
    for day, last_rth in (("2024-11-27", 16 * 60), ("2024-11-29", 13 * 60)):
        for m in range(4 * 60, 20 * 60):
            v = 1000.0 if config.RTH_START_MIN <= m < last_rth else 10.0
            rows.append({"date": pd.Timestamp(day), "mod": m, "v": v})
    hd = scal.detect_half_days(pd.DataFrame(rows))
    assert not hd.loc["2024-11-27"] and hd.loc["2024-11-29"]


def test_month_range_and_third_friday():
    assert sdata.month_range("2019-11-15", "2020-02-01") == [(2019, 11), (2019, 12), (2020, 1), (2020, 2)]
    assert scal.third_friday(2026, 9) == pd.Timestamp("2026-09-18")
    assert scal.third_friday(2024, 3) == pd.Timestamp("2024-03-15")


def test_every_probe_generates_valid_signals():
    from test_no_lookahead import _context
    from soxlab import features as sfeat
    panels, official, premarket, cal = _context(n_days=30, half_days=())
    F = sfeat.compute_features("SOXL", panels, official, premarket, cal)
    for name in st.PROBES:
        ss = st.make_signals(name, F, panels["SOXL"])
        assert ss.entries.shape == panels["SOXL"].c.shape
        assert set(np.unique(ss.entries)).issubset({-1, 0, 1}), name
