"""Truncation-invariance tests: every look-ahead-safe feature at (d*, j*) must be identical whether or not
data after (d*, j*) exists. Forward-looking label columns must FAIL this test (proves the test has power).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from conftest import make_calendar, make_panel
from soxlab import features as sfeat
from soxlab.data import Panel

SYN = ["SOXL", "SOXS", "SOXX", "NVDA", "QQQ", "SMH"]


def _context(n_days=40, half_days=(25,)):
    panels = {tk: make_panel(tk, n_days=n_days, seed=i + 10, half_days=half_days,
                             phi=0.05 if tk == "SOXL" else 0.0, gap_sigma=0.01) for i, tk in enumerate(SYN)}
    dates = panels["SOXL"].dates
    official = {tk: pd.Series([p.c[d, p.n_min[d] - 1] for d in range(len(dates))], index=dates) for tk, p in panels.items()}
    rng = np.random.default_rng(99)
    premarket = {tk: pd.DataFrame({"pm_high": p.o[:, 0] * 1.01, "pm_low": p.o[:, 0] * 0.99,
                                   "pm_last": p.o[:, 0] * (1 + rng.normal(0, 0.001, len(dates))),
                                   "pm_volume": 1000.0, "pm_bars": 50}, index=dates)
                 for tk, p in panels.items() if tk in ("SOXL", "SOXS")}
    cal = make_calendar(dates, half_days)
    return panels, official, premarket, cal


def _truncate_panel(p: Panel, d_star: int, j_star: int) -> Panel:
    arrays = {}
    for k in list(Panel.FIELDS) + ["c_unadj", "o_unadj", "present"]:
        a = getattr(p, k)[: d_star + 1].copy()
        if a.dtype == bool:
            a[d_star, j_star + 1:] = False
        else:
            a[d_star, j_star + 1:] = np.nan
        arrays[k] = a
    return Panel(p.ticker, p.dates[: d_star + 1], arrays, p.n_min[: d_star + 1])


def _truncated_inputs(panels, official, premarket, d_star, j_star):
    pt = {tk: _truncate_panel(p, d_star, j_star) for tk, p in panels.items()}
    ot = {}
    for tk, s in official.items():
        s2 = s.iloc[: d_star + 1].copy()
        s2.iloc[d_star] = np.nan              # today's official close is not known intraday
        ot[tk] = s2
    mt = {tk: df.iloc[: d_star + 1] for tk, df in premarket.items()}
    return pt, ot, mt


@pytest.mark.parametrize("ticker", ["SOXL", "SOXS"])
@pytest.mark.parametrize("d_star,j_star", [(30, 0), (30, 4), (31, 14), (33, 29), (34, 200), (25, 150), (38, 384)])
def test_features_truncation_invariant(ticker, d_star, j_star):
    panels, official, premarket, cal = _context()
    full = sfeat.compute_features(ticker, panels, official, premarket, cal)
    pt, ot, mt = _truncated_inputs(panels, official, premarket, d_star, j_star)
    trunc = sfeat.compute_features(ticker, pt, ot, mt, cal)
    safe = [k for k in full if not k.startswith("label_")]
    bad = []
    for k in safe:
        a = full[k][: d_star + 1].copy()
        b = trunc[k][: d_star + 1].copy()
        a[d_star, j_star + 1:] = np.nan
        b[d_star, j_star + 1:] = np.nan
        if not np.allclose(a, b, equal_nan=True, rtol=1e-12, atol=1e-12):
            bad.append(k)
    assert not bad, f"look-ahead detected in: {bad}"


def test_labels_are_detected_as_lookahead():
    panels, official, premarket, cal = _context()
    d_star, j_star = 31, 100
    full = sfeat.compute_features("SOXL", panels, official, premarket, cal)
    pt, ot, mt = _truncated_inputs(panels, official, premarket, d_star, j_star)
    trunc = sfeat.compute_features("SOXL", pt, ot, mt, cal)
    for k in ("label_fwd_ret_1m", "label_fwd_ret_5m", "label_fwd_ret_to_close"):
        a, b = full[k][d_star, : j_star + 1], trunc[k][d_star, : j_star + 1]
        assert not np.allclose(a, b, equal_nan=True), k


def test_dictionary_covers_features():
    dd = sfeat.data_dictionary()
    assert {"name", "definition", "granularity", "look_ahead_safe"} <= set(dd.columns)
    assert dd["look_ahead_safe"].sum() >= 30
    assert (~dd["look_ahead_safe"]).sum() >= 1
