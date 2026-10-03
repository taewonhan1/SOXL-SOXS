#!/usr/bin/env python3
"""What you can see before the open, or by 09:45, that raises the odds of a trend day (SOXX open->close >= 2%).

Exploratory and descriptive. For each era (2011-06..2018, 2019..2025, 2026-01..09), the share of trend days overall
and within buckets of conditions known at 09:30 or 09:45, all built from trailing data (no look-ahead):
  * vol regime: SOXL's median daily range over the prior 20 sessions / its median over the prior 250 sessions
  * yesterday was a trend day (SOXX |open->close| >= 2%)
  * QQQ's prior close below its 50-day average
  * gap: |SOXL open / prior close - 1| as a share of SOXL's prior 20-day median daily range
  * first 15 minutes (known at 09:45): SOXL's 09:30-09:44 range / its average over the prior 20 sessions
  * 2019+ only: FOMC / 08:30 macro / chip-earnings reaction days (event calendar); pre-market range vs its
    20-day average (pre-market bars are sparse before 2019)
Plus a count of "hot" flags: vol regime >= 1.2, yesterday a trend day, QQQ below its 50-day, gap >= half a typical
day's range (pre-open score, 0-4), and the same plus a first-15-minute range >= 1.25x normal (09:45 score, 0-5).
Finally, the 10:30 rule (SOXL 3-4% from its open at 10:30 -> go with it, stop at the open, exit 15:55; case B)
split by the pre-open and 09:45 scores (0-1 vs 2+ flags), per era.
Writes analysis/strategies/trend_day_predictors/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
import trend_days as TD
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "trend_day_predictors"
ERAS = (("2011-2018", "2011-06-01", "2018-12-31"), ("2019-2025", "2019-01-02", "2025-12-31"),
        ("2026", "2026-01-02", "2026-09-25"))
BUCKETS = {
    "vol_regime": ([0, 0.9, 1.2, np.inf], ["calm (<0.9x)", "normal", "hot (>=1.2x)"]),
    "gap_rel": ([0, 0.25, 0.5, np.inf], ["small (<0.25 day)", "medium", "big (>=0.5 day)"]),
    "or15_rel": ([0, 0.8, 1.25, np.inf], ["narrow (<0.8x)", "normal", "wide (>=1.25x)"]),
    "pm_range_rel": ([0, 0.8, 1.25, np.inf], ["quiet (<0.8x)", "normal", "busy (>=1.25x)"]),
}
BINARY = ["yday_trend", "qqq_below_50d", "event_day"]


def features(ctx, start: str) -> pd.DataFrame:
    L, X = ctx["SOXL"], ctx["SOXX"]
    p = L.p
    oc = X.last_c / X.o0 - 1
    df = pd.DataFrame(index=ctx.dates)
    df["trend"] = np.where(np.isfinite(oc), (np.abs(oc) >= 0.02).astype(float), np.nan)
    rp = L.range_pct
    med20 = R._prior_window_stat(rp, 20, np.median, 10)
    df["vol_regime"] = med20 / R._prior_window_stat(rp, 250, np.median, 100)
    df["yday_trend"] = (TD._lag(np.abs(oc), 1) >= 0.02).astype(float)
    df["qqq_below_50d"] = 1 - TD.qqq_above_ma50(ctx.dates)
    df["gap_rel"] = np.abs(L.o0 / L.pc - 1) / med20
    or15 = np.nanmax(p.h[:, :15], axis=1) / np.nanmin(p.l[:, :15], axis=1) - 1
    df["or15_rel"] = or15 / R._prior_window_stat(or15, 20, np.mean, 10)
    ev = pd.read_csv(C.RESEARCH_DIR / "output" / "event_calendar.csv", parse_dates=["date"]).set_index("date")
    ev = ev.reindex(ctx.dates)
    cols = ["fomc", "macro_0830", "earn_NVDA", "earn_AMD", "earn_AVGO", "earn_MU"]
    df["event_day"] = ev[cols].fillna(False).astype(bool).any(axis=1).astype(float).where(ctx.dates >= "2019-01-02")
    pm = L.premarket
    pmr = (pm["pm_high"] - pm["pm_low"]).to_numpy(float) / L.pc
    df["pm_range_rel"] = pd.Series(pmr / R._prior_window_stat(pmr, 20, np.mean, 10),
                                   index=ctx.dates).where(ctx.dates >= "2019-01-02")
    df = df.replace([np.inf, -np.inf], np.nan)
    df["score_preopen"] = ((df["vol_regime"] >= 1.2).astype(int) + df["yday_trend"].fillna(0).astype(int)
                           + df["qqq_below_50d"].fillna(0).astype(int) + (df["gap_rel"] >= 0.5).astype(int))
    df["score_0945"] = df["score_preopen"] + (df["or15_rel"] >= 1.25).astype(int)
    return df[(df.index >= start) & df["trend"].notna()]


def rule_1030(ctx, start: str, end: str, cms: dict) -> pd.DataFrame:
    """The 10:30 rule: SOXL 3-4% from its open at the 10:29 close -> go with it, stop at the open, exit 15:55."""
    L = ctx["SOXL"]
    p = L.p
    it = []
    for d in np.flatnonzero((ctx.dates >= start) & (ctx.dates <= end)):
        flat = int(p.n_min[d]) - FLAT_OPEN
        if 60 >= flat or not (np.isfinite(L.o0[d]) and np.isfinite(p.c[d, 59])):
            continue
        m = (p.c[d, 59] / L.o0[d] - 1) * 100
        if 3 <= abs(m) < 4:
            it.append({"d": d, "sig": 59, "e": 60, "s": 1 if m > 0 else -1, "tx": flat, "tx_kind": "open",
                       "stop": L.o0[d]})
    return E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], cms)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cms = {"B": C.cost_model(C.COMMISSION_B)}
    rows, scores, rule = [], [], []
    for era, start, end in ERAS:
        ctx = C.Context(start="2025-10-01" if era == "2026" else "2010-06-01" if era == "2011-2018" else "2018-01-02",
                        end=end)
        df = features(ctx, start)
        df = df[df.index <= end]
        ex = rule_1030(ctx, start, end, cms).join(df[["score_preopen", "score_0945"]], on="date")
        for sc in ("score_preopen", "score_0945"):
            for grp, g in ex.groupby(np.where(ex[sc] >= 2, "2+ flags", "0-1 flags")):
                rule.append({"era": era, "score": sc, "group": grp, "trades": len(g),
                             "win": float((g["net_B"] > 0).mean()), "net_pct": float(g["net_B"].mean()) / 100})
        base = df["trend"].mean()
        rows.append({"era": era, "condition": "all days", "bucket": "", "days": len(df), "share_of_days": 1.0,
                     "trend_day_rate": base, "lift": 1.0})
        for f, (edges, labels) in BUCKETS.items():
            b = pd.cut(df[f], edges, right=False, labels=labels)
            for lab, g in df.groupby(b, observed=True):
                rows.append({"era": era, "condition": f, "bucket": lab, "days": len(g), "share_of_days": len(g) / len(df),
                             "trend_day_rate": g["trend"].mean(), "lift": g["trend"].mean() / base})
        for f in BINARY:
            for val, g in df.groupby(df[f]):
                rows.append({"era": era, "condition": f, "bucket": "yes" if val == 1 else "no", "days": len(g),
                             "share_of_days": len(g) / len(df), "trend_day_rate": g["trend"].mean(),
                             "lift": g["trend"].mean() / base})
        for sc in ("score_preopen", "score_0945"):
            s = df[sc].clip(upper=3)
            for val, g in df.groupby(s):
                scores.append({"era": era, "score": sc, "hot_flags": f"{int(val)}" + ("+" if val == 3 else ""),
                               "days": len(g), "share_of_days": len(g) / len(df), "trend_day_rate": g["trend"].mean()})
    res, sc, rl = pd.DataFrame(rows), pd.DataFrame(scores), pd.DataFrame(rule)
    rl.to_csv(OUT / "rule_1030_by_flags.csv", index=False, float_format="%.4f")
    res.to_csv(OUT / "conditions.csv", index=False, float_format="%.4f")
    sc.to_csv(OUT / "hot_flag_scores.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    print(res.pivot_table(index=["condition", "bucket"], columns="era", values=["trend_day_rate", "share_of_days"],
                          sort=False).round(2).to_string())
    print("\n" + sc.pivot_table(index=["score", "hot_flags"], columns="era",
                                values=["trend_day_rate", "share_of_days"]).round(2).to_string())
    print("\n" + rl.pivot_table(index=["score", "group"], columns="era", values=["net_pct", "trades"]).round(2).to_string())
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
