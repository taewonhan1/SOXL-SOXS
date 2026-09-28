#!/usr/bin/env python3
"""Study 4: noise-boundary momentum (REGISTRY.md, 4 variants) with the SPY implementation check."""
import numpy as np
import pandas as pd

from runlib import CROSS, Runner  # noqa: I001
from soxlab.research import engine as E
from soxlab.research import rules as R

VARIANTS = [("S4-01", 1.0, "M"), ("S4-02", 1.0, "H"), ("S4-03", 1.5, "M"), ("S4-04", 1.5, "H")]


def main() -> None:
    run = Runner("study4_noise_boundary")
    for vid, k, chk in VARIANTS:
        run.log(f"{vid} k={k} check={chk}")
        run.main_variant(vid, R.s4_trades, is_trades=True, k=k, check=chk)
        run.robustness(vid, "delay", R.s4_trades, is_trades=True, k=k, check=chk, entry_delay=1)
        run.robustness(vid, "neighbour", R.s4_trades, is_trades=True, k=k + 0.25, check=chk)
        run.crosscheck(vid, R.s4_trades, tickers=CROSS + ["SPY"], is_trades=True, k=k, check=chk)
    ver = run.finish()
    # SPY implementation check: mean gross over pre+dev+val must be > 0 (published result: positive)
    rows = []
    for vid, k, chk in VARIANTS:
        ex, _ = run.trades(R.s4_trades, sig="SPY", mode="ls", is_trades=True, k=k, check=chk)
        ex = ex[np.isin(E.period_of(ex["date"]), ["pre", "dev", "val"])]
        mu, t, g = E.cluster_t(ex["gross_bps"].to_numpy(), ex["date"].to_numpy())
        rows.append({"variant": vid, "spy_trades": len(ex), "spy_mean_gross_bps": mu, "spy_t_gross": t,
                     "spy_check_pass": bool(mu > 0)})
    spy = pd.DataFrame(rows)
    spy.to_csv(run.out / "spy_check.csv", index=False, float_format="%.4f")
    print(spy.to_string(index=False))


if __name__ == "__main__":
    main()
