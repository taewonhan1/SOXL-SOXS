"""Step 4: statistics from daily and 1-minute bars (Massive /v2/aggs), splits and ticker reference.

Outputs (analysis/microstructure/output/):
  price_levels.csv, splits.csv, activity_windows.csv, activity_yearly.csv, activity_monthly.csv,
  relative_tick_monthly.csv, minbar_tick_stats.csv, minbar_vol_by_bucket.csv, volume_profile_minute.csv,
  volume_session_split.csv, rth_trade_gaps_2024_2026.csv, and charts activity_trend.png (dollar volume,
  trades/day, relative tick), volume_profile.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from ms_common import DATA, ET, OUT, TICKERS, focus_lines, style_ax, trading_days_and_halfdays, FOCUS_COLORS, CONTEXT_GRAY, TEXT_SECONDARY  # noqa: E402

BARS = DATA / "bars"
REF = DATA / "ref"
END = "2026-09-25"
COLORS = {"SOXL": "#1f77b4", "SOXS": "#d62728", "SOXX": "#9467bd", "SMH": "#8c564b", "NVDA": "#2ca02c",
          "TQQQ": "#ff7f0e", "SQQQ": "#e377c2", "QQQ": "#7f7f7f", "SPY": "#17becf"}


def day_bars(T, adj):
    d = pd.read_parquet(BARS / f"{T}_day_{'adj' if adj else 'raw'}.parquet")
    d["dollar"] = d["v"] * d["vw"]
    return d.set_index("date")


def min_bars(T):
    m = pd.read_parquet(BARS / f"{T}_min_raw.parquet")
    et = pd.to_datetime(m["t"], unit="ms", utc=True).dt.tz_convert(ET)
    m["date"] = et.dt.strftime("%Y-%m-%d")
    m["minute"] = et.dt.hour * 60 + et.dt.minute
    return m


def main():
    tick = json.load(open(REF / "tickers.json"))
    splits = json.load(open(REF / "splits.json"))
    # ---------------- splits
    rows = []
    for T in TICKERS:
        for s in splits[T]:
            rows.append({"ticker": T, "execution_date": s["execution_date"], "split_from": s["split_from"],
                         "split_to": s["split_to"],
                         "type": "reverse" if s["split_to"] < s["split_from"] else "forward"})
    sp = pd.DataFrame(rows).sort_values(["ticker", "execution_date"])
    sp.to_csv(OUT / "splits.csv", index=False)

    # ---------------- price levels, activity
    pl, aw, ay, am, rt = [], [], [], [], []
    for T in TICKERS:
        raw = day_bars(T, False)
        adj = day_bars(T, True)
        last = raw.loc[END]
        l12 = raw.loc["2025-09-26":END]
        a12 = adj.loc["2025-09-26":END]
        pl.append({"ticker": T, "primary_exchange": tick[T].get("primary_exchange"), "round_lot": tick[T].get("round_lot"),
                   "close_unadj_2026_09_25": last["c"], "vwap_2026_09_25": last["vw"],
                   "rel_tick_bps_at_close": 1e4 * 0.01 / last["c"],
                   "min_close_unadj_12m": l12["c"].min(), "max_close_unadj_12m": l12["c"].max(),
                   "min_close_adj_12m": a12["c"].min(), "max_close_adj_12m": a12["c"].max(),
                   "shares_outstanding_ref": tick[T].get("share_class_shares_outstanding")})
        for lab, start in (("3m", "2026-06-26"), ("6m", "2026-03-26"), ("12m", "2025-09-26")):
            w = raw.loc[start:END]
            wa = adj.loc[start:END]
            aw.append({"ticker": T, "window": lab, "start": w.index.min(), "end": w.index.max(), "n_days": len(w),
                       "adv_shares_unadj": w["v"].mean(), "adv_shares_split_adj": wa["v"].mean(),
                       "median_daily_shares_unadj": w["v"].median(),
                       "adv_dollar": w["dollar"].mean(), "median_daily_dollar": w["dollar"].median(),
                       "avg_trades_per_day": w["n"].mean(), "avg_trade_size_shares": (w["v"] / w["n"]).mean(),
                       "avg_trade_size_dollar": (w["dollar"] / w["n"]).mean(),
                       "avg_close_unadj": w["c"].mean()})
        raw2 = raw.loc["2022-01-01":END].copy()
        raw2["year"] = raw2.index.str[:4]
        raw2["month"] = raw2.index.str[:7]
        adj2 = adj.loc["2022-01-01":END].copy()
        raw2["v_adj"] = adj2["v"]
        raw2["rel_tick_bps"] = 1e4 * 0.01 / raw2["c"]
        for key, L in (("year", ay), ("month", am)):
            g = raw2.groupby(key)
            df = pd.DataFrame({"n_days": g.size(), "adv_shares_unadj": g["v"].mean(), "adv_shares_split_adj": g["v_adj"].mean(),
                               "adv_dollar": g["dollar"].mean(), "avg_trades_per_day": g["n"].mean(),
                               "avg_trade_size_shares": g.apply(lambda x: x["v"].sum() / x["n"].sum()),
                               "avg_trade_size_dollar": g.apply(lambda x: x["dollar"].sum() / x["n"].sum()),
                               "mean_close_unadj": g["c"].mean(), "min_close_unadj": g["c"].min(), "max_close_unadj": g["c"].max(),
                               "mean_rel_tick_bps": g["rel_tick_bps"].mean()}).reset_index()
            df.insert(0, "ticker", T)
            L.append(df)
    pd.DataFrame(pl).to_csv(OUT / "price_levels.csv", index=False)
    pd.DataFrame(aw).to_csv(OUT / "activity_windows.csv", index=False)
    ay = pd.concat(ay); ay.to_csv(OUT / "activity_yearly.csv", index=False)
    am = pd.concat(am); am.to_csv(OUT / "activity_monthly.csv", index=False)
    am[["ticker", "month", "mean_close_unadj", "mean_rel_tick_bps"]].to_csv(OUT / "relative_tick_monthly.csv", index=False)

    # charts: activity trend + relative tick (one measure per panel, focus + context)
    fig, axes = plt.subplots(3, 1, figsize=(11, 11.5), sharex=True)
    for ax, col, scale, lab in ((axes[0], "adv_dollar", 1e9, "Avg daily $ volume ($bn, log)"),
                                (axes[1], "avg_trades_per_day", 1e3, "Avg trades per day (thousands, log)"),
                                (axes[2], "mean_rel_tick_bps", 1.0, "Relative tick = $0.01 / close (bps, log)")):
        ax.set_yscale("log")
        ser = {}
        for T in TICKERS:
            d = am[am.ticker == T]
            ser[T] = (pd.to_datetime(d["month"] + "-15").values, (d[col] / scale).values)
        allv = np.concatenate([v[1] for v in ser.values()])
        ax.set_ylim(np.nanmin(allv) * 0.8, np.nanmax(allv) * 1.25)
        focus_lines(ax, ser, logy=True)
        ax.set_ylabel(lab)
    axes[0].set_title("Monthly averages from daily bars (unadjusted), Jan-2022 to 25-Sep-2026 (Massive /v2/aggs)", fontsize=10)
    fig.subplots_adjust(right=0.9, hspace=0.12, top=0.95, bottom=0.05, left=0.08)
    fig.savefig(OUT / "activity_trend.png", dpi=110); plt.close(fig)

    # ---------------- minute-bar statistics
    ts_rows, vol_rows, prof_rows, sess_rows, gap_rows, mon_rows = [], [], [], [], [], []
    _, half = trading_days_and_halfdays()
    for T in TICKERS:
        m = min_bars(T)
        m = m[~m.date.isin(half)]  # half-days (13:00 close) excluded from all minute-bar statistics
        rth = m[(m.minute >= 570) & (m.minute < 960)].copy()
        # full 390-minute grid per day, forward-filled close (a missing minute = no eligible trade = no change)
        days = sorted(rth.date.unique())
        idx = pd.MultiIndex.from_product([days, range(570, 960)], names=["date", "minute"])
        g = rth.set_index(["date", "minute"])[["c", "v"]].reindex(idx)
        g["missing"] = g["c"].isna()
        g["c"] = g.groupby(level=0)["c"].ffill()
        g["dc"] = g.groupby(level=0)["c"].diff()
        g = g.reset_index()
        g["year"] = g["date"].str[:4]
        g["ticks"] = (g["dc"].abs() / 0.01).round(6)
        for per, sel in [(y, g.year == y) for y in ["2022", "2023", "2024", "2025", "2026"]] + \
                        [("last12m", (g.date >= "2025-09-26") & (g.date <= END)), ("last3m", (g.date >= "2026-06-26") & (g.date <= END))]:
            x = g[sel & g.dc.notna()]
            tk = x["ticks"]
            ts_rows.append({"ticker": T, "period": per, "n_days": x.date.nunique(), "n_1min_changes": len(x),
                            "share_zero_change": (tk < 0.5).mean(), "share_1tick": ((tk >= 0.5) & (tk < 1.5)).mean(),
                            "share_2tick": ((tk >= 1.5) & (tk < 2.5)).mean(), "share_3to5": ((tk >= 2.5) & (tk < 5.5)).mean(),
                            "share_6to10": ((tk >= 5.5) & (tk < 10.5)).mean(), "share_gt10": (tk >= 10.5).mean(),
                            "mean_abs_ticks": tk.mean(), "median_abs_ticks": tk.median(),
                            "mean_abs_ticks_nonzero": tk[tk >= 0.5].mean(),
                            "share_missing_minutes": g[sel]["missing"].mean(),
                            "mean_price": x["c"].mean()})
        g["month"] = g["date"].str[:7]
        x = g[g.dc.notna()]
        gm = x.groupby("month")
        mon = pd.DataFrame({"n": gm.size(), "share_zero_change": gm["ticks"].apply(lambda v: (v < 0.5).mean()),
                            "mean_abs_ticks": gm["ticks"].mean(), "median_abs_ticks": gm["ticks"].median(),
                            "mean_price": gm["c"].mean()}).reset_index()
        mon["rel_tick_bps"] = 1e4 * 0.01 / mon["mean_price"]
        mon.insert(0, "ticker", T)
        mon_rows.append(mon)
        # 1-min and 5-min close-to-close return std by 30-min bucket, trade-price based
        for per, lo in (("last12m", "2025-09-26"), ("since_2026-07-15", "2026-07-15")):
            l12 = g[(g.date >= lo) & (g.date <= END)].copy()
            l12["r1"] = np.log(l12["c"]).groupby(l12["date"]).diff() * 1e4
            l12["bucket"] = 570 + ((l12["minute"] - 570) // 30) * 30
            l12["c5"] = l12.groupby("date")["c"].shift(5)
            l12["r5"] = np.log(l12["c"] / l12["c5"]) * 1e4
            five = l12[(l12.minute - 570) % 5 == 4]  # non-overlapping 5-min returns ending on minute 4 of each 5
            for b, x in l12.groupby("bucket"):
                y5 = five[five.bucket == b]["r5"].dropna()
                vol_rows.append({"ticker": T, "period": per, "n_days": x.date.nunique(), "bucket_start": b,
                                 "std_r1_bps": x["r1"].std(), "n_r1": x["r1"].notna().sum(), "std_r5_bps": y5.std(),
                                 "n_r5": len(y5), "mean_abs_r1_bps": x["r1"].abs().mean()})
            x = l12
            y5 = five["r5"].dropna()
            vol_rows.append({"ticker": T, "period": per, "n_days": x.date.nunique(), "bucket_start": -1,
                             "std_r1_bps": x["r1"].std(), "n_r1": x["r1"].notna().sum(), "std_r5_bps": y5.std(),
                             "n_r5": len(y5), "mean_abs_r1_bps": x["r1"].abs().mean()})
        # intraday volume profile (last 12 months, all sessions) from minute bars
        ml = m[(m.date >= "2025-09-26") & (m.date <= END)]
        tot = ml.groupby("date")["v"].sum()
        ml = ml.assign(share=ml["v"] / ml["date"].map(tot))
        rth_tot = ml[(ml.minute >= 570) & (ml.minute < 960)].groupby("date")["v"].sum()
        prof = ml.groupby("minute")["share"].sum() / len(tot)
        rshare = (ml[(ml.minute >= 570) & (ml.minute < 960)].assign(rs=lambda d: d["v"] / d["date"].map(rth_tot))
                  .groupby("minute")["rs"].sum() / len(tot))
        p = pd.DataFrame({"minute": prof.index, "share_of_minutebar_day_volume": prof.values})
        p["share_of_rth_volume"] = p["minute"].map(rshare)
        p.insert(0, "ticker", T)
        prof_rows.append(p)
        sess = ml.assign(sess=np.select([ml.minute < 570, ml.minute < 960], ["pre", "rth"], "post")).groupby(["date", "sess"])["v"].sum().unstack(fill_value=0)
        sess = sess.div(sess.sum(axis=1), axis=0)
        # compare with daily-bar volume (daily bars include the closing-auction print; see notes)
        dv = day_bars(T, False).loc["2025-09-26":END, "v"]
        sess_rows.append({"ticker": T, "n_days": len(sess), "pre_share": sess["pre"].mean(), "rth_share": sess["rth"].mean(),
                          "post_share": sess["post"].mean(),
                          "minutebar_sum_over_dailybar_volume": (tot / dv.reindex(tot.index)).mean(),
                          "first30_share_of_rth": p[(p.minute >= 570) & (p.minute < 600)]["share_of_rth_volume"].sum(),
                          "last30_share_of_rth": p[(p.minute >= 930) & (p.minute < 960)]["share_of_rth_volume"].sum(),
                          "min_1200_1300_share_of_rth": p[(p.minute >= 720) & (p.minute < 780)]["share_of_rth_volume"].sum()})
        # RTH gaps without any minute bar, 2024-2026 (candidate halts)
        r24 = rth[rth.date >= "2024-01-01"].sort_values(["date", "minute"])
        for dte, x in r24.groupby("date"):
            mins = np.r_[x.minute.values]
            # include session edges
            first, last = mins.min(), mins.max()
            gaps = np.diff(mins)
            for i in np.nonzero(gaps >= 3)[0]:
                gap_rows.append({"ticker": T, "date": dte, "last_bar_before": f"{mins[i] // 60:02d}:{mins[i] % 60:02d}",
                                 "next_bar": f"{mins[i + 1] // 60:02d}:{mins[i + 1] % 60:02d}",
                                 "missing_minutes": int(gaps[i] - 1)})
            if first > 575:
                gap_rows.append({"ticker": T, "date": dte, "last_bar_before": "open", "next_bar": f"{first // 60:02d}:{first % 60:02d}",
                                 "missing_minutes": int(first - 570)})
    pd.DataFrame(ts_rows).to_csv(OUT / "minbar_tick_stats.csv", index=False)
    mon = pd.concat(mon_rows)
    mon.to_csv(OUT / "minbar_tick_stats_monthly.csv", index=False)
    # tick-constraint scatter: relative tick vs share of zero-change 1-min bars (ticker-months)
    fig, ax = plt.subplots(figsize=(9, 6))
    for T in TICKERS:
        d = mon[mon.ticker == T]
        if T in FOCUS_COLORS:
            continue
        ax.scatter(d.rel_tick_bps, d.share_zero_change * 100, s=10, color=CONTEXT_GRAY, alpha=0.7, lw=0)
    for T in ("SOXL", "SOXS"):
        d = mon[mon.ticker == T]
        ax.scatter(d.rel_tick_bps, d.share_zero_change * 100, s=22, color=FOCUS_COLORS[T], label=T, lw=0.6, edgecolor="white")
        last = d.iloc[-1]
        ax.annotate(f"{T} Sep-2026", (last.rel_tick_bps, last.share_zero_change * 100), xytext=(6, 6), textcoords="offset points",
                    fontsize=8, color=FOCUS_COLORS[T], fontweight="bold")
    ax.scatter([], [], s=10, color=CONTEXT_GRAY, label="SOXX, SMH, NVDA, TQQQ, SQQQ, QQQ, SPY")
    ax.set_xscale("log")
    ax.set_xlabel("Relative tick = $0.01 / mean price (bps, log)")
    ax.set_ylabel("% of RTH 1-min bars with zero close-to-close change")
    ax.set_title("Tick constraint vs price level: one point per ticker-month, Jan-2022 to Sep-2026\n(1-min bars, unadjusted, half-days excluded)", fontsize=10)
    ax.legend(fontsize=8, frameon=False)
    style_ax(ax)
    fig.tight_layout(); fig.savefig(OUT / "tick_constraint_scatter.png", dpi=110); plt.close(fig)
    pd.DataFrame(vol_rows).to_csv(OUT / "minbar_vol_by_bucket.csv", index=False)
    prof = pd.concat(prof_rows)
    prof.to_csv(OUT / "volume_profile_minute.csv", index=False)
    pd.DataFrame(sess_rows).to_csv(OUT / "volume_session_split.csv", index=False)
    pd.DataFrame(gap_rows, columns=["ticker", "date", "last_bar_before", "next_bar", "missing_minutes"]).to_csv(
        OUT / "rth_trade_gaps_2024_2026.csv", index=False)

    # volume profile chart (RTH share per minute): small multiples, one panel per ticker, same y scale
    fig, axes = plt.subplots(3, 3, figsize=(12, 8.5), sharex=True, sharey=True)
    ticks = list(range(570, 961, 90))
    for ax, T in zip(axes.flat, TICKERS):
        d = prof[(prof.ticker == T) & (prof.minute >= 570) & (prof.minute < 960)]
        c = {"SOXL": "#2a78d6", "SOXS": "#eb6834"}.get(T, "#6d6c67")
        ax.plot(d.minute, d.share_of_rth_volume * 100, color=c, lw=1.2)
        ax.set_yscale("log")
        ax.set_title(T, fontsize=9, loc="left")
        ax.set_xticks(ticks); ax.set_xticklabels([f"{t // 60:02d}:{t % 60:02d}" for t in ticks])
        style_ax(ax)
    for ax in axes[:, 0]:
        ax.set_ylabel("% of RTH volume per minute (log)")
    fig.suptitle("Intraday volume profile: mean share of 09:30-15:59 minute-bar volume per minute, 2025-09-26..2026-09-25\n"
                 "(1-min bars; the closing-auction print is not in the minute bars - see auction tables)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "volume_profile.png", dpi=110); plt.close(fig)
    print("done")


if __name__ == "__main__":
    main()
    import os
    os._exit(0)
