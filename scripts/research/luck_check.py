#!/usr/bin/env python3
"""Luck check for the live trend-odds table (intraday_trend_odds.py): how good would the table look if the morning
move's direction said nothing about the rest of the day?

Null: each day's direction is flipped at random, with the same flip at every check time so a day's signals stay
consistent. Both legs are executed for every candidate day: up = long SOXL, down = long SOXS (prior close >= $10,
else no trade); no stop; next open -> 15:55; case B. The null therefore keeps the real costs, skips and the overlap
between cells. Over the 35 no-stop cells, pooled over 2011-06..2018, 2019..2025 and 2026-01..09, it compares:
  * the best cell's t (the chance that a search this size finds something this good by luck);
  * the number of cells positive in all three eras;
  * the average net per trade over all 35 cells (also per era: observed minus random direction = what the
    direction is worth, and the random-direction average = the cost drag).
A second null asks whether the NET result beats zero (not just a random side): White's reality check. Each cell's
trades are recentred to a mean of zero (per era for the era count, pooled otherwise), days are resampled with
replacement within each era (a day keeps all its cells, so the overlap is kept), and the statistics are recomputed.
Writes analysis/strategies/intraday_trend_odds/luck_check.csv and luck_check_by_era.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from intraday_trend_odds import BUCKETS, CHECKS, ERAS, OUT
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research.rules import FLAT_OPEN

N_PERM = 2000
SEED = 7
NB = len(BUCKETS)


def legs(ctx, in_era: np.ndarray, cms: dict) -> list[tuple]:
    """Per check time: (day index, bucket, observed sign, net_B if up-leg, net_B if down-leg)."""
    L = ctx["SOXL"]
    p = L.p
    out = []
    for bar in CHECKS.values():
        rows = []
        for d in np.flatnonzero(in_era):
            flat = int(p.n_min[d]) - FLAT_OPEN
            if bar + 1 >= flat or not (np.isfinite(L.o0[d]) and np.isfinite(p.c[d, bar])):
                continue
            m = (p.c[d, bar] / L.o0[d] - 1) * 100
            b = next((i for i, (lo, hi, _) in enumerate(BUCKETS) if lo <= abs(m) < hi), None)
            if b is not None:
                rows.append((d, b, 1 if m > 0 else -1, flat))
        d_arr = np.array([r[0] for r in rows])
        net = {}
        for s in (1, -1):
            it = E.make_intents([{"d": d, "sig": bar, "e": bar + 1, "s": s, "tx": flat, "tx_kind": "open"}
                                 for d, _, _, flat in rows])
            ex = E.add_costs(E.execute(E.simulate(L, it), ctx, mode="switch")[0], cms)
            net[s] = pd.Series(ex["net_B"].to_numpy(float), index=ex["d"].to_numpy(int)).reindex(d_arr).to_numpy()
        out.append((d_arr, np.array([r[1] for r in rows]), np.array([r[2] for r in rows]), net[1], net[-1]))
    return out


def cell_stats(data: list, eps: list, w: list | None = None, shift: np.ndarray | None = None
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per cell (check x bucket): pooled mean, pooled t, and whether the mean is > 0 in every era (>= 5 trades).
    ``eps``: per-era day flips; ``w``: per-era day weights (bootstrap counts); ``shift``: per era x check x bucket
    amount subtracted from every trade (recentring)."""
    n = np.zeros((len(data), len(CHECKS), NB))
    s1 = np.zeros_like(n)
    s2 = np.zeros_like(n)
    for e, (era_legs, ep) in enumerate(zip(data, eps)):
        for c, (d, b, s, up, dn) in enumerate(era_legs):
            v = np.where(s * ep[d] > 0, up, dn)
            ok = np.isfinite(v)
            bb, vv = b[ok], v[ok]
            if shift is not None:
                vv = vv - shift[e, c, bb]
            ww = np.ones(len(vv)) if w is None else w[e][d[ok]]
            n[e, c] = np.bincount(bb, weights=ww, minlength=NB)
            s1[e, c] = np.bincount(bb, weights=ww * vv, minlength=NB)
            s2[e, c] = np.bincount(bb, weights=ww * vv ** 2, minlength=NB)
    N, S, Q = n.sum(0), s1.sum(0), s2.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = S / N
        t = mean / np.sqrt((Q - S ** 2 / N) / (N - 1) / N)
    pos_all = ((s1 > 0) & (n >= 5)).all(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        era_mean = np.where(n >= 5, s1 / n, np.nan)
    return mean, t, pos_all, era_mean


def era_cell_means(data: list) -> np.ndarray:
    """Observed mean net per era x check x bucket (0 where a cell is empty)."""
    out = np.zeros((len(data), len(CHECKS), NB))
    for e, era_legs in enumerate(data):
        for c, (d, b, s, up, dn) in enumerate(era_legs):
            v = np.where(s > 0, up, dn)
            ok = np.isfinite(v)
            cnt = np.bincount(b[ok], minlength=NB)
            out[e, c] = np.where(cnt > 0, np.bincount(b[ok], weights=v[ok], minlength=NB) / np.maximum(cnt, 1), 0)
    return out


def main() -> None:
    cms = {"B": C.cost_model(C.COMMISSION_B)}
    data, ndays = [], []
    for era, start, end in ERAS:
        ctx = C.Context(start="2025-10-01" if era == "2026" else start, end=end)
        data.append(legs(ctx, (ctx.dates >= start) & (ctx.dates <= end), cms))
        ndays.append(len(ctx.dates))
    mean, t, pos, era_obs = cell_stats(data, [np.ones(k) for k in ndays])
    best = np.unravel_index(np.nanargmax(t), t.shape)
    obs = {"best_t": float(np.nanmax(t)), "cells_positive_all_eras": int(pos.sum()), "avg_cell_net_bps": float(np.nanmean(mean)),
           "cell_1030_3to4_t": float(t[list(CHECKS).index("10:30"), 2])}
    rng = np.random.default_rng(SEED)
    null, era_null = [], []
    for _ in range(N_PERM):
        m0, t0, p0, e0 = cell_stats(data, [rng.choice((-1, 1), size=k) for k in ndays])
        era_null.append(np.nanmean(e0.reshape(len(data), -1), axis=1))
        null.append({"best_t": float(np.nanmax(t0)), "cells_positive_all_eras": int(p0.sum()),
                     "avg_cell_net_bps": float(np.nanmean(m0)), "cell_1030_3to4_t": float(t0[list(CHECKS).index("10:30"), 2])})
    null = pd.DataFrame(null)
    # reality check: recentred net, days resampled within each era
    ones = [np.ones(k) for k in ndays]
    pooled_shift = np.broadcast_to(mean, (len(data),) + mean.shape)
    era_shift = era_cell_means(data)
    boot = []
    for _ in range(N_PERM):
        w = [np.bincount(rng.integers(0, k, size=k), minlength=k).astype(float) for k in ndays]
        m1, t1, _, _ = cell_stats(data, ones, w, pooled_shift)
        _, _, p1, _ = cell_stats(data, ones, w, era_shift)
        boot.append({"best_t": float(np.nanmax(t1)), "cells_positive_all_eras": int(p1.sum()),
                     "avg_cell_net_bps": float(np.nanmean(m1)), "cell_1030_3to4_t": float(t1[list(CHECKS).index("10:30"), 2])})
    boot = pd.DataFrame(boot)
    rows = []
    for name, dist in (("random direction (no information, real costs)", null),
                       ("zero net edge (reality check bootstrap)", boot)):
        rows += [{"null": name, "statistic": k, "observed": v, "null_median": float(dist[k].median()),
                  "null_95th": float(dist[k].quantile(0.95)), "share_of_null_at_least_as_good": float((dist[k] >= v).mean())}
                 for k, v in obs.items()]
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "luck_check.csv", index=False, float_format="%.4f")
    rand = np.mean(era_null, axis=0)
    by_era = pd.DataFrame({"era": [e[0] for e in ERAS],
                           "avg_cell_net_bps": np.nanmean(era_obs.reshape(len(data), -1), axis=1),
                           "random_direction_avg_net_bps": rand})
    by_era["direction_worth_bps"] = by_era["avg_cell_net_bps"] - by_era["random_direction_avg_net_bps"]
    by_era.to_csv(OUT / "luck_check_by_era.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 200)
    print(f"best cell: {list(CHECKS)[best[0]]} {BUCKETS[best[1]][2]}  (pooled mean {mean[best]:+.1f} bps, t {t[best]:.2f})")
    print(res.round(3).to_string(index=False))
    print("\n" + by_era.round(1).to_string(index=False))
    print(f"\n{N_PERM} runs per null; wrote {OUT.relative_to(ROOT)}/luck_check.csv")


if __name__ == "__main__":
    main()
