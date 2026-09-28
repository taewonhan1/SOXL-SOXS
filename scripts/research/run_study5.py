#!/usr/bin/env python3
"""Study 5 (exploratory, REGISTRY.md): big-day gates on the four near-miss rules + NR7 side check."""
import numpy as np
import pandas as pd
from scipy import stats

from runlib import Runner  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R

RULES = [("S3-01", R.s3_intents, False, dict(design="A")),
         ("S3-13", R.s3_intents, False, dict(design="A", trail=1.0)),
         ("S4-02", R.s4_trades, True, dict(k=1.0, check="H")),
         ("S4-04", R.s4_trades, True, dict(k=1.5, check="H"))]
GATES = ["G1", "G2", "G3", "G4"]


def gate_masks(td) -> dict:
    rp = td.range_pct
    g1 = np.zeros(len(rp), bool)
    for d in range(61, len(rp)):
        win = rp[d - 60:d]
        win = win[np.isfinite(win)]
        if len(win) >= 40 and np.isfinite(rp[d - 1]):
            g1[d] = rp[d - 1] >= np.percentile(win, 60)
    v15 = np.nansum(td.p.v[:, :15], axis=1)
    base = R._prior_window_stat(v15, 14, np.mean, 7)
    with np.errstate(all="ignore"):
        g2 = np.nan_to_num(v15 / base) >= 1.5
    ev = pd.read_csv(C.RESEARCH_OUT / "event_calendar.csv", parse_dates=["date"]).set_index("date")
    g3 = ev["g3_any"].reindex(td.dates).fillna(False).to_numpy(bool)
    return {"G1": g1, "G2": g2, "G3": g3, "G4": g1 | g2 | g3}


def main() -> None:
    run = Runner("study5_big_day_gates")
    td = run.ctx["SOXL"]
    masks = gate_masks(td)
    share = {g: float(m[np.isin(td.period, ["dev", "val"])].mean()) for g, m in masks.items()}
    run.log(f"gate day shares (dev+val): {share}")
    base_rows, dec = [], []
    for i, (rid, fn, is_tr, prm) in enumerate(RULES):
        ex, sk = run.trades(fn, is_trades=is_tr, **prm)
        b = E.summarize(ex, run.ctx, f"{rid} ungated", sk)
        base_rows.append(b)
        for j, g in enumerate(GATES):
            vid = f"S5-{4 * i + j + 1:02d}"
            run.log(f"{vid}: {rid} + {g}")
            run.main_variant(vid, fn, is_trades=is_tr, day_mask=masks[g], **prm)
            s = run.summ[-1]
            imp = {}
            for per in ("dev", "val"):
                gv = E.pick(s, vid, per).get("mean_net_bps", np.nan)
                bv = E.pick(b, f"{rid} ungated", per).get("mean_net_bps", np.nan)
                imp[per] = (gv, bv)
            dec.append({"variant": vid, "rule": rid, "gate": g, "gate_day_share": share[g],
                        "dev_net_gated": imp["dev"][0], "dev_net_ungated": imp["dev"][1],
                        "val_net_gated": imp["val"][0], "val_net_ungated": imp["val"][1],
                        "kept": bool(imp["dev"][0] > imp["dev"][1] and imp["val"][0] > imp["val"][1])})
    pd.concat(base_rows).to_csv(run.out / "ungated_reference.csv", index=False, float_format="%.4f")
    dd = pd.DataFrame(dec)
    dd.to_csv(run.out / "gate_decisions.csv", index=False, float_format="%.4f")
    print(dd.round(2).to_string(index=False))
    # NR7 side check (descriptive): next-day range after NR7 days vs other days, 2022-2026
    rng = td.range_pct
    nr7 = np.zeros(len(rng), bool)
    for d in range(7, len(rng)):
        w = rng[d - 7:d]
        nr7[d] = np.isfinite(w).all() and rng[d - 1] == w.min()
    per = np.isin(td.period, ["dev", "val", "hold"]) & np.isfinite(rng)
    a, b = rng[per & nr7] * 100, rng[per & ~nr7] * 100
    u = stats.mannwhitneyu(a, b)
    nr = pd.DataFrame([{"n_after_nr7": len(a), "median_range_after_nr7_pct": np.median(a),
                        "n_other": len(b), "median_range_other_pct": np.median(b), "mannwhitney_p": u.pvalue}])
    nr.to_csv(run.out / "nr7_check.csv", index=False, float_format="%.4f")
    print(nr.round(3).to_string(index=False))
    run.finish()


if __name__ == "__main__":
    main()
