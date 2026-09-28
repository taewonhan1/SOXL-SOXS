"""Intent-based trade simulation, SOXL/SOXS switch execution, cost cases and evaluation.

Workflow for every study variant
--------------------------------
1. A rule produces *intents* on the signal chart (normally SOXL): day, signal bar, entry bar, side,
   optional stop/target price levels, a time exit (bar + kind) and optional close-based exits.
2. ``simulate`` walks each intent through the signal chart's 1-minute bars and returns trades with
   the exit bar, exit kind and exit price on the signal chart:
     * stops/targets are checked on each bar's high/low; if a bar touches both, the stop wins;
       a bar that OPENS beyond the level fills at that open ("gap");
     * close-based exits (signal/trailing) exit at the NEXT bar's open;
     * time exits: ``open`` of bar tx, ``close`` of bar tx, or the ``official`` close (auction).
3. ``execute`` maps signal-chart trades to the traded instrument:
     * ``switch``: bullish -> long SOXL (same prices); bearish -> long SOXS, only if SOXS's unadjusted
       prior close >= $10 (otherwise the trade is skipped and logged). SOXS exits are "mirror" exits
       taken at the same bar/kind as the SOXL signal-chart exit; an intrabar SOXL stop/target level P is
       translated with SOXS_exit = SOXS_entry * (2 - P/pcL) / (2 - SOXL_entry/pcL) (pcL = SOXL prior
       close; exact under perfect +/-3x daily tracking; median error ~5 bps vs the actual SOXS print
       in 2022-2026) and clipped into that SOXS bar's [low, high];
     * ``switch_short``: bearish -> short SOXL;
     * ``ls``: long/short the signal ticker itself (cross-checks on SOXX, SMH, NVDA, QQQ, TQQQ, SPY).
4. ``add_costs`` computes cost cases A ($0 commission) and B ($0.0035/share), both with the measured
   half-spread per side (half-hour bucket, year, unadjusted price) plus SEC/FINRA fees on sells;
   an ``official`` (closing-auction) exit pays no half-spread.
5. ``add_quote_fills`` (case Q) re-prices entries/exits at the real NBBO (Massive /v3/quotes, last quote
   at or before the fill time): buys at the ask, sells at the bid; stop exits at level -/+ the prevailing
   half-spread; target exits at the level (resting limit); auction exits at the official close.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .. import api, config
from .common import (PERIOD_ORDER, PERIODS, RESEARCH_DATA, SOXS_MIN_PRICE, Context, bar_time_ns,
                     cluster_t, max_drawdown_bps, period_of, quarter_share_positive)

INTENT_DEFAULTS = {"stop": np.nan, "target": np.nan, "tx_kind": "open", "trail_r": np.nan, "entry_px": np.nan}


def make_intents(rows: list[dict]) -> pd.DataFrame:
    cols = ["d", "sig", "e", "s", "stop", "target", "tx", "tx_kind", "trail_r", "entry_px"]
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows)
    for k, v in INTENT_DEFAULTS.items():
        if k not in df:
            df[k] = v
    df = df[cols].sort_values(["d", "e"]).reset_index(drop=True)
    return df


# --------------------------------------------------------------------------------------
# simulation on the signal chart
# --------------------------------------------------------------------------------------
def simulate(td, intents: pd.DataFrame, exit_long: np.ndarray | None = None,
             exit_short: np.ndarray | None = None, one_position: bool = True) -> pd.DataFrame:
    p = td.p
    o, h, l, c = p.o, p.h, p.l, p.c
    vwap = td.vwap if intents["trail_r"].notna().any() else None
    free: dict[int, int] = {}
    recs = []
    for r in intents.itertuples(index=False):
        d, e, s, tx = int(r.d), int(r.e), int(r.s), int(r.tx)
        kind = r.tx_kind
        nmin = int(p.n_min[d])
        if one_position and e < free.get(d, 0):
            continue
        if e < 0 or e >= nmin:
            continue
        if kind == "open":
            tx = min(tx, nmin - 1)
            if e >= tx:
                continue
            last = tx - 1
        else:
            tx = min(tx, nmin - 1)
            if e > tx:
                continue
            last = tx
        # entry: the bar's open, or a resting stop order filled inside bar e at ``entry_px`` (level entry)
        lvl_entry = np.isfinite(r.entry_px)
        ep = float(r.entry_px) if lvl_entry else o[d, e]
        if not np.isfinite(ep) or ep <= 0:
            continue
        hh, ll, oo, cc = h[d, e:last + 1], l[d, e:last + 1], o[d, e:last + 1], c[d, e:last + 1]
        n = hh.size
        stop, tgt = float(r.stop), float(r.target)
        st = np.zeros(n, bool)
        tg = np.zeros(n, bool)
        if np.isfinite(stop):
            st = (ll <= stop) if s > 0 else (hh >= stop)
        if np.isfinite(tgt):
            tg = (hh >= tgt) if s > 0 else (ll <= tgt)
        if lvl_entry and n:
            # conservative on the entry bar: a touched stop counts (assumed after the fill); no target fills
            tg[0] = False
        anyh = np.flatnonzero(st | tg)
        k_level = int(anyh[0]) if anyh.size else n
        k_sig = n
        ex = exit_long if s > 0 else exit_short
        if ex is not None:
            hit = np.flatnonzero(ex[d, e:last + 1])
            if hit.size:
                k_sig = int(hit[0])
        k_tr = n
        if vwap is not None and np.isfinite(r.trail_r) and np.isfinite(stop):
            R = abs(ep - stop)
            arm = (hh >= ep + r.trail_r * R) if s > 0 else (ll <= ep - r.trail_r * R)
            ia = np.flatnonzero(arm)
            if ia.size:
                vv = vwap[d, e:last + 1]
                cond = (cc < vv) if s > 0 else (cc > vv)
                cond[: int(ia[0])] = False
                it = np.flatnonzero(cond)
                if it.size:
                    k_tr = int(it[0])
        k_close = min(k_sig, k_tr)
        xb = None
        if k_level < n and k_level <= k_close:
            k = k_level
            xb = e + k
            if st[k]:
                gap = ((oo[k] <= stop) if s > 0 else (oo[k] >= stop)) and not (lvl_entry and k == 0)
                xp, xk, why = (oo[k], "gap", "stop") if gap else (stop, "level", "stop")
            else:
                gap = (oo[k] >= tgt) if s > 0 else (oo[k] <= tgt)
                xp, xk, why = (oo[k], "gap", "target") if gap else (tgt, "level", "target")
            nxt_free = xb + 1
        elif k_close < n and e + k_close + 1 <= nmin - 1 and \
                ((kind == "open" and e + k_close + 1 < tx) or (kind != "open" and e + k_close + 1 <= tx)):
            xb = e + k_close + 1
            xp, xk, why = o[d, xb], "open", ("trail" if k_tr <= k_sig else "signal")
            nxt_free = xb
        if xb is None:
            xb = tx
            if kind == "open":
                xp, xk = o[d, tx], "open"
                if not np.isfinite(xp):
                    xp = c[d, tx - 1]
                nxt_free = tx
            elif kind == "close":
                xp, xk, nxt_free = c[d, tx], "close", tx + 1
            else:
                xp, xk, nxt_free = td.off[d], "official", tx + 1
            why = "time"
        if not np.isfinite(xp):
            continue
        free[d] = nxt_free
        recs.append((d, int(r.sig), e, xb, s, float(ep), float(xp), xk, why, "level" if lvl_entry else "open"))
    tr = pd.DataFrame(recs, columns=["d", "sig", "e", "xb", "s", "ep", "xp", "x_kind", "reason", "e_kind"])
    tr["date"] = td.dates[tr["d"].to_numpy()] if len(tr) else pd.Series(dtype="datetime64[ns]")
    tr["gross_chart_bps"] = tr["s"] * (tr["xp"] / tr["ep"] - 1) * 1e4
    return tr


# --------------------------------------------------------------------------------------
# paired legs (scale-out exits) and position limits applied after simulation
# --------------------------------------------------------------------------------------
LEG_KEY = ["d", "sig", "e", "s"]


def _next_free(tr: pd.DataFrame) -> np.ndarray:
    """First bar a new position may enter after this trade (same rule as ``simulate``'s one-position)."""
    xb = tr["xb"].to_numpy().astype(int)
    return np.where(tr["x_kind"].to_numpy() == "open", xb, xb + 1)


def filter_positions(legs: list[pd.DataFrame], max_per_day: int | None = None) -> list[pd.DataFrame]:
    """Legs simulated with ``one_position=False`` from the same intents -> keep a signal only if its entry
    bar is at or after the bar at which every leg of the previously kept signal is out, and at most
    ``max_per_day`` signals per day. Returns the legs restricted to the kept signals."""
    base = legs[0][LEG_KEY].copy()
    base["nf"] = _next_free(legs[0])
    for lg in legs[1:]:
        base = base.merge(lg[LEG_KEY].assign(nf2=_next_free(lg)), on=LEG_KEY, how="inner")
        base["nf"] = np.maximum(base["nf"], base.pop("nf2"))
    keep, cur, free, n = [], -1, 0, 0
    for r in base.sort_values(["d", "e", "sig"]).itertuples(index=False):
        if r.d != cur:
            cur, free, n = r.d, 0, 0
        if r.e < free or (max_per_day is not None and n >= max_per_day):
            continue
        keep.append((r.d, r.sig, r.e, r.s))
        free, n = r.nf, n + 1
    kk = pd.DataFrame(keep, columns=LEG_KEY)
    return [lg.merge(kk, on=LEG_KEY, how="inner") for lg in legs]


PNL_MEAN_COLS = ("ep", "ep_u", "xp", "xp_u", "gross_bps", "cost_A", "net_A", "cost_B", "net_B", "gross_Q",
                 "net_Q", "net_S", "q_entry_spread_bps")


def merge_legs(legs: list[pd.DataFrame], names=("A", "B")) -> pd.DataFrame:
    """Equal-size legs of one position -> one trade per signal. P&L columns (and prices) are the leg
    average, i.e. the result of the whole position; the exit bar is the last leg's exit."""
    key = ["date", "d", "sig", "e", "s", "inst"]
    allp = pd.concat([lg.assign(leg=nm) for lg, nm in zip(legs, names)], ignore_index=True)
    allp = allp[allp.groupby(key)["leg"].transform("count") == len(legs)]      # signals present in every leg
    agg = {c: "mean" for c in PNL_MEAN_COLS if c in allp}
    agg.update({"xb": "max", "exit_min": "max", "x_kind": "+".join, "reason": "+".join})
    if "q_fallback" in allp:
        agg["q_fallback"] = "max"
    agg.update({c: "first" for c in allp.columns if c not in agg and c not in key and c != "leg"})
    out = allp.sort_values("leg").groupby(key, sort=False).agg(agg).reset_index()
    return out.sort_values(["date", "e"]).reset_index(drop=True)


def add_stop_slippage(tr: pd.DataFrame, cents: float = 1.0) -> pd.DataFrame:
    """Case S (stress): case B plus ``cents`` of extra slippage on every stop-order fill, i.e. level
    (stop) entries and stop-loss exits filled at the level."""
    tr = tr.copy()
    if tr.empty:
        tr["net_S"] = []
        return tr
    slip_in = np.where(tr["e_kind"].to_numpy() == "level", cents / 100 / tr["ep_u"].to_numpy() * 1e4, 0.0)
    stop_lvl = (tr["x_kind"].to_numpy() == "level") & (tr["reason"].to_numpy() == "stop")
    slip_out = np.where(stop_lvl, cents / 100 / tr["xp_u"].to_numpy() * 1e4, 0.0)
    tr["net_S"] = tr["net_B"] - slip_in - slip_out
    return tr


# --------------------------------------------------------------------------------------
# execution mapping
# --------------------------------------------------------------------------------------
def _exit_minute(xb: np.ndarray, kind: np.ndarray) -> np.ndarray:
    m = config.RTH_START_MIN + xb.astype(int)
    return np.where(kind == "official", config.RTH_END_MIN, m)


def execute(tr: pd.DataFrame, ctx: Context, mode: str = "switch", sig: str = "SOXL",
            bear_min_price: float = SOXS_MIN_PRICE) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Map signal-chart trades to instrument trades. Returns (trades, skipped_bearish)."""
    cols = ["date", "d", "sig", "e", "xb", "s", "inst", "side", "ep", "xp", "ep_u", "xp_u", "x_kind",
            "reason", "entry_min", "exit_min", "gross_bps", "e_kind"]
    if "e_kind" not in tr.columns:
        tr = tr.assign(e_kind="open")
    if tr.empty:
        return pd.DataFrame(columns=cols), tr.iloc[0:0]
    parts = []
    skipped = tr.iloc[0:0]

    def _finish(df, inst, td):
        df = df.copy()
        df["inst"] = inst
        fac = td.fac[df["d"].to_numpy()]
        df["ep_u"] = df["ep"] * fac
        df["xp_u"] = df["xp"] * fac
        df["entry_min"] = config.RTH_START_MIN + df["e"].astype(int)
        df["exit_min"] = _exit_minute(df["xb"].to_numpy(), df["x_kind"].to_numpy())
        df["gross_bps"] = df["side"] * (df["xp"] / df["ep"] - 1) * 1e4
        return df

    if mode == "ls" or sig != "SOXL":
        df = tr.copy()
        df["side"] = df["s"]
        return _finish(df, sig, ctx[sig])[cols], skipped
    tdL = ctx["SOXL"]
    bull = tr[tr["s"] > 0].copy()
    bull["side"] = 1
    parts.append(_finish(bull, "SOXL", tdL))
    bear = tr[tr["s"] < 0].copy()
    if mode == "switch_short":
        bear["side"] = -1
        parts.append(_finish(bear, "SOXL", tdL))
    elif mode == "switch":
        tdS = ctx["SOXS"]
        d = bear["d"].to_numpy()
        elig = tdS.pc_u[d] >= bear_min_price
        skipped = bear[~elig]
        b = bear[elig].copy()
        if len(b):
            d, e, xb = b["d"].to_numpy(), b["e"].to_numpy(), b["xb"].to_numpy()
            pS = tdS.p
            ep = pS.o[d, e].astype(float)
            if "e_kind" in b:
                # level (stop-order) entries: SOXS price mirrored from the SOXL fill level, anchored at the bar open
                m_le = (b["e_kind"] == "level").to_numpy()
                if m_le.any():
                    P0 = b["ep"].to_numpy()[m_le]
                    oL = tdL.p.o[d[m_le], e[m_le]]
                    pcL0 = tdL.pc[d[m_le]]
                    mapped0 = pS.o[d[m_le], e[m_le]] * (2 - P0 / pcL0) / (2 - oL / pcL0)
                    ep[m_le] = np.clip(mapped0, pS.l[d[m_le], e[m_le]], pS.h[d[m_le], e[m_le]])
            kinds = b["x_kind"].to_numpy()
            xp = np.full(len(b), np.nan)
            m_open = np.isin(kinds, ["open", "gap"])
            xp[m_open] = pS.o[d[m_open], xb[m_open]]
            m_close = kinds == "close"
            xp[m_close] = pS.c[d[m_close], xb[m_close]]
            m_off = kinds == "official"
            xp[m_off] = tdS.off[d[m_off]]
            m_lvl = kinds == "level"
            if m_lvl.any():
                # entry-anchored mirror: SOXS moves as (2 - SOXL/pcL) scaled from the actual SOXS entry
                P = b["xp"].to_numpy()[m_lvl]
                epL = b["ep"].to_numpy()[m_lvl]
                pcL = tdL.pc[d[m_lvl]]
                mapped = ep[m_lvl] * (2 - P / pcL) / (2 - epL / pcL)
                lo, hi = pS.l[d[m_lvl], xb[m_lvl]], pS.h[d[m_lvl], xb[m_lvl]]
                xp[m_lvl] = np.clip(mapped, lo, hi)
            b["ep"], b["xp"] = ep, xp
            b["side"] = 1
            b = b[np.isfinite(b["ep"]) & np.isfinite(b["xp"]) & (b["ep"] > 0)]
            parts.append(_finish(b, "SOXS", tdS))
    else:
        raise ValueError(mode)
    out = pd.concat([x for x in parts if len(x)], ignore_index=True) if any(len(x) for x in parts) else \
        pd.DataFrame(columns=cols)
    return out[cols].sort_values(["date", "e"]).reset_index(drop=True), skipped


# --------------------------------------------------------------------------------------
# costs
# --------------------------------------------------------------------------------------
def add_costs(tr: pd.DataFrame, cms: dict) -> pd.DataFrame:
    """cms = {"A": CostModel($0), "B": CostModel($0.0035)}; adds cost_X / net_X columns (bps)."""
    tr = tr.copy()
    for case in cms:
        tr[f"cost_{case}"] = np.nan
        tr[f"net_{case}"] = np.nan
    if tr.empty:
        return tr
    yrs = pd.to_datetime(tr["date"]).dt.year.to_numpy()
    for inst, idx in tr.groupby("inst").groups.items():
        g = tr.loc[idx]
        y = yrs[tr.index.get_indexer(idx)]
        if inst == "SOXL":
            # SOXL split 15:1 on 2021-03-02; the 2021 spread row (median 1 cent) describes the post-split
            # stock, so pre-split 2021 trades use the 2020 row (spreads of tens of cents at ~$400-600).
            y = np.where(pd.to_datetime(g["date"]).to_numpy() < np.datetime64("2021-03-02"), np.minimum(y, 2020), y)
        for case, cm in cms.items():
            hs_in = cm.half_spread_bps(inst, y, g["entry_min"].to_numpy(), g["ep_u"].to_numpy())
            hs_out = cm.half_spread_bps(inst, y, g["exit_min"].to_numpy(), g["xp_u"].to_numpy())
            hs_out = np.where(g["x_kind"].to_numpy() == "official", 0.0, hs_out)
            comm = cm.commission_bps(g["ep_u"].to_numpy()) + cm.commission_bps(g["xp_u"].to_numpy())
            sell_px = np.where(g["side"].to_numpy() > 0, g["xp_u"].to_numpy(), g["ep_u"].to_numpy())
            fees = cm.sec_fee_bps(g["date"]) + cm.taf_bps(g["date"], sell_px)
            cost = hs_in + hs_out + comm + fees
            tr.loc[idx, f"cost_{case}"] = cost
            tr.loc[idx, f"net_{case}"] = g["gross_bps"].to_numpy() - cost
    return tr


# --------------------------------------------------------------------------------------
# case Q: fills at the real NBBO
# --------------------------------------------------------------------------------------
NBBO_POINTS_DIR = RESEARCH_DATA / "nbbo_points"


def _nbbo_cache_path(inst: str) -> Path:
    return NBBO_POINTS_DIR / f"{inst}.parquet"


def nbbo_lookup(inst: str, ns_values) -> pd.DataFrame:
    """Last NBBO at or before each ns timestamp (cached on disk). Columns: ns, bid, ask, q_ns."""
    ns_values = np.unique(np.asarray(list(ns_values), dtype=np.int64))
    p = _nbbo_cache_path(inst)
    cache = pd.read_parquet(p) if p.exists() else pd.DataFrame(columns=["ns", "bid", "ask", "q_ns"])
    have = set(cache["ns"].astype(np.int64).tolist())
    todo = [int(x) for x in ns_values if int(x) not in have]

    def _one(ns):
        r = api.get(f"/v3/quotes/{inst}", {"timestamp.lte": ns, "order": "desc", "sort": "timestamp", "limit": 1})
        res = (r.json() or {}).get("results") or []
        if not res:
            return (ns, np.nan, np.nan, np.nan)
        q = res[0]
        return (ns, float(q.get("bid_price", np.nan)), float(q.get("ask_price", np.nan)),
                float(q.get("sip_timestamp", np.nan)))

    if todo:
        print(f"  NBBO lookups for {inst}: {len(todo)} new points", flush=True)
        new = []
        for i in range(0, len(todo), 2000):          # checkpoint every 2,000 lookups
            chunk = api.parallel_map(_one, todo[i:i + 2000], desc=f"nbbo {inst}", verbose=False)
            new.extend(chunk)
            add = pd.DataFrame(new, columns=["ns", "bid", "ask", "q_ns"])
            full = pd.concat([cache, add], ignore_index=True).drop_duplicates("ns")
            NBBO_POINTS_DIR.mkdir(parents=True, exist_ok=True)
            full.to_parquet(p, index=False)
            print(f"    {min(i + 2000, len(todo))}/{len(todo)} cached", flush=True)
        cache = full
    cache = cache.astype({"ns": np.int64})
    return cache.set_index("ns").reindex(ns_values).reset_index()


def add_quote_fills(tr: pd.DataFrame, cm_b, periods=("dev", "val", "hold")) -> pd.DataFrame:
    """Case Q net (bps) using real NBBO fills for trades in ``periods`` (NaN elsewhere); trades without a
    usable quote fall back to case B and are flagged in ``q_fallback``."""
    tr = tr.copy()
    if tr.empty:
        tr["net_Q"] = []
        return tr
    in_scope = np.isin(period_of(tr["date"]), list(periods))
    full = tr
    tr = tr[in_scope].copy()
    if tr.empty:
        full["net_Q"], full["gross_Q"] = np.nan, np.nan
        return full
    dates = pd.to_datetime(tr["date"])
    e_ns = np.array([bar_time_ns(dt, int(e)) for dt, e in zip(dates, tr["e"])], dtype=np.int64)
    kinds = tr["x_kind"].to_numpy()
    x_ns = np.array([bar_time_ns(dt, int(x) + (1 if k == "close" else 0)) - (1 if k == "close" else 0)
                     for dt, x, k in zip(dates, tr["xb"], kinds)], dtype=np.int64)
    ent_bid = np.full(len(tr), np.nan)
    ent_ask = np.full(len(tr), np.nan)
    ex_bid = np.full(len(tr), np.nan)
    ex_ask = np.full(len(tr), np.nan)
    for inst in tr["inst"].unique():
        m = (tr["inst"] == inst).to_numpy()
        need = np.concatenate([e_ns[m], x_ns[m & (kinds != "official")]])
        q = nbbo_lookup(inst, need).set_index("ns")
        ent_bid[m] = q["bid"].reindex(e_ns[m]).to_numpy()
        ent_ask[m] = q["ask"].reindex(e_ns[m]).to_numpy()
        ex_bid[m] = q["bid"].reindex(x_ns[m]).to_numpy()
        ex_ask[m] = q["ask"].reindex(x_ns[m]).to_numpy()

    def _ok(b, a):
        mid = (a + b) / 2
        return np.isfinite(b) & np.isfinite(a) & (b > 0) & (a > b) & ((a - b) / mid < 0.05)

    side = tr["side"].to_numpy()
    ok_e = _ok(ent_bid, ent_ask)
    ok_x = _ok(ex_bid, ex_ask) | (kinds == "official")
    entry_fill = np.where(side > 0, ent_ask, ent_bid)
    if "e_kind" in tr:
        hs_e = (ent_ask - ent_bid) / 2
        entry_fill = np.where(tr["e_kind"].to_numpy() == "level", tr["ep_u"].to_numpy() + side * hs_e, entry_fill)
    hs_x = (ex_ask - ex_bid) / 2
    xp_u = tr["xp_u"].to_numpy()
    reason = tr["reason"].to_numpy()
    exit_fill = np.where(side > 0, ex_bid, ex_ask)
    lvl = kinds == "level"
    exit_fill = np.where(lvl & (reason == "stop"), xp_u - side * hs_x, exit_fill)
    exit_fill = np.where(lvl & (reason == "target"), xp_u, exit_fill)
    exit_fill = np.where(kinds == "official", xp_u, exit_fill)
    gross_q = side * (exit_fill / entry_fill - 1) * 1e4
    comm = cm_b.commission_bps(tr["ep_u"].to_numpy()) + cm_b.commission_bps(tr["xp_u"].to_numpy())
    sell_px = np.where(side > 0, tr["xp_u"].to_numpy(), tr["ep_u"].to_numpy())
    fees = cm_b.sec_fee_bps(tr["date"]) + cm_b.taf_bps(tr["date"], sell_px)
    net_q = gross_q - comm - fees
    good = ok_e & ok_x & np.isfinite(net_q)
    tr["gross_Q"] = np.where(good, gross_q, tr["gross_bps"])
    tr["net_Q"] = np.where(good, net_q, tr["net_B"])
    tr["q_fallback"] = (~good).astype(int)
    tr["q_entry_spread_bps"] = np.where(ok_e, (ent_ask - ent_bid) / ((ent_ask + ent_bid) / 2) * 1e4, np.nan)
    for col in ("gross_Q", "net_Q", "q_fallback", "q_entry_spread_bps"):
        full.loc[tr.index, col] = tr[col]
    return full


# --------------------------------------------------------------------------------------
# summaries
# --------------------------------------------------------------------------------------
def summarize(tr: pd.DataFrame, ctx: Context, variant: str, skipped: pd.DataFrame | None = None,
              periods=("pre", "dev", "val"), extra: dict | None = None) -> pd.DataFrame:
    """One row per (period, side, cost case). The holdout is excluded unless explicitly requested."""
    extra = extra or {}
    rows = []
    cal_period = period_of(ctx.dates)
    per_col = period_of(tr["date"]) if len(tr) else np.array([], dtype=object)
    sk_per = period_of(skipped["date"]) if skipped is not None and len(skipped) else np.array([], dtype=object)
    cases = [c for c in ("A", "B", "Q", "S") if f"net_{c}" in tr.columns]
    for per in periods:
        n_days = int((cal_period == per).sum())
        t_per = tr[per_col == per] if len(tr) else tr
        for side_name in ("all", "bull", "bear"):
            if side_name == "all":
                t = t_per
            elif side_name == "bull":
                t = t_per[t_per["s"] > 0]
            else:
                t = t_per[t_per["s"] < 0]
            for case in cases:
                x = t[f"net_{case}"].to_numpy(float) if len(t) else np.array([])
                g = (t["gross_Q"] if case == "Q" and "gross_Q" in t else t["gross_bps"]).to_numpy(float) \
                    if len(t) else np.array([])
                mu, tt, G = cluster_t(x, t["date"].to_numpy()) if len(t) else (np.nan, np.nan, 0)
                mg, tg, _ = cluster_t(g, t["date"].to_numpy()) if len(t) else (np.nan, np.nan, 0)
                qpos, nq = quarter_share_positive(x, t["date"]) if len(t) else (np.nan, 0)
                pos, neg = x[x > 0].sum(), -x[x < 0].sum()
                rows.append({"variant": variant, "period": per, "side": side_name, "case": case,
                             "n_trades": int(len(t)), "n_days_traded": int(G), "period_days": n_days,
                             "trades_per_day": len(t) / max(1, n_days),
                             "mean_gross_bps": mg, "t_gross": tg, "mean_net_bps": mu, "t_net": tt,
                             "median_net_bps": float(np.median(x)) if len(x) else np.nan,
                             "win_rate": float((x > 0).mean()) if len(x) else np.nan,
                             "profit_factor": float(pos / neg) if neg > 0 else np.nan,
                             "quarters_positive": qpos, "n_quarters": nq,
                             "total_pct": float(np.nansum(x) / 100.0),
                             "max_dd_pct": max_drawdown_bps(x) / 100.0,
                             "mean_cost_bps": float(np.nanmean(g - x)) if len(x) else np.nan,
                             "skipped_bearish": int((sk_per == per).sum()) if side_name != "bull" else 0,
                             **extra})
    return pd.DataFrame(rows)


def pick(summary: pd.DataFrame, variant: str, period: str, side: str = "all", case: str = "B") -> pd.Series:
    m = (summary["variant"] == variant) & (summary["period"] == period) & (summary["side"] == side) & \
        (summary["case"] == case)
    s = summary[m]
    return s.iloc[0] if len(s) else pd.Series(dtype=float)


def save_trades(tr: pd.DataFrame, study: str, variant: str) -> Path:
    p = RESEARCH_DATA / "trades" / study / f"{variant}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    tr.to_parquet(p, index=False)
    return p


def write_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str))
