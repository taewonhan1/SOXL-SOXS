"""Look-ahead-safe intraday feature engineering on the regular-session minute panel.

Convention: a feature value at (day d, bar j) may use only
  * regular-session bars 0..j of day d (bar j is complete at its close, i.e. at 09:30 + j + 1 minutes),
  * pre-market bars (04:00-09:29 ET) of day d,
  * anything from days < d (including official daily closes of prior days).
Signals built from these features are executed at the OPEN of bar j+1 by soxlab.backtest.

``FEATURE_DICTIONARY`` documents every column (name, definition, granularity, look-ahead safety).
Columns flagged ``look_ahead_safe=False`` are forward-looking LABELS for research only; they must
never be used as signal inputs. ``tests/test_no_lookahead.py`` verifies the safe ones by truncation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config
from . import data as sdata

LN = np.log
PRICE_LEVEL = {"pm_high", "pm_low", "pd_high", "pd_low", "pd_close", "atr14_1m", "atr14_d", "true_range_1m",
               "gap", "gap_atr", "ret_since_prev_close", "dist_vwap_sd"}


# --------------------------------------------------------------------------------------
# small causal helpers on (n_days, n_bars) arrays
# --------------------------------------------------------------------------------------
def shift_cols(a: np.ndarray, k: int) -> np.ndarray:
    """out[:, j] = a[:, j-k] (NaN for j < k). k may be negative (forward shift -> NOT causal)."""
    out = np.full_like(a, np.nan, dtype=float)
    if k > 0:
        out[:, k:] = a[:, :-k]
    elif k < 0:
        out[:, :k] = a[:, -k:]
    else:
        out[:] = a
    return out


def shift_days(a: np.ndarray, k: int = 1) -> np.ndarray:
    out = np.full_like(a, np.nan, dtype=float)
    if a.ndim == 1:
        out[k:] = a[:-k]
    else:
        out[k:, ...] = a[:-k, ...]
    return out


def ema_cols(x: np.ndarray, span: int) -> np.ndarray:
    """Session-reset EMA along bars (adjust=False), NaN-tolerant (holds value through NaN)."""
    alpha = 2.0 / (span + 1.0)
    out = np.full_like(x, np.nan, dtype=float)
    prev = np.full(x.shape[0], np.nan)
    for j in range(x.shape[1]):
        xj = x[:, j]
        new = np.where(np.isnan(prev), xj, alpha * xj + (1 - alpha) * prev)
        new = np.where(np.isnan(xj), prev, new)
        out[:, j] = new
        prev = new
    return out


def wilder_cols(x: np.ndarray, n: int) -> np.ndarray:
    alpha = 1.0 / n
    out = np.full_like(x, np.nan, dtype=float)
    prev = np.full(x.shape[0], np.nan)
    for j in range(x.shape[1]):
        xj = x[:, j]
        new = np.where(np.isnan(prev), xj, alpha * xj + (1 - alpha) * prev)
        new = np.where(np.isnan(xj), prev, new)
        out[:, j] = new
        prev = new
    return out


def rolling_sum_cols(x: np.ndarray, w: int) -> np.ndarray:
    """Causal rolling sum over the last w bars within the session (NaN if fewer than w bars)."""
    cs = np.nancumsum(np.nan_to_num(x), axis=1)
    out = cs - shift_cols(cs, w)
    out[:, : w - 1] = np.nan
    out[:, w - 1] = cs[:, w - 1]
    return out


def rolling_days_mean(x: np.ndarray, w: int) -> np.ndarray:
    """Mean over the PREVIOUS w days (excludes day d), axis 0, NaN-aware; x is (n_days, ...) ."""
    n = x.shape[0]
    out = np.full_like(x, np.nan, dtype=float)
    for d in range(1, n):
        lo = max(0, d - w)
        blk = x[lo:d]
        if len(blk) >= max(3, w // 2):
            with np.errstate(all="ignore"):
                out[d] = np.nanmean(blk, axis=0)
    return out


# --------------------------------------------------------------------------------------
# day-level inputs (all computed from data available before day d's open, or pre-market)
# --------------------------------------------------------------------------------------
def rth_daily(p: sdata.Panel) -> pd.DataFrame:
    """Regular-session OHLCV per day from the minute panel (09:30-15:59 bars, adjusted)."""
    with np.errstate(all="ignore"):
        last = np.array([p.c[i, p.n_min[i] - 1] for i in range(len(p.dates))])
        first_o = pd.DataFrame(p.o).bfill(axis=1).to_numpy()[:, 0]  # day-level summary (used only for prior days)
        df = pd.DataFrame({"open": first_o, "high": np.nanmax(p.h, axis=1), "low": np.nanmin(p.l, axis=1),
                           "close": last, "volume": np.nansum(p.v, axis=1)}, index=p.dates)
    return df


def official_close(ticker: str, dates: pd.DatetimeIndex, adjusted: bool = True) -> pd.Series:
    """Official daily close (daily-bar close = closing-auction price) aligned to ``dates``."""
    d = sdata.load_daily(ticker, adjusted)
    return d["c"].reindex(dates)


def premarket_summary(ticker: str, dates: pd.DatetimeIndex, adjusted: bool = True) -> pd.DataFrame:
    """Pre-market (04:00-09:29 ET) high / low / last / volume per day."""
    start, end = dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d")
    b = sdata.load_minute_bars(ticker, adjusted, start, end)
    pm = b[(b["mod"] >= config.EXT_START_MIN) & (b["mod"] < config.RTH_START_MIN)]
    g = pm.sort_values("t").groupby("date")
    out = pd.DataFrame({"pm_high": g["h"].max(), "pm_low": g["l"].min(), "pm_last": g["c"].last(),
                        "pm_volume": g["v"].sum(), "pm_bars": g["c"].size()})
    return out.reindex(dates)


# --------------------------------------------------------------------------------------
# feature computation
# --------------------------------------------------------------------------------------
def compute_features(ticker: str, panels: dict, official: dict, premarket: dict,
                     cal: pd.DataFrame, drivers=("SOXX", "NVDA", "QQQ", "SMH")) -> dict:
    """Return {feature_name: 2-D float array (n_days, 390)} for ``ticker``.

    panels     {ticker: Panel} on identical date grids (SOXL, SOXS, drivers)
    official   {ticker: Series of official adjusted daily closes aligned to the panel dates}
    premarket  {ticker: DataFrame from premarket_summary} (only ``ticker`` needed)
    cal        calendar DataFrame (soxlab.calendar) indexed by date
    """
    p = panels[ticker]
    nd, nb = p.c.shape
    J = np.broadcast_to(np.arange(nb)[None, :], (nd, nb))
    inside = p.valid()
    F: dict[str, np.ndarray] = {}

    def day2d(x):  # broadcast a per-day vector to the grid (masked outside session)
        return np.where(inside, np.asarray(x, float)[:, None] * np.ones((1, nb)), np.nan)

    c, o, h, l, v = p.c, p.o, p.h, p.l, p.v
    logc = LN(c)
    prev_c = shift_cols(c, 1)
    prev_c[:, 0] = o[:, 0]
    # ---- returns
    F["ret_1m"] = LN(c / prev_c)
    for k in (5, 15, 30, 60):
        F[f"ret_{k}m"] = logc - shift_cols(logc, k)
    F["ret_since_open"] = LN(c / o[:, [0]])
    # ---- range / volatility
    tr = np.fmax(h, prev_c) - np.fmin(l, prev_c)
    F["true_range_1m"] = tr
    F["true_range_1m_bps"] = tr / c * 1e4
    F["atr14_1m"] = wilder_cols(tr, 14)
    F["atr14_1m_bps"] = F["atr14_1m"] / c * 1e4
    F["rv_30m"] = np.sqrt(rolling_sum_cols(F["ret_1m"] ** 2, 30))
    F["rv_30m_ann"] = F["rv_30m"] * np.sqrt(252 * 390 / 30)
    daily = rth_daily(p)
    offc = official[ticker].to_numpy()
    prev_off = shift_days(offc, 1)
    tr_d = np.fmax(daily["high"].to_numpy(), prev_off) - np.fmin(daily["low"].to_numpy(), prev_off)
    atr_d = pd.Series(tr_d).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean().to_numpy()
    atr_d_prev = shift_days(atr_d, 1)                       # through day d-1 -> known at d's open
    F["atr14_d"] = day2d(atr_d_prev)
    F["atr14_d_pct"] = day2d(atr_d_prev / prev_off * 100)
    r_d = np.log(offc / prev_off)
    rv_d = pd.Series(r_d).rolling(20, min_periods=15).std().to_numpy() * np.sqrt(252)
    F["rv20_d_ann"] = day2d(shift_days(rv_d, 1))
    # ---- VWAP and bands (session VWAP from 09:30 on bar vw)
    vw = np.where(np.isnan(p.vw), c, p.vw)
    cv = np.nancumsum(v, axis=1)
    cpv = np.nancumsum(vw * v, axis=1)
    cp2v = np.nancumsum(vw * vw * v, axis=1)
    with np.errstate(all="ignore"):
        vwap = np.where(cv > 0, cpv / cv, np.nan)
        var = np.where(cv > 0, cp2v / cv - vwap ** 2, np.nan)
    vwap = np.where(np.isnan(vwap), c, vwap)
    sd = np.sqrt(np.clip(var, 0, None))
    F["vwap"] = vwap
    F["vwap_sd"] = sd
    for k in (1, 2, 3):
        F[f"vwap_up{k}"] = vwap + k * sd
        F[f"vwap_dn{k}"] = vwap - k * sd
    F["dist_vwap_bps"] = (c / vwap - 1) * 1e4
    with np.errstate(all="ignore"):
        F["dist_vwap_sd"] = np.where(sd > 0, (c - vwap) / sd, np.nan)
    above = np.sign(c - vwap)
    cross = (above != shift_cols(above, 1)) & (above != 0) & ~np.isnan(shift_cols(above, 1))
    F["vwap_cross_count"] = np.cumsum(cross, axis=1).astype(float)
    # ---- opening ranges
    for n in (5, 15, 30):
        hi = np.nanmax(h[:, :n], axis=1)
        lo = np.nanmin(l[:, :n], axis=1)
        ok = J >= n - 1
        F[f"or{n}_high"] = np.where(ok, hi[:, None], np.nan)
        F[f"or{n}_low"] = np.where(ok, lo[:, None], np.nan)
        F[f"or{n}_size_bps"] = np.where(ok, ((hi / lo - 1) * 1e4)[:, None], np.nan)
    # ---- pre-market and prior day
    pm = premarket[ticker]
    F["pm_high"] = day2d(pm["pm_high"].to_numpy())
    F["pm_low"] = day2d(pm["pm_low"].to_numpy())
    F["pm_volume"] = day2d(pm["pm_volume"].fillna(0).to_numpy())
    F["pm_ret"] = day2d(pm["pm_last"].to_numpy() / prev_off - 1)
    F["pd_high"] = day2d(shift_days(daily["high"].to_numpy(), 1))
    F["pd_low"] = day2d(shift_days(daily["low"].to_numpy(), 1))
    F["pd_close"] = day2d(prev_off)
    F["gap"] = day2d(o[:, 0] / prev_off - 1)
    F["gap_atr"] = day2d((o[:, 0] - prev_off) / atr_d_prev)
    F["dist_pd_high_bps"] = (c / F["pd_high"] - 1) * 1e4
    F["dist_pd_low_bps"] = (c / F["pd_low"] - 1) * 1e4
    F["ret_since_prev_close"] = c / F["pd_close"] - 1
    # ---- volume
    cumv = np.where(inside, cv, np.nan)
    tot_v = np.nansum(np.where(inside, v, 0), axis=1)
    F["cum_volume"] = cumv
    F["rvol_tod"] = cumv / rolling_days_mean(cumv, 20)
    F["cumvol_share"] = cumv / day2d(rolling_days_mean(tot_v[:, None], 20)[:, 0])
    F["rvol_1m"] = v / rolling_days_mean(np.where(inside, v, np.nan), 20)
    # ---- EMAs (1-min, session reset) and 5-min EMAs (updated at 5-min bar closes)
    F["ema9_1m"] = ema_cols(c, 9)
    F["ema21_1m"] = ema_cols(c, 21)
    F["ema_diff_1m_bps"] = (F["ema9_1m"] / F["ema21_1m"] - 1) * 1e4
    c5 = np.where((J + 1) % 5 == 0, c, np.nan)
    e9_5 = ema_cols(c5[:, 4::5], 9)
    e21_5 = ema_cols(c5[:, 4::5], 21)
    for nm, e in (("ema9_5m", e9_5), ("ema21_5m", e21_5)):
        g = np.full((nd, nb), np.nan)
        g[:, 4::5] = e
        F[nm] = pd.DataFrame(g).ffill(axis=1).to_numpy()
    F["ema_diff_5m_bps"] = (F["ema9_5m"] / F["ema21_5m"] - 1) * 1e4
    # ---- drivers
    for dx in drivers:
        if dx not in panels:
            continue
        q = panels[dx]
        qc = q.c
        qprev = shift_cols(qc, 1)
        qprev[:, 0] = q.o[:, 0]
        r1 = LN(qc / qprev)
        F[f"{dx}_ret_1m"] = r1
        F[f"{dx}_ret_1m_lag1"] = shift_cols(r1, 1)
        F[f"{dx}_ret_1m_lag2"] = shift_cols(r1, 2)
        F[f"{dx}_ret_5m"] = LN(qc) - shift_cols(LN(qc), 5)
        qoff = shift_days(official[dx].to_numpy(), 1)
        F[f"{dx}_ret_since_prev_close"] = qc / qoff[:, None] - 1
    # ---- index proxy, implied leverage, tracking gap
    L = config.LEVERAGE.get(ticker, 1.0)
    proxy = config.INDEX_PROXY.get(ticker)
    if proxy and f"{proxy}_ret_since_prev_close" in F:
        r = F[f"{proxy}_ret_since_prev_close"]
        F["idx_ret_since_prev_close"] = r
        F["lev_implied"] = L * (1 + r) / (1 + L * r)
        F["tracking_gap_bps"] = (F["ret_since_prev_close"] - L * r) * 1e4
        with np.errstate(all="ignore"):
            F["lev_realized"] = np.where(np.abs(r) > 0.0025, F["ret_since_prev_close"] / r, np.nan)
    # ---- SOXL-SOXS divergence
    if "SOXL" in panels and "SOXS" in panels:
        rl = panels["SOXL"].c / shift_days(official["SOXL"].to_numpy(), 1)[:, None] - 1
        rs = panels["SOXS"].c / shift_days(official["SOXS"].to_numpy(), 1)[:, None] - 1
        F["soxl_soxs_div_bps"] = (rl + rs) * 1e4
        F["soxl_soxs_ret1m_sum_bps"] = (LN(panels["SOXL"].c / shift_cols(panels["SOXL"].c, 1)) +
                                        LN(panels["SOXS"].c / shift_cols(panels["SOXS"].c, 1))) * 1e4
    # ---- time and calendar
    F["minute_of_session"] = np.where(inside, J, np.nan).astype(float)
    F["minutes_to_close"] = np.where(inside, p.n_min[:, None] - 1 - J, np.nan).astype(float)
    calr = cal.reindex(p.dates)
    F["dow"] = day2d(calr["dow"].to_numpy())
    for flag in ("is_half_day", "pre_holiday", "post_holiday", "month_end", "month_start", "quarter_end",
                 "monthly_opex", "quad_witching", f"split_{ticker}" if f"split_{ticker}" in calr else None,
                 f"exdiv_{ticker}" if f"exdiv_{ticker}" in calr else None):
        if flag:
            F[f"flag_{flag.replace('_' + ticker, '')}"] = day2d(calr[flag].astype(float).to_numpy())
    F["flag_large_gap"] = day2d((np.abs(o[:, 0] - prev_off) > atr_d_prev).astype(float))
    # ---- forward-looking LABELS (NOT look-ahead safe; research/evaluation only)
    F["label_fwd_ret_1m"] = LN(shift_cols(c, -1) / c)
    F["label_fwd_ret_5m"] = LN(shift_cols(c, -5) / c)
    last = np.array([c[i, p.n_min[i] - 1] for i in range(nd)])
    F["label_fwd_ret_to_close"] = LN(last[:, None] / c)
    # price-level features (compared against prices by strategies) stay float64; the rest float32 (memory)
    for k in list(F):
        keep64 = k in PRICE_LEVEL or k.startswith(("or5_", "or15_", "or30_", "vwap", "ema"))
        F[k] = np.where(inside, F[k], np.nan).astype(np.float64 if keep64 else np.float32)
    return F


def to_frame(F: dict, p: sdata.Panel, names=None) -> pd.DataFrame:
    """Long format: one row per (date, minute) inside the session."""
    names = names or list(F)
    inside = p.valid()
    di, jj = np.nonzero(inside)
    df = pd.DataFrame({"date": p.dates[di], "bar": jj.astype(np.int16)})
    df["time_et"] = [f"{(config.RTH_START_MIN + j) // 60:02d}:{(config.RTH_START_MIN + j) % 60:02d}" for j in jj]
    for k in names:
        df[k] = F[k][di, jj].astype(np.float32)
    return df


# --------------------------------------------------------------------------------------
# data dictionary
# --------------------------------------------------------------------------------------
_DD = [
    # name, definition, granularity, look_ahead_safe
    ("ret_1m", "log(c_j / c_{j-1}); bar 0 uses log(c_0/o_0)", "1-min", True),
    ("ret_{5,15,30,60}m", "log(c_j / c_{j-k}); NaN until k bars into the session (no overnight mixing)", "1-min", True),
    ("ret_since_open", "log(c_j / o_0) where o_0 is the 09:30 bar open", "1-min", True),
    ("true_range_1m[_bps]", "max(h_j, c_{j-1}) - min(l_j, c_{j-1}) (bps: / c_j)", "1-min", True),
    ("atr14_1m[_bps]", "Wilder ATR(14) of 1-min true range, reset each session", "1-min", True),
    ("rv_30m / rv_30m_ann", "sqrt(sum of squared 1-min log returns over last 30 bars); ann. x sqrt(252*390/30)", "1-min", True),
    ("atr14_d / atr14_d_pct", "Wilder ATR(14) of daily true range (RTH high/low vs prior official close) through day d-1", "daily (constant intraday)", True),
    ("rv20_d_ann", "stdev of 20 prior daily close-to-close log returns x sqrt(252)", "daily", True),
    ("vwap", "session VWAP from 09:30: cumsum(vw*v)/cumsum(v) over bars 0..j (bar vw = bar VWAP)", "1-min", True),
    ("vwap_sd, vwap_up{1,2,3}, vwap_dn{1,2,3}", "volume-weighted stdev of bar vw around VWAP; bands = vwap +/- k*sd", "1-min", True),
    ("dist_vwap_bps / dist_vwap_sd", "(c_j/vwap_j - 1)*1e4 ; (c_j - vwap_j)/vwap_sd_j", "1-min", True),
    ("vwap_cross_count", "cumulative number of sign changes of (c - vwap) since the open", "1-min", True),
    ("or{5,15,30}_high/low/size_bps", "high/low of the first N regular-session bars; NaN before bar N-1 closes", "1-min", True),
    ("pm_high / pm_low / pm_volume / pm_ret", "pre-market 04:00-09:29 ET high, low, volume, last/prior-official-close - 1", "daily", True),
    ("pd_high / pd_low / pd_close", "prior session RTH high/low (from minute bars) and prior OFFICIAL close (daily bar)", "daily", True),
    ("gap / gap_atr / flag_large_gap", "o_0/pd_close - 1 ; (o_0 - pd_close)/atr14_d ; |gap| > 1 ATR", "daily (known at bar 0 close)", True),
    ("dist_pd_high_bps / dist_pd_low_bps", "(c_j / pd_high - 1)*1e4 etc.", "1-min", True),
    ("ret_since_prev_close", "c_j / pd_close - 1 (simple return since last official close)", "1-min", True),
    ("cum_volume", "cumulative RTH volume through bar j", "1-min", True),
    ("rvol_tod", "cum_volume_j / mean(cum_volume at the same bar over the prior 20 sessions)", "1-min", True),
    ("cumvol_share", "cum_volume_j / mean(total RTH volume of prior 20 sessions)", "1-min", True),
    ("rvol_1m", "v_j / mean(v at the same bar over prior 20 sessions)", "1-min", True),
    ("ema9_1m / ema21_1m / ema_diff_1m_bps", "EMA(9)/EMA(21) of 1-min closes (session reset); diff in bps", "1-min", True),
    ("ema9_5m / ema21_5m / ema_diff_5m_bps", "EMAs of 5-min closes, updated when each 5-min bar completes, held in between", "5-min (on 1-min grid)", True),
    ("{SOXX,NVDA,QQQ,SMH}_ret_1m[_lag1,_lag2]", "driver 1-min log return (and lagged by 1/2 bars) on the same minute grid", "1-min", True),
    ("{driver}_ret_5m / {driver}_ret_since_prev_close", "driver 5-min log return ; driver c_j / prior official close - 1", "1-min", True),
    ("idx_ret_since_prev_close", "index-proxy (SOXX for SOXL/SOXS) return since its prior official close = r", "1-min", True),
    ("lev_implied", "L(1+r)/(1+L*r): exposure/NAV of a daily-reset L-x fund after index move r (L=+3 SOXL, -3 SOXS)", "1-min", True),
    ("tracking_gap_bps", "(ret_since_prev_close - L*r)*1e4: deviation from L x proxy move since the close", "1-min", True),
    ("lev_realized", "ret_since_prev_close / r when |r| > 0.25%", "1-min", True),
    ("soxl_soxs_div_bps", "(SOXL ret since prior close + SOXS ret since prior close)*1e4 (0 under perfect tracking)", "1-min", True),
    ("soxl_soxs_ret1m_sum_bps", "(SOXL 1-min log ret + SOXS 1-min log ret)*1e4", "1-min", True),
    ("minute_of_session / minutes_to_close", "bar index j (0 = 09:30) ; session bars remaining (half-days end 13:00)", "1-min", True),
    ("dow", "day of week (0 = Monday)", "daily", True),
    ("flag_is_half_day, flag_pre_holiday, flag_post_holiday", "early close (13:00) ; next / previous weekday is a market holiday", "daily", True),
    ("flag_month_end, flag_month_start, flag_quarter_end", "last / first trading day of month ; last trading day of quarter", "daily", True),
    ("flag_monthly_opex, flag_quad_witching", "3rd Friday (or prior trading day) ; same in Mar/Jun/Sep/Dec", "daily", True),
    ("flag_split, flag_exdiv", "split execution date / ex-dividend date of the ticker (from /v3/reference)", "daily", True),
    ("label_fwd_ret_1m / label_fwd_ret_5m / label_fwd_ret_to_close", "FUTURE log returns c_{j+k}/c_j - research labels only", "1-min", False),
]


def data_dictionary() -> pd.DataFrame:
    return pd.DataFrame(_DD, columns=["name", "definition", "granularity", "look_ahead_safe"])
