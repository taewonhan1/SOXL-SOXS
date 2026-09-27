"""Harness tests: execution timing, intra-bar resolution, session flattening, costs, no look-ahead."""
from __future__ import annotations

import numpy as np
import pandas as pd

from conftest import make_panel
from soxlab import backtest as bt
from soxlab import config
from soxlab.costs import CostModel


def _sig_on_bar_return(p):
    """Signal = sign of the just-closed bar's return (known at that bar's close)."""
    r = np.log(p.c / p.o)
    E = np.sign(np.nan_to_num(r)).astype(np.int8)
    E[:, :1] = 0
    return E


def test_entry_is_next_bar_open():
    p = make_panel(n_days=3, seed=3)
    E = np.zeros(p.c.shape, np.int8)
    E[0, 10] = 1
    E[1, 200] = -1
    tr = bt.simulate(p, E, bt.Rules(max_hold=5))
    assert len(tr) == 2
    for _, t in tr.iterrows():
        assert t.entry_bar == t.sig_bar + 1
        assert t.entry_px == p.o[t.day_idx, t.entry_bar]
        assert t.exit_bar == t.entry_bar + 5
        assert t.exit_px == p.o[t.day_idx, t.exit_bar]
        # the signal bar closes at 09:30 + sig_bar + 1 minutes == entry bar start: never earlier
        assert t.entry_min_et >= config.RTH_START_MIN + t.sig_bar + 1


def test_stop_first_when_both_touched():
    p = make_panel(n_days=1, seed=4, sigma=1e-6)
    E = np.zeros(p.c.shape, np.int8)
    E[0, 50] = 1
    e = 51
    ep = p.o[0, e]
    k = 55  # bar that touches both levels
    p.h[0, k] = ep * 1.02
    p.l[0, k] = ep * 0.98
    tr = bt.simulate(p, E, bt.Rules(stop_bps=100, tp_bps=100))
    t = tr.iloc[0]
    assert t.exit_reason == "stop"
    assert t.exit_bar == k
    assert np.isclose(t.exit_px, ep * 0.99)
    assert t.gross_bps < 0


def test_stop_gap_through_fills_at_open():
    p = make_panel(n_days=1, seed=5, sigma=1e-6)
    E = np.zeros(p.c.shape, np.int8)
    E[0, 20] = 1
    ep = p.o[0, 21]
    p.o[0, 30] = ep * 0.95          # opens below the 1% stop
    p.l[0, 30] = ep * 0.94
    p.h[0, 30] = ep * 0.96
    tr = bt.simulate(p, E, bt.Rules(stop_bps=100))
    t = tr.iloc[0]
    assert t.exit_reason == "stop" and t.exit_bar == 30
    assert np.isclose(t.exit_px, ep * 0.95)   # worse than the stop level


def test_flat_by_1555_and_half_day():
    p = make_panel(n_days=4, seed=6, half_days=(2,))
    E = np.ones(p.c.shape, np.int8)      # always wants to be long
    tr = bt.simulate(p, E, bt.Rules())
    assert len(tr) > 0
    for _, t in tr.iterrows():
        flat_idx = p.n_min[t.day_idx] - config.FLAT_BEFORE_CLOSE_MIN
        assert t.entry_bar < flat_idx
        assert t.exit_bar <= flat_idx
    last_exit = tr.groupby("day_idx")["exit_min_et"].max()
    assert last_exit.loc[2] == config.RTH_START_MIN + 210 - 5           # 12:55 on the half-day
    assert last_exit.drop(2).max() == config.RTH_START_MIN + 390 - 5     # 15:55 otherwise


def test_same_bar_signal_has_no_edge_on_iid_data(iid_panel):
    """On an iid random walk, the just-closed bar's return is useless for the NEXT bar. A harness that
    (wrongly) filled at the signal bar's own open would show a large positive edge."""
    p = iid_panel
    E = _sig_on_bar_return(p)
    tr = bt.simulate(p, E, bt.Rules(max_hold=1))
    t_stat = tr.gross_bps.mean() / tr.gross_bps.std() * np.sqrt(len(tr))
    assert abs(t_stat) < 4, t_stat
    cheat = bt.simulate(p, bt.lag_entries(E, -1), bt.Rules(max_hold=1))   # look-ahead diagnostic
    assert cheat.gross_bps.mean() > 5 * abs(tr.gross_bps.mean()) + 1.0


def test_lagged_and_shuffled_signals_on_ar1(ar_panel):
    """AR(1) returns (phi=0.3): edge exists at lag 0, decays with one extra bar of delay, vanishes when shuffled."""
    p = ar_panel
    E = _sig_on_bar_return(p)
    g0 = bt.simulate(p, E, bt.Rules(max_hold=1)).gross_bps
    g1 = bt.simulate(p, bt.lag_entries(E, 1), bt.Rules(max_hold=1)).gross_bps
    gs = bt.simulate(p, bt.shuffle_days(E, seed=7), bt.Rules(max_hold=1)).gross_bps
    t0 = g0.mean() / g0.std() * np.sqrt(len(g0))
    ts = gs.mean() / gs.std() * np.sqrt(len(gs))
    assert t0 > 10
    assert g0.mean() > g1.mean()
    assert abs(ts) < 4


def test_cost_model_units_and_sell_side_fees():
    cm = CostModel(spread_table=pd.DataFrame({
        "ticker": ["X", "X"], "year": [2024, 2024], "bucket_start_et": ["09:30", "10:00"],
        "bucket_end_et": ["10:00", "16:00"], "median_spread_cents": [2.0, 1.0]}).assign(
        b0=[570, 600], b1=[600, 960]), commission_per_share=0.0, notional=10_000)
    # 1 cent spread at $20 -> half-spread 0.5c = 2.5 bps
    hs = cm.half_spread_bps("X", [2024], [config.RTH_START_MIN + 60], [20.0])
    assert np.isclose(hs[0], 2.5)
    hs_open = cm.half_spread_bps("X", [2024], [config.RTH_START_MIN + 1], [20.0])
    assert np.isclose(hs_open[0], 5.0)
    # nearest-year fallback
    assert np.isclose(cm.half_spread_bps("X", [2031], [config.RTH_START_MIN + 60], [20.0])[0], 2.5)
    tr = pd.DataFrame({"date": pd.to_datetime(["2024-06-03", "2024-06-03"]), "side": [1, -1],
                       "entry_min_et": [config.RTH_START_MIN + 60] * 2, "exit_min_et": [config.RTH_START_MIN + 90] * 2,
                       "entry_px_unadj": [20.0, 20.0], "exit_px_unadj": [20.0, 20.0], "gross_bps": [0.0, 0.0]})
    out = cm.trade_costs(tr, "X")
    sec_bps = 27.80 / 1e6 * 1e4          # SEC rate in force on 2024-06-03 (from 2024-05-22)
    taf_bps = 0.000166 * (10_000 / 20.0) / 10_000 * 1e4
    assert np.allclose(out["cost_spread_bps"], 5.0)
    assert np.allclose(out["cost_fees_bps"], sec_bps + taf_bps)
    assert np.allclose(out["net_bps"], -(5.0 + sec_bps + taf_bps))
    # SEC fee schedule changes with date
    assert np.isclose(cm.sec_fee_bps(["2025-06-02"])[0], 0.0)
    assert np.isclose(cm.sec_fee_bps(["2026-05-01"])[0], 20.60 / 100)


def test_costs_use_unadjusted_price():
    p = make_panel(n_days=2, seed=8, factor=10.0)          # unadjusted = 10x adjusted
    E = np.zeros(p.c.shape, np.int8)
    E[0, 30] = 1
    cm = CostModel(fixed_half_spread_bps=None, commission_per_share=0.01, notional=10_000,
                   spread_table=pd.DataFrame({"ticker": ["SYN"], "year": [2023], "bucket_start_et": ["04:00"],
                                              "bucket_end_et": ["20:00"], "median_spread_cents": [1.0]}).assign(b0=[240], b1=[1200]))
    tr = bt.simulate(p, E, bt.Rules(max_hold=3), cost_model=cm)
    t = tr.iloc[0]
    assert np.isclose(t.entry_px_unadj, 10 * t.entry_px)
    assert np.isclose(t.cost_comm_bps, 0.01 / t.entry_px_unadj * 1e4 + 0.01 / t.exit_px_unadj * 1e4)


def test_metrics_and_random_baseline(iid_panel):
    p = iid_panel
    E = _sig_on_bar_return(p)
    cm = CostModel(fixed_half_spread_bps=1.0, commission_per_share=0.0)
    tr = bt.simulate(p, E, bt.Rules(max_hold=5), cost_model=cm)
    m = bt.metrics(tr, p.dates, bt.session_minutes(p, p.dates))
    assert m["n_trades"] == len(tr)
    assert 0 <= m["exposure"] <= 1
    assert np.isclose(m["avg_net_bps"], m["avg_gross_bps"] - m["avg_cost_bps"])
    rb = bt.random_entry_baseline(p, tr, cm, n_iter=20, seed=1)
    assert len(rb) == 20 and np.all(np.isfinite(rb["avg_net_bps"]))
    # iid data: random entries have ~zero gross edge
    assert abs(rb["avg_gross_bps"].mean()) < 3
