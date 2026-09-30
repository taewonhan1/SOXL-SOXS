#!/usr/bin/env python3
"""Real-time trend odds: what SOXL's move from the 09:30 open, seen at a given time, says about the rest of the day.

For each check time (10:00, 10:30, 11:00, 11:30, 12:00, 13:00, 14:00 = closes of bars 29/59/89/119/149/209/269) and
each size of move already made (1-2%, 2-3%, 3-4%, 4-6%, >=6%, either direction):
  * going with the move from the next minute's open to 15:55 (up -> SOXL, down -> SOXS if its prior close >= $10),
    case B costs: win rate and mean net per trade, with no stop and with a stop back at SOXL's 09:30 open;
  * how often SOXL keeps going the same way from the check to the close;
  * how often the day finishes as a trend day the same way (SOXX open->close >= 2% in the move's direction).
Two more live questions, same eras:
  * how much of the day's move is already done at each check, on days that end as trend days, and the median
    SOXL move still to come (check close -> last close, in the trend's direction);
  * the flip: SOXL first gets k% (2 / 3 / 4) from its open, then a 1-minute close back through the open by 14:30
    -> take the other side (SOXS after an up move, SOXL after a down move) at the next open, hold to 15:55, no stop.
Descriptive (no rule is selected); every cell is shown for 2011-06..2018, 2019..2025 and 2026-01..09.
Writes analysis/strategies/intraday_trend_odds/.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "intraday_trend_odds"
ERAS = (("2011-2018", "2011-06-01", "2018-12-31"), ("2019-2025", "2019-01-02", "2025-12-31"),
        ("2026", "2026-01-02", "2026-09-25"))
CHECKS = {"10:00": 29, "10:30": 59, "11:00": 89, "11:30": 119, "12:00": 149, "13:00": 209, "14:00": 269}
BUCKETS = [(1, 2, "1-2%"), (2, 3, "2-3%"), (3, 4, "3-4%"), (4, 6, "4-6%"), (6, 1e9, ">=6%")]
FLIP_K = (2, 3, 4)
FLIP_LAST = 299                      # latest cross bar for a flip (close of 14:29)


def clock(bar: int) -> str:
    return f"{9 + (30 + bar) // 60}:{(30 + bar) % 60:02d}"


def remaining(era: str, ctx, in_era: np.ndarray, soxx_oc: np.ndarray) -> list[dict]:
    """On days that end as trend days: share of SOXL's open->last-close move done at each check, and the move
    still to come from the check close, in the day's direction."""
    L = ctx["SOXL"]
    p = L.p
    rows = []
    days = [d for d in np.flatnonzero(in_era & (soxx_oc >= 0.02)) if np.isfinite(L.o0[d])]
    last = np.array([p.c[d, int(p.n_min[d]) - 1] for d in days])
    o0 = L.o0[days]
    tot = last / o0 - 1
    for tname, bar in CHECKS.items():
        cb = p.c[days, bar]
        ok = np.isfinite(cb) & (np.abs(tot) > 0)
        done = (cb[ok] / o0[ok] - 1) / tot[ok]
        left = np.sign(tot[ok]) * (last[ok] / cb[ok] - 1) * 100
        rows.append({"era": era, "check": tname, "trend_days": int(ok.sum()),
                     "median_share_done": float(np.median(done)), "median_pct_left": float(np.median(left)),
                     "share_with_2pct_plus_left": float(np.mean(left >= 2))})
    return rows


def flip_intents(ctx, in_era: np.ndarray, k: float) -> pd.DataFrame:
    L = ctx["SOXL"]
    p = L.p
    rows = []
    for d in np.flatnonzero(in_era):
        n = int(p.n_min[d])
        flat = n - FLAT_OPEN
        if not np.isfinite(L.o0[d]):
            continue
        m = p.c[d, :n] / L.o0[d] - 1
        best = None
        for s in (1, -1):                              # s = direction of the move that gets erased
            hit = np.flatnonzero(s * m >= k / 100)
            if not len(hit):
                continue
            back = np.flatnonzero(s * m[hit[0] + 1:] <= 0)
            if not len(back):
                continue
            t2 = hit[0] + 1 + back[0]
            if t2 <= FLIP_LAST and t2 + 1 < flat and (best is None or t2 < best[0]):
                best = (t2, -s)
        if best:
            rows.append({"d": d, "sig": best[0], "e": best[0] + 1, "s": best[1], "tx": flat, "tx_kind": "open"})
    return E.make_intents(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    rows, rem, flips = [], [], []
    for era, start, end in ERAS:
        ctx = C.Context(start="2025-10-01" if era == "2026" else start, end=end)
        L, X = ctx["SOXL"], ctx["SOXX"]
        p = L.p
        soxx_ret = X.last_c / X.o0 - 1
        soxx_oc = np.abs(soxx_ret)
        in_era = (ctx.dates >= start) & (ctx.dates <= end)
        rem += remaining(era, ctx, in_era, soxx_oc)
        for k in FLIP_K:
            ex = E.add_costs(E.execute(E.simulate(L, flip_intents(ctx, in_era, k)), ctx, mode="switch")[0], cms)
            x = ex["net_B"].to_numpy(float)
            years = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
            flips.append({"era": era, "first_move_k_pct": k, "trades": len(x), "trades_per_year": len(x) / years,
                          "to_soxs": float((ex["s"] < 0).mean()) if len(x) else np.nan,
                          "win": float((x > 0).mean()) if len(x) else np.nan,
                          "net_pct": float(x.mean()) / 100 if len(x) else np.nan,
                          "median_entry": clock(int(np.median(ex["e"]))) if len(x) else ""})
        for (tname, bar), (lo, hi, bname) in itertools.product(CHECKS.items(), BUCKETS):
            cand = []
            for d in np.flatnonzero(in_era):
                flat = int(p.n_min[d]) - FLAT_OPEN
                if bar + 1 >= flat or not (np.isfinite(L.o0[d]) and np.isfinite(p.c[d, bar])):
                    continue
                m = (p.c[d, bar] / L.o0[d] - 1) * 100
                if lo <= abs(m) < hi:
                    cand.append((d, 1 if m > 0 else -1, flat))
            if len(cand) < 5:
                continue
            r = {"era": era, "check": tname, "move_so_far": bname, "days": len(cand)}
            d_arr = np.array([c[0] for c in cand])
            s_arr = np.array([c[1] for c in cand])
            last = np.array([p.c[d, int(p.n_min[d]) - 1] for d in d_arr])
            r["keeps_going_to_close"] = float(np.mean(np.sign(last - p.c[d_arr, bar]) == s_arr))
            r["trend_day_same_way"] = float(np.mean(soxx_ret[d_arr] * s_arr >= 0.02))
            for stop in ("none", "OPEN"):
                it = E.make_intents([{"d": d, "sig": bar, "e": bar + 1, "s": s, "tx": flat, "tx_kind": "open",
                                      "stop": (L.o0[d] if stop == "OPEN" else np.nan)} for d, s, flat in cand])
                ex = E.add_costs(E.execute(E.simulate(L, it), ctx, mode="switch")[0], cms)
                sfx = "" if stop == "none" else "_stop_at_open"
                r[f"trades{sfx}"] = len(ex)
                r[f"win{sfx}"] = float((ex["net_B"] > 0).mean()) if len(ex) else np.nan
                r[f"net_pct{sfx}"] = float(ex["net_B"].mean()) / 100 if len(ex) else np.nan
            rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "odds.csv", index=False, float_format="%.4f")
    key = ["check", "move_so_far"]
    order = {k: i for i, k in enumerate(CHECKS)}
    border = {b[2]: i for i, b in enumerate(BUCKETS)}
    srt = lambda t: t.sort_index(key=lambda s: s.map(order) if s.name == "check" else s.map(border))  # noqa: E731
    w = srt(df.pivot_table(index=key, columns="era", values=["net_pct", "net_pct_stop_at_open", "win", "trend_day_same_way"]))
    wm = lambda g, col, n: float((g[col] * g[n]).sum() / g[n].sum())                                   # noqa: E731
    cols = ["days", "trades", "trades_stop_at_open", "trend_day_same_way", "keeps_going_to_close", "win", "net_pct",
            "win_stop_at_open", "net_pct_stop_at_open"]
    pooled = srt(df.groupby(key)[cols].apply(lambda g: pd.Series({
        "days": int(g["days"].sum()), "trend_day_same_way": wm(g, "trend_day_same_way", "days"),
        "keeps_going_to_close": wm(g, "keeps_going_to_close", "days"),
        "win": wm(g, "win", "trades"), "net_pct": wm(g, "net_pct", "trades"),
        "win_stop_at_open": wm(g, "win_stop_at_open", "trades_stop_at_open"),
        "net_pct_stop_at_open": wm(g, "net_pct_stop_at_open", "trades_stop_at_open")})))
    pooled["positive_all_3_eras"] = (w["net_pct"] > 0).all(axis=1).reindex(pooled.index)
    pooled["positive_all_3_eras_stop"] = (w["net_pct_stop_at_open"] > 0).all(axis=1).reindex(pooled.index)
    pooled.to_csv(OUT / "pooled.csv", float_format="%.4f")
    rem = pd.DataFrame(rem)
    rem.to_csv(OUT / "trend_day_move_done.csv", index=False, float_format="%.4f")
    flips = pd.DataFrame(flips)
    flips.to_csv(OUT / "flip_at_open.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    print(w.round(3).to_string())
    print("\n== pooled over 2011-2026 (go with the move to 15:55)\n" + pooled.round(3).to_string())
    print("\n== trend days: how much of SOXL's move is done at each check\n" +
          rem.pivot_table(index="check", columns="era", values=["median_share_done", "median_pct_left",
                                                                "share_with_2pct_plus_left"]).reindex(list(CHECKS)).round(2).to_string())
    print("\n== flip when SOXL closes back through its open (by 14:30) after a k% move\n" + flips.round(3).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
