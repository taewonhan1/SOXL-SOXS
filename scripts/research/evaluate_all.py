#!/usr/bin/env python3
"""Cross-study evaluation (REGISTRY.md pass criteria 1-6) with Benjamini-Hochberg over all variants.

Holdout results are computed ONLY for variants that pass criteria 1-5 (including BH); every other
variant's 2026 holdout stays unopened. Writes analysis/strategies/verdicts_all.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT, Runner  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E

STUDIES = {  # study dir -> (confirmatory?, extra pre-sample checks?)
    "study1_late_day_fade": (True, True),
    "study2_opening_burst": (True, True),
    "study3_opening_range_breakout": (True, False),
    "study4_noise_boundary": (True, False),
    "study6_failed_break_fade": (True, False),
    "study5_big_day_gates": (False, False),
    "study8_execution": (False, False),
}


def main() -> None:
    frames = []
    for st, (confirm, extra) in STUDIES.items():
        v = pd.read_csv(C.RESEARCH_DIR / st / "verdicts.csv")
        v["study"], v["confirmatory"], v["extra_checks"] = st, confirm, extra
        frames.append(v)
    allv = pd.concat(frames, ignore_index=True)
    allv["q_bh"] = C.bh_qvalues(allv["p_val_one_sided"].fillna(1.0).to_numpy())
    allv["c3_bh"] = allv["q_bh"] <= 0.10

    def _b(col):
        return allv[col].fillna(False).astype(bool) if col in allv else pd.Series(False, index=allv.index)

    q_ok = allv["c1_q_pos"].isna() | _b("c1_q_pos")
    allv["pass_1_5"] = (_b("c1_net_ge5") & q_ok & _b("c2_t_and_quarters") & allv["c3_bh"] &
                        _b("c4_robust") & _b("c5_cross_same_sign") & allv["confirmatory"])
    extra_ok = (~allv["extra_checks"]) | (_b("x_pre_net_pos") & _b("x_pre_dev_cross_sign"))
    allv["pass_1_5"] &= extra_ok
    # criterion 6: open the holdout only for variants that passed 1-5
    allv["hold_net_B"], allv["hold_opened"] = np.nan, False
    passing = allv[allv["pass_1_5"]]
    if len(passing):
        run = Runner("holdout_checks")
        for _, r in passing.iterrows():
            tr = pd.read_parquet(C.RESEARCH_DATA / "trades" / r["study"] / f"{r['variant']}.parquet")
            s = E.summarize(tr, run.ctx, r["variant"], periods=("hold",))
            allv.loc[allv["variant"] == r["variant"], "hold_net_B"] = E.pick(s, r["variant"], "hold").get("mean_net_bps")
            allv.loc[allv["variant"] == r["variant"], "hold_opened"] = True
    allv["pass_1_6"] = allv["pass_1_5"] & (allv["hold_net_B"].fillna(-1) >= 0)
    def _reasons(r: dict) -> str:
        out = []
        for k, col in (("c1", "c1_net_ge5"), ("c2", "c2_t_and_quarters"), ("c3", "c3_bh"), ("c4", "c4_robust"),
                       ("c5", "c5_cross_same_sign"), ("pre", "x_pre_net_pos"), ("pre-cross", "x_pre_dev_cross_sign")):
            val = r.get(col)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            if not bool(val):
                out.append(k)
        return ", ".join(out)

    allv["fail_reasons"] = [_reasons(r) for r in allv.to_dict("records")]
    dst = C.RESEARCH_DIR / "verdicts_all.csv"
    allv.to_csv(dst, index=False, float_format="%.4f")
    show = ["study", "variant", "val_n", "val_mean_net_B", "val_t_net_B", "val_quarters_pos", "dev_mean_net_B",
            "pre_mean_net_B", "p_val_one_sided", "q_bh", "pass_1_5", "hold_opened", "fail_reasons"]
    print(allv[show].round(3).to_string(index=False))
    print(f"\nvariants: {len(allv)} | pass 1-5: {int(allv['pass_1_5'].sum())} | min q: {allv['q_bh'].min():.3f}")
    print(f"wrote {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
