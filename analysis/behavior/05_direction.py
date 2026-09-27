"""Directional structure at scalping horizons (RTH, full days, split-adjusted log returns).

A. lag-1 autocorrelation of non-overlapping h-minute returns (h=1,2,5,15,30), robust t; 1-min AC at
   lags 1-5; AC by 30-min bucket.
B. Lo-MacKinlay variance ratios (overlapping q-sums of 1-min returns, q=2,5,15,30,60,120) with the
   heteroskedasticity-robust z*; raw and day-standardised; VR by 30-min bucket.
C. DFA-1 scaling exponent on deseasonalised 1-min returns (full day and per hour block) vs a
   within-day shuffle benchmark.
D. Continuation vs reversal after large 1-min / 5-min moves (|z|>=2, >=3; sigma = RMS of the same
   30-min bucket over the previous 20 full sessions -> no look-ahead).
E. Run lengths of consecutive up/down minutes vs within-day shuffled benchmark.
F. Efficiency ratio |net|/sum|1-min moves| per day and per hour block vs sign-randomised benchmark.
The first RTH bar (open print -> 09:30 bar close) is excluded from A/B/C/D/E (auction effects)."""
from __future__ import annotations

import numpy as np
import pandas as pd

import plotstyle as ps
from common import MAIN, OUT, PERIODS, Tk, block_sum, robust_ac, save_csv

RNG = np.random.default_rng(7)
BUCKET = np.arange(390) // 30  # 13 buckets


def bucket_label(b, w=30):
    m = 570 + w * b
    return f"{m // 60:02d}:{m % 60:02d}"


# ------------------------------------------------------------------ A
def autocorr_tables(t, T, per, rows_h, rows_lag, rows_tod):
    sel = T.sel(per)
    r = T.r1[sel][:, 1:]  # drop open bar
    zs = deseason(r)
    for h in (1, 2, 5, 15, 30):
        R = block_sum(r, h)
        x, y = R[:, :-1].ravel(), R[:, 1:].ravel()
        rho, tt, n = robust_ac(x, y)
        Z = block_sum(zs, h)
        rho_s, tt_s, _ = robust_ac(Z[:, :-1].ravel(), Z[:, 1:].ravel())
        rows_h.append({"ticker": t, "period": per, "h_min": h, "ac1": rho, "robust_t": tt, "n_pairs": n,
                       "ac1_deseasonalised": rho_s, "robust_t_deseasonalised": tt_s})
    for lag in range(1, 6):
        rho, tt, n = robust_ac(r[:, :-lag].ravel(), r[:, lag:].ravel())
        rows_lag.append({"ticker": t, "period": per, "lag_min": lag, "ac": rho, "robust_t": tt, "n_pairs": n})
    rr = T.r1[sel]
    for h in (1, 5):
        for b in range(13):
            lo, hi = 30 * b, 30 * b + 30
            if h == 1:
                lo = max(lo, 1)
                x, y = rr[:, lo:hi - 1].ravel(), rr[:, lo + 1:hi].ravel()
            else:
                start = max(lo, 1)
                R = block_sum(rr[:, start:hi], 5)
                x, y = R[:, :-1].ravel(), R[:, 1:].ravel()
            rho, tt, n = robust_ac(x, y)
            rows_tod.append({"ticker": t, "period": per, "h_min": h, "bucket": bucket_label(b), "ac1": rho,
                             "robust_t": tt, "n_pairs": n})


# ------------------------------------------------------------------ B
def vr_stats(r: np.ndarray, q: int):
    """Pooled overlapping VR(q) within rows of r (rows = days), LM (1988) robust z*."""
    mu = np.nanmean(r)
    e = r - mu
    s1 = np.nanmean(e ** 2)
    cs = np.concatenate([np.zeros((r.shape[0], 1)), np.nancumsum(r, axis=1)], axis=1)
    S = cs[:, q:] - cs[:, :-q] - q * mu
    sq = np.nanmean(S ** 2) / q
    vr = sq / s1
    e2 = e ** 2
    den = np.nansum(e2) ** 2
    N = np.isfinite(e).sum()
    theta = 0.0
    for j in range(1, q):
        dj = N * np.nansum(e2[:, j:] * e2[:, :-j]) / den
        theta += (2 * (q - j) / q) ** 2 * dj
    z = np.sqrt(N) * (vr - 1) / np.sqrt(theta)
    return vr, z, N


def deseason(r: np.ndarray) -> np.ndarray:
    """Divide by each day's RMS and by the period's time-of-day RMS profile (Andersen-Bollerslev style)."""
    sd_day = np.sqrt(np.nanmean(r ** 2, axis=1, keepdims=True))
    z = r / sd_day
    return z / np.sqrt(np.nanmean(z ** 2, axis=0, keepdims=True))


def vr_nonoverlap(r: np.ndarray, q: int, n_boot: int = 400):
    """Ratio of totals: sum of squared non-overlapping q-sums / sum of squared 1-min returns
    over the same minutes; each minute weighted once. 95% CI from a day bootstrap."""
    nb = r.shape[1] // q
    R = block_sum(r, q)
    num = np.nansum(R ** 2, axis=1)
    den = np.nansum(r[:, :nb * q] ** 2, axis=1)
    vr = num.sum() / den.sum()
    idx = RNG.integers(0, len(num), size=(n_boot, len(num)))
    bs = num[idx].sum(1) / den[idx].sum(1)
    return vr, np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def vr_tables(t, T, per, rows_vr, rows_vr_tod):
    sel = T.sel(per)
    r = T.r1[sel][:, 1:]
    z = deseason(r)
    for q in (2, 5, 15, 30, 60, 120):
        vr_d, z_d, n = vr_stats(z, q)
        vr_r, z_r, _ = vr_stats(r, q)
        vr_n, lo, hi = vr_nonoverlap(r, q)
        rows_vr.append({"ticker": t, "period": per, "q_min": q,
                        "VR_overlap_deseasonalised": vr_d, "z_robust_deseasonalised": z_d,
                        "VR_nonoverlap_raw": vr_n, "VR_nonoverlap_raw_ci95_lo": lo, "VR_nonoverlap_raw_ci95_hi": hi,
                        "VR_overlap_raw_BIASED_by_Ushape": vr_r, "z_overlap_raw": z_r, "n_returns": n})
    zz = np.concatenate([np.full((z.shape[0], 1), np.nan), z], axis=1)  # re-align to 390 columns
    for q in (5, 15):
        for b in range(13):
            lo = max(30 * b, 1)
            seg = zz[:, lo:30 * b + 30]
            vr, zq, n = vr_stats(seg, q)
            rows_vr_tod.append({"ticker": t, "period": per, "q_min": q, "bucket": bucket_label(b),
                                "VR_overlap_deseasonalised": vr, "z_robust": zq})


# ------------------------------------------------------------------ C
def dfa_F(x: np.ndarray, scales) -> np.ndarray:
    """x: rows = independent segments (days/blocks) of standardised returns. Returns F(s)."""
    prof = np.cumsum(x - np.nanmean(x, axis=1, keepdims=True), axis=1)
    F = []
    for s in scales:
        n = prof.shape[1] // s
        if n < 1:
            F.append(np.nan)
            continue
        seg = prof[:, :n * s].reshape(-1, s)
        tt = np.arange(s) - (s - 1) / 2
        a = seg.mean(1, keepdims=True)
        b = (seg * tt).sum(1, keepdims=True) / (tt ** 2).sum()
        res = seg - a - b * tt
        F.append(np.sqrt(np.mean(res ** 2)))
    return np.array(F)


def alpha(scales, F):
    m = np.isfinite(F)
    return np.polyfit(np.log(np.asarray(scales)[m]), np.log(F[m]), 1)[0]


def shuffle_rows(x):
    y = x.copy()
    for i in range(y.shape[0]):
        RNG.shuffle(y[i])
    return y


def dfa_tables(t, T, per, rows_dfa):
    sel = T.sel(per)
    r = T.r1[sel][:, 1:]
    sd_day = np.sqrt(np.nanmean(r ** 2, axis=1, keepdims=True))
    z = r / sd_day
    prof_tod = np.sqrt(np.nanmean(z ** 2, axis=0, keepdims=True))
    z = z / prof_tod  # deseasonalised
    sc_full = [5, 6, 8, 10, 13, 16, 20, 26, 32, 39, 48, 65, 78, 97, 129]
    F = dfa_F(z, sc_full)
    Fs = dfa_F(shuffle_rows(z), sc_full)
    rows_dfa.append({"ticker": t, "period": per, "segment": "full_day_389min",
                     "alpha_5_129": alpha(sc_full, F), "alpha_5_20": alpha(sc_full[:7], F[:7]),
                     "alpha_20_129": alpha(sc_full[6:], F[6:]),
                     "alpha_shuffled_5_129": alpha(sc_full, Fs), "alpha_shuffled_5_20": alpha(sc_full[:7], Fs[:7]),
                     "alpha_shuffled_20_129": alpha(sc_full[6:], Fs[6:])})
    sc_blk = [4, 5, 6, 10, 12, 15, 20, 30]
    blocks = [(0, 60, "09:31-10:30"), (60, 120, "10:31-11:30"), (120, 180, "11:31-12:30"),
              (180, 240, "12:31-13:30"), (240, 300, "13:31-14:30"), (300, 360, "14:31-15:30"), (360, 389, "15:31-16:00")]
    for lo, hi, lab in blocks:
        x = z[:, lo:hi]
        sc = [s for s in sc_blk if s <= (hi - lo) // 2]
        F = dfa_F(x, sc)
        Fs = dfa_F(shuffle_rows(x), sc)
        rows_dfa.append({"ticker": t, "period": per, "segment": lab, "alpha_5_129": np.nan,
                         "alpha_block": alpha(sc, F), "alpha_block_shuffled": alpha(sc, Fs)})


# ------------------------------------------------------------------ D
def sigma_ref(T, which: str):
    """RMS of returns per (day, 30-min bucket) over the previous 20 full sessions (warm-up included)."""
    fm = T.full
    r = T.r1.copy()
    r[:, 0] = np.nan
    if which == "1m":
        ms = np.stack([np.nanmean(r[:, 30 * b:30 * b + 30] ** 2, axis=1) for b in range(13)], axis=1)
    else:
        R5 = block_sum(np.nan_to_num(T.r1), 5)  # block 0 includes open print
        R5[:, 0] = np.nan
        ms = np.stack([np.nanmean(R5[:, 6 * b:6 * b + 6] ** 2, axis=1) for b in range(13)], axis=1)
    msf = pd.DataFrame(ms[fm])
    ref = np.sqrt(msf.shift(1).rolling(20, min_periods=15).mean()).to_numpy()
    out = np.full(ms.shape, np.nan)
    out[fm] = ref
    return out


def event_stats(sig_r, fwd, day_idx, label, extra):
    """sig_r: event return sign; fwd: forward log return array (n_events x H)."""
    rows = []
    for j, H in enumerate((1, 5, 15, 30)):
        f = fwd[:, j] * sig_r
        ok = np.isfinite(f)
        f, di = f[ok], day_idx[ok]
        nz = f != 0
        # day-clustered s.e.
        dfc = pd.DataFrame({"f": f, "d": di}).groupby("d").f.agg(["sum", "count"])
        mean = f.mean()
        u = dfc["sum"] - mean * dfc["count"]
        se = np.sqrt((u ** 2).sum()) / len(f)
        rows.append({**extra, "event": label, "H_min": H, "n_events": len(f), "n_days": len(dfc),
                     "mean_signed_fwd_bps": 1e4 * mean, "median_signed_fwd_bps": 1e4 * np.median(f),
                     "t_clustered": mean / se if se > 0 else np.nan,
                     "pct_continuation": 100 * (f[nz] > 0).mean() if nz.any() else np.nan,
                     "pct_zero": 100 * (~nz).mean()})
    return rows


def continuation_tables(t, T, rows_ev):
    s1 = sigma_ref(T, "1m")
    s5 = sigma_ref(T, "5m")
    cs = np.nancumsum(np.nan_to_num(T.r1), axis=1)  # cs[k] = log(C_k / O_0)
    for per in PERIODS:
        sel = T.sel(per)
        idx = np.where(sel)[0]
        # ---- 1-minute events
        r = T.r1[idx]
        z = r / s1[idx][:, BUCKET]
        K = np.arange(390)
        for lo_k, hi_k, tod in ((1, 30, "09:31-10:00"), (30, 360, "10:00-15:30"), (1, 360, "all_to_15:30")):
            kmask = (K >= lo_k) & (K < hi_k)
            for thr in (0, 2, 3):
                m = np.isfinite(z) & kmask[None, :] & (np.abs(z) >= thr) & (r != 0)
                di, ki = np.where(m)
                fwd = np.stack([cs[idx[di], ki + H] - cs[idx[di], ki] for H in (1, 5, 15, 30)], axis=1)
                lab = "all_nonzero_1m" if thr == 0 else f"1m_|z|>={thr}"
                rows_ev += event_stats(np.sign(r[di, ki]), fwd, di, lab,
                                       {"ticker": t, "period": per, "tod": tod})
        # ---- 5-minute events (block ends)
        R5 = block_sum(np.nan_to_num(T.r1[idx]), 5)
        z5 = R5 / s5[idx][:, np.arange(78) // 6]
        J = np.arange(78)
        endk = 5 * J + 4
        for lo_j, hi_j, tod in ((1, 6, "09:35-10:00"), (6, 72, "10:00-15:30"), (1, 72, "all_to_15:30")):
            jmask = (J >= lo_j) & (J < hi_j)
            for thr in (0, 2, 3):
                m = np.isfinite(z5) & jmask[None, :] & (np.abs(z5) >= thr) & (R5 != 0)
                di, ji = np.where(m)
                kk = endk[ji]
                fwd = np.stack([cs[idx[di], kk + H] - cs[idx[di], kk] for H in (1, 5, 15, 30)], axis=1)
                lab = "all_nonzero_5m" if thr == 0 else f"5m_|z|>={thr}"
                rows_ev += event_stats(np.sign(R5[di, ji]), fwd, di, lab, {"ticker": t, "period": per, "tod": tod})


# ------------------------------------------------------------------ E
def runs_of(signs_rows):
    lengths = []
    for s in signs_rows:
        s = s[s != 0]
        if len(s) < 2:
            continue
        chg = np.flatnonzero(np.diff(s) != 0)
        b = np.concatenate([[-1], chg, [len(s) - 1]])
        lengths.append(np.diff(b))
    return np.concatenate(lengths)


def run_tables(t, T, per, rows_runs):
    sel = T.sel(per)
    r = T.r1[sel][:, 1:]
    sg = np.sign(r)
    obs = runs_of(sg)
    sh = []
    for _ in range(3):
        sh.append(runs_of([RNG.permutation(x[x != 0]) for x in sg]))
    ben = np.concatenate(sh)
    row = {"ticker": t, "period": per, "pct_zero_return_minutes": 100 * (sg == 0).mean(),
           "pct_up_of_nonzero": 100 * (sg > 0).sum() / (sg != 0).sum(),
           "mean_run_obs": obs.mean(), "mean_run_shuffled": ben.mean()}
    for k in (2, 3, 5, 8):
        row[f"P_run>={k}_obs"] = (obs >= k).mean()
        row[f"P_run>={k}_shuffled"] = (ben >= k).mean()
    row["max_run_obs"] = obs.max()
    rows_runs.append(row)


# ------------------------------------------------------------------ F
def er_tables(t, T, per, rows_er):
    sel = T.sel(per)
    r = T.r1[sel]
    blocks = [(0, 390, "full_day")] + [(60 * i, 60 * i + 60, f"{bucket_label(2 * i)}-{bucket_label(2 * i + 2)}") for i in range(6)] + [(360, 390, "15:30-16:00")]
    for lo, hi, lab in blocks:
        x = r[:, lo:hi]
        a = np.abs(x)
        er = np.abs(x.sum(1)) / a.sum(1)
        bench = np.mean([np.abs((a * RNG.choice([-1, 1], size=a.shape)).sum(1)) / a.sum(1) for _ in range(50)], axis=0)
        rows_er.append({"ticker": t, "period": per, "window": lab, "n_days": len(er), "median_ER": np.median(er),
                        "mean_ER": er.mean(), "median_ER_signrandom": np.median(bench),
                        "mean_ER_signrandom": bench.mean(), "ratio_mean_ER_obs_to_random": er.mean() / bench.mean(),
                        "mean_diff_ER_obs_minus_random": (er - bench).mean(),
                        "t_paired_diff": (er - bench).mean() / ((er - bench).std(ddof=1) / np.sqrt(len(er)))})


# ------------------------------------------------------------------ G (tick-size stratification)
def tick_tables(t, T, rows_tick):
    """1 cent as bps of the prior day's UNADJUSTED close; AC/VR on deseasonalised returns per tick bucket."""
    tick_bps = (100.0 / T.D.C_unadj.shift(1)).reindex(T.dates).to_numpy()
    bins = [(0, 2, "<2bps (px>$50)"), (2, 5, "2-5bps ($20-50)"), (5, 10, "5-10bps ($10-20)"), (10, 1e9, ">=10bps (px<$10)")]
    for per in list(PERIODS) + ["all"]:
        sel = T.sel(None if per == "all" else per)
        for lo, hi, lab in bins:
            m = sel & (tick_bps >= lo) & (tick_bps < hi)
            if m.sum() < 20:
                continue
            r = T.r1[m][:, 1:]
            z = deseason(r)
            rho, tt, n = robust_ac(z[:, :-1].ravel(), z[:, 1:].ravel())
            row = {"ticker": t, "period": per, "tick_bucket": lab, "n_days": int(m.sum()),
                   "median_tick_bps": float(np.median(tick_bps[m])),
                   "pct_zero_1m_returns": 100 * float((r == 0).mean()), "ac1_1m_deseason": rho, "t_ac1": tt}
            for q in (5, 15, 60):
                vr, zq, _ = vr_stats(z, q)
                row[f"VR{q}_deseason"] = vr
                row[f"z_VR{q}"] = zq
            rows_tick.append(row)


def main():
    ps.setup()
    A_h, A_lag, A_tod, B, B_tod, C, D, E, Fer, G = ([] for _ in range(10))
    for t in MAIN:
        T = Tk(t)
        for per in PERIODS:
            autocorr_tables(t, T, per, A_h, A_lag, A_tod)
            vr_tables(t, T, per, B, B_tod)
            dfa_tables(t, T, per, C)
            run_tables(t, T, per, E)
            er_tables(t, T, per, Fer)
        continuation_tables(t, T, D)
        tick_tables(t, T, G)
        print("done", t, flush=True)
    save_csv(pd.DataFrame(A_h), "dir_autocorr_by_horizon.csv", index=False)
    save_csv(pd.DataFrame(A_lag), "dir_autocorr_1min_lags.csv", index=False)
    save_csv(pd.DataFrame(A_tod), "dir_autocorr_by_time_of_day.csv", index=False)
    VR = pd.DataFrame(B)
    save_csv(VR, "dir_variance_ratios.csv", index=False)
    save_csv(pd.DataFrame(B_tod), "dir_variance_ratios_by_time_of_day.csv", index=False)
    save_csv(pd.DataFrame(C), "dir_dfa_hurst.csv", index=False)
    save_csv(pd.DataFrame(D), "dir_continuation_after_large_moves.csv", index=False)
    save_csv(pd.DataFrame(E), "dir_run_lengths.csv", index=False)
    save_csv(pd.DataFrame(Fer), "dir_efficiency_ratio.csv", index=False)
    save_csv(pd.DataFrame(G), "dir_tick_size_stratified.csv", index=False)

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, per in zip(axes, ["secondary", "primary"]):
        for t in ["SOXL", "SOXS", "SOXX", "QQQ"]:
            g = VR[(VR.ticker == t) & (VR.period == per)]
            ax.plot(g.q_min, g.VR_overlap_deseasonalised, marker="o", ms=5, color=ps.COL[t], label=t)
        ax.axhline(1, color=ps.THEORY, lw=1)
        ax.set_xscale("log")
        ax.set_xticks([2, 5, 15, 30, 60, 120])
        ax.set_xticklabels(["2", "5", "15", "30", "60", "120"])
        ax.set_xlabel("q (minutes), overlapping sums of 1-min returns")
        ax.set_title(f"Deseasonalised VR(q), {PERIODS[per][0]}..{PERIODS[per][1]}")
        ax.legend()
    axes[0].set_ylabel("VR(q) (1 = random walk; <1 mean-reverting; >1 trending)")
    ps.save(fig, OUT / "variance_ratios.png")


if __name__ == "__main__":
    main()
