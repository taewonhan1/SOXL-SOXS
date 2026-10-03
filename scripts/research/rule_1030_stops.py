#!/usr/bin/env python3
"""Stop placement for the 10:30 rule (SOXL 3-4% from its open at the 10:29 close -> go with it at the next open,
exit 15:55): is the stop at SOXL's open too far away?

Stops compared (all on SOXL's chart; SOXS trades mirror them): none; SOXL's 09:30 open (the rule as found); half the
morning move retraced; fixed 3 / 2.5 / 2 / 1.5 / 1% from the entry price. Case B costs, plus case S (1 cent of
extra slippage per stop fill). Reported per trade in % (same position size every trade) and in R (net / stop
distance: same dollar risk every trade), pooled and per era, for all days and for days with two or more pre-open
flags (trend_day_predictors.py: hot volatility regime, yesterday a trend day, QQQ below its 50-day, big gap).
Also compares sizing plans with the fixed 1.5% stop, in R (1 R = the dollar risk of one unit): every setup at one
unit; 2+ flag days only; every setup with 1.5 or 2 units on 2+ flag days.
Exploratory: seven variants on the same data.
Writes analysis/strategies/rule_1030_stops/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
import trend_day_predictors as TP
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "rule_1030_stops"
ERAS = (("2011-2018", "2011-06-01", "2018-12-31"), ("2019-2025", "2019-01-02", "2025-12-31"),
        ("2026", "2026-01-02", "2026-09-25"))
HISTORY = {"2011-2018": "2010-06-01", "2019-2025": "2018-01-02", "2026": "2024-10-01"}   # trailing windows
STOPS = ["none", "open (as found)", "50% retrace", "fixed 3%", "fixed 2.5%", "fixed 2%", "fixed 1.5%", "fixed 1%"]


def level(stop: str, o0: float, c_sig: float, ep: float, s: int) -> float:
    if stop == "none":
        return np.nan
    if stop.startswith("open"):
        return o0
    if stop == "50% retrace":
        return o0 + 0.5 * (c_sig - o0)
    return ep * (1 - s * float(stop.split()[1].rstrip("%")) / 100)


def sizing_plans(tr: pd.DataFrame) -> pd.DataFrame:
    """R results of sizing plans on the fixed-1.5% trades (1 R = the dollar risk of one unit)."""
    tr = tr.sort_values(["date", "e"]).reset_index(drop=True)
    hot = (tr["preopen_flags"] >= 2).to_numpy()
    years = {era: (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25 for era, start, end in ERAS}
    plans = {"every setup, 1 unit": np.ones(len(tr)), "2+ flag days only, 1 unit": hot.astype(float),
             "every setup, 1.5 units on 2+ flag days": np.where(hot, 1.5, 1.0),
             "every setup, 2 units on 2+ flag days": np.where(hot, 2.0, 1.0)}
    rows = []
    for name, w in plans.items():
        r = tr["net_R"].to_numpy() * w
        cum = np.cumsum(r)
        dd = (cum - np.maximum.accumulate(cum)).min()
        yr = pd.Series(r).groupby(tr["date"].dt.year.to_numpy()).sum()
        yr = yr[pd.Series(w).groupby(tr["date"].dt.year.to_numpy()).sum() > 0]
        era_r = pd.Series(r).groupby(tr["era"].to_numpy()).sum()
        era_w = pd.Series(w).groupby(tr["era"].to_numpy()).sum()
        rows.append({"plan": name, "trades": int((w > 0).sum()), "total_R": r.sum(),
                     "R_per_year": r.sum() / sum(years.values()), "max_drawdown_R": dd, "worst_year_R": yr.min(),
                     "losing_years": f"{int((yr < 0).sum())}/{len(yr)}", "total_over_max_drawdown": r.sum() / -dd,
                     **{f"R_per_unit_{e}": era_r[e] / era_w[e] for e in years},
                     **{f"R_per_year_{e}": era_r[e] / years[e] for e in years}})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cms = {"B": C.cost_model(C.COMMISSION_B)}
    parts = []
    for era, start, end in ERAS:
        ctx = C.Context(start=HISTORY[era], end=end)
        flags = TP.features(ctx, start)["score_preopen"]
        L = ctx["SOXL"]
        p = L.p
        base = []
        for d in np.flatnonzero((ctx.dates >= start) & (ctx.dates <= end)):
            flat = int(p.n_min[d]) - FLAT_OPEN
            if 60 >= flat or not (np.isfinite(L.o0[d]) and np.isfinite(p.c[d, 59]) and np.isfinite(p.o[d, 60])):
                continue
            m = (p.c[d, 59] / L.o0[d] - 1) * 100
            if 3 <= abs(m) < 4:
                base.append((d, 1 if m > 0 else -1, flat))
        for stop in STOPS:
            it, dist = [], {}
            for d, s, flat in base:
                ep = p.o[d, 60]
                lvl = level(stop, L.o0[d], p.c[d, 59], ep, s)
                dist[d] = abs(ep - lvl) / ep * 100 if np.isfinite(lvl) else np.nan
                it.append({"d": d, "sig": 59, "e": 60, "s": s, "tx": flat, "tx_kind": "open", "stop": lvl})
            ex = E.add_stop_slippage(E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], cms))
            ex["stop_dist_pct"] = pd.Series(dist).reindex(ex["d"].to_numpy().astype(int)).to_numpy()
            ex["preopen_flags"] = flags.reindex(ex["date"]).to_numpy()
            parts.append(ex.assign(era=era, stop_rule=stop))
    ex = pd.concat(parts, ignore_index=True)
    ex["net_pct"], ex["net_S_pct"] = ex["net_B"] / 100, ex["net_S"] / 100
    ex["net_R"] = ex["net_pct"] / ex["stop_dist_pct"]
    sizing = sizing_plans(ex[ex["stop_rule"] == "fixed 1.5%"])
    ex = pd.concat([ex.assign(days="all days"), ex[ex["preopen_flags"] >= 2].assign(days="2+ pre-open flags")],
                   ignore_index=True)

    def summ(g: pd.DataFrame) -> pd.Series:
        g = g.sort_values(["date", "e"])
        x = g["net_pct"].to_numpy()
        cum = np.cumsum(x)
        yr = g.groupby(g["date"].dt.year)["net_pct"].sum()
        return pd.Series({"trades": len(x), "win": (x > 0).mean(), "avg_pct": x.mean(), "avg_pct_S": g["net_S_pct"].mean(),
                          "losing_years": f"{int((yr < 0).sum())}/{len(yr)}", "total_pct": x.sum(),
                          "avg_win_pct": x[x > 0].mean(), "avg_loss_pct": x[x <= 0].mean(), "worst_pct": x.min(),
                          "stopped": g["reason"].isin(["stop", "stop_moved"]).mean(),
                          "max_dd_pct": (cum - np.maximum.accumulate(cum)).min(),
                          "avg_stop_dist_pct": g["stop_dist_pct"].mean(), "avg_R": g["net_R"].mean()})

    key = ["days", "stop_rule"]
    order = pd.MultiIndex.from_product([["all days", "2+ pre-open flags"], STOPS], names=key)
    pooled = ex.groupby(key)[ex.columns.drop(key)].apply(summ).reindex(order)
    by_era = ex.pivot_table(index=key, columns="era", values=["net_pct", "net_R"], aggfunc="mean").reindex(order)
    counts = ex.pivot_table(index=key, columns="era", values="net_pct", aggfunc="size").reindex(order)
    by_era = by_era.join(pd.concat({"trades": counts}, axis=1))
    pooled.to_csv(OUT / "pooled.csv", float_format="%.4f")
    sizing.to_csv(OUT / "sizing_plans_1p5_stop.csv", index=False, float_format="%.4f")
    by_era.to_csv(OUT / "by_era.csv", float_format="%.4f")
    pd.set_option("display.width", 250)
    print(pooled.round(2).to_string())
    print("\n" + by_era.round(3).to_string())
    print("\n" + sizing.round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
