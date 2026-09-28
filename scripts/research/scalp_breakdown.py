#!/usr/bin/env python3
"""Descriptive breakdown of Studies 10-12 (1-minute momentum scalps) for every registered variant: bull vs
bear legs, entry time of day, cost cases (gross, A, B, Q, S), exit mix and year. Uses 2019-01-02 ..
2025-12-31 only; the 2026 holdout stays sealed. Writes analysis/strategies/scalps_breakdown/*.csv."""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C

STUDIES = ["study10_hitchhiker", "study11_bone_zone", "study12_flags"]
OUT = C.RESEARCH_DIR / "scalps_breakdown"
TOD = [(570, 600, "09:30-10:00"), (600, 630, "10:00-10:30"), (630, 720, "10:30-12:00"),
       (720, 840, "12:00-14:00"), (840, 960, "14:00-16:00")]


def block(g: pd.DataFrame, col: str = "net_B") -> dict:
    x = g[col].to_numpy(float)
    mu, t, _ = C.cluster_t(x, g["date"].to_numpy()) if len(x) else (np.nan, np.nan, 0)
    return {"n": len(x), "mean_net_B": mu, "t": t, "win_rate": float((x > 0).mean()) if len(x) else np.nan,
            "mean_gross": float(g["gross_bps"].mean()) if len(x) else np.nan}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    side_rows, tod_rows, case_rows, exit_rows, year_rows = [], [], [], [], []
    for st in STUDIES:
        for f in sorted((C.RESEARCH_DATA / "trades" / st).glob("S*.parquet")):
            vid = f.stem
            if "skipped" in vid:
                continue
            tr = pd.read_parquet(f)
            tr = tr[(tr["date"] >= "2019-01-02") & (tr["date"] <= "2025-12-31")].copy()       # holdout excluded
            tr["period"] = C.period_of(tr["date"])
            tr["side_name"] = np.where(tr["s"] > 0, "bull", "bear")
            tr["tod"] = pd.cut(tr["entry_min"], [a for a, _, _ in TOD] + [TOD[-1][1]], right=False,
                               labels=[n for _, _, n in TOD])
            for (per, sd), g in tr.groupby(["period", "side_name"]):
                side_rows.append({"variant": vid, "period": per, "side": sd, **block(g)})
            dv = tr[tr["period"].isin(["dev", "val"])]
            for tod, g in dv.groupby("tod", observed=True):
                tod_rows.append({"variant": vid, "sample": "dev+val", "entry_time": tod, **block(g)})
            v = tr[tr["period"] == "val"]
            case_rows.append({"variant": vid, "val_n": len(v), "gross": v["gross_bps"].mean(),
                              "net_A": v["net_A"].mean(), "net_B": v["net_B"].mean(),
                              "net_Q": v["net_Q"].mean() if "net_Q" in v else np.nan,
                              "net_S": v["net_S"].mean() if "net_S" in v else np.nan,
                              "cost_B": v["cost_B"].mean(),
                              "q_fallback_share": v["q_fallback"].mean() if "q_fallback" in v else np.nan,
                              "soxs_share": float((v["inst"] == "SOXS").mean()),
                              "median_hold_min": float((v["exit_min"] - v["entry_min"]).median())})
            for rs, g in v.groupby("reason"):
                exit_rows.append({"variant": vid, "reason": rs, "share": len(g) / max(1, len(v)), **block(g)})
            tr["year"] = pd.to_datetime(tr["date"]).dt.year
            for y, g in tr.groupby("year"):
                year_rows.append({"variant": vid, "year": y, **block(g)})
    res = {"by_side": pd.DataFrame(side_rows), "by_entry_time": pd.DataFrame(tod_rows),
           "val_cost_cases": pd.DataFrame(case_rows), "val_exits": pd.DataFrame(exit_rows),
           "by_year": pd.DataFrame(year_rows)}
    pd.set_option("display.width", 220)
    for k, df in res.items():
        df.to_csv(OUT / f"{k}.csv", index=False, float_format="%.4f")
        print(f"\n== {k}\n" + df.round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
