#!/usr/bin/env python3
"""Exploratory (not pre-registered): how the near-miss rules' trades depend on market conditions and when
their returns came. Uses 2019-01-02 .. 2025-12-31 only (pre + dev + val); the 2026 holdout stays sealed.

Conditions known at the open (usable as filters): semis 20-day trend, QQQ vs its 50-day average, SOXL
20-day median range (volatility regime), overnight gap in ATR units, first-15-minute relative volume
(known at 09:45). Outcome condition (NOT known in advance, descriptive only): SOXX open->close move.
Outputs: analysis/strategies/exploratory/*.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import rules as R

OUT = C.RESEARCH_DIR / "exploratory"
RULES = {"S3-01": "study3_opening_range_breakout", "S8-01": "study8_execution",
         "S4-02": "study4_noise_boundary", "S4-04": "study4_noise_boundary", "S1-06": "study1_late_day_fade"}


def day_conditions(ctx) -> pd.DataFrame:
    L, X, Q = ctx["SOXL"], ctx["SOXX"], ctx["QQQ"]
    n = len(ctx.dates)
    soxx_ret20 = X.pc / np.concatenate([np.full(20, np.nan), X.pc[:-20]]) - 1
    q_ma50 = pd.Series(Q.off).shift(1).rolling(50, min_periods=40).mean().to_numpy()
    rng20 = pd.Series(L.range_pct).shift(1).rolling(20, min_periods=10).median().to_numpy()
    gap_atr = np.abs(L.o0 - L.pc) / L.atr_prev
    v15 = np.nansum(L.p.v[:, :15], axis=1)
    rvol15 = v15 / R._prior_window_stat(v15, 14, np.mean, 7)
    soxx_oc = X.last_c / X.o0 - 1
    df = pd.DataFrame({"soxx_ret20": soxx_ret20, "qqq_above_ma50": Q.pc > q_ma50, "soxl_range20": rng20,
                       "gap_atr": gap_atr, "rvol15": rvol15, "soxx_open_close": soxx_oc}, index=ctx.dates)
    df["d"] = np.arange(n)
    return df


def bucketize(df: pd.DataFrame) -> pd.DataFrame:
    b = pd.DataFrame(index=df.index)
    b["semis_trend_20d"] = pd.qcut(df["soxx_ret20"], 3, labels=["down", "flat", "up"])
    b["qqq_vs_50dma"] = np.where(df["qqq_above_ma50"], "above", "below")
    b["vol_regime"] = pd.qcut(df["soxl_range20"], 3, labels=["calm", "normal", "wild"])
    b["gap_size"] = pd.cut(df["gap_atr"], [-np.inf, 0.25, 0.75, np.inf], labels=["small", "medium", "large"])
    b["early_volume"] = pd.cut(df["rvol15"], [-np.inf, 1.0, 1.5, np.inf], labels=["<1x", "1-1.5x", ">=1.5x"])
    b["OUTCOME_semis_day_move"] = pd.cut(df["soxx_open_close"].abs(), [-np.inf, 0.01, 0.02, np.inf],
                                         labels=["<1%", "1-2%", ">=2%"])
    return b


def stats_block(x: pd.Series, dates: pd.Series) -> dict:
    mu, t, g = C.cluster_t(x.to_numpy(), dates.to_numpy())
    return {"n": len(x), "mean_net_bps": mu, "t": t, "win_rate": float((x > 0).mean()), "total_pct": x.sum() / 100}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context()
    cond = day_conditions(ctx)
    buck = bucketize(cond[(cond.index >= "2019-01-02") & (cond.index <= "2025-12-31")])
    cond_rows, when_rows, tod_rows, top_rows, corr_rows = [], [], [], [], []
    for rid, st in RULES.items():
        tr = pd.read_parquet(C.RESEARCH_DATA / "trades" / st / f"{rid}.parquet")
        tr = tr[(tr["date"] >= "2019-01-02") & (tr["date"] <= "2025-12-31")].copy()     # holdout excluded
        tr = tr.join(buck, on="date")
        tr = tr.join(cond[["soxx_ret20", "soxl_range20", "gap_atr", "rvol15", "soxx_open_close"]], on="date")
        for col in buck.columns:
            for lvl, g in tr.groupby(col, observed=True):
                cond_rows.append({"rule": rid, "condition": col, "bucket": str(lvl), **stats_block(g["net_B"], g["date"])})
        for col in ["soxx_ret20", "soxl_range20", "gap_atr", "rvol15"]:
            ok = tr[col].notna()
            rho = tr.loc[ok, "net_B"].corr(tr.loc[ok, col], method="spearman")
            corr_rows.append({"rule": rid, "variable": col, "spearman_rho": rho, "n": int(ok.sum())})
        tr["year"] = pd.to_datetime(tr["date"]).dt.year
        tr["month"] = pd.to_datetime(tr["date"]).dt.to_period("M").astype(str)
        for y, g in tr.groupby("year"):
            when_rows.append({"rule": rid, "year": y, **stats_block(g["net_B"], g["date"])})
        tr["entry_half_hour"] = ((tr["entry_min"] - 570) // 30 * 30 + 570).map(lambda m: f"{m // 60:02d}:{m % 60:02d}")
        for hh, g in tr.groupby("entry_half_hour"):
            tod_rows.append({"rule": rid, "entry_half_hour": hh, **stats_block(g["net_B"], g["date"])})
        m = tr.groupby("month")["net_B"].agg(["count", "sum"]).rename(columns={"sum": "total_bps"})
        m["rule"] = rid
        top_rows.append(m.sort_values("total_bps", ascending=False).head(5).reset_index().assign(rank="best"))
        top_rows.append(m.sort_values("total_bps").head(3).reset_index().assign(rank="worst"))
    res = {"conditions": pd.DataFrame(cond_rows), "by_year": pd.DataFrame(when_rows),
           "by_time_of_day": pd.DataFrame(tod_rows), "best_worst_months": pd.concat(top_rows, ignore_index=True),
           "correlations": pd.DataFrame(corr_rows)}
    for k, v in res.items():
        v.to_csv(OUT / f"{k}.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 220)
    for k, v in res.items():
        print(f"\n== {k}\n" + v.round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
