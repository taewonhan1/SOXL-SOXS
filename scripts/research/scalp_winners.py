#!/usr/bin/env python3
"""Exploratory (not pre-registered): which entry-time data elements separate winning from losing trades in
Studies 10-12 (Hitchhiker-, Bone Zone- and flag-like 1-minute scalps).

* Trades: per family, the registered single-exit variant with the most trades (primary) and the same rule
  with the other entry type (replication), as traded (one position at a time); outcome = case-B net bps.
* Features: ``soxlab.features.compute_features`` (the look-ahead-tested data elements) sampled at the last
  completed bar before the entry bar, plus setup geometry recomputed from the bars (impulse size, pause
  length, giveback, volume dry-up, stop distance) and trade context (side, trade number, event day).
  Directional features are signed so that + means "in the trade's direction".
* A relationship counts only if it has the same sign in all three periods (pre 2019-21, dev 2022-24,
  val 2024-10..2025-12) and survives Benjamini-Hochberg across every feature x variant test.
* Out-of-sample check: an L2 logistic model of "trade wins" and a ridge model of net bps, fitted on dev only
  (penalty picked on dev's last third), scored on pre and val.

2019-01-02 .. 2025-12-31 only; the 2026 holdout stays sealed. Writes analysis/strategies/scalps_winners/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, stats

from runlib import ROOT  # noqa: I001
from soxlab import features as sfeat
from soxlab.research import common as C
from soxlab.research import rules as R

OUT = C.RESEARCH_DIR / "scalps_winners"
LAST_DAY = "2025-12-31"
VARIANTS = [  # (family, variant, study dir, generator, params) -- primary first within each family
    ("HH", "S10-09", "study10_hitchhiker", R.s10_hh_intents, dict(window_end=59, entry="stop", exit_="X2R")),
    ("HH", "S10-11", "study10_hitchhiker", R.s10_hh_intents, dict(window_end=59, entry="close", exit_="X2R")),
    ("BZ", "S11-01", "study11_bone_zone", R.s11_bz_intents, dict(entry="close", exit_="XT")),
    ("BZ", "S11-04", "study11_bone_zone", R.s11_bz_intents, dict(entry="stop", exit_="XT")),
    ("Flag", "S12-01", "study12_flags", R.s12_flag_intents, dict(entry="stop", exit_="XM")),
    ("Flag", "S12-04", "study12_flags", R.s12_flag_intents, dict(entry="close", exit_="XM")),
]
DIRECTIONAL = ["ret_1m", "ret_5m", "ret_15m", "ret_30m", "ret_60m", "ret_since_open", "ret_since_prev_close",
               "gap", "gap_atr", "pm_ret", "dist_vwap_bps", "dist_vwap_sd", "ema_diff_1m_bps", "ema_diff_5m_bps",
               "SOXX_ret_5m", "SOXX_ret_since_prev_close", "NVDA_ret_5m", "NVDA_ret_since_prev_close",
               "QQQ_ret_5m", "QQQ_ret_since_prev_close", "tracking_gap_bps"]
NONDIR = ["atr14_1m_bps", "rv_30m", "atr14_d_pct", "rv20_d_ann", "rvol_tod", "rvol_1m", "cumvol_share",
          "vwap_cross_count", "minute_of_session", "dow", "soxl_soxs_div_bps"]
SETUP = ["R_bps", "impulse_z", "impulse_bars", "pause_bars", "giveback", "vol_ratio"]
EXTRA = ["beyond_pd_extreme_bps", "range_so_far_atr", "dist_from_day_extreme_atr", "is_bull", "trade_no",
         "event_day"]


# ------------------------------------------------------------------ feature assembly
def data_elements(ctx) -> dict:
    tks = ["SOXL", "SOXS", "SOXX", "NVDA", "QQQ", "SMH"]
    panels = {t: ctx[t].p for t in tks}
    official = {t: pd.Series(ctx[t].off, index=ctx.dates) for t in tks}
    F = sfeat.compute_features("SOXL", panels, official, {"SOXL": ctx["SOXL"].premarket}, ctx.cal)
    p = ctx["SOXL"].p
    hmax, lmin = np.fmax.accumulate(p.h, axis=1), np.fmin.accumulate(p.l, axis=1)
    F["_hmax"], F["_lmin"] = hmax, lmin
    return F


def setup_geometry(fam: str, td, sig_o, stod, d: int, t: int, s: int) -> dict:
    """Recompute the setup's shape at trigger bar t (same definitions as the registered generators)."""
    h, l, v, O = td.p.h[d], td.p.l[d], np.nan_to_num(td.p.v[d]), td.o0[d]
    if fam == "HH":
        pk = int(np.nanargmax(h[:t]) if s > 0 else np.nanargmin(l[:t]))
        ext = h[pk] if s > 0 else l[pk]
        drive = s * (ext / O - 1)
        box = np.nanmin(l[pk + 1:t]) if s > 0 else np.nanmax(h[pk + 1:t])
        return {"impulse_z": drive / sig_o[d], "impulse_bars": pk + 1, "pause_bars": t - 1 - pk,
                "giveback": s * (ext - box) / (s * (ext - O)), "vol_ratio": v[pk + 1:t].mean() / v[:pk + 1].mean()}
    W = 11 if fam == "BZ" else 13
    lo = max(0, t - W)
    pk = lo + int(np.nanargmax(h[lo:t]) if s > 0 else np.nanargmin(l[lo:t]))
    b0 = max(0, pk - 15)
    bi = b0 + int(np.nanargmin(l[b0:pk + 1]) if s > 0 else np.nanargmax(h[b0:pk + 1]))
    ext, bv = (h[pk], l[bi]) if s > 0 else (l[pk], h[bi])
    nimp = max(pk - bi, 1)
    worst = np.nanmin(l[pk + 1:t]) if s > 0 else np.nanmax(h[pk + 1:t])
    return {"impulse_z": s * (ext - bv) / bv / (stod[d, pk] * np.sqrt(nimp)), "impulse_bars": pk - bi,
            "pause_bars": t - 1 - pk, "giveback": s * (ext - worst) / (s * (ext - bv)),
            "vol_ratio": v[pk + 1:t].mean() / v[bi:pk + 1].mean()}


def trade_table(ctx, F, fam, vid, study, fn, prm, events) -> pd.DataFrame:
    td = ctx["SOXL"]
    tr = pd.read_parquet(C.RESEARCH_DATA / "trades" / study / f"{vid}.parquet")
    tr = tr[tr["date"] <= LAST_DAY].copy()                                  # holdout excluded
    it = fn(ctx, **prm)
    tr = tr.merge(it[["d", "sig", "e", "s", "stop", "entry_px"]], on=["d", "sig", "e", "s"], how="left")
    d, e, s, t = (tr[c].to_numpy().astype(int) for c in ("d", "e", "s", "sig"))
    k = e - 1                                                               # last completed bar before entry
    ep_chart = np.where(np.isfinite(tr["entry_px"]), tr["entry_px"], td.p.o[d, e])
    out = pd.DataFrame({"family": fam, "variant": vid, "date": tr["date"].to_numpy(),
                        "period": C.period_of(tr["date"]), "net_B": tr["net_B"].to_numpy(),
                        "win": (tr["net_B"] > 0).to_numpy().astype(int)})
    for f in DIRECTIONAL:
        out[f] = s * F[f][d, k].astype(float)
    for f in NONDIR:
        out[f] = F[f][d, k].astype(float)
    atr = F["atr14_d"][d, k]
    cc = td.p.c[d, k]
    out["beyond_pd_extreme_bps"] = np.where(s > 0, F["dist_pd_high_bps"][d, k], -F["dist_pd_low_bps"][d, k])
    out["range_so_far_atr"] = (F["_hmax"][d, k] - F["_lmin"][d, k]) / atr
    out["dist_from_day_extreme_atr"] = np.where(s > 0, F["_hmax"][d, k] - cc, cc - F["_lmin"][d, k]) / atr
    out["is_bull"] = (s > 0).astype(float)
    out["trade_no"] = tr.groupby("date").cumcount().to_numpy() + 1.0
    out["event_day"] = events.reindex(pd.DatetimeIndex(tr["date"])).fillna(False).to_numpy().astype(float)
    out["R_bps"] = np.abs(ep_chart - tr["stop"].to_numpy()) / ep_chart * 1e4
    sig_o, stod = R.s2_sigma_open(td), R.sigma_tod(td)
    geo = [setup_geometry(fam, td, sig_o, stod, dd, tt, ss) for dd, tt, ss in zip(d, t, s)]
    for f in SETUP[1:]:
        out[f] = [g[f] for g in geo]
    return out.replace([np.inf, -np.inf], np.nan)


# ------------------------------------------------------------------ statistics
def cluster_slope(x: np.ndarray, y: np.ndarray, g: np.ndarray) -> tuple[float, float, int]:
    """OLS slope of y on x with a day-clustered standard error: (slope, t, clusters)."""
    X = np.column_stack([np.ones_like(x), x])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    S = pd.DataFrame({"g": g, "a": e, "b": x * e}).groupby("g")[["a", "b"]].sum().to_numpy()
    G = len(S)
    V = XtXi @ (S.T @ S) @ XtXi * G / (G - 1)
    return float(b[1]), float(b[1] / np.sqrt(V[1, 1])), G


def univariate(tt: pd.DataFrame, feats: list[str]) -> pd.DataFrame:
    rows = []
    for (fam, vid), g in tt.groupby(["family", "variant"], sort=False):
        for f in feats:
            if g[f].nunique() < 3:
                continue
            r = {"family": fam, "variant": vid, "feature": f}
            xs, ys, gs = [], [], []
            for per in ("pre", "dev", "val"):
                h = g[(g["period"] == per) & g[f].notna()]
                r[f"rho_{per}"] = stats.spearmanr(h[f], h["net_B"]).statistic if len(h) > 10 else np.nan
                rk = h[f].rank(pct=True, method="average").to_numpy()
                ter = np.minimum((rk * 3).astype(int), 2) if f not in ("is_bull", "event_day") else \
                    np.where(h[f].to_numpy() > 0, 2, 0)
                for q, nm in ((0, "low"), (2, "high")):
                    m = ter == q
                    r[f"{nm}_third_net_{per}"] = h["net_B"].to_numpy()[m].mean() if m.any() else np.nan
                    r[f"{nm}_third_win_{per}"] = h["win"].to_numpy()[m].mean() if m.any() else np.nan
                xs.append(rk)
                ys.append(h["net_B"].to_numpy())
                gs.append(h["date"].astype(str).to_numpy())
            b, t, G = cluster_slope(np.concatenate(xs), np.concatenate(ys), np.concatenate(gs))
            r["slope_bps_low_to_high"], r["t_pooled"] = b, t
            r["p_pooled"] = float(2 * stats.t.sf(abs(t), df=max(1, G - 1)))
            sg = np.sign([r["rho_pre"], r["rho_dev"], r["rho_val"]])
            r["same_sign_all_periods"] = bool(np.all(sg == np.sign(b)) and b != 0)
            r["high_third_positive_all_periods"] = bool(all(r[f"high_third_net_{p}"] > 0 for p in ("pre", "dev", "val")))
            r["low_third_positive_all_periods"] = bool(all(r[f"low_third_net_{p}"] > 0 for p in ("pre", "dev", "val")))
            rows.append(r)
    u = pd.DataFrame(rows)
    u["q_bh"] = C.bh_qvalues(u["p_pooled"].fillna(1).to_numpy())
    u["holds_up"] = u["same_sign_all_periods"] & (u["q_bh"] <= 0.10)
    return u


def _auc(score: np.ndarray, y: np.ndarray) -> float:
    pos, neg = score[y == 1], score[y == 0]
    if not len(pos) or not len(neg):
        return np.nan
    return float(stats.mannwhitneyu(pos, neg).statistic / (len(pos) * len(neg)))


def _logit_l2(X: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    def f(w):
        z = X @ w
        ll = np.sum(y * z - np.logaddexp(0, z))
        return -ll + lam / 2 * np.sum(w[1:] ** 2)

    def gr(w):
        pr = 1 / (1 + np.exp(-(X @ w)))
        gg = -(X.T @ (y - pr))
        gg[1:] += lam * w[1:]
        return gg
    return optimize.minimize(f, np.zeros(X.shape[1]), jac=gr, method="L-BFGS-B").x


def _ridge(X: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    P = np.eye(X.shape[1]) * lam
    P[0, 0] = 0
    return np.linalg.solve(X.T @ X + P, X.T @ y)


def oos_models(tt: pd.DataFrame, feats: list[str]) -> pd.DataFrame:
    rows = []
    for (fam, vid), g in tt.groupby(["family", "variant"], sort=False):
        dev = g[g["period"] == "dev"].sort_values("date")
        use = [f for f in feats if dev[f].notna().mean() > 0.8 and dev[f].std() > 0]
        mu, sd = dev[use].mean(), dev[use].std()

        def mat(h):
            return np.column_stack([np.ones(len(h)), ((h[use] - mu) / sd).fillna(0).clip(-5, 5).to_numpy()])
        Xd, yw, yn = mat(dev), dev["win"].to_numpy(), dev["net_B"].to_numpy()
        cut = int(len(dev) * 2 / 3)                                     # penalty chosen on dev's last third
        best = {}
        for kind in ("logit_win", "ridge_net"):
            sc = {}
            for lam in (1.0, 10.0, 100.0, 1000.0):
                if kind == "logit_win":
                    w = _logit_l2(Xd[:cut], yw[:cut], lam)
                    sc[lam] = _auc(Xd[cut:] @ w, yw[cut:])
                else:
                    w = _ridge(Xd[:cut], yn[:cut], lam)
                    sc[lam] = stats.spearmanr(Xd[cut:] @ w, yn[cut:]).statistic
            best[kind] = max(sc, key=lambda k: np.nan_to_num(sc[k], nan=-9))
        for kind, lam in best.items():
            w = _logit_l2(Xd, yw, lam) if kind == "logit_win" else _ridge(Xd, yn, lam)
            r = {"family": fam, "variant": vid, "model": kind, "penalty": lam, "n_features": len(use)}
            for per in ("pre", "val"):
                h = g[g["period"] == per]
                score = mat(h) @ w
                top = score >= np.quantile(score, 0.7)
                r[f"auc_win_{per}"] = _auc(score, h["win"].to_numpy())
                r[f"rank_corr_net_{per}"] = stats.spearmanr(score, h["net_B"]).statistic
                r[f"all_mean_net_{per}"] = h["net_B"].mean()
                r[f"top30_mean_net_{per}"] = h["net_B"].to_numpy()[top].mean()
                r[f"top30_n_{per}"] = int(top.sum())
            coef = pd.Series(w[1:], index=use)
            r["largest_weights"] = ", ".join(f"{k} {v:+.2f}" for k, v in coef.reindex(
                coef.abs().sort_values(ascending=False).index[:5]).items())
            rows.append(r)
    return pd.DataFrame(rows)


def gap_alignment(ctx) -> pd.DataFrame:
    """Every Study 10-12 variant split by whether the trade goes with the opening gap (s * gap > 0)."""
    L = ctx["SOXL"]
    gap = L.o0 / L.pc - 1
    rows = []
    for st, pre in (("study10_hitchhiker", "S10"), ("study11_bone_zone", "S11"), ("study12_flags", "S12")):
        for f in sorted((C.RESEARCH_DATA / "trades" / st).glob(f"{pre}-*.parquet")):
            if "skipped" in f.stem:
                continue
            tr = pd.read_parquet(f)
            tr = tr[tr["date"] <= LAST_DAY].copy()
            tr["period"] = C.period_of(tr["date"])
            tr["group"] = np.where(tr["s"].to_numpy() * gap[tr["d"].to_numpy().astype(int)] > 0,
                                   "with_gap", "against_gap")
            for (grp, per), g in list(tr.groupby(["group", "period"])) + \
                    [((grp, "all"), g) for grp, g in tr.groupby("group")]:
                mu, t, _ = C.cluster_t(g["net_B"].to_numpy(), g["date"].to_numpy())
                rows.append({"variant": f.stem, "group": grp, "period": per, "n": len(g), "mean_net_B": mu, "t": t,
                             "win_rate": float((g["net_B"] > 0).mean())})
    return pd.DataFrame(rows)


def gap_size_buckets(ctx) -> pd.DataFrame:
    """Hitchhiker-like variants by the size of the opening gap in the trade's direction (% of the prior
    close; buckets fixed at round numbers around SOXL's median |gap| of ~2%)."""
    L = ctx["SOXL"]
    gap = (L.o0 / L.pc - 1) * 100
    edges, labels = [-np.inf, -1, 0, 1, 3, np.inf], ["against >1%", "against 0-1%", "with 0-1%", "with 1-3%", "with >3%"]
    rows = []
    for f in sorted((C.RESEARCH_DATA / "trades" / "study10_hitchhiker").glob("S10-*.parquet")):
        if "skipped" in f.stem:
            continue
        tr = pd.read_parquet(f)
        tr = tr[tr["date"] <= LAST_DAY].copy()
        tr["period"] = C.period_of(tr["date"])
        tr["bucket"] = pd.cut(tr["s"].to_numpy() * gap[tr["d"].to_numpy().astype(int)], edges, labels=labels)
        for b, g0 in tr.groupby("bucket", observed=True):
            for per, g in [(p, g0[g0["period"] == p]) for p in ("pre", "dev", "val")] + [("all", g0)]:
                mu, t, _ = C.cluster_t(g["net_B"].to_numpy(), g["date"].to_numpy()) if len(g) else (np.nan, np.nan, 0)
                rows.append({"variant": f.stem, "gap_in_trade_direction": b, "period": per, "n": len(g),
                             "mean_net_B": mu, "t": t, "win_rate": float((g["net_B"] > 0).mean()) if len(g) else np.nan})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = C.Context()
    F = data_elements(ctx)
    ev = pd.read_csv(C.RESEARCH_DIR / "output" / "event_calendar.csv", parse_dates=["date"]).set_index("date")["g3_any"]
    tt = pd.concat([trade_table(ctx, F, *v, ev) for v in VARIANTS], ignore_index=True)
    feats = DIRECTIONAL + NONDIR + SETUP + EXTRA
    uni = univariate(tt, feats)
    oos = oos_models(tt, feats)
    wins = tt.groupby(["family", "variant", "period"])["net_B"].agg(
        trades="size", win_rate=lambda x: (x > 0).mean(), mean_win=lambda x: x[x > 0].mean(),
        mean_loss=lambda x: x[x <= 0].mean(), best_trade="max").reset_index()
    uni.to_csv(OUT / "univariate.csv", index=False, float_format="%.4f")
    oos.to_csv(OUT / "oos_models.csv", index=False, float_format="%.4f")
    wins.to_csv(OUT / "winners_losers.csv", index=False, float_format="%.4f")
    gal = gap_alignment(ctx)
    gal.to_csv(OUT / "gap_alignment.csv", index=False, float_format="%.4f")
    gsz = gap_size_buckets(ctx)
    gsz.to_csv(OUT / "gap_size_buckets.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("== winners and losers\n" + wins.round(2).to_string(index=False))
    show = ["family", "variant", "feature", "rho_pre", "rho_dev", "rho_val", "slope_bps_low_to_high", "t_pooled",
            "q_bh", "low_third_net_pre", "high_third_net_pre", "low_third_net_dev", "high_third_net_dev",
            "low_third_net_val", "high_third_net_val"]
    print("\n== relationships that hold up (same sign in all periods, BH q <= 0.10)\n" +
          uni[uni["holds_up"]].sort_values(["family", "t_pooled"])[show].round(2).to_string(index=False))
    pos = uni[uni["high_third_positive_all_periods"] | uni["low_third_positive_all_periods"]]
    print("\n== thirds that are net positive in all three periods\n" +
          (pos[show].round(2).to_string(index=False) if len(pos) else "none"))
    print("\n== out-of-sample models (fitted on dev only)\n" + oos.round(3).to_string(index=False))
    print("\n== with vs against the opening gap (mean net bps per trade)\n" +
          gal.pivot_table(index=["variant", "group"], columns="period", values="mean_net_B").round(1).to_string())
    print("\n== Hitchhiker-like: gap size in the trade's direction (mean net bps, all periods)\n" +
          gsz[gsz["period"] == "all"].pivot_table(index="variant", columns="gap_in_trade_direction",
                                                  values="mean_net_B", observed=True).round(1).to_string())
    print(f"\ntests: {len(uni)} | hold up: {int(uni['holds_up'].sum())} | wrote {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
