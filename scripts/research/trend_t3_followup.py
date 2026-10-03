#!/usr/bin/env python3
"""Exploratory follow-up to Study T3 (post-hoc; the registered verdict stands as it came out).

Reads the saved T3 feature table (data/research/trend_t3_features.parquet; run trend_t3.py first).
1. Continuation screen: per feature, AUC for CONT (REST >= 2%) and rank correlation with REST, per era.
2. Feature families: the strongest feature of each family (by training |AUC - 0.5|) for T1 and for CONT, with its
   test AUCs, so families such as RSI, yesterday's high/low/close, pivots and moving averages can be read off.
3. Model top third vs the rest: mean and median REST, t of the difference, mean R, per era. The T3 models are
   refitted exactly as registered (same features, data and fixed parameters).
4. A readable two-input table: SOXX's own move from its open at 10:29 x the share of the 23 members moving more than
   1% the same way, cut at the training terciles.
Writes analysis/strategies/trend_t3/followup_*.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr, ttest_ind

from runlib import ROOT  # noqa: I001
import trend_t3 as T3
from soxlab.research import common as C

ERAS, TRAIN, TESTS, YEARS = T3.ERAS, T3.TRAIN, T3.TESTS, T3.YEARS
FAMILIES = {
    "Size of the move so far": ["abs_move", "move_scaled", "move_from_pc", "x_SOXX", "x_SMH", "members_mean"],
    "Breadth across the 23 chip stocks": ["breadth", "breadth_1pct", "leaders", "nvda_vs_rest", "members_disp", "x_NVDA"],
    "Other markets at 10:29": ["x_QQQ", "x_SPY", "x_IWM", "x_XLK", "x_EWT", "x_EWY", "x_TLT", "x_UUP", "x_GLD", "x_HYG",
                               "x_VIXY", "semis_vs_qqq", "soxx_vs_spy"],
    "Recent volatility (daily)": ["d_atr_pct", "d_atr_ratio_5_20", "d_bb_width", "d_range_rel20", "d_nr4", "d_nr7",
                                  "d_inside", "F1_vol_hot"],
    "Daily RSI and stochastic": ["d_rsi2", "d_rsi5", "d_rsi14", "d_stoch_k"],
    "Intraday RSI (1- and 5-minute)": ["rsi1m_14", "rsi5m_9"],
    "Daily trend (SMAs, MACD, ADX, Bollinger, 52-week)": [
        "d_px_vs_sma5", "d_px_vs_sma10", "d_px_vs_sma20", "d_px_vs_sma50", "d_px_vs_sma100", "d_px_vs_sma200",
        "d_sma20_slope5", "d_sma50_slope10", "d_macd", "d_macd_hist", "d_adx", "d_di_diff", "d_donchian_pos",
        "d_52w_pos", "d_bb_pctb"],
    "Prior days' returns and candle": ["d_ret1", "d_ret2", "d_ret5", "d_ret20", "d_streak", "d_clv", "F2_yday_trend"],
    "Yesterday's high, low and close": ["beyond_pd_level_atr", "pd_level_hold", "vs_pdc_atr", "open_outside_dir",
                                        "F5_open_outside"],
    "Pivots and prior week's high/low": ["pivot_pos_atr", "beyond_r1s1", "beyond_r2s2", "beyond_week_atr"],
    "Gap and pre-market": ["gap", "gap_atr", "gap_agree", "gap_filled", "F4_big_gap", "pm_ret", "pm_range_rel",
                           "beyond_pm_level_atr"],
    "Opening ranges": ["or5_size_rel", "or5_pos", "or15_size_rel", "or15_pos", "or30_size_rel", "or30_pos",
                       "or60_size_rel", "or30_break_hold", "range_expansion"],
    "Intraday EMA, MACD, Bollinger, VWAP": ["ema9_21_1m", "px_vs_ema21_1m", "ema21_slope10", "ema9_21_5m", "macd1m",
                                            "macd1m_hist", "bb1m_pctb", "vwap_dist_sd", "vwap_side_share",
                                            "vwap_crosses", "vwap_slope"],
    "Path shape": ["path_clean_0_59", "path_clean_30_59", "pullback", "recent_leg", "extreme_age", "new_extremes_30",
                   "max_1m_with", "max_1m_against", "rvol_1m_rel"],
    "Volume and order flow": ["volume_trend", "rel_volume", "upvol_share_0_59", "upvol_share_30_59",
                              "tick_flow_to_1000", "soxs_soxl_vol_rel"],
    "Market regime (daily)": ["qqq_vs_sma50", "spy_vs_sma200", "F3_qqq_below", "tlt_ret5", "uup_ret5", "vixy_ret5"],
    "Calendar": ["dow", "month", "cal_month_end", "cal_month_start", "cal_quarter_end", "cal_pre_holiday",
                 "cal_post_holiday", "opex_week"],
    "Pre-open flag count": ["stage1"],
}
NON_FEATURES = ("s", "move_pct", "T1", "REST", "era", "d", "R", "date", "CONT")


def cont_screen(df: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    rows = []
    for f in names:
        r = {"feature": f}
        for era in ERAS:
            g = df[df["era"] == era]
            x = g[f].to_numpy(float)
            m = np.isfinite(x)
            r[f"{era} auc"] = T3.auc(x, g["CONT"].to_numpy())
            r[f"{era} rho_REST"] = spearmanr(x[m], g["REST"].to_numpy()[m]).statistic if m.sum() > 20 and np.nanstd(x) > 0 else np.nan
        tr = df[df["era"] == TRAIN]
        x, y = tr[f].to_numpy(float), tr["CONT"].to_numpy()
        m = np.isfinite(x)
        try:
            r["p"] = mannwhitneyu(x[m & (y == 1)], x[m & (y == 0)]).pvalue
        except ValueError:
            r["p"] = np.nan
        rows.append(r)
    u = pd.DataFrame(rows)
    u["q_bh"] = C.bh_qvalues(u["p"].fillna(1).to_numpy())
    cols = [f"{e} auc" for e in ERAS]
    u["consistent"] = (u[cols] - 0.5).apply(np.sign).nunique(axis=1) == 1
    u["strength"] = (u[f"{TRAIN} auc"] - 0.5).abs()
    return u.sort_values("strength", ascending=False)


def family_table(uni_t1: pd.DataFrame, uni_c: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fam, feats in FAMILIES.items():
        for target, u, tcol in (("T1", uni_t1, "train_auc"), ("CONT", uni_c, f"{TRAIN} auc")):
            sub = u[u["feature"].isin(feats)].copy()
            sub["strength"] = (sub[tcol] - 0.5).abs()
            b = sub.sort_values("strength", ascending=False).iloc[0]
            te = {e: b[f"{e} auc"] for e in TESTS}
            rows.append({"family": fam, "target": target, "best_feature": b["feature"], "train_auc": b[tcol],
                         **{f"{e} auc": v for e, v in te.items()}, "consistent": bool(b["consistent"])})
    return pd.DataFrame(rows)


def top_vs_rest(df: pd.DataFrame, prob: np.ndarray, label: str) -> list[dict]:
    tr = (df["era"] == TRAIN).to_numpy()
    top = prob >= np.quantile(prob[tr], 2 / 3)
    rows = []
    for era in ERAS:
        e = (df["era"] == era).to_numpy()
        a, b = df.loc[e & top, "REST"].dropna(), df.loc[e & ~top, "REST"].dropna()
        ra, rb = df.loc[e & top, "R"].dropna(), df.loc[e & ~top, "R"].dropna()
        rows.append({"model": label, "era": era, "top_per_year": len(a) / YEARS[era], "top_REST": a.mean(),
                     "rest_REST": b.mean(), "top_median_REST": a.median(), "rest_median_REST": b.median(),
                     "t_diff": ttest_ind(a, b, equal_var=False).statistic, "top_win": (a > 0).mean(),
                     "top_R": ra.mean(), "rest_R": rb.mean(), "t_top_R": ra.mean() / ra.std() * np.sqrt(len(ra))})
    return rows


def soxx_breadth(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    tr = (df["era"] == TRAIN).to_numpy()
    cuts = {f: np.nanquantile(df.loc[tr, f], [1 / 3, 2 / 3]) for f in ("x_SOXX", "breadth_1pct")}

    def terc(f):
        x = df[f].to_numpy(float)
        return np.where(~np.isfinite(x), np.nan, np.where(x >= cuts[f][1], 2, np.where(x >= cuts[f][0], 1, 0)))

    ts, tb = terc("x_SOXX"), terc("breadth_1pct")
    groups = {"both top tercile": (ts == 2) & (tb == 2), "one top, other not bottom": ((ts == 2) & (tb == 1)) | ((ts == 1) & (tb == 2)),
              "either bottom tercile": (ts == 0) | (tb == 0), "all with move >= 2%": np.ones(len(df), bool)}
    rows = []
    for g, m in groups.items():
        for era in ERAS:
            x = df[m & (df["era"] == era).to_numpy()]
            rows.append({"group": g, "era": era, "per_year": len(x) / YEARS[era], "trend_share": x["T1"].mean(),
                         "cont_share": x["CONT"].mean(), "mean_REST": x["REST"].mean(), "median_REST": x["REST"].median(),
                         "mean_R": x["R"].mean()})
    return pd.DataFrame(rows), {f: [round(float(c), 4) for c in v] for f, v in cuts.items()}


def main() -> None:
    df = pd.read_parquet(ROOT / "data" / "research" / "trend_t3_features.parquet")
    names = [k for k in df.columns if k not in NON_FEATURES]
    assigned = [f for v in FAMILIES.values() for f in v]
    assert sorted(assigned) == sorted(names), set(names) ^ set(assigned)
    uni_t1 = pd.read_csv(T3.OUT / "univariate.csv")
    uni_c = cont_screen(df, names)
    uni_c.to_csv(T3.OUT / "followup_cont_univariate.csv", index=False, float_format="%.4f")
    fam = family_table(uni_t1, uni_c)
    fam.to_csv(T3.OUT / "followup_families.csv", index=False, float_format="%.4f")
    rows = []
    for target in ("T1", "CONT"):
        p_l1, _ = T3.l1_logistic(df, names, target)
        p_gb, _ = T3.lgbm(df, names, target)
        rows += top_vs_rest(df, p_l1, f"L1 logistic, target {target}")
        rows += top_vs_rest(df, p_gb, f"LightGBM, target {target}")
    tvr = pd.DataFrame(rows)
    tvr.to_csv(T3.OUT / "followup_top_vs_rest.csv", index=False, float_format="%.4f")
    sb, cuts = soxx_breadth(df)
    sb.to_csv(T3.OUT / "followup_soxx_breadth.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 200)
    print("== continuation screen (top 25 by training strength)\n" + uni_c.head(25).round(3).to_string(index=False))
    print(f"\nCONT: consistent in all three eras {int(uni_c['consistent'].sum())} of {len(uni_c)}; "
          f"q_bh <= 0.10 in training: {int((uni_c['q_bh'] <= 0.10).sum())}")
    print("\n== families\n" + fam.round(3).to_string(index=False))
    print("\n== model top third vs rest\n" + tvr.round(2).to_string(index=False))
    print(f"\n== SOXX move x breadth (training tercile cuts {cuts})\n" + sb.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
