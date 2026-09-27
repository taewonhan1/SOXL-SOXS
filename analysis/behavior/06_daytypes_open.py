"""Day types, high/low timing, overnight gaps & gap fills, opening-range behaviour, first hour.
Full days only; official daily O/H/L/C (split-adjusted) and RTH minute bars.
Random-walk benchmark = sign-randomised minute path (keeps each day's |1-min returns| and their
time-of-day order, randomises direction; 20 draws/day)."""
from __future__ import annotations

import numpy as np
import pandas as pd

import plotstyle as ps
from common import MAIN, OUT, PANEL, PERIODS, Tk, q, save_csv

RNG = np.random.default_rng(11)
NSIM = 20


def path_stats(P0, path):
    """P0: (n,) open; path: (n, 390) closes. Returns body, clv, argmax, argmin using the close path."""
    full = np.concatenate([P0[:, None], path], axis=1)
    H, L = full.max(1), full.min(1)
    C = path[:, -1]
    rng = H - L
    body = np.abs(C - P0) / rng
    clv = (C - L) / rng
    return body, clv, full.argmax(1), full.argmin(1)


def sim_paths(r):
    """Sign-randomised log-price paths starting at 0; r: (n, 390) 1-min log returns (col 0 incl. open print)."""
    out = []
    for _ in range(NSIM):
        s = RNG.choice([-1.0, 1.0], size=r.shape)
        out.append(np.cumsum(np.abs(r) * s, axis=1))
    return out


def daytypes(t, T, dm, per, rows, tod_rows):
    sel = T.sel(per)
    D = dm[sel]
    body = (D.C - D.O).abs() / (D.H - D.L)
    clv = (D.C - D.L) / (D.H - D.L)
    up = D.C > D.O
    row = {"ticker": t, "period": per, "n_days": int(sel.sum()),
           "pct_close_top15_or_bottom15": 100 * ((clv >= 0.85) | (clv <= 0.15)).mean(),
           "pct_close_top15": 100 * (clv >= 0.85).mean(), "pct_close_bottom15": 100 * (clv <= 0.15).mean(),
           "pct_body_ge_0.7": 100 * (body >= 0.7).mean(), "pct_body_le_0.3": 100 * (body <= 0.3).mean(),
           "pct_trend_day(body>=0.7 & close in extreme 15% in body direction)":
               100 * ((body >= 0.7) & (((clv >= 0.85) & up) | ((clv <= 0.15) & ~up))).mean(),
           "median_body": body.median(), "mean_body": body.mean()}
    # close-path versions + random benchmark
    r = T.r1[sel]
    lp = np.cumsum(r, axis=1)
    b_obs, c_obs, amax_obs, amin_obs = path_stats(np.zeros(len(lp)), lp)
    sims = sim_paths(r)
    bs, cs, amaxs, amins = [], [], [], []
    for sp in sims:
        b, c, amx, amn = path_stats(np.zeros(len(sp)), sp)
        bs.append(b), cs.append(c), amaxs.append(amx), amins.append(amn)
    bs, cs = np.concatenate(bs), np.concatenate(cs)
    row.update({"closepath_pct_body_ge_0.7": 100 * (b_obs >= 0.7).mean(),
                "RANDOM_pct_body_ge_0.7": 100 * (bs >= 0.7).mean(),
                "closepath_pct_body_le_0.3": 100 * (b_obs <= 0.3).mean(),
                "RANDOM_pct_body_le_0.3": 100 * (bs <= 0.3).mean(),
                "closepath_pct_close_extreme15": 100 * ((c_obs >= 0.85) | (c_obs <= 0.15)).mean(),
                "RANDOM_pct_close_extreme15": 100 * ((cs >= 0.85) | (cs <= 0.15)).mean(),
                "closepath_mean_body": b_obs.mean(), "RANDOM_mean_body": bs.mean()})
    # HOD / LOD timing from minute bars (first occurrence)
    Hm, Lm = T.H[sel], T.L[sel]
    k_hi = np.nanargmax(Hm, axis=1)
    k_lo = np.nanargmin(Lm, axis=1)
    amaxs, amins = np.concatenate(amaxs), np.concatenate(amins)
    # close-path index: 0 = open print, j>=1 = close of minute j-1  -> convert to minute index
    ks_hi, ks_lo = np.maximum(amaxs - 1, 0), np.maximum(amins - 1, 0)
    ko_hi, ko_lo = np.maximum(amax_obs - 1, 0), np.maximum(amin_obs - 1, 0)
    for lab, lo, hi in (("first30", 0, 30), ("first60", 0, 60), ("last30", 360, 390), ("last60", 330, 390)):
        f = lambda a: (a >= lo) & (a < hi)  # noqa: E731
        row[f"pct_HOD_{lab}"] = 100 * f(k_hi).mean()
        row[f"pct_LOD_{lab}"] = 100 * f(k_lo).mean()
        row[f"pct_HOD_or_LOD_{lab}"] = 100 * (f(k_hi) | f(k_lo)).mean()
        row[f"closepath_pct_HOD_or_LOD_{lab}"] = 100 * (f(ko_hi) | f(ko_lo)).mean()
        row[f"RANDOM_pct_HOD_or_LOD_{lab}"] = 100 * (f(ks_hi) | f(ks_lo)).mean()
    row["pct_both_HOD_and_LOD_first60"] = 100 * ((k_hi < 60) & (k_lo < 60)).mean()
    rows.append(row)
    for b in range(26):
        lo, hi = 15 * b, 15 * b + 15
        tod_rows.append({"ticker": t, "period": per, "bucket": f"{(570 + lo) // 60:02d}:{(570 + lo) % 60:02d}",
                         "pct_HOD": 100 * ((k_hi >= lo) & (k_hi < hi)).mean(),
                         "pct_LOD": 100 * ((k_lo >= lo) & (k_lo < hi)).mean(),
                         "RANDOM_pct_HOD": 100 * ((ks_hi >= lo) & (ks_hi < hi)).mean(),
                         "RANDOM_pct_LOD": 100 * ((ks_lo >= lo) & (ks_lo < hi)).mean()})


def gaps(t, T, dm, per, rows, fill_rows):
    sel = T.sel(per)
    D = dm[sel].copy()
    g = D.gap_pct
    rows.append({"ticker": t, "period": per, "n_days": len(D), "gap_p10": q(g, 10), "gap_median": q(g, 50),
                 "gap_p90": q(g, 90), "absgap_median": q(g.abs(), 50), "absgap_p90": q(g.abs(), 90),
                 **{f"pct_absgap_gt_{x}": 100 * (g.abs() > x).mean() for x in (0.5, 1, 2, 3, 5)},
                 "gap_up_share_pct": 100 * (g > 0).mean(),
                 "median_absgap_in_ATRprev": (g.abs() / D.atr14_prev).median()})
    Lm, Hm = T.L[sel], T.H[sel]
    pc = D.prevC_adj.to_numpy()
    up = (g > 0).to_numpy()
    touch = np.where(up[:, None], Lm <= pc[:, None], Hm >= pc[:, None])
    filled = touch.any(1)
    kfill = np.where(filled, touch.argmax(1), -1)
    D["filled"], D["kfill"] = filled, kfill
    D["gap_atr"] = g.abs() / D.atr14_prev
    for lab, col, edges in (("pct", g.abs(), [0.25, 0.5, 1, 2, 3, 5, 1e9]),
                            ("ATR", D.gap_atr, [0.03, 0.1, 0.25, 0.5, 1, 1e9])):
        for lo, hi in zip(edges[:-1], edges[1:]):
            for direction in ("all", "up", "down"):
                m = (col >= lo) & (col < hi)
                if direction == "up":
                    m &= g > 0
                elif direction == "down":
                    m &= g < 0
                x = D[m]
                if len(x) < 5:
                    continue
                fill_rows.append({"ticker": t, "period": per, "bin_unit": lab, "bin_lo": lo, "bin_hi": hi,
                                  "direction": direction, "n": len(x), "fill_rate_pct": 100 * x.filled.mean(),
                                  "fill_within_30min_pct": 100 * ((x.kfill >= 0) & (x.kfill < 30)).mean(),
                                  "median_minutes_to_fill_if_filled": x.kfill[x.filled].median()})


def opening_range(t, T, dm, per, rows):
    sel = T.sel(per)
    D = dm[sel]
    Hm, Lm, Cm, Vm = T.H[sel], T.L[sel], T.C[sel], T.V[sel]
    day_rng = (D.H - D.L).to_numpy()
    C_off = D.C.to_numpy()
    for N in (5, 15, 30, 60):
        orh, orl = Hm[:, :N].max(1), Lm[:, :N].min(1)
        ors = orh - orl
        post_h, post_l = Hm[:, N:], Lm[:, N:]
        bu = post_h > orh[:, None]
        bd = post_l < orl[:, None]
        ku = np.where(bu.any(1), bu.argmax(1), 10 ** 6)
        kd = np.where(bd.any(1), bd.argmax(1), 10 ** 6)
        anyb = (ku < 10 ** 6) | (kd < 10 ** 6)
        upfirst = ku < kd
        dnfirst = kd < ku
        same = (ku == kd) & anyb
        both = (ku < 10 ** 6) & (kd < 10 ** 6)
        mfe, mae, mfe60, mae60, close_beyond = [], [], [], [], []
        for i in np.where(upfirst | dnfirst)[0]:
            if upfirst[i]:
                k = ku[i]
                lvl = orh[i]
                fh, fl = post_h[i, k:], post_l[i, k:]
                mfe.append(fh.max() / lvl - 1), mae.append(1 - fl.min() / lvl)
                mfe60.append(fh[:60].max() / lvl - 1), mae60.append(1 - fl[:60].min() / lvl)
                close_beyond.append(C_off[i] > lvl)
            else:
                k = kd[i]
                lvl = orl[i]
                fh, fl = post_h[i, k:], post_l[i, k:]
                mfe.append(1 - fl.min() / lvl), mae.append(fh.max() / lvl - 1)
                mfe60.append(1 - fl[:60].min() / lvl), mae60.append(fh[:60].max() / lvl - 1)
                close_beyond.append(C_off[i] < lvl)
        mfe, mae, mfe60, mae60 = map(np.array, (mfe, mae, mfe60, mae60))
        orsz = (ors / D.O.to_numpy())[upfirst | dnfirst]
        rows.append({"ticker": t, "period": per, "OR_minutes": N, "n_days": int(sel.sum()),
                     "median_OR_size_pct": 100 * np.median(ors / D.O.to_numpy()),
                     "median_OR_share_of_day_range": np.median(ors / day_rng),
                     "pct_days_OR_broken": 100 * anyb.mean(), "pct_up_break_first": 100 * upfirst.mean(),
                     "pct_down_break_first": 100 * dnfirst.mean(), "pct_same_minute_both": 100 * same.mean(),
                     "pct_both_sides_broken": 100 * both.mean(),
                     "pct_close_beyond_first_break_level": 100 * np.mean(close_beyond),
                     "median_MFE_to_close_pct": 100 * np.median(mfe), "median_MAE_to_close_pct": 100 * np.median(mae),
                     "median_MFE_to_close_OR_units": np.median(mfe / orsz), "median_MAE_to_close_OR_units": np.median(mae / orsz),
                     "median_MFE_60m_pct": 100 * np.median(mfe60), "median_MAE_60m_pct": 100 * np.median(mae60),
                     "pct_MFE60_gt_MAE60": 100 * np.mean(mfe60 > mae60),
                     "median_minutes_to_first_break": float(np.median(np.minimum(ku, kd)[anyb]) + N)})
    # first hour share
    fh_rng = Hm[:, :60].max(1) - Lm[:, :60].min(1)
    vol_share = np.nansum(Vm[:, :60], 1) / np.nansum(Vm, 1)
    rows.append({"ticker": t, "period": per, "OR_minutes": "first_hour_summary", "n_days": int(sel.sum()),
                 "median_first_hour_share_of_day_range": np.median(fh_rng / day_rng),
                 "mean_first_hour_share_of_day_range": np.mean(fh_rng / day_rng),
                 "median_first_hour_share_of_RTH_minute_volume": np.median(vol_share),
                 "mean_first_hour_share_of_RTH_minute_volume": np.mean(vol_share),
                 "median_first30_share_of_RTH_minute_volume": np.median(np.nansum(Vm[:, :30], 1) / np.nansum(Vm, 1))})


def main():
    ps.setup()
    DT, TOD, GP, GF, ORr = [], [], [], [], []
    for t in MAIN:
        T = Tk(t)
        dm = pd.read_parquet(PANEL / f"{t}_dm.parquet").reindex(T.dates)
        for per in PERIODS:
            daytypes(t, T, dm, per, DT, TOD)
            gaps(t, T, dm, per, GP, GF)
            opening_range(t, T, dm, per, ORr)
        print("done", t, flush=True)
    save_csv(pd.DataFrame(DT), "day_types.csv", index=False)
    tod = pd.DataFrame(TOD)
    save_csv(tod, "day_hod_lod_timing_15min.csv", index=False)
    save_csv(pd.DataFrame(GP), "open_gap_distribution.csv", index=False)
    save_csv(pd.DataFrame(GF), "open_gap_fill_rates.csv", index=False)
    save_csv(pd.DataFrame(ORr), "open_opening_range.csv", index=False)

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, t in zip(axes, ["SOXL", "SOXS"]):
        g = tod[(tod.ticker == t) & (tod.period == "primary")]
        x = np.arange(len(g))
        ax.bar(x - 0.2, g.pct_HOD, width=0.38, color=ps.COL["SOXL"], label="high of day")
        ax.bar(x + 0.2, g.pct_LOD, width=0.38, color=ps.COL["SOXS"], label="low of day")
        ax.plot(x, (g.RANDOM_pct_HOD + g.RANDOM_pct_LOD) / 2, color=ps.THEORY, lw=1.5, label="random-sign benchmark")
        ax.set_xticks(x[::2])
        ax.set_xticklabels(g.bucket.iloc[::2], rotation=60)
        ax.set_title(f"{t}: when the day's high / low is set (15-min buckets)")
        ax.set_xlabel("bucket start (ET), 2024-10-01..2026-09-25, full days")
        ax.legend()
    axes[0].set_ylabel("% of days")
    ps.save(fig, OUT / "hod_lod_timing_primary.png")


if __name__ == "__main__":
    main()
