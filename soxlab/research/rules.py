"""Signal generators for the pre-registered studies (see analysis/strategies/REGISTRY.md).

Every generator works on one ticker's regular-session panel (the "signal chart") and returns either
intents for ``engine.simulate`` or, for the stateful Study 4, finished signal-chart trades. All inputs
at a decision bar j use only bars <= j of the same day, pre-market bars of the same day and prior days.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .common import Context
from .engine import make_intents

FLAT_OPEN = 5          # flat at the open of the bar 5 minutes before the session end (15:55)
INDEX_FOR = {"SOXL": "SOXX", "SOXX": "SOXX", "SMH": "SOXX", "NVDA": "SOXX", "SOXS": "SOXX",
             "QQQ": "QQQ", "TQQQ": "QQQ", "SPY": "SPY"}


def _prior_window_stat(x: np.ndarray, w: int, fn, min_n: int) -> np.ndarray:
    """fn over x[d-w .. d-1] (finite values only) for each day d."""
    out = np.full(len(x), np.nan)
    for d in range(1, len(x)):
        blk = x[max(0, d - w):d]
        blk = blk[np.isfinite(blk)]
        if len(blk) >= min_n:
            out[d] = fn(blk)
    return out


# --------------------------------------------------------------------------------------
# Study 1: late-day fade
# --------------------------------------------------------------------------------------
def s1_gate_slope(td, window: int = 120, min_n: int = 60) -> np.ndarray:
    """OLS slope of (15:30->15:59 close) on (09:30 open->15:30) over the prior ``window`` full sessions."""
    c = td.p.c
    x = np.where(td.full, c[:, 359] / td.o0 - 1, np.nan)
    y = np.where(td.full, c[:, 389] / c[:, 359] - 1, np.nan)
    out = np.full(len(x), np.nan)
    for d in range(1, len(x)):
        lo = max(0, d - window)
        xx, yy = x[lo:d], y[lo:d]
        ok = np.isfinite(xx) & np.isfinite(yy)
        if ok.sum() >= min_n:
            xv, yv = xx[ok], yy[ok]
            vx = np.var(xv)
            out[d] = np.cov(xv, yv, bias=True)[0, 1] / vx if vx > 0 else np.nan
    return out


def s1_intents(ctx: Context, sig: str = "SOXL", thr: float = 0.01, gate: bool = True, exit_: str = "E1",
               entry_delay: int = 0, exec_mode: str = "switch") -> pd.DataFrame:
    td, ix = ctx[sig], ctx[INDEX_FOR[sig]]
    c = td.p.c
    D = c[:, 359] / td.pc - 1
    R = ix.p.c[:, 359] / ix.pc - 1
    slope = s1_gate_slope(td)
    y = np.where(td.full, c[:, 389] / c[:, 359] - 1, np.nan)
    sig30 = _prior_window_stat(y, 20, lambda b: float(np.sqrt(np.mean(b ** 2))), 15)
    rows = []
    for d in np.flatnonzero(td.full):
        if not (np.isfinite(D[d]) and np.isfinite(R[d]) and np.isfinite(sig30[d])) or D[d] == 0:
            continue
        if abs(R[d]) < thr:
            continue
        if gate and not (np.isfinite(slope[d]) and slope[d] < 0):
            continue
        s = -int(np.sign(D[d]))
        e = 360 + entry_delay
        ep = td.p.o[d, e]
        if not np.isfinite(ep):
            continue
        stop = ep * (1 - s * 1.5 * sig30[d])
        if exit_ == "E1":
            tx, kind = 385, "open"
        elif exit_ == "E2":
            tx, kind = 389, "close"
        else:   # E3: auction exit; in switch mode only for SOXL legs (SOXS legs use E2)
            tx, kind = 389, ("official" if (s > 0 or exec_mode == "ls") else "close")
        rows.append({"d": d, "sig": 359, "e": e, "s": s, "stop": stop, "tx": tx, "tx_kind": kind})
    return make_intents(rows)


# --------------------------------------------------------------------------------------
# Study 2: opening burst continuation
# --------------------------------------------------------------------------------------
def s2_sigma_open(td, w: int = 20) -> np.ndarray:
    r = td.ret1[:, 1:30]                                   # bars 09:31 .. 09:59
    ss = np.nansum(r ** 2, axis=1)
    nn = np.isfinite(r).sum(axis=1).astype(float)
    out = np.full(len(ss), np.nan)
    for d in range(1, len(ss)):
        lo = max(0, d - w)
        n = nn[lo:d].sum()
        if (d - lo) >= 15 and n > 0:
            out[d] = np.sqrt(ss[lo:d].sum() / n)
    return out


def s2_intents(ctx: Context, sig: str = "SOXL", k: float = 2.0, hold: int = 1, filt: str = "F0",
               entry_delay: int = 0, max_trades: int = 3) -> pd.DataFrame:
    td = ctx[sig]
    p = td.p
    r = td.ret1
    sig_o = s2_sigma_open(td)
    vmean = td.minute_mean_prior(np.where(p.valid(), p.v, np.nan), 20) if filt == "F1" else None
    gap = td.o0 / td.pc - 1
    rows = []
    for d in range(len(td.dates)):
        if not np.isfinite(sig_o[d]) or sig_o[d] <= 0:
            continue
        z = r[d, 1:29] / sig_o[d]                          # trigger bars 1..28 (09:31 .. 09:58)
        cand = np.flatnonzero(np.abs(z) >= k) + 1
        taken, free = 0, 0
        for t in cand:
            s = int(np.sign(r[d, t]))
            if s == 0:
                continue
            if filt == "F1" and not (np.isfinite(vmean[d, t]) and p.v[d, t] >= 2 * vmean[d, t]):
                continue
            if filt == "F2":
                rng = p.h[d, t] - p.l[d, t]
                if not rng > 0:
                    continue
                loc = (p.c[d, t] - p.l[d, t]) / rng
                if (s > 0 and loc < 0.75) or (s < 0 and loc > 0.25):
                    continue
            if filt == "F3" and not (np.isfinite(gap[d]) and np.sign(gap[d]) == s):
                continue
            e = t + 1 + entry_delay
            if e < free:
                continue
            tx = e + hold
            ep = p.o[d, e]
            if not np.isfinite(ep):
                continue
            stop = ep * (1 - s * sig_o[d]) if hold > 1 else np.nan
            rows.append({"d": d, "sig": t, "e": e, "s": s, "stop": stop, "tx": tx, "tx_kind": "open"})
            free = tx
            taken += 1
            if taken >= max_trades:
                break
    return make_intents(rows)


# --------------------------------------------------------------------------------------
# Study 3: opening-range breakout
# --------------------------------------------------------------------------------------
def rvol_first(td, n: int = 5, w: int = 14) -> np.ndarray:
    v = np.nansum(td.p.v[:, :n], axis=1)
    base = _prior_window_stat(v, w, np.mean, max(5, w // 2))
    with np.errstate(all="ignore"):
        return v / base


def s3_intents(ctx: Context, sig: str = "SOXL", design: str = "A", rvol_min: float | None = None,
               atr_stop: float | None = None, e1: bool = False, e2: bool = False, trail: float | None = None,
               or_len: int = 15, candle_len: int = 5, band=(20, 80), e2_pct: float = 60,
               entry_delay: int = 0) -> pd.DataFrame:
    td = ctx[sig]
    p = td.p
    rv = rvol_first(td, 5, 14) if rvol_min is not None else None
    or_hi = np.nanmax(p.h[:, :or_len], axis=1)
    or_lo = np.nanmin(p.l[:, :or_len], axis=1)
    or_size = or_hi / or_lo - 1
    if e1:
        lo_b = _prior_window_stat(or_size, 60, lambda b: np.percentile(b, band[0]), 40)
        hi_b = _prior_window_stat(or_size, 60, lambda b: np.percentile(b, band[1]), 40)
    if e2:
        rp = td.range_pct
        prev_rank_ok = np.full(len(rp), False)
        for d in range(61, len(rp)):
            win = rp[d - 60:d]
            win = win[np.isfinite(win)]
            if len(win) >= 40 and np.isfinite(rp[d - 1]):
                prev_rank_ok[d] = rp[d - 1] >= np.percentile(win, e2_pct)
    rows = []
    for d in range(len(td.dates)):
        nmin = int(p.n_min[d])
        tx = nmin - FLAT_OPEN
        if rv is not None and not (np.isfinite(rv[d]) and rv[d] >= rvol_min):
            continue
        if design == "A":
            if e1 and not (np.isfinite(lo_b[d]) and lo_b[d] <= or_size[d] <= hi_b[d]):
                continue
            if e2 and not prev_rank_ok[d]:
                continue
            cc = p.c[d, or_len:tx - 1]
            up = np.flatnonzero(cc > or_hi[d])
            dn = np.flatnonzero(cc < or_lo[d])
            if not up.size and not dn.size:
                continue
            if up.size and (not dn.size or up[0] < dn[0]):
                j, s = or_len + int(up[0]), 1
            else:
                j, s = or_len + int(dn[0]), -1
            e = j + 1 + entry_delay
            if e >= tx:
                continue
            ep = p.o[d, e]
            stop = or_lo[d] if s > 0 else or_hi[d]
            tgt = np.nan
        else:   # design B: first candle of ``candle_len`` minutes
            O = td.o0[d]
            C = p.c[d, candle_len - 1]
            H = np.nanmax(p.h[d, :candle_len])
            L = np.nanmin(p.l[d, :candle_len])
            if not (np.isfinite(O) and np.isfinite(C) and H > L) or abs(C - O) < 0.1 * (H - L):
                continue
            s = int(np.sign(C - O))
            j = candle_len - 1
            e = candle_len + entry_delay
            ep = p.o[d, e]
            stop = L if s > 0 else H
            tgt = np.nan
        if not np.isfinite(ep):
            continue
        if atr_stop is not None:
            if not np.isfinite(td.atr_prev[d]):
                continue
            stop = ep - s * atr_stop * td.atr_prev[d]
        if (s > 0 and stop >= ep) or (s < 0 and stop <= ep):
            continue          # entry already beyond the stop: no valid risk
        if design == "B":
            tgt = ep + s * 10 * abs(ep - stop)
        rows.append({"d": d, "sig": j, "e": e, "s": s, "stop": stop, "target": tgt, "tx": tx,
                     "tx_kind": "open", "trail_r": trail if trail else np.nan})
    return make_intents(rows)


# --------------------------------------------------------------------------------------
# Study 4: noise-boundary momentum (stateful; returns signal-chart trades)
# --------------------------------------------------------------------------------------
CHECK_BARS = list(range(29, 360, 30))       # bar closes at 10:00, 10:30, ..., 15:30


def s4_sigma_move(td, lookback: int = 14) -> np.ndarray:
    """sigma_move[d, t] = mean over the prior ``lookback`` full sessions of |c[k,t]/open_k - 1|."""
    a = np.abs(td.p.c / td.o0[:, None] - 1)
    a = np.where(td.full[:, None], a, np.nan)
    out = np.full_like(a, np.nan)
    idx_full = np.flatnonzero(td.full)
    for d in range(len(a)):
        prev = idx_full[idx_full < d][-lookback:]
        if len(prev) >= lookback:
            out[d] = np.nanmean(a[prev], axis=0)
    return out


def s4_trades(ctx: Context, sig: str = "SOXL", k: float = 1.0, check: str = "M", lookback: int = 14,
              entry_delay: int = 0) -> pd.DataFrame:
    td = ctx[sig]
    p = td.p
    sm = s4_sigma_move(td, lookback)
    vw = td.vwap
    recs = []
    for d in np.flatnonzero(td.full):
        if not (np.isfinite(td.o0[d]) and np.isfinite(td.pc[d])) or not np.isfinite(sm[d, 29]):
            continue
        up_ref, dn_ref = max(td.o0[d], td.pc[d]), min(td.o0[d], td.pc[d])
        UB = up_ref * (1 + k * sm[d])
        LB = dn_ref * (1 - k * sm[d])
        c = p.c[d]
        tx = 390 - FLAT_OPEN
        pos, e_bar, ep = 0, -1, np.nan

        def close_pos(xb, why):
            recs.append((d, e_bar - 1 - entry_delay, e_bar, xb, pos, ep, p.o[d, xb], "open", why))

        for t in range(0, tx):
            desired = 0
            is_check = t in CHECK_BARS
            if is_check:
                if c[t] > UB[t]:
                    desired = 1
                elif c[t] < LB[t]:
                    desired = -1
            nxt = t + 1 + entry_delay
            if is_check and desired != 0 and desired != pos and nxt < tx:
                if pos != 0 and t >= e_bar:
                    close_pos(t + 1, "reverse")
                pos, e_bar, ep = desired, nxt, p.o[d, nxt]
                continue
            if pos != 0 and t >= e_bar and (check == "M" or is_check):
                if (pos > 0 and c[t] < max(UB[t], vw[d, t])) or (pos < 0 and c[t] > min(LB[t], vw[d, t])):
                    close_pos(t + 1, "trail")
                    pos, e_bar, ep = 0, -1, np.nan
        if pos != 0:
            close_pos(tx, "time")
    tr = pd.DataFrame(recs, columns=["d", "sig", "e", "xb", "s", "ep", "xp", "x_kind", "reason"])
    tr = tr[np.isfinite(tr["ep"]) & np.isfinite(tr["xp"]) & (tr["xb"] > tr["e"])].reset_index(drop=True)
    tr["date"] = td.dates[tr["d"].to_numpy()] if len(tr) else pd.Series(dtype="datetime64[ns]")
    tr["gross_chart_bps"] = tr["s"] * (tr["xp"] / tr["ep"] - 1) * 1e4
    return tr


# --------------------------------------------------------------------------------------
# Study 6: failed-break fade at key levels
# --------------------------------------------------------------------------------------
def s6_intents(ctx: Context, sig: str = "SOXL", level: str = "PM", target: str = "T1", window: int = 60,
               fail_window: int = 10, buffer: float = 0.001, time_stop: int = 20,
               entry_delay: int = 0) -> pd.DataFrame:
    td = ctx[sig]
    p = td.p
    if level == "PM":
        pm = td.premarket
        hi_lv = pm["pm_high"].to_numpy(float)
        lo_lv = pm["pm_low"].to_numpy(float)
        ok_lv = pm["pm_bars"].fillna(0).to_numpy() >= 5
    else:
        hi_lv = np.concatenate([[np.nan], td.hi[:-1]])
        lo_lv = np.concatenate([[np.nan], td.lo[:-1]])
        ok_lv = np.isfinite(hi_lv)
    vw = td.vwap
    rows = []
    for d in range(len(td.dates)):
        if not ok_lv[d]:
            continue
        nmin = int(p.n_min[d])
        tick = 0.01 / td.fac[d]
        cands = []
        for lv, s in ((hi_lv[d], -1), (lo_lv[d], 1)):           # failed high -> bearish; failed low -> bullish
            if not np.isfinite(lv):
                continue
            hh, ll = p.h[d, :window], p.l[d, :window]
            brk = np.flatnonzero(hh >= lv + tick) if s < 0 else np.flatnonzero(ll <= lv - tick)
            if not brk.size:
                continue
            b = int(brk[0])
            seg = p.c[d, b:b + fail_window + 1]
            back = np.flatnonzero(seg < lv) if s < 0 else np.flatnonzero(seg > lv)
            if not back.size:
                continue
            f = b + int(back[0])
            e = f + 1 + entry_delay
            tx = min(e + time_stop, nmin - FLAT_OPEN)
            if e >= tx:
                continue
            ep = p.o[d, e]
            if not np.isfinite(ep):
                continue
            ext = np.nanmax(p.h[d, b:f + 1]) if s < 0 else np.nanmin(p.l[d, b:f + 1])
            stop = ext * (1 + buffer) if s < 0 else ext * (1 - buffer)
            if (s > 0 and stop >= ep) or (s < 0 and stop <= ep):
                continue
            if target == "T1":
                tgt = ep + s * abs(ep - stop)
            else:
                tgt = vw[d, f]
                if not ((s > 0 and tgt > ep) or (s < 0 and tgt < ep)):
                    tgt = np.nan
            cands.append({"d": d, "sig": f, "e": e, "s": s, "stop": stop, "target": tgt, "tx": tx,
                          "tx_kind": "open"})
        rows.extend(sorted(cands, key=lambda r: r["e"]))
    return make_intents(rows)
