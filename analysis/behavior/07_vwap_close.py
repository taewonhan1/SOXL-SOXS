"""VWAP behaviour and closing behaviour (full days, RTH).

VWAP = cumulative sum(minute vw * v) / cumulative sum(v) from 09:30 (minute bars; auction prints are
not in minute bars). VWAP sigma band = volume-weighted SD of minute vw around the running VWAP.
Benchmark = sign-randomised minute path (same |returns| order, same volumes; 10 draws/day).
Closing: Gao-Han-Li-Zhou (2018) intraday momentum regressions with Newey-West (5 lags) SEs;
LETF-rebalancing test (late-day moves vs the index move since the prior close); 15:50-16:00 and the
closing-auction jump (official close vs last trade before 16:00)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

import plotstyle as ps
from common import MAIN, OUT, PANEL, PERIODS, Tk, q, save_csv

RNG = np.random.default_rng(5)
NSIM = 10


def vwap_arrays(P, V):
    cv = np.nancumsum(V, 1)
    cpv = np.nancumsum(P * V, 1)
    cp2v = np.nancumsum(P * P * V, 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        vw = cpv / cv
        sd = np.sqrt(np.maximum(cp2v / cv - vw ** 2, 0))
    return vw, sd


def crosses(C, VWAP, band=None):
    d = C - VWAP
    if band is None:
        s = np.sign(d[:, 5:])
        s = np.where(s == 0, np.nan, s)
        s = pd.DataFrame(s).T.ffill().T.to_numpy()
        return np.nansum(np.abs(np.diff(s, axis=1)) > 0, axis=1)
    # hysteresis: state flips only after crossing to the other side of +/- band
    n, m = d.shape
    cnt = np.zeros(n, int)
    state = np.zeros(n)
    for k in range(5, m):
        bk = band[:, k] if np.ndim(band) == 2 else band
        up = d[:, k] > bk
        dn = d[:, k] < -bk
        cnt += ((state < 0) & up) | ((state > 0) & dn)
        state = np.where(up, 1, np.where(dn, -1, state))
    return cnt


def revisit(C, L, H, VWAP, SD, m, use_close_only=False):
    """events: fresh close beyond VWAP +/- m*SD at k in [30, 329]; revisit within 15/30/60 min."""
    out = {15: [], 30: [], 60: []}
    n = C.shape[0]
    for side in (1, -1):
        lvl = VWAP + side * m * SD
        beyond = (C - lvl) * side > 0
        fresh = beyond[:, 1:] & ~beyond[:, :-1]
        fresh = np.concatenate([np.zeros((n, 1), bool), fresh], axis=1)
        fresh[:, :30] = False
        fresh[:, 330:] = False
        if use_close_only:
            touch = (C - VWAP) * side <= 0
        else:
            touch = (L - VWAP) <= 0 if side == 1 else (H - VWAP) >= 0
        di, ki = np.where(fresh)
        for d, k in zip(di, ki):
            tt = touch[d, k + 1:k + 61]
            first = np.argmax(tt) if tt.any() else 999
            for w in out:
                out[w].append(first < w)
    return {w: (100 * np.mean(v) if v else np.nan) for w, v in out.items()}, len(out[15])


def vwap_block(t, T, dm, per, rows, tod_rows):
    sel = T.sel(per)
    C, H, L, V, VW = T.C[sel], T.H[sel], T.L[sel], T.V[sel], T.VW[sel]
    atr = dm.atr14_prev.to_numpy()[sel]
    VWAP, SD = vwap_arrays(VW, V)
    dist_bps = 1e4 * np.log(C / VWAP)
    dist_atr = (dist_bps / 100) / atr[:, None]
    after = dist_bps[:, 30:]
    row = {"ticker": t, "period": per, "n_days": int(sel.sum()),
           "median_abs_dist_bps_from_10:00": q(np.abs(after), 50), "p90_abs_dist_bps_from_10:00": q(np.abs(after), 90),
           "median_abs_dist_ATR_from_10:00": q(np.abs(dist_atr[:, 30:]), 50),
           "p90_abs_dist_ATR_from_10:00": q(np.abs(dist_atr[:, 30:]), 90),
           "median_band_sd_bps_at_12:00": q(1e4 * SD[:, 150] / VWAP[:, 150], 50)}
    cr_raw = crosses(C, VWAP)
    cr_band = crosses(C, VWAP, band=(0.02 * atr / 100)[:, None] * VWAP)
    row["median_crosses_per_day_raw"] = np.median(cr_raw)
    row["mean_crosses_per_day_raw"] = cr_raw.mean()
    row["median_crosses_per_day_band0.02ATR"] = np.median(cr_band)
    row["mean_crosses_per_day_band0.02ATR"] = cr_band.mean()
    one_close = ((C[:, 60:] > VWAP[:, 60:]).all(1)) | ((C[:, 60:] < VWAP[:, 60:]).all(1))
    one_hl = ((L[:, 60:] > VWAP[:, 60:]).all(1)) | ((H[:, 60:] < VWAP[:, 60:]).all(1))
    row["pct_days_one_side_after_10:30_closes"] = 100 * one_close.mean()
    row["pct_days_one_side_after_10:30_no_touch_hl"] = 100 * one_hl.mean()
    for m in (1, 2):
        rv, n = revisit(C, L, H, VWAP, SD, m)
        rvc, _ = revisit(C, L, H, VWAP, SD, m, use_close_only=True)
        for w in (15, 30, 60):
            row[f"pct_revisit_{w}m_after_{m}sd_touch_hl"] = rv[w]
            row[f"pct_revisit_{w}m_after_{m}sd_close"] = rvc[w]
        row[f"n_events_{m}sd"] = n
    # random benchmark
    r = T.r1[sel]
    O = T.O[sel][:, 0]
    bench = {k: [] for k in ("cr_raw", "cr_band", "one", "rv1_15", "rv1_30", "rv1_60", "rv2_15", "rv2_30", "rv2_60")}
    for _ in range(NSIM):
        s = RNG.choice([-1.0, 1.0], size=r.shape)
        Cs = O[:, None] * np.exp(np.cumsum(np.abs(r) * s, axis=1))
        VWs, SDs = vwap_arrays(Cs, V)
        bench["cr_raw"].append(crosses(Cs, VWs).mean())
        bench["cr_band"].append(crosses(Cs, VWs, band=(0.02 * atr / 100)[:, None] * VWs).mean())
        bench["one"].append(100 * (((Cs[:, 60:] > VWs[:, 60:]).all(1)) | ((Cs[:, 60:] < VWs[:, 60:]).all(1))).mean())
        for m in (1, 2):
            rv, _ = revisit(Cs, Cs, Cs, VWs, SDs, m, use_close_only=True)
            for w in (15, 30, 60):
                bench[f"rv{m}_{w}"].append(rv[w])
    row["RANDOM_mean_crosses_raw"] = np.mean(bench["cr_raw"])
    row["RANDOM_mean_crosses_band0.02ATR"] = np.mean(bench["cr_band"])
    row["RANDOM_pct_days_one_side_after_10:30_closes"] = np.mean(bench["one"])
    for m in (1, 2):
        for w in (15, 30, 60):
            row[f"RANDOM_pct_revisit_{w}m_after_{m}sd_close"] = np.mean(bench[f"rv{m}_{w}"])
    rows.append(row)
    for b in range(13):
        seg = dist_bps[:, 30 * b:30 * b + 30]
        tod_rows.append({"ticker": t, "period": per, "bucket": f"{(570 + 30 * b) // 60:02d}:{(570 + 30 * b) % 60:02d}",
                         "median_abs_dist_bps": q(np.abs(seg), 50),
                         "median_abs_dist_ATR": q(np.abs(dist_atr[:, 30 * b:30 * b + 30]), 50)})


def hac(y, X, lags=5):
    Xc = sm.add_constant(X)
    m = sm.OLS(y, Xc, missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return m


def closing_block(t, T, dm, per, rows):
    sel = T.sel(per)
    C = T.C[sel]
    D = dm[sel]
    Cc, O, pc = D.C.to_numpy(), D.O.to_numpy(), D.prevC_adj.to_numpy()
    r_l30 = np.log(Cc / C[:, 359])
    preds = {"prevclose_to_10:00 (GHLZ first half-hour)": np.log(C[:, 29] / pc),
             "09:30_to_10:00": np.log(C[:, 29] / O),
             "09:30_to_15:30": np.log(C[:, 359] / O),
             "prevclose_to_15:30": np.log(C[:, 359] / pc),
             "15:00_to_15:30 (GHLZ 12th half-hour)": np.log(C[:, 359] / C[:, 329])}
    for name, x in preds.items():
        mdl = hac(r_l30, x)
        agree = np.mean(np.sign(r_l30[x != 0]) == np.sign(x[x != 0]))
        rows.append({"ticker": t, "period": per, "model": f"last30 ~ {name}", "n": int(mdl.nobs),
                     "slope": mdl.params[1], "t_NW": mdl.tvalues[1], "R2_pct": 100 * mdl.rsquared,
                     "sign_agreement_pct": 100 * agree, "mean_abs_last30_bps": 1e4 * np.mean(np.abs(r_l30))})
    X = np.column_stack([preds["prevclose_to_10:00 (GHLZ first half-hour)"], preds["15:00_to_15:30 (GHLZ 12th half-hour)"]])
    mdl = hac(r_l30, X)
    rows.append({"ticker": t, "period": per, "model": "last30 ~ first_half_hour + 12th_half_hour (joint)", "n": int(mdl.nobs),
                 "slope": mdl.params[1], "t_NW": mdl.tvalues[1], "slope2": mdl.params[2], "t2_NW": mdl.tvalues[2],
                 "R2_pct": 100 * mdl.rsquared})


def rebalancing_block(per, TT, DM, rows, final_rows):
    """Late-day behaviour vs the driver-index move from the prior close to 15:30."""
    for driver, tickers in (("SOXX", ["SOXX", "SMH", "NVDA", "SOXL", "SOXS"]), ("QQQ", ["QQQ", "TQQQ", "SQQQ"])):
        Td, Dd = TT[driver], DM[driver]
        sel = Td.sel(per)
        R = np.log(Td.C[sel][:, 359] / Dd.prevC_adj.to_numpy()[sel])
        bins = [(0, 0.01, "|R|<1%"), (0.01, 0.02, "1-2%"), (0.02, 0.03, "2-3%"), (0.03, 1, ">=3%")]
        for t in tickers:
            T, D = TT[t], DM[t]
            C = T.C[sel]
            Dx = D[sel]
            own = np.log(C[:, 359] / Dx.prevC_adj.to_numpy())
            r_l30 = np.log(Dx.C.to_numpy() / C[:, 359])
            r_1550 = np.log(Dx.C.to_numpy() / C[:, 379])
            r_last10_trade = np.log(C[:, 389] / C[:, 379])
            jump = np.log(Dx.C.to_numpy() / C[:, 389])
            for lo, hi, lab in bins:
                m = (np.abs(R) >= lo) & (np.abs(R) < hi)
                if m.sum() < 5:
                    continue
                sg = np.sign(own[m])
                rows.append({"driver": driver, "ticker": t, "period": per, "driver_move_bin": lab, "n_days": int(m.sum()),
                             "mean_abs_last30_bps": 1e4 * np.mean(np.abs(r_l30[m])),
                             "mean_signed_last30_bps (+ = continues own day move)": 1e4 * np.mean(sg * r_l30[m]),
                             "pct_last30_same_dir_as_own_day_move": 100 * np.mean(np.sign(r_l30[m]) == sg),
                             "mean_signed_15:50_to_close_bps": 1e4 * np.mean(sg * r_1550[m]),
                             "pct_15:50_to_close_same_dir": 100 * np.mean(np.sign(r_1550[m]) == sg),
                             "mean_signed_auction_jump_bps": 1e4 * np.mean(sg * jump[m]),
                             "mean_abs_auction_jump_bps": 1e4 * np.mean(np.abs(jump[m]))})
            # regression of last-30 on own day-so-far move (all days)
            mdl = hac(r_l30, own)
            final_rows.append({"ticker": t, "period": per, "stat": "last30 ~ own prevclose_to_15:30", "slope": mdl.params[1],
                               "t_NW": mdl.tvalues[1], "n": int(mdl.nobs)})
            mdl = hac(r_1550, own)
            final_rows.append({"ticker": t, "period": per, "stat": "15:50_to_close ~ own prevclose_to_15:30",
                               "slope": mdl.params[1], "t_NW": mdl.tvalues[1], "n": int(mdl.nobs)})
            mdl = hac(jump, np.log(C[:, 389] / Dx.prevC_adj.to_numpy()))
            final_rows.append({"ticker": t, "period": per, "stat": "auction_jump ~ own prevclose_to_15:59",
                               "slope": mdl.params[1], "t_NW": mdl.tvalues[1], "n": int(mdl.nobs)})
            mdl = hac(jump, r_last10_trade)
            final_rows.append({"ticker": t, "period": per, "stat": "auction_jump ~ 15:50_to_15:59_last_trade",
                               "slope": mdl.params[1], "t_NW": mdl.tvalues[1], "n": int(mdl.nobs)})


def last10_block(t, T, dm, per, rows):
    sel = T.sel(per)
    r = T.r1[sel]
    V = T.V[sel]
    D = dm[sel]
    jump = 1e4 * np.log(D.C.to_numpy() / T.C[sel][:, 389])
    rows.append({"ticker": t, "period": per, "n_days": int(sel.sum()),
                 "pct_RTH_minute_volume_15:50-15:59": 100 * np.median(np.nansum(V[:, 380:], 1) / np.nansum(V, 1)),
                 "pct_RTH_minute_volume_15:30-15:59": 100 * np.median(np.nansum(V[:, 360:], 1) / np.nansum(V, 1)),
                 "rms_1m_15:50-15:59_over_15:00-15:49": np.sqrt(np.nanmean(r[:, 380:] ** 2) / np.nanmean(r[:, 330:380] ** 2)),
                 "median_abs_auction_jump_bps": q(np.abs(jump), 50), "p90_abs_auction_jump_bps": q(np.abs(jump), 90),
                 "p99_abs_auction_jump_bps": q(np.abs(jump), 99),
                 "median_abs_auction_jump_in_1min_rms_units": q(np.abs(jump) / (1e4 * np.sqrt(np.nanmean(r[:, 380:] ** 2))), 50),
                 "median_unadj_price": D.C_unadj.median(), "median_tick_bps": q(100 / D.C_unadj, 50)})


def main():
    ps.setup()
    VW, VWT, CL, RB, RBF, L10 = [], [], [], [], [], []
    TT, DM = {}, {}
    for t in MAIN:
        T = Tk(t)
        dm = pd.read_parquet(PANEL / f"{t}_dm.parquet").reindex(T.dates)
        TT[t], DM[t] = T, dm
        for per in PERIODS:
            vwap_block(t, T, dm, per, VW, VWT)
            closing_block(t, T, dm, per, CL)
            last10_block(t, T, dm, per, L10)
        print("done", t, flush=True)
    for per in PERIODS:
        rebalancing_block(per, TT, DM, RB, RBF)
    save_csv(pd.DataFrame(VW), "vwap_behaviour.csv", index=False)
    save_csv(pd.DataFrame(VWT), "vwap_distance_by_time_of_day.csv", index=False)
    save_csv(pd.DataFrame(CL), "close_intraday_momentum_ghlz.csv", index=False)
    save_csv(pd.DataFrame(RB), "close_letf_rebalancing_by_index_move.csv", index=False)
    save_csv(pd.DataFrame(RBF), "close_late_day_regressions.csv", index=False)
    save_csv(pd.DataFrame(L10), "close_last10min_and_auction.csv", index=False)


if __name__ == "__main__":
    main()
