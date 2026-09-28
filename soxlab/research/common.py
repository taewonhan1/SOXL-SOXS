"""Shared definitions for the research studies: periods, data context, costs and statistics.

Conventions (see RESEARCH_PLAN.md, section 1):
* Signal chart = the ticker's regular-session 1-minute panel (09:30-15:59 ET), split-adjusted prices.
  Bar j covers [09:30+j, 09:31+j); a decision at the CLOSE of bar j is executed at the OPEN of bar j+1.
* Day-level inputs use only information available before the session (prior official close,
  prior-day range, ATR through the prior day, pre-market bars).
"""
from __future__ import annotations

from functools import cached_property
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .. import calendar as scal
from .. import config
from .. import data as sdata
from .. import features as sfeat
from ..costs import CostModel, load_halfspread_table

RESEARCH_DIR = config.REPO_ROOT / "analysis" / "strategies"
RESEARCH_OUT = RESEARCH_DIR / "output"
RESEARCH_DATA = config.REPO_ROOT / "data" / "research"
SUPPLEMENT_COST_FILE = RESEARCH_OUT / "cost_table_supplement.csv"
HIST_START, HIST_END = "2019-01-01", "2026-09-25"

PERIODS = {
    "pre": ("2019-01-02", "2021-12-31"),
    "dev": ("2022-01-03", "2024-09-30"),
    "val": ("2024-10-01", "2025-12-31"),
    "hold": ("2026-01-02", "2026-09-25"),
}
PERIOD_ORDER = ["pre", "dev", "val", "hold"]
SOXS_MIN_PRICE = 10.0          # bearish legs use SOXS only when its unadjusted prior close >= $10
COMMISSION_B = 0.0035          # cost case B, USD per share per side (ASSUMPTION, per the plan)
N_RTH = config.N_RTH


def period_of(dates) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates)).to_numpy()
    out = np.full(len(d), "", dtype=object)
    for k, (a, b) in PERIODS.items():
        m = (d >= np.datetime64(a)) & (d <= np.datetime64(b))
        out[m] = k
    return out


def shift1(x: np.ndarray) -> np.ndarray:
    out = np.full_like(np.asarray(x, float), np.nan)
    out[1:] = x[:-1]
    return out


def first_valid_row(a: np.ndarray) -> np.ndarray:
    ok = np.isfinite(a)
    idx = ok.argmax(axis=1)
    val = a[np.arange(a.shape[0]), idx]
    return np.where(ok.any(axis=1), val, np.nan)


def bar_time_ns(date: pd.Timestamp, bar: int, second_offset: float = 0.0) -> int:
    """UTC ns timestamp of the START of regular-session bar ``bar`` on ``date`` (+ offset seconds)."""
    t = pd.Timestamp(date).tz_localize(config.TZ) + pd.Timedelta(minutes=config.RTH_START_MIN + int(bar),
                                                                  seconds=second_offset)
    return int(t.value)


# --------------------------------------------------------------------------------------
# per-ticker data
# --------------------------------------------------------------------------------------
class TickerData:
    """Panel plus day-level arrays for one ticker (all aligned to the same trading calendar)."""

    def __init__(self, ticker: str, panel: sdata.Panel):
        self.tk = ticker
        self.p = panel
        dates = panel.dates
        self.dates = dates
        self.off = sfeat.official_close(ticker, dates, True).to_numpy(float)
        self.off_u = sfeat.official_close(ticker, dates, False).to_numpy(float)
        self.pc = shift1(self.off)
        self.pc_u = shift1(self.off_u)
        with np.errstate(all="ignore"):
            fac = np.nanmedian(panel.c_unadj / panel.c, axis=1)
        self.fac = np.where(np.isfinite(fac), fac, 1.0)          # unadjusted / adjusted, per day
        self.o0 = first_valid_row(np.where(panel.present, panel.o, np.nan))
        with np.errstate(all="ignore"):
            self.hi = np.nanmax(panel.h, axis=1)
            self.lo = np.nanmin(panel.l, axis=1)
        self.n_min = panel.n_min
        self.full = panel.n_min == N_RTH
        self.last_c = np.array([panel.c[i, panel.n_min[i] - 1] for i in range(len(dates))])
        tr = np.fmax(self.hi, self.pc) - np.fmin(self.lo, self.pc)
        atr = pd.Series(tr).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean().to_numpy()
        self.atr_prev = shift1(atr)                               # daily ATR14 through d-1
        self.range_pct = self.hi / self.lo - 1                    # regular-session range of day d
        self.period = period_of(dates)

    # ---- intraday derived arrays (computed on first use)
    @cached_property
    def vwap(self) -> np.ndarray:
        p = self.p
        vw = np.where(np.isnan(p.vw), p.c, p.vw)
        v = np.nan_to_num(p.v)
        cv = np.cumsum(v, axis=1)
        cpv = np.cumsum(np.nan_to_num(vw) * v, axis=1)
        with np.errstate(all="ignore"):
            out = np.where(cv > 0, cpv / cv, np.nan)
        out = np.where(np.isnan(out), p.c, out)
        return np.where(p.valid(), out, np.nan)

    @cached_property
    def vwap_sd(self) -> np.ndarray:
        p = self.p
        vw = np.where(np.isnan(p.vw), p.c, p.vw)
        v = np.nan_to_num(p.v)
        cv = np.cumsum(v, axis=1)
        cpv = np.cumsum(np.nan_to_num(vw) * v, axis=1)
        cp2v = np.cumsum(np.nan_to_num(vw) ** 2 * v, axis=1)
        with np.errstate(all="ignore"):
            m = np.where(cv > 0, cpv / cv, np.nan)
            var = np.where(cv > 0, cp2v / cv - m ** 2, np.nan)
        return np.sqrt(np.clip(var, 0, None))

    @cached_property
    def ret1(self) -> np.ndarray:
        """Simple 1-minute close-to-close returns within the session (bar 0 = NaN)."""
        c = self.p.c
        out = np.full_like(c, np.nan)
        out[:, 1:] = c[:, 1:] / c[:, :-1] - 1
        return out

    @cached_property
    def premarket(self) -> pd.DataFrame:
        return sfeat.premarket_summary(self.tk, self.dates)

    def minute_mean_prior(self, x: np.ndarray, w: int) -> np.ndarray:
        """Mean of x[k, j] over the previous w sessions k (per column j), NaN-aware."""
        n = x.shape[0]
        cs = np.nancumsum(np.nan_to_num(x), axis=0)
        cnt = np.cumsum(np.isfinite(x), axis=0)
        out = np.full_like(x, np.nan, dtype=float)
        for d in range(1, n):
            lo = d - w - 1
            s = cs[d - 1] - (cs[lo] if lo >= 0 else 0)
            c = cnt[d - 1] - (cnt[lo] if lo >= 0 else 0)
            with np.errstate(all="ignore"):
                out[d] = np.where(c >= max(3, w // 2), s / np.maximum(c, 1), np.nan)
        return out


class Context:
    """Lazy loader for TickerData on a common trading calendar (2019-01-02 .. 2026-09-25)."""

    def __init__(self, start: str = HIST_START, end: str = HIST_END):
        self.start, self.end = start, end
        cal = scal.load_calendar()
        self.cal = cal[(cal.index >= pd.Timestamp(start)) & (cal.index <= pd.Timestamp(end))]
        self._td: dict[str, TickerData] = {}

    def __getitem__(self, ticker: str) -> TickerData:
        if ticker not in self._td:
            p = sdata.build_panel(ticker, self.cal, self.start, self.end)
            self._td[ticker] = TickerData(ticker, p)
        return self._td[ticker]

    @property
    def dates(self) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.cal.index)


# --------------------------------------------------------------------------------------
# costs
# --------------------------------------------------------------------------------------
def combined_spread_table() -> tuple[pd.DataFrame, str]:
    """Microstructure table (2022-2026) plus the research supplement (2019-2021, SPY)."""
    micro, src = load_halfspread_table()
    parts, srcs = [micro], [src]
    if SUPPLEMENT_COST_FILE.exists():
        sup, s2 = load_halfspread_table(path=SUPPLEMENT_COST_FILE)
        have = set(zip(micro["ticker"], micro["year"]))
        sup = sup[[(t, y) not in have for t, y in zip(sup["ticker"], sup["year"])]]
        parts.append(sup)
        srcs.append(s2)
    t = pd.concat(parts, ignore_index=True)
    return t, " + ".join(srcs)


def cost_model(commission: float) -> CostModel:
    t, src = combined_spread_table()
    return CostModel(spread_table=t, spread_source=src, commission_per_share=commission)


# --------------------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------------------
def cluster_t(x: np.ndarray, groups: np.ndarray) -> tuple[float, float, int]:
    """Mean of x with a group-(day-)clustered standard error. Returns (mean, t, n_groups)."""
    x = np.asarray(x, float)
    ok = np.isfinite(x)
    x, g = x[ok], np.asarray(groups)[ok]
    n = len(x)
    if n < 2:
        return (float(x.mean()) if n else np.nan), np.nan, n
    mu = x.mean()
    df = pd.DataFrame({"g": g, "e": x - mu})
    s = df.groupby("g")["e"].sum().to_numpy()
    G = len(s)
    if G < 2:
        return float(mu), np.nan, G
    var = (s ** 2).sum() / n ** 2 * G / (G - 1)
    return float(mu), float(mu / np.sqrt(var)) if var > 0 else np.nan, G


def one_sided_p(t: float, dof: int) -> float:
    if not np.isfinite(t) or dof < 1:
        return 1.0
    return float(stats.t.sf(t, df=max(1, dof - 1)))


def bh_qvalues(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float)
    n = len(p)
    if n == 0:
        return p
    o = np.argsort(p)
    ranked = p[o] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.clip(q, 0, 1)
    return out


def quarter_share_positive(x: np.ndarray, dates) -> tuple[float, int]:
    s = pd.Series(np.asarray(x, float), index=pd.to_datetime(pd.Series(dates)).to_numpy())
    s = s[np.isfinite(s.to_numpy())]
    if s.empty:
        return np.nan, 0
    q = s.groupby(s.index.to_period("Q")).mean()
    return float((q > 0).mean()), int(len(q))


def max_drawdown_bps(x: np.ndarray) -> float:
    cum = np.cumsum(np.nan_to_num(np.asarray(x, float)))
    if cum.size == 0:
        return 0.0
    peak = np.maximum.accumulate(np.concatenate([[0.0], cum]))
    return float(np.max(peak[1:] - cum))


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)
