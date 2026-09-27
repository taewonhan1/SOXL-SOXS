"""Short-horizon predictability in RTH.

  * autocorrelation of 1-min and 5-min returns (within-day pairs only), raw and
    time-of-day-standardised, with Lo-MacKinlay heteroskedasticity-robust z statistics
  * Lo-MacKinlay variance ratios VR(q) (1-min base: q=2,5,10,15,30; 5-min base: q=2,3,6),
    pooled and by 30-min time-of-day bucket
  * continuation vs reversal after large 1-min / 5-min moves (> 2 sigma and > 3 sigma, where sigma is the
    trailing-20-day std for that 15-min (1-min moves) or 30-min (5-min moves) time-of-day bucket - no look-ahead).
    Forward returns measured (i) from the event bar's close and (ii) from the NEXT bar's open (tradeable),
    signed in the direction of the move; day-clustered t-stats.
Outputs: pred_acf.csv, pred_vr.csv, pred_vr_tod.csv, pred_bigmoves.csv, fig_pred_acf.png
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import (COLORS, INK2, IS_WIN, OOS_WIN, OUT, PRIMARY, ROBUST, TICKERS, build_panel, in_window,
                    save_csv, setup_mpl)

WINDOWS = {"primary": PRIMARY, "IS": IS_WIN, "OOS": OOS_WIN, "robust": ROBUST}


def returns(P, k=1):
    p = P["p"]
    idx = np.arange(0, 391, k)
    return p[:, idx[1:]] / p[:, idx[:-1]] - 1


def acf_robust(R, j, mask_first=None):
    """R: [days, T] within-day returns. Pooled rho_j over within-day pairs, and Lo-MacKinlay delta_j."""
    x = R - R.mean()
    a = x[:, j:]
    b = x[:, :-j]
    if mask_first is not None:  # mask on the LATER return index (bucket selection)
        mk = mask_first[j:]
        a = a[:, mk]
        b = b[:, mk]
    den = (x ** 2).sum() * (a.size / x.size)  # scale denominator to the number of pairs used
    rho = (a * b).sum() / den
    delta = ((a ** 2) * (b ** 2)).sum() / den ** 2
    return rho, delta, a.size


def vr(R, q, cols=None):
    """Lo-MacKinlay VR via autocorrelations (within-day), heteroskedasticity-robust z*."""
    vr_ = 1.0
    theta = 0.0
    for j in range(1, q):
        if cols is not None:
            sub = R[:, cols]
            rho, delta, _ = acf_robust(sub, j)
        else:
            rho, delta, _ = acf_robust(R, j)
        w = 2 * (1 - j / q)
        vr_ += w * rho
        theta += w ** 2 * delta
    return vr_, (vr_ - 1) / np.sqrt(theta)


def tod_standardise(R):
    s = np.sqrt((R ** 2).mean(axis=0, keepdims=True))
    return R / s


def trailing_sigma(R, bucket_len, lookback=20):
    """sigma[d, t] = sqrt(mean r^2 over previous `lookback` days for the time bucket of t)."""
    nd, T = R.shape
    nb = int(np.ceil(T / bucket_len))
    ss = np.zeros((nd, nb))
    cnt = np.zeros((nd, nb))
    for b in range(nb):
        blk = R[:, b * bucket_len:(b + 1) * bucket_len]
        ss[:, b] = (blk ** 2).sum(axis=1)
        cnt[:, b] = blk.shape[1]
    ss_roll = pd.DataFrame(ss).rolling(lookback).sum().shift(1).to_numpy()
    c_roll = pd.DataFrame(cnt).rolling(lookback).sum().shift(1).to_numpy()
    sig_b = np.sqrt(ss_roll / c_roll)
    return np.repeat(sig_b, bucket_len, axis=1)[:, :T]


def cluster_t(vals, day_ids):
    vals = np.asarray(vals)
    if len(vals) < 3:
        return np.nan
    mu = vals.mean()
    e = vals - mu
    s = pd.Series(e).groupby(day_ids).sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / len(vals)
    return mu / se if se > 0 else np.nan


def big_moves(P, k, thr, horizons, bucket_len, win_mask):
    """k: bar size in minutes (1 or 5). Returns list of dicts."""
    p = P["p"]
    o = P["o"]
    R = returns(P, k)
    sig = trailing_sigma(R, bucket_len)
    nd, T = R.shape
    z = R / sig
    out = []
    ev_d, ev_t = np.where((np.abs(z) > thr) & win_mask[:, None] & np.isfinite(z))
    sgn = np.sign(R[ev_d, ev_t])
    end_pt = (ev_t + 1) * k  # price point index at the event bar's close
    for h in horizons:
        ok = end_pt + h <= 390
        d, t_end, s = ev_d[ok], end_pt[ok], sgn[ok]
        # (i) from event close
        f_close = p[d, t_end + h] / p[d, t_end] - 1
        # (ii) from the next 1-min bar's open (first trade after the signal) to price point t_end+h
        nxt_open = o[d, t_end]  # bar index t_end == minute starting at the event close
        f_open = p[d, t_end + h] / nxt_open - 1
        for lab, f in (("from_close", f_close), ("from_next_open", f_open)):
            sf = s * f
            for dirn, mm in (("all", np.ones_like(s, bool)), ("up", s > 0), ("down", s < 0)):
                v = sf[mm]
                out.append(dict(bar_min=k, thr_sigma=thr, horizon_min=h, entry=lab, direction=dirn, n_events=int(mm.sum()),
                                n_days=int(len(np.unique(d[mm]))),
                                mean_signed_fwd_bps=1e4 * v.mean() if len(v) else np.nan,
                                median_signed_fwd_bps=1e4 * np.median(v) if len(v) else np.nan,
                                share_continuation=(v > 0).mean() if len(v) else np.nan,
                                t_cluster_day=cluster_t(v, d[mm]) if len(v) > 2 else np.nan,
                                mean_abs_fwd_bps=1e4 * np.abs(f[mm]).mean() if len(v) else np.nan))
    return out


def main():
    plt = setup_mpl()
    acf_rows, vr_rows, vrt_rows, bm_rows = [], [], [], []
    for t in TICKERS:
        P = build_panel(t)
        for wn, win in WINDOWS.items():
            m = in_window(P["dates"], win)
            Pm = {kk: (vv[m] if isinstance(vv, np.ndarray) and vv.shape[:1] == m.shape else vv) for kk, vv in P.items()}
            for k, lags in ((1, range(1, 11)), (5, range(1, 7))):
                R = returns(Pm, k)
                for std in (False, True):
                    X = tod_standardise(R) if std else R
                    for j in lags:
                        rho, delta, n = acf_robust(X, j)
                        acf_rows.append(dict(ticker=t, window=wn, bar_min=k, standardised=std, lag=j, rho=rho,
                                             z_robust=rho / np.sqrt(delta), n_pairs=n, n_days=int(m.sum())))
                # excluding first 5 minutes (opening auction effects) for 1-min lag-1
                if k == 1:
                    X = R[:, 5:]
                    rho, delta, n = acf_robust(X, 1)
                    acf_rows.append(dict(ticker=t, window=wn, bar_min=1, standardised="ex_first5", lag=1, rho=rho,
                                         z_robust=rho / np.sqrt(delta), n_pairs=n, n_days=int(m.sum())))
            R1 = returns(Pm, 1)
            R5 = returns(Pm, 5)
            for q in (2, 5, 10, 15, 30):
                v, z = vr(R1, q)
                vr_rows.append(dict(ticker=t, window=wn, base_min=1, q=q, horizon_min=q, VR=v, z_star=z))
            for q in (2, 3, 6):
                v, z = vr(R5, q)
                vr_rows.append(dict(ticker=t, window=wn, base_min=5, q=q, horizon_min=5 * q, VR=v, z_star=z))
            if wn in ("primary", "robust"):
                for b in range(0, 390, 30):
                    cols = np.arange(b, b + 30)
                    for q in (5, 15):
                        v, z = vr(R1, q, cols=cols)
                        vrt_rows.append(dict(ticker=t, window=wn, bucket=f"{(570 + b) // 60:02d}:{(570 + b) % 60:02d}",
                                             q=q, VR=v, z_star=z))
                    rho, delta, n = acf_robust(R1[:, cols], 1)
                    vrt_rows.append(dict(ticker=t, window=wn, bucket=f"{(570 + b) // 60:02d}:{(570 + b) % 60:02d}",
                                         q="acf1", VR=rho, z_star=rho / np.sqrt(delta)))
        # big moves (rolling sigma needs full history -> compute on full panel, then mask window)
        for wn, win in WINDOWS.items():
            m = in_window(P["dates"], win)
            for thr in (2.0, 3.0):
                for r in big_moves(P, 1, thr, (1, 5, 15, 30), 15, m):
                    r.update(ticker=t, window=wn)
                    bm_rows.append(r)
                for r in big_moves(P, 5, thr, (5, 15, 30), 6, m):
                    r.update(ticker=t, window=wn)
                    bm_rows.append(r)
        print("done", t, flush=True)
    A = pd.DataFrame(acf_rows)
    save_csv(A, "pred_acf.csv")
    V = pd.DataFrame(vr_rows)
    save_csv(V, "pred_vr.csv")
    save_csv(pd.DataFrame(vrt_rows), "pred_vr_tod.csv")
    B = pd.DataFrame(bm_rows)
    save_csv(B, "pred_bigmoves.csv")

    # figure: 1-min ACF (standardised) primary window
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for t in TICKERS:
        x = A[(A.ticker == t) & (A.window == "primary") & (A.bar_min == 1) & (A.standardised == True)]
        axes[0].plot(x.lag, x.rho, marker="o", markersize=4, color=COLORS[t], label=t)
        x = V[(V.ticker == t) & (V.window == "primary") & (V.base_min == 1)]
        axes[1].plot(x.q, x.VR, marker="o", markersize=4, color=COLORS[t], label=t)
    axes[0].axhline(0, color=INK2, linewidth=0.8)
    axes[1].axhline(1, color=INK2, linewidth=0.8)
    axes[0].set_title("Autocorrelation of 1-min RTH returns (ToD-standardised)")
    axes[0].set_xlabel("lag (minutes)")
    axes[1].set_title("Variance ratio VR(q), 1-min base")
    axes[1].set_xlabel("q (minutes)")
    axes[1].legend(ncol=2, fontsize=8)
    for ax in axes:
        ax.text(0.01, 0.02, "2024-10-01 to 2026-09-25, 493 sessions", transform=ax.transAxes, fontsize=7, color=INK2)
    fig.tight_layout()
    fig.savefig(OUT / "fig_pred_acf_vr.png")
    plt.close(fig)

    pd.set_option("display.width", 250)
    print(A[(A.window == "primary") & (A.lag <= 3) & (A.standardised != True)].round(4).to_string())
    print(V[V.window.isin(["primary", "robust"])].round(3).to_string())
    bb = B[(B.window == "primary") & (B.direction == "all") & (B.ticker.isin(["SOXL", "SOXS", "SOXX"]))]
    print(bb.round(2).to_string())


if __name__ == "__main__":
    main()
