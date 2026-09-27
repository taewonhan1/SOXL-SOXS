"""Extended hours (pre-market 04:00-09:30, after-hours 16:00-20:00 ET, minute bars), tails,
discontinuities (multi-minute gaps in RTH minute bars = candidate halts), closing-price dislocations.
Full days only for extended-hours statistics."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import MAIN, PANEL, PERIODS, Tk, q, save_csv


def ext_hours(t, T, dm, per, rows, lvl_rows):
    sel = T.sel(per)
    D = dm[sel]
    tot = D.pm_vol.fillna(0) + D.V_rth + D.ah_vol.fillna(0)
    pm_rng = 100 * (D.pm_high - D.pm_low) / D.prevC_adj
    ah_rng = 100 * (D.ah_high - D.ah_low) / D.C
    rth_rng = 100 * (D.H - D.L) / D.O
    Hm, Lm, Cm = T.H[sel], T.L[sel], T.C[sel]
    ph, pl = D.pm_high.to_numpy(), D.pm_low.to_numpy()
    O = D.O.to_numpy()
    has_pm = np.isfinite(ph)
    above_open = O > ph
    below_open = O < pl
    takes_hi = (D.H.to_numpy() > ph)
    takes_lo = (D.L.to_numpy() < pl)
    rows.append({"ticker": t, "period": per, "n_days": int(sel.sum()), "pct_days_with_premarket_bars": 100 * has_pm.mean(),
                 "median_premarket_bars": D.pm_bars.median(), "median_afterhours_bars": D.ah_bars.median(),
                 "median_premarket_range_pct_of_prevclose": q(pm_rng, 50), "p90_premarket_range_pct": q(pm_rng, 90),
                 "median_afterhours_range_pct_of_close": q(ah_rng, 50), "p90_afterhours_range_pct": q(ah_rng, 90),
                 "median_premarket_range_over_RTH_range": q(pm_rng / rth_rng, 50),
                 "median_premarket_vol_share_pct": 100 * q(D.pm_vol / tot, 50), "mean_premarket_vol_share_pct": 100 * (D.pm_vol / tot).mean(),
                 "median_afterhours_vol_share_pct": 100 * q(D.ah_vol / tot, 50), "mean_afterhours_vol_share_pct": 100 * (D.ah_vol / tot).mean(),
                 "pct_open_above_PM_high": 100 * np.mean(above_open[has_pm]), "pct_open_below_PM_low": 100 * np.mean(below_open[has_pm]),
                 "pct_RTH_takes_PM_high": 100 * np.mean(takes_hi[has_pm]), "pct_RTH_takes_PM_low": 100 * np.mean(takes_lo[has_pm]),
                 "pct_RTH_takes_both": 100 * np.mean((takes_hi & takes_lo)[has_pm]),
                 "pct_RTH_takes_neither": 100 * np.mean((~takes_hi & ~takes_lo)[has_pm])})
    # behaviour at the first RTH break of PM high / low (open inside the PM range)
    for side, lvl in (("PM_high", ph), ("PM_low", pl)):
        res = []
        for i in np.where(has_pm & ~above_open & ~below_open)[0]:
            if side == "PM_high":
                hit = np.where(Hm[i] > lvl[i])[0]
            else:
                hit = np.where(Lm[i] < lvl[i])[0]
            if not len(hit):
                continue
            k = hit[0]
            s = 1 if side == "PM_high" else -1
            fwdC = Cm[i, k + 1:k + 16]
            back = np.any((fwdC - lvl[i]) * s < 0) if len(fwdC) else np.nan
            fh, fl = Hm[i, k:k + 31], Lm[i, k:k + 31]
            mfe = (fh.max() / lvl[i] - 1) if s == 1 else (1 - fl.min() / lvl[i])
            mae = (1 - fl.min() / lvl[i]) if s == 1 else (fh.max() / lvl[i] - 1)
            close_beyond = (D.C.iloc[i] - lvl[i]) * s > 0
            res.append((k, back, mfe, mae, close_beyond))
        if not res:
            continue
        k, back, mfe, mae, cb = map(np.array, zip(*res))
        lvl_rows.append({"ticker": t, "period": per, "level": side, "n_breaks": len(k),
                         "median_minutes_after_open": float(np.median(k)),
                         "pct_breaks_in_first_15min": 100 * np.mean(k < 15),
                         "pct_close_back_inside_within_15min": 100 * np.nanmean(back.astype(float)),
                         "median_MFE_30m_pct": 100 * np.median(mfe), "median_MAE_30m_pct": 100 * np.median(mae),
                         "pct_MFE30_gt_MAE30": 100 * np.mean(mfe > mae),
                         "pct_day_closes_beyond_level": 100 * np.mean(cb)})


def tails(t, T, per, rows, top_rows):
    sel = T.sel(per, full_only=False) & np.isin(T.period, [per])
    r = T.r1[sel]
    dates = T.dates[sel]
    a = np.abs(r)
    nmin = np.isfinite(r).sum()
    row = {"ticker": t, "period": per, "n_days": int(sel.sum()), "n_minutes": int(nmin),
           "p99_abs_1m_bps": 1e4 * q(a, 99), "p999_abs_1m_bps": 1e4 * q(a, 99.9)}
    for th in (0.01, 0.02, 0.03, 0.05):
        big = a > th
        row[f"pct_minutes_abs1m>{int(th * 100)}%"] = 100 * np.nansum(big) / nmin
        row[f"mean_count_per_day_abs1m>{int(th * 100)}%"] = np.nansum(big) / sel.sum()
        row[f"pct_days_with_any_abs1m>{int(th * 100)}%"] = 100 * np.mean(np.nansum(big, 1) > 0)
        row[f"share_of_abs1m>{int(th * 100)}%_in_first_15min"] = (np.nansum(big[:, :15]) / np.nansum(big)) if np.nansum(big) else np.nan
    lc = np.log(T.C[sel])
    r5 = lc[:, 5:] - lc[:, :-5]
    a5 = np.abs(r5)
    for th in (0.02, 0.03, 0.05):
        row[f"pct_5m_windows_abs>{int(th * 100)}%"] = 100 * np.nanmean(a5 > th)
    rows.append(row)
    for lab, arr, off in (("1min", r, 0), ("5min_rolling", r5, 5)):
        flat = np.abs(np.nan_to_num(arr)).ravel()
        order = np.argsort(flat)[::-1]
        seen = set()
        for idx in order:
            i, k = divmod(idx, arr.shape[1])
            if dates[i] in seen:
                continue
            seen.add(dates[i])
            mm = 570 + k + (0 if lab == "1min" else 0)
            end = 570 + k + off
            top_rows.append({"ticker": t, "period": per, "window": lab, "date": dates[i],
                             "minute_ET" if lab == "1min" else "window_end_ET": f"{(mm if lab == '1min' else end) // 60:02d}:{(mm if lab == '1min' else end) % 60:02d}",
                             "return_pct": 100 * (np.expm1(arr[i, k]))})
            if len(seen) >= 10:
                break


def gaps_in_bars(TT, rows):
    for t, T in TT.items():
        has, valid = T.has, T.valid
        m = np.isin(T.period, ["primary", "secondary"])
        for i in np.where(m)[0]:
            miss = valid[i] & ~has[i]
            if not miss.any():
                continue
            k = 0
            n = valid[i].sum()
            while k < n:
                if miss[k]:
                    j = k
                    while j < n and miss[j]:
                        j += 1
                    if j - k >= 5:
                        others = [o for o, U in TT.items() if o != t and U.valid[i, k:j].all() and (~U.has[i, k:j]).all()]
                        mm = 570 + k
                        rows.append({"ticker": t, "date": T.dates[i], "start_ET": f"{mm // 60:02d}:{mm % 60:02d}",
                                     "missing_minutes": j - k, "tickers_also_missing_same_window": ",".join(others),
                                     "price_move_across_gap_pct": 100 * (T.C[i, min(j, n - 1)] / T.C[i, max(k - 1, 0)] - 1)})
                    k = j
                else:
                    k += 1


def main():
    EH, LV, TL, TOP, GP, DL = ([] for _ in range(6))
    TT = {}
    for t in MAIN:
        T = Tk(t)
        TT[t] = T
        dm = pd.read_parquet(PANEL / f"{t}_dm.parquet").reindex(T.dates)
        for per in PERIODS:
            ext_hours(t, T, dm, per, EH, LV)
            tails(t, T, per, TL, TOP)
        D = dm[np.isin(T.period, ["primary", "secondary"])].copy()
        D["close_vs_last_trade_bps"] = 1e4 * np.log(D.C / D.C_last)
        D["next_gap_pct"] = D.gap_pct.shift(-1)
        for d, r in D[D.close_vs_last_trade_bps.abs() > 100].iterrows():
            DL.append({"ticker": t, "date": d, "official_close_vs_last_pre16:00_trade_bps": r.close_vs_last_trade_bps,
                       "day_cc_pct": r.cc_pct, "next_day_gap_pct": r.next_gap_pct})
        print("done", t, flush=True)
    gaps_in_bars(TT, GP)
    save_csv(pd.DataFrame(EH), "ext_hours_summary.csv", index=False)
    save_csv(pd.DataFrame(LV), "ext_hours_pm_level_breaks.csv", index=False)
    save_csv(pd.DataFrame(TL), "tails_frequency.csv", index=False)
    save_csv(pd.DataFrame(TOP), "tails_top10_moves.csv", index=False)
    save_csv(pd.DataFrame(GP), "tails_rth_minute_bar_gaps_ge5min.csv", index=False)
    save_csv(pd.DataFrame(DL), "tails_closing_dislocations_gt100bps.csv", index=False)


if __name__ == "__main__":
    main()
