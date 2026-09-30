#!/usr/bin/env python3
"""Exploratory (not pre-registered): trend and medium days.

Day type = |SOXX regular-session open -> close|: quiet < 1%, medium 1-2%, trend >= 2%. It is only known after
the close, so
  * Part A (how each tested rule did on each day type; how the 15-minute breakout behaves on trend days) is
    descriptive: it says what to do on such a day, not how to know you are in one;
  * Part B asks what was knowable at 09:30 or 09:45 that flags trend/medium days. Each condition is checked per
    period, and a combined detector is fitted on two periods and scored on the third (pre 2019-21, dev
    2022-01..2024-09, val 2024-10..2025-12), with its day-selection thresholds taken from the fitting periods.
    It then checks whether the 15-minute breakout does better on the days the detector flags.
2019-01-02 .. 2025-12-31 only; the 2026 holdout stays sealed. Writes analysis/strategies/trend_days/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from scalp_winners import _auc, _logit_l2
from soxlab.research import common as C
from soxlab.research import rules as R

OUT = C.RESEARCH_DIR / "trend_days"
LAST_DAY = "2025-12-31"
PERIODS = ("pre", "dev", "val")
RULES = [  # (variant, study dir, label)
    ("S3-01", "study3_opening_range_breakout", "15-min opening-range breakout"),
    ("S8-01", "study8_execution", "15-min breakout, bearish = short SOXL"),
    ("S3-13", "study3_opening_range_breakout", "15-min breakout + VWAP trail after +1R"),
    ("S3-02", "study3_opening_range_breakout", "first 5-min candle breakout, 10R target"),
    ("S4-02", "study4_noise_boundary", "noise-boundary momentum, k=1.0"),
    ("S4-04", "study4_noise_boundary", "noise-boundary momentum, k=1.5"),
    ("S2-09", "study2_opening_burst", "opening burst, 1-min hold"),
    ("S10-05", "study10_hitchhiker", "Hitchhiker-like, buy-stop, by 10:14"),
    ("S10-07", "study10_hitchhiker", "Hitchhiker-like, close entry, by 10:14"),
    ("S11-01", "study11_bone_zone", "Bone Zone-like pullback"),
    ("S12-01", "study12_flags", "flag-like, trendline break"),
    ("S6-02", "study6_failed_break_fade", "failed-break fade"),
    ("S1-06", "study1_late_day_fade", "late-day fade"),
]
FEATS_OPEN = ["gap_abs_pct", "gap_atr", "soxx_gap_abs_pct", "pm_volume_rel", "pm_range_pct", "prev_range_rel",
              "prev_soxx_move_abs_pct", "vol_regime_range20_pct", "qqq_above_50dma", "soxx_ret20_abs_pct",
              "soxx_ret5_abs_pct", "earnings_day", "fomc_day", "macro_0830_day", "monthly_opex", "dow"]
FEATS_0945 = ["rvol15", "or15_range_pct", "or15_range_atr", "drive15_abs_pct", "soxx_drive15_abs_pct",
              "gap_and_go", "complex_agree15"]
BINARY = {"qqq_above_50dma", "earnings_day", "fomc_day", "macro_0830_day", "monthly_opex", "gap_and_go",
          "complex_agree15"}


def _lag(x: np.ndarray, k: int) -> np.ndarray:
    return np.concatenate([np.full(k, np.nan), x[:-k]])


def day_table(ctx) -> pd.DataFrame:
    L, X, N, Q = ctx["SOXL"], ctx["SOXX"], ctx["NVDA"], ctx["QQQ"]
    df = pd.DataFrame(index=ctx.dates)
    df["period"] = C.period_of(ctx.dates)
    oc = X.last_c / X.o0 - 1
    a = np.abs(oc)
    df["soxx_open_close_pct"] = oc * 100
    df["day_type"] = pd.Series(np.where(a >= 0.02, "trend", np.where(a >= 0.01, "medium", "quiet")),
                               index=df.index).where(np.isfinite(oc))
    df["day_dir"] = np.sign(oc)
    # ---- known at 09:30
    gap = L.o0 / L.pc - 1
    df["gap_abs_pct"] = np.abs(gap) * 100
    df["gap_atr"] = np.abs(L.o0 - L.pc) / L.atr_prev
    df["soxx_gap_abs_pct"] = np.abs(X.o0 / X.pc - 1) * 100
    pm = L.premarket
    pmv = pm["pm_volume"].fillna(0).to_numpy(float)
    df["pm_volume_rel"] = pmv / R._prior_window_stat(pmv, 20, np.mean, 10)
    df["pm_range_pct"] = (pm["pm_high"] - pm["pm_low"]).to_numpy(float) / L.pc * 100
    rp = L.range_pct
    med20 = R._prior_window_stat(rp, 20, np.median, 10)
    df["prev_range_rel"] = _lag(rp, 1) / med20
    df["prev_soxx_move_abs_pct"] = _lag(a, 1) * 100
    df["vol_regime_range20_pct"] = med20 * 100
    q_ma50 = pd.Series(Q.off).shift(1).rolling(50, min_periods=40).mean().to_numpy()
    df["qqq_above_50dma"] = (Q.pc > q_ma50).astype(float)
    df["soxx_ret20_abs_pct"] = np.abs(X.pc / _lag(X.pc, 20) - 1) * 100
    df["soxx_ret5_abs_pct"] = np.abs(X.pc / _lag(X.pc, 5) - 1) * 100
    ev = pd.read_csv(C.RESEARCH_DIR / "output" / "event_calendar.csv", parse_dates=["date"]).set_index("date")
    ev = ev.reindex(ctx.dates).fillna(False)
    df["earnings_day"] = ev[["earn_NVDA", "earn_AMD", "earn_AVGO", "earn_MU"]].any(axis=1).astype(float)
    df["fomc_day"] = ev["fomc"].astype(float)
    df["macro_0830_day"] = ev["macro_0830"].astype(float)
    df["monthly_opex"] = ctx.cal["monthly_opex"].reindex(ctx.dates).astype(float).to_numpy()
    df["dow"] = ctx.cal["dow"].reindex(ctx.dates).astype(float).to_numpy()
    # ---- known at 09:45 (bars 0..14 closed)
    p = L.p
    v15 = np.nansum(p.v[:, :15], axis=1)
    df["rvol15"] = v15 / R._prior_window_stat(v15, 20, np.mean, 10)
    hi, lo = np.nanmax(p.h[:, :15], axis=1), np.nanmin(p.l[:, :15], axis=1)
    df["or15_range_pct"] = (hi / lo - 1) * 100
    df["or15_range_atr"] = (hi - lo) / L.atr_prev
    d15 = p.c[:, 14] / L.o0 - 1
    xs, ns, qs = (T.p.c[:, 14] / T.o0 - 1 for T in (X, N, Q))
    df["drive15_abs_pct"] = np.abs(d15) * 100
    df["soxx_drive15_abs_pct"] = np.abs(xs) * 100
    df["gap_and_go"] = (np.sign(gap) == np.sign(d15)).astype(float)
    df["complex_agree15"] = ((np.sign(xs) == np.sign(d15)) & (np.sign(ns) == np.sign(d15)) &
                             (np.sign(qs) == np.sign(d15))).astype(float)
    df = df[(df.index >= "2019-01-02") & (df.index <= LAST_DAY) & df["day_type"].notna()]
    return df.replace([np.inf, -np.inf], np.nan)


def load_rule(vid: str, study: str, days: pd.DataFrame) -> pd.DataFrame:
    tr = pd.read_parquet(C.RESEARCH_DATA / "trades" / study / f"{vid}.parquet")
    tr = tr[tr["date"] <= LAST_DAY].join(days[["period", "day_type", "day_dir"]], on="date", how="inner")
    tr["right_dir"] = tr["s"].to_numpy() == tr["day_dir"].to_numpy()        # signal side = the day's final direction
    return tr


# ------------------------------------------------------------------ Part A
def setups_by_daytype(days: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for vid, st, label in RULES:
        tr = load_rule(vid, st, days)
        for dt, g in tr.groupby("day_type"):
            mu, t, _ = C.cluster_t(g["net_B"].to_numpy(), g["date"].to_numpy())
            r = {"rule": vid, "label": label, "day_type": dt, "trades": len(g), "win_rate": (g["net_B"] > 0).mean(),
                 "mean_net_bps": mu, "t": t, "right_direction_share": g["right_dir"].mean(),
                 "net_right_direction": g.loc[g["right_dir"], "net_B"].mean(),
                 "net_wrong_direction": g.loc[~g["right_dir"], "net_B"].mean()}
            for per in PERIODS:
                r[f"net_{per}"] = g.loc[g["period"] == per, "net_B"].mean()
            rows.append(r)
    return pd.DataFrame(rows)


def breakout_detail(days: pd.DataFrame) -> pd.DataFrame:
    """15-minute breakout (S3-01) on each day type, by entry time."""
    tr = load_rule("S3-01", "study3_opening_range_breakout", days)
    tr["entry_time"] = pd.cut(tr["entry_min"], [0, 600, 630, 720, 960], right=False,
                              labels=["09:45-10:00", "10:00-10:30", "10:30-12:00", "after 12:00"])
    rows = []
    for (dt, et), g in tr.groupby(["day_type", "entry_time"], observed=True):
        rows.append({"day_type": dt, "entry_time": et, "trades": len(g), "win_rate": (g["net_B"] > 0).mean(),
                     "mean_net_bps": g["net_B"].mean(), "right_direction_share": g["right_dir"].mean()})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ Part B
def conditions(days: pd.DataFrame, orb: pd.DataFrame) -> pd.DataFrame:
    """Each 09:30 / 09:45 condition in thirds (pooled 2019-2025 cut points; 0/1 for flags): share of trend and
    medium-or-trend days, and the 15-minute breakout's net per trade, per period."""
    rows = []
    orb_by_day = orb.groupby("date")["net_B"].mean()
    for f in FEATS_OPEN + FEATS_0945:
        x = days[f]
        if f in BINARY:
            b = x.map({0.0: "no", 1.0: "yes"})
            cuts = ""
        elif f == "dow":
            b = x.map({0.0: "Mon", 1.0: "Tue", 2.0: "Wed", 3.0: "Thu", 4.0: "Fri"})
            cuts = ""
        else:
            q1, q2 = np.nanquantile(x, [1 / 3, 2 / 3])
            b = pd.Series(np.where(x < q1, "low", np.where(x < q2, "mid", "high")), index=x.index).where(x.notna())
            cuts = f"low < {q1:.2f} <= mid < {q2:.2f} <= high"
        for lvl in [v for v in b.dropna().unique()]:
            m = b == lvl
            r = {"condition": f, "bucket": lvl, "cut_points": cuts, "days": int(m.sum())}
            for per in PERIODS + ("all",):
                mp = m & ((days["period"] == per) if per != "all" else True)
                dd = days[mp]
                r[f"trend_share_{per}"] = (dd["day_type"] == "trend").mean()
                r[f"med_or_trend_share_{per}"] = dd["day_type"].isin(["medium", "trend"]).mean()
                o = orb_by_day.reindex(dd.index).dropna()
                r[f"orb_net_{per}"] = o.mean()
                r[f"orb_trades_{per}"] = len(o)
            rows.append(r)
    c = pd.DataFrame(rows)
    base = {per: (days.loc[days["period"] == per, "day_type"] == "trend").mean() for per in PERIODS}
    for per in PERIODS:
        c[f"trend_lift_{per}"] = c[f"trend_share_{per}"] / base[per]
    c["lift_above_1_all_periods"] = np.all([c[f"trend_lift_{p}"] > 1 for p in PERIODS], axis=0)
    c["orb_positive_all_periods"] = np.all([c[f"orb_net_{p}"] > 0 for p in PERIODS], axis=0)
    return c


def detector(days: pd.DataFrame, feats: list[str], target: str, lam: float = 10.0):
    """Leave-one-period-out L2 logistic. Returns out-of-sample probabilities, the training-set tercile cut
    points used for each held-out period, AUCs and the full-sample weights."""
    y = (days["day_type"] == "trend") if target == "trend" else days["day_type"].isin(["medium", "trend"])
    y = y.astype(int).to_numpy()
    prob = pd.Series(np.nan, index=days.index)
    cut = {}
    aucs = {}

    def fit(mask):
        tr = days.loc[mask, feats]
        mu, sd = tr.mean(), tr.std().replace(0, 1)
        X = np.column_stack([np.ones(mask.sum()), ((tr - mu) / sd).fillna(0).clip(-5, 5).to_numpy()])
        w = _logit_l2(X, y[mask], lam)
        return mu, sd, w

    def score(mu, sd, w, mask):
        Z = ((days.loc[mask, feats] - mu) / sd).fillna(0).clip(-5, 5).to_numpy()
        return 1 / (1 + np.exp(-(w[0] + Z @ w[1:])))

    for per in PERIODS:
        test = (days["period"] == per).to_numpy()
        mu, sd, w = fit(~test)
        prob[test] = score(mu, sd, w, test)
        cut[per] = np.quantile(score(mu, sd, w, ~test), [1 / 3, 2 / 3])      # thresholds from the fitting periods
        aucs[per] = _auc(prob[test].to_numpy(), y[test])
    mu, sd, w = fit(np.ones(len(days), bool))
    weights = pd.Series(w[1:], index=feats)
    return prob, cut, aucs, weights


def orb_by_detector(days, prob, cut, rules=("S3-01", "S8-01")) -> pd.DataFrame:
    rows = []
    band = pd.Series("", index=days.index)
    for per in PERIODS:
        m = days["period"] == per
        band[m] = np.where(prob[m] < cut[per][0], "low", np.where(prob[m] < cut[per][1], "mid", "high"))
    for vid in rules:
        st = "study3_opening_range_breakout" if vid.startswith("S3") else "study8_execution"
        tr = load_rule(vid, st, days).join(band.rename("band"), on="date")
        for per in PERIODS + ("all",):
            g0 = tr if per == "all" else tr[tr["period"] == per]
            for bnd in ("low", "mid", "high"):
                g = g0[g0["band"] == bnd]
                mu, t, _ = C.cluster_t(g["net_B"].to_numpy(), g["date"].to_numpy()) if len(g) > 2 else (np.nan,) * 3
                dd = days[(band == bnd) & ((days["period"] == per) if per != "all" else True)]
                rows.append({"rule": vid, "period": per, "detector_band": bnd, "days": len(dd),
                             "trend_day_share": (dd["day_type"] == "trend").mean(),
                             "med_or_trend_share": dd["day_type"].isin(["medium", "trend"]).mean(),
                             "trades": len(g), "win_rate": (g["net_B"] > 0).mean() if len(g) else np.nan,
                             "mean_net_bps": mu, "t": t})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context()
    days = day_table(ctx)
    mix = days.groupby(["period", "day_type"]).size().unstack().reindex(list(PERIODS))
    mix = mix.div(mix.sum(axis=1), axis=0)
    setups = setups_by_daytype(days)
    detail = breakout_detail(days)
    orb = load_rule("S3-01", "study3_opening_range_breakout", days)
    cond = conditions(days, orb)
    det_rows, bands = [], []
    for name, feats in (("at 09:30", FEATS_OPEN), ("at 09:45", FEATS_OPEN + FEATS_0945)):
        for target in ("trend", "medium_or_trend"):
            prob, cut, aucs, w = detector(days, feats, target)
            top = w.reindex(w.abs().sort_values(ascending=False).index[:6])
            det_rows.append({"model": name, "target": target, **{f"auc_{p}": aucs[p] for p in PERIODS},
                             "largest_weights": ", ".join(f"{k} {v:+.2f}" for k, v in top.items())})
            if target == "trend":
                bands.append(orb_by_detector(days, prob, cut).assign(model=name))
    det = pd.DataFrame(det_rows)
    band_tbl = pd.concat(bands, ignore_index=True)
    for k, v in {"day_mix": mix.reset_index(), "setups_by_day_type": setups, "breakout_by_entry_time": detail,
                 "conditions": cond, "detector": det, "breakout_by_detector_band": band_tbl}.items():
        v.to_csv(OUT / f"{k}.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("== day mix (share of days)\n" + mix.round(3).to_string())
    print("\n== setups by day type\n" + setups[["rule", "label", "day_type", "trades", "win_rate", "mean_net_bps", "t",
                                               "right_direction_share", "net_pre", "net_dev", "net_val"]]
          .round(2).to_string(index=False))
    print("\n== 15-min breakout by entry time\n" + detail.round(2).to_string(index=False))
    show = ["condition", "bucket", "days", "trend_share_all", "trend_lift_pre", "trend_lift_dev", "trend_lift_val",
            "orb_net_pre", "orb_net_dev", "orb_net_val", "lift_above_1_all_periods", "orb_positive_all_periods"]
    print("\n== conditions\n" + cond[show].round(2).to_string(index=False))
    print("\n== detector (out-of-sample AUC by held-out period)\n" + det.round(3).to_string(index=False))
    print("\n== breakout by detector band (trend model)\n" + band_tbl.round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
