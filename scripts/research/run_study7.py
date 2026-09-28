#!/usr/bin/env python3
"""Study 7, stage 1: 1-minute chart-pattern event study on SOXL (REGISTRY.md).

Development period only. For each pattern x context x horizon: signed forward return from the next
bar's open, minus the time-of-day baseline, minus the case-B SOXL round-trip cost. A combination passes
stage 1 when net >= +5 bps, day-clustered t >= 2 and BH q <= 0.10 across the 60 tests.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as swv

import warnings

from runlib import Runner  # noqa: I001

warnings.filterwarnings("ignore", category=RuntimeWarning)
from soxlab.research import common as C

H_LIST = [1, 5, 15, 30]
PATTERNS = ["engulfing", "hammer", "inside_break", "flag", "squeeze"]
CONTEXTS = ["C1_first30", "C2_near_level", "C3_vwap_2sd"]


def sh(a: np.ndarray, k: int) -> np.ndarray:
    """out[:, t] = a[:, t-k] (NaN / False fill)."""
    out = np.full_like(a, np.nan, dtype=float) if a.dtype != bool else np.zeros_like(a)
    if k > 0:
        out[:, k:] = a[:, :-k]
    else:
        out[:] = a
    return out


def roll_incl(a: np.ndarray, L: int, fn) -> np.ndarray:
    """fn over the inclusive window a[:, t-L+1 .. t]; NaN for t < L-1."""
    out = np.full(a.shape, np.nan)
    with np.errstate(all="ignore"):
        out[:, L - 1:] = fn(swv(a, L, axis=1), axis=2)
    return out


def roll_prev(a: np.ndarray, L: int, fn) -> np.ndarray:
    """fn over the previous L bars a[:, t-L .. t-1]; NaN for t < L."""
    return sh(roll_incl(a, L, fn), 1)


def sigma_tod(td) -> np.ndarray:
    """RMS of 1-min returns in the same half-hour bucket over the prior 20 sessions, mapped to bars."""
    r = td.ret1
    D, B = r.shape
    nb = B // 30
    ss = np.stack([np.nansum(r[:, b * 30:(b + 1) * 30] ** 2, axis=1) for b in range(nb)], axis=1)
    nn = np.stack([np.isfinite(r[:, b * 30:(b + 1) * 30]).sum(axis=1) for b in range(nb)], axis=1)
    sig = np.full((D, nb), np.nan)
    for d in range(1, D):
        lo = max(0, d - 20)
        n = nn[lo:d].sum(axis=0)
        with np.errstate(all="ignore"):
            sig[d] = np.where((d - lo >= 15) & (n > 0), np.sqrt(ss[lo:d].sum(axis=0) / np.maximum(n, 1)), np.nan)
    return np.repeat(sig, 30, axis=1)[:, :B]


def detect(td) -> dict:
    p = td.p
    o, h, l, c, v = p.o, p.h, p.l, p.c, np.nan_to_num(p.v)
    tick = (0.01 / td.fac)[:, None]
    c1, o1, h1, l1, h2, l2 = sh(c, 1), sh(o, 1), sh(h, 1), sh(l, 1), sh(h, 2), sh(l, 2)
    out = {}
    # engulfing
    body = np.abs(c - o)
    medb = roll_prev(body, 20, np.nanmedian)
    big = body >= 1.5 * medb
    out["engulfing"] = ((c1 < o1) & (c > o) & (o <= c1) & (c >= o1) & big,
                        (c1 > o1) & (c < o) & (o >= c1) & (c <= o1) & big)
    # hammer / shooting star
    rng = h - l
    medr = roll_prev(rng, 20, np.nanmedian)
    bodyh = np.maximum(body, tick)
    lower = np.minimum(o, c) - l
    upper = h - np.maximum(o, c)
    wide = (rng >= 1.5 * medr) & (rng > 0)
    out["hammer"] = ((lower >= 2 * bodyh) & (upper <= 0.25 * rng) & wide,
                     (upper >= 2 * bodyh) & (lower <= 0.25 * rng) & wide)
    # inside-bar break
    inside = (h1 <= h2) & (l1 >= l2)
    out["inside_break"] = (inside & (c > h2), inside & (c < l2))
    # flags
    sig = sigma_tod(td)
    green = np.cumsum((c > o).astype(float), axis=1)
    red = np.cumsum((c < o).astype(float), axis=1)
    cv = np.cumsum(v, axis=1)
    bull = np.zeros(c.shape, bool)
    bear = np.zeros(c.shape, bool)
    for n in range(3, 11):
        ih = roll_incl(h, n, np.nanmax)
        il = roll_incl(l, n, np.nanmin)
        for m in range(3, 11):
            cs = sh(c, m + n + 1)
            ce = sh(c, m + 1)
            s_imp = sh(sig, m + 1) * np.sqrt(n)
            IH, IL = sh(ih, m + 1), sh(il, m + 1)
            PH = sh(roll_incl(h, m, np.nanmax), 1)
            PL = sh(roll_incl(l, m, np.nanmin), 1)
            gfrac = (sh(green, m + 1) - sh(green, m + n + 1)) / n
            rfrac = (sh(red, m + 1) - sh(red, m + n + 1)) / n
            vimp = (sh(cv, m + 1) - sh(cv, m + n + 1)) / n
            vpb = (sh(cv, 1) - sh(cv, m + 1)) / m
            with np.errstate(all="ignore"):
                up_move = ce / cs - 1
                ret_b = (IH - PL) / (IH - cs)
                ret_s = (PH - IL) / (cs - IL)
            bull |= ((up_move >= 2.5 * s_imp) & (gfrac >= 0.7) & (IH > cs) & (ret_b >= 0.25) & (ret_b <= 0.60)
                     & (vpb < vimp) & (c > PH))
            bear |= ((up_move <= -2.5 * s_imp) & (rfrac >= 0.7) & (IL < cs) & (ret_s >= 0.25) & (ret_s <= 0.60)
                     & (vpb < vimp) & (c < PL))
    out["flag"] = (bull, bear)
    # squeeze
    sma = roll_incl(c, 20, np.nanmean)
    sd = roll_incl(c, 20, np.nanstd)
    width = 4 * sd / sma
    wmin = roll_incl(width, 120, np.nanmin)
    sq = sh(width, 1) <= sh(wmin, 1)
    up_b, lo_b = sma + 2 * sd, sma - 2 * sd
    out["squeeze"] = (sq & (c > up_b) & (c1 <= sh(up_b, 1)), sq & (c < lo_b) & (c1 >= sh(lo_b, 1)))
    return {k: (np.nan_to_num(a).astype(bool), np.nan_to_num(b).astype(bool)) for k, (a, b) in out.items()}


def contexts(td) -> dict:
    p = td.p
    c = p.c
    D, B = c.shape
    J = np.broadcast_to(np.arange(B)[None, :], (D, B))
    ctx = {"C1_first30": J <= 29}
    pm = td.premarket
    lv = [pm["pm_high"].to_numpy(float), pm["pm_low"].to_numpy(float),
          np.concatenate([[np.nan], td.hi[:-1]]), np.concatenate([[np.nan], td.lo[:-1]])]
    near = np.zeros((D, B), bool)
    with np.errstate(all="ignore"):
        for x in lv:
            near |= np.abs(c / x[:, None] - 1) <= 0.001
        or_hi = np.nanmax(p.h[:, :15], axis=1)[:, None]
        or_lo = np.nanmin(p.l[:, :15], axis=1)[:, None]
        near |= (J >= 15) & ((np.abs(c / or_hi - 1) <= 0.001) | (np.abs(c / or_lo - 1) <= 0.001))
        ctx["C2_near_level"] = near
        ctx["C3_vwap_2sd"] = (td.vwap_sd > 0) & (np.abs(c - td.vwap) >= 2 * td.vwap_sd)
    return ctx


def main() -> None:
    run = Runner("study7_chart_patterns")
    td = run.ctx["SOXL"]
    cmB = run.cms["B"]
    p = td.p
    D, B = p.c.shape
    dev = td.period == "dev"
    pats = detect(td)
    ctxs = contexts(td)
    run.log("patterns detected")
    rows, side_rows = [], []
    J = np.broadcast_to(np.arange(B)[None, :], (D, B))
    for H in H_LIST:
        fwd = np.full((D, B), np.nan)
        with np.errstate(all="ignore"):
            fwd[:, :B - 1 - H] = p.o[:, 1 + H:B] / p.o[:, 1:B - H] - 1
        ok_t = (J + 1 + H) <= (p.n_min[:, None] - 5)
        fwd = np.where(ok_t, fwd, np.nan)
        base = np.nanmean(np.where(dev[:, None], fwd, np.nan), axis=0)      # dev time-of-day baseline
        for pat in PATTERNS:
            bull, bear = pats[pat]
            for cx in CONTEXTS:
                m_ctx = ctxs[cx] & dev[:, None] & np.isfinite(fwd)
                db, jb = np.nonzero(bull & m_ctx)
                ds, js = np.nonzero(bear & m_ctx)
                d_all = np.concatenate([db, ds])
                j_all = np.concatenate([jb, js])
                s = np.concatenate([np.ones(len(db)), -np.ones(len(ds))])
                if len(d_all) == 0:
                    rows.append({"pattern": pat, "context": cx, "H": H, "n": 0})
                    continue
                gross = s * fwd[d_all, j_all] * 1e4
                excess = gross - s * base[j_all] * 1e4
                ep_u = p.o_unadj[d_all, j_all + 1]
                xp_u = p.o_unadj[d_all, j_all + 1 + H]
                yrs = td.dates[d_all].year.to_numpy()
                mins_in = 570 + j_all + 1
                cost = (cmB.half_spread_bps("SOXL", yrs, mins_in, ep_u) +
                        cmB.half_spread_bps("SOXL", yrs, mins_in + H, xp_u) +
                        cmB.commission_bps(ep_u) + cmB.commission_bps(xp_u) +
                        cmB.sec_fee_bps(td.dates[d_all]) + cmB.taf_bps(td.dates[d_all], np.where(s > 0, xp_u, ep_u)))
                net = excess - cost
                mu, t, G = C.cluster_t(net, d_all)
                rows.append({"pattern": pat, "context": cx, "H": H, "n": int(len(net)), "n_days": G,
                             "n_bull": int(len(db)), "n_bear": int(len(ds)),
                             "mean_gross_bps": float(np.nanmean(gross)), "mean_excess_bps": float(np.nanmean(excess)),
                             "mean_cost_bps": float(np.nanmean(cost)), "mean_net_bps": mu, "t_net": t,
                             "p_one_sided": C.one_sided_p(t, G)})
                for side_name, msk in (("bull", s > 0), ("bear", s < 0)):
                    if msk.sum() > 1:
                        mu2, t2, _ = C.cluster_t(net[msk], d_all[msk])
                        side_rows.append({"pattern": pat, "context": cx, "H": H, "side": side_name,
                                          "n": int(msk.sum()), "mean_excess_bps": float(np.nanmean(excess[msk])),
                                          "mean_net_bps": mu2, "t_net": t2})
    res = pd.DataFrame(rows)
    tested = res["n"] > 1
    res.loc[tested, "q_bh"] = C.bh_qvalues(res.loc[tested, "p_one_sided"].to_numpy())
    res["stage1_pass"] = (res["mean_net_bps"] >= 5) & (res["t_net"] >= 2) & (res["q_bh"] <= 0.10)
    res.to_csv(run.out / "stage1.csv", index=False, float_format="%.4f")
    pd.DataFrame(side_rows).to_csv(run.out / "stage1_by_side.csv", index=False, float_format="%.4f")
    print(res.round(2).to_string(index=False))
    run.log(f"stage-1 passes: {int(res['stage1_pass'].sum())}")


if __name__ == "__main__":
    main()
