"""Behavior-probe signal generators.

Each generator returns a ``SignalSet``: entries (+1 long / -1 short at the CLOSE of bar j), optional
exit signals, stop / target levels and ``Rules``. All inputs come from ``features.compute_features``
(look-ahead safe) and the panel's own bars up to j. Canonical parameters were fixed before looking at
any results; the small grids in ``PROBES`` are used only for in-sample selection demos.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .backtest import Rules
from .data import Panel
from .features import rolling_sum_cols, shift_cols


@dataclass
class SignalSet:
    entries: np.ndarray
    rules: Rules = field(default_factory=Rules)
    stop_px: np.ndarray | None = None
    tp_px: np.ndarray | None = None
    stop_bps_arr: np.ndarray | None = None
    exit_long: np.ndarray | None = None
    exit_short: np.ndarray | None = None


def _J(p: Panel) -> np.ndarray:
    return np.broadcast_to(np.arange(p.c.shape[1])[None, :], p.c.shape)


def _first_true(mask: np.ndarray) -> np.ndarray:
    """Index of first True per row (-1 if none)."""
    anyt = mask.any(axis=1)
    idx = mask.argmax(axis=1)
    return np.where(anyt, idx, -1)


def _cross(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Boolean up/down crossings of zero for a series a (causal: compares j with j-1)."""
    prev = shift_cols(a, 1)
    up = (a > 0) & (prev <= 0)
    dn = (a < 0) & (prev >= 0)
    return up, dn


def _sigma_prev(r: np.ndarray, w: int = 60) -> np.ndarray:
    """RMS of 1-min returns over the previous w bars (excludes bar j)."""
    ss = rolling_sum_cols(np.nan_to_num(r) ** 2, w)
    return shift_cols(np.sqrt(ss / w), 1)


# --------------------------------------------------------------------------------------
# probes
# --------------------------------------------------------------------------------------
def orb(F, p: Panel, n: int = 15, tp_mult: float | None = None, **_) -> SignalSet:
    """Opening-range breakout: first close outside the N-minute range; stop = opposite side."""
    J = _J(p)
    c = p.c
    hi, lo = F[f"or{n}_high"], F[f"or{n}_low"]
    up = (c > hi) & (J >= n)
    dn = (c < lo) & (J >= n)
    fu, fd = _first_true(up), _first_true(dn)
    E = np.zeros(c.shape, np.int8)
    stop = np.full(c.shape, np.nan)
    tp = np.full(c.shape, np.nan)
    for d in range(c.shape[0]):
        a, b = fu[d], fd[d]
        if a < 0 and b < 0:
            continue
        if b < 0 or (0 <= a < b):
            j, s = a, 1
        else:
            j, s = b, -1
        E[d, j] = s
        rng = hi[d, j] - lo[d, j]
        stop[d, j] = lo[d, j] if s > 0 else hi[d, j]
        if tp_mult:
            tp[d, j] = c[d, j] + s * tp_mult * rng
    return SignalSet(E, Rules(earliest_entry_bar=n), stop_px=stop, tp_px=tp if tp_mult else None)


def vwap_reversion(F, p: Panel, k_entry: float = 2.0, k_stop: float = 3.0, max_hold: int = 60,
                   start_bar: int = 15, **_) -> SignalSet:
    """Fade closes that move beyond the k-sigma VWAP band; exit at VWAP, stop at the 3-sigma band."""
    J = _J(p)
    c, vwap, sd = p.c, F["vwap"], F["vwap_sd"]
    z = F["dist_vwap_sd"]
    lo_hit = (z < -k_entry) & (shift_cols(z, 1) >= -k_entry)
    hi_hit = (z > k_entry) & (shift_cols(z, 1) <= k_entry)
    ok = (J >= start_bar) & (sd > 0)
    E = np.where(lo_hit & ok, 1, np.where(hi_hit & ok, -1, 0)).astype(np.int8)
    stop = np.where(E > 0, vwap - k_stop * sd, np.where(E < 0, vwap + k_stop * sd, np.nan))
    return SignalSet(E, Rules(max_hold=max_hold, earliest_entry_bar=start_bar + 1), stop_px=stop,
                     exit_long=c >= vwap, exit_short=c <= vwap)


def vwap_trend(F, p: Panel, start_bar: int = 15, **_) -> SignalSet:
    """Follow VWAP crosses: long on a close crossing above VWAP, short below; reverse on the next cross."""
    J = _J(p)
    up, dn = _cross(p.c - F["vwap"])
    ok = J >= start_bar
    E = np.where(up & ok, 1, np.where(dn & ok, -1, 0)).astype(np.int8)
    return SignalSet(E, Rules(earliest_entry_bar=start_bar + 1), exit_long=dn, exit_short=up)


def large_move(F, p: Panel, horizon: int = 1, z: float = 3.0, hold: int = 5, mode: str = "momentum",
               start_bar: int = 30, **_) -> SignalSet:
    """After a |return| > z-sigma move over 1 or 5 minutes, trade with (momentum) or against (reversal)."""
    J = _J(p)
    r1 = F["ret_1m"]
    sig = _sigma_prev(r1, 60) * np.sqrt(horizon)
    r = r1 if horizon == 1 else F[f"ret_{horizon}m"]
    big = (np.abs(r) > z * sig) & (sig > 0) & (J >= start_bar)
    if horizon > 1:  # first bar of a trigger episode only
        big = big & ~shift_cols(big.astype(float), 1).astype(bool)
    s = np.sign(r) * (1 if mode == "momentum" else -1)
    E = np.where(big, s, 0).astype(np.int8)
    return SignalSet(E, Rules(max_hold=hold, earliest_entry_bar=start_bar + 1))


def ema_cross(F, p: Panel, tf: str = "1m", start_bar: int | None = None, **_) -> SignalSet:
    """EMA(9) / EMA(21) crossover on 1-min or 5-min closes (session reset); always reverse on the next cross."""
    J = _J(p)
    diff = F[f"ema_diff_{tf}_bps"]
    up, dn = _cross(diff)
    sb = start_bar if start_bar is not None else (30 if tf == "1m" else 60)
    ok = J >= sb
    E = np.where(up & ok, 1, np.where(dn & ok, -1, 0)).astype(np.int8)
    return SignalSet(E, Rules(earliest_entry_bar=sb + 1), exit_long=dn, exit_short=up)


def last30(F, p: Panel, signal: str = "day", **_) -> SignalSet:
    """Intraday momentum into the close: sign of (prior close -> 15:30) return [or prior close -> 10:00],
    entered at the 15:30 open and exited at the 15:55 open (12:30 -> 12:55 on half-days)."""
    E = np.zeros(p.c.shape, np.int8)
    rsc = F["ret_since_prev_close"]
    for d in range(p.c.shape[0]):
        jsig = int(p.n_min[d]) - 31
        src = rsc[d, jsig] if signal == "day" else rsc[d, 29]
        if np.isfinite(src) and src != 0:
            E[d, jsig] = int(np.sign(src))
    return SignalSet(E, Rules(earliest_entry_bar=1))


def lead_lag(F, p: Panel, driver: str = "NVDA", z: float = 2.0, hold: int = 1, lev_sign: float = 1.0,
             start_bar: int = 5, **_) -> SignalSet:
    """Driver 1-min move beyond z-sigma -> trade the ETF in the implied direction at the next open."""
    J = _J(p)
    rd = F[f"{driver}_ret_1m"]
    sig = _sigma_prev(rd, 60)
    big = (np.abs(rd) > z * sig) & (sig > 0) & (J >= start_bar)
    E = np.where(big, np.sign(rd) * np.sign(lev_sign), 0).astype(np.int8)
    return SignalSet(E, Rules(max_hold=hold, earliest_entry_bar=start_bar + 1))


def gap_fill(F, p: Panel, min_gap_atr: float = 0.5, stop_mult: float = 1.0, **_) -> SignalSet:
    """Fade opening gaps larger than min_gap_atr x daily ATR: target = prior close, stop = 1 gap beyond the open."""
    E = np.zeros(p.c.shape, np.int8)
    stop = np.full(p.c.shape, np.nan)
    tp = np.full(p.c.shape, np.nan)
    ga, pc = F["gap_atr"][:, 0], F["pd_close"][:, 0]
    o0 = p.o[:, 0]
    for d in range(p.c.shape[0]):
        if np.isfinite(ga[d]) and abs(ga[d]) > min_gap_atr and np.isfinite(o0[d]):
            s = -int(np.sign(ga[d]))
            g = o0[d] - pc[d]
            E[d, 0] = s
            tp[d, 0] = pc[d]
            stop[d, 0] = o0[d] + np.sign(g) * stop_mult * abs(g)
    return SignalSet(E, Rules(earliest_entry_bar=1), stop_px=stop, tp_px=tp)


# --------------------------------------------------------------------------------------
# probe registry: canonical parameters (fixed a priori) + small IS-selection grids
# --------------------------------------------------------------------------------------
PROBES = {
    # name: (generator, canonical params, grid list)
    "orb5": (orb, {"n": 5}, [{"n": 5}, {"n": 5, "tp_mult": 2.0}]),
    "orb15": (orb, {"n": 15}, [{"n": 15}, {"n": 15, "tp_mult": 2.0}]),
    "orb30": (orb, {"n": 30}, [{"n": 30}, {"n": 30, "tp_mult": 2.0}]),
    "vwap_reversion": (vwap_reversion, {"k_entry": 2.0, "k_stop": 3.0, "max_hold": 60},
                       [{"k_entry": k, "k_stop": k + 1, "max_hold": h} for k in (1.5, 2.0, 2.5) for h in (30, 60)]),
    "vwap_trend": (vwap_trend, {"start_bar": 15}, [{"start_bar": s} for s in (15, 30, 60)]),
    "mom_1m_z3": (large_move, {"horizon": 1, "z": 3.0, "hold": 5, "mode": "momentum"},
                  [{"horizon": 1, "z": z, "hold": h, "mode": "momentum"} for z in (3.0, 4.0) for h in (1, 5, 15, 30)]),
    "rev_1m_z3": (large_move, {"horizon": 1, "z": 3.0, "hold": 5, "mode": "reversal"},
                  [{"horizon": 1, "z": z, "hold": h, "mode": "reversal"} for z in (3.0, 4.0) for h in (1, 5, 15, 30)]),
    "mom_5m_z3": (large_move, {"horizon": 5, "z": 3.0, "hold": 15, "mode": "momentum"},
                  [{"horizon": 5, "z": z, "hold": h, "mode": "momentum"} for z in (3.0, 4.0) for h in (5, 15, 30)]),
    "rev_5m_z3": (large_move, {"horizon": 5, "z": 3.0, "hold": 15, "mode": "reversal"},
                  [{"horizon": 5, "z": z, "hold": h, "mode": "reversal"} for z in (3.0, 4.0) for h in (5, 15, 30)]),
    "ema_1m": (ema_cross, {"tf": "1m"}, [{"tf": "1m", "start_bar": s} for s in (15, 30, 60)]),
    "ema_5m": (ema_cross, {"tf": "5m"}, [{"tf": "5m", "start_bar": s} for s in (30, 60, 90)]),
    "last30_day": (last30, {"signal": "day"}, [{"signal": "day"}, {"signal": "first30"}]),
    "last30_first30": (last30, {"signal": "first30"}, [{"signal": "first30"}]),
    "leadlag_nvda": (lead_lag, {"driver": "NVDA", "z": 2.0, "hold": 1},
                     [{"driver": "NVDA", "z": z, "hold": h} for z in (2.0, 3.0) for h in (1, 5)]),
    "leadlag_soxx": (lead_lag, {"driver": "SOXX", "z": 2.0, "hold": 1},
                     [{"driver": "SOXX", "z": z, "hold": h} for z in (2.0, 3.0) for h in (1, 5)]),
    "gap_fill": (gap_fill, {"min_gap_atr": 0.5, "stop_mult": 1.0},
                 [{"min_gap_atr": g, "stop_mult": s} for g in (0.25, 0.5, 1.0) for s in (1.0, 2.0)]),
}

PROBE_FAMILY = {
    "orb5": "opening-range breakout", "orb15": "opening-range breakout", "orb30": "opening-range breakout",
    "vwap_reversion": "VWAP reversion", "vwap_trend": "VWAP trend-follow",
    "mom_1m_z3": "momentum after large 1-min move", "rev_1m_z3": "reversal after large 1-min move",
    "mom_5m_z3": "momentum after large 5-min move", "rev_5m_z3": "reversal after large 5-min move",
    "ema_1m": "EMA(9/21) crossover 1-min", "ema_5m": "EMA(9/21) crossover 5-min",
    "last30_day": "last-30-min momentum (prior close->15:30 signal)",
    "last30_first30": "last-30-min momentum (prior close->10:00 signal)",
    "leadlag_nvda": "lead-lag NVDA -> ETF next minute", "leadlag_soxx": "lead-lag SOXX -> ETF next minute",
    "gap_fill": "gap fill (fade gaps > 0.5 ATR)",
}


def make_signals(name: str, F, p: Panel, lev_sign: float = 1.0, params: dict | None = None) -> SignalSet:
    gen, canon, _grid = PROBES[name]
    kw = dict(canon if params is None else params)
    if gen is lead_lag:
        kw["lev_sign"] = lev_sign
    return gen(F, p, **kw)


# --------------------------------------------------------------------------------------
# transformations used by switch mode and timing diagnostics
# --------------------------------------------------------------------------------------
def to_relative(ss: SignalSet, p: Panel) -> tuple[SignalSet, np.ndarray | None]:
    """Express price-level stops/targets as distances (bps) from the signal-bar close, so they can be
    applied to another instrument (switch mode) or another day (shuffle diagnostic)."""
    stop_bps = ss.stop_bps_arr
    if ss.stop_px is not None:
        stop_bps = np.abs(ss.stop_px / p.c - 1) * 1e4
    if ss.tp_px is not None:
        tp_bps = np.abs(ss.tp_px / p.c - 1) * 1e4
    else:
        tp_bps = None
    return SignalSet(ss.entries, ss.rules, None, None, stop_bps, ss.exit_long, ss.exit_short), tp_bps


def shift_signalset(ss: SignalSet, k: int) -> SignalSet:
    """Delay (k>0) or advance (k<0, look-ahead diagnostic) every per-bar array by k bars within the day."""
    def sh(a, fill):
        if a is None:
            return None
        out = np.full_like(a, fill)
        if k > 0:
            out[:, k:] = a[:, :-k]
        elif k < 0:
            out[:, :k] = a[:, -k:]
        else:
            out[:] = a
        return out
    return SignalSet(sh(ss.entries, 0), ss.rules, sh(ss.stop_px, np.nan), sh(ss.tp_px, np.nan),
                     sh(ss.stop_bps_arr, np.nan), sh(ss.exit_long, False), sh(ss.exit_short, False))
