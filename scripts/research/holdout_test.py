#!/usr/bin/env python3
"""One-time 2026 holdout test (REGISTRY.md: "Final strategy S15 and the one-time 2026 holdout test").

Opens 2026-01-02 .. 2026-09-25 for the registered rules. Primary: S15 (= S3-01, the plain 15-minute breakout);
it passes if both its case-B and case-Q (real NBBO fills) mean net per trade are >= 0. S15-K (60-signal kill
switch), S8-01, S4-02, S4-04, S13-A and S14-A are reported for context. Writes analysis/strategies/holdout_2026/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
import orb_strategy_design as OSD
from orb_best import run as run_s14
from orb_strategy_design import run_config as run_s13
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R

OUT = C.RESEARCH_DIR / "holdout_2026"
HOLD = ("2026-01-02", "2026-09-25")
KILL_WINDOW = 60


def base_rule(ctx, cms, fn, is_tr, mode, **prm) -> pd.DataFrame:
    obj = fn(ctx, sig="SOXL", **prm)
    tr = obj if is_tr else E.simulate(ctx["SOXL"], obj)
    return E.add_costs(E.execute(tr, ctx, mode=mode)[0], cms)


def kill_switch(ex: pd.DataFrame, w: int = KILL_WINDOW) -> np.ndarray:
    """True where the previous w signals (traded or not) averaged > 0 net (case B)."""
    x = ex.sort_values(["date", "e"])["net_B"].to_numpy()
    prior = pd.Series(x).rolling(w).mean().shift(1).to_numpy()
    on = np.nan_to_num(prior, nan=-1) > 0
    return pd.Series(on, index=ex.sort_values(["date", "e"]).index).reindex(ex.index).to_numpy()


def summary(rule: str, g: pd.DataFrame) -> dict:
    x = g["net_B"].to_numpy(float)
    mu, t, _ = C.cluster_t(x, g["date"].to_numpy()) if len(x) > 2 else (np.nan,) * 3
    q = g["net_Q"].to_numpy(float) if "net_Q" in g else np.array([])
    cum = np.cumsum(x)
    return {"rule": rule, "trades": len(x), "win_rate": float((x > 0).mean()) if len(x) else np.nan,
            "net_B_bps": mu, "t": t, "net_Q_bps": float(np.nanmean(q)) if len(q) else np.nan,
            "gross_bps": float(g["gross_bps"].mean()) if len(x) else np.nan,
            "total_pct": x.sum() / 100, "max_dd_pct": float((cum - np.maximum.accumulate(cum)).min()) / 100 if len(x) else np.nan,
            "q_fallback_share": float(g["q_fallback"].mean()) if "q_fallback" in g and len(x) else np.nan}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    OSD.LAST_DAY = HOLD[1]              # run_config trims to its design window by default
    ctx = C.Context()
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    in_hold = lambda ex: (ex["date"] >= HOLD[0]) & (ex["date"] <= HOLD[1])       # noqa: E731
    rules = {
        "S15 (primary: plain 15-min breakout)": base_rule(ctx, cms, R.s3_intents, False, "switch", design="A"),
        "S8-01 (breakout, bearish = short SOXL)": base_rule(ctx, cms, R.s3_intents, False, "switch_short", design="A"),
        "S4-02 (noise-boundary k=1.0)": base_rule(ctx, cms, R.s4_trades, True, "switch", k=1.0, check="H"),
        "S4-04 (noise-boundary k=1.5)": base_rule(ctx, cms, R.s4_trades, True, "switch", k=1.5, check="H"),
        "S13-A": run_s13(ctx, cms, "F1", "OR", "HOLD", "none", "T11", mode="switch")[0],
        "S14-A": run_s14(ctx, cms, 15, "PM", "CAP4", "1200", "HOLD", "SOXS"),
    }
    s15 = rules["S15 (primary: plain 15-min breakout)"]
    rules["S15-K (S15 + 60-signal kill switch)"] = s15[kill_switch(s15)]
    rows, trades = [], []
    for name, ex in rules.items():
        h = ex[in_hold(ex)].copy()
        h = E.add_quote_fills(h, cms["B"], periods=("hold",))
        rows.append(summary(name, h))
        trades.append(h.assign(rule=name))
    res = pd.DataFrame(rows)
    primary = res.iloc[0]
    passed = bool(primary["net_B_bps"] >= 0 and primary["net_Q_bps"] >= 0)
    h15 = trades[0]
    monthly = h15.groupby(h15["date"].dt.to_period("M"))["net_B"].agg(trades="size", mean_bps="mean",
                                                                    total_pct=lambda x: x.sum() / 100)
    X = ctx["SOXX"]
    oc = np.abs(X.last_c / X.o0 - 1)
    dmask = (ctx.dates >= HOLD[0]) & (ctx.dates <= HOLD[1])
    dt = pd.Series(np.where(oc >= 0.02, "trend", np.where(oc >= 0.01, "medium", "quiet")), index=ctx.dates)[dmask]
    day_mix = dt.value_counts(normalize=True).round(3).to_dict()
    ks = kill_switch(s15)
    ks_hold = pd.Series(ks, index=s15.index)[in_hold(s15)]
    res.to_csv(OUT / "summary.csv", index=False, float_format="%.4f")
    monthly.to_csv(OUT / "s15_monthly.csv", float_format="%.4f")
    pd.concat(trades, ignore_index=True).to_csv(OUT / "trades.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    print(res.round(2).to_string(index=False))
    print("\nS15 by month (case B)\n" + monthly.round(2).to_string())
    print(f"\n2026 day mix (SOXX open->close): {day_mix}")
    print(f"S15-K switch on for {ks_hold.mean():.0%} of 2026 signals; state at the last 2026 signal: "
          f"{'ON' if ks_hold.iloc[-1] else 'OFF'}")
    print(f"\nPRIMARY VERDICT (S15): {'PASS' if passed else 'FAIL'} -- case B {primary['net_B_bps']:+.1f} bps, "
          f"case Q {primary['net_Q_bps']:+.1f} bps per trade over {int(primary['trades'])} trades")
    (OUT / "verdict.txt").write_text(f"S15 holdout 2026-01-02..2026-09-25: {'PASS' if passed else 'FAIL'}; "
                                     f"case B {primary['net_B_bps']:+.2f} bps, case Q {primary['net_Q_bps']:+.2f} bps, "
                                     f"{int(primary['trades'])} trades, win rate {primary['win_rate']:.3f}\n")


if __name__ == "__main__":
    main()
