"""Download, cache and load Massive aggregate bars and reference data.

Cache layout (all under ``config.DATA_DIR``, gitignored)::

    bars_1min/{adjusted|unadjusted}/{TICKER}/{YYYY-MM}.parquet   one file per calendar month
    bars_1day/{adjusted|unadjusted}/{TICKER}.parquet             full daily history
    reference/splits_{TICKER}.parquet, dividends_{TICKER}.parquet
    reference/manifest.json                                       what was downloaded when

Minute bars: ``t`` is the bar START in UTC epoch milliseconds (Massive convention); the bar covers
[t, t+60s). Bars exist only for minutes with at least one eligible trade (zero-trade minutes are
absent). The API returns 04:00-20:00 ET (extended hours) bars; we keep them all.

Incremental updates: months strictly before the current month that are already cached are
considered final; the latest cached month (and any missing month) is (re)downloaded.
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import api, config

BAR_COLS = ["t", "o", "h", "l", "c", "v", "vw", "n"]


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def _adj_dir(adjusted: bool) -> str:
    return "adjusted" if adjusted else "unadjusted"


def month_range(start: str, end: str) -> list[tuple[int, int]]:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    out = []
    y, m = s.year, s.month
    while (y, m) <= (e.year, e.month):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def bars_path(ticker: str, adjusted: bool, y: int, m: int) -> Path:
    return config.BARS_DIR / _adj_dir(adjusted) / ticker / f"{y:04d}-{m:02d}.parquet"


def _results_to_frame(results: list[dict]) -> pd.DataFrame:
    if not results:
        return pd.DataFrame({c: pd.Series(dtype="float64") for c in BAR_COLS}).astype({"t": "int64"})
    df = pd.DataFrame(results)
    for c in BAR_COLS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[BAR_COLS].copy()
    df["t"] = df["t"].astype("int64")
    for c in ["o", "h", "l", "c", "v", "vw"]:
        df[c] = df[c].astype("float64")
    df["n"] = pd.to_numeric(df["n"], errors="coerce").astype("float64")
    return df


def fetch_aggs(ticker: str, mult: int, timespan: str, start: str, end: str, adjusted: bool = True,
               limit: int = 50_000) -> pd.DataFrame:
    """Fetch aggregates [start, end] (dates, inclusive) following next_url pagination."""
    path = f"/v2/aggs/ticker/{ticker}/range/{mult}/{timespan}/{start}/{end}"
    params = {"adjusted": "true" if adjusted else "false", "sort": "asc", "limit": limit}
    res = api.get_all(path, params)
    df = _results_to_frame(res)
    return df.drop_duplicates("t").sort_values("t").reset_index(drop=True)


def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add ET timestamp, trading date and minute-of-day (DST-aware via America/New_York)."""
    ts = pd.to_datetime(df["t"], unit="ms", utc=True).dt.tz_convert(config.TZ)
    df = df.copy()
    df["ts"] = ts
    df["date"] = ts.dt.tz_localize(None).dt.normalize()
    df["mod"] = (ts.dt.hour * 60 + ts.dt.minute).astype("int16")
    return df


# --------------------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------------------
def _manifest_path() -> Path:
    return config.REF_DIR / "manifest.json"


def load_manifest() -> dict:
    p = _manifest_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def save_manifest(man: dict) -> None:
    config.REF_DIR.mkdir(parents=True, exist_ok=True)
    _manifest_path().write_text(json.dumps(man, indent=1, sort_keys=True))


# --------------------------------------------------------------------------------------
# minute bars
# --------------------------------------------------------------------------------------
def download_month(ticker: str, adjusted: bool, y: int, m: int, end: str = config.HISTORY_END) -> dict:
    first = date(y, m, 1)
    last = (date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1))
    last = min(last, pd.Timestamp(end).date())
    df = fetch_aggs(ticker, 1, "minute", first.isoformat(), last.isoformat(), adjusted)
    p = bars_path(ticker, adjusted, y, m)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return {"ticker": ticker, "adjusted": adjusted, "month": f"{y:04d}-{m:02d}", "rows": len(df),
            "last_t": int(df["t"].max()) if len(df) else None, "through": last.isoformat(),
            "downloaded_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"}


def plan_downloads(tickers=config.TICKERS, start=config.HISTORY_START, end=config.HISTORY_END,
                   adjusted_flags=(True, False), refresh_last: bool = True) -> list[tuple]:
    """Months to (re)download: missing ones, plus the last month of the range if it may be partial."""
    man = load_manifest()
    months = month_range(start, end)
    jobs = []
    for tk in tickers:
        for adj in adjusted_flags:
            for (y, m) in months:
                p = bars_path(tk, adj, y, m)
                key = f"{tk}|{_adj_dir(adj)}|{y:04d}-{m:02d}"
                rec = man.get(key)
                is_last = (y, m) == months[-1]
                complete = rec is not None and rec.get("through", "") >= min(
                    end, (date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1)).isoformat())
                if not p.exists() or not complete or (refresh_last and is_last and rec
                                                        and rec.get("through", "") < end):
                    jobs.append((tk, adj, y, m))
    return jobs


def download_minute_bars(tickers=config.TICKERS, start=config.HISTORY_START, end=config.HISTORY_END,
                         adjusted_flags=(True, False), max_workers: int | None = None) -> pd.DataFrame:
    jobs = plan_downloads(tickers, start, end, adjusted_flags)
    print(f"minute-bar jobs to run: {len(jobs)}")
    if not jobs:
        return pd.DataFrame()
    recs = api.parallel_map(lambda j: download_month(*j, end=end), jobs, max_workers, desc="1min")
    man = load_manifest()
    for r in recs:
        man[f"{r['ticker']}|{_adj_dir(r['adjusted'])}|{r['month']}"] = r
    save_manifest(man)
    return pd.DataFrame(recs)


def load_minute_bars(ticker: str, adjusted: bool = True, start: str | None = None, end: str | None = None,
                     rth_only: bool = False) -> pd.DataFrame:
    start = start or config.HISTORY_START
    end = end or config.HISTORY_END
    frames = []
    for (y, m) in month_range(start, end):
        p = bars_path(ticker, adjusted, y, m)
        if p.exists():
            frames.append(pd.read_parquet(p))
    if not frames:
        raise FileNotFoundError(f"no cached minute bars for {ticker} ({_adj_dir(adjusted)}); run scripts/download_data.py")
    df = pd.concat(frames, ignore_index=True)
    df = add_time_columns(df)
    df = df[(df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))]
    if rth_only:
        df = df[(df["mod"] >= config.RTH_START_MIN) & (df["mod"] < config.RTH_END_MIN)]
    return df.reset_index(drop=True)


# --------------------------------------------------------------------------------------
# daily bars and reference data
# --------------------------------------------------------------------------------------
def daily_path(ticker: str, adjusted: bool) -> Path:
    return config.DAILY_DIR / _adj_dir(adjusted) / f"{ticker}.parquet"


def download_daily(tickers=config.TICKERS, start: str = "2010-01-01", end: str = config.HISTORY_END) -> None:
    def _one(job):
        tk, adj = job
        df = fetch_aggs(tk, 1, "day", start, end, adj)
        df = add_time_columns(df)
        p = daily_path(tk, adj)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p, index=False)
        return len(df)
    api.parallel_map(_one, [(tk, adj) for tk in tickers for adj in (True, False)], desc="1day")


def load_daily(ticker: str, adjusted: bool = True) -> pd.DataFrame:
    df = pd.read_parquet(daily_path(ticker, adjusted))
    return df.set_index("date").sort_index()


def download_reference(tickers=config.TICKERS) -> None:
    config.REF_DIR.mkdir(parents=True, exist_ok=True)
    for tk in tickers:
        sp = pd.DataFrame(api.get_all("/v3/reference/splits", {"ticker": tk, "limit": 1000}))
        sp.to_parquet(config.REF_DIR / f"splits_{tk}.parquet", index=False)
        dv = pd.DataFrame(api.get_all("/v3/reference/dividends", {"ticker": tk, "limit": 1000}))
        dv.to_parquet(config.REF_DIR / f"dividends_{tk}.parquet", index=False)
        time.sleep(0.1)


def load_splits(ticker: str) -> pd.DataFrame:
    p = config.REF_DIR / f"splits_{ticker}.parquet"
    if not p.exists():
        return pd.DataFrame(columns=["execution_date", "split_from", "split_to", "ticker"])
    df = pd.read_parquet(p)
    if len(df):
        df["execution_date"] = pd.to_datetime(df["execution_date"])
        df = df.sort_values("execution_date").reset_index(drop=True)
    return df


def load_dividends(ticker: str) -> pd.DataFrame:
    p = config.REF_DIR / f"dividends_{ticker}.parquet"
    if not p.exists():
        return pd.DataFrame(columns=["ex_dividend_date", "cash_amount"])
    df = pd.read_parquet(p)
    if len(df) and "ex_dividend_date" in df:
        df["ex_dividend_date"] = pd.to_datetime(df["ex_dividend_date"])
    return df


# --------------------------------------------------------------------------------------
# regular-session panel: 2-D arrays [n_days, 390]
# --------------------------------------------------------------------------------------
class Panel:
    """Regular-session (09:30-15:59 ET) 1-minute bars as dense 2-D arrays.

    Attributes are numpy arrays of shape (n_days, 390): ``o h l c v vw n`` (adjusted prices),
    ``c_unadj`` / ``o_unadj`` (unadjusted, for per-share cost conversion), ``present`` (bool: a bar
    existed; missing minutes are forward-filled with o=h=l=c=previous close, v=0).
    ``dates`` is a DatetimeIndex; ``n_min`` gives the number of regular minutes per day (390, or 210
    on 13:00 early-close days); columns >= n_min are NaN.
    """

    FIELDS = ("o", "h", "l", "c", "v", "vw", "n")

    def __init__(self, ticker: str, dates: pd.DatetimeIndex, arrays: dict, n_min: np.ndarray):
        self.ticker = ticker
        self.dates = dates
        self.n_min = n_min
        for k, v in arrays.items():
            setattr(self, k, v)

    @property
    def shape(self):
        return self.c.shape

    def valid(self) -> np.ndarray:
        """Mask of columns inside each day's session (handles half-days)."""
        j = np.arange(self.c.shape[1])[None, :]
        return j < self.n_min[:, None]

    def subset(self, start=None, end=None) -> "Panel":
        m = np.ones(len(self.dates), bool)
        if start is not None:
            m &= self.dates >= pd.Timestamp(start)
        if end is not None:
            m &= self.dates <= pd.Timestamp(end)
        arrays = {k: getattr(self, k)[m] for k in list(self.FIELDS) + ["c_unadj", "o_unadj", "present"]}
        return Panel(self.ticker, self.dates[m], arrays, self.n_min[m])


def _pivot(df: pd.DataFrame, col: str, dates: pd.DatetimeIndex) -> np.ndarray:
    j = (df["mod"].to_numpy() - config.RTH_START_MIN).astype(int)
    di = dates.get_indexer(df["date"])
    out = np.full((len(dates), config.N_RTH), np.nan)
    ok = (di >= 0) & (j >= 0) & (j < config.N_RTH)
    out[di[ok], j[ok]] = df[col].to_numpy()[ok]
    return out


def build_panel(ticker: str, calendar: pd.DataFrame, start: str | None = None, end: str | None = None,
                use_cache: bool = True) -> Panel:
    """Dense regular-session panel on the trading calendar (``calendar`` from soxlab.calendar)."""
    start = start or config.HISTORY_START
    end = end or config.HISTORY_END
    cache = config.CACHE_DIR / f"panel_{ticker}_{start}_{end}.npz"
    cal = calendar[(calendar.index >= pd.Timestamp(start)) & (calendar.index <= pd.Timestamp(end))]
    dates = pd.DatetimeIndex(cal.index)
    n_min = cal["n_rth_minutes"].to_numpy().astype(int)
    if use_cache and cache.exists():
        z = np.load(cache, allow_pickle=False)
        if len(z["dates"]) == len(dates) and (z["dates"] == dates.values.astype("int64")).all():
            arrays = {k: z[k] for k in z.files if k not in ("dates", "n_min")}
            return Panel(ticker, dates, arrays, n_min)
    adj = load_minute_bars(ticker, True, start, end, rth_only=True)
    una = load_minute_bars(ticker, False, start, end, rth_only=True)
    arrays = {k: _pivot(adj, k, dates) for k in Panel.FIELDS}
    c_unadj = _pivot(una, "c", dates)
    o_unadj = _pivot(una, "o", dates)
    present = ~np.isnan(arrays["c"])
    # mask minutes beyond the day's session end (half-days)
    j = np.arange(config.N_RTH)[None, :]
    inside = j < n_min[:, None]
    present &= inside
    # Causal forward-fill of missing minutes with the previous close (v = 0). If the session's
    # first bar(s) are missing they stay NaN until the first real bar (no back-filling = no look-ahead).
    c = pd.DataFrame(arrays["c"]).ffill(axis=1).to_numpy()
    cu = pd.DataFrame(c_unadj).ffill(axis=1).to_numpy()
    nan_col = np.full((len(dates), 1), np.nan)
    prev_c = np.concatenate([nan_col, c[:, :-1]], axis=1)
    prev_cu = np.concatenate([nan_col, cu[:, :-1]], axis=1)
    for k in ("o", "h", "l"):
        arrays[k] = np.where(present, arrays[k], prev_c)
    arrays["c"] = np.where(present, arrays["c"], prev_c)
    arrays["vw"] = np.where(present, arrays["vw"], arrays["c"])
    arrays["v"] = np.where(present, arrays["v"], 0.0)
    arrays["n"] = np.where(present, arrays["n"], 0.0)
    arrays["c_unadj"] = np.where(present, c_unadj, prev_cu)
    arrays["o_unadj"] = np.where(present, o_unadj, prev_cu)
    for k in list(Panel.FIELDS) + ["c_unadj", "o_unadj"]:
        arrays[k] = np.where(inside, arrays[k], np.nan)
    arrays["present"] = present
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, dates=dates.values.astype("int64"), n_min=n_min, **arrays)
    return Panel(ticker, dates, arrays, n_min)
