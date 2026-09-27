"""Driver linkage (RTH, full days, split-adjusted prices; SOXX is used as the proxy for the index
SOXL/SOXS reference - an assumption).

a) beta / correlation of 1-min and 5-min returns vs SOXX, SMH, NVDA, QQQ (first RTH bar excluded)
b) intraday leverage drift: beta of SOXL/SOXS 5-min returns on SOXX 5-min returns, binned by SOXX's
   return since the prior official close measured at the START of the interval (no look-ahead),
   vs theory L(1+r)/(1+L*r); interaction regression y = a + b*x + c*x*r (theory b=L, c=L(1-L))
c) cross-correlation lead-lag of 1-min returns (lags -5..+5 min)
d) 1-second lead-lag: Hayashi-Yoshida cross-covariance on 1-second bar closes (asynchronous,
   no forward-fill staleness bias), lags -30..+30 s, 10 sessions 2026-09-14..2026-09-25, 09:35-15:55
e) SOXL vs SOXS mirror: correlation, ratio of moves, divergence of returns since prior close."""
from __future__ import annotations

import numpy as np
import pandas as pd

import plotstyle as ps
from common import DATA, OUT, PANEL, PERIODS, TZ, Tk, block_sum, save_csv

PAIRS_BETA = [("SOXL", "SOXX"), ("SOXL", "SMH"), ("SOXL", "NVDA"), ("SOXL", "QQQ"),
              ("SOXS", "SOXX"), ("SOXS", "SMH"), ("SOXS", "NVDA"), ("SOXS", "QQQ"),
              ("SOXL", "SOXS"), ("SOXX", "NVDA"), ("SMH", "NVDA"), ("TQQQ", "QQQ"), ("SQQQ", "QQQ"), ("SOXX", "QQQ"),
              ("SMH", "SOXX"), ("NVDA", "SOXX"), ("QQQ", "SOXX"), ("TQQQ", "SOXX"), ("SQQQ", "SOXX")]
LEADLAG_1M = [("NVDA", "SOXL"), ("SOXX", "SOXL"), ("SMH", "SOXL"), ("QQQ", "SOXL"), ("NVDA", "SOXS"),
              ("SOXX", "SOXS"), ("SOXL", "SOXS"), ("NVDA", "SOXX"), ("SOXX", "SMH"), ("QQQ", "TQQQ")]
SEC_PAIRS = [("NVDA", "SOXL"), ("SOXX", "SOXL"), ("SMH", "SOXL"), ("QQQ", "SOXL"), ("NVDA", "SOXS"),
             ("SOXX", "SOXS"), ("SOXL", "SOXS"), ("NVDA", "SOXX"), ("NVDA", "SMH"), ("SMH", "SOXX")]
SEC_DAYS = ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18",
            "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25"]


def ols(y, x):
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    xc, yc = x - x.mean(), y - y.mean()
    b = (xc * yc).sum() / (xc ** 2).sum()
    rho = (xc * yc).sum() / np.sqrt((xc ** 2).sum() * (yc ** 2).sum())
    return b, rho, len(x)


def betas(TT, rows):
    for per in PERIODS:
        for y, x in PAIRS_BETA:
            sel = TT[y].sel(per) & TT[x].sel(per)
            ry, rx = TT[y].r1[sel][:, 1:], TT[x].r1[sel][:, 1:]
            b1, c1, n1 = ols(ry.ravel(), rx.ravel())
            b5, c5, n5 = ols(block_sum(ry, 5).ravel(), block_sum(rx, 5).ravel())
            b30, c30, n30 = ols(block_sum(ry, 30).ravel(), block_sum(rx, 30).ravel())
            # daily close-to-close (official, dividend-adjusted)
            Dy, Dx = TT[y].D, TT[x].D
            dsel = TT[y].dates[sel]
            cy = np.log(Dy.C / Dy.prevC_adj).reindex(dsel).to_numpy()
            cx = np.log(Dx.C / Dx.prevC_adj).reindex(dsel).to_numpy()
            bd, cd, nd = ols(cy, cx)
            rows.append({"y": y, "x": x, "period": per, "beta_1m": b1, "corr_1m": c1, "n_1m": n1,
                         "beta_5m": b5, "corr_5m": c5, "beta_30m": b30, "corr_30m": c30,
                         "beta_daily_cc": bd, "corr_daily_cc": cd, "n_days": nd})


def leverage_drift(TT, rows, rows_reg, rows_track):
    X = TT["SOXX"]
    for per in PERIODS:
        for y, L in (("SOXL", 3), ("SOXS", -3)):
            Y = TT[y]
            sel = Y.sel(per) & X.sel(per)
            pcx = X.D.prevC_adj.reindex(X.dates).to_numpy()[sel]
            Cx = X.C[sel]
            # SOXX cumulative simple return since prior close at the START of each 5-min block (blocks from minute 1)
            starts = np.arange(0, 385, 5)          # block covers minutes s+1..s+5; start price = close of minute s
            Rstart = Cx[:, starts] / pcx[:, None] - 1
            rx = block_sum(X.r1[sel][:, 1:], 5)
            ry = block_sum(Y.r1[sel][:, 1:], 5)
            # use simple returns for the theory comparison
            sx, sy = np.expm1(rx), np.expm1(ry)
            R = Rstart[:, :sx.shape[1]]
            edges = [-1, -0.04, -0.02, -0.01, -0.005, 0.005, 0.01, 0.02, 0.04, 1]
            for lo, hi in zip(edges[:-1], edges[1:]):
                m = (R >= lo) & (R < hi) & np.isfinite(sx) & np.isfinite(sy)
                if m.sum() < 200:
                    continue
                b, c, n = ols(sy[m], sx[m])
                rmid = np.median(R[m])
                rows.append({"ticker": y, "period": per, "soxx_ret_since_prev_close_bin": f"[{lo:+.3f},{hi:+.3f})",
                             "median_R": rmid, "n_5m_intervals": n, "beta_obs": b, "corr": c,
                             "beta_theory_L(1+R)/(1+LR)": L * (1 + rmid) / (1 + L * rmid)})
            ok = np.isfinite(sx) & np.isfinite(sy) & np.isfinite(R)
            x1, yv, rr = sx[ok], sy[ok], R[ok]
            Xm = np.column_stack([np.ones_like(x1), x1, x1 * rr])
            coef, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
            e = yv - Xm @ coef
            XtX_inv = np.linalg.inv(Xm.T @ Xm)
            S = (Xm * e[:, None]).T @ (Xm * e[:, None])
            se = np.sqrt(np.diag(XtX_inv @ S @ XtX_inv))
            rows_reg.append({"ticker": y, "period": per, "b_on_x": coef[1], "se_b": se[1], "c_on_x_times_R": coef[2],
                             "se_c": se[2], "theory_b": L, "theory_c_first_order": L * (1 - L), "n": len(yv)})
            # cumulative since-close tracking at 15:30 (minute 359): R_y vs L * R_x
            pcy = Y.D.prevC_adj.reindex(Y.dates).to_numpy()[sel]
            Ry = Y.C[sel][:, 359] / pcy - 1
            Rx = Cx[:, 359] / pcx - 1
            b, c, n = ols(Ry, Rx)
            dev = 1e4 * (Ry - L * Rx)
            rows_track.append({"ticker": y, "period": per, "slope_R_since_close_1530_vs_SOXX": b, "corr": c, "n_days": n,
                               "median_abs_dev_from_L*R_bps": np.nanmedian(np.abs(dev)),
                               "p90_abs_dev_from_L*R_bps": np.nanpercentile(np.abs(dev), 90)})


def leadlag_1m(TT, rows):
    for per in PERIODS:
        for x, y in LEADLAG_1M:
            sel = TT[y].sel(per) & TT[x].sel(per)
            rx, ry = TT[x].r1[sel][:, 1:], TT[y].r1[sel][:, 1:]
            for lag in range(-5, 6):
                if lag > 0:
                    a, b = rx[:, :-lag], ry[:, lag:]
                elif lag < 0:
                    a, b = rx[:, -lag:], ry[:, :lag]
                else:
                    a, b = rx, ry
                _, c, n = ols(b.ravel(), a.ravel())
                rows.append({"x": x, "y": y, "period": per, "lag_min (+ = x leads y)": lag, "corr": c, "n": n})


# ---------------------------------------------------------------- 1-second Hayashi-Yoshida
def load_sec(t, day):
    df = pd.read_parquet(DATA / "second" / t / f"{day}.parquet")
    ts = pd.to_datetime(df.t, unit="ms", utc=True).dt.tz_convert(TZ)
    sec = (ts.dt.hour * 3600 + ts.dt.minute * 60 + ts.dt.second).to_numpy()
    m = (sec >= 9 * 3600 + 35 * 60) & (sec < 15 * 3600 + 55 * 60)
    return sec[m].astype(np.int64), np.log(df.c.to_numpy()[m])


def hy_lag(tx, lx, ty, ly, lag):
    dX = np.diff(lx)
    a, b = tx[:-1], tx[1:]
    s = ty - lag
    j1 = np.searchsorted(s, a, side="right")
    j2 = np.searchsorted(s, b, side="left")
    j1c = np.maximum(j1, 1)
    j2c = np.minimum(j2, len(s) - 1)
    ok = j1c <= j2c
    sumY = np.zeros(len(dX))
    sumY[ok] = ly[j2c[ok]] - ly[j1c[ok] - 1]
    return np.sum(dX * sumY)


def prevtick_grid(t_, l_, grid):
    idx = np.searchsorted(t_, grid, side="right") - 1
    out = np.where(idx >= 0, l_[np.maximum(idx, 0)], np.nan)
    return out


def leadlag_1s(rows, rows_sum, cov_rows):
    lags = np.arange(-30, 31)
    for day in SEC_DAYS:
        cache = {t: load_sec(t, day) for t in {p for pr in SEC_PAIRS for p in pr}}
        for t, (tt, ll) in cache.items():
            cov_rows.append({"day": day, "ticker": t, "seconds_with_trades_09:35-15:55": len(tt),
                             "share_of_seconds": len(tt) / (6 * 3600 + 20 * 60)})
        grid = np.arange(9 * 3600 + 35 * 60, 15 * 3600 + 55 * 60)
        for x, y in SEC_PAIRS:
            tx, lx = cache[x]
            ty, ly = cache[y]
            rvx, rvy = np.sum(np.diff(lx) ** 2), np.sum(np.diff(ly) ** 2)
            gx, gy = np.diff(prevtick_grid(tx, lx, grid)), np.diff(prevtick_grid(ty, ly, grid))
            for lag in lags:
                hy = hy_lag(tx, lx, ty, ly, lag) / np.sqrt(rvx * rvy)
                if lag > 0:
                    a, b = gx[:-lag], gy[lag:]
                elif lag < 0:
                    a, b = gx[-lag:], gy[:lag]
                else:
                    a, b = gx, gy
                ok = np.isfinite(a) & np.isfinite(b)
                cc = np.corrcoef(a[ok], b[ok])[0, 1]
                rows.append({"day": day, "x": x, "y": y, "lag_s (+ = x leads y)": int(lag), "hy_corr": hy,
                             "prevtick_grid_corr": cc})
    df = pd.DataFrame(rows)
    for (x, y), g in df.groupby(["x", "y"]):
        m = g.groupby("lag_s (+ = x leads y)")[["hy_corr", "prevtick_grid_corr"]].mean()
        pos, neg = m.loc[1:30], m.loc[-30:-1]
        g = g.assign(abs_hy=g.hy_corr.abs())
        day_peaks = g.loc[g.groupby("day").abs_hy.idxmax(), "lag_s (+ = x leads y)"]
        rows_sum.append({"x": x, "y": y, "n_days": g.day.nunique(),
                         "HY_peak_lag_s_(max |corr|)": int(m.hy_corr.abs().idxmax()),
                         "HY_peak_corr": m.hy_corr.loc[m.hy_corr.abs().idxmax()],
                         "HY_corr_lag0": m.hy_corr.loc[0], "HY_corr_lag+1": m.hy_corr.loc[1], "HY_corr_lag-1": m.hy_corr.loc[-1],
                         "HY_LLR_(sum rho^2 +lags / -lags)": (pos.hy_corr ** 2).sum() / (neg.hy_corr ** 2).sum(),
                         "HY_days_peak_lag>0": int((day_peaks > 0).sum()), "HY_days_peak_lag<0": int((day_peaks < 0).sum()),
                         "HY_days_peak_lag=0": int((day_peaks == 0).sum()), "HY_median_daily_peak_lag_s": float(day_peaks.median()),
                         "grid_peak_lag_s_(max |corr|)": int(m.prevtick_grid_corr.abs().idxmax()),
                         "grid_LLR": (pos.prevtick_grid_corr ** 2).sum() / (neg.prevtick_grid_corr ** 2).sum()})
    return df


def mirror(TT, rows, ep_rows):
    L, S = TT["SOXL"], TT["SOXS"]
    for per in PERIODS:
        sel = L.sel(per) & S.sel(per)
        rl, rs = L.r1[sel][:, 1:], S.r1[sel][:, 1:]
        b1, c1, _ = ols(rs.ravel(), rl.ravel())
        b5, c5, _ = ols(block_sum(rs, 5).ravel(), block_sum(rl, 5).ravel())
        nz = (rl != 0) & (rs != 0)
        same = np.mean(np.sign(rl[nz]) == np.sign(rs[nz]))
        ratio = np.median(np.abs(rs[nz]) / np.abs(rl[nz]))
        pcl = L.D.prevC_adj.reindex(L.dates).to_numpy()[sel]
        pcs = S.D.prevC_adj.reindex(S.dates).to_numpy()[sel]
        Rl = L.C[sel] / pcl[:, None] - 1
        Rs = S.C[sel] / pcs[:, None] - 1
        d = 1e4 * (Rl + Rs)  # theory: ~0 (both reset at the prior close; ignores fees/financing)
        dd = d[:, 5:]
        di = d[:, 5:] - d[:, [4]]  # change in divergence since 09:35 (removes prior-close dislocations)
        # daily close-to-close
        cl = (L.D.C / L.D.prevC_adj - 1).reindex(L.dates[sel]).to_numpy()
        cs = (S.D.C / S.D.prevC_adj - 1).reindex(S.dates[sel]).to_numpy()
        rows.append({"period": per, "n_days": int(sel.sum()), "corr_1m": c1, "slope_SOXS_on_SOXL_1m": b1,
                     "corr_5m": c5, "slope_SOXS_on_SOXL_5m": b5, "pct_1m_same_direction_(both_nonzero)": 100 * same,
                     "median_abs_ratio_|rSOXS|/|rSOXL|_1m": ratio,
                     "median_abs_divergence_bps_(R_L+R_S since prior close)": np.nanmedian(np.abs(dd)),
                     "p90_abs_divergence_bps": np.nanpercentile(np.abs(dd), 90),
                     "p99_abs_divergence_bps": np.nanpercentile(np.abs(dd), 99),
                     "pct_minutes_|div|>25bps": 100 * np.nanmean(np.abs(dd) > 25),
                     "pct_minutes_|div|>50bps": 100 * np.nanmean(np.abs(dd) > 50),
                     "pct_minutes_|div|>100bps": 100 * np.nanmean(np.abs(dd) > 100),
                     "intraday_change_since_09:35_median_abs_bps": np.nanmedian(np.abs(di)),
                     "intraday_change_since_09:35_p90_abs_bps": np.nanpercentile(np.abs(di), 90),
                     "intraday_change_since_09:35_p99_abs_bps": np.nanpercentile(np.abs(di), 99),
                     "intraday_change_pct_minutes_|x|>50bps": 100 * np.nanmean(np.abs(di) > 50),
                     "median_abs_daily_cc_sum_bps": np.nanmedian(np.abs(1e4 * (cl + cs))),
                     "median_daily_cc_sum_bps": np.nanmedian(1e4 * (cl + cs))})
        # divergence episodes: >=3 consecutive minutes with |div| > 100 bps
        dates = L.dates[sel]
        for i in range(dd.shape[0]):
            big = np.abs(dd[i]) > 100
            if not big.any():
                continue
            k = 0
            while k < len(big):
                if big[k]:
                    j = k
                    while j < len(big) and big[j]:
                        j += 1
                    if j - k >= 3:
                        mm = 575 + k
                        ep_rows.append({"period": per, "date": dates[i], "start_ET": f"{mm // 60:02d}:{mm % 60:02d}",
                                        "minutes": j - k, "max_abs_div_bps": float(np.max(np.abs(dd[i, k:j])))})
                    k = j
                else:
                    k += 1


def main():
    ps.setup()
    TT = {t: Tk(t) for t in ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "QQQ", "TQQQ", "SQQQ"]}
    B, LD, LR, TR, LL, S1, S1s, COV, MR, EP = ([] for _ in range(10))
    betas(TT, B)
    leverage_drift(TT, LD, LR, TR)
    leadlag_1m(TT, LL)
    s1 = leadlag_1s(S1, S1s, COV)
    mirror(TT, MR, EP)
    save_csv(pd.DataFrame(B), "link_betas_correlations.csv", index=False)
    ld = pd.DataFrame(LD)
    save_csv(ld, "link_leverage_drift_beta_bins.csv", index=False)
    save_csv(pd.DataFrame(LR), "link_leverage_drift_regression.csv", index=False)
    save_csv(pd.DataFrame(TR), "link_since_close_tracking_1530.csv", index=False)
    save_csv(pd.DataFrame(LL), "link_leadlag_1min.csv", index=False)
    save_csv(s1, "link_leadlag_1sec_by_day.csv", index=False)
    save_csv(pd.DataFrame(S1s), "link_leadlag_1sec_summary.csv", index=False)
    save_csv(pd.DataFrame(COV), "link_second_bar_coverage.csv", index=False)
    save_csv(pd.DataFrame(MR), "link_soxl_soxs_mirror.csv", index=False)
    save_csv(pd.DataFrame(EP), "link_soxl_soxs_divergence_episodes.csv", index=False)

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, (y, L) in zip(axes, (("SOXL", 3), ("SOXS", -3))):
        for per, mk in (("secondary", "s"), ("primary", "o")):
            g = ld[(ld.ticker == y) & (ld.period == per)]
            ax.plot(100 * g.median_R, g.beta_obs, marker=mk, ms=6, lw=1.5, color=ps.COL[y],
                    alpha=1.0 if per == "primary" else 0.55, label=f"observed {PERIODS[per][0][:4]}-{PERIODS[per][1][:4]}")
        rr = np.linspace(-0.06, 0.06, 100)
        ax.plot(100 * rr, L * (1 + rr) / (1 + L * rr), color=ps.THEORY, lw=1.5, label="theory L(1+r)/(1+Lr)")
        ax.set_xlabel("SOXX return since prior close at interval start (%)")
        ax.set_title(f"{y}: 5-min beta to SOXX vs index move so far")
        ax.legend()
    axes[0].set_ylabel("beta of 5-min returns")
    ps.save(fig, OUT / "leverage_drift_beta.png")

    fig, ax = plt.subplots(figsize=(7.5, 4))
    g = s1.groupby(["x", "y", "lag_s (+ = x leads y)"]).hy_corr.mean().reset_index()
    for (x, y), col in ((("NVDA", "SOXL"), ps.COL["NVDA"]), (("SOXX", "SOXL"), ps.COL["SOXX"]), (("SMH", "SOXL"), ps.COL["SMH"]),
                        (("QQQ", "SOXL"), ps.COL["QQQ"])):
        h = g[(g.x == x) & (g.y == y)]
        ax.plot(h["lag_s (+ = x leads y)"], h.hy_corr, color=col, label=f"{x} vs SOXL")
    ax.axvline(0, color=ps.AXIS, lw=1)
    ax.set_xlim(-15, 15)
    ax.set_xlabel("lag in seconds (+ = driver leads SOXL)")
    ax.set_ylabel("Hayashi-Yoshida correlation (mean of 10 days)")
    ax.set_title("1-second lead-lag, 2026-09-14..2026-09-25, 09:35-15:55 ET")
    ax.legend()
    ps.save(fig, OUT / "leadlag_1sec_hy.png")


if __name__ == "__main__":
    main()
