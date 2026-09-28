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


# --------------------------------------------------------------------------------------
# shared helpers for the 1-minute momentum-scalp studies (10: HH-like, 11: BZ-like)
# --------------------------------------------------------------------------------------
def sigma_tod(td, w: int = 20) -> np.ndarray:
    """RMS of 1-min returns in the same half-hour bucket over the prior ``w`` sessions, mapped to bars."""
    r = td.ret1
    D, B = r.shape
    nb = int(np.ceil(B / 30))
    ss = np.stack([np.nansum(r[:, b * 30:(b + 1) * 30] ** 2, axis=1) for b in range(nb)], axis=1)
    nn = np.stack([np.isfinite(r[:, b * 30:(b + 1) * 30]).sum(axis=1) for b in range(nb)], axis=1)
    sig = np.full((D, nb), np.nan)
    for d in range(1, D):
        lo = max(0, d - w)
        n = nn[lo:d].sum(axis=0)
        with np.errstate(all="ignore"):
            sig[d] = np.where((d - lo >= 15) & (n > 0), np.sqrt(ss[lo:d].sum(axis=0) / np.maximum(n, 1)), np.nan)
    return np.repeat(sig, 30, axis=1)[:, :B]


def _ema_session(x: np.ndarray, span: int) -> np.ndarray:
    from ..features import ema_cols
    return ema_cols(x, span)


def _exit_intent(rows, d, sig_bar, e, s, ep_level, stop, exit_, leg, flat, ep_est, target_hint=np.nan):
    """Append one intent for the exit scheme. ``ep_level`` = stop-order fill level (NaN = bar open)."""
    R = abs(ep_est - stop)
    if not np.isfinite(R) or R <= 0 or e >= flat:
        return False
    base = {"d": d, "sig": sig_bar, "e": e, "s": s, "stop": stop, "entry_px": ep_level, "tx_kind": "open"}
    if exit_ == "X2R":
        rows.append({**base, "target": ep_est + s * 2 * R, "tx": min(e + 30, flat)})
    elif exit_ == "XT":        # retest of the impulse extreme if it is >= 1R away, else 2R
        tgt = target_hint if (np.isfinite(target_hint) and s * (target_hint - ep_est) >= R) else ep_est + s * 2 * R
        rows.append({**base, "target": tgt, "tx": min(e + 30, flat)})
    elif exit_ == "XM":        # measured move: target passed in ``target_hint`` (entry + pole height); 60 min
        rows.append({**base, "target": target_hint, "tx": min(e + 60, flat)})
    elif exit_ == "XS":        # quick scalp: 1R target, 10-minute time stop
        rows.append({**base, "target": ep_est + s * R, "tx": min(e + 10, flat)})
    elif exit_ == "XSO":       # scale-out: leg A = 1R target / 30 min; leg B = trailing exit / 60 min
        if leg not in ("A", "B"):
            raise ValueError("XSO needs leg='A' or leg='B'")
        if leg == "A":
            rows.append({**base, "target": ep_est + s * R, "tx": min(e + 30, flat)})
        else:
            rows.append({**base, "target": np.nan, "tx": min(e + 60, flat)})
    else:
        raise ValueError(exit_)
    return True


# --------------------------------------------------------------------------------------
# Study 10: Hitchhiker-like opening-drive consolidation breakout (1-minute)
# --------------------------------------------------------------------------------------
def s10_hh_intents(ctx: Context, sig: str = "SOXL", entry: str = "stop", exit_: str = "X2R",
                   window_end: int = 29, drive_k: float = 3.0, min_cons: int = 3, max_cons: int = 15,
                   max_give: float = 0.4, entry_delay: int = 0, leg: str | None = None):
    td = ctx[sig]
    p = td.p
    sig_o = s2_sigma_open(td)
    ema9 = _ema_session(p.c, 9)
    rows = []
    for d in range(len(td.dates)):
        O = td.o0[d]
        if not (np.isfinite(sig_o[d]) and np.isfinite(O) and sig_o[d] > 0):
            continue
        h, l, o, c = p.h[d], p.l[d], p.o[d], p.c[d]
        flat = int(p.n_min[d]) - FLAT_OPEN
        tick = 0.01 / td.fac[d]
        found = None
        for t in range(min_cons + 2, min(window_end, flat - 2) + 1):
            for s in (1, -1):
                seg_h, seg_l = h[:t], l[:t]
                if not (np.isfinite(seg_h).any() and np.isfinite(seg_l).any()):
                    continue
                if s > 0:
                    pk = int(np.nanargmax(seg_h))
                    ext = seg_h[pk]
                    drive = ext / O - 1
                else:
                    pk = int(np.nanargmin(seg_l))
                    ext = seg_l[pk]
                    drive = 1 - ext / O
                ncons = t - 1 - pk
                if drive < drive_k * sig_o[d] or ncons < min_cons or ncons > max_cons:
                    continue
                if not np.isfinite(l[pk + 1:t]).any():
                    continue
                if s > 0:
                    box = np.nanmin(l[pk + 1:t])
                    if ext - box > max_give * (ext - O):
                        continue
                    level, stop = ext + tick, box - tick
                    hit = h[t] >= level if entry == "stop" else c[t] > ext
                else:
                    box = np.nanmax(h[pk + 1:t])
                    if box - ext > max_give * (O - ext):
                        continue
                    level, stop = ext - tick, box + tick
                    hit = l[t] <= level if entry == "stop" else c[t] < ext
                if hit:
                    found = (t, s, level, stop, ext)
                    break
            if found:
                break
        if not found:
            continue
        t, s, level, stop, ext = found
        if entry == "stop" and entry_delay == 0:
            e = t
            ep_level = max(o[t], level) if s > 0 else min(o[t], level)
            ep_est = ep_level
        else:
            e = t + (1 if entry == "stop" else 1 + entry_delay)
            ep_level = np.nan
            ep_est = o[e] if e < len(o) else np.nan
        if not np.isfinite(ep_est) or (s > 0 and stop >= ep_est) or (s < 0 and stop <= ep_est):
            continue
        _exit_intent(rows, d, t, e, s, ep_level, stop, exit_, leg, flat, ep_est)
    it = make_intents(rows)
    if exit_ == "XSO" and leg == "B":
        return it, {"exit_long": p.c < ema9, "exit_short": p.c > ema9}
    return it


# --------------------------------------------------------------------------------------
# Study 11: Bone Zone-like momentum pullback into the EMA9/EMA21 band (1-minute)
# --------------------------------------------------------------------------------------
def _roll_arg(a: np.ndarray, L: int, fn_arg) -> tuple[np.ndarray, np.ndarray]:
    """For each bar t: index (absolute) and value of fn over the inclusive window [t-L+1, t]."""
    from numpy.lib.stride_tricks import sliding_window_view as swv
    D, B = a.shape
    idx = np.full((D, B), -1)
    val = np.full((D, B), np.nan)
    filled = np.where(np.isfinite(a), a, np.inf if fn_arg is np.nanargmin else -np.inf)
    w = swv(filled, L, axis=1)
    k = (np.argmin(w, axis=2) if fn_arg is np.nanargmin else np.argmax(w, axis=2))
    idx[:, L - 1:] = k + np.arange(B - L + 1)[None, :]
    val[:, L - 1:] = np.take_along_axis(filled, idx[:, L - 1:], axis=1)
    val[~np.isfinite(val)] = np.nan
    return idx, val


def s11_bz_intents(ctx: Context, sig: str = "SOXL", entry: str = "close", exit_: str = "XT",
                   imp_k: float = 2.5, pull_min: int = 2, pull_max: int = 10, give_max: float = 0.5,
                   vol_ratio: float = 0.9, start_bar: int = 30, end_bar: int = 360, entry_delay: int = 0,
                   leg: str | None = None):
    """One intent per impulse peak (its first valid trigger). Overlaps and the 3-trades-a-day cap are
    applied after simulation by ``engine.filter_positions`` (so scale-out legs stay paired)."""
    td = ctx[sig]
    p = td.p
    o, h, l, c, v = p.o, p.h, p.l, p.c, np.nan_to_num(p.v)
    D, B = c.shape
    e9, e21 = _ema_session(c, 9), _ema_session(c, 21)
    stod = sigma_tod(td)
    cv = np.cumsum(v, axis=1)
    below9 = np.cumsum(np.nan_to_num(l <= e9).astype(int), axis=1)         # touches of the zone from above
    above9 = np.cumsum(np.nan_to_num(h >= e9).astype(int), axis=1)
    cl_lt21 = np.cumsum(np.nan_to_num(c < e21).astype(int), axis=1)        # closes below the zone floor
    cl_gt21 = np.cumsum(np.nan_to_num(c > e21).astype(int), axis=1)
    # candidate peak = extreme of the window [t-pull_max-1, t-1]
    pk_hi, _ = _roll_arg(h, pull_max + 1, np.nanargmax)
    pk_lo, _ = _roll_arg(l, pull_max + 1, np.nanargmin)
    base_lo_i, base_lo = _roll_arg(l, 16, np.nanargmin)                     # base within 15 bars before peak
    base_hi_i, base_hi = _roll_arg(h, 16, np.nanargmax)
    pl_min = {k: _roll_arg(l, k, np.nanargmin)[1] for k in range(1, pull_max + 1)}
    ph_max = {k: _roll_arg(h, k, np.nanargmax)[1] for k in range(1, pull_max + 1)}
    rows = []

    def seg_count(cs, d, a, b):          # count over bars a..b inclusive from a cumulative array
        return cs[d, b] - (cs[d, a - 1] if a > 0 else 0)

    for d in range(D):
        flat = int(p.n_min[d]) - FLAT_OPEN
        tick = 0.01 / td.fac[d]
        used = set()                      # (side, peak bar): each impulse peak is traded at most once
        for t in range(max(start_bar, pull_max + 17), min(end_bar, flat - 2) + 1):
            for s in (1, -1):
                if s > 0:
                    if not (e9[d, t] > e21[d, t] and c[d, t] > o[d, t] and c[d, t] >= e21[d, t]):
                        continue
                    pk = pk_hi[d, t - 1]
                else:
                    if not (e9[d, t] < e21[d, t] and c[d, t] < o[d, t] and c[d, t] <= e21[d, t]):
                        continue
                    pk = pk_lo[d, t - 1]
                npull = t - 1 - pk
                if pk < 16 or npull < pull_min or npull > pull_max or (s, pk) in used:
                    continue
                if s > 0:
                    ext, bi, bv = h[d, pk], base_lo_i[d, pk], base_lo[d, pk]
                    gain = ext / bv - 1
                else:
                    ext, bi, bv = l[d, pk], base_hi_i[d, pk], base_hi[d, pk]
                    gain = 1 - ext / bv
                nimp = pk - bi
                sg = stod[d, pk]
                if not (np.isfinite(gain) and np.isfinite(sg)) or nimp < 3 or gain < imp_k * sg * np.sqrt(nimp):
                    continue
                a, b = pk + 1, t - 1
                if s > 0:
                    if seg_count(below9, d, a, b) == 0 or seg_count(cl_lt21, d, a, b) > 0:
                        continue
                    pl = pl_min[npull][d, b]
                    if not np.isfinite(pl) or (ext - pl) > give_max * (ext - bv):
                        continue
                else:
                    if seg_count(above9, d, a, b) == 0 or seg_count(cl_gt21, d, a, b) > 0:
                        continue
                    pl = ph_max[npull][d, b]
                    if not np.isfinite(pl) or (pl - ext) > give_max * (bv - ext):
                        continue
                vol_pull = (cv[d, b] - cv[d, a - 1]) / npull
                vol_imp = (cv[d, pk] - (cv[d, bi - 1] if bi > 0 else 0)) / (nimp + 1)
                if not vol_pull <= vol_ratio * vol_imp:
                    continue
                stop = (min(pl, l[d, t]) - tick) if s > 0 else (max(pl, h[d, t]) + tick)
                if entry == "close":
                    e = t + 1 + entry_delay
                    ep_level, ep_est = np.nan, (o[d, e] if e < B else np.nan)
                else:
                    # buy (sell) stop one tick beyond the trigger candle, working for 3 bars; cancelled if the
                    # protective stop trades first
                    level = h[d, t] + tick if s > 0 else l[d, t] - tick
                    e = None
                    for u in range(t + 1, min(t + 4, flat)):
                        if (s > 0 and h[d, u] >= level) or (s < 0 and l[d, u] <= level):
                            e = u
                            break
                        if (s > 0 and l[d, u] <= stop) or (s < 0 and h[d, u] >= stop):
                            break
                    if e is None:
                        continue
                    if entry_delay:
                        e, ep_level = e + 1, np.nan
                        ep_est = o[d, e] if e < B else np.nan
                    else:
                        ep_level = max(o[d, e], level) if s > 0 else min(o[d, e], level)
                        ep_est = ep_level
                if not np.isfinite(ep_est) or (s > 0 and stop >= ep_est) or (s < 0 and stop <= ep_est):
                    continue
                if _exit_intent(rows, d, t, e, s, ep_level, stop, exit_, leg, flat, ep_est, target_hint=ext):
                    used.add((s, pk))
                break
    it = make_intents(rows)
    if exit_ == "XSO" and leg == "B":
        return it, {"exit_long": c < e21, "exit_short": c > e21}
    return it


# --------------------------------------------------------------------------------------
# Study 12: bull/bear-flag-like continuation (1-minute)
# --------------------------------------------------------------------------------------
def _roll_arg_pad(a: np.ndarray, L: int, fn_arg) -> tuple[np.ndarray, np.ndarray]:
    """``_roll_arg`` over [max(0, t-L+1), t] (partial windows at the session start); index -1 = none."""
    fill = np.inf if fn_arg is np.nanargmin else -np.inf
    D = a.shape[0]
    idx, val = _roll_arg(np.concatenate([np.full((D, L - 1), fill), a], axis=1), L, fn_arg)
    idx = idx[:, L - 1:] - (L - 1)
    return np.where(np.isfinite(val[:, L - 1:]), idx, -1), val[:, L - 1:]


def s12_flag_intents(ctx: Context, sig: str = "SOXL", entry: str = "stop", exit_: str = "XM",
                     imp_k: float = 2.5, flag_min: int = 3, flag_max: int = 12, give_max: float = 0.5,
                     vol_ratio: float = 0.9, start_bar: int = 10, end_bar: int = 360, entry_delay: int = 0,
                     leg: str | None = None):
    """Pole = move from the extreme of the 15 bars before the pole top, >= imp_k * sigma_tod * sqrt(bars);
    flag = flag_min..flag_max bars after the top, retracing <= give_max of the pole on lighter volume;
    trigger = a break of both the flag's resistance line (anchored at the pole top, through the highest
    later flag high; mirror for bear flags) and the prior bar's high. One intent per pole top; overlaps and
    the 3-a-day cap are applied after simulation (``engine.filter_positions``)."""
    td = ctx[sig]
    p = td.p
    o, h, l, c, v = p.o, p.h, p.l, p.c, np.nan_to_num(p.v)
    D, B = c.shape
    stod = sigma_tod(td)
    e9 = _ema_session(c, 9)
    cv = np.cumsum(v, axis=1)
    W = flag_max + 1
    tt = np.arange(B)[None, :]
    ext_roll = {1: _roll_arg_pad(h, W, np.nanargmax)[0], -1: _roll_arg_pad(l, W, np.nanargmin)[0]}
    base_roll = {1: _roll_arg_pad(l, 16, np.nanargmin)[0], -1: _roll_arg_pad(h, 16, np.nanargmax)[0]}
    worst_roll = {1: {k: _roll_arg(l, k, np.nanargmin)[1] for k in range(flag_min, flag_max + 1)},
                  -1: {k: _roll_arg(h, k, np.nanargmax)[1] for k in range(flag_min, flag_max + 1)}}

    def lag1(a, fill):
        out = np.full_like(a, fill)
        out[:, 1:] = a[:, :-1]
        return out

    # vectorised pre-screen (pole, flag length, giveback, volume) for every (day, trigger bar t)
    cand = {}
    for s in (1, -1):
        pk = lag1(ext_roll[s], -1)                        # pole top = extreme of [t-W, t-1]
        pkc = np.maximum(pk, 0)
        bi = np.take_along_axis(base_roll[s], pkc, axis=1)
        bic = np.maximum(bi, 0)
        ext = np.take_along_axis(h if s > 0 else l, pkc, axis=1)
        bv = np.take_along_axis(l if s > 0 else h, bic, axis=1)
        nflag, nimp = tt - 1 - pk, pk - bi
        sg = np.take_along_axis(stod, pkc, axis=1)
        with np.errstate(all="ignore"):
            pole = s * (ext - bv)
            m = (pk >= 0) & (bi >= 0) & (nflag >= flag_min) & (nflag <= flag_max) & (nimp >= 3) & \
                np.isfinite(pole) & np.isfinite(sg) & (pole >= imp_k * sg * np.sqrt(np.maximum(nimp, 1)) * bv)
            worst = np.full((D, B), np.nan)
            for k, src in worst_roll[s].items():
                worst = np.where(m & (nflag == k), lag1(src, np.nan), worst)
            m &= np.isfinite(worst) & (s * (ext - worst) <= give_max * pole)
            cv_pk = np.take_along_axis(cv, pkc, axis=1)
            cv_b0 = np.where(bi > 0, np.take_along_axis(cv, np.maximum(bic - 1, 0), axis=1), 0.0)
            m &= (lag1(cv, np.nan) - cv_pk) / np.maximum(nflag, 1) <= vol_ratio * (cv_pk - cv_b0) / (nimp + 1)
        cand[s] = (m, pk, bi, ext, bv, pole, worst)
    rows, used = [], set()
    for d, t in np.argwhere(cand[1][0] | cand[-1][0]):
        flat = int(p.n_min[d]) - FLAT_OPEN
        if t < start_bar or t > min(end_bar, flat - 2):
            continue
        tick = 0.01 / td.fac[d]
        hd, ld, od, cd = h[d], l[d], o[d], c[d]
        for s in (1, -1):
            m, PK, _, EXT, _, POLE, WORST = cand[s]
            if not m[d, t] or (d, s, int(PK[d, t])) in used:
                continue
            pk, ext, pole, worst = int(PK[d, t]), EXT[d, t], POLE[d, t], WORST[d, t]
            jj = np.arange(pk + 1, t)
            fh, fl = hd[pk + 1:t], ld[pk + 1:t]
            ok = np.isfinite(fh) & np.isfinite(fl)
            if s > 0:
                slope = np.max((fh[ok] - ext) / (jj[ok] - pk))              # <= 0: resistance through the highs
                line = ext + slope * (t - pk)
                trig = max(line, hd[t - 1]) if np.isfinite(hd[t - 1]) else line
                hit = (hd[t] >= trig + tick) if entry == "stop" else (cd[t] > trig)
            else:
                slope = np.min((fl[ok] - ext) / (jj[ok] - pk))              # >= 0: support through the lows
                line = ext + slope * (t - pk)
                trig = min(line, ld[t - 1]) if np.isfinite(ld[t - 1]) else line
                hit = (ld[t] <= trig - tick) if entry == "stop" else (cd[t] < trig)
            if not hit:
                continue
            if entry == "stop" and entry_delay == 0:
                e = t
                lvl = trig + s * tick
                ep_level = max(od[t], lvl) if s > 0 else min(od[t], lvl)
                ep_est = ep_level
                stop = worst - s * tick
            else:
                e = t + 1 + (entry_delay if entry == "close" else 0)
                ep_level = np.nan
                ep_est = od[e] if e < B else np.nan
                stop = (min(worst, ld[t]) - tick) if s > 0 else (max(worst, hd[t]) + tick)
            if not np.isfinite(ep_est) or (s > 0 and stop >= ep_est) or (s < 0 and stop <= ep_est):
                continue
            if _exit_intent(rows, d, t, e, s, ep_level, stop, exit_, leg, flat, ep_est,
                            target_hint=ep_est + s * pole):
                used.add((d, s, pk))
            break
    it = make_intents(rows)
    if exit_ == "XSO" and leg == "B":
        return it, {"exit_long": c < e9, "exit_short": c > e9}
    return it
