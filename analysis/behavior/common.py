"""Shared configuration and helpers for the SOXL/SOXS intraday behavior study.

All raw/cached data lives under data/behavior/ (gitignored); small result tables and
charts go to analysis/behavior/output/.
"""
from __future__ import annotations

import os
import random
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "behavior"
OUT = ROOT / "analysis" / "behavior" / "output"
PANEL = DATA / "panel"
for p in (DATA, OUT, PANEL):
    p.mkdir(parents=True, exist_ok=True)

BASE = "https://api.massive.com"
TZ = "America/New_York"

MAIN = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "TQQQ", "SQQQ", "QQQ"]
EXTRA = ["AVGO", "AMD", "MU"]            # only used to detect earnings dates
SECOND_TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "QQQ"]

START = "2022-01-01"
END = "2026-09-25"
WARMUP_START = "2021-11-01"              # history for trailing baselines / ATR warm-up
PERIODS = {
    "secondary": ("2022-01-01", "2024-09-30"),
    "primary": ("2024-10-01", "2026-09-25"),
}
# Leverage of each fund vs its natural driver (for reference only)
LEV = {"SOXL": 3, "SOXS": -3, "TQQQ": 3, "SQQQ": -3}

N_RTH = 390  # minutes 09:30..15:59 (bar start times)


def period_of(dates) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates)).dt.strftime("%Y-%m-%d").to_numpy()
    out = np.where(d <= PERIODS["secondary"][1], "secondary", "primary")
    out = np.where(d < PERIODS["secondary"][0], "warmup", out)
    return out


# ---------------------------------------------------------------- API client
_local = threading.local()


def _session() -> requests.Session:
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        _local.s = s
    return s


def api_get(url: str, max_tries: int = 8) -> dict:
    """GET with retry/backoff on 429/5xx/connection errors. Auth is injected by the proxy."""
    if not url.startswith("http"):
        url = BASE + url
    delay = 1.0
    last = None
    for _ in range(max_tries):
        try:
            r = _session().get(url, timeout=120)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay + random.random())
                delay = min(delay * 2, 60)
                continue
            raise RuntimeError(last)
        except (requests.ConnectionError, requests.Timeout) as e:  # transient
            last = repr(e)
            time.sleep(delay + random.random())
            delay = min(delay * 2, 60)
    raise RuntimeError(f"failed after retries: {url} :: {last}")


def fetch_aggs(ticker: str, mult: int, span: str, fr: str, to: str, adjusted: bool = True) -> pd.DataFrame:
    url = (f"{BASE}/v2/aggs/ticker/{ticker}/range/{mult}/{span}/{fr}/{to}"
           f"?adjusted={'true' if adjusted else 'false'}&sort=asc&limit=50000")
    rows = []
    while url:
        j = api_get(url)
        rows += j.get("results", []) or []
        url = j.get("next_url")
    df = pd.DataFrame(rows)
    if len(df):
        df = df.drop_duplicates("t").sort_values("t").reset_index(drop=True)
    return df


# ---------------------------------------------------------------- loaders
def load_daily(ticker: str, adjusted: bool = True) -> pd.DataFrame:
    f = DATA / ("daily_adj" if adjusted else "daily_unadj") / f"{ticker}.parquet"
    df = pd.read_parquet(f)
    df["date"] = pd.to_datetime(df.t, unit="ms", utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
    return df.set_index("date")


def load_minute(ticker: str) -> pd.DataFrame:
    files = sorted((DATA / "minute" / ticker).glob("*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    df = df.drop_duplicates("t").sort_values("t").reset_index(drop=True)
    ts = pd.to_datetime(df.t, unit="ms", utc=True).dt.tz_convert(TZ)
    df["date"] = ts.dt.strftime("%Y-%m-%d")
    df["mod"] = (ts.dt.hour * 60 + ts.dt.minute).astype(np.int16)  # minute of day, ET
    return df


def load_panel(ticker: str) -> dict:
    """RTH minute matrices built by 02_build_panel.py."""
    z = np.load(PANEL / f"{ticker}_rth.npz", allow_pickle=True)
    return {k: z[k] for k in z.files}


def sessions() -> pd.DataFrame:
    return pd.read_csv(PANEL / "sessions.csv", dtype={"date": str}).set_index("date")


def daily_table(ticker: str) -> pd.DataFrame:
    return pd.read_parquet(PANEL / f"{ticker}_daily.parquet")


def save_csv(df: pd.DataFrame, name: str, index: bool = True, float_format: str = "%.6g"):
    path = OUT / name
    df.to_csv(path, index=index, float_format=float_format)
    return path


def q(x, p):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return np.nanpercentile(x, p) if len(x) else np.nan


# ---------------------------------------------------------------- panel helpers
class Tk:
    """Convenience bundle: RTH matrices + daily table for one ticker, aligned to sessions()."""

    def __init__(self, t: str):
        self.t = t
        z = load_panel(t)
        self.dates = z["dates"].astype(str)
        for k in ("O", "H", "L", "C", "V", "VW", "N", "has", "valid"):
            setattr(self, k, z[k])
        self.D = daily_table(t)
        S = sessions()
        self.S = S.loc[self.dates]
        self.period = self.S.period.to_numpy()
        self.full = ~self.S.is_half.to_numpy()
        self.quarter = self.S.quarter.to_numpy()
        # 1-minute log returns; column 0 = open print -> close of 09:30 bar
        C = self.C
        r = np.full(C.shape, np.nan)
        r[:, 0] = np.log(C[:, 0] / self.O[:, 0])
        r[:, 1:] = np.log(C[:, 1:] / C[:, :-1])
        self.r1 = r

    def sel(self, period: str | None = None, full_only: bool = True) -> np.ndarray:
        m = np.isin(self.period, ["primary", "secondary"])
        if period:
            m &= self.period == period
        if full_only:
            m &= self.full
        return m


def block_sum(r: np.ndarray, h: int, start: int = 0) -> np.ndarray:
    """Non-overlapping h-minute sums of 1-min returns (days x floor((390-start)/h))."""
    n = (r.shape[1] - start) // h
    return r[:, start:start + n * h].reshape(r.shape[0], n, h).sum(axis=2)


def robust_ac(x: np.ndarray, y: np.ndarray):
    """Correlation of pairs (x_t, y_t) + heteroskedasticity-robust t-stat of the OLS slope y~x."""
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 30:
        return np.nan, np.nan, len(x)
    xc, yc = x - x.mean(), y - y.mean()
    rho = (xc * yc).sum() / np.sqrt((xc ** 2).sum() * (yc ** 2).sum())
    b = (xc * yc).sum() / (xc ** 2).sum()
    e = yc - b * xc
    se = np.sqrt(((xc ** 2) * (e ** 2)).sum()) / (xc ** 2).sum()
    return rho, b / se, len(x)


PERIOD_LABEL = {"secondary": "2022-01-03..2024-09-30", "primary": "2024-10-01..2026-09-25"}


def wilder(x: pd.Series, n: int = 14) -> pd.Series:
    x = x.astype(float)
    out = np.full(len(x), np.nan)
    v = x.to_numpy()
    ok = np.where(np.isfinite(v))[0]
    if len(ok) < n:
        return pd.Series(out, index=x.index)
    start = ok[n - 1]
    out[start] = np.nanmean(v[ok[:n]])
    for i in range(start + 1, len(v)):
        out[i] = out[i - 1] + ((v[i] if np.isfinite(v[i]) else out[i - 1]) - out[i - 1]) / n
    return pd.Series(out, index=x.index)


def daily_metrics(T: "Tk") -> pd.DataFrame:
    """Per-day metrics in percent (split-adjusted prices; prior close dividend-adjusted)."""
    D = T.D.copy()
    D["range_pct"] = 100 * (D.H - D.L) / D.O
    D["tr_pct"] = 100 * (np.maximum(D.H, D.prevC_adj) - np.minimum(D.L, D.prevC_adj)) / D.prevC_adj
    D["atr14_pct"] = wilder(D.tr_pct, 14)
    D["atr14_prev"] = D.atr14_pct.shift(1)              # known before today's open
    D["gap_pct"] = 100 * (D.O / D.prevC_adj - 1)
    D["oc_pct"] = 100 * (D.C / D.O - 1)
    D["cc_pct"] = 100 * (D.C / D.prevC_adj - 1)
    D["range_med20_prev"] = D.range_pct.shift(1).rolling(20, min_periods=15).median()
    D["full"] = ~D.is_half
    return D
