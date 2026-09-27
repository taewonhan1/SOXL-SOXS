#!/usr/bin/env python3
"""Behavior-probe battery for SOXL / SOXS on 1-minute bars (next-bar-open execution, full cost model).

Periods (fixed a priori): in-sample 2022-01-01 -> 2024-09-30, out-of-sample 2024-10-01 -> 2026-09-25,
plus calendar years 2019-2026 (2019-2021 are pre-sample years, never used for selection).
Canonical parameters are fixed in soxlab/strategies.PROBES; the small grids are used only for the
in-sample selection demo and the rolling walk-forward. Nothing is tuned on the out-of-sample period.

Modes
-----
  SOXL L/S   signals from SOXL's own bars, long or short SOXL
  SOXS L/S   signals from SOXS's own bars, long or short SOXS
  switch     signals from SOXL's bars; bullish -> long SOXL, bearish -> long SOXS (no shorting)

Outputs (analysis/backtests/output/)
------------------------------------
  battery_summary.csv            probe x mode x period x side, gross and net metrics
  battery_yearly.csv             probe x mode x year (side = all)
  battery_is_selected_oos.csv    grid member selected on IS net Sharpe and its OOS result
  battery_walkforward.csv        rolling 24m-train / 6m-test walk-forward (stitched test results)
  battery_random_baseline.csv    random-entry baseline (matched day, holding time, side) percentiles
  battery_timing_diagnostics.csv lag -1 (look-ahead, NOT tradable) / 0 / +1 bar and day-shuffled signals
  battery_multiple_testing.csv   OOS daily t-stats, p-values, Benjamini-Hochberg q-values
  leadlag_xcorr.csv              1-min cross-correlations ETF vs drivers at lags -3..+3
  battery_run_info.json          provenance (cost file, hash, cost assumptions, run time)
  battery_is_vs_oos.png, battery_equity_curves.png, leadlag_xcorr.png
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soxlab import backtest as bt  # noqa: E402
from soxlab import config, pipeline  # noqa: E402
from soxlab import strategies as st  # noqa: E402
from soxlab.costs import CostModel  # noqa: E402

OUT = config.OUTPUT_DIR
PERIODS = {"IS": (config.IS_START, config.IS_END), "OOS": (config.OOS_START, config.OOS_END)}
YEARS = list(range(2019, 2027))
MODES = ["SOXL L/S", "SOXS L/S", "switch"]


def days_between(cal_idx, a, b):
    return cal_idx[(cal_idx >= pd.Timestamp(a)) & (cal_idx <= pd.Timestamp(b))]


def run_mode(probe: str, mode: str, ctx: dict, cm: CostModel, params: dict | None = None,
             transform=None) -> pd.DataFrame:
    """Simulate one probe in one mode. ``transform(ss, p)`` may alter the SignalSet (diagnostics)."""
    P, F = ctx["panels"], ctx["features"]
    if mode in ("SOXL L/S", "SOXS L/S"):
        T = mode.split()[0]
        p = P[T]
        ss = st.make_signals(probe, F[T], p, lev_sign=np.sign(config.LEVERAGE[T]), params=params)
        tp_bps = None
        if transform is not None:
            ss, tp_bps = transform(ss, p)
        tr = bt.simulate(p, ss.entries, ss.rules, stop_px=ss.stop_px, tp_px=ss.tp_px, stop_bps_arr=ss.stop_bps_arr,
                         tp_bps_arr=tp_bps, exit_long=ss.exit_long, exit_short=ss.exit_short, cost_model=cm, ticker=T)
        tr["mode"] = mode
        return tr
    # switch: SOXL-derived signal; bullish -> long SOXL, bearish -> long SOXS
    pL, pS = P["SOXL"], P["SOXS"]
    ss = st.make_signals(probe, F["SOXL"], pL, lev_sign=1.0, params=params)
    rel, tp_bps = st.to_relative(ss, pL)
    if transform is not None:
        rel, tp_bps2 = transform(rel, pL)
        tp_bps = tp_bps2 if tp_bps2 is not None else tp_bps
    E = rel.entries
    legs = []
    for p, T, ent, ex in ((pL, "SOXL", (E > 0).astype(np.int8), rel.exit_long),
                          (pS, "SOXS", (E < 0).astype(np.int8), rel.exit_short)):
        tr = bt.simulate(p, ent, rel.rules, stop_bps_arr=rel.stop_bps_arr, tp_bps_arr=tp_bps, exit_long=ex,
                         cost_model=cm, ticker=T)
        legs.append(tr)
    tr = pd.concat(legs, ignore_index=True).sort_values(["date", "entry_bar"]).reset_index(drop=True)
    tr["mode"] = mode
    return tr


def summarize(tr: pd.DataFrame, days, sess_min, extra: dict) -> dict:
    m = bt.metrics(tr, days, sess_min)
    t = tr[tr["date"].isin(days)]
    if len(t):
        m["avg_net_bps_zero_commission"] = float((t["net_bps"] + t["cost_comm_bps"]).mean())
        m["avg_spread_cost_bps"] = float(t["cost_spread_bps"].mean())
    return {**extra, **m}


def sess_minutes(ctx, mode, days):
    T = "SOXL" if mode in ("SOXL L/S", "switch") else "SOXS"
    return bt.session_minutes(ctx["panels"][T], days)


# ------------------------------------------------------------------------------------------------
def lead_lag_xcorr(ctx: dict) -> pd.DataFrame:
    P = ctx["panels"]
    rows = []
    for per, (a, b) in PERIODS.items():
        for T in config.TRADED:
            pt = P[T]
            m = (pt.dates >= pd.Timestamp(a)) & (pt.dates <= pd.Timestamp(b))
            rt = np.log(pt.c[m][:, 1:] / pt.c[m][:, :-1])
            okt = pt.present[m][:, 1:] & pt.present[m][:, :-1]
            for D in ("NVDA", "SOXX", "QQQ", "SMH"):
                pdd = P[D]
                rd = np.log(pdd.c[m][:, 1:] / pdd.c[m][:, :-1])
                okd = pdd.present[m][:, 1:] & pdd.present[m][:, :-1]
                for k in range(-3, 4):
                    # corr(r_T[t], r_D[t-k]); k > 0 means the driver LEADS by k minutes
                    if k > 0:
                        x, y, ok = rt[:, k:], rd[:, :-k], okt[:, k:] & okd[:, :-k]
                    elif k < 0:
                        x, y, ok = rt[:, :k], rd[:, -k:], okt[:, :k] & okd[:, -k:]
                    else:
                        x, y, ok = rt, rd, okt & okd
                    xv, yv = x[ok], y[ok]
                    good = np.isfinite(xv) & np.isfinite(yv)
                    xv, yv = xv[good], yv[good]
                    rows.append({"period": per, "etf": T, "driver": D, "lag_driver_leads_min": k,
                                 "corr": float(np.corrcoef(xv, yv)[0, 1]), "n_minutes": int(len(xv)),
                                 "beta_etf_on_driver": float(np.polyfit(yv, xv, 1)[0])})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------
def charts(summary: pd.DataFrame, curves: dict, xc: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
    S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
    LIGHT, DARK = "#86b6ef", "#1c5cab"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.facecolor": SURF, "figure.facecolor": SURF,
                         "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                         "axes.spines.right": False})
    # 1. IS -> OOS dumbbell of average net bps per trade (canonical, side = all)
    probes = list(st.PROBES)
    fig, axes = plt.subplots(1, 3, figsize=(13, 6.2), sharey=True)
    for ax, mode in zip(axes, MODES):
        s = summary[(summary["mode"] == mode) & (summary["side"] == "all") & (summary["variant"] == "canonical")]
        y = np.arange(len(probes))[::-1]
        for yi, pr in zip(y, probes):
            r = s[s["probe"] == pr].set_index("period")
            if not {"IS", "OOS"} <= set(r.index):
                continue
            a, b = r.loc["IS", "avg_net_bps"], r.loc["OOS", "avg_net_bps"]
            ax.plot([a, b], [yi, yi], color=AXIS, lw=1.5, zorder=1)
            ax.scatter([a], [yi], s=36, color=LIGHT, zorder=2, edgecolor=SURF, linewidth=1.5, label="IS 2022-01..2024-09" if yi == y[0] else None)
            ax.scatter([b], [yi], s=36, color=DARK, zorder=3, edgecolor=SURF, linewidth=1.5, label="OOS 2024-10..2026-09" if yi == y[0] else None)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_title(mode, color=INK, fontsize=10, loc="left")
        ax.set_xlabel("average net return per trade (bps)")
        ax.set_yticks(y)
        ax.set_yticklabels(probes)
        ax.grid(axis="y", visible=False)
    axes[0].legend(frameon=False, loc="lower left", fontsize=8)
    fig.suptitle("Behavior probes: average net bps per trade, in-sample vs out-of-sample (canonical parameters)",
                 x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "battery_is_vs_oos.png", dpi=110)
    plt.close(fig)
    # 2. equity curves small multiples
    n = len(probes)
    ncol = 4
    fig, axes = plt.subplots(int(np.ceil(n / ncol)), ncol, figsize=(14, 12), sharex=True)
    for ax, pr in zip(axes.flat, probes):
        for mode, col in (("SOXL L/S", S1), ("SOXS L/S", S2)):
            cv = curves.get((pr, mode))
            if cv is None:
                continue
            ax.plot(cv.index, cv.values, color=col, lw=1.3, label=mode)
            ax.annotate(f"{cv.values[-1]:+.0f}%", (cv.index[-1], cv.values[-1]), color=INK2, fontsize=7,
                        xytext=(2, 0), textcoords="offset points", va="center")
        ax.axvline(pd.Timestamp(config.OOS_START), color=INK2, lw=0.8)
        ax.axhline(0, color=AXIS, lw=0.8)
        ax.set_title(pr, color=INK, fontsize=9, loc="left")
        ax.tick_params(axis="x", labelrotation=0, labelsize=7)
    for ax in list(axes.flat)[n:]:
        ax.set_visible(False)
    axes.flat[0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.suptitle("Cumulative net P&L, % of a fixed notional (additive, 2022-01-03 -> 2026-09-25); vertical line = start of OOS",
                 x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "battery_equity_curves.png", dpi=100)
    plt.close(fig)
    # 3. lead-lag cross-correlation
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, per in zip(axes, ("IS", "OOS")):
        s = xc[(xc["period"] == per) & (xc["etf"] == "SOXL")]
        for D, col in (("NVDA", S1), ("SOXX", S2), ("QQQ", S3)):
            d = s[s["driver"] == D].sort_values("lag_driver_leads_min")
            ax.plot(d["lag_driver_leads_min"], d["corr"], color=col, lw=2, marker="o", ms=5, label=D)
            last = d[d["lag_driver_leads_min"] == 1]
            ax.annotate(f"{D} lag+1: {last['corr'].iloc[0]:.3f}", (1, last["corr"].iloc[0]), xytext=(8, 0),
                        textcoords="offset points", color=INK2, fontsize=7, va="center")
        ax.axhline(0, color=AXIS, lw=0.8)
        ax.set_title(f"SOXL 1-min return vs driver return k minutes earlier ({per})", color=INK, fontsize=9, loc="left")
        ax.set_xlabel("k (driver leads by k minutes; k < 0 = driver lags)")
    axes[0].set_ylabel("correlation")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "leadlag_xcorr.png", dpi=110)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = pipeline.load_context()
    cal_idx = ctx["cal"].index
    cm = CostModel.default()
    src = Path(cm.spread_source)
    info = {"run_started_utc": pd.Timestamp.now(tz="UTC").isoformat(), "spread_source": str(src),
            "spread_source_mtime_utc": pd.Timestamp(src.stat().st_mtime, unit="s", tz="UTC").isoformat() if src.exists() else None,
            "spread_source_sha256": hashlib.sha256(src.read_bytes()).hexdigest() if src.exists() else None,
            "spread_stat": cm.spread_stat, "commission_per_share": cm.commission_per_share, "notional_usd": cm.notional,
            "sec_fee_schedule": cm.sec_schedule, "finra_taf_schedule": cm.taf_schedule,
            "periods": PERIODS, "execution": "signal at bar close -> fill at next bar open; stop-first; flat by 15:55 ET"}
    print("cost model:", info["spread_source"])

    summary, yearly, curves, canon_trades = [], [], {}, {}
    for probe in st.PROBES:
        for mode in MODES:
            tr = run_mode(probe, mode, ctx, cm)
            canon_trades[(probe, mode)] = tr
            for per, (a, b) in PERIODS.items():
                days = days_between(cal_idx, a, b)
                sm = sess_minutes(ctx, mode, days)
                for side in ("all", "long", "short"):
                    t = tr if side == "all" else tr[tr["side"] == (1 if side == "long" else -1)]
                    if mode == "switch" and side != "all":
                        t = tr[tr["ticker"] == ("SOXL" if side == "long" else "SOXS")]
                    summary.append(summarize(t, days, sm, {"probe": probe, "family": st.PROBE_FAMILY[probe],
                                                           "mode": mode, "variant": "canonical", "period": per,
                                                           "side": side if mode != "switch" else
                                                           {"all": "all", "long": "long SOXL", "short": "long SOXS"}[side]}))
            for y in YEARS:
                days = cal_idx[cal_idx.year == y]
                yearly.append(summarize(tr, days, sess_minutes(ctx, mode, days),
                                        {"probe": probe, "mode": mode, "year": y,
                                         "sample": "pre-IS" if y < 2022 else ("IS" if y < 2024 else "IS/OOS split" if y == 2024 else "OOS")}))
            d22 = days_between(cal_idx, config.IS_START, config.OOS_END)
            if mode != "switch":
                daily = tr[tr["date"].isin(d22)].groupby("date")["net_bps"].sum().reindex(d22).fillna(0) / 100
                curves[(probe, mode)] = daily.cumsum()
        print(f"  {probe:16s} done  ({time.time() - t0:.0f}s)")
    summary = pd.DataFrame(summary)
    yearly = pd.DataFrame(yearly)

    # ---- in-sample selection on the grid + rolling walk-forward
    sel_rows, wf_rows = [], []
    windows = []
    start = pd.Timestamp("2020-01-01")
    while True:
        tr_a, tr_b = start, start + pd.DateOffset(months=24) - pd.Timedelta(days=1)
        te_a, te_b = tr_b + pd.Timedelta(days=1), tr_b + pd.DateOffset(months=6)
        if te_a > pd.Timestamp(config.OOS_END):
            break
        windows.append((tr_a, tr_b, te_a, min(te_b, pd.Timestamp(config.OOS_END))))
        start = start + pd.DateOffset(months=6)
    for probe, (gen, canon, grid) in st.PROBES.items():
        for mode in ("SOXL L/S", "SOXS L/S"):
            by_param = {json.dumps(g, sort_keys=True): run_mode(probe, mode, ctx, cm, params=g) for g in grid}
            is_days = days_between(cal_idx, *PERIODS["IS"])
            oos_days = days_between(cal_idx, *PERIODS["OOS"])
            best, best_v = None, -np.inf
            for lab, tr in by_param.items():
                m = bt.metrics(tr, is_days)
                if m["n_trades"] >= 30 and np.isfinite(m.get("sharpe_net", np.nan)) and m["sharpe_net"] > best_v:
                    best, best_v = lab, m["sharpe_net"]
            if best is not None:
                mo = bt.metrics(by_param[best], oos_days, sess_minutes(ctx, mode, oos_days))
                mi = bt.metrics(by_param[best], is_days, sess_minutes(ctx, mode, is_days))
                sel_rows.append({"probe": probe, "mode": mode, "grid_size": len(grid), "selected_params": best,
                                 "canonical_params": json.dumps(canon, sort_keys=True),
                                 **{f"IS_{k}": mi[k] for k in ("n_trades", "avg_gross_bps", "avg_net_bps", "sharpe_net")},
                                 **{f"OOS_{k}": mo[k] for k in ("n_trades", "avg_gross_bps", "avg_net_bps", "sharpe_net",
                                                               "profit_factor", "max_dd_net_pct", "t_stat_net")}})
            wf = bt.walk_forward(by_param, windows, cal_idx, select="sharpe_net", min_trades=20)
            if len(wf):
                parts = []
                for _, r in wf.iterrows():
                    tr = by_param[r["selected"]]
                    parts.append(tr[(tr["date"] >= r["test_start"]) & (tr["date"] <= r["test_end"])])
                stitched = pd.concat(parts)
                te_days = cal_idx[(cal_idx >= wf["test_start"].min()) & (cal_idx <= wf["test_end"].max())]
                ms = bt.metrics(stitched, te_days, sess_minutes(ctx, mode, te_days))
                wf_rows.append({"probe": probe, "mode": mode, "n_windows": len(wf),
                                "test_span": f"{wf['test_start'].min():%Y-%m-%d}..{wf['test_end'].max():%Y-%m-%d}",
                                "selections": "; ".join(f"{r['test_start']:%Y-%m}:{r['selected']}" for _, r in wf.iterrows()),
                                **{f"stitched_{k}": ms.get(k) for k in ("n_trades", "avg_gross_bps", "avg_net_bps",
                                                                         "sharpe_net", "t_stat_net", "max_dd_net_pct")}})
        print(f"  grid/WF {probe:16s} done  ({time.time() - t0:.0f}s)")
    sel = pd.DataFrame(sel_rows)
    wfd = pd.DataFrame(wf_rows)

    # ---- random-entry baseline
    rb_rows = []
    for (probe, mode), tr in canon_trades.items():
        if mode == "switch":
            continue
        T = mode.split()[0]
        p = ctx["panels"][T]
        ss = st.make_signals(probe, ctx["features"][T], p, lev_sign=np.sign(config.LEVERAGE[T]))
        for per, (a, b) in PERIODS.items():
            t = tr[(tr["date"] >= pd.Timestamp(a)) & (tr["date"] <= pd.Timestamp(b))]
            if len(t) < 10:
                continue
            rb = bt.random_entry_baseline(p, t, cm, n_iter=200, seed=hash((probe, mode, per)) % 2**32,
                                          earliest_entry_bar=ss.rules.earliest_entry_bar)
            strat = t["net_bps"].mean()
            rb_rows.append({"probe": probe, "mode": mode, "period": per, "n_trades": len(t),
                            "strategy_avg_net_bps": strat, "strategy_avg_gross_bps": t["gross_bps"].mean(),
                            "random_avg_net_bps_mean": rb["avg_net_bps"].mean(),
                            "random_avg_net_bps_p05": rb["avg_net_bps"].quantile(0.05),
                            "random_avg_net_bps_p95": rb["avg_net_bps"].quantile(0.95),
                            "random_avg_gross_bps_mean": rb["avg_gross_bps"].mean(),
                            "strategy_percentile_vs_random": float((rb["avg_net_bps"] < strat).mean() * 100)})
    rbd = pd.DataFrame(rb_rows)
    print(f"  random baselines done ({time.time() - t0:.0f}s)")

    # ---- timing diagnostics: lag -1 (look-ahead), 0, +1, day-shuffled
    diag = []
    d_all = days_between(cal_idx, config.IS_START, config.OOS_END)

    def lagger(k):
        def f(ss, p):
            rel, tp = st.to_relative(ss, p)
            sh = st.shift_signalset(rel, k)
            tp2 = None
            if tp is not None:
                tp2 = st.shift_signalset(st.SignalSet(np.zeros_like(rel.entries), rel.rules, stop_bps_arr=tp), k).stop_bps_arr
            return sh, tp2
        return f

    def shuffler(seed):
        def f(ss, p):
            rel, tp = st.to_relative(ss, p)
            perm = np.random.default_rng(seed).permutation(rel.entries.shape[0])
            pick = lambda a: None if a is None else a[perm]  # noqa: E731
            return st.SignalSet(pick(rel.entries), rel.rules, None, None, pick(rel.stop_bps_arr), pick(rel.exit_long),
                                pick(rel.exit_short)), pick(tp)
        return f

    for probe in st.PROBES:
        for mode in ("SOXL L/S", "SOXS L/S"):
            for lab, tf in (("lag-1 (look-ahead, not tradable)", lagger(-1)), ("lag 0 (harness default, relative stops)", lagger(0)),
                            ("lag+1 (one extra bar delay)", lagger(1)), ("day-shuffled signals", shuffler(1)),
                            ("day-shuffled signals (seed 2)", shuffler(2))):
                tr = run_mode(probe, mode, ctx, cm, transform=tf)
                m = bt.metrics(tr, d_all)
                diag.append({"probe": probe, "mode": mode, "variant": lab, "n_trades": m["n_trades"],
                             "avg_gross_bps": m.get("avg_gross_bps"), "avg_net_bps": m.get("avg_net_bps"),
                             "sharpe_gross": m.get("sharpe_gross"), "t_stat_gross": m.get("t_stat_gross")})
    diagd = pd.DataFrame(diag)
    print(f"  timing diagnostics done ({time.time() - t0:.0f}s)")

    # ---- multiple testing on canonical OOS results
    mt = summary[(summary["side"] == "all") & (summary["variant"] == "canonical")].copy()
    rows = []
    for per in ("IS", "OOS"):
        s = mt[mt["period"] == per].copy()
        s["p_value"] = 2 * (1 - stats.norm.cdf(np.abs(s["t_stat_net"].astype(float))))
        s = s.sort_values("p_value")
        m_ = s["p_value"].notna().sum()
        ranks = np.arange(1, len(s) + 1)
        q = (s["p_value"].to_numpy() * m_ / ranks)
        q = np.minimum.accumulate(q[::-1])[::-1]
        s["bh_q_value"] = np.minimum(q, 1.0)
        s["bonferroni_p"] = np.minimum(s["p_value"] * m_, 1.0)
        s["n_tests"] = m_
        rows.append(s[["probe", "mode", "period", "n_trades", "avg_net_bps", "sharpe_net", "t_stat_net", "p_value",
                       "bh_q_value", "bonferroni_p", "n_tests"]])
    mtd = pd.concat(rows)

    # ---- lead-lag cross-correlations
    xc = lead_lag_xcorr(ctx)

    # ---- write
    summary.to_csv(OUT / "battery_summary.csv", index=False, float_format="%.4f")
    yearly.to_csv(OUT / "battery_yearly.csv", index=False, float_format="%.4f")
    sel.to_csv(OUT / "battery_is_selected_oos.csv", index=False, float_format="%.4f")
    wfd.to_csv(OUT / "battery_walkforward.csv", index=False, float_format="%.4f")
    rbd.to_csv(OUT / "battery_random_baseline.csv", index=False, float_format="%.4f")
    diagd.to_csv(OUT / "battery_timing_diagnostics.csv", index=False, float_format="%.4f")
    mtd.to_csv(OUT / "battery_multiple_testing.csv", index=False, float_format="%.5f")
    xc.to_csv(OUT / "leadlag_xcorr.csv", index=False, float_format="%.5f")
    all_tr = pd.concat(canon_trades.values(), ignore_index=True)
    all_tr["probe"] = np.repeat([k[0] for k in canon_trades], [len(v) for v in canon_trades.values()])
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    all_tr.to_parquet(config.CACHE_DIR / "battery_trades_canonical.parquet", index=False)
    charts(summary, curves, xc)
    info["run_seconds"] = round(time.time() - t0, 1)
    info["n_summary_rows"] = len(summary)
    (OUT / "battery_run_info.json").write_text(json.dumps(info, indent=1, default=str))
    print(f"battery done in {time.time() - t0:.0f}s")
    view = summary[(summary["side"] == "all")][["probe", "mode", "period", "n_trades", "avg_gross_bps", "avg_net_bps",
                                                 "win_rate", "profit_factor", "sharpe_net", "max_dd_net_pct", "exposure"]]
    with pd.option_context("display.width", 220, "display.max_rows", 200):
        print(view.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
