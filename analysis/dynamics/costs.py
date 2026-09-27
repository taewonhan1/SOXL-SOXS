"""Transaction-cost model (per side), in fractions of the unadjusted price.

Quoted spread model (from the light NBBO sample in output/nbbo_windows.csv, built by 02_download_quotes.py):
  * For each (ticker, trade date) pick the nearest NBBO sample day in the SAME split regime
    (fallback: nearest overall); for the time of day use that day's window nearest in clock time
    (09:35 / 10:30 / 12:30 / 14:30 / 15:45 windows; monthly sample days have 09:35, 10:30, 14:30).
  * If the sampled window was tick-bound (>= 80% of time at a 1-cent spread) its $ spread is used as-is;
    otherwise the $ spread is scaled by (unadjusted price at trade / sampled mid) - i.e. spreads are
    assumed proportional to price when they are not pinned at the 1-cent tick.
  * Floor of $0.01 (one tick).
  Tickers without a monthly history (SOXX, SMH, NVDA, TQQQ, QQQ) use the median bps spread of the
  recent 10-day sample (10:30 and 14:30 windows) - see move-to-cost caveats.

Fees (sell side only unless stated):
  * SEC Section 31: $27.80 per $1M sold until 2025-05-13; $0.00 from 2025-05-14 to 2026-04-03;
    $20.60 per $1M from 2026-04-04 (Federal Register / SEC fee-rate advisories).  For dates before
    2024-10-01 (robustness window) $27.80/M is ASSUMED (simplification; <= 0.28 bps).
  * FINRA TAF: $0.000166/share sold through 2025, $0.000195/share sold from 2026-01-01 (caps not binding
    at the assumed trade size).
  * Scenario "retail": zero commission, cross the quoted spread, regulatory fees passed through.
  * Scenario "per_share": retail + $0.0035/share commission on BOTH sides.
Position size assumption: $25,000 notional per trade (only matters for caps/minimums, which are ignored).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import OUT

TICK = 0.01
WIN_MIN = {"09:35": 5, "10:30": 60, "12:30": 180, "14:30": 300, "15:45": 375}  # minute-of-day (from 09:30)


def sec_rate(dates) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates)).to_numpy()
    r = np.full(len(d), 27.80e-6)
    r[(d >= np.datetime64("2025-05-14")) & (d < np.datetime64("2026-04-04"))] = 0.0
    r[d >= np.datetime64("2026-04-04")] = 20.60e-6
    return r


def taf_per_share(dates) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates)).to_numpy()
    return np.where(d >= np.datetime64("2026-01-01"), 0.000195, 0.000166)


class SpreadModel:
    def __init__(self, ticker: str, panel_dates, panel_fac):
        self.ticker = ticker
        nb = pd.read_csv(OUT / "nbbo_windows.csv")
        nb = nb[(nb.ticker == ticker) & (nb.n_quotes > 0)].copy()
        self.has_history = (nb["sample"] == "monthly").any()
        nb["date"] = pd.to_datetime(nb["date"]).dt.date
        self.nb = nb
        # regime id per date (changes whenever the unadjusted factor changes)
        fac_map = dict(zip(panel_dates, panel_fac))
        self.fac_map = fac_map
        days = sorted(nb["date"].unique())
        self.sample_days = np.array(days)
        self.sample_fac = np.array([fac_map.get(d, np.nan) for d in days])
        self.tab = {}
        for d, g in nb.groupby("date"):
            wins = []
            for _, r in g.iterrows():
                wins.append((WIN_MIN[r["window"]], r["tw_spread_usd"], r["tw_mid"], r["share_time_1tick"] >= 0.8))
            wins.sort()
            self.tab[d] = wins
        rec = nb[(nb["sample"] == "recent") & nb["window"].isin(["10:30", "14:30"])]
        self.recent_bps = float(np.median(rec["tw_spread_bps"])) if len(rec) else np.nan

    def nearest_day(self, d, fac):
        dd = np.array([(pd.Timestamp(x) - pd.Timestamp(d)).days for x in self.sample_days])
        same = np.isclose(self.sample_fac, fac, rtol=1e-6) if np.isfinite(fac) else np.zeros_like(dd, bool)
        cand = np.where(same)[0] if same.any() else np.arange(len(dd))
        return self.sample_days[cand[np.argmin(np.abs(dd[cand]))]]

    def spread_usd(self, d, minute, px_unadj):
        """quoted spread in $ for date d, minute-of-day index (0..389), unadjusted price."""
        if not self.has_history:
            return max(TICK, self.recent_bps * 1e-4 * px_unadj)
        sd = self.nearest_day(d, self.fac_map.get(d, np.nan))
        wins = self.tab[sd]
        w = min(wins, key=lambda x: abs(x[0] - minute))
        _, s, mid, tickbound = w
        val = s if tickbound else s * px_unadj / mid
        return max(TICK, val)

    def day_table(self, dates):
        """precompute per-date list of (minute, spread_usd_base, mid, tickbound) for vectorised use."""
        out = {}
        for d in dates:
            sd = self.nearest_day(d, self.fac_map.get(d, np.nan))
            out[d] = self.tab[sd]
        return out

    def spread_matrix(self, dates, px_unadj):
        """px_unadj: [n_days, 390] unadjusted prices -> spread $ matrix [n_days, 390]."""
        n = len(dates)
        S = np.empty((n, 390))
        mins = np.arange(390)
        if not self.has_history:
            return np.maximum(TICK, self.recent_bps * 1e-4 * px_unadj)
        for i, d in enumerate(dates):
            wins = self.tab[self.nearest_day(d, self.fac_map.get(d, np.nan))]
            wm = np.array([w[0] for w in wins])
            j = np.abs(mins[:, None] - wm[None, :]).argmin(axis=1)
            s = np.array([w[1] for w in wins])[j]
            mid = np.array([w[2] for w in wins])[j]
            tb = np.array([w[3] for w in wins])[j]
            S[i] = np.where(tb, s, s * px_unadj[i] / mid)
        return np.maximum(TICK, S)


def side_costs(scenario: str, dates, px_unadj, spread_usd, is_sell: bool):
    """Cost of one side (fraction of price): half spread + fees.  Arrays broadcast."""
    half = 0.5 * spread_usd / px_unadj
    c = half
    if is_sell:
        c = c + sec_rate(dates) + taf_per_share(dates) / px_unadj
    if scenario == "per_share":
        c = c + 0.0035 / px_unadj
    return c
