"""Robustness: deseasonalised overlapping VR(q) under a sign-randomised null (keeps every minute's
|return|, hence the exact intraday heteroskedasticity, and removes serial dependence). 20 draws."""
from __future__ import annotations

import importlib.util

import numpy as np
import pandas as pd

from common import MAIN, PERIODS, Tk, save_csv

spec = importlib.util.spec_from_file_location("d", __file__.replace("05b_vr_null_check.py", "05_direction.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
rng = np.random.default_rng(3)
rows = []
for t in MAIN:
    T = Tk(t)
    for per in PERIODS:
        r = T.r1[T.sel(per)][:, 1:]
        obs = {q: d.vr_stats(d.deseason(r), q)[0] for q in (5, 15, 60)}
        sims = {q: [] for q in obs}
        for _ in range(20):
            z = d.deseason(np.abs(r) * rng.choice([-1.0, 1.0], size=r.shape))
            for q in obs:
                sims[q].append(d.vr_stats(z, q)[0])
        for q in obs:
            m, s = np.mean(sims[q]), np.std(sims[q])
            rows.append({"ticker": t, "period": per, "q_min": q, "VR_obs": obs[q], "VR_null_mean": m, "VR_null_sd": s,
                         "obs_minus_null_in_null_sd": (obs[q] - m) / s, "null_p2.5": np.percentile(sims[q], 2.5),
                         "null_p97.5": np.percentile(sims[q], 97.5)})
    print("done", t, flush=True)
save_csv(pd.DataFrame(rows), "dir_vr_signrandom_null.csv", index=False)
