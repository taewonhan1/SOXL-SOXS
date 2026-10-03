#!/usr/bin/env python3
"""How early does SOXL show the day's trend direction, and does entering earlier than 10:30 pay?

Exploratory; the grid below was fixed before running and every cell is reported, per era (2011-06..2018,
2019..2025, 2026-01..09).
A. Direction on days that END as trend days (SOXX |open->close| >= 2%), hindsight: how often the sign of the opening
   gap and of SOXL's move from its 09:30 open at 09:35 / 09:45 / 10:00 / 10:30 / 11:00 already matched the day's
   final direction, and how often the move so far was already >= 1% / 2% / 3% that way.
B. Entries: at the close of 09:44 / 09:59 / 10:14 / 10:29, if SOXL is 2-3% or 3-4% from its open, go with it at the
   next minute's open (up -> SOXL, down -> SOXS if its prior close >= $10), fixed 1.5% stop on SOXL's chart from
   the entry price, exit 15:55, case B. Results in % and in R (net / 1.5%), for all such days, for days where the
   move agrees with the opening gap's direction, and for days where it disagrees.
C. Cascade, set after seeing B: the first that applies of (09:45, 2-3% with the gap), (10:00, 3-4% with the gap),
   (10:30, 3-4% either way); one trade a day, same stop and exit. Compared with the 10:30 rule alone.
Writes analysis/strategies/early_trend/.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "early_trend"
ERAS = (("2011-2018", "2011-06-01", "2018-12-31"), ("2019-2025", "2019-01-02", "2025-12-31"),
        ("2026", "2026-01-02", "2026-09-25"))
SEEN_AT = {"09:35": 4, "09:45": 14, "10:00": 29, "10:30": 59, "11:00": 89}
ENTRY_AT = {"09:45": 14, "10:00": 29, "10:15": 44, "10:30": 59}
BANDS = ((2, 3, "2-3%"), (3, 4, "3-4%"))
STOP = 0.015


def direction_table(era: str, ctx, in_era: np.ndarray) -> list[dict]:
    L, X = ctx["SOXL"], ctx["SOXX"]
    p = L.p
    oc = X.last_c / X.o0 - 1
    days = np.flatnonzero(in_era & (np.abs(oc) >= 0.02) & np.isfinite(L.o0))
    final = np.sign(oc[days])
    rows = [{"era": era, "seen_at": "gap (09:30)", "trend_days": len(days),
             "direction_right": float(np.mean(np.sign(L.o0[days] / L.pc[days] - 1) == final))}]
    for t, bar in SEEN_AT.items():
        m = p.c[days, bar] / L.o0[days] - 1
        r = {"era": era, "seen_at": t, "trend_days": len(days), "direction_right": float(np.mean(np.sign(m) == final))}
        for k in (1, 2, 3):
            r[f"already_{k}pct_that_way"] = float(np.mean(final * m >= k / 100))
        rows.append(r)
    return rows


def entries(era: str, ctx, in_era: np.ndarray, cms: dict) -> pd.DataFrame:
    L = ctx["SOXL"]
    p = L.p
    gap = np.sign(L.o0 / L.pc - 1)
    parts = []
    for (t, bar), (lo, hi, band) in itertools.product(ENTRY_AT.items(), BANDS):
        it, agree = [], {}
        for d in np.flatnonzero(in_era):
            flat = int(p.n_min[d]) - FLAT_OPEN
            if bar + 1 >= flat or not (np.isfinite(L.o0[d]) and np.isfinite(p.c[d, bar]) and np.isfinite(p.o[d, bar + 1])):
                continue
            m = (p.c[d, bar] / L.o0[d] - 1) * 100
            if lo <= abs(m) < hi:
                s = 1 if m > 0 else -1
                agree[d] = gap[d] == s
                it.append({"d": d, "sig": bar, "e": bar + 1, "s": s, "tx": flat, "tx_kind": "open",
                           "stop": p.o[d, bar + 1] * (1 - s * STOP)})
        ex = E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], cms)
        ex["with_gap"] = pd.Series(agree).reindex(ex["d"].to_numpy().astype(int)).to_numpy()
        parts.append(ex.assign(era=era, entry=t, band=band))
    return pd.concat(parts, ignore_index=True)


CASCADE = (("09:45", 14, 2, 3, True), ("10:00", 29, 3, 4, True), ("10:30", 59, 3, 4, False))


def cascade(era: str, ctx, in_era: np.ndarray, cms: dict, steps=CASCADE) -> pd.DataFrame:
    L = ctx["SOXL"]
    p = L.p
    gap = np.sign(L.o0 / L.pc - 1)
    it, step_of = [], {}
    for d in np.flatnonzero(in_era):
        flat = int(p.n_min[d]) - FLAT_OPEN
        if not np.isfinite(L.o0[d]):
            continue
        for t, bar, lo, hi, need_gap in steps:
            if bar + 1 >= flat or not (np.isfinite(p.c[d, bar]) and np.isfinite(p.o[d, bar + 1])):
                continue
            m = (p.c[d, bar] / L.o0[d] - 1) * 100
            s = 1 if m > 0 else -1
            if lo <= abs(m) < hi and (not need_gap or gap[d] == s):
                it.append({"d": d, "sig": bar, "e": bar + 1, "s": s, "tx": flat, "tx_kind": "open",
                           "stop": p.o[d, bar + 1] * (1 - s * STOP)})
                step_of[d] = t
                break
    ex = E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], cms)
    ex["step"] = pd.Series(step_of).reindex(ex["d"].to_numpy().astype(int)).to_numpy()
    return ex.assign(era=era)


def plan_summary(name: str, ex: pd.DataFrame, years: float) -> dict:
    ex = ex.sort_values(["date", "e"])
    r = (ex["net_B"] / 100 / (STOP * 100)).to_numpy()
    cum = np.cumsum(r)
    yr = pd.Series(r).groupby(ex["date"].dt.year.to_numpy()).sum()
    era = pd.Series(r).groupby(ex["era"].to_numpy()).mean()
    return {"plan": name, "trades": len(r), "trades_per_year": len(r) / years, "win": float((r > 0).mean()),
            "avg_R": r.mean(), "R_per_year": r.sum() / years, "max_drawdown_R": (cum - np.maximum.accumulate(cum)).min(),
            "losing_years": f"{int((yr < 0).sum())}/{len(yr)}", **{f"R_{e}": era.get(e, np.nan) for e, _, _ in ERAS}}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cms = {"B": C.cost_model(C.COMMISSION_B)}
    dirs, trades, casc, base = [], [], [], []
    for era, start, end in ERAS:
        ctx = C.Context(start="2025-10-01" if era == "2026" else start, end=end)
        in_era = (ctx.dates >= start) & (ctx.dates <= end)
        dirs += direction_table(era, ctx, in_era)
        trades.append(entries(era, ctx, in_era, cms))
        casc.append(cascade(era, ctx, in_era, cms))
        base.append(cascade(era, ctx, in_era, cms, steps=(CASCADE[-1],)))
    dirs = pd.DataFrame(dirs)
    ex = pd.concat(trades, ignore_index=True)
    ex["net_pct"] = ex["net_B"] / 100
    ex["R"] = ex["net_pct"] / (STOP * 100)
    ex = pd.concat([ex.assign(subset="all"), ex[ex["with_gap"] == True].assign(subset="with the gap"),  # noqa: E712
                    ex[ex["with_gap"] == False].assign(subset="against the gap")], ignore_index=True)  # noqa: E712
    key = ["entry", "band", "subset"]
    years = sum((pd.Timestamp(e) - pd.Timestamp(s)).days / 365.25 for _, s, e in ERAS)
    pooled = ex.groupby(key).agg(trades=("R", "size"), win=("R", lambda x: (x > 0).mean()), avg_pct=("net_pct", "mean"),
                                 avg_R=("R", "mean"))
    pooled["trades_per_year"] = pooled["trades"] / years
    by_era = ex.pivot_table(index=key, columns="era", values="R", aggfunc="mean")
    pooled = pooled.join(by_era.add_prefix("R_"))
    pooled["positive_all_eras"] = (by_era > 0).all(axis=1)
    casc, base = pd.concat(casc, ignore_index=True), pd.concat(base, ignore_index=True)
    plans = pd.DataFrame([plan_summary("10:30 rule alone (3-4%, 1.5% stop)", base, years),
                          plan_summary("cascade: 09:45 / 10:00 with the gap, else 10:30", casc, years)]
                         + [plan_summary(f"  of which entered at {t}", casc[casc["step"] == t], years)
                            for t, *_ in CASCADE])
    plans.to_csv(OUT / "cascade.csv", index=False, float_format="%.4f")
    dirs.to_csv(OUT / "direction_on_trend_days.csv", index=False, float_format="%.4f")
    pooled.to_csv(OUT / "entries.csv", float_format="%.4f")
    pd.set_option("display.width", 250)
    print(dirs.round(2).to_string(index=False))
    print("\n" + pooled.round(2).to_string())
    print("\n" + plans.round(2).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
