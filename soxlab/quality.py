"""Data-quality checks on the cached Massive bars (all computed from data actually downloaded)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import api, config
from . import data as sdata


def md_table(df: pd.DataFrame, floatfmt: str = "{:.4g}", max_rows: int = 60) -> str:
    """Minimal markdown table renderer (no tabulate dependency)."""
    df = df.head(max_rows)
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for v in r.values:
            if isinstance(v, (float, np.floating)):
                cells.append("" if not np.isfinite(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------
def coverage(tickers, cal: pd.DataFrame, start=config.HISTORY_START, end=config.HISTORY_END) -> pd.DataFrame:
    """Per ticker-year coverage of 1-min bars: RTH missing minutes, extended-hours bars, fractional volume."""
    rows = []
    n_rth = cal["n_rth_minutes"]
    for tk in tickers:
        # UNADJUSTED bars: split-adjusting divides volume (e.g. SOXS adjusted volume becomes fractional)
        b = sdata.load_minute_bars(tk, False, start, end)
        b["year"] = b["date"].dt.year
        b["sess"] = np.select([b["mod"] < config.RTH_START_MIN, b["mod"] < config.RTH_END_MIN], ["pre", "rth"], "post")
        # on half-days, bars 13:00-15:59 are extended-hours
        hd = b["date"].map(cal["is_half_day"]).fillna(False).astype(bool)
        b.loc[hd & (b["mod"] >= config.HALF_DAY_END_MIN) & (b["mod"] < config.RTH_END_MIN), "sess"] = "post"
        for y, g in b.groupby("year"):
            days = cal.index[cal.index.year == y]
            exp = int(n_rth.loc[days].sum())
            rth = g[g["sess"] == "rth"]
            per_day = rth.groupby("date").size().reindex(days).fillna(0)
            rows.append({
                "ticker": tk, "year": y, "trading_days": len(days), "rth_expected_minutes": exp,
                "rth_bars": len(rth), "rth_missing_pct": 100 * (1 - len(rth) / exp),
                "rth_missing_per_day_mean": float((n_rth.loc[days] - per_day).mean()),
                "days_with_missing_0930_bar": int((~rth.groupby("date")["mod"].min().reindex(days).eq(config.RTH_START_MIN)).sum()),
                "pre_bars_per_day": len(g[g["sess"] == "pre"]) / len(days),
                "post_bars_per_day": len(g[g["sess"] == "post"]) / len(days),
                "ext_volume_share_pct": 100 * g.loc[g["sess"] != "rth", "v"].sum() / g["v"].sum(),
                "fractional_volume_bars_pct": 100 * float((g["v"] % 1 != 0).mean()),
                "dup_timestamps_in_cache": int(g["t"].duplicated().sum()),
                "bars_not_on_minute": int((g["t"] % 60000 != 0).sum()),
                "ohlc_inconsistent": int(((g["h"] < g[["o", "c"]].max(axis=1) - 1e-9) |
                                          (g["l"] > g[["o", "c"]].min(axis=1) + 1e-9)).sum()),
                "vw_outside_hl": int(((g["vw"] > g["h"] + 1e-6) | (g["vw"] < g["l"] - 1e-6)).sum()),
                "vw_outside_hl_rth_pct": 100 * float(((rth["vw"] > rth["h"] + 1e-6) | (rth["vw"] < rth["l"] - 1e-6)).mean()),
                "vw_outside_hl_ext_pct": 100 * float(((g.loc[g["sess"] != "rth", "vw"] > g.loc[g["sess"] != "rth", "h"] + 1e-6) |
                                                      (g.loc[g["sess"] != "rth", "vw"] < g.loc[g["sess"] != "rth", "l"] - 1e-6)).mean()),
                "first_fractional_volume_bar": (g.loc[g["v"] % 1 != 0, "ts"].min().strftime("%Y-%m-%d %H:%M")
                                                if (g["v"] % 1 != 0).any() else ""),
                "nonpositive_volume": int((g["v"] <= 0).sum()),
            })
    return pd.DataFrame(rows)


def raw_duplicate_sample(tickers, months=("2019-06", "2022-03", "2024-04", "2026-07"), adjusted: bool = False) -> pd.DataFrame:
    """Re-fetch a sample of months WITHOUT de-duplication and compare against the cache."""
    rows = []
    for tk in tickers:
        for ym in months:
            y, m = map(int, ym.split("-"))
            first = f"{ym}-01"
            last = (pd.Timestamp(first) + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
            res = api.get_all(f"/v2/aggs/ticker/{tk}/range/1/minute/{first}/{last}",
                              {"adjusted": "true" if adjusted else "false", "sort": "asc", "limit": 50000})
            raw = pd.DataFrame(res)
            cache = pd.read_parquet(sdata.bars_path(tk, adjusted, y, m))
            same = raw.drop_duplicates("t").set_index("t")[["o", "h", "l", "c", "v"]].sort_index()
            cc = cache.set_index("t")[["o", "h", "l", "c", "v"]].sort_index()
            common = same.index.intersection(cc.index)
            rows.append({"ticker": tk, "month": ym, "raw_rows": len(raw), "raw_duplicate_t": int(raw["t"].duplicated().sum()),
                         "cache_rows": len(cache), "rows_only_in_api": int(len(same.index.difference(cc.index))),
                         "rows_only_in_cache": int(len(cc.index.difference(same.index))),
                         "value_mismatches": int((~np.isclose(same.loc[common].values, cc.loc[common].values)).any(axis=1).sum())})
    return pd.DataFrame(rows)


def outliers(tickers, start=config.HISTORY_START, end=config.HISTORY_END, thr: float = 0.05) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Isolated spikes: |log r_t| > thr AND |log r_{t+1}| > thr with opposite sign (price jumps then reverts)."""
    summ, ex = [], []
    for tk in tickers:
        b = sdata.load_minute_bars(tk, True, start, end).sort_values("t")
        lc = np.log(b["c"].to_numpy())
        same_day = (b["date"].to_numpy()[1:] == b["date"].to_numpy()[:-1])
        r = np.full(len(b), np.nan)
        r[1:] = np.where(same_day, np.diff(lc), np.nan)
        rn = np.append(r[1:], np.nan)
        spike = (np.abs(r) > thr) & (np.abs(rn) > thr) & (np.sign(r) == -np.sign(rn))
        wide = (b["h"] / b["l"] - 1).to_numpy() > 2 * thr
        rth = (b["mod"] >= config.RTH_START_MIN) & (b["mod"] < config.RTH_END_MIN)
        summ.append({"ticker": tk, "bars": len(b), "isolated_spikes_rth": int((spike & rth).sum()),
                     "isolated_spikes_ext": int((spike & ~rth).sum()),
                     f"bars_range_gt_{int(200 * thr)}pct_rth": int((wide & rth).sum()),
                     f"bars_range_gt_{int(200 * thr)}pct_ext": int((wide & ~rth).sum())})
        for i in np.flatnonzero(spike)[:3]:
            ex.append({"ticker": tk, "ts_et": b["ts"].iloc[i].strftime("%Y-%m-%d %H:%M"),
                       "prev_close": b["c"].iloc[i - 1], "close": b["c"].iloc[i], "next_close": b["c"].iloc[i + 1],
                       "volume": b["v"].iloc[i], "trades": b["n"].iloc[i]})
    return pd.DataFrame(summ), pd.DataFrame(ex)


def split_checks(tickers, start=config.HISTORY_START, end=config.HISTORY_END) -> pd.DataFrame:
    """At each split execution date: unadjusted overnight ratio vs split ratio; adjusted series continuity."""
    rows = []
    for tk in tickers:
        sp = sdata.load_splits(tk)
        if sp.empty:
            continue
        du = sdata.load_daily(tk, False)
        da = sdata.load_daily(tk, True)
        fac = (du["c"] / da["c"]).rename("unadj_over_adj")
        for _, s in sp.iterrows():
            d = pd.Timestamp(s["execution_date"])
            if d < pd.Timestamp(start) or d > pd.Timestamp(end) or d not in du.index:
                continue
            i = du.index.get_loc(d)
            prev = du.index[i - 1]
            ratio = s["split_to"] / s["split_from"]           # shares after / before
            un_gap = du.loc[d, "o"] / du.loc[prev, "c"]
            ad_gap = da.loc[d, "o"] / da.loc[prev, "c"]
            f = fac.iloc[max(0, i - 3): i + 3]
            steps = int((f.pct_change().abs() > 0.01).sum())
            rows.append({"ticker": tk, "execution_date": d.strftime("%Y-%m-%d"), "split_from": s["split_from"],
                         "split_to": s["split_to"], "expected_unadj_open_over_prev_close": 1 / ratio,
                         "unadj_open_over_prev_close": un_gap, "adj_open_over_prev_close": ad_gap,
                         "unadj_prev_close": du.loc[prev, "c"], "unadj_open": du.loc[d, "o"],
                         "adj_prev_close": da.loc[prev, "c"], "adj_open": da.loc[d, "o"],
                         "factor_steps_near_date": steps})
        # factor should only change on split dates
        chg = fac[(fac.pct_change().abs() > 0.001)]
        chg = chg[(chg.index >= pd.Timestamp(start)) & (chg.index <= pd.Timestamp(end))]
        unexpected = [x for x in chg.index if x not in set(pd.to_datetime(sp["execution_date"]))]
        rows.append({"ticker": tk, "execution_date": "ALL", "factor_changes_off_split_dates": len(unexpected),
                     "examples": ",".join(x.strftime("%Y-%m-%d") for x in unexpected[:5])})
    return pd.DataFrame(rows)


def soxl_soxs_consistency(ctx: dict) -> pd.DataFrame:
    """Daily and minute-level consistency between SOXL, SOXS and 3x SOXX (by year)."""
    off = ctx["official"]
    pl, ps, px = ctx["panels"]["SOXL"], ctx["panels"]["SOXS"], ctx["panels"]["SOXX"]
    dates = pl.dates
    rl = off["SOXL"].pct_change()
    rs = off["SOXS"].pct_change()
    rx = off["SOXX"].pct_change()
    m1l = np.log(pl.c[:, 1:] / pl.c[:, :-1])
    m1s = np.log(ps.c[:, 1:] / ps.c[:, :-1])
    both = pl.present[:, 1:] & ps.present[:, 1:] & pl.present[:, :-1] & ps.present[:, :-1]
    div = ctx["features"]["SOXL"]["soxl_soxs_div_bps"]
    rows = []
    for y in sorted(set(dates.year)):
        dm = (dates.year == y)
        ok = dm & rl.notna().to_numpy() & rs.notna().to_numpy()
        a, b, x = rl[ok].to_numpy(), rs[ok].to_numpy(), rx[ok].to_numpy()
        slope_sx = np.polyfit(a, b, 1)[0]
        slope_lx = np.polyfit(x, a, 1)[0]
        ml, ms = m1l[dm][both[dm]], m1s[dm][both[dm]]
        big = (np.abs(ml) > 5e-4) & (np.abs(ms) > 5e-4)
        dv = div[dm]
        rows.append({"year": y, "days": int(ok.sum()),
                     "daily_corr_SOXL_SOXS": float(np.corrcoef(a, b)[0, 1]),
                     "daily_slope_SOXS_on_SOXL": float(slope_sx),
                     "daily_slope_SOXL_on_SOXX": float(slope_lx),
                     "days_same_sign_pct": 100 * float(np.mean(np.sign(a) == np.sign(b))),
                     "minute_corr_SOXL_SOXS": float(np.corrcoef(ml, ms)[0, 1]),
                     "minutes_same_direction_pct(|r|>5bp)": 100 * float(np.mean(np.sign(ml[big]) == np.sign(ms[big]))),
                     "div_since_close_bps_p50": float(np.nanmedian(dv)),
                     "div_since_close_bps_p05": float(np.nanpercentile(dv, 5)),
                     "div_since_close_bps_p95": float(np.nanpercentile(dv, 95))})
    return pd.DataFrame(rows)


def daily_vs_minute(tickers, cal: pd.DataFrame, start=config.HISTORY_START, end=config.HISTORY_END) -> pd.DataFrame:
    """Reconcile daily bars with minute bars: official close vs last RTH minute close, volume totals."""
    rows = []
    for tk in tickers:
        b = sdata.load_minute_bars(tk, False, start, end)
        d = sdata.load_daily(tk, False)
        d = d[(d.index >= pd.Timestamp(start)) & (d.index <= pd.Timestamp(end))]
        close_min = cal["n_rth_minutes"].reindex(d.index) + config.RTH_START_MIN
        rth = b[(b["mod"] >= config.RTH_START_MIN)]
        rth = rth[rth["mod"] < rth["date"].map(close_min)]
        last_rth = rth.sort_values("t").groupby("date")["c"].last().reindex(d.index)
        first_rth = rth.sort_values("t").groupby("date")["o"].first().reindex(d.index)
        v_all = b.groupby("date")["v"].sum().reindex(d.index)
        v_rth = rth.groupby("date")["v"].sum().reindex(d.index)
        diff_bps = (d["c"] / last_rth - 1) * 1e4
        rows.append({"ticker": tk, "days": len(d),
                     "official_close_ne_last_rth_minute_close_pct": 100 * float((np.abs(diff_bps) > 0.01).mean()),
                     "abs_diff_close_bps_median": float(np.nanmedian(np.abs(diff_bps))),
                     "abs_diff_close_bps_p95": float(np.nanpercentile(np.abs(diff_bps), 95)),
                     "daily_open_ne_first_rth_open_pct": 100 * float((np.abs(d["o"] / first_rth - 1) > 1e-6).mean()),
                     "daily_volume_over_all_session_minute_volume_median": float(np.nanmedian(d["v"] / v_all)),
                     "daily_volume_over_rth_minute_volume_median": float(np.nanmedian(d["v"] / v_rth))})
    return pd.DataFrame(rows)
