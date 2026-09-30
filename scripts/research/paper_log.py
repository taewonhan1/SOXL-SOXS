#!/usr/bin/env python3
"""Forward paper-trading log (RESEARCH_PLAN.md, Study 9).

Run after each session's close. It refreshes the cached bars, runs the tracked rules on the new session(s)
and appends their trades to analysis/strategies/paper_log.csv. The log starts 2026-09-28, the first
session after the research data ends; earlier dates are refused unless --allow-backfill (for testing),
so the 2026 holdout is never used here.

Tracked rules (no rule passed the pre-registered bar; these are the near-misses plus one regime watch):
  S3-01  15-minute opening-range breakout, SOXS leg only when SOXS >= $10
  S8-01  same rule, bearish leg = short SOXL
  S4-02  noise-boundary momentum, k = 1.0, trailing checks at half-hour marks
  S4-04  noise-boundary momentum, k = 1.5, trailing checks at half-hour marks
  S1-06  late-day fade, |SOXX| >= 1%, exit at the official close (regime watch)
  S13-A  final breakout rules (REGISTRY.md): skip breaks against a >1% gap, range stop, 11:00 time stop, hold to 15:55
  S13-B  S13-A without the 11:00 time stop
It also prints the S15 kill-switch state (mean of the last 60 S3-01 signals; S15 = S3-01, see REGISTRY.md).

Usage:
  python scripts/research/paper_log.py                  # all sessions since the last logged one
  python scripts/research/paper_log.py --start 2026-09-28 --end 2026-10-02
"""
from __future__ import annotations

import argparse
from datetime import datetime

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab import calendar as scal
from soxlab import config
from soxlab import data as sdata
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R
from orb_strategy_design import orb_intents

FORWARD_START = "2026-09-28"
LOG = C.RESEARCH_DIR / "paper_log.csv"
TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "QQQ"]
RULES = {
    "S3-01": (R.s3_intents, False, "switch", dict(design="A")),
    "S8-01": (R.s3_intents, False, "switch_short", dict(design="A")),
    "S4-02": (R.s4_trades, True, "switch", dict(k=1.0, check="H")),
    "S4-04": (R.s4_trades, True, "switch", dict(k=1.5, check="H")),
    "S1-06": (R.s1_intents, False, "switch", dict(thr=0.01, gate=False, exit_="E3", exec_mode="switch")),
    "S13-A": (orb_intents, False, "switch", dict(filt="F1", stop_kind="OR", exit_="HOLD"), dict(time_stop=(89, 0.0))),
    "S13-B": (orb_intents, False, "switch", dict(filt="F1", stop_kind="OR", exit_="HOLD")),
}


def kill_switch_state(log: pd.DataFrame, w: int = 60) -> tuple[float, bool, int]:
    """S15 kill switch (REGISTRY.md): mean case-B net of the last ``w`` S3-01 signals, backtest history before the
    forward start plus logged forward signals. ON when the mean is > 0."""
    hist = pd.read_parquet(C.RESEARCH_DATA / "trades" / "study3_opening_range_breakout" / "S3-01.parquet")
    parts = [hist[hist["date"] < pd.Timestamp(FORWARD_START)][["date", "net_B"]]]
    if len(log) and "net_B_bps" in log:
        f = log[(log["rule"] == "S3-01") & log["net_B_bps"].notna()]
        parts.append(pd.DataFrame({"date": pd.to_datetime(f["date"]), "net_B": f["net_B_bps"].astype(float)}))
    x = pd.concat(parts, ignore_index=True).sort_values("date")["net_B"].to_numpy()[-w:]
    return float(x.mean()), bool(x.mean() > 0), len(x)


def refresh_data(end: str) -> None:
    sdata.download_minute_bars(TICKERS, start="2026-01-01", end=end)
    sdata.download_daily(TICKERS, start="2010-01-01", end=end)
    scal.build_calendar(start=config.HISTORY_START, end=end)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start")
    ap.add_argument("--end", default=pd.Timestamp.now(tz=config.TZ).strftime("%Y-%m-%d"))
    ap.add_argument("--allow-backfill", action="store_true", help="permit dates before 2026-09-28 (testing only)")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print trades without appending to the log")
    a = ap.parse_args()
    log = pd.read_csv(LOG, parse_dates=["date"]) if LOG.exists() else pd.DataFrame()
    start = a.start or (max(pd.Timestamp(FORWARD_START), log["date"].max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                        if len(log) else FORWARD_START)
    if pd.Timestamp(start) < pd.Timestamp(FORWARD_START) and not a.allow_backfill:
        raise SystemExit(f"start {start} is before the forward period ({FORWARD_START}); use --allow-backfill to test")
    if not a.no_download:
        refresh_data(a.end)
    lookback = (pd.Timestamp(start) - pd.Timedelta(days=400)).strftime("%Y-%m-%d")
    ctx = C.Context(start=lookback, end=a.end)
    in_win = (ctx.dates >= pd.Timestamp(start)) & (ctx.dates <= pd.Timestamp(a.end))
    if not in_win.any():
        print(f"no complete sessions between {start} and {a.end} in the cached data yet")
        return
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    rows = []
    for rid, (fn, is_tr, mode, prm, *sim_kw) in RULES.items():
        obj = fn(ctx, sig="SOXL", **prm)
        tr = obj if is_tr else E.simulate(ctx["SOXL"], obj, **(sim_kw[0] if sim_kw else {}))
        ex, sk = E.execute(tr, ctx, mode=mode)
        ex = E.add_costs(ex, cms)
        ex = ex[(ex["date"] >= pd.Timestamp(start)) & (ex["date"] <= pd.Timestamp(a.end))]
        for r in ex.itertuples(index=False):
            rows.append({"logged_at": datetime.utcnow().isoformat(timespec="seconds") + "Z", "date": r.date,
                         "rule": rid, "inst": r.inst, "side": int(r.side), "signal": "bull" if r.s > 0 else "bear",
                         "entry_time": f"{r.entry_min // 60:02d}:{r.entry_min % 60:02d}",
                         "exit_time": f"{r.exit_min // 60:02d}:{r.exit_min % 60:02d}", "exit_kind": r.x_kind,
                         "exit_reason": r.reason, "entry_px": round(r.ep_u, 4), "exit_px": round(r.xp_u, 4),
                         "gross_bps": r.gross_bps, "net_A_bps": r.net_A, "net_B_bps": r.net_B})
        sk = sk[(sk["date"] >= pd.Timestamp(start)) & (sk["date"] <= pd.Timestamp(a.end))] if len(sk) else sk
        for r in sk.itertuples(index=False):
            rows.append({"logged_at": datetime.utcnow().isoformat(timespec="seconds") + "Z", "date": r.date,
                         "rule": rid, "inst": "SOXS", "side": 1, "signal": "bear", "exit_reason": "skipped: SOXS < $10"})
    new = pd.DataFrame(rows)
    print(new.round(2).to_string(index=False) if len(new) else "no trades in the window")
    ks_log = pd.concat([log, new], ignore_index=True) if not (a.dry_run or new.empty) else log
    mu, on, n = kill_switch_state(ks_log)
    print(f"S15 kill switch: last {n} S3-01 signals average {mu:+.1f} bps -> {'ON (take signals)' if on else 'OFF (paper-track only)'}")
    if a.dry_run or new.empty:
        return
    out = pd.concat([log, new], ignore_index=True)
    out = out.drop_duplicates(subset=["date", "rule", "entry_time", "exit_reason"], keep="first")
    out.sort_values(["date", "rule", "entry_time"]).to_csv(LOG, index=False, float_format="%.4f")
    st = out[out["net_B_bps"].notna()].groupby("rule")["net_B_bps"].agg(["count", "mean", "std"])
    st["t"] = st["mean"] / (st["std"] / np.sqrt(st["count"]))
    print("\nforward record (case B, bps/trade):\n" + st.round(2).to_string())
    print(f"appended {len(new)} rows -> {LOG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
