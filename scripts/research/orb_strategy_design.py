#!/usr/bin/env python3
"""Stop / target / trade-management design for the 15-minute opening-range breakout (exploratory).

Design sample = 2019-01-02 .. 2024-09-30 (pre + dev). The Oct 2024 - Dec 2025 validation period is used only to
check the rules picked on the design sample; the 2026 holdout stays sealed. Entry filters come from
orb_conditions.py, which looked at 2019-2025, so validation is not a clean test of the filters (it is for the
stop / target choice).

Grid (144 configurations):
  filter  F0 all breaks | F1 skip breaks against a gap > 1% | F2 = F1 + skip breakout minutes < 1.5x normal volume
  stop    OR  = the other side of the 15-minute range | MID = the middle of the range
  exit    HOLD to 15:55 | T2 = 2R target | T3 = 3R target | SO2 = half at 2R, the rest held to 15:55
  steps   none | BE1 = stop to entry once +1R is reached | BE1L2 = BE1, then stop to +1R once +2R is reached
  tstop   none | T11 = out at 11:01 if the trade is not in profit at the 11:00 close
Bearish signals are executed as short SOXL (mode switch_short); the chosen rules are also shown with SOXS.
Selection (fixed before looking at the grid): the highest worse-period mean net per trade, min(pre, dev); a
second pick is the best configuration by that criterion whose design win rate is >= 55%.
Writes analysis/strategies/orb_strategy/.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R
from trend_days import qqq_above_ma50

OUT = C.RESEARCH_DIR / "orb_strategy"
LAST_DAY = "2025-12-31"
STEPS = {"none": (), "BE1": ((1.0, 0.0),), "BE1L2": ((1.0, 0.0), (2.0, 1.0))}
TSTOP = {"none": None, "T11": (89, 0.0)}           # bar 89 closes at 11:00
_CACHE: dict = {}


def orb_intents(ctx, sig: str = "SOXL", filt: str = "F1", stop_kind: str = "OR", exit_: str = "HOLD",
                leg: str | None = None) -> pd.DataFrame:
    td = ctx[sig]
    p = td.p
    if sig not in _CACHE:
        base = R.s3_intents(ctx, sig=sig, design="A")
        vm = td.minute_mean_prior(np.where(p.valid(), p.v, np.nan), 20)
        d, j = base["d"].to_numpy().astype(int), base["sig"].to_numpy().astype(int)
        base = base.assign(gap_dir=(td.o0 / td.pc - 1)[d] * 100 * base["s"].to_numpy(),
                           trig_vol=p.v[d, j] / vm[d, j])
        _CACHE[sig] = base
    it = _CACHE[sig].copy()
    if filt in ("F1", "F2"):
        it = it[~(it["gap_dir"] < -1)]
    if filt == "F2":
        it = it[it["trig_vol"] >= 1.5]
    d, e, s = (it[c].to_numpy().astype(int) for c in ("d", "e", "s"))
    ep = p.o[d, e]
    if stop_kind == "MID":
        it["stop"] = ((np.nanmax(p.h[:, :15], axis=1) + np.nanmin(p.l[:, :15], axis=1)) / 2)[d]
    Rp = np.abs(ep - it["stop"].to_numpy())
    ok = np.isfinite(ep) & (s * (ep - it["stop"].to_numpy()) > 0)
    tr_r = {"HOLD": np.nan, "T2": 2.0, "T3": 3.0, "SO2": (2.0 if leg == "A" else np.nan)}[exit_]
    it["target"] = ep + s * tr_r * Rp if np.isfinite(tr_r) else np.nan
    return E.make_intents(it[ok].drop(columns=["gap_dir", "trig_vol"]).to_dict("records"))


def run_config(ctx, cms, filt, stop_kind, exit_, steps, tstop, mode="switch_short", sig="SOXL"):
    legs = ("A", "B") if exit_ == "SO2" else (None,)
    exs, skipped = [], None
    for lg in legs:
        it = orb_intents(ctx, sig=sig, filt=filt, stop_kind=stop_kind, exit_=exit_, leg=lg)
        tr = E.simulate(ctx[sig], it, one_position=False, stop_steps=STEPS[steps], time_stop=TSTOP[tstop])
        stops = pd.DataFrame({"d": it["d"].to_numpy().astype(int), "e": it["e"].to_numpy().astype(int),
                              "stop": it["stop"].to_numpy(float)})
        rb = tr[["d", "e", "ep"]].merge(stops, on=["d", "e"], how="left")
        rb["R_bps"] = np.abs(rb["ep"] - rb["stop"]) / rb["ep"] * 1e4            # risk on the signal chart
        ex, sk = E.execute(tr, ctx, mode=mode if sig == "SOXL" else "ls", sig=sig)
        ex = E.add_stop_slippage(E.add_costs(ex, cms))
        ex = ex.merge(rb[["d", "e", "R_bps"]], on=["d", "e"], how="left")
        exs.append(ex)
        skipped = sk
    ex = E.merge_legs(exs, legs) if len(exs) > 1 else exs[0]
    ex = ex[ex["date"] <= LAST_DAY].copy()
    ex["period"] = C.period_of(ex["date"])
    return ex, skipped


def metrics(ex: pd.DataFrame, per: str) -> dict:
    g = ex if per == "all" else (ex[ex["period"].isin(["pre", "dev"])] if per == "design" else ex[ex["period"] == per])
    x = g["net_B"].to_numpy(float)
    if not len(x):
        return {}
    mu, t, _ = C.cluster_t(x, g["date"].to_numpy())
    cum = np.cumsum(x)
    pos, neg = x[x > 0].sum(), -x[x < 0].sum()
    return {f"{per}_n": len(x), f"{per}_win": float((x > 0).mean()), f"{per}_net": mu, f"{per}_t": t,
            f"{per}_total_pct": x.sum() / 100, f"{per}_maxdd_pct": float((cum - np.maximum.accumulate(cum)).min()) / 100,
            f"{per}_pf": pos / neg if neg > 0 else np.nan, f"{per}_avg_R": float(np.nanmean(x / g["R_bps"].to_numpy())),
            f"{per}_net_S": float(g["net_S"].mean())}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context()
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    rows, trades = [], {}
    grid = list(itertools.product(("F0", "F1", "F2"), ("OR", "MID"), ("HOLD", "T2", "T3", "SO2"),
                                  tuple(STEPS), tuple(TSTOP)))
    for filt, stop_kind, exit_, steps, tstop in grid:
        cid = f"{filt}|{stop_kind}|{exit_}|{steps}|{tstop}"
        ex, _ = run_config(ctx, cms, filt, stop_kind, exit_, steps, tstop)
        trades[cid] = ex
        r = {"config": cid, "filter": filt, "stop": stop_kind, "exit": exit_, "steps": steps, "time_stop": tstop}
        for per in ("pre", "dev", "design", "val", "all"):
            r.update(metrics(ex, per))
        r["design_worst_period_net"] = min(r["pre_net"], r["dev_net"])
        rows.append(r)
    grid_df = pd.DataFrame(rows).sort_values("design_worst_period_net", ascending=False)
    grid_df.to_csv(OUT / "grid.csv", index=False, float_format="%.4f")
    pick_pnl = grid_df.iloc[0]["config"]
    hw = grid_df[grid_df["design_win"] >= 0.55]
    pick_wr = hw.iloc[0]["config"] if len(hw) else None
    base = "F0|OR|HOLD|none|none"
    final = []
    q = qqq_above_ma50(ctx.dates)
    for label, cid in (("as tested (S8-01)", base), ("pick: P&L", pick_pnl), ("pick: win rate >= 55%", pick_wr)):
        if cid is None:
            continue
        f, sk_, ex_, st_, ts_ = cid.split("|")
        for mode in ("switch_short", "switch"):
            ex, _ = run_config(ctx, cms, f, sk_, ex_, st_, ts_, mode=mode)
            r = {"rule": label, "config": cid, "bearish_via": "short SOXL" if mode == "switch_short" else "buy SOXS"}
            for per in ("pre", "dev", "val", "all"):
                r.update(metrics(ex, per))
            qb = q[ex["d"].to_numpy().astype(int)] == 0
            r["all_net_qqq_below"], r["all_net_qqq_above"] = ex.loc[qb, "net_B"].mean(), ex.loc[~qb, "net_B"].mean()
            r["exit_mix"] = ", ".join(f"{k} {v:.0%}" for k, v in ex["reason"].value_counts(normalize=True).head(5).items())
            final.append(r)
            if mode == "switch_short" and label != "as tested (S8-01)":
                ex.to_csv(OUT / f"trades_{label.split(':')[1].strip().split()[0].replace('&', '')}.csv", index=False,
                          float_format="%.4f")
    fin = pd.DataFrame(final)
    fin.to_csv(OUT / "final_rules.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 40)
    show = ["config", "design_n", "design_win", "design_net", "pre_net", "dev_net", "design_avg_R", "design_maxdd_pct",
            "val_n", "val_win", "val_net", "val_t", "val_maxdd_pct"]
    print("== top 15 by worse design-period mean\n" + grid_df[show].head(15).round(2).to_string(index=False))
    print("\n== top 10 with design win rate >= 55%\n" + hw[show].head(10).round(2).to_string(index=False))
    print("\n== by component (mean over the other settings, design net / val net)")
    for col in ("filter", "stop", "exit", "steps", "time_stop"):
        print(grid_df.groupby(col)[["design_win", "design_net", "val_win", "val_net"]].mean().round(2).to_string(), "\n")
    print("== final rules\n" + fin.round(2).T.to_string())
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
