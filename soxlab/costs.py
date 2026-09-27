"""Transaction-cost model: half-spread per side + per-share commission + SEC / FINRA fees on sells.

Half-spread source (in order of preference):
  1. analysis/microstructure/output/cost_model_halfspread.csv (separate analyst). Columns:
     ticker, year, bucket_start_et, bucket_end_et, median_spread_cents, mean_spread_cents,
     median_half_spread_bps, mean_half_spread_bps, n_obs.  We use the CENTS column and convert to bps
     with the UNADJUSTED price at trade time: half_bps = spread_cents/2 / 100 / price * 1e4.
  2. analysis/backtests/output/halfspread_estimate_nbbo_sample.csv produced by
     scripts/estimate_spreads.py from a light /v3/quotes sample (same columns).
Lookups fall back to the nearest available year and the nearest time bucket.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

FALLBACK_FILE = config.OUTPUT_DIR / "halfspread_estimate_nbbo_sample.csv"


def _hhmm_to_min(s) -> int:
    s = str(s).strip()
    if ":" in s:
        hh, mm = s.split(":")[:2]
        return int(hh) * 60 + int(mm)
    return int(float(s))


def load_halfspread_table(prefer_micro: bool = True) -> tuple[pd.DataFrame, str]:
    """Return (table, source_path). Raises FileNotFoundError when neither source exists."""
    cands = [config.MICRO_COST_FILE, FALLBACK_FILE] if prefer_micro else [FALLBACK_FILE, config.MICRO_COST_FILE]
    for pth in cands:
        if Path(pth).exists():
            t = pd.read_csv(pth)
            need = {"ticker", "year", "bucket_start_et", "bucket_end_et", "median_spread_cents"}
            if not need.issubset(t.columns):
                continue
            t = t.copy()
            t["b0"] = t["bucket_start_et"].map(_hhmm_to_min)
            t["b1"] = t["bucket_end_et"].map(_hhmm_to_min)
            t["year"] = t["year"].astype(int)
            t = t.dropna(subset=["median_spread_cents"])
            return t, str(pth)
    raise FileNotFoundError("no half-spread table found; run scripts/estimate_spreads.py")


@dataclass
class CostModel:
    spread_table: pd.DataFrame | None = None
    spread_source: str = ""
    spread_stat: str = "median_spread_cents"       # or mean_spread_cents
    commission_per_share: float = config.COMMISSION_PER_SHARE
    notional: float = config.TRADE_NOTIONAL
    sec_schedule: list = field(default_factory=lambda: list(config.SEC_FEE_SCHEDULE))
    taf_schedule: list = field(default_factory=lambda: list(config.FINRA_TAF_SCHEDULE))
    spread_multiplier: float = 1.0                  # sensitivity knob (1.0 = half-spread per side)
    fixed_half_spread_bps: float | None = None      # override (tests / sensitivity)

    @classmethod
    def default(cls, **kw) -> "CostModel":
        try:
            t, src = load_halfspread_table()
        except FileNotFoundError:
            t, src = None, ""
        return cls(spread_table=t, spread_source=src, **kw)

    # ---------------------------------------------------------------- spread
    def half_spread_bps(self, ticker, years, minutes_et, prices_unadj) -> np.ndarray:
        years = np.asarray(years, int)
        minutes_et = np.asarray(minutes_et, int)
        prices_unadj = np.asarray(prices_unadj, float)
        if self.fixed_half_spread_bps is not None:
            return np.full(len(years), self.fixed_half_spread_bps) * self.spread_multiplier
        if self.spread_table is None:
            raise RuntimeError("CostModel has no spread table")
        t = self.spread_table[self.spread_table["ticker"] == ticker]
        if t.empty:
            raise KeyError(f"no spread rows for {ticker}")
        out = np.full(len(years), np.nan)
        avail_years = np.array(sorted(t["year"].unique()))
        for y in np.unique(years):
            yy = avail_years[np.argmin(np.abs(avail_years - y))]
            ty = t[t["year"] == yy].sort_values("b0")
            mids = ((ty["b0"] + ty["b1"]) / 2).to_numpy()
            cents = ty[self.spread_stat].to_numpy()
            sel = years == y
            m = minutes_et[sel]
            inb = (m[:, None] >= ty["b0"].to_numpy()[None, :]) & (m[:, None] < ty["b1"].to_numpy()[None, :])
            idx = np.where(inb.any(axis=1), inb.argmax(axis=1), np.abs(m[:, None] - mids[None, :]).argmin(axis=1))
            out[sel] = cents[idx]
        return out / 2.0 / 100.0 / prices_unadj * 1e4 * self.spread_multiplier

    # ---------------------------------------------------------------- fees
    @staticmethod
    def _sched(schedule, dates) -> np.ndarray:
        eff = pd.to_datetime([s[0] for s in schedule])
        dates = pd.to_datetime(dates)
        idx = np.searchsorted(eff.values, dates.values, side="right") - 1
        idx = np.clip(idx, 0, len(schedule) - 1)
        return idx

    def sec_fee_bps(self, dates) -> np.ndarray:
        idx = self._sched(self.sec_schedule, dates)
        rate_per_million = np.array([self.sec_schedule[i][1] for i in idx])
        return rate_per_million / 1e6 * 1e4

    def taf_bps(self, dates, prices_unadj) -> np.ndarray:
        idx = self._sched(self.taf_schedule, dates)
        per_share = np.array([self.taf_schedule[i][1] for i in idx])
        cap = np.array([self.taf_schedule[i][2] for i in idx])
        shares = self.notional / np.asarray(prices_unadj, float)
        fee = np.minimum(per_share * shares, cap)
        return fee / self.notional * 1e4

    def commission_bps(self, prices_unadj) -> np.ndarray:
        return self.commission_per_share / np.asarray(prices_unadj, float) * 1e4

    # ---------------------------------------------------------------- per trade
    def trade_costs(self, trades: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Add cost columns (bps of notional) to a trades frame from soxlab.backtest.

        Required columns: date, side (+1 long / -1 short), entry_min_et, exit_min_et,
        entry_px_unadj, exit_px_unadj.
        """
        tr = trades.copy()
        if tr.empty:
            for c in ("cost_spread_bps", "cost_comm_bps", "cost_fees_bps", "cost_bps"):
                tr[c] = pd.Series(dtype=float)
            return tr
        yrs = pd.to_datetime(tr["date"]).dt.year.to_numpy()
        hs_in = self.half_spread_bps(ticker, yrs, tr["entry_min_et"], tr["entry_px_unadj"])
        hs_out = self.half_spread_bps(ticker, yrs, tr["exit_min_et"], tr["exit_px_unadj"])
        comm = self.commission_bps(tr["entry_px_unadj"]) + self.commission_bps(tr["exit_px_unadj"])
        # sells: long exit, short entry (short sale)
        sell_px = np.where(tr["side"].to_numpy() > 0, tr["exit_px_unadj"], tr["entry_px_unadj"])
        fees = self.sec_fee_bps(tr["date"]) + self.taf_bps(tr["date"], sell_px)
        tr["cost_spread_bps"] = hs_in + hs_out
        tr["cost_comm_bps"] = comm
        tr["cost_fees_bps"] = fees
        tr["cost_bps"] = tr["cost_spread_bps"] + tr["cost_comm_bps"] + tr["cost_fees_bps"]
        tr["net_bps"] = tr["gross_bps"] - tr["cost_bps"]
        return tr
