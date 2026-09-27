"""Volatility and range: daily range / ATR distributions, realized vol by horizon, intraday
U-shape, volatility clustering, weekday effects, catalyst days (detected, see 04_events.py).
Full (non-half) days only unless stated. Returns are log returns on split-adjusted prices."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

import plotstyle as ps
from common import MAIN, OUT, PANEL, PERIODS, Tk, block_sum, daily_metrics, q, save_csv

HORIZONS = [1, 2, 5, 15, 30, 60]


def main():
    ps.setup()
    rng_rows, rv_rows, u5, u30, acf_rows, wd_rows, cat_rows = [], [], [], [], [], [], []
    ev = pd.read_csv(OUT / "events_all_detected.csv", dtype={"date": str})
    for t in MAIN:
        T = Tk(t)
        D = daily_metrics(T)
        D.to_parquet(PANEL / f"{t}_dm.parquet")
        for per in PERIODS:
            m = (D.period == per) & D.full
            d = D[m]
            row = {"ticker": t, "period": per, "n_days": int(m.sum()), "first": d.index.min(), "last": d.index.max()}
            for col in ["range_pct", "atr14_pct", "tr_pct"]:
                row[f"{col}_p10"] = q(d[col], 10)
                row[f"{col}_median"] = q(d[col], 50)
                row[f"{col}_p90"] = q(d[col], 90)
                row[f"{col}_mean"] = d[col].mean()
            for th in (1, 2, 3, 5, 8, 10):
                row[f"share_range_gt_{th}pct"] = 100 * (d.range_pct > th).mean()
            row["cc_vol_ann_pct"] = d.cc_pct.std() * np.sqrt(252)
            row["median_unadj_close"] = d.C_unadj.median()
            rng_rows.append(row)

            # realized vol by horizon (pooled non-overlapping intervals)
            sel = T.sel(per)
            r = T.r1[sel]
            s1 = np.sqrt(np.nanmean(r ** 2))
            for h in HORIZONS:
                R = block_sum(r, h)
                sd = np.sqrt(np.nanmean(R ** 2))
                rv_rows.append({"ticker": t, "period": per, "h_min": h, "n_intervals": int(np.isfinite(R).sum()),
                                "rms_bps": 1e4 * sd, "mean_abs_bps": 1e4 * np.nanmean(np.abs(R)),
                                "ann_vol_pct": 100 * sd * np.sqrt(252 * 390 / h),
                                "var_ratio_vs_1min": sd ** 2 / (h * s1 ** 2)})
            # daily realized variance (sum of squared 1-min returns incl. open bar) vs close-to-close
            rv_day = np.nansum(r ** 2, axis=1)
            rv_rows.append({"ticker": t, "period": per, "h_min": "RTH_open_to_close", "n_intervals": int(sel.sum()),
                            "rms_bps": 1e4 * np.sqrt(np.nanmean(np.log(d.C / d.O) ** 2)), "mean_abs_bps": np.nan,
                            "ann_vol_pct": 100 * np.sqrt(np.nanmean(np.log(d.C / d.O) ** 2) * 252),
                            "var_ratio_vs_1min": np.nanmean(np.log(d.C / d.O) ** 2) / np.nanmean(rv_day)})
            rv_rows.append({"ticker": t, "period": per, "h_min": "overnight_prevclose_to_open", "n_intervals": int(sel.sum()),
                            "rms_bps": 1e4 * np.sqrt(np.nanmean(np.log(d.O / d.prevC_adj) ** 2)), "mean_abs_bps": np.nan,
                            "ann_vol_pct": 100 * np.sqrt(np.nanmean(np.log(d.O / d.prevC_adj) ** 2) * 252),
                            "var_ratio_vs_1min": np.nan})

            # U-shape
            R5 = block_sum(r, 5)
            V = T.V[sel]
            V5 = block_sum(V, 5)
            Vtot = np.nansum(V, axis=1, keepdims=True)
            sh5 = V5 / Vtot
            for b in range(R5.shape[1]):
                u5.append({"ticker": t, "period": per, "bucket": f"{(570 + 5 * b) // 60:02d}:{(570 + 5 * b) % 60:02d}",
                           "rms_bps": 1e4 * np.sqrt(np.nanmean(R5[:, b] ** 2)),
                           "mean_abs_bps": 1e4 * np.nanmean(np.abs(R5[:, b])),
                           "vol_share_pct": 100 * np.nanmean(sh5[:, b])})
            R30 = block_sum(r, 30)
            sh30 = block_sum(V, 30) / Vtot
            for b in range(R30.shape[1]):
                u30.append({"ticker": t, "period": per, "bucket": f"{(570 + 30 * b) // 60:02d}:{(570 + 30 * b) % 60:02d}",
                            "rms_bps": 1e4 * np.sqrt(np.nanmean(R30[:, b] ** 2)),
                            "mean_abs_bps": 1e4 * np.nanmean(np.abs(R30[:, b])),
                            "vol_share_pct": 100 * np.nanmean(sh30[:, b])})

            # clustering: ACF of daily range (full days in sequence)
            x = d.range_pct.to_numpy()
            lx = np.log(x)
            ar = {"ticker": t, "period": per, "n_days": len(x)}
            for lag in (1, 2, 3, 5, 10, 20):
                ar[f"acf_range_lag{lag}"] = np.corrcoef(x[lag:], x[:-lag])[0, 1]
                ar[f"acf_logrange_lag{lag}"] = np.corrcoef(lx[lag:], lx[:-lag])[0, 1]
            sl = stats.linregress(x[:-1], x[1:])
            ar["ar1_slope"] = sl.slope
            ar["ar1_r2"] = sl.rvalue ** 2
            ar["spearman_lag1"] = stats.spearmanr(x[:-1], x[1:]).statistic
            qq = pd.qcut(x[:-1], 5, labels=False)
            nxt = x[1:]
            ar["median_next_range_after_top_quintile"] = np.median(nxt[qq == 4])
            ar["median_next_range_after_bottom_quintile"] = np.median(nxt[qq == 0])
            # abs 1-min return ACF over days of daily RV
            acf_rows.append(ar)

            # weekday (raw and regime-normalised by trailing 20-day median range)
            d2 = d.assign(wd=pd.to_datetime(d.index).day_name(), rel=d.range_pct / d.range_med20_prev)
            groups = [g.rel.dropna().to_numpy() for _, g in d2.groupby("wd")]
            kw = stats.kruskal(*groups).pvalue
            for wd, g in d2.groupby("wd"):
                wd_rows.append({"ticker": t, "period": per, "weekday": wd, "n": len(g), "median_range_pct": g.range_pct.median(),
                                "mean_range_pct": g.range_pct.mean(), "median_range_rel_trailing20": g.rel.median(),
                                "kruskal_p_rel_all_weekdays": kw})

            # catalyst days
            d3 = d.assign(rel=d.range_pct / d.range_med20_prev)
            evd = ev[ev.date.isin(d3.index)]
            base = d3[~d3.index.isin(ev.date)]
            cat_rows.append({"ticker": t, "period": per, "type": "no_detected_event", "n": len(base),
                             "median_range_pct": base.range_pct.median(), "median_rel_range": base.rel.median(),
                             "mean_rel_range": base.rel.mean(), "median_abs_oc_pct": base.oc_pct.abs().median(),
                             "median_abs_gap_pct": base.gap_pct.abs().median()})
            for typ, g in evd.groupby("type"):
                dd = d3.loc[g.date]
                mw = stats.mannwhitneyu(dd.rel.dropna(), base.rel.dropna()).pvalue if len(dd) > 3 else np.nan
                cat_rows.append({"ticker": t, "period": per, "type": typ, "n": len(dd), "median_range_pct": dd.range_pct.median(),
                                 "median_rel_range": dd.rel.median(), "mean_rel_range": dd.rel.mean(),
                                 "median_abs_oc_pct": dd.oc_pct.abs().median(),
                                 "median_abs_gap_pct": dd.gap_pct.abs().median(), "mannwhitney_p_rel_vs_base": mw})
        print("done", t, flush=True)

    save_csv(pd.DataFrame(rng_rows), "vol_daily_range_atr.csv", index=False)
    save_csv(pd.DataFrame(rv_rows), "vol_realized_by_horizon.csv", index=False)
    U5, U30 = pd.DataFrame(u5), pd.DataFrame(u30)
    save_csv(U5, "vol_ushape_5min.csv", index=False)
    save_csv(U30, "vol_ushape_30min.csv", index=False)
    save_csv(pd.DataFrame(acf_rows), "vol_clustering_range_acf.csv", index=False)
    save_csv(pd.DataFrame(wd_rows), "vol_weekday.csv", index=False)
    save_csv(pd.DataFrame(cat_rows), "vol_catalyst_days.csv", index=False)

    # chart: 30-min U-shape, primary period, volatility and volume share (two panels, one axis each)
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for t in ["SOXL", "SOXS", "SOXX", "QQQ"]:
        g = U30[(U30.ticker == t) & (U30.period == "primary")]
        rel = g.rms_bps / g.rms_bps.mean()
        axes[0].plot(g.bucket, rel, color=ps.COL[t], label=t, marker="o", ms=4)
        axes[1].plot(g.bucket, g.vol_share_pct, color=ps.COL[t], label=t, marker="o", ms=4)
    axes[0].set_title("30-min return volatility relative to the day's average bucket")
    axes[0].set_ylabel("RMS 30-min return / mean over buckets")
    axes[1].set_title("Share of RTH minute-bar volume per 30-min bucket (%)")
    axes[1].set_ylabel("% of RTH volume")
    for a in axes:
        a.tick_params(axis="x", rotation=60)
        a.legend()
        a.set_xlabel("bucket start (ET), 2024-10-01..2026-09-25, full days")
    ps.save(fig, OUT / "ushape_30min_primary.png")


if __name__ == "__main__":
    main()
