#!/usr/bin/env python3
"""Exploratory (not pre-registered): when the 15-minute opening-range breakout (S3-01) is worth taking.

Every S3-01 trade is described by what was known when its trigger bar closed (and before the open), and each
condition is split into buckets whose results are shown per period (pre 2019-21, dev 2022-01..2024-09,
val 2024-10..2025-12). A bucket counts as "take" / "skip" only if its net result is above / below the rest of
that condition's trades in all three periods. Also compares the two bearish executions (buy SOXS vs short SOXL)
on the same signals. 2019-01-02 .. 2025-12-31 only; the 2026 holdout stays sealed.
Writes analysis/strategies/orb_conditions/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import rules as R
from trend_days import qqq_above_ma50

OUT = C.RESEARCH_DIR / "orb_conditions"
LAST_DAY = "2025-12-31"
PERIODS = ("pre", "dev", "val")


def load(vid: str, study: str) -> pd.DataFrame:
    tr = pd.read_parquet(C.RESEARCH_DATA / "trades" / study / f"{vid}.parquet")
    tr = tr[tr["date"] <= LAST_DAY].sort_values(["date", "e"]).reset_index(drop=True)
    tr["period"] = C.period_of(tr["date"])
    return tr


def describe(ctx, tr: pd.DataFrame) -> pd.DataFrame:
    """Bucket labels for each trade, from information available at its trigger bar (sig) or before the open."""
    L, X, N, Q = ctx["SOXL"], ctx["SOXX"], ctx["NVDA"], ctx["QQQ"]
    p = L.p
    d, j, s = (tr[c].to_numpy().astype(int) for c in ("d", "sig", "s"))
    hi, lo = np.nanmax(p.h[:, :15], axis=1)[d], np.nanmin(p.l[:, :15], axis=1)[d]
    c_j = p.c[d, j]
    b = pd.DataFrame(index=tr.index)
    t = tr["entry_min"].to_numpy()
    b["trigger time"] = np.select([t <= 575, t <= 600, t <= 630, t <= 720],
                                  ["09:46-09:50", "09:51-10:00", "10:01-10:30", "10:31-12:00"], "after 12:00")
    b["direction"] = np.where(s > 0, "bullish (SOXL)", "bearish")
    g = (L.o0 / L.pc - 1)[d] * 100 * s                                   # gap in the trade's direction, %
    b["gap vs break"] = np.select([g < -1, g < 0, g < 1, g < 3], ["against, >1%", "against, 0-1%", "with, 0-1%",
                                                                   "with, 1-3%"], "with, >3%")
    orp = (hi / lo - 1) * 100
    b["opening-range size"] = np.select([orp < 2, orp < 3, orp < 4.5], ["<2%", "2-3%", "3-4.5%"], ">=4.5%")
    v15 = np.nansum(p.v[:, :15], axis=1)
    rv = (v15 / R._prior_window_stat(v15, 20, np.mean, 10))[d]
    b["first-15-min volume vs normal"] = np.select([rv < 0.8, rv < 1.2, rv < 1.6], ["<0.8x", "0.8-1.2x", "1.2-1.6x"],
                                                   ">=1.6x")
    b["QQQ vs 50-day average"] = np.where(qqq_above_ma50(ctx.dates)[d] == 1, "above", "below")
    med20 = R._prior_window_stat(L.range_pct, 20, np.median, 10)[d] * 100
    b["SOXL 20-day median range"] = np.select([med20 < 5, med20 < 7], ["<5% (calm)", "5-7%"], ">=7% (volatile)")
    strength = np.where(s > 0, c_j - hi, lo - c_j) / (hi - lo)
    b["trigger close beyond the range"] = np.select([strength < 0.05, strength < 0.15], ["<5% of range", "5-15%"],
                                                    ">=15% of range")
    vm = L.minute_mean_prior(np.where(p.valid(), p.v, np.nan), 20)
    tv = p.v[d, j] / vm[d, j]
    b["trigger-bar volume vs normal"] = np.select([tv < 1.5, tv < 3], ["<1.5x", "1.5-3x"], ">=3x")
    for T, nm in ((X, "SOXX"), (N, "NVDA"), (Q, "QQQ")):
        b[f"{nm} since its open"] = np.where(np.sign(T.p.c[d, j] / T.o0[d] - 1) == s, "same direction", "opposite")
    pm = L.premarket["pm_last"].to_numpy(float)[d]
    b["pre-market move"] = np.where(np.sign(pm / L.pc[d] - 1) == s, "same direction", "opposite")
    xoc = X.last_c / X.o0 - 1
    prev = np.concatenate([[np.nan], xoc[:-1]])[d]
    b["prior day (SOXX)"] = np.select([np.abs(prev) >= 0.02], ["trend day (>=2%)"], "not a trend day")
    ev = pd.read_csv(C.RESEARCH_DIR / "output" / "event_calendar.csv", parse_dates=["date"]).set_index("date")
    ev = ev.reindex(ctx.dates).fillna(False)
    earn = ev[["earn_NVDA", "earn_AMD", "earn_AVGO", "earn_MU"]].any(axis=1).to_numpy()[d]
    b["event"] = np.select([earn, ev["fomc"].to_numpy()[d], ev["macro_0830"].to_numpy()[d]],
                           ["chip earnings reaction", "FOMC day", "08:30 data (CPI/jobs)"], "none")
    b["weekday"] = pd.DatetimeIndex(tr["date"]).day_name().str[:3]
    return b


def bucket_table(tr: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cond in b.columns:
        for lvl in sorted(b[cond].unique()):
            m = (b[cond] == lvl).to_numpy()
            r = {"condition": cond, "bucket": lvl}
            better, worse = [], []
            for per in PERIODS + ("all",):
                pm = np.ones(len(tr), bool) if per == "all" else (tr["period"] == per).to_numpy()
                g, rest = tr[m & pm], tr[~m & pm]
                mu, t, _ = C.cluster_t(g["net_B"].to_numpy(), g["date"].to_numpy()) if len(g) > 2 else (np.nan,) * 3
                r[f"n_{per}"], r[f"net_{per}"], r[f"t_{per}"] = len(g), mu, t
                r[f"win_{per}"] = (g["net_B"] > 0).mean() if len(g) else np.nan
                r[f"rest_net_{per}"] = rest["net_B"].mean()
                if per != "all":
                    better.append(np.nan_to_num(mu, nan=-1e9) > rest["net_B"].mean())
                    worse.append(np.nan_to_num(mu, nan=1e9) < rest["net_B"].mean())
            r["verdict"] = ("take (better than the rest in all 3 periods)" if all(better) else
                            "skip (worse than the rest in all 3 periods)" if all(worse) else "mixed")
            rows.append(r)
    return pd.DataFrame(rows)


def bearish_execution(soxs: pd.DataFrame, short: pd.DataFrame) -> pd.DataFrame:
    """Same bearish signals: buy SOXS (S3-01) vs short SOXL (S8-01)."""
    a = soxs[soxs["s"] < 0][["date", "period", "net_B", "gross_bps", "cost_B"]]
    bsh = short[short["s"] < 0][["date", "net_B", "gross_bps", "cost_B"]]
    m = a.merge(bsh, on="date", suffixes=("_soxs", "_short"))
    rows = []
    for per in PERIODS + ("all",):
        g = m if per == "all" else m[m["period"] == per]
        rows.append({"period": per, "signals": len(g), "soxs_net": g["net_B_soxs"].mean(),
                     "short_soxl_net": g["net_B_short"].mean(), "soxs_cost": g["cost_B_soxs"].mean(),
                     "short_soxl_cost": g["cost_B_short"].mean(),
                     "soxs_win": (g["net_B_soxs"] > 0).mean(), "short_soxl_win": (g["net_B_short"] > 0).mean()})
    only = bsh[~bsh["date"].isin(a["date"])].assign(period=lambda x: C.period_of(x["date"]))
    for per in PERIODS + ("all",):
        g = only if per == "all" else only[only["period"] == per]
        rows.append({"period": f"{per} (SOXS < $10: short SOXL only)", "signals": len(g),
                     "short_soxl_net": g["net_B"].mean(), "short_soxl_win": (g["net_B"] > 0).mean()})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context()
    tr = load("S3-01", "study3_opening_range_breakout")
    b = describe(ctx, tr)
    tbl = bucket_table(tr, b)
    bear = bearish_execution(tr, load("S8-01", "study8_execution"))
    tbl.to_csv(OUT / "conditions.csv", index=False, float_format="%.4f")
    bear.to_csv(OUT / "bearish_execution.csv", index=False, float_format="%.4f")
    pd.concat([tr[["date", "period", "s", "inst", "entry_min", "net_B"]], b], axis=1).to_csv(
        OUT / "trades_with_conditions.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 30)
    show = ["condition", "bucket", "n_all", "win_all", "net_all", "net_pre", "net_dev", "net_val", "rest_net_pre",
            "rest_net_dev", "rest_net_val", "verdict"]
    print(tbl[show].round(1).to_string(index=False))
    print("\n== bearish execution on the same signals\n" + bear.round(1).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
