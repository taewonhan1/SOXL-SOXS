"""Bar-level backtest harness for intraday strategies on the regular-session minute panel.

Execution model
---------------
* A signal observed at the CLOSE of bar j (``entries[d, j] = +1 long / -1 short``) is executed at the
  OPEN of bar j+1. Exit signals work the same way (``exit_long[d, k]`` -> exit at open of k+1).
* Take-profit / stop are checked intra-bar on every bar from the entry bar onward using bar high/low.
  If both are touched in the same bar the STOP is assumed to fill first (conservative). A stop that is
  gapped through at a bar open fills at that (worse) open; a take-profit fills at its level, or at the
  bar open when the bar opens beyond it (resting limit order).
* Positions are flat by ``flat_before_close`` minutes before the session close: forced exit at the open
  of the 15:55 bar (12:55 on 13:00 early-close days); no entry may execute at or after that bar.
* One position at a time per call; a new entry may execute at the same open as the previous exit.
* Returns are computed on adjusted prices; within a session adjusted/unadjusted returns are identical
  (split adjustments are per-day constants). Unadjusted prices are carried for per-share costs.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from . import config
from .costs import CostModel
from .data import Panel


@dataclass
class Rules:
    stop_bps: float | None = None
    tp_bps: float | None = None
    max_hold: int | None = None           # bars between entry open and forced exit open
    flat_before_close: int = config.FLAT_BEFORE_CLOSE_MIN
    earliest_entry_bar: int = 1           # first bar whose OPEN may be used for an entry
    one_position: bool = True


def _day_factor(p: Panel) -> np.ndarray:
    """Unadjusted/adjusted price factor per day (constant within a day)."""
    with np.errstate(all="ignore"):
        f = np.nanmedian(p.c_unadj / p.c, axis=1)
    return np.where(np.isfinite(f), f, 1.0)


def simulate(p: Panel, entries: np.ndarray, rules: Rules = Rules(), *, stop_px: np.ndarray | None = None,
             tp_px: np.ndarray | None = None, stop_bps_arr: np.ndarray | None = None,
             tp_bps_arr: np.ndarray | None = None, exit_long: np.ndarray | None = None, exit_short: np.ndarray | None = None,
             cost_model: CostModel | None = None, ticker: str | None = None) -> pd.DataFrame:
    """Simulate trades. Returns one row per trade (gross, and net when ``cost_model`` is given)."""
    ticker = ticker or p.ticker
    nd, nb = p.c.shape
    o, h, l = p.o, p.h, p.l
    fac = _day_factor(p)
    recs = []
    E = np.nan_to_num(entries).astype(np.int8)
    for d in range(nd):
        row = E[d]
        cand = np.flatnonzero(row)
        if cand.size == 0:
            continue
        flat_idx = int(p.n_min[d]) - rules.flat_before_close
        free_from = 0
        for j in cand:
            e = j + 1
            if e < rules.earliest_entry_bar or e >= flat_idx or e < free_from:
                continue
            ep = o[d, e]
            if not np.isfinite(ep) or ep <= 0:
                continue
            s = int(np.sign(row[j]))
            # levels
            stop = tp = np.nan
            if stop_px is not None and np.isfinite(stop_px[d, j]):
                stop = stop_px[d, j]
            elif stop_bps_arr is not None and np.isfinite(stop_bps_arr[d, j]):
                stop = ep * (1 - s * stop_bps_arr[d, j] / 1e4)
            elif rules.stop_bps is not None:
                stop = ep * (1 - s * rules.stop_bps / 1e4)
            if tp_px is not None and np.isfinite(tp_px[d, j]):
                tp = tp_px[d, j]
            elif tp_bps_arr is not None and np.isfinite(tp_bps_arr[d, j]):
                tp = ep * (1 + s * tp_bps_arr[d, j] / 1e4)
            elif rules.tp_bps is not None:
                tp = ep * (1 + s * rules.tp_bps / 1e4)
            # open-exit bar (time / signal / end-of-day)
            m_open = flat_idx if rules.max_hold is None else min(e + rules.max_hold, flat_idx)
            reason = "eod" if m_open == flat_idx else "time"
            ex = exit_long if s > 0 else exit_short
            if ex is not None:
                seg = ex[d, e:m_open]
                hit = np.flatnonzero(seg)
                if hit.size:
                    m_sig = e + int(hit[0]) + 1
                    if m_sig < m_open or (m_sig == m_open and reason != "eod"):
                        m_open, reason = m_sig, "signal"
            # intra-bar stops / targets on bars e .. m_open-1
            k_hit, px, why = None, np.nan, None
            if np.isfinite(stop) or np.isfinite(tp):
                hh = h[d, e:m_open]
                ll = l[d, e:m_open]
                oo = o[d, e:m_open]
                if s > 0:
                    st = ll <= stop if np.isfinite(stop) else np.zeros(hh.size, bool)
                    tg = hh >= tp if np.isfinite(tp) else np.zeros(hh.size, bool)
                else:
                    st = hh >= stop if np.isfinite(stop) else np.zeros(hh.size, bool)
                    tg = ll <= tp if np.isfinite(tp) else np.zeros(hh.size, bool)
                anyhit = np.flatnonzero(st | tg)
                if anyhit.size:
                    k = int(anyhit[0])
                    k_hit = e + k
                    if st[k]:  # stop first when both touched
                        gap_through = (oo[k] <= stop) if s > 0 else (oo[k] >= stop)
                        px, why = (oo[k] if gap_through else stop), "stop"
                    else:
                        gap_through = (oo[k] >= tp) if s > 0 else (oo[k] <= tp)
                        px, why = (oo[k] if gap_through else tp), "target"
            if k_hit is not None:
                xbar, xp, reason, free_from = k_hit, px, why, k_hit + 1
            else:
                xbar, xp, free_from = m_open, o[d, m_open], m_open
                if not np.isfinite(xp):
                    xp = p.c[d, m_open - 1]
            gross = s * (xp / ep - 1.0) * 1e4
            recs.append((p.dates[d], d, s, j, e, xbar, ep, xp, ep * fac[d], xp * fac[d], gross, reason,
                         xbar - e + (1 if k_hit is not None else 0)))
            if not rules.one_position:
                free_from = 0
    cols = ["date", "day_idx", "side", "sig_bar", "entry_bar", "exit_bar", "entry_px", "exit_px",
            "entry_px_unadj", "exit_px_unadj", "gross_bps", "exit_reason", "hold_bars"]
    tr = pd.DataFrame(recs, columns=cols)
    tr["ticker"] = ticker
    tr["entry_min_et"] = config.RTH_START_MIN + tr["entry_bar"]
    tr["exit_min_et"] = config.RTH_START_MIN + tr["exit_bar"]
    tr["entry_time"] = tr["entry_min_et"].map(lambda m: f"{m // 60:02d}:{m % 60:02d}")
    tr["exit_time"] = tr["exit_min_et"].map(lambda m: f"{m // 60:02d}:{m % 60:02d}")
    if cost_model is not None:
        tr = cost_model.trade_costs(tr, ticker)
    return tr


# --------------------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------------------
def _dd(cum: np.ndarray) -> float:
    if cum.size == 0:
        return 0.0
    peak = np.maximum.accumulate(np.concatenate([[0.0], cum]))
    return float(np.max(peak[1:] - cum))


def metrics(trades: pd.DataFrame, days: pd.DatetimeIndex, session_minutes: float | None = None) -> dict:
    """Trade and daily metrics over ``days`` (all trading days of the evaluation window).

    Daily P&L = sum of trade returns that day on a fixed notional (additive, no compounding).
    """
    out = {"n_trades": 0, "n_days": len(days)}
    t = trades[trades["date"].isin(days)] if len(trades) else trades
    n = len(t)
    out["n_trades"] = n
    if n == 0:
        return {**out, "win_rate": np.nan, "avg_gross_bps": np.nan, "avg_net_bps": np.nan,
                "avg_cost_bps": np.nan, "profit_factor": np.nan, "sharpe_gross": np.nan,
                "sharpe_net": np.nan, "max_dd_net_pct": 0.0, "exposure": 0.0, "t_stat_net": np.nan}
    has_net = "net_bps" in t
    out["trades_per_day"] = n / max(1, len(days))
    out["win_rate"] = float((t["net_bps"] > 0).mean()) if has_net else float((t["gross_bps"] > 0).mean())
    out["win_rate_gross"] = float((t["gross_bps"] > 0).mean())
    out["avg_gross_bps"] = float(t["gross_bps"].mean())
    out["median_gross_bps"] = float(t["gross_bps"].median())
    for k, col in (("gross", "gross_bps"), ("net", "net_bps")):
        if col not in t:
            continue
        pos = t.loc[t[col] > 0, col].sum()
        neg = -t.loc[t[col] < 0, col].sum()
        out[f"profit_factor_{k}"] = float(pos / neg) if neg > 0 else np.inf
        daily = t.groupby("date")[col].sum().reindex(days).fillna(0.0) / 1e4
        mu, sd = daily.mean(), daily.std(ddof=1)
        out[f"sharpe_{k}"] = float(mu / sd * np.sqrt(252)) if sd > 0 else np.nan
        out[f"t_stat_{k}"] = float(mu / sd * np.sqrt(len(daily))) if sd > 0 else np.nan
        out[f"total_{k}_pct"] = float(daily.sum() * 100)
        out[f"ann_{k}_pct"] = float(mu * 252 * 100)
        out[f"max_dd_{k}_pct"] = _dd(daily.cumsum().to_numpy()) * 100
    if has_net:
        out["avg_net_bps"] = float(t["net_bps"].mean())
        out["median_net_bps"] = float(t["net_bps"].median())
        out["avg_cost_bps"] = float(t["cost_bps"].mean())
        out["profit_factor"] = out["profit_factor_net"]
    out["avg_hold_min"] = float(t["hold_bars"].mean())
    if session_minutes:
        out["exposure"] = float(t["hold_bars"].sum() / session_minutes)
    out["long_share"] = float((t["side"] > 0).mean())
    return out


def session_minutes(p: Panel, days: pd.DatetimeIndex) -> float:
    m = p.dates.isin(days)
    return float(p.n_min[m].sum())


# --------------------------------------------------------------------------------------
# walk-forward, random-entry baseline, signal-timing diagnostics
# --------------------------------------------------------------------------------------
def walk_forward(trades_by_param: dict, windows: list[tuple], cal_days: pd.DatetimeIndex,
                 select: str = "sharpe_net", min_trades: int = 30) -> pd.DataFrame:
    """Select the best parameter set on each train window, report it on the following test window.

    trades_by_param  {param_label: trades DataFrame over the whole history}
    windows          [(train_start, train_end, test_start, test_end), ...]
    """
    rows = []
    for (a, b, c, d) in windows:
        tr_days = cal_days[(cal_days >= pd.Timestamp(a)) & (cal_days <= pd.Timestamp(b))]
        te_days = cal_days[(cal_days >= pd.Timestamp(c)) & (cal_days <= pd.Timestamp(d))]
        best, best_v = None, -np.inf
        for lab, tr in trades_by_param.items():
            m = metrics(tr, tr_days)
            v = m.get(select, np.nan)
            if m["n_trades"] >= min_trades and np.isfinite(v) and v > best_v:
                best, best_v = lab, v
        if best is None:
            continue
        mt = metrics(trades_by_param[best], te_days)
        rows.append({"train_start": a, "train_end": b, "test_start": c, "test_end": d, "selected": best,
                     f"train_{select}": best_v, **{f"test_{k}": v for k, v in mt.items()}})
    return pd.DataFrame(rows)


def random_entry_baseline(p: Panel, trades: pd.DataFrame, cost_model: CostModel | None, n_iter: int = 100,
                          seed: int = 0, earliest_entry_bar: int = 1,
                          flat_before_close: int = config.FLAT_BEFORE_CLOSE_MIN) -> pd.DataFrame:
    """Random-entry null matched to the strategy's trades: same days, same holding times, entry time uniform
    over the allowed window, side = fair coin. Gross expectation is ~0 (plus/minus drift), net = -costs.

    Pitfalls deliberately avoided (both leak information and inflate the "random" benchmark):
      * keeping each trade's SIDE while allowing entries before the signal (e.g. entering before an
        opening-range breakout in the breakout's direction);
      * keeping the side AND the realized holding time, even with entries after the signal: realized holds
        encode whether the trade worked (whipsaw losers get short holds), so the null inherits hindsight.
    """
    rng = np.random.default_rng(seed)
    if trades.empty:
        return pd.DataFrame()
    d = trades["day_idx"].to_numpy()
    hold = np.maximum(1, trades["hold_bars"].to_numpy())
    flat_idx = p.n_min[d] - flat_before_close
    last_start = np.maximum(earliest_entry_bar, flat_idx - hold)
    fac = _day_factor(p)[d]
    out = []
    for it in range(n_iter):
        e = rng.integers(earliest_entry_bar, last_start + 1)
        x = np.minimum(e + hold, flat_idx)
        ep, xp = p.o[d, e], p.o[d, x]
        sd = rng.choice([-1, 1], size=len(d))
        g = sd * (xp / ep - 1) * 1e4
        tr = pd.DataFrame({"date": trades["date"].to_numpy(), "side": sd, "gross_bps": g,
                           "entry_min_et": config.RTH_START_MIN + e, "exit_min_et": config.RTH_START_MIN + x,
                           "entry_px_unadj": ep * fac, "exit_px_unadj": xp * fac})
        tr = tr[np.isfinite(tr["gross_bps"])]
        if cost_model is not None:
            tr = cost_model.trade_costs(tr, p.ticker)
            out.append((it, tr["gross_bps"].mean(), tr["net_bps"].mean()))
        else:
            out.append((it, tr["gross_bps"].mean(), np.nan))
    return pd.DataFrame(out, columns=["iter", "avg_gross_bps", "avg_net_bps"])


def lag_entries(entries: np.ndarray, k: int) -> np.ndarray:
    """Shift signals by k bars within each day (k>0 = extra delay; k<0 = LOOK-AHEAD diagnostic only)."""
    out = np.zeros_like(entries)
    if k > 0:
        out[:, k:] = entries[:, :-k]
    elif k < 0:
        out[:, :k] = entries[:, -k:]
    else:
        out[:] = entries
    return out


def shuffle_days(arr: np.ndarray, seed: int = 0) -> np.ndarray:
    """Permute whole days of a signal array (destroys any link between signal and that day's prices)."""
    rng = np.random.default_rng(seed)
    return arr[rng.permutation(arr.shape[0])]
