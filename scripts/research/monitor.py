#!/usr/bin/env python3
"""Daily regime monitors (RESEARCH_PLAN.md, Study 9).

Market-state series only (no strategy P&L from the sealed 2026 holdout); rule performance comes from the
forward paper log. Writes analysis/strategies/monitors.csv and analysis/strategies/MONITOR.md.

Monitors
  late_slope_SOXL / late_slope_SOXX  trailing-120-session slope of (15:30->close) on (open->15:30); < 0 = fade regime
  burst_next_open_60                 mean gross (bps) of the Study 2 opening-burst signal traded at the next open,
                                     trailing 60 sessions (was ~+3.6 in validation vs ~7.7 bps of costs)
  soxs_close_unadj / soxs_rel_tick   SOXS price level and one cent in bps; SOXS leg is on when price >= $10
  soxl_range_med_20                  median SOXL regular-session range, trailing 20 sessions (%)
  soxl_one_tick_share_20             share of NBBO samples at a one-cent spread (13 half-hour points/day, 20 days)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R

PAPER = C.RESEARCH_DIR / "paper_log.csv"


def main() -> None:
    cal = C.Context().cal
    ctx = C.Context(start="2021-06-01", end=cal.index.max().strftime("%Y-%m-%d"))
    L, S, X = ctx["SOXL"], ctx["SOXS"], ctx["SOXX"]
    df = pd.DataFrame(index=ctx.dates)
    df["late_slope_SOXL"] = R.s1_gate_slope(L)
    df["late_slope_SOXX"] = R.s1_gate_slope(X)
    burst = E.simulate(L, R.s2_intents(ctx, k=2.0, hold=1, filt="F0"))
    daily = burst.groupby("d")["gross_chart_bps"].mean().reindex(range(len(ctx.dates)))
    df["burst_next_open_60"] = daily.rolling(60, min_periods=20).mean().to_numpy()
    df["soxs_close_unadj"] = S.off_u
    df["soxs_rel_tick_bps"] = 0.01 / S.off_u * 1e4
    df["soxs_leg_on_next_day"] = S.off_u >= C.SOXS_MIN_PRICE
    df["soxl_range_med_20"] = pd.Series(L.range_pct * 100).rolling(20, min_periods=10).median().to_numpy()
    # SOXL spread regime from NBBO points at 13 half-hour marks over the last 20 sessions
    last = ctx.dates[-20:]
    pts = [C.bar_time_ns(d, b) + 15 * 10**9 for d in last for b in range(0, 390, 30)]
    q = E.nbbo_lookup("SOXL", pts)
    spr = (q["ask"] - q["bid"]).to_numpy()
    ok = np.isfinite(spr) & (spr > 0)
    one_tick = float(np.mean(np.abs(spr[ok] - 0.01) < 1e-6)) if ok.any() else np.nan
    df["soxl_one_tick_share_20"] = np.nan
    df.iloc[-1, df.columns.get_loc("soxl_one_tick_share_20")] = one_tick
    df = df[df.index >= "2022-01-01"]
    df.index.name = "date"
    df.to_csv(C.RESEARCH_DIR / "monitors.csv", float_format="%.5f")
    cur = df.iloc[-1]
    lines = [f"# Regime monitor — {df.index[-1]:%Y-%m-%d}", "",
             "| Monitor | Value | Reading |", "|---|---|---|",
             f"| Late-day slope, SOXL (120 sessions) | {cur.late_slope_SOXL:+.3f} | "
             f"{'fade regime (late moves lean against the day)' if cur.late_slope_SOXL < 0 else 'momentum/neutral regime'} |",
             f"| Late-day slope, SOXX (120 sessions) | {cur.late_slope_SOXX:+.3f} | cross-check on the unlevered semis ETF |",
             f"| Opening-burst edge at next open (60 sessions) | {cur.burst_next_open_60:+.1f} bps | "
             "needs > ~8 bps to cover costs; Study 2 failed at ~+3.6 |",
             f"| SOXS price (last close) | ${cur.soxs_close_unadj:,.2f} | "
             f"SOXS leg {'ON' if cur.soxs_leg_on_next_day else 'OFF (skip bearish or short SOXL)'}; one cent = "
             f"{cur.soxs_rel_tick_bps:.1f} bps |",
             f"| SOXL median daily range (20 sessions) | {cur.soxl_range_med_20:.2f}% | movement budget |",
             f"| SOXL share of time at a one-cent spread (20 sessions) | {one_tick:.0%} | "
             f"{'tick-constrained book' if one_tick > 0.5 else 'fluid, multi-tick book'} |", ""]
    if PAPER.exists():
        pl = pd.read_csv(PAPER, parse_dates=["date"])
        pl = pl[pl["net_B_bps"].notna()]
        lines += ["## Forward paper record (case B)", "", "| Rule | Trades | Mean net (bps) | t | Last-60 mean | Status |",
                  "|---|---|---|---|---|---|"]
        for rid, g in pl.groupby("rule"):
            x = g["net_B_bps"].to_numpy()
            t = x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan
            l60 = x[-60:]
            t60 = l60.mean() / (l60.std(ddof=1) / np.sqrt(len(l60))) if len(l60) > 2 and l60.std(ddof=1) > 0 else np.nan
            paused = len(l60) >= 60 and l60.mean() < 0 and t60 < -1
            lines.append(f"| {rid} | {len(x)} | {x.mean():+.1f} | {t:.2f} | {l60.mean():+.1f} | "
                         f"{'PAUSED' if paused else ('judge at 60 trades' if len(x) < 60 else 'active')} |")
    else:
        lines += ["Forward paper log is empty; run `python scripts/research/paper_log.py` after each close."]
    (C.RESEARCH_DIR / "MONITOR.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"wrote {(C.RESEARCH_DIR / 'monitors.csv').relative_to(ROOT)} and MONITOR.md")


if __name__ == "__main__":
    main()
