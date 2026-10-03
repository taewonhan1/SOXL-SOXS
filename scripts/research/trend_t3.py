#!/usr/bin/env python3
"""Study T3 (REGISTRY.md, registered 2026-10-03 before running; includes Study T2): exhaustive technical search for
trend days at 10:30.

Signals: SOXL >= 2% from its 09:30 open at the 10:29 close (direction s); the 3-4% subset is reported separately.
Targets: T1 = trend day that way (SOXX open->close x s >= 2%); REST = SOXL 10:30 open -> 15:55 open x s (no stop);
R = the 10:30 trade with a fixed 1.5% stop (case B), in R.
Features (about 150, all known by the 10:29 close; directional ones multiplied by s): daily technicals through the
prior close, prior-day levels and pivots, intraday technicals on bars 0..59, cross-asset moves, breadth, calendar.
Methods (fitted on 2019-2025 only; judged on 2011-06..2018 and 2026-01..09): univariate AUC screen with BH; all pairs
and triples of the top 40 features as tercile rules; L1 logistic (C = 0.05); LightGBM (fixed parameters); the
Study T2 score and logistic. Writes analysis/strategies/trend_t3/.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from runlib import ROOT  # noqa: I001
import trend_days as TD
import trend_detector as T1
from download_detector_data import MEMBERS
from soxlab import data as sdata
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "trend_t3"
START, END = "2011-03-23", "2026-09-25"
ERAS, TRAIN, TESTS, YEARS = T1.ERAS, T1.TRAIN, T1.TESTS, T1.YEARS
B = 59
CROSS = ["SOXX", "SMH", "NVDA", "QQQ", "SPY", "IWM", "TLT", "UUP", "GLD", "HYG", "VIXY", "EWT", "EWY", "XLK"]
LEADERS = ["NVDA", "AVGO", "AMD", "TSM"]
STOP = 0.015


def prior(x, w, fn=np.median, mn=10):
    return R._prior_window_stat(np.asarray(x, float), w, fn, mn)


def light60(ticker, dates):
    df = sdata.load_minute_bars(ticker, True, START, END, rth_only=True)
    c = sdata._pivot(df, "c", dates)[:, :60]
    o = sdata._pivot(df, "o", dates)[:, :60]
    v = np.nan_to_num(sdata._pivot(df, "v", dates)[:, :60])
    present = ~np.isnan(c)
    first = np.argmax(present, axis=1)
    has = present.any(axis=1) & (first <= 5)
    o0 = np.where(has, o[np.arange(len(dates)), first], np.nan)
    return o0, pd.DataFrame(c).ffill(axis=1).to_numpy(), v


def rsi_series(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 * up / (up + dn)


def daily_technicals(dates: pd.DatetimeIndex) -> tuple[pd.DataFrame, set]:
    """SOXL daily-bar technicals as of the prior close, aligned to dates. Returns (frame, directional names)."""
    D = sdata.load_daily("SOXL", True)[["o", "h", "l", "c"]].astype(float)
    D.index = pd.to_datetime(D.index).normalize()
    c, h, l = D["c"], D["h"], D["l"]
    f = pd.DataFrame(index=D.index)
    dirn = set()
    for n in (2, 5, 14):
        f[f"d_rsi{n}"] = rsi_series(c, n) - 50
        dirn.add(f"d_rsi{n}")
    for n in (5, 10, 20, 50, 100, 200):
        f[f"d_px_vs_sma{n}"] = c / c.rolling(n).mean() - 1
        dirn.add(f"d_px_vs_sma{n}")
    s20, s50 = c.rolling(20).mean(), c.rolling(50).mean()
    f["d_sma20_slope5"], f["d_sma50_slope10"] = s20 / s20.shift(5) - 1, s50 / s50.shift(10) - 1
    e12, e26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    f["d_macd"], f["d_macd_hist"] = macd / c, (macd - macd.ewm(span=9, adjust=False).mean()) / c
    m20, sd20 = c.rolling(20).mean(), c.rolling(20).std()
    f["d_bb_pctb"] = (c - (m20 - 2 * sd20)) / (4 * sd20) - 0.5
    f["d_bb_width"] = 4 * sd20 / m20
    ll14, hh14 = l.rolling(14).min(), h.rolling(14).max()
    f["d_stoch_k"] = (c - ll14) / (hh14 - ll14) - 0.5
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    upm, dnm = h.diff(), -l.diff()
    pdm = pd.Series(np.where((upm > dnm) & (upm > 0), upm, 0.0), index=D.index)
    ndm = pd.Series(np.where((dnm > upm) & (dnm > 0), dnm, 0.0), index=D.index)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    pdi = 100 * pdm.ewm(alpha=1 / 14, adjust=False).mean() / atr
    ndi = 100 * ndm.ewm(alpha=1 / 14, adjust=False).mean() / atr
    f["d_adx"] = (100 * (pdi - ndi).abs() / (pdi + ndi)).ewm(alpha=1 / 14, adjust=False).mean()
    f["d_di_diff"] = (pdi - ndi) / 100
    f["d_atr_pct"], f["d_atr_ratio_5_20"] = atr / c, tr.rolling(5).mean() / tr.rolling(20).mean()
    hh20, ll20 = h.rolling(20).max(), l.rolling(20).min()
    f["d_donchian_pos"] = (c - ll20) / (hh20 - ll20) - 0.5
    hh250, ll250 = h.rolling(250, min_periods=120).max(), l.rolling(250, min_periods=120).min()
    f["d_52w_pos"] = (c - ll250) / (hh250 - ll250) - 0.5
    for n in (1, 2, 5, 20):
        f[f"d_ret{n}"] = c / c.shift(n) - 1
    sg = np.sign(c.diff()).fillna(0)
    grp = (sg != sg.shift()).cumsum()
    f["d_streak"] = sg * sg.groupby(grp).cumcount().add(1)
    f["d_clv"] = ((c - l) - (h - c)) / (h - l)
    rng = (h - l) / c
    f["d_range_rel20"] = rng / rng.rolling(20).mean()
    f["d_nr4"] = ((h - l) <= (h - l).rolling(4).min()).astype(float)
    f["d_nr7"] = ((h - l) <= (h - l).rolling(7).min()).astype(float)
    f["d_inside"] = ((h < h.shift()) & (l > l.shift())).astype(float)
    dirn |= {"d_sma20_slope5", "d_sma50_slope10", "d_macd", "d_macd_hist", "d_bb_pctb", "d_stoch_k", "d_di_diff",
             "d_donchian_pos", "d_52w_pos", "d_ret1", "d_ret2", "d_ret5", "d_ret20", "d_streak", "d_clv"}
    return f.shift(1).reindex(dates), dirn


def other_daily(ticker: str, dates: pd.DatetimeIndex) -> pd.Series:
    d = sdata.load_daily(ticker, True)["c"].astype(float)
    d.index = pd.to_datetime(d.index).normalize()
    return d


def build(ctx) -> tuple[pd.DataFrame, list[str]]:
    dates = ctx.dates
    n = len(dates)
    L, X, S = ctx["SOXL"], ctx["SOXX"], ctx["SOXS"]
    p = L.p
    o0, pc = L.o0, L.pc
    c, h, l, v = p.c[:, :60], p.h[:, :60], p.l[:, :60], np.nan_to_num(p.v[:, :60])
    c59 = c[:, B]
    with np.errstate(all="ignore"):
        move = c59 / o0 - 1
    s = np.sign(move)
    F, dirn = {}, set()

    def add(name, val, directional=False):
        F[name] = np.asarray(val, float)
        if directional:
            dirn.add(name)

    with np.errstate(all="ignore"):
        # ---- stage-1 flags (Study T1 definitions)
        soxx_oc = X.last_c / X.o0 - 1
        rp = L.range_pct
        med20, med250 = prior(rp, 20), prior(rp, 250, mn=100)
        gap = o0 / pc - 1
        pdh, pdl, pdc = C.shift1(L.hi), C.shift1(L.lo), pc
        atr = L.atr_prev
        fl = {"F1_vol_hot": med20 / med250 >= 1.2, "F2_yday_trend": TD._lag(np.abs(soxx_oc), 1) >= 0.02,
              "F3_qqq_below": np.nan_to_num(TD.qqq_above_ma50(dates), nan=1) < 0.5,
              "F4_big_gap": np.abs(gap) / med20 >= 0.5, "F5_open_outside": (o0 > pdh) | (o0 < pdl)}
        for k, val in fl.items():
            add(k, np.asarray(val, float))
        add("stage1", sum(np.asarray(val, float) for val in fl.values()))
        add("abs_move", np.abs(move) * 100)
        add("move_scaled", np.abs(move) / prior(np.abs(move), 20))
        add("move_from_pc", (c59 / pc - 1), True)
        add("gap", gap, True)
        add("gap_atr", (o0 - pc) / atr, True)
        add("gap_agree", (np.sign(gap) == s).astype(float))
        gf = np.where(gap > 0, np.nanmin(l, axis=1) <= pc, np.where(gap < 0, np.nanmax(h, axis=1) >= pc, np.nan))
        add("gap_filled", gf)
        # ---- prior-day levels, pivots, prior week
        add("open_outside_dir", np.where((s > 0) & (o0 > pdh) | (s < 0) & (o0 < pdl), 1,
                                         np.where((s > 0) & (o0 < pdl) | (s < 0) & (o0 > pdh), -1, 0)))
        add("beyond_pd_level_atr", np.where(s > 0, (c59 - pdh) / atr, (pdl - c59) / atr))
        last5 = c[:, B - 4:B + 1]
        up_b, dn_b = np.nanmax(h, axis=1) > pdh, np.nanmin(l, axis=1) < pdl
        add("pd_level_hold", np.where(s > 0, np.where(up_b & (np.nanmin(last5, axis=1) > pdh), 1, np.where(up_b & (c59 <= pdh), -1, 0)),
                                      np.where(dn_b & (np.nanmax(last5, axis=1) < pdl), 1, np.where(dn_b & (c59 >= pdl), -1, 0))))
        add("vs_pdc_atr", (c59 - pdc) / atr, True)
        P = (pdh + pdl + pdc) / 3
        r1, s1, r2, s2 = 2 * P - pdl, 2 * P - pdh, P + (pdh - pdl), P - (pdh - pdl)
        add("pivot_pos_atr", (c59 - P) / atr, True)
        add("beyond_r1s1", np.where(s > 0, c59 > r1, c59 < s1).astype(float))
        add("beyond_r2s2", np.where(s > 0, c59 > r2, c59 < s2).astype(float))
        hi5 = pd.Series(L.hi).rolling(5).max().shift(1).to_numpy()
        lo5 = pd.Series(L.lo).rolling(5).min().shift(1).to_numpy()
        add("beyond_week_atr", np.where(s > 0, (c59 - hi5) / atr, (lo5 - c59) / atr))
        # ---- opening ranges
        for k in (5, 15, 30, 60):
            orh, orl = np.nanmax(h[:, :k], axis=1), np.nanmin(l[:, :k], axis=1)
            size = orh / orl - 1
            add(f"or{k}_size_rel", size / prior(size, 20))
            if k < 60:
                add(f"or{k}_pos", np.where(orh > orl, (c59 - orl) / (orh - orl) - 0.5, np.nan), True)
        or30h, or30l = np.nanmax(h[:, :30], axis=1), np.nanmin(l[:, :30], axis=1)
        add("or30_break_hold", np.where(s > 0, np.nanmin(last5, axis=1) > or30h, np.nanmax(last5, axis=1) < or30l).astype(float))
        # ---- intraday technicals
        r1m = np.diff(c, axis=1) / c[:, :-1]
        d14 = np.diff(c[:, B - 14:B + 1], axis=1)
        g, ls = np.clip(d14, 0, None).mean(axis=1), np.clip(-d14, 0, None).mean(axis=1)
        add("rsi1m_14", 100 * g / (g + ls) - 50, True)
        c5 = c[:, 4::5]
        d5 = np.diff(c5, axis=1)[:, -9:]
        g5, l5 = np.clip(d5, 0, None).mean(axis=1), np.clip(-d5, 0, None).mean(axis=1)
        add("rsi5m_9", 100 * g5 / (g5 + l5) - 50, True)
        cdf = pd.DataFrame(c.T)
        e9, e21 = cdf.ewm(span=9, adjust=False).mean().T.to_numpy(), cdf.ewm(span=21, adjust=False).mean().T.to_numpy()
        add("ema9_21_1m", (e9[:, B] - e21[:, B]) / c59, True)
        add("px_vs_ema21_1m", c59 / e21[:, B] - 1, True)
        add("ema21_slope10", e21[:, B] / e21[:, B - 10] - 1, True)
        c5df = pd.DataFrame(c5.T)
        e9_5, e21_5 = c5df.ewm(span=9, adjust=False).mean().T.to_numpy(), c5df.ewm(span=21, adjust=False).mean().T.to_numpy()
        add("ema9_21_5m", (e9_5[:, -1] - e21_5[:, -1]) / c59, True)
        e12, e26 = cdf.ewm(span=12, adjust=False).mean().T.to_numpy(), cdf.ewm(span=26, adjust=False).mean().T.to_numpy()
        macd = e12 - e26
        sig = pd.DataFrame(macd.T).ewm(span=9, adjust=False).mean().T.to_numpy()
        add("macd1m", macd[:, B] / c59, True)
        add("macd1m_hist", (macd[:, B] - sig[:, B]) / c59, True)
        w20 = c[:, B - 19:B + 1]
        m20, sd20 = w20.mean(axis=1), w20.std(axis=1)
        add("bb1m_pctb", (c59 - (m20 - 2 * sd20)) / (4 * sd20) - 0.5, True)
        vw, vsd = L.vwap[:, :60], L.vwap_sd[:, :60]
        add("vwap_dist_sd", (c59 - vw[:, B]) / vsd[:, B], True)
        add("vwap_side_share", ((c[:, 5:B + 1] - vw[:, 5:B + 1]) * s[:, None] > 0).mean(axis=1))
        add("vwap_crosses", (np.diff(np.sign(c - vw), axis=1) != 0).sum(axis=1))
        add("vwap_slope", vw[:, B] / vw[:, 29] - 1, True)
        path = np.concatenate([o0[:, None], c], axis=1)
        steps = np.abs(np.diff(path, axis=1))
        add("path_clean_0_59", np.abs(c59 - o0) / np.nansum(steps, axis=1))
        add("path_clean_30_59", np.abs(c59 - c[:, 29]) / np.nansum(steps[:, 30:], axis=1))
        ext = np.where(s > 0, np.nanmax(h, axis=1), np.nanmin(l, axis=1))
        add("pullback", np.where(s > 0, (ext - c59) / (ext - o0), (c59 - ext) / (o0 - ext)))
        add("recent_leg", c59 / c[:, 29] - 1, True)
        add("extreme_age", np.where(s > 0, B - np.argmax(np.where(np.isnan(h), -np.inf, h), axis=1),
                                     B - np.argmin(np.where(np.isnan(l), np.inf, l), axis=1)))
        add("volume_trend", v[:, 30:].sum(axis=1) / np.maximum(v[:, :30].sum(axis=1), 1))
        rng60 = np.nanmax(h, axis=1) / np.nanmin(l, axis=1) - 1
        add("range_expansion", rng60 / prior(rng60, 20))
        runmax = np.fmax.accumulate(h, axis=1)
        runmin = np.fmin.accumulate(l, axis=1)
        newx = np.where(s[:, None] > 0, h[:, 30:] > runmax[:, 29:B], l[:, 30:] < runmin[:, 29:B])
        add("new_extremes_30", newx.sum(axis=1))
        rv = np.nanstd(r1m, axis=1)
        add("rvol_1m_rel", rv / prior(rv, 20))
        cv = v.sum(axis=1)
        add("rel_volume", cv / prior(cv, 20, np.mean))
        sg = np.sign(np.diff(path, axis=1))
        add("upvol_share_0_59", (sg * v).sum(axis=1) / np.maximum(v.sum(axis=1), 1), True)
        add("upvol_share_30_59", (sg[:, 30:] * v[:, 30:]).sum(axis=1) / np.maximum(v[:, 30:].sum(axis=1), 1), True)
        csd, cdl, have = T1.load_flow(dates)
        add("tick_flow_to_1000", np.where(have & (cdl[:, 29] > 0), csd[:, 29] / np.where(cdl[:, 29] > 0, cdl[:, 29], 1), np.nan), True)
        add("max_1m_with", np.nanmax(r1m * s[:, None], axis=1))
        add("max_1m_against", np.nanmax(-r1m * s[:, None], axis=1))
        pm = L.premarket
        pmh, pml, pmlast = (pm[k].to_numpy(float) for k in ("pm_high", "pm_low", "pm_last"))
        add("pm_ret", pmlast / pc - 1, True)
        pmr = (pmh - pml) / pc
        add("pm_range_rel", pmr / prior(pmr, 20, np.mean))
        add("beyond_pm_level_atr", np.where(s > 0, (c59 - pmh) / atr, (pml - c59) / atr))
        # ---- cross-asset and breadth
        cross = {t: light60(t, dates) for t in CROSS}
        mv = {t: cross[t][1][:, B] / cross[t][0] - 1 for t in CROSS}
        for t in CROSS:
            add(f"x_{t}", mv[t], True)
        add("semis_vs_qqq", mv["SOXX"] - mv["QQQ"], True)
        add("soxx_vs_spy", mv["SOXX"] - mv["SPY"], True)
        mem = {t: light60(t, dates) for t in MEMBERS}
        M = np.array([mem[t][1][:, B] / mem[t][0] - 1 for t in MEMBERS])
        V = np.isfinite(M)
        nv = V.sum(axis=0)
        agree = (np.sign(M) == s[None, :]) & V
        add("breadth", np.where(nv >= 10, agree.sum(axis=0) / np.maximum(nv, 1), np.nan))
        li = [MEMBERS.index(t) for t in LEADERS]
        add("leaders", np.where(V[li].sum(axis=0) >= 3, agree[li].sum(axis=0) / np.maximum(V[li].sum(axis=0), 1), np.nan))
        add("breadth_1pct", np.where(nv >= 10, ((M * s[None, :] > 0.01) & V).sum(axis=0) / np.maximum(nv, 1), np.nan))
        others = np.where(V, M, np.nan)
        others[MEMBERS.index("NVDA")] = np.nan
        add("nvda_vs_rest", mv["NVDA"] - np.nanmedian(others, axis=0), True)
        add("members_mean", np.nanmean(np.where(V, M, np.nan), axis=0), True)
        add("members_disp", np.nanstd(np.where(V, M, np.nan), axis=0))
        # ---- daily context
        q = other_daily("QQQ", dates)
        add("qqq_vs_sma50", (q / q.rolling(50).mean() - 1).shift(1).reindex(dates).to_numpy(), True)
        sp = other_daily("SPY", dates)
        add("spy_vs_sma200", (sp / sp.rolling(200).mean() - 1).shift(1).reindex(dates).to_numpy(), True)
        for t in ("TLT", "UUP", "VIXY"):
            d = other_daily(t, dates)
            add(f"{t.lower()}_ret5", (d / d.shift(5) - 1).shift(1).reindex(dates).to_numpy(), True)
        sv = np.nan_to_num(S.p.v[:, :60]).sum(axis=1)
        ratio = sv / np.maximum(cv, 1)
        add("soxs_soxl_vol_rel", np.log(ratio / prior(ratio, 20)), True)
        # ---- calendar
        cal = ctx.cal
        add("dow", cal["dow"].to_numpy(float))
        add("month", dates.month.to_numpy(float))
        for k in ("month_end", "month_start", "quarter_end", "pre_holiday", "post_holiday"):
            add(f"cal_{k}", cal[k].to_numpy(float))
        wk = dates.to_period("W")
        opex_weeks = set(wk[cal["monthly_opex"].to_numpy(bool)])
        add("opex_week", np.array([w in opex_weeks for w in wk], float))
    feats = pd.DataFrame(F, index=dates)
    dt, ddir = daily_technicals(dates)
    feats = pd.concat([feats, dt], axis=1)
    dirn |= ddir
    for k in dirn:
        feats[k] = feats[k] * s
    feats["s"], feats["move_pct"] = s, move * 100
    feats["T1"] = (soxx_oc * s >= 0.02).astype(int)
    flat = (p.n_min - FLAT_OPEN).astype(int)
    rest = np.array([s[d] * (p.o[d, flat[d]] / p.o[d, B + 1] - 1) * 100 if B + 1 < flat[d] else np.nan for d in range(n)])
    feats["REST"] = rest
    feats["era"] = T1.era_of(pd.Series(dates))
    sel = (feats["era"] != "") & (np.abs(feats["move_pct"]) >= 2) & np.isfinite(feats["move_pct"])
    feats = feats[sel.to_numpy()].copy()
    feats["d"] = np.flatnonzero(sel.to_numpy())
    it = [{"d": int(d), "sig": B, "e": B + 1, "s": int(sd), "tx": int(flat[d]), "tx_kind": "open",
           "stop": p.o[d, B + 1] * (1 - sd * STOP)} for d, sd in zip(feats["d"], feats["s"]) if B + 1 < flat[d] and np.isfinite(p.o[d, B + 1])]
    ex = E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], {"B": C.cost_model(C.COMMISSION_B)})
    feats["R"] = pd.Series(ex["net_B"].to_numpy() / 100 / (STOP * 100), index=ex["d"].to_numpy().astype(int)).reindex(feats["d"]).to_numpy()
    names = [k for k in feats.columns if k not in ("s", "move_pct", "T1", "REST", "era", "d", "R")]
    feats = feats.replace([np.inf, -np.inf], np.nan)
    return feats, names


# ------------------------------------------------------------------------------------------------ evaluation
def auc(score, y):
    m = np.isfinite(score)
    return TD._auc(score[m], y[m]) if m.sum() > 20 and 0 < y[m].mean() < 1 else np.nan


def group_metrics(g: pd.DataFrame, era: str) -> dict:
    x = g["R"].dropna()
    return {"signals_per_year": len(g) / YEARS[era], "trend_share": g["T1"].mean() if len(g) else np.nan,
            "mean_REST": g["REST"].mean() if len(g) else np.nan, "mean_R": x.mean() if len(x) else np.nan}


def compare(df: pd.DataFrame, sel: np.ndarray, label: str) -> list[dict]:
    rows = []
    sub34 = (np.abs(df["move_pct"]) >= 3) & (np.abs(df["move_pct"]) < 4)
    for subset, m in (("2%+", np.ones(len(df), bool)), ("3-4%", sub34.to_numpy())):
        for era in ERAS:
            e = (df["era"] == era).to_numpy() & m
            base = df[e]
            rows.append({"model": label, "set": subset, "era": era, "base_trend": base["T1"].mean(),
                         **{f"top_{k}": v for k, v in group_metrics(df[e & sel], era).items()},
                         **{f"rest_{k}": v for k, v in group_metrics(df[e & ~sel], era).items()}})
    return rows


def univariate(df, names):
    tr = df[df["era"] == TRAIN]
    rows = []
    for f in names:
        y = tr["T1"].to_numpy()
        x = tr[f].to_numpy(float)
        m = np.isfinite(x)
        if m.sum() < 50 or np.nanstd(x) == 0:
            continue
        a = auc(x, y)
        try:
            pval = mannwhitneyu(x[m & (y == 1)], x[m & (y == 0)]).pvalue
        except ValueError:
            pval = np.nan
        r = {"feature": f, "train_auc": a, "p": pval}
        for era in TESTS:
            te = df[df["era"] == era]
            r[f"{era} auc"] = auc(te[f].to_numpy(float), te["T1"].to_numpy())
        rows.append(r)
    u = pd.DataFrame(rows)
    u["q_bh"] = C.bh_qvalues(u["p"].fillna(1).to_numpy())
    u["consistent"] = ((u[["train_auc"] + [f"{e} auc" for e in TESTS]] - 0.5).apply(np.sign).nunique(axis=1) == 1)
    return u.assign(strength=(u["train_auc"] - 0.5).abs()).sort_values("strength", ascending=False)


def combos(df, uni, k_top=40, rank_by="trend"):
    tr = (df["era"] == TRAIN).to_numpy()
    top = uni.head(k_top)
    fav = {}
    for _, r in top.iterrows():
        x = df[r["feature"]].to_numpy(float)
        lo, hi = np.nanquantile(x[tr], [1 / 3, 2 / 3])
        fav[r["feature"]] = np.nan_to_num(x, nan=np.nan) >= hi if r["train_auc"] > 0.5 else x <= lo
    names = list(fav)
    Fm = np.column_stack([fav[f] for f in names])
    y = df["T1"].to_numpy()
    rest = df["REST"].to_numpy()
    rows = []
    for k in (2, 3):
        for S in itertools.combinations(range(len(names)), k):
            sel = Fm[:, S].all(axis=1)
            m = sel & tr
            if m.sum() / YEARS[TRAIN] < 10:
                continue
            rows.append({"rule": " & ".join(names[i] for i in S), "train_signals_per_year": m.sum() / YEARS[TRAIN],
                         "train_trend_share": y[m].mean(), "train_mean_REST": rest[m].mean(), "_S": S})
    key = "train_trend_share" if rank_by == "trend" else "train_mean_REST"
    res = pd.DataFrame(rows).sort_values([key, "train_signals_per_year"], ascending=[False, False])
    top20 = res.head(20).reset_index(drop=True)
    for i, r in top20.iterrows():
        sel = Fm[:, list(r["_S"])].all(axis=1)
        for era in ERAS:
            g = df[sel & (df["era"] == era).to_numpy()]
            for kk, vv in group_metrics(g, era).items():
                top20.loc[i, f"{era} {kk}"] = vv
    best_sel = Fm[:, list(top20.iloc[0]["_S"])].all(axis=1)
    return top20.drop(columns="_S"), len(res), best_sel


def standardize(df, names):
    tr = df[df["era"] == TRAIN][names]
    mu, sd = tr.mean(), tr.std().replace(0, 1)
    return ((df[names] - mu) / sd).fillna(0).clip(-5, 5)


def l1_logistic(df, names, target="T1"):
    from sklearn.linear_model import LogisticRegression
    Z = standardize(df, names)
    tr = (df["era"] == TRAIN).to_numpy()
    m = LogisticRegression(penalty="l1", C=0.05, solver="liblinear", max_iter=2000).fit(Z[tr], df[target][tr])
    prob = m.predict_proba(Z)[:, 1]
    coef = pd.Series(m.coef_[0], index=names)
    return prob, coef[coef != 0].sort_values(key=np.abs, ascending=False)


def lgbm(df, names, target="T1"):
    import lightgbm as lgb
    tr = (df["era"] == TRAIN).to_numpy()
    params = dict(objective="binary", n_estimators=300, max_depth=3, num_leaves=7, learning_rate=0.03,
                  min_child_samples=30, colsample_bytree=0.7, subsample=0.7, subsample_freq=1, verbose=-1, random_state=7)
    m = lgb.LGBMClassifier(**params).fit(df.loc[tr, names], df.loc[tr, target])
    prob = m.predict_proba(df[names])[:, 1]
    imp = pd.Series(m.booster_.feature_importance("gain"), index=names).sort_values(ascending=False)
    return prob, imp


def t2_components(df):
    tr = (df["era"] == TRAIN).to_numpy()
    t2f = ["stage1", "move_scaled", "gap_agree", "path_clean_0_59", "vwap_side_share", "tick_flow_to_1000", "upvol_share_0_59",
           "breadth", "leaders", "x_VIXY", "semis_vs_qqq", "pd_level_hold", "pullback", "recent_leg", "extreme_age",
           "volume_trend", "range_expansion", "abs_move"]
    Z = standardize(df, t2f).to_numpy()
    X = np.column_stack([np.ones(tr.sum()), Z[tr]])
    w = TD._logit_l2(X, df["T1"].to_numpy()[tr], 10.0)
    prob = 1 / (1 + np.exp(-(w[0] + Z @ w[1:])))
    q = lambda f, qq: np.nanquantile(df.loc[tr, f], qq)                                 # noqa: E731
    comp = [(df["stage1"] >= 2), (df["breadth"] >= q("breadth", 2 / 3)), (df["semis_vs_qqq"] >= q("semis_vs_qqq", 2 / 3)),
            (df["x_VIXY"] >= q("x_VIXY", 2 / 3)), (df["pullback"] <= q("pullback", 1 / 3)), (df["recent_leg"] >= q("recent_leg", 2 / 3))]
    score = sum(np.asarray(cc, int) for cc in comp)
    return prob, score


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context(start=START, end=END)
    df, names = build(ctx)
    df = df.reset_index(drop=False).rename(columns={"index": "date"})
    df["CONT"] = (df["REST"] >= 2).astype(int)
    df.to_parquet(ROOT / "data" / "research" / "trend_t3_features.parquet", index=False)
    print(f"signals: {len(df)}  features: {len(names)}  base trend share by era: "
          f"{df.groupby('era')['T1'].mean().round(3).to_dict()}")
    uni = univariate(df, names)
    uni.to_csv(OUT / "univariate.csv", index=False, float_format="%.4f")
    rows = []
    tr = (df["era"] == TRAIN).to_numpy()
    top20, n_rules, best = combos(df, uni)
    top20.to_csv(OUT / "combos_top20.csv", index=False, float_format="%.4f")
    rows += compare(df, best, f"best pair/triple rule by trend share (of {n_rules}): {top20.iloc[0]['rule']}")
    top20r, n_rules_r, best_r = combos(df, uni, rank_by="rest")
    top20r.to_csv(OUT / "combos_top20_by_rest.csv", index=False, float_format="%.4f")
    rows += compare(df, best_r, f"best pair/triple rule by REST (of {n_rules_r}): {top20r.iloc[0]['rule']}")
    aucs = []
    p_l1, coef = l1_logistic(df, names)
    coef.to_csv(OUT / "l1_logistic_coef.csv", header=["coef"], float_format="%.4f")
    p_gb, imp = lgbm(df, names)
    imp.to_csv(OUT / "lgbm_importance.csv", header=["gain"], float_format="%.2f")
    p_t2, score_t2 = t2_components(df)
    p_l1c, coef_c = l1_logistic(df, names, "CONT")
    coef_c.to_csv(OUT / "l1_logistic_coef_CONT.csv", header=["coef"], float_format="%.4f")
    p_gbc, imp_c = lgbm(df, names, "CONT")
    imp_c.to_csv(OUT / "lgbm_importance_CONT.csv", header=["gain"], float_format="%.2f")
    for label, prob in (("L1 logistic", p_l1), ("LightGBM", p_gb), ("T2 logistic", p_t2),
                        ("L1 logistic, target CONT", p_l1c), ("LightGBM, target CONT", p_gbc)):
        cut = np.quantile(prob[tr], 2 / 3)
        rows += compare(df, prob >= cut, f"{label}, top third")
        tgt = "CONT" if "CONT" in label else "T1"
        aucs.append({"model": label, "target": tgt, **{f"{era} AUC": auc(prob[(df['era'] == era).to_numpy()],
                                                         df[tgt].to_numpy()[(df['era'] == era).to_numpy()]) for era in ERAS}})
    rows += compare(df, score_t2 >= 4, "T2 simple score 4-6")
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "models.csv", index=False, float_format="%.4f")
    pd.DataFrame(aucs).to_csv(OUT / "aucs.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 320)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.max_colwidth", 70)
    print("\n== univariate (top 25 by training strength)\n" + uni.head(25).round(3).to_string(index=False))
    print(f"\nfeatures consistent in all three eras: {int(uni['consistent'].sum())} of {len(uni)}; "
          f"q_bh <= 0.10 in training: {int((uni['q_bh'] <= 0.10).sum())}")
    print("\n== AUCs\n" + pd.DataFrame(aucs).round(3).to_string(index=False))
    show = ["model", "set", "era", "base_trend", "top_trend_share", "rest_trend_share", "top_mean_REST", "rest_mean_REST",
            "top_mean_R", "top_signals_per_year"]
    print("\n== top selections vs rest\n" + res[show].round(2).to_string(index=False))
    print("\n== best pair/triple rules (top 5)\n" + top20.head(5).round(2).to_string(index=False))
    print("\n== L1 logistic non-zero coefficients\n" + coef.round(3).to_string())
    print("\n== LightGBM top 15 by gain\n" + imp.head(15).round(1).to_string())
    print("\n== LightGBM (CONT) top 15 by gain\n" + imp_c.head(15).round(1).to_string())
    print("\n== best rules by REST (top 5)\n" + top20r.head(5).round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
