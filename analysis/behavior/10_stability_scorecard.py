"""Stability across quarters and the comparison scorecard.

Per-quarter metrics (full days) use the same definitions as scripts 03-08 (compact re-implementation):
range/ATR, 1-min RMS, deseasonalised AC(1m, 5m), deseasonalised VR(15), VR(60), trend/range-day
shares, HOD/LOD-in-first-60 share, OR30 close-beyond-break share, gap-fill (0.1-0.5 ATR gaps),
VWAP crosses (0.02 ATR band), last-30 ~ 09:30-15:30 slope, 5-min beta to SOXX, pre-market volume
share, median tick size in bps. Persistence summary: mean/min/max across quarters, share of quarters
on the same side of the random-walk / zero reference, and primary-vs-secondary difference in units of
the quarterly standard deviation. The scorecard is assembled from the full-window CSVs of 03-09."""
from __future__ import annotations

import numpy as np
import pandas as pd

import plotstyle as ps
from common import MAIN, OUT, PANEL, Tk, block_sum, robust_ac, save_csv


def deseason(r):
    sd = np.sqrt(np.nanmean(r ** 2, axis=1, keepdims=True))
    z = r / sd
    return z / np.sqrt(np.nanmean(z ** 2, axis=0, keepdims=True))


def vr(z, qq):
    mu = np.nanmean(z)
    e = z - mu
    cs = np.concatenate([np.zeros((z.shape[0], 1)), np.nancumsum(z, axis=1)], axis=1)
    S = cs[:, qq:] - cs[:, :-qq] - qq * mu
    return (np.nanmean(S ** 2) / qq) / np.nanmean(e ** 2)


def quarter_metrics(t, T, dm, X):
    rows = []
    for qtr in sorted(set(T.quarter[np.isin(T.period, ["primary", "secondary"])])):
        sel = T.full & (T.quarter == qtr) & np.isin(T.period, ["primary", "secondary"])
        if sel.sum() < 20:
            continue
        D = dm[sel]
        r = T.r1[sel]
        r1 = r[:, 1:]
        z = deseason(r1)
        ac1, _, _ = robust_ac(z[:, :-1].ravel(), z[:, 1:].ravel())
        Z5 = block_sum(z, 5)
        ac5, _, _ = robust_ac(Z5[:, :-1].ravel(), Z5[:, 1:].ravel())
        body = (D.C - D.O).abs() / (D.H - D.L)
        clv = (D.C - D.L) / (D.H - D.L)
        up = D.C > D.O
        trend = (body >= 0.7) & (((clv >= 0.85) & up) | ((clv <= 0.15) & ~up))
        k_hi, k_lo = np.nanargmax(T.H[sel], 1), np.nanargmin(T.L[sel], 1)
        # OR30
        Hm, Lm = T.H[sel], T.L[sel]
        orh, orl = Hm[:, :30].max(1), Lm[:, :30].min(1)
        bu, bd = Hm[:, 30:] > orh[:, None], Lm[:, 30:] < orl[:, None]
        ku = np.where(bu.any(1), bu.argmax(1), 10 ** 6)
        kd = np.where(bd.any(1), bd.argmax(1), 10 ** 6)
        Cc = D.C.to_numpy()
        cb = np.where(ku < kd, Cc > orh, np.where(kd < ku, Cc < orl, np.nan))
        # gap fill for 0.1-0.5 ATR gaps
        g = D.gap_pct.to_numpy()
        gatr = np.abs(g) / D.atr14_prev.to_numpy()
        pc = D.prevC_adj.to_numpy()
        filled = np.where(g > 0, Lm.min(1) <= pc, Hm.max(1) >= pc)
        mg = (gatr >= 0.1) & (gatr < 0.5)
        # VWAP crosses with 0.02 ATR hysteresis
        V, VW, C = T.V[sel], T.VW[sel], T.C[sel]
        vwap = np.nancumsum(VW * V, 1) / np.nancumsum(V, 1)
        band = (0.02 * D.atr14_prev.to_numpy() / 100)[:, None] * vwap
        d = C - vwap
        state = np.zeros(len(d))
        cnt = np.zeros(len(d))
        for k in range(5, 390):
            u, dn = d[:, k] > band[:, k], d[:, k] < -band[:, k]
            cnt += ((state < 0) & u) | ((state > 0) & dn)
            state = np.where(u, 1, np.where(dn, -1, state))
        # last-30 vs 09:30-15:30
        rl30 = np.log(Cc / C[:, 359])
        rday = np.log(C[:, 359] / D.O.to_numpy())
        slope = np.polyfit(rday, rl30, 1)[0]
        # beta to SOXX at 5-min
        if t != "SOXX":
            s2 = sel & X.full
            bx = block_sum(X.r1[s2][:, 1:], 5).ravel()
            by = block_sum(T.r1[s2][:, 1:], 5).ravel()
            beta = np.cov(by, bx)[0, 1] / np.var(bx, ddof=1)
        else:
            beta = 1.0
        tot = D.pm_vol.fillna(0) + D.V_rth + D.ah_vol.fillna(0)
        rows.append({"ticker": t, "quarter": qtr, "n_days": int(sel.sum()),
                     "median_range_pct": D.range_pct.median(), "median_atr14_pct": D.atr14_pct.median(),
                     "rms_1m_bps": 1e4 * np.sqrt(np.nanmean(r ** 2)),
                     "ac1_1m_deseason": ac1, "ac1_5m_deseason": ac5, "VR15_deseason": vr(z, 15), "VR60_deseason": vr(z, 60),
                     "trend_day_pct": 100 * trend.mean(), "range_day_pct(body<=0.3)": 100 * (body <= 0.3).mean(),
                     "HOD_or_LOD_first60_pct": 100 * ((k_hi < 60) | (k_lo < 60)).mean(),
                     "OR30_close_beyond_first_break_pct": 100 * np.nanmean(cb),
                     "gapfill_0.1-0.5ATR_pct": 100 * filled[mg].mean() if mg.sum() >= 5 else np.nan,
                     "vwap_crosses_band_mean": cnt.mean(), "last30_on_0930_1530_slope": slope,
                     "beta_5m_vs_SOXX": beta, "premarket_vol_share_pct": 100 * (D.pm_vol / tot).median(),
                     "median_tick_bps": np.median(100 / D.C_unadj.to_numpy()),
                     "pct_zero_1m_returns": 100 * np.mean(r1 == 0)})
    return rows


REF = {"ac1_1m_deseason": 0, "ac1_5m_deseason": 0, "VR15_deseason": 1, "VR60_deseason": 1,
       "OR30_close_beyond_first_break_pct": 50, "last30_on_0930_1530_slope": 0}


def persistence(Q):
    out = []
    for (t), g in Q.groupby("ticker"):
        g = g.sort_values("quarter")
        sec = g[g.quarter <= "2024Q3"]
        pri = g[g.quarter >= "2024Q4"]
        for col in [c for c in g.columns if c not in ("ticker", "quarter", "n_days")]:
            x = g[col].astype(float)
            row = {"ticker": t, "metric": col, "n_quarters": int(x.notna().sum()), "mean_q": x.mean(),
                   "min_q": x.min(), "max_q": x.max(), "sd_q": x.std(),
                   "mean_secondary_q": sec[col].mean(), "mean_primary_q": pri[col].mean(),
                   "diff_primary_minus_secondary_in_sd_q": (pri[col].mean() - sec[col].mean()) / x.std() if x.std() > 0 else np.nan}
            if col in REF:
                ref = REF[col]
                row["reference"] = ref
                row["pct_quarters_below_ref"] = 100 * (x < ref).mean()
                row["pct_quarters_above_ref"] = 100 * (x > ref).mean()
            out.append(row)
    return pd.DataFrame(out)


def scorecard():
    rd = pd.read_csv(OUT / "vol_daily_range_atr.csv")
    rv = pd.read_csv(OUT / "vol_realized_by_horizon.csv")
    ac = pd.read_csv(OUT / "dir_autocorr_by_horizon.csv")
    vrr = pd.read_csv(OUT / "dir_variance_ratios.csv")
    dfa = pd.read_csv(OUT / "dir_dfa_hurst.csv")
    ev = pd.read_csv(OUT / "dir_continuation_after_large_moves.csv")
    runs = pd.read_csv(OUT / "dir_run_lengths.csv")
    er = pd.read_csv(OUT / "dir_efficiency_ratio.csv")
    dt = pd.read_csv(OUT / "day_types.csv")
    gp = pd.read_csv(OUT / "open_gap_distribution.csv")
    gf = pd.read_csv(OUT / "open_gap_fill_rates.csv")
    orr = pd.read_csv(OUT / "open_opening_range.csv", dtype={"OR_minutes": str})
    vw = pd.read_csv(OUT / "vwap_behaviour.csv")
    gh = pd.read_csv(OUT / "close_intraday_momentum_ghlz.csv")
    l10 = pd.read_csv(OUT / "close_last10min_and_auction.csv")
    bt = pd.read_csv(OUT / "link_betas_correlations.csv")
    eh = pd.read_csv(OUT / "ext_hours_summary.csv")
    tl = pd.read_csv(OUT / "tails_frequency.csv")
    cov = pd.read_csv(OUT / "data_coverage.csv")
    tables = {}
    for per in ("primary", "secondary"):
        rows = {}
        for t in MAIN:
            def one(df, cond, col):
                x = df[cond & (df.ticker == t) & (df.period == per)] if "period" in df else df[cond & (df.ticker == t)]
                return x[col].iloc[0] if len(x) else np.nan
            T_ = np.ones(len(rd), bool)
            s = {}
            s["daily range % median (p10-p90)"] = f"{one(rd, T_, 'range_pct_median'):.2f} ({one(rd, T_, 'range_pct_p10'):.2f}-{one(rd, T_, 'range_pct_p90'):.2f})"
            s["ATR14 % median"] = round(one(rd, T_, "atr14_pct_median"), 2)
            s["% days range >5% / >10%"] = f"{one(rd, T_, 'share_range_gt_5pct'):.1f} / {one(rd, T_, 'share_range_gt_10pct'):.1f}"
            s["1-min RMS return (bps)"] = round(one(rv, rv.h_min.astype(str) == "1", "rms_bps"), 1)
            s["RTH ann. vol from 1-min (%)"] = round(one(rv, rv.h_min.astype(str) == "1", "ann_vol_pct"), 1)
            s["overnight ann. vol (%)"] = round(one(rv, rv.h_min.astype(str) == "overnight_prevclose_to_open", "ann_vol_pct"), 1)
            s["AC 1-min (deseas.) [t]"] = f"{one(ac, ac.h_min == 1, 'ac1_deseasonalised'):+.3f} [{one(ac, ac.h_min == 1, 'robust_t_deseasonalised'):+.1f}]"
            s["AC 5-min (deseas.) [t]"] = f"{one(ac, ac.h_min == 5, 'ac1_deseasonalised'):+.3f} [{one(ac, ac.h_min == 5, 'robust_t_deseasonalised'):+.1f}]"
            s["VR(15) deseas. [z]"] = f"{one(vrr, vrr.q_min == 15, 'VR_overlap_deseasonalised'):.3f} [{one(vrr, vrr.q_min == 15, 'z_robust_deseasonalised'):+.1f}]"
            s["VR(60) deseas. [z]"] = f"{one(vrr, vrr.q_min == 60, 'VR_overlap_deseasonalised'):.3f} [{one(vrr, vrr.q_min == 60, 'z_robust_deseasonalised'):+.1f}]"
            s["VR(60) non-overlap raw [95% CI]"] = f"{one(vrr, vrr.q_min == 60, 'VR_nonoverlap_raw'):.2f} [{one(vrr, vrr.q_min == 60, 'VR_nonoverlap_raw_ci95_lo'):.2f}-{one(vrr, vrr.q_min == 60, 'VR_nonoverlap_raw_ci95_hi'):.2f}]"
            a = one(dfa, dfa.segment == "full_day_389min", "alpha_5_129")
            b = one(dfa, dfa.segment == "full_day_389min", "alpha_shuffled_5_129")
            s["DFA alpha (shuffled)"] = f"{a:.3f} ({b:.3f})"
            s["after 1-min |z|>=2: signed fwd 5m bps [% cont.]"] = f"{one(ev, (ev.event == '1m_|z|>=2') & (ev.tod == 'all_to_15:30') & (ev.H_min == 5), 'mean_signed_fwd_bps'):+.1f} [{one(ev, (ev.event == '1m_|z|>=2') & (ev.tod == 'all_to_15:30') & (ev.H_min == 5), 'pct_continuation'):.1f}]"
            s["after 5-min |z|>=2: signed fwd 15m bps [% cont.]"] = f"{one(ev, (ev.event == '5m_|z|>=2') & (ev.tod == 'all_to_15:30') & (ev.H_min == 15), 'mean_signed_fwd_bps'):+.1f} [{one(ev, (ev.event == '5m_|z|>=2') & (ev.tod == 'all_to_15:30') & (ev.H_min == 15), 'pct_continuation'):.1f}]"
            s["mean run length 1-min (shuffled)"] = f"{one(runs, runs.ticker == runs.ticker, 'mean_run_obs'):.3f} ({one(runs, runs.ticker == runs.ticker, 'mean_run_shuffled'):.3f})"
            s["% zero-return minutes"] = round(one(runs, runs.ticker == runs.ticker, "pct_zero_return_minutes"), 2)
            s["efficiency ratio full day: obs/random"] = round(one(er, er.window == "full_day", "ratio_mean_ER_obs_to_random"), 3)
            s["trend days % (body>=0.7 & close at extreme)"] = round(one(dt, dt.ticker == dt.ticker, "pct_trend_day(body>=0.7 & close in extreme 15% in body direction)"), 1)
            s["range days % (body<=0.3)"] = round(one(dt, dt.ticker == dt.ticker, "pct_body_le_0.3"), 1)
            s["close in top/bottom 15%: obs (random)"] = f"{one(dt, dt.ticker == dt.ticker, 'closepath_pct_close_extreme15'):.1f} ({one(dt, dt.ticker == dt.ticker, 'RANDOM_pct_close_extreme15'):.1f})"
            s["HOD or LOD in first 60 min %: obs (random)"] = f"{one(dt, dt.ticker == dt.ticker, 'pct_HOD_or_LOD_first60'):.1f} ({one(dt, dt.ticker == dt.ticker, 'RANDOM_pct_HOD_or_LOD_first60'):.1f})"
            s["median |gap| %"] = round(one(gp, gp.ticker == gp.ticker, "absgap_median"), 2)
            s["% |gap|>2%"] = round(one(gp, gp.ticker == gp.ticker, "pct_absgap_gt_2"), 1)
            s["gap fill % (0.25-0.5 ATR gaps)"] = round(one(gf, (gf.bin_unit == "ATR") & (gf.bin_lo == 0.25) & (gf.direction == "all"), "fill_rate_pct"), 1)
            s["OR30 size % / share of day range"] = f"{one(orr, orr.OR_minutes == '30', 'median_OR_size_pct'):.2f} / {one(orr, orr.OR_minutes == '30', 'median_OR_share_of_day_range'):.2f}"
            s["OR30: close beyond 1st break %"] = round(one(orr, orr.OR_minutes == "30", "pct_close_beyond_first_break_level"), 1)
            s["OR30: both sides broken %"] = round(one(orr, orr.OR_minutes == "30", "pct_both_sides_broken"), 1)
            s["first-hour share of day range (median)"] = round(one(orr, orr.OR_minutes == "first_hour_summary", "median_first_hour_share_of_day_range"), 2)
            s["first-hour share of RTH minute volume"] = round(one(orr, orr.OR_minutes == "first_hour_summary", "median_first_hour_share_of_RTH_minute_volume"), 2)
            s["median |dist. from VWAP| after 10:00 (bps; ATR)"] = f"{one(vw, vw.ticker == vw.ticker, 'median_abs_dist_bps_from_10:00'):.0f}; {one(vw, vw.ticker == vw.ticker, 'median_abs_dist_ATR_from_10:00'):.2f}"
            s["VWAP crosses/day, 0.02-ATR band: obs (random)"] = f"{one(vw, vw.ticker == vw.ticker, 'mean_crosses_per_day_band0.02ATR'):.2f} ({one(vw, vw.ticker == vw.ticker, 'RANDOM_mean_crosses_band0.02ATR'):.2f})"
            s["revisit VWAP <=30m after 1-sd close: obs (random) %"] = f"{one(vw, vw.ticker == vw.ticker, 'pct_revisit_30m_after_1sd_close'):.1f} ({one(vw, vw.ticker == vw.ticker, 'RANDOM_pct_revisit_30m_after_1sd_close'):.1f})"
            s["one side of VWAP after 10:30 %: obs (random)"] = f"{one(vw, vw.ticker == vw.ticker, 'pct_days_one_side_after_10:30_closes'):.1f} ({one(vw, vw.ticker == vw.ticker, 'RANDOM_pct_days_one_side_after_10:30_closes'):.1f})"
            s["last30 ~ first half-hour (GHLZ) slope [t]"] = f"{one(gh, gh.model.str.startswith('last30 ~ prevclose_to_10:00'), 'slope'):+.3f} [{one(gh, gh.model.str.startswith('last30 ~ prevclose_to_10:00'), 't_NW'):+.1f}]"
            s["last30 ~ 09:30-15:30 slope [t]"] = f"{one(gh, gh.model == 'last30 ~ 09:30_to_15:30', 'slope'):+.3f} [{one(gh, gh.model == 'last30 ~ 09:30_to_15:30', 't_NW'):+.1f}]"
            s["median |closing-auction jump| bps"] = round(one(l10, l10.ticker == l10.ticker, "median_abs_auction_jump_bps"), 1)
            s["15:30-15:59 share of RTH minute volume %"] = round(one(l10, l10.ticker == l10.ticker, "pct_RTH_minute_volume_15:30-15:59"), 1)
            drv = "QQQ" if t == "SOXX" else "SOXX"
            x = bt[(bt.y == t) & (bt.x == drv) & (bt.period == per)]
            s["5-min beta / corr vs SOXX (SOXX: vs QQQ)"] = f"{x.beta_5m.iloc[0]:+.2f} / {x.corr_5m.iloc[0]:+.3f}" if len(x) else ""
            x = bt[(bt.y == t) & (bt.x == "QQQ") & (bt.period == per)]
            s["5-min beta / corr vs QQQ"] = f"{x.beta_5m.iloc[0]:+.2f} / {x.corr_5m.iloc[0]:+.3f}" if len(x) else ("1 / 1" if t == "QQQ" else "")
            s["pre-market vol share % (median)"] = round(one(eh, eh.ticker == eh.ticker, "median_premarket_vol_share_pct"), 1)
            s["pre-market range % of prev close (median)"] = round(one(eh, eh.ticker == eh.ticker, "median_premarket_range_pct_of_prevclose"), 2)
            s["RTH takes PM high / PM low %"] = f"{one(eh, eh.ticker == eh.ticker, 'pct_RTH_takes_PM_high'):.1f} / {one(eh, eh.ticker == eh.ticker, 'pct_RTH_takes_PM_low'):.1f}"
            s["% minutes |1m|>1%"] = round(one(tl, tl.ticker == tl.ticker, "pct_minutes_abs1m>1%"), 3)
            s["% days with a |1m|>2% move"] = round(one(tl, tl.ticker == tl.ticker, "pct_days_with_any_abs1m>2%"), 1)
            s["median unadjusted price $ / 1-cent tick (bps)"] = f"{one(l10, l10.ticker == l10.ticker, 'median_unadj_price'):.2f} / {one(l10, l10.ticker == l10.ticker, 'median_tick_bps'):.2f}"
            rows[t] = s
        tables[per] = pd.DataFrame(rows)
    return tables


def main():
    ps.setup()
    X = Tk("SOXX")
    rows = []
    for t in MAIN:
        T = X if t == "SOXX" else Tk(t)
        dm = pd.read_parquet(PANEL / f"{t}_dm.parquet").reindex(T.dates)
        rows += quarter_metrics(t, T, dm, X)
        print("done", t, flush=True)
    Q = pd.DataFrame(rows)
    save_csv(Q, "stability_quarterly_metrics.csv", index=False)
    P = persistence(Q)
    save_csv(P, "stability_persistence_summary.csv", index=False)
    tk = []
    for t, g in Q.groupby("ticker"):
        tk.append({"ticker": t, "n_quarters": len(g),
                   "corr_tick_bps_vs_ac1_1m": g.median_tick_bps.corr(g.ac1_1m_deseason),
                   "corr_tick_bps_vs_VR15": g.median_tick_bps.corr(g.VR15_deseason),
                   "corr_tick_bps_vs_pct_zero_1m": g.median_tick_bps.corr(g.pct_zero_1m_returns),
                   "spearman_tick_bps_vs_ac1_1m": g.median_tick_bps.corr(g.ac1_1m_deseason, method="spearman")})
    save_csv(pd.DataFrame(tk), "stability_tick_size_vs_microstructure.csv", index=False)
    tabs = scorecard()
    for per, tb in tabs.items():
        save_csv(tb, f"scorecard_{per}.csv")

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    for ax, col, ref, title in ((axes[0, 0], "median_range_pct", None, "Median daily range (% of open)"),
                                (axes[0, 1], "VR15_deseason", 1, "Deseasonalised VR(15)"),
                                (axes[1, 0], "ac1_1m_deseason", 0, "Deseasonalised 1-min autocorrelation"),
                                (axes[1, 1], "median_tick_bps", None, "1-cent tick as bps of unadjusted price (median)")):
        for t in ["SOXL", "SOXS", "SOXX", "QQQ"]:
            g = Q[Q.ticker == t]
            ax.plot(g.quarter, g[col], marker="o", ms=4, color=ps.COL[t], label=t)
        if ref is not None:
            ax.axhline(ref, color=ps.THEORY, lw=1)
        ax.axvline("2024Q4", color=ps.AXIS, lw=1)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=70)
        ax.legend(fontsize=7)
    ps.save(fig, OUT / "stability_quarterly.png")


if __name__ == "__main__":
    main()
