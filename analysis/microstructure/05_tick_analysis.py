"""Step 5: microstructure statistics from the windowed tick data (step 2) and the full-day SOXL/SOXS data (step 3).

Main outputs (analysis/microstructure/output/):
  cost_model_halfspread.csv            backtest cost table (fixed schema; see README)
  cost_model_halfspread_detail.csv     same rows + sample sizes, p90, one-tick share, finer extended-hours strata
  quoted_spread_by_bucket.csv          time-weighted quoted spread by ticker x group x bucket (cents, bps, one-tick share, ...)
  depth_by_bucket.csv                  time-weighted NBBO bid/ask size (shares, $) by bucket
  quote_dynamics_by_bucket.csv         NBBO message rate, price-change rate, inside-quote persistence
  tick_constraint_summary.csv          relative tick, one-tick share, spread in ticks, sub-penny quote counts by ticker x year
  trade_size_oddlot.csv                trade-size distribution, odd-lot shares, off-exchange shares
  effective_spread.csv                 effective / realized spread and price impact (60 s, 300 s), Lee-Ready signed
  effective_spread_by_size.csv         effective spread by trade-size bucket (last 12 months)
  auctions_by_day.csv / auctions_summary.csv   opening/closing auction prints and their share of daily volume
  spread_to_vol.csv                    quoted spread / sd of 1-min and 5-min mid returns by bucket
  stress_vs_normal.csv                 stress days vs normal days (RTH aggregates)
  sample_day_summary.csv               per ticker-day RTH summary for every sampled day
  window_validation_fullday.csv        windowed estimates vs full-session truth (SOXL/SOXS)
  fullday_soxl_soxs_summary.csv        full-session stats for SOXL/SOXS (odd lots, auctions, eff spreads, ...)
  charts: spread_by_time_of_day.png, depth_by_time_of_day.png, spread_to_vol.png, stress_vs_normal.png,
          fullday_spread_profile.png
Usage: python3 05_tick_analysis.py [--cost-only]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from ms_common import (COST_TICKERS, CONTEXT_GRAY, DATA, ET, FOCUS_COLORS, OUT, TEXT_SECONDARY, TICKERS,  # noqa: E402
                       focus_lines, hhmm_to_min, min_to_hhmm, sample_days, style_ax, unpack_conds)

TICK = DATA / "tick"
FD = DATA / "fullday"
BARS = DATA / "bars"
NS = 1e9
DUR_EDGES_US = np.concatenate([[0.0], np.logspace(0, 9, 91)])
PRIMARY = {"SOXL": 11, "SOXS": 11, "SPY": 11, "SOXX": 12, "SMH": 12, "NVDA": 12, "TQQQ": 12, "SQQQ": 12, "QQQ": 12}
PRE_STRATA = [(240, 420), (420, 480), (480, 540), (540, 570)]
POST_STRATA = [(960, 1020), (1020, 1080), (1080, 1200)]
RTH_BUCKETS = [(570 + 30 * i, 600 + 30 * i) for i in range(13)]
# trade conditions excluded from effective-spread / trade-flow calculations (not regular continuous-market prints)
EXCL_EFF = {2, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 25, 28, 29, 32, 33, 38, 52, 53, 55}
NO_VOLUME = {15, 16, 38}  # official open/close and corrected close: do not update consolidated volume
OPEN_CODES = {17, 25}   # Market Center Opening Trade (CTA 'O') / Opening Prints (UTP 'O')
CLOSE_CODES = {8, 19}   # Closing Prints (UTP '6') / Market Center Closing Trade (CTA '6')
LAST12_START, NORMAL18_START = "2025-09-26", "2025-03-25"
CURRENT_START = "2026-07-15"  # SOXS 1-for-10 reverse split; "current regime" group = normal days on/after this date


# ------------------------------------------------------------------ helpers
def wquantile(v, w, qs):
    v = np.asarray(v, float); w = np.asarray(w, float)
    m = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v, w = v[m], w[m]
    if len(v) == 0:
        return [np.nan] * len(qs)
    o = np.argsort(v, kind="stable")
    v, w = v[o], w[o]
    cw = np.cumsum(w)
    return [float(v[min(np.searchsorted(cw, q * cw[-1], side="left"), len(v) - 1)]) for q in qs]


def hist_quantiles(counts, qs, weights_by_dur=False):
    """Quantiles (ms) of a duration histogram on DUR_EDGES_US bins (log-interpolated within a bin)."""
    counts = np.asarray(counts, float)
    lo, hi = DUR_EDGES_US[:-1].copy(), DUR_EDGES_US[1:]
    lo[0] = 0.1
    mids = np.sqrt(lo * hi)
    w = counts * mids if weights_by_dur else counts
    if w.sum() <= 0:
        return [np.nan] * len(qs)
    cw = np.cumsum(w) / w.sum()
    out = []
    for q in qs:
        i = int(np.searchsorted(cw, q))
        prev = cw[i - 1] if i > 0 else 0.0
        f = (q - prev) / max(cw[i] - prev, 1e-12)
        out.append(float(np.exp(np.log(lo[i]) + f * (np.log(hi[i]) - np.log(lo[i]))) / 1000.0))
    return out


def conds_has_any(packed: np.ndarray, codes: set) -> np.ndarray:
    c = np.asarray(packed, dtype=np.int64)
    out = np.zeros(len(c), dtype=bool)
    for i in range(7):
        out |= np.isin((c >> (8 * i)) & 0xFF, list(codes))
    return out


def has_code(packed, code):
    return conds_has_any(packed, {code})


SD = sample_days()
CAT = dict(zip(SD.day, SD.category))


def groups_for(day: str) -> list[str]:
    cat = CAT[day]
    g = []
    if cat in ("normal", "recent"):
        g.append(f"y{day[:4]}")
        if day >= LAST12_START:
            g.append("last12m")
        if day >= NORMAL18_START:
            g.append("normal18m")
        if day >= CURRENT_START:
            g.append("since_2026-07-15")
    else:
        g.append("stress")
    if cat == "recent":
        g.append("last5")
    return g


def bucket_of(kind, s0, s1):
    return (int(s0), int(s1))


def daily_bars(T):
    d = pd.read_parquet(BARS / f"{T}_day_raw.parquet").set_index("date")
    a = pd.read_parquet(BARS / f"{T}_day_adj.parquet").set_index("date")
    d["ret_adj"] = a["c"].pct_change() * 100
    d["range_pct"] = (d["h"] / d["l"] - 1) * 100
    return d


# ------------------------------------------------------------------ loading
def load_ticker(T, with_trades=True, with_snap=True):
    Q, H, D, S, TR, W = [], [], [], [], [], []
    for day in SD.day:
        f = TICK / T / f"{day}_wmeta.parquet"
        if not f.exists():
            continue
        w = pd.read_parquet(f); w["day"] = day; W.append(w)
        q = pd.read_parquet(TICK / T / f"{day}_qstats.parquet"); q["day"] = day; Q.append(q)
        h = pd.read_parquet(TICK / T / f"{day}_shist.parquet")
        if len(h):
            h["day"] = day; H.append(h)
        dd = pd.read_parquet(TICK / T / f"{day}_dhist.parquet")
        if len(dd):
            dd["day"] = day; D.append(dd)
        if with_snap:
            s = pd.read_parquet(TICK / T / f"{day}_snap.parquet")
            if len(s):
                s["day"] = day; S.append(s)
        if with_trades:
            t = pd.read_parquet(TICK / T / f"{day}_trades.parquet")
            if len(t):
                t["day"] = day; TR.append(t)
    cat = lambda L: pd.concat(L, ignore_index=True) if L else pd.DataFrame()  # noqa: E731
    Q, H, D, S, TR, W = cat(Q), cat(H), cat(D), cat(S), cat(TR), cat(W)
    if len(H):
        H = H.merge(Q[["day", "wid", "sub_start", "kind", "stratum_start", "stratum_end"]], on=["day", "wid", "sub_start"], how="left")
    if len(D):
        D = D.merge(Q[["day", "wid", "sub_start", "kind", "stratum_start", "stratum_end"]], on=["day", "wid", "sub_start"], how="left")
    if len(S):
        S = S.merge(W[["day", "wid", "kind", "stratum_start", "stratum_end", "q0"]], on=["day", "wid"], how="left")
    if len(TR):
        TR = TR.merge(W[["day", "wid", "kind", "stratum_start", "stratum_end"]], on=["day", "wid"], how="left")
    return Q, H, D, S, TR, W


def explode_groups(df):
    """Duplicate rows for every analysis group the day belongs to (column 'group')."""
    if not len(df):
        return df
    gmap = {d: groups_for(d) for d in df["day"].unique()}
    parts = []
    for gname in sorted({g for v in gmap.values() for g in v}):
        days = [d for d, v in gmap.items() if gname in v]
        p = df[df["day"].isin(days)].copy()
        p["group"] = gname
        parts.append(p)
    return pd.concat(parts, ignore_index=True)


# ------------------------------------------------------------------ quoted spreads
def spread_cells(H, strata_len_weight=False):
    """Return value arrays and weights for pooled time-weighted quantiles.
    If strata_len_weight: weight each stratum by its length / sampled time (stratified estimator)."""
    cents = H["k_halfc"].to_numpy() * 0.5
    bps = (H["time_x_bps"] / H["time_s"]).to_numpy()
    w = H["time_s"].to_numpy().astype(float)
    if strata_len_weight:
        L = (H["stratum_end"] - H["stratum_start"]).to_numpy().astype(float)
        samp = H.groupby(["stratum_start"])["time_s"].transform("sum").to_numpy()
        w = w * L / samp
    return cents, bps, w, H["k_halfc"].to_numpy()


def spread_summary(H, strat=False):
    if not len(H):
        return {}
    cents, bps, w, k = spread_cells(H, strat)
    W = w.sum()
    med_c, p90_c = wquantile(cents, w, [0.5, 0.9])
    med_b, p90_b = wquantile(bps, w, [0.5, 0.9])
    return {"tw_mean_spread_cents": float((cents * w).sum() / W), "tw_median_spread_cents": med_c,
            "tw_p90_spread_cents": p90_c, "tw_mean_spread_bps": float((bps * w).sum() / W),
            "tw_median_spread_bps": med_b, "tw_p90_spread_bps": p90_b,
            "tw_mean_spread_ticks": float((k * 0.5 * w).sum() / W),
            "share_time_one_tick": float(w[k == 2].sum() / W), "share_time_two_ticks": float(w[k == 4].sum() / W),
            "share_time_ge5_ticks": float(w[k >= 10].sum() / W),
            "share_time_halfpenny_spread": float(w[k % 2 == 1].sum() / W)}


def quote_summary(Q):
    T = Q["T_total"].sum()
    Tp = Q["T_pos"].sum()
    two = Q["T_twosided"].sum()
    r = {"n_days": Q["day"].nunique(), "n_subwindows": len(Q), "sampled_seconds": T,
         "n_quote_msgs": int(Q["n_msg"].sum()), "share_time_twosided": two / T if T else np.nan,
         "share_twosided_time_locked": Q["T_locked"].sum() / two if two else np.nan,
         "share_twosided_time_crossed": Q["T_crossed"].sum() / two if two else np.nan,
         "msgs_per_sec": Q["n_msg"].sum() / T, "px_changes_per_sec": Q["n_px_chg"].sum() / T,
         "bid_px_changes_per_sec": Q["n_bid_px_chg"].sum() / T, "ask_px_changes_per_sec": Q["n_ask_px_chg"].sum() / T,
         "n_subpenny_quotes": int(Q["n_subpenny_quotes"].sum()), "n_luld_quotes": int(Q["n_luld_quotes"].sum())}
    if Tp > 0:
        for c in ("bsz", "asz", "bdol", "adol"):
            r[f"tw_mean_{c}"] = float((Q[f"tw_mean_{c}"].fillna(0) * Q["T_pos"]).sum() / Tp)
            r[f"median_of_window_tw_median_{c}"] = float(Q[f"tw_med_{c}"].median())
        r["tw_mid"] = float((Q["tw_mid"].fillna(0) * Q["T_pos"]).sum() / Tp)
    return r


def by_bucket(Q, H, D, group_col="group"):
    rows = []
    specs = [("rth", b) for b in RTH_BUCKETS] + [("open5", (570, 575)), ("close5", (955, 960))] + \
            [("pre", b) for b in PRE_STRATA] + [("post", b) for b in POST_STRATA] + \
            [("pre", (240, 570)), ("post", (960, 1200)), ("rth", (570, 960))]
    for g in sorted(Q[group_col].unique()):
        q_g, h_g, d_g = Q[Q[group_col] == g], H[H[group_col] == g], D[D[group_col] == g]
        for kind, (b0, b1) in specs:
            selq = (q_g.kind == kind) & (q_g.stratum_start >= b0) & (q_g.stratum_end <= b1)
            selh = (h_g.kind == kind) & (h_g.stratum_start >= b0) & (h_g.stratum_end <= b1)
            seld = (d_g.kind == kind) & (d_g.stratum_start >= b0) & (d_g.stratum_end <= b1)
            if not selq.any():
                continue
            multi = kind in ("pre", "post") and (b1 - b0) > 180 or (kind == "rth" and b1 - b0 > 30)
            r = {"group": g, "session": kind, "bucket_start_et": min_to_hhmm(b0), "bucket_end_et": min_to_hhmm(b1)}
            r.update(quote_summary(q_g[selq]))
            r.update(spread_summary(h_g[selh], strat=multi and kind in ("pre", "post")))
            cnt = d_g[seld].groupby("bin")["count"].sum().reindex(range(len(DUR_EDGES_US) - 1), fill_value=0).to_numpy()
            p10, p50, p90 = hist_quantiles(cnt, [0.1, 0.5, 0.9])
            (tw50,) = hist_quantiles(cnt, [0.5], weights_by_dur=True)
            r.update({"n_price_states": int(cnt.sum()), "state_dur_p10_ms": p10, "state_dur_median_ms": p50,
                      "state_dur_p90_ms": p90, "state_dur_timeweighted_median_ms": tw50,
                      "share_states_lt_1ms": float(cnt[:31].sum() / cnt.sum()) if cnt.sum() else np.nan})
            rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ trades
def prep_trades(TR, T):
    tr = TR
    et = pd.to_datetime(tr["t"], unit="ns", utc=True).dt.tz_convert(ET)
    tr["minute"] = (et.dt.hour * 60 + et.dt.minute + et.dt.second / 60).astype(float)
    tr["novol"] = conds_has_any(tr["cond"].to_numpy(), NO_VOLUME)
    tr["excl"] = conds_has_any(tr["cond"].to_numpy(), EXCL_EFF)
    tr["odd_flag"] = has_code(tr["cond"].to_numpy(), 37)
    tr["mid"] = (tr["bid"] + tr["ask"]) / 2
    tr["qspr"] = tr["ask"] - tr["bid"]
    validq = (tr["bid"] > 0) & (tr["ask"] > 0) & (tr["qspr"] >= -1e-9)
    tr["elig"] = (~tr["excl"]) & (~tr["novol"]) & validq & tr["kind"].isin(["rth", "open5", "close5"]) & \
                 (tr["minute"] >= 570) & (tr["minute"] < 960) & (tr["price"] > 0) & (tr["size"] > 0)
    # quote rule
    diff = tr["price"] - tr["mid"]
    qs = np.sign(np.where(np.abs(diff) < 1e-9, 0.0, diff))
    # tick test within (day, wid) over eligible trades
    tr = tr.sort_values(["day", "wid", "t"], kind="stable")
    e = tr[tr["elig"]]
    dp = e.groupby(["day", "wid"])["price"].diff()
    ts = np.sign(dp.where(dp.abs() > 1e-9))
    ts = ts.groupby([e["day"], e["wid"]]).ffill()
    tr["tick_sign"] = np.nan
    tr.loc[e.index, "tick_sign"] = ts
    tr["quote_sign"] = pd.Series(qs, index=TR.index).reindex(tr.index)
    tr["lr_sign"] = np.where(tr["quote_sign"] != 0, tr["quote_sign"], tr["tick_sign"])
    m = tr["mid"]
    tr["eff_bps"] = 2 * (tr["price"] - m).abs() / m * 1e4
    tr["eff_cents"] = 2 * (tr["price"] - m).abs() * 100
    tr["eff_signed_bps"] = 2 * tr["lr_sign"] * (tr["price"] - m) / m * 1e4
    for h in ("60", "300"):
        tr[f"rs{h}_bps"] = 2 * tr["lr_sign"] * (tr["price"] - tr[f"mid{h}"]) / m * 1e4
        tr[f"pi{h}_bps"] = 2 * tr["lr_sign"] * (tr[f"mid{h}"] - m) / m * 1e4
    tr["dollars"] = tr["price"] * tr["size"]
    tr["at_mid"] = (tr["price"] - m).abs() < 1e-6
    tr["at_quote"] = ((tr["price"] - tr["bid"]).abs() < 1e-6) | ((tr["price"] - tr["ask"]).abs() < 1e-6)
    tr["outside"] = (tr["price"] < tr["bid"] - 1e-6) | (tr["price"] > tr["ask"] + 1e-6)
    tr["inside"] = ~tr["at_mid"] & ~tr["at_quote"] & ~tr["outside"]
    tr["trf"] = tr["ex"] == 4
    tr["subpenny_px"] = (np.abs(tr["price"] * 100 - np.rint(tr["price"] * 100)) > 1e-6)
    return tr


SIZE_BUCKETS = [(0, 1, "<1 (fractional)"), (1, 100, "1-99"), (100, 101, "100"), (101, 500, "101-499"),
                (500, 1000, "500-999"), (1000, 5000, "1000-4999"), (5000, 10000, "5000-9999"), (10000, 1e12, ">=10000")]


def trade_size_stats(tr, label):
    x = tr[(~tr["novol"]) & (tr["size"] > 0)]
    if not len(x):
        return {}
    n, v, dv = len(x), x["size"].sum(), x["dollars"].sum()
    r = {"sample": label, "n_trades": n, "shares": v, "dollars": dv,
         "share_trades_oddlot_flag37": x["odd_flag"].mean(), "share_volume_oddlot_flag37": x.loc[x.odd_flag, "size"].sum() / v,
         "share_trades_lt100sh": (x["size"] < 100).mean(), "share_volume_lt100sh": x.loc[x["size"] < 100, "size"].sum() / v,
         "share_trades_fractional": (x["size"] < 1).mean(),
         "share_trades_offexchange_trf": x["trf"].mean(), "share_volume_offexchange_trf": x.loc[x.trf, "size"].sum() / v,
         "share_trades_subpenny_price": x["subpenny_px"].mean(),
         "share_trades_iso_flag14": has_code(x["cond"].to_numpy(), 14).mean(),
         "mean_size_sh": x["size"].mean(), "median_size_sh": x["size"].median(),
         "p90_size_sh": x["size"].quantile(0.9), "p99_size_sh": x["size"].quantile(0.99),
         "volume_weighted_median_size_sh": wquantile(x["size"].to_numpy(), x["size"].to_numpy(), [0.5])[0],
         "mean_size_usd": x["dollars"].mean(), "median_size_usd": x["dollars"].median()}
    for lo, hi, lab in SIZE_BUCKETS:
        s = (x["size"] >= lo) & (x["size"] < hi)
        r[f"trades_{lab}"] = s.mean()
        r[f"volume_{lab}"] = x.loc[s, "size"].sum() / v
    return r


def eff_stats(e):
    """e = eligible trades. Trade-weighted and dollar-weighted effective/realized/impact (bps) and cents."""
    if not len(e):
        return {}
    w = e["dollars"]
    r = {"n_trades": len(e), "dollars": w.sum(),
         "eff_bps_tw": e["eff_bps"].mean(), "eff_bps_dw": np.average(e["eff_bps"], weights=w),
         "eff_bps_median": e["eff_bps"].median(),
         "eff_cents_tw": e["eff_cents"].mean(), "eff_cents_dw": np.average(e["eff_cents"], weights=w),
         "quoted_bps_at_trade_tw": (e["qspr"] / e["mid"] * 1e4).mean(),
         "quoted_bps_at_trade_dw": np.average(e["qspr"] / e["mid"] * 1e4, weights=w),
         "eff_over_quoted_dw": np.average(e["eff_bps"], weights=w) / np.average(e["qspr"] / e["mid"] * 1e4, weights=w),
         "share_at_mid": e["at_mid"].mean(), "share_inside_not_mid": e["inside"].mean(),
         "share_at_quote": e["at_quote"].mean(), "share_outside": e["outside"].mean(),
         "share_signed_by_quote_rule": (e["quote_sign"] != 0).mean(),
         "share_signed_lee_ready": e["lr_sign"].notna().mean(),
         "share_buys_lee_ready": (e["lr_sign"] > 0).sum() / max(e["lr_sign"].notna().sum(), 1),
         "share_trf": e["trf"].mean()}
    for h in ("60", "300"):
        x = e[e[f"rs{h}_bps"].notna()]
        if len(x):
            ww = x["dollars"]
            r.update({f"n_{h}s": len(x), f"eff_signed_bps_dw_{h}s_sample": np.average(x["eff_signed_bps"], weights=ww),
                      f"realized_bps_tw_{h}s": x[f"rs{h}_bps"].mean(), f"realized_bps_dw_{h}s": np.average(x[f"rs{h}_bps"], weights=ww),
                      f"impact_bps_tw_{h}s": x[f"pi{h}_bps"].mean(), f"impact_bps_dw_{h}s": np.average(x[f"pi{h}_bps"], weights=ww)})
    return r


# ------------------------------------------------------------------ cost table
def cost_rows(T, Q, H):
    rows, drows = [], []
    for g in sorted(G for G in H["group"].unique() if G.startswith("y")):
        yr = int(g[1:])
        hg, qg = H[H.group == g], Q[Q.group == g]
        specs = [("rth", b) for b in RTH_BUCKETS] + [("pre", (240, 570)), ("post", (960, 1200))] + \
                [("pre", b) for b in PRE_STRATA] + [("post", b) for b in POST_STRATA]
        for kind, (b0, b1) in specs:
            sh = hg[(hg.kind == kind) & (hg.stratum_start >= b0) & (hg.stratum_end <= b1)]
            sq = qg[(qg.kind == kind) & (qg.stratum_start >= b0) & (qg.stratum_end <= b1)]
            if not len(sh):
                continue
            strat = kind in ("pre", "post") and (b1 - b0) > 180
            cents, bps, w, k = spread_cells(sh, strat)
            W = w.sum()
            hs = bps / 2
            row = {"ticker": T, "year": yr, "bucket_start_et": min_to_hhmm(b0), "bucket_end_et": min_to_hhmm(b1),
                   "median_spread_cents": round(wquantile(cents, w, [0.5])[0], 4),
                   "mean_spread_cents": round(float((cents * w).sum() / W), 4),
                   "median_half_spread_bps": round(wquantile(hs, w, [0.5])[0], 4),
                   "mean_half_spread_bps": round(float((hs * w).sum() / W), 4),
                   "n_obs": int(sq["n_msg"].sum())}
            det = dict(row)
            det.update({"session": kind, "n_days": sq["day"].nunique(), "n_5min_subwindows": len(sq),
                        "sampled_seconds_with_positive_spread": round(float(sh["time_s"].sum()), 1),
                        "p90_spread_cents": wquantile(cents, w, [0.9])[0], "p90_half_spread_bps": wquantile(hs, w, [0.9])[0],
                        "share_time_one_tick": float(w[k == 2].sum() / W),
                        "share_twosided_time_locked_or_crossed": float((sq["T_locked"].sum() + sq["T_crossed"].sum()) / max(sq["T_twosided"].sum(), 1e-9)),
                        "stratified_extended_hours": strat,
                        "days": ";".join(sorted(sq["day"].unique()))})
            drows.append(det)
            if not (kind in ("pre", "post") and (b1 - b0) <= 180):
                rows.append(row)
    return rows, drows


# ------------------------------------------------------------------ main
def main(cost_only=False):
    SPREAD, DEPTH, DYN, TICKC, SIZE, EFF, EFFSZ, AUC, S2V, STRESS, DAYSUM = ([] for _ in range(11))
    cost, cost_det = [], []
    for T in TICKERS:
        Q, H, D, S, TR, W = load_ticker(T, with_trades=not cost_only, with_snap=not cost_only)
        if not len(Q):
            continue
        Qg, Hg, Dg = explode_groups(Q), explode_groups(H), explode_groups(D)
        if T in COST_TICKERS:
            r, d = cost_rows(T, Qg, Hg)
            cost += r; cost_det += d
        if cost_only:
            continue
        bb = by_bucket(Qg, Hg, Dg)
        bb.insert(0, "ticker", T)
        SPREAD.append(bb)
        # tick-constraint summary by year group (RTH pooled)
        for g in sorted(Qg.group.unique()):
            q = Qg[(Qg.group == g) & (Qg.kind == "rth")]
            h = Hg[(Hg.group == g) & (Hg.kind == "rth")]
            if not len(q):
                continue
            ss = spread_summary(h)
            TICKC.append({"ticker": T, "group": g, "n_days": q.day.nunique(), "tw_mid_price": quote_summary(q).get("tw_mid"),
                          "rel_tick_bps": 1e4 * 0.01 / quote_summary(q).get("tw_mid", np.nan),
                          "tw_mean_spread_cents": ss.get("tw_mean_spread_cents"), "tw_mean_spread_ticks": ss.get("tw_mean_spread_ticks"),
                          "tw_median_spread_cents": ss.get("tw_median_spread_cents"),
                          "tw_mean_spread_bps": ss.get("tw_mean_spread_bps"),
                          "share_time_one_tick": ss.get("share_time_one_tick"), "share_time_ge5_ticks": ss.get("share_time_ge5_ticks"),
                          "share_time_halfpenny_spread_all_sessions": spread_summary(Hg[Hg.group == g]).get("share_time_halfpenny_spread"),
                          "n_subpenny_quotes_all_sessions": int(Qg[Qg.group == g]["n_subpenny_quotes"].sum()),
                          "n_quote_msgs_all_sessions": int(Qg[Qg.group == g]["n_msg"].sum())})
        # trades
        tr = prep_trades(TR, T)
        gdays = {}
        for d in tr.day.unique():
            for gname in groups_for(d):
                gdays.setdefault(gname, []).append(d)
        flow = {}
        for g in sorted(gdays):
            x = tr[tr.day.isin(gdays[g])]
            xr = x[(x.kind == "rth") & ~x.novol & (x.minute >= 570) & (x.minute < 960)]
            n_win = x[x.kind == "rth"].groupby(["day", "wid"]).ngroups
            secs = n_win * 300.0
            flow[g] = {"rth_shares_per_sec": xr["size"].sum() / secs if secs else np.nan,
                       "rth_trades_per_sec": len(xr) / secs if secs else np.nan,
                       "rth_dollars_per_sec": xr["dollars"].sum() / secs if secs else np.nan}
            for lab, sel in (("RTH rotating windows", (x.kind == "rth") & (x.minute >= 570) & (x.minute < 960)),
                             ("pre-market windows", x.kind == "pre"), ("after-hours windows", x.kind == "post")):
                r = trade_size_stats(x[sel], lab)
                if r:
                    r.update({"ticker": T, "group": g}); SIZE.append(r)
            e = x[x.elig]
            for (lab, b0, b1) in [("RTH all", 570, 960)] + [(f"{min_to_hhmm(a)}-{min_to_hhmm(b)}", a, b) for a, b in RTH_BUCKETS] + \
                                 [("open 09:30-09:35 (fixed)", 570, 575), ("close 15:55-16:00 (fixed)", 955, 960)]:
                if lab.startswith("open") or lab.startswith("close"):
                    sel = e.kind.isin(["open5" if lab.startswith("open") else "close5"])
                elif lab == "RTH all":
                    sel = e.kind == "rth"
                else:
                    sel = (e.kind == "rth") & (e.stratum_start == b0)
                for venue, vs in (("all", pd.Series(True, index=e.index)), ("lit", ~e.trf), ("offexchange_TRF", e.trf)):
                    if venue != "all" and lab != "RTH all":
                        continue
                    r = eff_stats(e[sel & vs])
                    if r:
                        r.update({"ticker": T, "group": g, "bucket": lab, "venue": venue}); EFF.append(r)
            if g in ("last12m", "stress", "normal18m", "since_2026-07-15"):
                er = e[e.kind == "rth"]
                for lo, hi, lab in SIZE_BUCKETS:
                    r = eff_stats(er[(er["size"] >= lo) & (er["size"] < hi)])
                    if r:
                        r.update({"ticker": T, "group": g, "size_bucket": lab}); EFFSZ.append(r)
            del x, e
        for r in TICKC:
            if r["ticker"] == T and r["group"] in flow:
                r.update(flow[r["group"]])
                bs = Qg[(Qg.group == r["group"]) & (Qg.kind == "rth")]
                tp = bs["T_pos"].sum()
                mb = float((bs["tw_mean_bsz"].fillna(0) * bs["T_pos"]).sum() / tp) if tp else np.nan
                ma = float((bs["tw_mean_asz"].fillna(0) * bs["T_pos"]).sum() / tp) if tp else np.nan
                r["tw_mean_bid_size_sh"], r["tw_mean_ask_size_sh"] = mb, ma
                r["queue_turnover_sec_bid"] = mb / r["rth_shares_per_sec"] if r["rth_shares_per_sec"] else np.nan
        # auctions
        dbar = daily_bars(T)
        for day in sorted(tr.day.unique()):
            x = tr[(tr.day == day) & (tr.ex == PRIMARY[T])]
            op = x[(x.kind == "open5") & conds_has_any(x["cond"].to_numpy(), OPEN_CODES) & ~x.novol]
            cl = x[(x.kind == "cauc") & conds_has_any(x["cond"].to_numpy(), CLOSE_CODES) & ~x.novol]
            v = dbar.loc[day, "v"] if day in dbar.index else np.nan
            AUC.append({"ticker": T, "day": day, "category": CAT[day], "open_auction_shares": op["size"].sum() if len(op) else np.nan,
                        "open_auction_price": op["price"].iloc[0] if len(op) else np.nan, "n_open_prints": len(op),
                        "open_print_time_et": pd.Timestamp(int(op["t"].iloc[0]), unit="ns", tz="UTC").tz_convert(ET).strftime("%H:%M:%S.%f") if len(op) else "",
                        "close_auction_shares": cl["size"].sum() if len(cl) else np.nan,
                        "close_auction_price": cl["price"].iloc[0] if len(cl) else np.nan, "n_close_prints": len(cl),
                        "close_print_time_et": pd.Timestamp(int(cl["t"].iloc[0]), unit="ns", tz="UTC").tz_convert(ET).strftime("%H:%M:%S.%f") if len(cl) else "",
                        "daily_volume": v, "open_share_of_daily_volume": (op["size"].sum() / v) if len(op) else np.nan,
                        "close_share_of_daily_volume": (cl["size"].sum() / v) if len(cl) else np.nan,
                        "open_auction_dollars": (op["size"] * op["price"]).sum() if len(op) else np.nan,
                        "close_auction_dollars": (cl["size"] * cl["price"]).sum() if len(cl) else np.nan})
        # spread-to-volatility from 1-second NBBO snapshots in the 10-minute RTH windows
        s = S[S.kind == "rth"].copy()
        s["mid"] = np.where((s.bid > 0) & (s.ask > 0) & (s.ask >= s.bid), (s.bid + s.ask) / 2, np.nan)
        s = s.sort_values(["day", "wid", "sec"])
        s1 = s[s.sec % 60 == 0].copy()
        s1["lm"] = np.log(s1["mid"])
        s1["r1"] = s1.groupby(["day", "wid"])["lm"].diff() * 1e4
        s5 = s[s.sec % 300 == 0].copy()
        s5["lm"] = np.log(s5["mid"])
        s5["r5"] = s5.groupby(["day", "wid"])["lm"].diff() * 1e4
        r1_raw = s1[["day", "wid", "stratum_start", "r1"]].dropna()
        r1 = explode_groups(r1_raw)
        r5 = explode_groups(s5[["day", "wid", "stratum_start", "r5"]].dropna())
        for g in sorted(set(r1.group.unique())):
            for (b0, b1) in RTH_BUCKETS + [(570, 960)]:
                a1 = r1[(r1.group == g) & (r1.stratum_start >= b0) & (r1.stratum_start < b1)]["r1"]
                a5 = r5[(r5.group == g) & (r5.stratum_start >= b0) & (r5.stratum_start < b1)]["r5"]
                h = Hg[(Hg.group == g) & (Hg.kind == "rth") & (Hg.stratum_start >= b0) & (Hg.stratum_start < b1)]
                ss = spread_summary(h)
                if not len(a1) or not ss:
                    continue
                S2V.append({"ticker": T, "group": g, "bucket_start_et": min_to_hhmm(b0), "bucket_end_et": min_to_hhmm(b1),
                            "tw_mean_spread_bps": ss["tw_mean_spread_bps"], "sd_mid_ret_1m_bps": a1.std(), "n_1m": len(a1),
                            "sd_mid_ret_5m_bps": a5.std() if len(a5) > 2 else np.nan, "n_5m": len(a5),
                            "spread_over_sd1m": ss["tw_mean_spread_bps"] / a1.std(),
                            "spread_over_sd5m": ss["tw_mean_spread_bps"] / a5.std() if len(a5) > 2 else np.nan})
        # per-day RTH summary (all sample days) incl. stress
        for day in sorted(Q.day.unique()):
            q = Q[(Q.day == day) & (Q.kind == "rth")]
            h = H[(H.day == day) & (H.kind == "rth")]
            e = tr[(tr.day == day) & tr.elig & (tr.kind == "rth")]
            a1 = r1_raw[r1_raw.day == day]["r1"]
            qs_ = quote_summary(q); ss = spread_summary(h); es = eff_stats(e)
            DAYSUM.append({"ticker": T, "day": day, "category": CAT[day],
                           "daily_ret_pct": dbar.loc[day, "ret_adj"] if day in dbar.index else np.nan,
                           "daily_range_pct": dbar.loc[day, "range_pct"] if day in dbar.index else np.nan,
                           "daily_volume": dbar.loc[day, "v"] if day in dbar.index else np.nan,
                           "daily_dollar_volume": dbar.loc[day, "v"] * dbar.loc[day, "vw"] if day in dbar.index else np.nan,
                           "close_unadj": dbar.loc[day, "c"] if day in dbar.index else np.nan,
                           "tw_mean_spread_cents": ss.get("tw_mean_spread_cents"), "tw_median_spread_cents": ss.get("tw_median_spread_cents"),
                           "tw_mean_spread_bps": ss.get("tw_mean_spread_bps"), "tw_p90_spread_bps": ss.get("tw_p90_spread_bps"),
                           "share_time_one_tick": ss.get("share_time_one_tick"),
                           "tw_mean_bid_usd": qs_.get("tw_mean_bdol"), "tw_mean_ask_usd": qs_.get("tw_mean_adol"),
                           "tw_mean_bid_sh": qs_.get("tw_mean_bsz"), "tw_mean_ask_sh": qs_.get("tw_mean_asz"),
                           "msgs_per_sec": qs_.get("msgs_per_sec"), "px_changes_per_sec": qs_.get("px_changes_per_sec"),
                           "n_luld_quotes": qs_.get("n_luld_quotes"),
                           "eff_bps_dw": es.get("eff_bps_dw"), "realized_bps_dw_300s": es.get("realized_bps_dw_300s"),
                           "impact_bps_dw_300s": es.get("impact_bps_dw_300s"), "sd_mid_ret_1m_bps": a1.std() if len(a1) else np.nan,
                           "n_elig_trades": es.get("n_trades")})
        # depth / dynamics tables are subsets of the bucket table
        print(T, "done", flush=True)
        del tr, TR, S, s, s1, s5
    # ---- write cost table (schema fixed)
    cols = ["ticker", "year", "bucket_start_et", "bucket_end_et", "median_spread_cents", "mean_spread_cents",
            "median_half_spread_bps", "mean_half_spread_bps", "n_obs"]
    order = {T: i for i, T in enumerate(COST_TICKERS)}
    ck = pd.DataFrame(cost)[cols]
    ck["_o"] = ck.ticker.map(order)
    ck["_b"] = ck.bucket_start_et.map(lambda s: {"04:00": -1, "16:00": 99}.get(s, 0)) * 10000 + ck.bucket_start_et.str.replace(":", "").astype(int)
    ck = ck.sort_values(["_o", "year", "_b"]).drop(columns=["_o", "_b"])
    tmp = OUT / ".cost_model_halfspread.tmp.csv"
    ck.to_csv(tmp, index=False); tmp.rename(OUT / "cost_model_halfspread.csv")
    cd = pd.DataFrame(cost_det)
    cd.to_csv(OUT / "cost_model_halfspread_detail.csv", index=False)
    print("cost table rows:", len(ck), flush=True)
    if cost_only:
        return
    sp = pd.concat(SPREAD, ignore_index=True)
    sp.to_csv(OUT / "quoted_spread_by_bucket.csv", index=False)
    dcols = ["ticker", "group", "session", "bucket_start_et", "bucket_end_et", "n_days", "tw_mid"] + \
            [c for c in sp.columns if c.startswith("tw_mean_b") or c.startswith("tw_mean_a") or c.startswith("median_of_window")]
    sp[dcols].to_csv(OUT / "depth_by_bucket.csv", index=False)
    qcols = ["ticker", "group", "session", "bucket_start_et", "bucket_end_et", "n_days", "sampled_seconds", "n_quote_msgs",
             "msgs_per_sec", "px_changes_per_sec", "bid_px_changes_per_sec", "ask_px_changes_per_sec", "n_price_states",
             "state_dur_p10_ms", "state_dur_median_ms", "state_dur_p90_ms", "state_dur_timeweighted_median_ms",
             "share_states_lt_1ms", "share_twosided_time_locked", "share_twosided_time_crossed"]
    sp[qcols].to_csv(OUT / "quote_dynamics_by_bucket.csv", index=False)
    pd.DataFrame(TICKC).to_csv(OUT / "tick_constraint_summary.csv", index=False)
    pd.DataFrame(SIZE).to_csv(OUT / "trade_size_oddlot.csv", index=False)
    pd.DataFrame(EFF).to_csv(OUT / "effective_spread.csv", index=False)
    pd.DataFrame(EFFSZ).to_csv(OUT / "effective_spread_by_size.csv", index=False)
    auc = pd.DataFrame(AUC)
    auc.to_csv(OUT / "auctions_by_day.csv", index=False)
    auc["grp"] = np.where(auc.category == "stress", "stress", np.where(auc.day >= LAST12_START, "last12m_normal", "2022-2025_normal"))
    asum = auc.groupby(["ticker", "grp"]).agg(n_days=("day", "count"), n_open_found=("n_open_prints", lambda v: (v > 0).sum()),
                                              n_close_found=("n_close_prints", lambda v: (v > 0).sum()),
                                              open_share_mean=("open_share_of_daily_volume", "mean"),
                                              open_share_median=("open_share_of_daily_volume", "median"),
                                              close_share_mean=("close_share_of_daily_volume", "mean"),
                                              close_share_median=("close_share_of_daily_volume", "median"),
                                              close_share_max=("close_share_of_daily_volume", "max"),
                                              open_usd_median=("open_auction_dollars", "median"),
                                              close_usd_median=("close_auction_dollars", "median")).reset_index()
    asum.to_csv(OUT / "auctions_summary.csv", index=False)
    s2v = pd.DataFrame(S2V)
    mv = pd.read_csv(OUT / "minbar_vol_by_bucket.csv")
    mv["bucket_start_et"] = mv["bucket_start"].map(lambda b: "09:30" if b == -1 else min_to_hhmm(int(b)))
    mv["is_all"] = mv["bucket_start"] == -1
    mv = mv.rename(columns={"period": "group", "std_r1_bps": "sd_bar_ret_1m_bps", "std_r5_bps": "sd_bar_ret_5m_bps", "n_days": "n_days_bars"})
    s2v["is_all"] = s2v["bucket_end_et"] == "16:00"
    s2v.loc[s2v.bucket_start_et != "09:30", "is_all"] = False
    s2v["is_all"] = (s2v["bucket_start_et"] == "09:30") & (s2v["bucket_end_et"] == "16:00")
    s2v = s2v.merge(mv[["ticker", "group", "bucket_start_et", "is_all", "sd_bar_ret_1m_bps", "sd_bar_ret_5m_bps", "n_days_bars"]],
                    on=["ticker", "group", "bucket_start_et", "is_all"], how="left")
    s2v["spread_over_bar_sd1m"] = s2v["tw_mean_spread_bps"] / s2v["sd_bar_ret_1m_bps"]
    s2v["spread_over_bar_sd5m"] = s2v["tw_mean_spread_bps"] / s2v["sd_bar_ret_5m_bps"]
    s2v = s2v.drop(columns=["is_all"])
    s2v.to_csv(OUT / "spread_to_vol.csv", index=False)
    ds = pd.DataFrame(DAYSUM); ds.to_csv(OUT / "sample_day_summary.csv", index=False)
    # stress vs normal (last ~18 months)
    rows = []
    for T in TICKERS:
        x = ds[ds.ticker == T]
        base = x[(x.category.isin(["normal", "recent"])) & (x.day >= NORMAL18_START)]
        for lab, sub in [("normal days since 2025-03-25 (median)", base)] + [(f"stress {d}", x[x.day == d]) for d in sorted(x[x.category == "stress"].day)] + \
                        [("2026-09-24", x[x.day == "2026-09-24"])]:
            if not len(sub):
                continue
            agg = sub.drop(columns=["ticker", "day", "category"]).median(numeric_only=True)
            r = {"ticker": T, "sample": lab, "n_days": len(sub)}
            r.update(agg.to_dict())
            rows.append(r)
    st = pd.DataFrame(rows); st.to_csv(OUT / "stress_vs_normal.csv", index=False)
    charts(sp, s2v, ds)
    fullday()


# ------------------------------------------------------------------ full-day SOXL/SOXS + validation
def fullday():
    rows, val = [], []
    prof = []
    for T in ("SOXL", "SOXS"):
        for f in sorted((FD / T).glob("*_trades.parquet")):
            day = f.name[:10]
            mins = pd.read_parquet(FD / T / f"{day}_minute.parquet")
            shist = pd.read_parquet(FD / T / f"{day}_shist.parquet")
            tr = pd.read_parquet(f)
            tr["kind"] = "rth"; tr["wid"] = 0; tr["stratum_start"] = 0; tr["stratum_end"] = 0; tr["day"] = day
            tr = prep_trades(tr, T)
            et = pd.to_datetime(tr["t"], unit="ns", utc=True).dt.tz_convert(ET)
            tr["minute"] = et.dt.hour * 60 + et.dt.minute + et.dt.second / 60
            rth = (tr.minute >= 570) & (tr.minute < 960)
            v_all = tr.loc[~tr.novol, "size"].sum()
            op = tr[(tr.ex == PRIMARY[T]) & conds_has_any(tr["cond"].to_numpy(), OPEN_CODES) & ~tr.novol & (tr.minute >= 569) & (tr.minute < 575)]
            cl = tr[(tr.ex == PRIMARY[T]) & conds_has_any(tr["cond"].to_numpy(), CLOSE_CODES) & ~tr.novol & (tr.minute >= 960) & (tr.minute < 961)]
            e = tr[tr.elig]
            r = {"ticker": T, "day": day, "n_trades_all_sessions": int((~tr.novol).sum()), "volume_all_sessions": v_all,
                 "share_volume_premarket": tr.loc[~tr.novol & (tr.minute < 570), "size"].sum() / v_all,
                 "share_volume_rth_continuous": tr.loc[~tr.novol & rth, "size"].sum() / v_all - (op["size"].sum() / v_all),
                 "share_volume_open_auction": op["size"].sum() / v_all, "share_volume_close_auction": cl["size"].sum() / v_all,
                 "share_volume_afterhours_excl_close_auction": (tr.loc[~tr.novol & (tr.minute >= 960), "size"].sum() - cl["size"].sum()) / v_all}
            r.update({f"rth_{k}": v for k, v in trade_size_stats(tr[rth], "RTH").items() if k != "sample"})
            r.update({f"eff_{k}": v for k, v in eff_stats(e).items()})
            # whole-RTH time-weighted spread from full-session minute table
            m = mins[(mins.minute >= 570) & (mins.minute < 960)]
            r["fullday_rth_tw_mean_spread_cents"] = m.sd_spread_c.sum() / m.T_pos.sum()
            r["fullday_rth_tw_mean_spread_bps"] = m.sd_bps.sum() / m.T_pos.sum()
            r["fullday_rth_share_one_tick"] = m.T_1tick.sum() / m.T_pos.sum()
            r["fullday_rth_msgs_per_sec"] = m.n_msg.sum() / (390 * 60)
            sh = shist[(shist.b0 >= 570) & (shist.b1 <= 960)]
            r["fullday_rth_tw_median_spread_cents"] = wquantile(sh.k_halfc * 0.5, sh.time_s, [0.5])[0]
            rows.append(r)
            mm = mins.copy(); mm["ticker"] = T; mm["day"] = day
            prof.append(mm)
            # validation vs windows (same day)
            qf = TICK / T / f"{day}_qstats.parquet"
            if qf.exists():
                q = pd.read_parquet(qf)
                hq = pd.read_parquet(TICK / T / f"{day}_shist.parquet").merge(q[["wid", "sub_start", "kind", "stratum_start"]], on=["wid", "sub_start"])
                for (b0, b1) in RTH_BUCKETS:
                    mb = mins[(mins.minute >= b0) & (mins.minute < b1)]
                    truth = mb.sd_spread_c.sum() / mb.T_pos.sum()
                    truth_bps = mb.sd_bps.sum() / mb.T_pos.sum()
                    hw = hq[(hq.kind == "rth") & (hq.stratum_start == b0)]
                    est = (hw.k_halfc * 0.5 * hw.time_s).sum() / hw.time_s.sum()
                    val.append({"ticker": T, "day": day, "bucket_start_et": min_to_hhmm(b0), "fullday_tw_mean_spread_cents": truth,
                                "window_tw_mean_spread_cents": est, "fullday_tw_mean_spread_bps": truth_bps,
                                "window_tw_mean_spread_bps": (hw.time_x_bps.sum() / hw.time_s.sum())})
    fd = pd.DataFrame(rows); fd.to_csv(OUT / "fullday_soxl_soxs_summary.csv", index=False)
    v = pd.DataFrame(val)
    if len(v):
        v["rel_err"] = v.window_tw_mean_spread_cents / v.fullday_tw_mean_spread_cents - 1
        v.to_csv(OUT / "window_validation_fullday.csv", index=False)
    if prof:
        P = pd.concat(prof)
        P.to_parquet(DATA / "fullday_minute_profiles.parquet", index=False)
        recent = P[P.day >= "2026-09-21"]
        g = recent.groupby(["ticker", "minute"])[["sd_spread_c", "sd_bps", "T_pos", "sd_bdol", "sd_adol"]].sum().reset_index()
        g["spread_c"] = g.sd_spread_c / g.T_pos; g["spread_bps"] = g.sd_bps / g.T_pos
        g["depth_usd"] = (g.sd_bdol + g.sd_adol) / 2 / g.T_pos
        g.to_csv(OUT / "fullday_minute_spread_profile_2026-09-21_25.csv", index=False)
        fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
        for T in ("SOXL", "SOXS"):
            x = g[g.ticker == T]
            axes[0].plot(x.minute, x.spread_c, color=FOCUS_COLORS[T], lw=1.2, label=T)
            axes[1].plot(x.minute, x.spread_bps, color=FOCUS_COLORS[T], lw=1.2, label=T)
        for ax in axes:
            for b in (570, 960):
                ax.axvline(b, color="#b9b8b2", lw=0.8)
            ax.set_yscale("log"); style_ax(ax); ax.legend(fontsize=8, frameon=False)
        axes[0].set_ylabel("Time-weighted NBBO spread (cents, log)")
        axes[1].set_ylabel("Time-weighted NBBO spread (bps of mid, log)")
        ticks = list(range(240, 1201, 60))
        axes[1].set_xticks(ticks); axes[1].set_xticklabels([min_to_hhmm(t) for t in ticks], fontsize=8)
        axes[0].set_title("SOXL vs SOXS: full-session NBBO spread by minute (ET), pooled 2026-09-21..25 (5 days, all quotes)", fontsize=10)
        fig.tight_layout(); fig.savefig(OUT / "fullday_spread_profile.png", dpi=110); plt.close(fig)


def charts(sp, s2v, ds):
    # 1) spread by time of day (last 12 months, normal days), bps and cents
    CG = "since_2026-07-15"  # current price regime (after the SOXS 1:10 reverse split); pooled 12 months mixes regimes
    x = sp[(sp.group == CG) & (sp.session == "rth")].copy()
    x = x[(x.bucket_end_et.map(hhmm_to_min) - x.bucket_start_et.map(hhmm_to_min)) == 30]
    fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True)
    for ax, col, lab in ((axes[0], "tw_mean_spread_bps", "Time-weighted mean quoted spread (bps of mid, log)"),
                         (axes[1], "tw_mean_spread_cents", "Time-weighted mean quoted spread (cents, log)")):
        ax.set_yscale("log")
        ser = {}
        for T in TICKERS:
            d = x[x.ticker == T].sort_values("bucket_start_et")
            ser[T] = (np.arange(len(d)), d[col].to_numpy())
        allv = np.concatenate([v[1] for v in ser.values()])
        ax.set_ylim(np.nanmin(allv) * 0.8, np.nanmax(allv) * 1.3)
        focus_lines(ax, ser, logy=True)
        ax.set_ylabel(lab)
    labels = sorted(x.bucket_start_et.unique())
    axes[1].set_xticks(range(len(labels))); axes[1].set_xticklabels(labels, fontsize=8)
    axes[1].set_xlabel("30-minute bucket start (ET)")
    axes[0].set_title("Quoted NBBO spread by time of day, sampled windows on the 7 normal days since 2026-07-15 (current price regime)", fontsize=10)
    fig.subplots_adjust(right=0.9, hspace=0.08, top=0.95, bottom=0.07, left=0.09)
    fig.savefig(OUT / "spread_by_time_of_day.png", dpi=110); plt.close(fig)
    # 2) depth ($ at NBBO, mean of bid and ask) by time of day
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_yscale("log")
    ser = {}
    for T in TICKERS:
        d = x[x.ticker == T].sort_values("bucket_start_et")
        ser[T] = (np.arange(len(d)), ((d.tw_mean_bdol + d.tw_mean_adol) / 2 / 1e3).to_numpy())
    allv = np.concatenate([v[1] for v in ser.values()])
    ax.set_ylim(np.nanmin(allv) * 0.8, np.nanmax(allv) * 1.3)
    focus_lines(ax, ser, logy=True)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Time-weighted mean NBBO size, avg of bid & ask ($ thousands, log)")
    ax.set_title("Displayed NBBO depth by time of day, sampled windows on the 7 normal days since 2026-07-15", fontsize=10)
    fig.subplots_adjust(right=0.9, top=0.92, bottom=0.08, left=0.09)
    fig.savefig(OUT / "depth_by_time_of_day.png", dpi=110); plt.close(fig)
    # 3) spread-to-vol by time of day
    y = s2v[(s2v.group == CG) & ~((s2v.bucket_start_et == "09:30") & (s2v.bucket_end_et == "16:00"))]
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for ax, col, lab in ((axes[0], "spread_over_sd1m", "Quoted spread / sd(1-min mid return)"),
                         (axes[1], "spread_over_sd5m", "Quoted spread / sd(5-min mid return)")):
        ax.set_yscale("log")
        ser = {}
        for T in TICKERS:
            d = y[y.ticker == T].sort_values("bucket_start_et")
            ser[T] = (np.arange(len(d)), d[col].to_numpy())
        allv = np.concatenate([v[1] for v in ser.values()])
        ax.set_ylim(np.nanmin(allv) * 0.8, np.nanmax(allv) * 1.3)
        focus_lines(ax, ser, logy=True)
        ax.set_ylabel(lab + " (log)")
    labels2 = sorted(y.bucket_start_et.unique())
    axes[1].set_xticks(range(len(labels2))); axes[1].set_xticklabels(labels2, fontsize=8)
    axes[0].set_title("Spread / sd(mid return) by time of day, 7 normal days since 2026-07-15 (lower = spread small vs typical move)", fontsize=10)
    fig.subplots_adjust(right=0.9, hspace=0.08, top=0.95, bottom=0.07, left=0.09)
    fig.savefig(OUT / "spread_to_vol.png", dpi=110); plt.close(fig)
    # 3b) regime chart: per sample day RTH spread (ticks, bps) and one-tick share, SOXL vs SOXS, 2022-2026
    fig, axes = plt.subplots(3, 1, figsize=(11, 9.5), sharex=True)
    for T in ("SOXL", "SOXS"):
        d = ds[ds.ticker == T].sort_values("day")
        xd = pd.to_datetime(d.day)
        norm = d.category != "stress"
        for ax, col, f in ((axes[0], "tw_mean_spread_cents", 1.0), (axes[1], "tw_mean_spread_bps", 1.0), (axes[2], "share_time_one_tick", 100.0)):
            ax.plot(xd[norm], d.loc[norm, col] * f, color=FOCUS_COLORS[T], lw=1.2, marker="o", ms=4, label=f"{T} (normal/recent days)")
            ax.scatter(xd[~norm], d.loc[~norm, col] * f, color=FOCUS_COLORS[T], marker="D", s=30, edgecolor="white", lw=0.6, zorder=4,
                       label=f"{T} stress days")
    axes[0].set_yscale("log"); axes[0].set_ylabel("RTH time-weighted spread (cents = ticks, log)")
    axes[1].set_yscale("log"); axes[1].set_ylabel("RTH time-weighted spread (bps, log)")
    axes[2].set_ylabel("% of RTH time spread = 1 tick"); axes[2].set_ylim(-3, 103)
    for ax in axes:
        style_ax(ax)
    axes[0].legend(fontsize=7.5, frameon=False, ncol=2)
    axes[0].set_title("SOXL vs SOXS quoted-spread regime on every sampled day, 2022-2026 (sampled RTH windows)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "spread_regimes_by_day.png", dpi=110); plt.close(fig)
    # 4) stress vs normal: RTH spread (bps) per day, dots
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, T in enumerate(TICKERS):
        d = ds[ds.ticker == T]
        base = d[(d.category != "stress") & (d.day >= NORMAL18_START)]
        stv = d[d.category == "stress"]
        c = FOCUS_COLORS.get(T, "#6d6c67")
        ax.scatter(np.full(len(base), i - 0.12) + np.linspace(-0.05, 0.05, len(base)), base.tw_mean_spread_bps, s=12, color=c, alpha=0.45, lw=0)
        ax.scatter(np.full(len(stv), i + 0.15), stv.tw_mean_spread_bps, s=26, marker="D", color=c, lw=0.6, edgecolor="white")
    ax.scatter([], [], s=12, color="#6d6c67", alpha=0.45, label="normal sample days since 2025-03-25 (left)")
    ax.scatter([], [], s=26, marker="D", color="#6d6c67", label="stress days (right)")
    ax.set_xticks(range(len(TICKERS))); ax.set_xticklabels(TICKERS)
    ax.set_yscale("log"); ax.set_ylabel("RTH time-weighted mean quoted spread (bps, log)")
    ax.set_title("Quoted spread on stress days vs normal days (one mark per sampled day)", fontsize=10)
    ax.legend(fontsize=8, frameon=False); style_ax(ax)
    fig.tight_layout(); fig.savefig(OUT / "stress_vs_normal.png", dpi=110); plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cost-only", action="store_true")
    ap.add_argument("--fullday-only", action="store_true")
    a = ap.parse_args()
    if a.fullday_only:
        fullday()
    else:
        main(cost_only=a.cost_only)
    import os
    os._exit(0)
