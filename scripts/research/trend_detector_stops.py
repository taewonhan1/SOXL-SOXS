#!/usr/bin/env python3
"""Exploratory follow-up to Study T1 (post-hoc, after the registered test failed): does the detector's trend-day
skill turn into trade results when the stop is not a fixed 1.5%?

For the Study T1 signals (09:45 and 10:00, SOXL >= 1% from its open), with the registered B2 logistic model's
training top third as the selection, compare the mean net result per trade (%, case B) of all signals vs the top
third, under four stops on SOXL's chart: fixed 1.5% from entry; SOXL's 09:30 open; volatility-scaled = half of
SOXL's prior 20-day median daily range from entry; none. Exit 15:55. Writes trend_detector/stops_exploratory.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
import trend_detector as T
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R
from soxlab.research.rules import FLAT_OPEN

STOPS = ["fixed 1.5%", "SOXL open", "half typical range", "none"]


def main() -> None:
    sig = pd.read_parquet(ROOT / "data" / "research" / "trend_detector_signals.parquet")
    ctx = C.Context(start=T.START, end=T.END)
    L = ctx["SOXL"]
    p = L.p
    med20 = R._prior_window_stat(L.range_pct, 20, np.median, 10)
    cms = {"B": C.cost_model(C.COMMISSION_B)}
    rows = []
    for chk, g in sig.groupby("check"):
        g = g.reset_index(drop=True)
        _, top = T.logistic(g)
        b = T.CHECKS[chk]
        for stop in STOPS:
            it = []
            for d, s in zip(g["d"].to_numpy(), g["s"].to_numpy()):
                flat = int(p.n_min[d]) - FLAT_OPEN
                if b + 1 >= flat or not np.isfinite(p.o[d, b + 1]):
                    continue
                ep = p.o[d, b + 1]
                lvl = {"fixed 1.5%": ep * (1 - s * 0.015), "SOXL open": L.o0[d],
                       "half typical range": ep * (1 - s * 0.5 * med20[d]) if np.isfinite(med20[d]) else np.nan,
                       "none": np.nan}[stop]
                it.append({"d": int(d), "sig": b, "e": b + 1, "s": int(s), "tx": flat, "tx_kind": "open", "stop": lvl})
            ex = E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], cms)
            net = pd.Series(ex["net_B"].to_numpy() / 100, index=ex["d"].to_numpy().astype(int)).reindex(g["d"]).to_numpy()
            for era in T.ERAS:
                m = (g["era"] == era).to_numpy() & np.isfinite(net)
                for name, sel in (("all signals", m), ("detector top third", m & top)):
                    x = net[sel]
                    rows.append({"check": chk, "stop": stop, "era": era, "selection": name, "trades": len(x),
                                 "trend_share": g.loc[sel, "T1"].mean(), "win": (x > 0).mean(), "net_pct": x.mean()})
    out = pd.DataFrame(rows)
    out.to_csv(T.OUT / "stops_exploratory.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    print(out.pivot_table(index=["check", "stop", "selection"], columns="era", values="net_pct", sort=False).round(2).to_string())


if __name__ == "__main__":
    main()
