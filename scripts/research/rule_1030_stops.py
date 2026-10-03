#!/usr/bin/env python3
"""Stop placement for the 10:30 rule (SOXL 3-4% from its open at the 10:29 close -> go with it at the next open,
exit 15:55): is the stop at SOXL's open too far away?

Stops compared (all on SOXL's chart; SOXS trades mirror them): none; SOXL's 09:30 open (the rule as found); half the
morning move retraced; fixed 3 / 2.5 / 2 / 1.5 / 1% from the entry price. Case B costs, plus case S (1 cent of
extra slippage per stop fill). Reported per trade in % (same position size every trade) and in R (net / stop
distance: same dollar risk every trade), pooled and per era, for all days and for days with two or more pre-open
flags (trend_day_predictors.py: hot volatility regime, yesterday a trend day, QQQ below its 50-day, big gap).
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
    by_era.to_csv(OUT / "by_era.csv", float_format="%.4f")
    pd.set_option("display.width", 250)
    print(pooled.round(2).to_string())
    print("\n" + by_era.round(3).to_string())
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
