#!/usr/bin/env python3
"""Midday trend check (exploratory, requested): if SOXL has already moved at least k% from its open by a check
time, go with the move and hold to 15:55.

Grid fixed before running (all cells reported, nothing selected):
  check time  11:00 | 12:00 | 13:00   (close of bars 89 / 149 / 209)
  move k      2% | 3% | 4% | 6%       (SOXL open -> check-time close; SOXL is about 3x SOXX)
  stop        none | OPEN = exit if SOXL gets back to its opening price (the day's move fully erased)
Entry at the next bar's open: up -> buy SOXL, down -> buy SOXS (prior close >= $10, else skip); exit at the open
of bar n_min - 5 (15:55). Case B costs (measured spreads per era). Eras: 2011-06..2018, 2019..2025, 2026-01..09.
A cell "works" only if its net per trade is > 0 in all three eras. Writes analysis/strategies/midday_trend/.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "midday_trend"
ERAS = (("2011-2018", "2011-06-01", "2018-12-31"), ("2019-2025", "2019-01-02", "2025-12-31"),
        ("2026", "2026-01-02", "2026-09-25"))
CHECK = {"11:00": 89, "12:00": 149, "13:00": 209}


def intents(ctx, bar: int, k: float, stop: str) -> pd.DataFrame:
    L = ctx["SOXL"]
    p = L.p
    rows = []
    for d in range(len(ctx.dates)):
        flat = int(p.n_min[d]) - FLAT_OPEN
        if bar + 1 >= flat or not np.isfinite(L.o0[d]) or not np.isfinite(p.c[d, bar]):
            continue
        m = p.c[d, bar] / L.o0[d] - 1
        if abs(m) < k / 100:
            continue
        s = 1 if m > 0 else -1
        rows.append({"d": d, "sig": bar, "e": bar + 1, "s": s, "tx": flat, "tx_kind": "open",
                     "stop": L.o0[d] if stop == "OPEN" else np.nan})
    return E.make_intents(rows)


def midday_intents(ctx, sig: str = "SOXL", check: str = "11:00", k: float = 3.0, stop: str = "OPEN") -> pd.DataFrame:
    """Strategy S16 (REGISTRY.md) for the paper log: 11:00 check, 3% move, stop back at the open."""
    return intents(ctx, CHECK[check], k, stop)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    rows = []
    for era, start, end in ERAS:
        ctx = C.Context(start="2025-10-01" if era == "2026" else start, end=end)
        years = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
        for (tname, bar), k, stop in itertools.product(CHECK.items(), (2, 3, 4, 6), ("none", "OPEN")):
            it = intents(ctx, bar, k, stop)
            tr = E.simulate(ctx["SOXL"], it)
            ex = E.add_costs(E.execute(tr, ctx, mode="switch")[0], cms)
            ex = ex[(ex["date"] >= start) & (ex["date"] <= end)]
            x = ex["net_B"].to_numpy(float)
            mu, t, _ = C.cluster_t(x, ex["date"].to_numpy()) if len(x) > 2 else (np.nan,) * 3
            rows.append({"era": era, "check": tname, "move_k_pct": k, "stop": stop, "trades": len(x),
                         "trades_per_year": len(x) / years, "win_rate": float((x > 0).mean()) if len(x) else np.nan,
                         "gross_bps": float(ex["gross_bps"].mean()) if len(x) else np.nan,
                         "cost_bps": float(ex["cost_B"].mean()) if len(x) else np.nan, "net_bps": mu, "t": t})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "grid.csv", index=False, float_format="%.4f")
    wide = df.pivot_table(index=["check", "move_k_pct", "stop"], columns="era", values=["net_bps", "trades_per_year"])
    works = (wide["net_bps"] > 0).all(axis=1)
    pd.set_option("display.width", 250)
    print(df.pivot_table(index=["check", "move_k_pct", "stop"], columns="era",
                         values=["net_bps", "win_rate", "trades_per_year"]).round(2).to_string())
    print(f"\ncells positive in all three eras: {int(works.sum())} of {len(works)}")
    if works.any():
        print(wide[works].round(1).to_string())
    print(f"wrote {OUT.relative_to(ROOT)}/grid.csv")


if __name__ == "__main__":
    main()
