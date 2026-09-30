#!/usr/bin/env python3
"""Why the 2011-2018 deep-history test failed (run after orb_best.py --deep).

For the plain 15-minute breakout and S14-A in both eras (2011-06..2018 and 2019..2025): gross vs cost vs net, and
the share and result of trend / medium / quiet days; the breakout by trailing volatility regime; the pre-registered
noise-boundary (S4-02, S4-04) and late-day fade (S1-06) rules on 2011-2018; and a performance switch (trade only
while the previous N signals averaged > 0). Writes analysis/strategies/orb_best/deep_diagnostics_*.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from orb_best import OUT, run
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R

ERAS = (("2011-2018", "2011-06-01", "2018-12-31"), ("2019-2025", "2019-01-02", "2025-12-31"))


def main() -> None:
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    decomp, regime, others, switch = [], [], [], []
    for label, start, end in ERAS:
        ctx = C.Context(start=start, end=end)
        X, L = ctx["SOXX"], ctx["SOXL"]
        oc = np.abs(X.last_c / X.o0 - 1)
        dtype = pd.Series(np.where(oc >= 0.02, "trend", np.where(oc >= 0.01, "medium", "quiet")), index=ctx.dates)
        reg = R._prior_window_stat(L.range_pct, 20, np.median, 10) * 100
        for rule, cfg in (("plain 15-min breakout", "15|none|RNG|none|HOLD|SOXS"), ("S14-A", "15|PM|CAP4|1200|HOLD|SOXS")):
            a = cfg.split("|")
            ex = run(ctx, cms, int(a[0]), a[1], a[2], a[3], a[4], a[5])
            ex = ex[ex["date"] <= end].sort_values(["date", "e"]).reset_index(drop=True)
            ex["dtype"] = dtype.reindex(ex["date"]).to_numpy()
            r = {"era": label, "rule": rule, "trades": len(ex), "gross_bps": ex["gross_bps"].mean(),
                 "cost_bps": ex["cost_B"].mean(), "net_bps": ex["net_B"].mean()}
            for t in ("trend", "medium", "quiet"):
                g = ex[ex["dtype"] == t]
                r[f"{t}_share"], r[f"{t}_net_bps"] = len(g) / len(ex), g["net_B"].mean()
            decomp.append(r)
            if rule.startswith("plain"):
                ex["regime"] = pd.cut(reg[ex["d"].to_numpy().astype(int)], [0, 4, 5, 6, 8, 99], right=False,
                                      labels=["<4%", "4-5%", "5-6%", "6-8%", ">=8%"])
                for b, g in ex.groupby("regime", observed=True):
                    regime.append({"era": label, "soxl_20d_median_range": b, "trades": len(g),
                                   "gross_bps": g["gross_bps"].mean(), "cost_bps": g["cost_B"].mean(),
                                   "net_bps": g["net_B"].mean()})
                x = ex["net_B"].to_numpy()
                for w in (0, 40, 60, 100, 150):
                    take = np.ones(len(x), bool) if w == 0 else \
                        np.nan_to_num(pd.Series(x).rolling(w).mean().shift(1).to_numpy(), nan=-1) > 0
                    g = ex[take]
                    switch.append({"era": label, "switch": "always on" if w == 0 else f"last {w} signals avg > 0",
                                   "trades": int(take.sum()), "net_bps": g["net_B"].mean(),
                                   "total_pct": g["net_B"].sum() / 100})
        for rule, fn, is_tr, prm in (("S4-02", R.s4_trades, True, dict(k=1.0, check="H")),
                                     ("S4-04", R.s4_trades, True, dict(k=1.5, check="H")),
                                     ("S1-06", R.s1_intents, False,
                                      dict(thr=0.01, gate=False, exit_="E3", exec_mode="switch"))):
            obj = fn(ctx, sig="SOXL", **prm)
            tr = obj if is_tr else E.simulate(ctx["SOXL"], obj)
            ex = E.add_costs(E.execute(tr, ctx, mode="switch")[0], cms)
            ex = ex[ex["date"] <= end]
            mu, t, _ = C.cluster_t(ex["net_B"].to_numpy(), ex["date"].to_numpy())
            yr = ex.groupby(ex["date"].dt.year)["net_B"].mean()
            others.append({"era": label, "rule": rule, "trades": len(ex), "gross_bps": ex["gross_bps"].mean(),
                           "cost_bps": ex["cost_B"].mean(), "net_bps": mu, "t": t,
                           "positive_years": f"{int((yr > 0).sum())}/{len(yr)}"})
    pd.set_option("display.width", 250)
    for name, rows in (("decomposition", decomp), ("regime", regime), ("other_rules", others), ("switch", switch)):
        df = pd.DataFrame(rows)
        df.to_csv(OUT / f"deep_diagnostics_{name}.csv", index=False, float_format="%.4f")
        print(f"\n== {name}\n" + df.round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/deep_diagnostics_*.csv")


if __name__ == "__main__":
    main()
