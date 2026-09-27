"""Daily behavior tracker: one row per trading day per ticker, built from 1-minute bars.

Works on (a) the cached history and (b) a live/partial session fetched from the REST API
(minute aggregates + real-time snapshot). All fields for a partial day are "as of the last bar".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import api, config
from . import data as sdata
from .costs import load_halfspread_table


def _hhmm(m):
    return f"{int(m) // 60:02d}:{int(m) % 60:02d}" if pd.notna(m) else ""


def day_row(bars: pd.DataFrame, prev_close: float, atr_prev: float | None, n_rth_minutes: int = config.N_RTH,
            leverage: float | None = None, proxy_ret: float | None = None) -> dict:
    """Summarise one session. ``bars`` = that day's minute bars (any session, unadjusted or adjusted
    consistently with ``prev_close``); ``prev_close`` = prior OFFICIAL close."""
    end_min = config.RTH_START_MIN + n_rth_minutes
    rth = bars[(bars["mod"] >= config.RTH_START_MIN) & (bars["mod"] < end_min)].sort_values("t")
    pre = bars[bars["mod"] < config.RTH_START_MIN]
    if rth.empty:
        return {}
    o, h, l, c = rth["o"].iloc[0], rth["h"].max(), rth["l"].min(), rth["c"].iloc[-1]
    v = rth["v"].sum()
    vw = (rth["vw"].fillna(rth["c"]) * rth["v"]).cumsum() / rth["v"].cumsum().replace(0, np.nan)
    side = np.sign(rth["c"].to_numpy() - vw.to_numpy())
    side = side[side != 0]
    crosses = int(np.sum(side[1:] != side[:-1])) if side.size > 1 else 0
    tr = max(h, prev_close) - min(l, prev_close) if np.isfinite(prev_close) else h - l
    r1 = np.log(rth["c"]).diff().dropna()
    row = {
        "open": o, "high": h, "low": l, "last_rth_close": c, "prev_close": prev_close,
        "gap_pct": (o / prev_close - 1) * 100 if prev_close else np.nan,
        "range_pct": (h - l) / prev_close * 100 if prev_close else np.nan,
        "true_range_pct": tr / prev_close * 100 if prev_close else np.nan,
        "atr14_prev_pct": atr_prev / prev_close * 100 if (atr_prev and prev_close) else np.nan,
        "tr_over_atr": tr / atr_prev if atr_prev else np.nan,
        "ret_oc_pct": (c / o - 1) * 100, "ret_cc_pct": (c / prev_close - 1) * 100 if prev_close else np.nan,
        "close_location": (c - l) / (h - l) if h > l else np.nan,
        "vwap_close": float(vw.iloc[-1]), "close_vs_vwap_bps": (c / vw.iloc[-1] - 1) * 1e4,
        "vwap_crosses": crosses,
        "time_of_high": _hhmm(rth.loc[rth["h"].idxmax(), "mod"]), "time_of_low": _hhmm(rth.loc[rth["l"].idxmin(), "mod"]),
        "rth_volume": v, "rth_bars": len(rth), "pre_volume": pre["v"].sum(),
        "pre_high": pre["h"].max() if len(pre) else np.nan, "pre_low": pre["l"].min() if len(pre) else np.nan,
        "realized_vol_1m_ann_pct": float(r1.std() * np.sqrt(252 * 390) * 100) if len(r1) > 10 else np.nan,
    }
    for n in (5, 15, 30):
        f = rth[rth["mod"] < config.RTH_START_MIN + n]
        if len(f) and rth["mod"].max() >= config.RTH_START_MIN + n - 1:
            hi, lo = f["h"].max(), f["l"].min()
            row[f"or{n}_size_bps"] = (hi / lo - 1) * 1e4
            if n == 30:
                after = rth[rth["mod"] >= config.RTH_START_MIN + n]
                up = after[after["c"] > hi]
                dn = after[after["c"] < lo]
                tu = up["mod"].iloc[0] if len(up) else np.inf
                td = dn["mod"].iloc[0] if len(dn) else np.inf
                row["or30_first_break"] = "up" if tu < td else ("down" if td < tu else "none")
                row["or30_break_time"] = _hhmm(min(tu, td)) if np.isfinite(min(tu, td)) else ""
    body = abs(c - o) / (h - l) if h > l else 0.0
    row["trend_day"] = bool(body >= 0.6 and (row["tr_over_atr"] >= 1.0 if np.isfinite(row["tr_over_atr"]) else False))
    row["trend_dir"] = int(np.sign(c - o)) if row["trend_day"] else 0
    if leverage is not None and proxy_ret is not None and np.isfinite(proxy_ret):
        row["proxy_ret_pct"] = proxy_ret * 100
        row["implied_leverage_at_close"] = leverage * (1 + proxy_ret) / (1 + leverage * proxy_ret)
        row["tracking_gap_bps"] = (row["ret_cc_pct"] / 100 - leverage * proxy_ret) * 1e4
    return row


def build_history(tickers=config.TRADED, cal: pd.DataFrame | None = None, start=config.HISTORY_START,
                  end=config.HISTORY_END) -> pd.DataFrame:
    """Tracker rows for all cached days (unadjusted prices; prior close from the unadjusted daily bar
    with a split correction so gaps/ranges are not distorted on split dates)."""
    from .calendar import load_calendar
    cal = cal if cal is not None else load_calendar()
    cal = cal[(cal.index >= pd.Timestamp(start)) & (cal.index <= pd.Timestamp(end))]
    try:
        spread_tab, spread_src = load_halfspread_table()
    except FileNotFoundError:
        spread_tab, spread_src = None, ""
    out = []
    proxy_daily = {}
    for tk in tickers:
        bars = sdata.load_minute_bars(tk, False, start, end)
        da = sdata.load_daily(tk, True)
        du = sdata.load_daily(tk, False)
        fac = (du["c"] / da["c"])                                  # unadjusted / adjusted, per day
        prev_c_same_basis = (da["c"].shift(1) * fac)               # prior close expressed in today's share basis
        trd = np.maximum(da["h"], da["c"].shift(1)) - np.minimum(da["l"], da["c"].shift(1))
        atr_adj = trd.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean().shift(1)
        atr_same_basis = atr_adj * fac
        dv_rth = {}
        proxy = config.INDEX_PROXY.get(tk)
        if proxy and proxy not in proxy_daily:
            pdl = sdata.load_daily(proxy, True)["c"]
            proxy_daily[proxy] = pdl / pdl.shift(1) - 1
        for d, g in bars.groupby("date"):
            if d not in cal.index:
                continue
            row = day_row(g, prev_c_same_basis.get(d, np.nan), atr_same_basis.get(d, np.nan),
                          int(cal.loc[d, "n_rth_minutes"]), config.LEVERAGE.get(tk),
                          proxy_daily[proxy].get(d, np.nan) if proxy else None)
            if not row:
                continue
            row.update({"date": d, "ticker": tk, "official_close": du["c"].get(d, np.nan),
                        "daily_bar_volume": du["v"].get(d, np.nan), "is_half_day": bool(cal.loc[d, "is_half_day"])})
            if proxy is None:
                row.pop("proxy_ret_pct", None)
            dv_rth[d] = row["rth_volume"]
            out.append(row)
    df = pd.DataFrame(out).sort_values(["ticker", "date"]).reset_index(drop=True)
    df["ret_cc_pct"] = np.where(df["official_close"].notna(), (df["official_close"] / df["prev_close"] - 1) * 100,
                                df["ret_cc_pct"])
    df["rel_volume_20d"] = df.groupby("ticker")["rth_volume"].transform(
        lambda s: s / s.shift(1).rolling(20, min_periods=10).mean())
    # SOXL-SOXS divergence at the close
    if {"SOXL", "SOXS"} <= set(df["ticker"]):
        piv = df.pivot(index="date", columns="ticker", values="ret_cc_pct")
        div = (piv["SOXL"] + piv["SOXS"]) * 100
        df["soxl_soxs_div_close_bps"] = df["date"].map(div)
    if spread_tab is not None:
        rth_b = spread_tab[(spread_tab["b0"] >= config.RTH_START_MIN) & (spread_tab["b1"] <= config.RTH_END_MIN)]
        med = rth_b.groupby(["ticker", "year"])["median_spread_cents"].median()
        yrs = df["date"].dt.year
        df["spread_cents_model"] = [med.get((t, y), np.nan) for t, y in zip(df["ticker"], yrs)]
        df["half_spread_bps_at_close_model"] = df["spread_cents_model"] / 2 / 100 / df["last_rth_close"] * 1e4
        df.attrs["spread_source"] = spread_src
    return df


# --------------------------------------------------------------------------------------
# live / partial-session tracking via REST
# --------------------------------------------------------------------------------------
def live_rows(tickers=config.TRADED, day: str | None = None) -> pd.DataFrame:
    """Fetch today's (or ``day``'s) minute bars + the real-time snapshot and summarise so far."""
    day = day or pd.Timestamp.now(tz=config.TZ).strftime("%Y-%m-%d")
    snap = api.get("/v3/snapshot", {"ticker.any_of": ",".join(tickers)}).json().get("results", [])
    snap = {s["ticker"]: s for s in snap}
    rows = []
    for tk in tickers:
        b = sdata.fetch_aggs(tk, 1, "minute", day, day, adjusted=False)
        if b.empty:
            rows.append({"ticker": tk, "date": day, "note": "no bars for this date (market closed?)"})
            continue
        b = sdata.add_time_columns(b)
        prev = api.get(f"/v2/aggs/ticker/{tk}/range/1/day/{(pd.Timestamp(day) - pd.Timedelta(days=10)).date()}/"
                       f"{(pd.Timestamp(day) - pd.Timedelta(days=1)).date()}",
                       {"adjusted": "false", "sort": "desc", "limit": 1}).json().get("results", [])
        prev_close = prev[0]["c"] if prev else np.nan
        row = day_row(b, prev_close, None)
        s = snap.get(tk, {})
        q = s.get("last_quote") or {}
        if q.get("ask") and q.get("bid"):
            mid = (q["ask"] + q["bid"]) / 2
            row["snapshot_spread_cents"] = (q["ask"] - q["bid"]) * 100
            row["snapshot_half_spread_bps"] = (q["ask"] - q["bid"]) / 2 / mid * 1e4
            row["snapshot_quote_timeframe"] = q.get("timeframe")
        row["snapshot_last_trade"] = (s.get("last_trade") or {}).get("price")
        row["as_of_bar_et"] = b["ts"].max().strftime("%Y-%m-%d %H:%M")
        rows.append({"ticker": tk, "date": day, **row})
    return pd.DataFrame(rows)
