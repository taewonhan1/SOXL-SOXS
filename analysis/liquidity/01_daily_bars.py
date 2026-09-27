"""Step 1 - daily bars (adjusted + unadjusted), split history, activity summary.

Pulls /v2/aggs/ticker/{T}/range/1/day for all tickers 2022-01-01..2026-09-25
(SOXL/SOXS also from inception 2010-03-11), plus /v3/reference/splits.
Outputs (analysis/liquidity/output):
  splits_reference_vs_detected.csv, activity_summary.csv, price_levels.csv,
  monthly_dollar_volume.csv, soxl_soxs_annual_since_inception.csv, high_vol_days.csv
Cache (data/liquidity/daily/*.parquet).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import ALL, DATA, OUT, TICKERS, aggs, get_json

START, END = "2022-01-01", "2026-09-25"
D = DATA / "daily"
D.mkdir(parents=True, exist_ok=True)


def load(t: str, adjusted: bool, start: str = START) -> pd.DataFrame:
    f = D / f"{t}_{'adj' if adjusted else 'unadj'}_{start}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    df = aggs(t, 1, "day", start, END, adjusted)
    df["date"] = df["ts_et"].dt.strftime("%Y-%m-%d")
    df.to_parquet(f)
    return df


def main():
    frames = {}
    for t in ALL + ["MU"]:
        for adj in (True, False):
            frames[(t, adj)] = load(t, adj)
    for t in ["SOXL", "SOXS"]:
        for adj in (True, False):
            frames[(t, adj, "incep")] = load(t, adj, "2010-01-01")

    # ---- splits: reference vs detected from adjusted/unadjusted close ratio
    rows = []
    for t in ALL:
        ref = get_json("/v3/reference/splits", {"ticker": t, "limit": 1000}).get("results") or []
        for r in ref:
            rows.append(dict(ticker=t, source="reference", execution_date=r["execution_date"],
                             split_from=r["split_from"], split_to=r["split_to"],
                             kind="reverse" if r["split_from"] > r["split_to"] else "forward"))
        key = (t, True, "incep") if t in ("SOXL", "SOXS") else (t, True)
        key_u = (t, False, "incep") if t in ("SOXL", "SOXS") else (t, False)
        a, u = frames[key].set_index("date"), frames[key_u].set_index("date")
        fac = (u["c"] / a["c"]).dropna()
        chg = fac / fac.shift(1)
        for d, v in chg[(chg - 1).abs() > 0.05].items():
            i = fac.index.get_loc(d)
            prev_d = fac.index[i - 1]
            rows.append(dict(ticker=t, source="detected(unadj/adj close factor jump)", execution_date=d,
                             factor_change=round(float(v), 4),
                             unadj_close_prev=u.loc[prev_d, "c"], unadj_close_on=u.loc[d, "c"]))
    sp = pd.DataFrame(rows).sort_values(["ticker", "execution_date", "source"])
    sp.to_csv(OUT / "splits_reference_vs_detected.csv", index=False)

    # ---- activity summary (last 3/6/12 months to 2026-09-25)
    end = pd.Timestamp(END)
    periods = {"3m": end - pd.DateOffset(months=3), "6m": end - pd.DateOffset(months=6),
               "12m": end - pd.DateOffset(months=12)}
    summ, levels, monthly = [], [], []
    for t in ALL + ["MU"]:
        a = frames[(t, True)].copy()
        u = frames[(t, False)].copy()
        a["dt"] = pd.to_datetime(a["date"])
        u["dt"] = pd.to_datetime(u["date"])
        # dollar volume from UNADJUSTED vwap*volume (true dollars traded incl. ext hours)
        u["dollar_vol"] = u["vw"] * u["v"]
        m = u.merge(a[["date", "v", "c"]].rename(columns={"v": "v_adj", "c": "c_adj"}), on="date")
        last = m.iloc[-1]
        levels.append(dict(ticker=t, last_date=last["date"], close_unadj=last["c"], close_adj=last["c_adj"],
                           high_52w_adj=a[a.dt > end - pd.DateOffset(years=1)]["h"].max(),
                           low_52w_adj=a[a.dt > end - pd.DateOffset(years=1)]["l"].min(),
                           min_unadj_close_since_2022=u["c"].min(), max_unadj_close_since_2022=u["c"].max()))
        for p, st in periods.items():
            w = m[m.dt > st]
            summ.append(dict(ticker=t, period=p, start_excl=st.strftime("%Y-%m-%d"), end=END, n_days=len(w),
                             avg_shares_adj_current_basis=w["v_adj"].mean(),
                             median_shares_adj=w["v_adj"].median(),
                             avg_shares_unadj=w["v"].mean(),
                             avg_dollar_volume=w["dollar_vol"].mean(),
                             median_dollar_volume=w["dollar_vol"].median(),
                             avg_trades=w["n"].mean(), median_trades=w["n"].median(),
                             avg_trade_size_shares_unadj=(w["v"].sum() / w["n"].sum()),
                             avg_trade_dollars=(w["dollar_vol"].sum() / w["n"].sum()),
                             avg_close_unadj=w["c"].mean(),
                             avg_abs_ret_pct=(a[a.dt > st]["c"].pct_change().abs().mean() * 100),
                             avg_range_pct=((a[a.dt > st]["h"] / a[a.dt > st]["l"] - 1).mean() * 100)))
        mm = m.set_index("dt").resample("MS").agg({"dollar_vol": "mean", "v_adj": "mean", "n": "mean", "c": "last"})
        mm["ticker"] = t
        monthly.append(mm.reset_index())
    pd.DataFrame(summ).to_csv(OUT / "activity_summary.csv", index=False)
    pd.DataFrame(levels).to_csv(OUT / "price_levels.csv", index=False)
    mon = pd.concat(monthly)
    mon.to_csv(OUT / "monthly_dollar_volume.csv", index=False)

    # ---- SOXL/SOXS annual since inception
    ann = []
    for t in ["SOXL", "SOXS"]:
        u = frames[(t, False, "incep")].copy()
        a = frames[(t, True, "incep")].copy()
        u["year"] = u["date"].str[:4]
        u["dollar_vol"] = u["vw"] * u["v"]
        a["year"] = a["date"].str[:4]
        g = u.groupby("year").agg(avg_dollar_volume=("dollar_vol", "mean"), avg_trades=("n", "mean"),
                                  avg_shares_unadj=("v", "mean"), min_close_unadj=("c", "min"),
                                  max_close_unadj=("c", "max"), days=("c", "size"))
        ga = a.groupby("year").agg(avg_shares_adj=("v", "mean"), last_close_adj=("c", "last"))
        g = g.join(ga)
        g["ticker"] = t
        ann.append(g.reset_index())
    pd.concat(ann).to_csv(OUT / "soxl_soxs_annual_since_inception.csv", index=False)

    # ---- high-volatility days (last ~18 months) using SOXL adjusted bars
    a = frames[("SOXL", True)].copy()
    a["ret"] = a["c"].pct_change() * 100
    a["range"] = (a["h"] / a["l"] - 1) * 100
    a["gap"] = (a["o"] / a["c"].shift(1) - 1) * 100
    nv = frames[("NVDA", True)][["date", "o", "c"]].copy()
    nv["nvda_ret"] = nv["c"].pct_change() * 100
    nv["nvda_gap"] = (nv["o"] / nv["c"].shift(1) - 1) * 100
    mu = frames[("MU", True)][["date", "o", "c"]].copy()
    mu["mu_ret"] = mu["c"].pct_change() * 100
    mu["mu_gap"] = (mu["o"] / mu["c"].shift(1) - 1) * 100
    h = a.merge(nv[["date", "nvda_ret", "nvda_gap"]], on="date").merge(mu[["date", "mu_ret", "mu_gap"]], on="date")
    h = h[h["date"] >= "2025-03-01"][["date", "c", "ret", "range", "gap", "v", "n", "nvda_ret", "nvda_gap", "mu_ret", "mu_gap"]]
    h.sort_values("range", ascending=False).to_csv(OUT / "high_vol_days.csv", index=False)
    print(sp.to_string())
    print(pd.DataFrame(levels).to_string())
    print(pd.DataFrame(summ)[["ticker", "period", "n_days", "avg_shares_adj_current_basis", "avg_dollar_volume", "avg_trades", "avg_close_unadj"]].to_string())
    print(h.sort_values("range", ascending=False).head(30).to_string())


if __name__ == "__main__":
    main()
