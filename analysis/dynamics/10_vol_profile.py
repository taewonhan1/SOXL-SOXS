"""Volatility profile: daily RTH range, true range / ATR, realized vol by sampling horizon,
intraday U-shape, gap sizes, short-sale-restriction (SSR) trigger days.

Outputs (analysis/dynamics/output/):
  vol_daily_range.csv        per ticker x window: RTH high-low range % distribution, ATR14 %, days >5%/>10%
  vol_rv_by_horizon.csv      per ticker x window: std of 1/5/15/30-min returns (bps), annualised RV
  vol_tod_1min.csv           per ticker: std & mean |r| of 1-min returns per 5-min time-of-day bucket (primary window)
  vol_ssr_days.csv           SOXL/SOXS days where low <= 0.9 x prior close (Rule 201 SSR trigger proxy)
  fig_vol_ushape.png, fig_vol_soxl_range_hist.png
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import (COLORS, INK2, OOS_WIN, IS_WIN, PRIMARY, ROBUST, TICKERS, OUT, build_panel,
                    in_window, save_csv, setup_mpl)

WINDOWS = {"primary": PRIMARY, "IS": IS_WIN, "OOS": OOS_WIN, "robust": ROBUST}


def daily_stats(P):
    o = P["p"][:, 0]
    H = P["h"].max(axis=1)
    L = P["l"].min(axis=1)
    pc = P["prevclose"]
    rng = (H - L) / o
    tr = (np.maximum(H, pc) - np.minimum(L, pc)) / pc
    gap = o / pc - 1
    return rng, tr, gap, H, L, pc


def main():
    plt = setup_mpl()
    rows, rvrows, todrows, ssr = [], [], [], []
    for t in TICKERS:
        P = build_panel(t)
        rng, tr, gap, H, L, pc = daily_stats(P)
        atr14 = pd.Series(tr).rolling(14).mean().to_numpy()
        p = P["p"]
        r1 = p[:, 1:] / p[:, :-1] - 1  # 390 one-minute returns incl. the first minute from the opening print
        for wn, win in WINDOWS.items():
            m = in_window(P["dates"], win)
            n = int(m.sum())
            x = rng[m]
            rows.append(dict(ticker=t, window=wn, start=str(P["dates"][m][0]), end=str(P["dates"][m][-1]), n_days=n,
                             range_mean_pct=100 * x.mean(), range_median_pct=100 * np.median(x),
                             range_p10_pct=100 * np.percentile(x, 10), range_p90_pct=100 * np.percentile(x, 90),
                             range_max_pct=100 * x.max(),
                             days_range_gt5=int((x > 0.05).sum()), share_gt5=(x > 0.05).mean(),
                             days_range_gt10=int((x > 0.10).sum()), share_gt10=(x > 0.10).mean(),
                             tr_mean_pct=100 * tr[m].mean(), atr14_mean_pct=100 * np.nanmean(atr14[m]),
                             abs_gap_median_pct=100 * np.median(np.abs(gap[m])),
                             abs_gap_p90_pct=100 * np.percentile(np.abs(gap[m]), 90),
                             close_to_close_vol_ann_pct=100 * np.std(P["close_off"][m] / pc[m] - 1, ddof=1) * np.sqrt(252)))
            for h in (1, 5, 15, 30):
                idx = np.arange(0, 391, h)
                rh = p[m][:, idx[1:]] / p[m][:, idx[:-1]] - 1
                daily_rv = (rh ** 2).sum(axis=1)
                rvrows.append(dict(ticker=t, window=wn, horizon_min=h, n_days=n, n_returns=rh.size,
                                   std_bps=1e4 * rh.std(ddof=1), mean_abs_bps=1e4 * np.abs(rh).mean(),
                                   median_abs_bps=1e4 * np.median(np.abs(rh)),
                                   rth_rv_ann_pct=100 * np.sqrt(252 * daily_rv.mean())))
        # time of day (primary window), 5-min buckets of 1-min returns
        m = in_window(P["dates"], PRIMARY)
        rr = r1[m]
        for b in range(0, 390, 5):
            x = rr[:, b:b + 5].ravel()
            todrows.append(dict(ticker=t, bucket_start_min=b,
                                time=f"{(570 + b) // 60:02d}:{(570 + b) % 60:02d}",
                                std_bps=1e4 * x.std(ddof=1), mean_abs_bps=1e4 * np.abs(x).mean(),
                                median_abs_bps=1e4 * np.median(np.abs(x))))
        if t in ("SOXL", "SOXS"):
            for wn in ("primary", "robust"):
                mm = in_window(P["dates"], WINDOWS[wn])
                trig = (L[mm] <= 0.9 * pc[mm])
                ssr.append(dict(ticker=t, window=wn, n_days=int(mm.sum()), ssr_trigger_days=int(trig.sum()),
                                share=trig.mean(), dates=";".join(str(d) for d in P["dates"][mm][trig])))
    d1 = pd.DataFrame(rows)
    save_csv(d1, "vol_daily_range.csv")
    d2 = pd.DataFrame(rvrows)
    save_csv(d2, "vol_rv_by_horizon.csv")
    d3 = pd.DataFrame(todrows)
    save_csv(d3, "vol_tod_1min.csv")
    save_csv(pd.DataFrame(ssr), "vol_ssr_days.csv")

    # --- U-shape figure: two panels (absolute bps, and normalised to own daily mean)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for t in TICKERS:
        x = d3[d3.ticker == t]
        tt = x.bucket_start_min.to_numpy() / 60 + 9.5
        axes[0].plot(tt, x.std_bps, color=COLORS[t], label=t)
        axes[1].plot(tt, x.std_bps / x.std_bps.mean(), color=COLORS[t], label=t)
    axes[0].set_yscale("log")
    axes[0].set_title("Std of 1-min returns by time of day (bps, log scale)")
    axes[1].set_title("Same, normalised to each ticker's all-day mean")
    for ax in axes:
        ax.set_xticks([9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5])
        ax.set_xticklabels(["09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30"])
        ax.set_xlabel("ET, 5-min buckets, 2024-10-01 to 2026-09-25")
    axes[1].legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_vol_ushape.png")
    plt.close(fig)

    # --- SOXL daily range histogram (primary vs robust)
    P = build_panel("SOXL")
    rng, *_ = daily_stats(P)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    bins = np.arange(0, 0.40 + 0.005, 0.005) * 100
    for wn, col in (("robust", COLORS["SOXS"]), ("primary", COLORS["SOXL"])):
        m = in_window(P["dates"], WINDOWS[wn])
        ax.hist(100 * rng[m], bins=bins, histtype="step", linewidth=1.8, color=col,
                label=f"{wn} ({WINDOWS[wn][0]} to {WINDOWS[wn][1]}, n={m.sum()})")
    for v in (5, 10):
        ax.axvline(v, color=INK2, linewidth=0.8, linestyle="--")
    ax.set_xlabel("SOXL RTH high-low range, % of open")
    ax.set_ylabel("days")
    ax.set_title("SOXL daily RTH range distribution")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_vol_soxl_range_hist.png")
    plt.close(fig)

    pd.set_option("display.width", 250)
    print(d1[d1.window.isin(["primary", "robust"])].round(3).to_string())
    print(d2[d2.window == "primary"].round(2).to_string())
    print(pd.DataFrame(ssr).drop(columns="dates"))


if __name__ == "__main__":
    main()
