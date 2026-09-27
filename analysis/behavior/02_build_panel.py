"""Build the analysis panel from cached raw data.

Outputs (data/behavior/panel/):
  sessions.csv            trading calendar with half-day flag (detected from QQQ volume profile)
  {T}_rth.npz             RTH minute matrices (days x 390): O,H,L,C (C forward-filled), V, VW, N, has
  {T}_daily.parquet       per-day table: official O/H/L/C (split-adjusted), unadjusted close,
                          dividend-adjusted prior close, pre-market / after-hours stats, volumes
Outputs (analysis/behavior/output/):
  data_coverage.csv       bar coverage and consistency checks per ticker
  half_days.csv           detected half-days
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from common import DATA, END, MAIN, N_RTH, OUT, PANEL, WARMUP_START, load_daily, load_minute, period_of, save_csv

RTH_START = 9 * 60 + 30


def detect_sessions() -> pd.DataFrame:
    q = load_minute("QQQ")
    q = q[(q.date >= WARMUP_START) & (q.date <= END)]
    rth_morning = q[(q["mod"] >= RTH_START) & (q["mod"] < 13 * 60)].groupby("date").v.sum()
    afternoon = q[(q["mod"] >= 13 * 60 + 5) & (q["mod"] < 16 * 60)].groupby("date").v.sum()
    daily = load_daily("QQQ")
    dates = sorted(set(daily.index) & set(rth_morning.index))
    dates = [d for d in dates if WARMUP_START <= d <= END]
    ratio = (afternoon.reindex(dates).fillna(0) / rth_morning.reindex(dates)).rename("pm_am_vol_ratio")
    s = pd.DataFrame({"date": dates})
    s["pm_am_vol_ratio"] = ratio.values
    s["is_half"] = s.pm_am_vol_ratio < 0.15
    s["n_rth"] = np.where(s.is_half, 210, N_RTH)
    s["rth_end_mod"] = np.where(s.is_half, 13 * 60, 16 * 60)
    s["weekday"] = pd.to_datetime(s.date).dt.day_name()
    s["period"] = period_of(s.date)
    s["quarter"] = pd.PeriodIndex(pd.to_datetime(s.date), freq="Q").astype(str)
    return s.set_index("date")


def dividend_factors(ticker: str, unadj: pd.DataFrame) -> pd.Series:
    """factor f such that dividend-adjusted prior close = prior close * f on ex-dates."""
    ref = json.loads((DATA / "ref" / "splits_dividends.json").read_text())[ticker]["dividends"]
    f = pd.Series(1.0, index=unadj.index)
    dates = list(unadj.index)
    for d in ref:
        ex = d.get("ex_dividend_date")
        amt = d.get("cash_amount") or 0
        if ex in f.index and amt > 0:
            i = dates.index(ex)
            if i > 0:
                prev_close = unadj["c"].iloc[i - 1]
                f.loc[ex] = 1 - amt / prev_close
    return f


def build_ticker(t: str, sess: pd.DataFrame) -> dict:
    m = load_minute(t)
    m = m[m.date.isin(sess.index)]
    days = list(sess.index)
    di = {d: i for i, d in enumerate(days)}
    nd = len(days)

    # ---------------- RTH matrices
    r = m[(m["mod"] >= RTH_START) & (m["mod"] < 16 * 60)].copy()
    r["row"] = r.date.map(di).astype(int)
    r["col"] = (r["mod"] - RTH_START).astype(int)
    endcol = (sess.loc[r.date, "rth_end_mod"].to_numpy() - RTH_START)
    r = r[r.col.to_numpy() < endcol]
    shape = (nd, N_RTH)
    mats = {}
    for k, col in [("O", "o"), ("H", "h"), ("L", "l"), ("C", "c"), ("V", "v"), ("VW", "vw"), ("N", "n")]:
        a = np.full(shape, np.nan)
        a[r.row.to_numpy(), r.col.to_numpy()] = r[col].to_numpy(dtype=float)
        mats[k] = a
    has = np.isfinite(mats["C"])
    # forward fill close within the day; missing first minute -> first available open
    C = pd.DataFrame(mats["C"]).T.ffill().T.to_numpy()
    first_open = pd.DataFrame(mats["O"]).T.bfill().T.to_numpy()[:, 0]
    lead_nan = np.isnan(C)
    C = np.where(lead_nan, first_open[:, None], C)
    valid = np.zeros(shape, bool)
    for i, n in enumerate(sess.n_rth.to_numpy()):
        valid[i, :n] = True
    C[~valid] = np.nan
    O = np.where(has, mats["O"], C)
    H = np.where(has, mats["H"], C)
    L = np.where(has, mats["L"], C)
    V = np.where(has, mats["V"], 0.0)
    V[~valid] = np.nan
    VW = np.where(has, mats["VW"], C)
    N = np.where(has, mats["N"], 0.0)
    np.savez_compressed(PANEL / f"{t}_rth.npz", dates=np.array(days), O=O, H=H, L=L, C=C, V=V, VW=VW, N=N,
                        has=has, valid=valid)

    # ---------------- daily table
    dadj = load_daily(t, True).reindex(days)
    dun = load_daily(t, False).reindex(days)
    fdiv = dividend_factors(t, load_daily(t, False)).reindex(days).fillna(1.0)
    D = pd.DataFrame(index=pd.Index(days, name="date"))
    D["period"] = sess.period
    D["is_half"] = sess.is_half
    D["O"] = dadj.o
    D["H"] = dadj.h
    D["L"] = dadj.l
    D["C"] = dadj.c                       # official close (closing auction)
    D["V_daily"] = dadj.v
    D["C_unadj"] = dun.c
    D["div_factor"] = fdiv
    D["prevC"] = D.C.shift(1)
    D["prevC_adj"] = D.prevC * D.div_factor   # dividend-adjusted prior close
    # minute-derived RTH values
    D["O_min"] = O[:, 0]
    D["H_min"] = np.nanmax(H, axis=1)
    D["L_min"] = np.nanmin(L, axis=1)
    D["C_last"] = C[np.arange(nd), sess.n_rth.to_numpy() - 1]
    D["V_rth"] = np.nansum(V, axis=1)
    D["rth_bar_cov"] = has.sum(1) / sess.n_rth.to_numpy()
    # extended hours
    pre = m[(m["mod"] >= 4 * 60) & (m["mod"] < RTH_START)]
    g = pre.groupby("date")
    D["pm_open"] = g.o.first()
    D["pm_high"] = g.h.max()
    D["pm_low"] = g.l.min()
    D["pm_close"] = g.c.last()
    D["pm_vol"] = g.v.sum()
    D["pm_bars"] = g.v.size()
    endmod = sess.rth_end_mod.reindex(m.date).to_numpy()
    post = m[(m["mod"].to_numpy() >= endmod) & (m["mod"] < 20 * 60)]
    g = post.groupby("date")
    D["ah_high"] = g.h.max()
    D["ah_low"] = g.l.min()
    D["ah_close"] = g.c.last()
    D["ah_vol"] = g.v.sum()
    D["ah_bars"] = g.v.size()
    D.to_parquet(PANEL / f"{t}_daily.parquet")

    # ---------------- coverage / consistency
    inwin = (D.index >= "2022-01-01")
    Dw = D[inwin]
    cov = {
        "ticker": t,
        "days": int(inwin.sum()),
        "missing_daily_bar": int(Dw.C.isna().sum()),
        "median_rth_bar_coverage": float(Dw.rth_bar_cov.median()),
        "p1_rth_bar_coverage": float(Dw.rth_bar_cov.quantile(0.01)),
        "open_match_share": float((np.abs(Dw.O_min / Dw.O - 1) < 1e-6).mean()),
        "high_match_share": float((np.abs(Dw.H_min / Dw.H - 1) < 1e-6).mean()),
        "low_match_share": float((np.abs(Dw.L_min / Dw.L - 1) < 1e-6).mean()),
        "median_abs_close_vs_last_trade_bps": float((np.abs(Dw.C / Dw.C_last - 1) * 1e4).median()),
        "minute_rth_vol_share_of_daily_vol_median": float((Dw.V_rth / Dw.V_daily).median()),
        "ext_plus_rth_vol_share_of_daily_vol_median": float(((Dw.V_rth + Dw.pm_vol.fillna(0) + Dw.ah_vol.fillna(0)) / Dw.V_daily).median()),
        "median_unadj_close_secondary": float(Dw.C_unadj[Dw.period == "secondary"].median()),
        "median_unadj_close_primary": float(Dw.C_unadj[Dw.period == "primary"].median()),
        "min_unadj_close": float(Dw.C_unadj.min()),
        "max_unadj_close": float(Dw.C_unadj.max()),
        "n_dividend_exdates": int((Dw.div_factor < 1).sum()),
        "max_dividend_pct": float((1 - Dw.div_factor).max() * 100),
    }
    return cov


def main():
    sess = detect_sessions()
    sess.to_csv(PANEL / "sessions.csv")
    hd = sess[sess.is_half]
    save_csv(hd[["pm_am_vol_ratio", "weekday", "period"]], "half_days.csv")
    print("sessions:", len(sess), "half days:", list(hd.index))
    rows = []
    for t in MAIN:
        rows.append(build_ticker(t, sess))
        print(rows[-1], flush=True)
    save_csv(pd.DataFrame(rows).set_index("ticker"), "data_coverage.csv")


if __name__ == "__main__":
    main()
