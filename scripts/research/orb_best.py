#!/usr/bin/env python3
"""Best-combination search for the opening-range breakout, with an independent test on 2011-2018.

Stage 1 (search, 2019-01-02 .. 2025-12-31 -- the data every earlier study looked at). 480 combinations of:
  range      15 | 20 | 30 minutes
  filter     none | GAP (skip breaks against a gap > 1%) | PM (only if the pre-market moved the break's way)
             | GAP+VOL | PM+VOL (VOL = skip breakout minutes with < 1.5x their normal volume)
  stop       RNG = the other side of the range | CAP4 = the same, but never more than 4% from the entry
  time stop  none | 10:30 | 11:00 | 12:00 (out at that time if the trade is not in profit)
  exit       HOLD to 15:55 | SO2 (half at 2R, rest held)
  bearish    SOXS (only if its prior close >= $10) | short SOXL
Selection rule (fixed before running): among combinations averaging >= 60 trades a year, the highest worst-period
mean net per trade over pre (2019-21), dev (2022-01..2024-09) and val (2024-10..2025-12); ties by pooled t.
Also reported: the highest-win-rate combination whose worst-period mean is >= 80% of the best.

Stage 2 (--deep, run once after the pick is registered): the pick, the next four, and the baselines on
2011-06-01 .. 2018-12-31, which no rule has seen. Costs there use the NBBO spread samples for those years.
The 2026 holdout stays sealed.
Writes analysis/strategies/orb_best/.
"""
from __future__ import annotations

import argparse
import itertools

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R

OUT = C.RESEARCH_DIR / "orb_best"
TSTOP = {"none": None, "1030": (59, 0.0), "1100": (89, 0.0), "1200": (149, 0.0)}
FILTERS = {"none": (False, False, False), "GAP": (True, False, False), "PM": (False, True, False),
           "GAP+VOL": (True, False, True), "PM+VOL": (False, True, True)}
_BASE: dict = {}


def orb2_intents(ctx, sig: str = "SOXL", or_len: int = 15, filt: str = "GAP", stop: str = "RNG",
                 exit_: str = "HOLD", leg: str | None = None) -> pd.DataFrame:
    td = ctx[sig]
    p = td.p
    key = (id(ctx), sig, or_len)
    if key not in _BASE:
        base = R.s3_intents(ctx, sig=sig, design="A", or_len=or_len)
        d, j, s = (base[c].to_numpy().astype(int) for c in ("d", "sig", "s"))
        vm = td.minute_mean_prior(np.where(p.valid(), p.v, np.nan), 20)
        pm = td.premarket["pm_last"].to_numpy(float)
        _BASE[key] = base.assign(gap_dir=(td.o0 / td.pc - 1)[d] * 100 * s,
                                 pm_dir=np.sign(pm[d] / td.pc[d] - 1) * s,
                                 trig_vol=p.v[d, j] / vm[d, j])
    it = _BASE[key].copy()
    gapf, pmf, volf = FILTERS[filt]
    if gapf:
        it = it[~(it["gap_dir"] < -1)]
    if pmf:
        it = it[it["pm_dir"] > 0]
    if volf:
        it = it[it["trig_vol"] >= 1.5]
    d, e, s = (it[c].to_numpy().astype(int) for c in ("d", "e", "s"))
    ep = p.o[d, e]
    st = it["stop"].to_numpy(float)
    if stop == "CAP4":
        st = np.where(s > 0, np.maximum(st, ep * 0.96), np.minimum(st, ep * 1.04))
    it["stop"] = st
    Rp = np.abs(ep - st)
    ok = np.isfinite(ep) & (s * (ep - st) > 0)
    tr_r = 2.0 if (exit_ == "SO2" and leg == "A") else np.nan
    it["target"] = ep + s * tr_r * Rp if np.isfinite(tr_r) else np.nan
    return E.make_intents(it[ok].drop(columns=["gap_dir", "pm_dir", "trig_vol"]).to_dict("records"))


def run(ctx, cms, or_len, filt, stop, tstop, exit_, bear):
    legs = ("A", "B") if exit_ == "SO2" else (None,)
    mode = "switch" if bear == "SOXS" else "switch_short"
    exs = []
    for lg in legs:
        it = orb2_intents(ctx, or_len=or_len, filt=filt, stop=stop, exit_=exit_, leg=lg)
        tr = E.simulate(ctx["SOXL"], it, one_position=False, time_stop=TSTOP[tstop])
        ex, _ = E.execute(tr, ctx, mode=mode)
        exs.append(E.add_costs(ex, cms))
    ex = E.merge_legs(exs, legs) if len(exs) > 1 else exs[0]
    ex["period"] = C.period_of(ex["date"])
    return ex


def stats(ex: pd.DataFrame, mask=None) -> dict:
    g = ex if mask is None else ex[mask]
    x = g["net_B"].to_numpy(float)
    if len(x) < 3:
        return {"n": len(x)}
    mu, t, _ = C.cluster_t(x, g["date"].to_numpy())
    cum = np.cumsum(x)
    return {"n": len(x), "win": float((x > 0).mean()), "net": mu, "t": t, "total_pct": x.sum() / 100,
            "maxdd_pct": float((cum - np.maximum.accumulate(cum)).min()) / 100,
            "avg_win_pct": float(x[x > 0].mean()) / 100, "avg_loss_pct": float(x[x <= 0].mean()) / 100}


def search(ctx, cms) -> pd.DataFrame:
    rows = []
    grid = itertools.product((15, 20, 30), tuple(FILTERS), ("RNG", "CAP4"), tuple(TSTOP), ("HOLD", "SO2"),
                             ("SOXS", "short"))
    for or_len, filt, stop, tstop, exit_, bear in grid:
        ex = run(ctx, cms, or_len, filt, stop, tstop, exit_, bear)
        ex = ex[ex["date"] <= "2025-12-31"]
        r = {"config": f"{or_len}|{filt}|{stop}|{tstop}|{exit_}|{bear}", "range": or_len, "filter": filt, "stop": stop,
             "time_stop": tstop, "exit": exit_, "bearish": bear}
        for per in ("pre", "dev", "val"):
            r.update({f"{per}_{k}": v for k, v in stats(ex, ex["period"] == per).items()})
        r.update({f"all_{k}": v for k, v in stats(ex).items()})
        r["trades_per_year"] = r["all_n"] / 7.0
        r["worst_period_net"] = min(r["pre_net"], r["dev_net"], r["val_net"])
        rows.append(r)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep", action="store_true", help="run the registered picks on 2011-06-01 .. 2018-12-31")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 40)
    if not a.deep:
        g = search(C.Context(), cms)
        elig = g[g["trades_per_year"] >= 60].sort_values(["worst_period_net", "all_t"], ascending=False)
        g.to_csv(OUT / "search_2019_2025.csv", index=False, float_format="%.4f")
        best = elig.iloc[0]
        hw = elig[elig["worst_period_net"] >= 0.8 * best["worst_period_net"]].sort_values("all_win", ascending=False)
        show = ["config", "trades_per_year", "all_win", "all_net", "all_t", "pre_net", "dev_net", "val_net",
                "worst_period_net", "all_maxdd_pct", "all_avg_win_pct", "all_avg_loss_pct"]
        print("== top 15 (>= 60 trades a year) by worst-period mean\n" + elig[show].head(15).round(2).to_string(index=False))
        print("\n== highest win rate within 80% of the best worst-period mean\n" + hw[show].head(5).round(2).to_string(index=False))
        for col in ("range", "filter", "stop", "time_stop", "exit", "bearish"):
            print(f"\n-- by {col} (mean over other settings)\n" +
                  g.groupby(col)[["all_win", "all_net", "worst_period_net", "all_maxdd_pct"]].mean().round(2).to_string())
        print(f"\nPICK: {best['config']}\nHIGH-WIN-RATE PICK: {hw.iloc[0]['config']}")
        return
    # ---- stage 2: independent test on 2011-06-01 .. 2018-12-31 (run once, after registration)
    g = pd.read_csv(OUT / "search_2019_2025.csv")
    elig = g[g["trades_per_year"] >= 60].sort_values(["worst_period_net", "all_t"], ascending=False)
    picks = list(elig["config"].head(5))
    best = elig.iloc[0]
    hw = elig[elig["worst_period_net"] >= 0.8 * best["worst_period_net"]].sort_values("all_win", ascending=False)
    picks += [hw.iloc[0]["config"], "15|none|RNG|none|HOLD|SOXS", "15|GAP|RNG|1100|HOLD|SOXS"]
    deep = C.Context(start="2011-06-01", end="2018-12-31")
    rows = []
    for cfg in dict.fromkeys(picks):
        or_len, filt, stop, tstop, exit_, bear = cfg.split("|")
        ex = run(deep, cms, int(or_len), filt, stop, tstop, exit_, bear)
        label = ("PICK" if cfg == best["config"] else "high-win-rate pick" if cfg == hw.iloc[0]["config"] else
                 "baseline S3-01" if cfg.startswith("15|none|RNG|none|HOLD") else
                 "S13-A" if cfg == "15|GAP|RNG|1100|HOLD|SOXS" else "runner-up")
        r = {"config": cfg, "role": label, **{f"deep_{k}": v for k, v in stats(ex).items()},
             "deep_trades_per_year": len(ex) / 7.6}
        yr = ex.groupby(ex["date"].dt.year)["net_B"].mean().round(0)
        r["deep_net_by_year"] = ", ".join(f"{y}: {v:+.0f}" for y, v in yr.items())
        r["deep_positive_years"] = f"{int((yr > 0).sum())}/{len(yr)}"
        rows.append(r)
        ex.to_csv(OUT / f"deep_trades_{cfg.replace('|', '_')}.csv", index=False, float_format="%.4f")
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "deep_test_2011_2018.csv", index=False, float_format="%.4f")
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
