"""Tests for the research harness (soxlab/research): look-ahead safety of every rule, simulator exit
logic, and SOXL->SOXS switch execution. Uses the cached market data (skipped if it is missing)."""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from soxlab import config
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R

pytestmark = pytest.mark.skipif(not (config.BARS_DIR / "adjusted" / "SOXL").exists(),
                                reason="cached minute bars not available")


@pytest.fixture(scope="module")
def ctx():
    return C.Context()


class _Ctx:
    """Context stand-in serving a perturbed TickerData for one ticker."""

    def __init__(self, base, override):
        self.base, self.override = base, override
        self.cal, self.dates = base.cal, base.dates

    def __getitem__(self, k):
        return self.override.get(k) or self.base[k]


def _perturbed(ctx, ticker: str, day: int, after_bar: int, seed: int = 0):
    td = ctx[ticker]
    p = copy.copy(td.p)
    rng = np.random.default_rng(seed)
    for f in ("o", "h", "l", "c", "v", "vw", "c_unadj", "o_unadj"):
        a = getattr(td.p, f).copy()
        k = a[day, after_bar + 1:]
        a[day, after_bar + 1:] = k * (1 + rng.normal(0, 0.05, k.shape)) if f != "v" else k * 3
        setattr(p, f, a)
    p.h = np.fmax(p.h, np.fmax(p.o, p.c))
    p.l = np.fmin(p.l, np.fmin(p.o, p.c))
    return C.TickerData(ticker, p)


def _days_with(intents, sig_max):
    return intents[intents["sig"] <= sig_max][["d", "sig", "e", "s"]].reset_index(drop=True)


@pytest.mark.parametrize("gen,kwargs,bar", [
    (R.s1_intents, {"thr": 0.01, "gate": True, "exit_": "E1"}, 359),
    (R.s2_intents, {"k": 2.0, "hold": 1, "filt": "F1"}, 12),
    (R.s3_intents, {"design": "A", "rvol_min": 1.0}, 25),
    (R.s3_intents, {"design": "B"}, 4),
    (R.s6_intents, {"level": "PM", "target": "T2"}, 20),
])
def test_rules_are_causal(ctx, gen, kwargs, bar):
    base = gen(ctx, **kwargs)
    days = base["d"].unique()
    rng = np.random.default_rng(1)
    for d in rng.choice(days, size=min(5, len(days)), replace=False):
        pert = _Ctx(ctx, {"SOXL": _perturbed(ctx, "SOXL", int(d), bar)})
        a = _days_with(base[base["d"] == d], bar)
        b = gen(pert, **kwargs)
        b = _days_with(b[b["d"] == d], bar)
        pd.testing.assert_frame_equal(a, b)


def test_s4_is_causal(ctx):
    base = R.s4_trades(ctx, k=1.0, check="M")
    rng = np.random.default_rng(2)
    for d in rng.choice(base["d"].unique(), size=3, replace=False):
        first = base[base["d"] == d].sort_values("e").iloc[0]
        cut = int(first["sig"])
        pert = _Ctx(ctx, {"SOXL": _perturbed(ctx, "SOXL", int(d), cut)})
        b = R.s4_trades(pert, k=1.0, check="M")
        b = b[b["d"] == d].sort_values("e").iloc[0]
        assert (int(b["sig"]), int(b["e"]), int(b["s"])) == (cut, int(first["e"]), int(first["s"]))


def test_simulate_stop_first_and_gap(ctx):
    td = ctx["SOXL"]
    d = int(np.flatnonzero(td.full & (td.period == "dev"))[10])
    e = 100
    ep = td.p.o[d, e]
    hi, lo = td.p.h[d, e], td.p.l[d, e]
    # both stop and target inside bar e's range -> stop wins
    it = E.make_intents([{"d": d, "sig": e - 1, "e": e, "s": 1, "stop": lo + 1e-9, "target": hi - 1e-9,
                          "tx": 200}])
    tr = E.simulate(td, it)
    if lo < ep < hi:
        assert tr.iloc[0]["reason"] == "stop"
    # stop above the open for a long -> gap fill at the entry bar's open
    it = E.make_intents([{"d": d, "sig": e - 1, "e": e, "s": 1, "stop": ep * 1.5, "tx": 200}])
    tr = E.simulate(td, it)
    assert tr.iloc[0]["x_kind"] == "gap" and np.isclose(tr.iloc[0]["xp"], ep)
    # time exit at the close of the last bar and at the official close
    for kind in ("close", "official"):
        it = E.make_intents([{"d": d, "sig": 359, "e": 360, "s": 1, "tx": 389, "tx_kind": kind}])
        tr = E.simulate(td, it)
        want = td.p.c[d, 389] if kind == "close" else td.off[d]
        assert tr.iloc[0]["x_kind"] == kind and np.isclose(tr.iloc[0]["xp"], want)


def test_switch_execution(ctx):
    L, S = ctx["SOXL"], ctx["SOXS"]
    ok_days = np.flatnonzero(L.full & (S.pc_u >= 10) & (L.period == "val"))
    bad_days = np.flatnonzero(L.full & (S.pc_u < 10) & (L.period == "val"))
    d_ok, d_bad = int(ok_days[5]), int(bad_days[5])
    rows = [{"d": d_ok, "sig": 99, "e": 100, "s": -1, "tx": 130}, {"d": d_bad, "sig": 99, "e": 100, "s": -1, "tx": 130},
            {"d": d_ok, "sig": 199, "e": 200, "s": 1, "tx": 230}]
    tr = E.simulate(L, E.make_intents(rows))
    ex, sk = E.execute(tr, ctx, mode="switch")
    assert len(sk) == 1 and int(sk.iloc[0]["d"]) == d_bad
    bear = ex[ex["inst"] == "SOXS"].iloc[0]
    assert bear["side"] == 1 and np.isclose(bear["ep"], S.p.o[d_ok, 100]) and np.isclose(bear["xp"], S.p.o[d_ok, 130])
    bull = ex[ex["inst"] == "SOXL"].iloc[0]
    assert bull["side"] == 1 and np.isclose(bull["ep"], L.p.o[d_ok, 200])
    # intrabar level exit on SOXL maps into the SOXS bar range
    ep = L.p.o[d_ok, 100]
    it = E.make_intents([{"d": d_ok, "sig": 99, "e": 100, "s": -1, "stop": ep * 1.0005, "tx": 380}])
    trl = E.simulate(L, it)
    exl, _ = E.execute(trl, ctx, mode="switch")
    r = exl.iloc[0]
    xb = int(r["xb"])
    assert S.p.l[d_ok, xb] - 1e-9 <= r["xp"] <= S.p.h[d_ok, xb] + 1e-9
    # costs: case B >= case A, and net = gross - cost
    exc = E.add_costs(ex, {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)})
    assert (exc["cost_B"] >= exc["cost_A"]).all()
    assert np.allclose(exc["net_B"], exc["gross_bps"] - exc["cost_B"])


@pytest.mark.parametrize("gen,kwargs", [
    (R.s10_hh_intents, {"entry": "stop", "exit_": "X2R", "window_end": 44}),
    (R.s10_hh_intents, {"entry": "close", "exit_": "XSO", "window_end": 44, "leg": "A"}),
    (R.s11_bz_intents, {"entry": "close", "exit_": "XT"}),
    (R.s11_bz_intents, {"entry": "stop", "exit_": "XS"}),
    (R.s12_flag_intents, {"entry": "stop", "exit_": "XM"}),
    (R.s12_flag_intents, {"entry": "close", "exit_": "X2R"}),
])
def test_scalp_rules_are_causal(ctx, gen, kwargs):
    """Studies 10-12: every intent entered at or before bar ``cut`` is unchanged when the bars after
    ``cut`` are scrambled (stop-order entries fill inside bar e, so the check is on the entry bar)."""
    cols = ["d", "sig", "e", "s", "stop", "target", "tx", "entry_px"]
    base = gen(ctx, **kwargs)
    rng = np.random.default_rng(3)
    for d in rng.choice(base["d"].unique(), size=3, replace=False):
        cut = int(base[base["d"] == d]["e"].min())
        pert = _Ctx(ctx, {"SOXL": _perturbed(ctx, "SOXL", int(d), cut)})
        b = gen(pert, **kwargs)
        a = base[(base["d"] == d) & (base["e"] <= cut)][cols].reset_index(drop=True)
        b = b[(b["d"] == d) & (b["e"] <= cut)][cols].reset_index(drop=True)
        assert len(a) >= 1
        pd.testing.assert_frame_equal(a, b)


def test_level_entry_and_scale_out_legs(ctx):
    td = ctx["SOXL"]
    d = int(np.flatnonzero(td.full & (td.period == "val"))[20])
    e = 120
    lvl = float(td.p.l[d, e] + 0.5 * (td.p.h[d, e] - td.p.l[d, e]))
    # a stop-order entry fills at its level inside bar e; no target can fill on the entry bar
    it = E.make_intents([{"d": d, "sig": e - 1, "e": e, "s": 1, "entry_px": lvl, "stop": lvl * 0.9,
                          "target": td.p.h[d, e] - 1e-9, "tx": e + 30}])
    tr = E.simulate(td, it)
    assert tr.iloc[0]["e_kind"] == "level" and np.isclose(tr.iloc[0]["ep"], lvl) and tr.iloc[0]["xb"] > e
    # paired legs: the second signal (entry e+5) must be dropped while leg B (time exit e+30) is still open,
    # even though leg A is already out
    rows = [{"d": d, "sig": e - 1, "e": e, "s": 1, "stop": np.nan, "target": np.nan, "tx": e + 2},
            {"d": d, "sig": e + 4, "e": e + 5, "s": 1, "stop": np.nan, "target": np.nan, "tx": e + 7}]
    leg_a = E.simulate(td, E.make_intents(rows), one_position=False)
    leg_b = E.simulate(td, E.make_intents([{**r, "tx": r["tx"] + 28} for r in rows]), one_position=False)
    fa, fb = E.filter_positions([leg_a, leg_b], max_per_day=3)
    assert len(fa) == len(fb) == 1 and int(fa.iloc[0]["e"]) == e
    exs = [E.add_costs(E.execute(x, ctx, mode="switch")[0], {"B": C.cost_model(C.COMMISSION_B)}) for x in (fa, fb)]
    m = E.merge_legs(exs)
    assert len(m) == 1 and int(m.iloc[0]["xb"]) == e + 30
    assert np.isclose(m.iloc[0]["net_B"], (exs[0].iloc[0]["net_B"] + exs[1].iloc[0]["net_B"]) / 2)
    assert np.isclose(m.iloc[0]["gross_bps"], (m.iloc[0]["xp"] / m.iloc[0]["ep"] - 1) * 1e4)
