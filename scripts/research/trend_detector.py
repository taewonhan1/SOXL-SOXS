#!/usr/bin/env python3
"""Study T1: early trend-day detector (REGISTRY.md; registered 2026-10-03 before its data was downloaded).

Signals at 09:45 (bar 14) and 10:00 (bar 29) when SOXL is >= 1% from its 09:30 open; direction s = sign of the
move. Targets: T1 = trend day that way (SOXX open->close x s >= 2%); T2 = the trade in R (next bar's open, fixed
1.5% stop on SOXL's chart, exit 15:55, case B; R = net % / 1.5). Inputs: five stage-1 flags and eleven stage-2
inputs (see REGISTRY.md). Protocol: train 2019-2025; test 2011-06..2018 and 2026-01..09.
  A  univariate tables (training terciles), all eras
  B1 additive subsets of the 11 inputs (size 1-5, every threshold, with/without stage-1 score >= 2), chosen on
     training by mean R with >= 10 signals a year, then evaluated once on the test eras (top 10 also reported)
  B2 L2 logistic model of T1 on all inputs and flags, fitted on training
  B3 baselines: all signals; scaled move top tercile + gap agreement; the cascade's early rule
Writes analysis/strategies/trend_detector/.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
import trend_days as TD
from download_detector_data import FLOW_DIR, MEMBERS
from soxlab import data as sdata
from soxlab.research import common as C
from soxlab.research import engine as E
from soxlab.research import rules as R
from soxlab.research.rules import FLAT_OPEN

OUT = C.RESEARCH_DIR / "trend_detector"
START, END = "2011-03-23", "2026-09-25"
ERAS = {"test 2011-2018": ("2011-06-01", "2018-12-31"), "train 2019-2025": ("2019-01-02", "2025-12-31"),
        "test 2026": ("2026-01-02", "2026-09-25")}
TRAIN = "train 2019-2025"
TESTS = ["test 2011-2018", "test 2026"]
YEARS = {k: (pd.Timestamp(b) - pd.Timestamp(a)).days / 365.25 for k, (a, b) in ERAS.items()}
CHECKS = {"09:45": 14, "10:00": 29}
LEADERS = ["NVDA", "AVGO", "AMD", "TSM"]
STOP = 0.015
FLAGS = ["F1_vol_hot", "F2_yday_trend", "F3_qqq_below", "F4_big_gap", "F5_open_outside"]
INPUTS = ["I1_scaled_move", "I2_gap_agree", "I3_path_clean", "I4_vwap_side", "I5a_flow_tick", "I5b_flow_bar",
          "I6a_breadth", "I6b_leaders", "I7_vix", "I8_semis_vs_qqq", "I9_level"]
DISCRETE = {"I2_gap_agree", "I9_level"}


def light(ticker: str, dates: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray]:
    """Adjusted regular-session first open (within the first 5 minutes) and causally forward-filled closes of
    bars 0..29, for tickers stored without unadjusted bars."""
    df = sdata.load_minute_bars(ticker, True, START, END, rth_only=True)
    c = sdata._pivot(df, "c", dates)[:, :30]
    o = sdata._pivot(df, "o", dates)[:, :30]
    present = ~np.isnan(c)
    first = np.argmax(present, axis=1)
    has = present.any(axis=1) & (first <= 5)
    o0 = np.where(has, o[np.arange(len(dates)), first], np.nan)
    return o0, pd.DataFrame(c).ffill(axis=1).to_numpy()


def load_flow(dates: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    f = pd.concat([pd.read_parquet(p) for p in sorted(FLOW_DIR.glob("soxl_flow_*.parquet"))], ignore_index=True)
    di = dates.get_indexer(pd.to_datetime(f["date"]).dt.normalize())
    ok = di >= 0
    mi = f["minute"].to_numpy().astype(int)[ok]
    sd, dl = np.zeros((len(dates), 30)), np.zeros((len(dates), 30))
    np.add.at(sd, (di[ok], mi), f["signed_dollars"].to_numpy()[ok])
    np.add.at(dl, (di[ok], mi), f["dollars"].to_numpy()[ok])
    have = np.zeros(len(dates), bool)
    have[np.unique(di[ok])] = True
    return np.cumsum(sd, axis=1), np.cumsum(dl, axis=1), have


def era_of(dates: pd.Series) -> np.ndarray:
    out = np.full(len(dates), "", dtype=object)
    for k, (a, b) in ERAS.items():
        out[(dates >= a) & (dates <= b)] = k
    return out


def build(ctx) -> pd.DataFrame:
    dates = ctx.dates
    L, X, Q = ctx["SOXL"], ctx["SOXX"], ctx["QQQ"]
    p = L.p
    soxx_oc = X.last_c / X.o0 - 1
    med20 = R._prior_window_stat(L.range_pct, 20, np.median, 10)
    med250 = R._prior_window_stat(L.range_pct, 250, np.median, 100)
    gap = L.o0 / L.pc - 1
    pdh, pdl = C.shift1(L.hi), C.shift1(L.lo)
    with np.errstate(invalid="ignore"):
        flags = pd.DataFrame({"F1_vol_hot": med20 / med250 >= 1.2,
                              "F2_yday_trend": TD._lag(np.abs(soxx_oc), 1) >= 0.02,
                              "F3_qqq_below": np.nan_to_num(TD.qqq_above_ma50(dates), nan=1) < 0.5,
                              "F4_big_gap": np.abs(gap) / med20 >= 0.5,
                              "F5_open_outside": (L.o0 > pdh) | (L.o0 < pdl)}).astype(int)
    stage1 = flags.sum(axis=1).to_numpy()
    mem = {t: light(t, dates) for t in MEMBERS}
    vixy = light("VIXY", dates)
    csd, cdl, have_flow = load_flow(dates)
    vw = L.vwap
    cms = {"B": C.cost_model(C.COMMISSION_B)}
    frames = []
    for tname, b in CHECKS.items():
        cb = p.c[:, b]
        with np.errstate(all="ignore"):
            move = cb / L.o0 - 1
            s = np.sign(move)
            typ = R._prior_window_stat(np.abs(move), 20, np.median, 10)
            cpath = np.concatenate([L.o0[:, None], p.c[:, :b + 1]], axis=1)
            steps = np.diff(cpath, axis=1)
            path_clean = np.abs(cb - L.o0) / np.nansum(np.abs(steps), axis=1)
            vside = ((p.c[:, 5:b + 1] - vw[:, 5:b + 1]) * s[:, None] > 0).mean(axis=1)
            v = np.nan_to_num(p.v[:, :b + 1])
            flow_bar = (np.sign(np.nan_to_num(steps)) * v).sum(axis=1) / v.sum(axis=1) * s
            flow_tick = np.where(have_flow & (cdl[:, b] > 0), csd[:, b] / np.where(cdl[:, b] > 0, cdl[:, b], 1), np.nan) * s
            agree, valid = [], []
            for t in MEMBERS:
                o0m, cm = mem[t]
                mm = cm[:, b] / o0m - 1
                ok = np.isfinite(mm)
                agree.append(ok & (np.sign(mm) == s))
                valid.append(ok)
            A, V = np.array(agree), np.array(valid)
            nv = V.sum(axis=0)
            breadth = np.where(nv >= 10, A.sum(axis=0) / np.maximum(nv, 1), np.nan)
            li = [MEMBERS.index(t) for t in LEADERS]
            nl = V[li].sum(axis=0)
            leaders = np.where(nl >= 3, A[li].sum(axis=0) / np.maximum(nl, 1), np.nan)
            vix = -s * (vixy[1][:, b] / vixy[0] - 1) * 100
            semis_q = s * ((X.p.c[:, b] / X.o0 - 1) - (Q.p.c[:, b] / Q.o0 - 1)) * 100
            hmax, lmin = np.nanmax(p.h[:, :b + 1], axis=1), np.nanmin(p.l[:, :b + 1], axis=1)
            last5 = p.c[:, b - 4:b + 1]
            up_b, up_h = hmax > pdh, np.nanmin(last5, axis=1) > pdh
            dn_b, dn_h = lmin < pdl, np.nanmax(last5, axis=1) < pdl
            level = np.where(s > 0, np.where(up_b & up_h, 1, np.where(up_b & (cb <= pdh), -1, 0)),
                             np.where(dn_b & dn_h, 1, np.where(dn_b & (cb >= pdl), -1, 0)))
        df = pd.DataFrame({"date": dates, "check": tname, "d": np.arange(len(dates)), "s": s, "move_pct": move * 100,
                           "I1_scaled_move": np.abs(move) / typ, "I2_gap_agree": (np.sign(gap) == s).astype(int),
                           "I3_path_clean": path_clean, "I4_vwap_side": vside, "I5a_flow_tick": flow_tick,
                           "I5b_flow_bar": flow_bar, "I6a_breadth": breadth, "I6b_leaders": leaders, "I7_vix": vix,
                           "I8_semis_vs_qqq": semis_q, "I9_level": level, "stage1": stage1,
                           "T1": (soxx_oc * s >= 0.02).astype(int)})
        df = pd.concat([df, flags], axis=1)
        df["era"] = era_of(df["date"])
        df = df[(df["era"] != "") & (np.abs(df["move_pct"]) >= 1.0) & np.isfinite(df["move_pct"])].copy()
        it = []
        for d, sd_ in zip(df["d"].to_numpy(), df["s"].to_numpy()):
            flat = int(p.n_min[d]) - FLAT_OPEN
            if b + 1 < flat and np.isfinite(p.o[d, b + 1]):
                it.append({"d": int(d), "sig": b, "e": b + 1, "s": int(sd_), "tx": flat, "tx_kind": "open",
                           "stop": p.o[d, b + 1] * (1 - sd_ * STOP)})
        ex = E.add_costs(E.execute(E.simulate(L, E.make_intents(it)), ctx, mode="switch")[0], cms)
        r = pd.Series(ex["net_B"].to_numpy() / 100 / (STOP * 100), index=ex["d"].to_numpy().astype(int))
        df["R"] = r.reindex(df["d"]).to_numpy()
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def metrics(g: pd.DataFrame, era: str) -> dict:
    x = g["R"].dropna()
    return {"signals": len(g), "trades": len(x), "trades_per_year": len(x) / YEARS[era],
            "trend_share": g["T1"].mean() if len(g) else np.nan, "win": (x > 0).mean() if len(x) else np.nan,
            "mean_R": x.mean() if len(x) else np.nan}


def univariate(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for chk, g in df.groupby("check"):
        tr = g[g["era"] == TRAIN]
        cols = INPUTS + ["stage1"]
        for c in cols:
            if c in DISCRETE:
                bucket = g[c].astype("Int64").astype(str)
            elif c == "stage1":
                bucket = pd.cut(g[c], [-1, 1, 2, 9], labels=["0-1", "2", "3+"]).astype(str)
            else:
                lo, hi = np.nanquantile(tr[c], [1 / 3, 2 / 3])
                bucket = pd.Series(np.where(g[c].isna(), "n/a", np.where(g[c] >= hi, "high", np.where(g[c] >= lo, "mid", "low"))),
                                   index=g.index)
            for (b, era), gg in g.groupby([bucket, g["era"]]):
                rows.append({"check": chk, "input": c, "bucket": b, "era": era, **metrics(gg, era)})
    return pd.DataFrame(rows)


def favorable(g: pd.DataFrame, tr: pd.DataFrame) -> np.ndarray:
    cols = []
    for c in INPUTS:
        if c == "I2_gap_agree":
            cols.append(g[c].to_numpy() == 1)
        elif c == "I9_level":
            cols.append(g[c].to_numpy() == 1)
        else:
            thr = np.nanquantile(tr[c], 2 / 3)
            cols.append(np.nan_to_num(g[c].to_numpy(), nan=-np.inf) >= thr)
    return np.column_stack(cols).astype(np.int8)


def era_metrics(g: pd.DataFrame, sel: np.ndarray, prefix: str = "") -> dict:
    out = {}
    for era in ERAS:
        m = metrics(g[sel & (g["era"] == era).to_numpy()], era)
        out.update({f"{prefix}{era} {k}": v for k, v in m.items() if k in ("trades_per_year", "trend_share", "mean_R")})
    return out


def search(g: pd.DataFrame) -> pd.DataFrame:
    tr_mask = (g["era"] == TRAIN).to_numpy()
    fav = favorable(g, g[tr_mask])
    st1 = g["stage1"].to_numpy() >= 2
    Rv = g["R"].to_numpy()
    valid = np.isfinite(Rv)
    rows = []
    for k in range(1, 6):
        for S in itertools.combinations(range(len(INPUTS)), k):
            score = fav[:, S].sum(axis=1)
            for thr in range(1, k + 1):
                for req in (False, True):
                    sel = (score >= thr) & (st1 if req else True)
                    m = sel & tr_mask & valid
                    if m.sum() / YEARS[TRAIN] < 10:
                        continue
                    rows.append({"inputs": "+".join(INPUTS[i].split("_")[0] for i in S), "k": k, "min_count": thr,
                                 "stage1_ge2": req, "train_trades_per_year": m.sum() / YEARS[TRAIN],
                                 "train_mean_R": Rv[m].mean(), "_S": S})
    res = pd.DataFrame(rows)
    res["_R"] = res["train_mean_R"].round(6)                       # ties: prefer fewer inputs, then more trades
    res = res.sort_values(["_R", "k", "train_trades_per_year"], ascending=[False, True, False]).drop(columns="_R")
    res = res.reset_index(drop=True)
    top = res.head(10).copy()
    for i, row in top.iterrows():
        score = fav[:, list(row["_S"])].sum(axis=1)
        sel = (score >= row["min_count"]) & (st1 if row["stage1_ge2"] else True)
        for k, v in era_metrics(g, sel).items():
            top.loc[i, k] = v
    return top.drop(columns="_S"), len(res)


def logistic(g: pd.DataFrame) -> tuple[dict, np.ndarray]:
    feats = INPUTS + FLAGS
    tr = g[g["era"] == TRAIN]
    mu, sd = tr[feats].mean(), tr[feats].std().replace(0, 1)
    Z = lambda d: ((d[feats] - mu) / sd).fillna(0).clip(-5, 5).to_numpy()            # noqa: E731
    Xtr = np.column_stack([np.ones(len(tr)), Z(tr)])
    w = TD._logit_l2(Xtr, tr["T1"].to_numpy(), 10.0)
    prob = 1 / (1 + np.exp(-(w[0] + Z(g) @ w[1:])))
    cut = np.quantile(prob[(g["era"] == TRAIN).to_numpy()], 2 / 3)
    out = {"weights": dict(zip(feats, np.round(w[1:], 3)))}
    for era in ERAS:
        m = (g["era"] == era).to_numpy()
        out[f"{era} AUC"] = TD._auc(prob[m], g["T1"].to_numpy()[m])
    return out, prob >= cut


def baselines(g: pd.DataFrame, chk: str) -> dict[str, np.ndarray]:
    tr = g[g["era"] == TRAIN]
    hi = np.nanquantile(tr["I1_scaled_move"], 2 / 3)
    mv = np.abs(g["move_pct"].to_numpy())
    lo_b, hi_b = (2, 3) if chk == "09:45" else (3, 4)
    return {"all signals (>= 1%)": np.ones(len(g), bool),
            "move + gap (I1 top tercile & I2)": (g["I1_scaled_move"].to_numpy() >= hi) & (g["I2_gap_agree"].to_numpy() == 1),
            f"cascade rule ({lo_b}-{hi_b}% with the gap)": (mv >= lo_b) & (mv < hi_b) & (g["I2_gap_agree"].to_numpy() == 1)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context(start=START, end=END)
    df = build(ctx)
    df.to_parquet(ROOT / "data" / "research" / "trend_detector_signals.parquet", index=False)
    uni = univariate(df)
    uni.to_csv(OUT / "univariate.csv", index=False, float_format="%.4f")
    summary, tops, logit = [], [], []
    for chk, g in df.groupby("check"):
        g = g.reset_index(drop=True)
        top, n_rules = search(g)
        top.insert(0, "check", chk)
        tops.append(top)
        best = top.iloc[0]
        S = [INPUTS.index(next(c for c in INPUTS if c.split("_")[0] == tok)) for tok in best["inputs"].split("+")]
        fav = favorable(g, g[g["era"] == TRAIN])
        sel_b1 = (fav[:, S].sum(axis=1) >= best["min_count"]) & ((g["stage1"].to_numpy() >= 2) if best["stage1_ge2"] else True)
        lg, sel_b2 = logistic(g)
        logit.append({"check": chk, **{k: v for k, v in lg.items() if k != "weights"}, **lg["weights"]})
        rules = {**baselines(g, chk), f"B1 selected: {best['inputs']} >= {best['min_count']}"
                 f"{' & stage1>=2' if best['stage1_ge2'] else ''} (best of {n_rules})": sel_b1,
                 "B2 logistic, top third": sel_b2}
        for name, sel in rules.items():
            summary.append({"check": chk, "rule": name, **era_metrics(g, sel)})
    summary, tops, logit = pd.DataFrame(summary), pd.concat(tops, ignore_index=True), pd.DataFrame(logit)
    summary.to_csv(OUT / "summary.csv", index=False, float_format="%.4f")
    tops.to_csv(OUT / "search_top10.csv", index=False, float_format="%.4f")
    logit.to_csv(OUT / "logistic.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 300)
    pd.set_option("display.max_columns", 40)
    show = [c for c in summary.columns if "mean_R" in c or "trend_share" in c or "trades_per_year" in c]
    print(summary[["check", "rule"] + show].round(2).to_string(index=False))
    print("\n" + tops.drop(columns=[c for c in tops.columns if "trades_per_year" in c and "train" not in c]).round(2).to_string(index=False))
    print("\n" + logit.round(3).to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
