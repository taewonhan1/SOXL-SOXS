"""Shared helpers for the SOXL/SOXS intraday-dynamics study.

Conventions
-----------
* All raw/cached data lives under data/dynamics/ (gitignored).
* Small result tables and charts go to analysis/dynamics/output/.
* Timestamps from Massive are ms (aggregates) or ns (quotes/trades) since epoch UTC;
  they are converted to America/New_York (DST handled by pandas/zoneinfo).
* RTH = minute bars whose START time is in [09:30, 16:00) ET -> 390 bars per full day.
* "Price points": p[0] = open of the 09:30 bar, p[k] = close of bar k-1 (k=1..390), i.e. the
  price at 09:30:00, 09:31:00, ..., 16:00:00 (last trade in each minute).  Missing minutes
  (no trades) are forward-filled (flagged in `has`).
* Returns use split-ADJUSTED prices; cost conversions (ticks -> bps, $/share fees -> bps)
  use UNADJUSTED price levels via factor(date) = unadjusted_close / adjusted_close.
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

REPO = Path("/home/user/SOXL-SOXS")
ADIR = REPO / "analysis" / "dynamics"
OUT = ADIR / "output"
DATA = REPO / "data" / "dynamics"
for d in (OUT, DATA):
    d.mkdir(parents=True, exist_ok=True)

BASE = "https://api.massive.com"
TZ = "America/New_York"
TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "TQQQ", "QQQ"]

# windows
PRIMARY = ("2024-10-01", "2026-09-25")
IS_WIN = ("2024-10-01", "2025-09-30")
OOS_WIN = ("2025-10-01", "2026-09-25")
ROBUST = ("2022-01-01", "2024-09-30")
DL_START = "2021-11-01"  # warm-up for rolling estimates
DL_END = "2026-09-25"

NBARS = 390

if not os.environ.get("REQUESTS_CA_BUNDLE") and Path("/root/.ccr/ca-bundle.crt").exists():
    os.environ["REQUESTS_CA_BUNDLE"] = "/root/.ccr/ca-bundle.crt"

_tls = threading.local()


def _session() -> requests.Session:
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        _tls.s = s
    return s


def api_get(url: str, params: dict | None = None, max_tries: int = 10) -> dict:
    """GET with retry/backoff on 429/5xx/network errors. Auth is injected by the proxy."""
    if not url.startswith("http"):
        url = BASE + url
    last = None
    for i in range(max_tries):
        try:
            r = _session().get(url, params=params, timeout=180)
        except requests.RequestException as e:  # network hiccup
            last = repr(e)
            time.sleep(min(60, 2 ** i + random.random()))
            continue
        if r.status_code == 200:
            return r.json()
        last = f"HTTP {r.status_code}: {r.text[:200]}"
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(60, 2 ** i + random.random() * 2))
            continue
        raise RuntimeError(f"{url} {params} -> {last}")
    raise RuntimeError(f"giving up on {url} {params}: {last}")


def api_get_all(url: str, params: dict | None = None) -> list:
    """Follow next_url pagination; returns concatenated `results`."""
    out = []
    j = api_get(url, params)
    out.extend(j.get("results", []) or [])
    while j.get("next_url"):
        j = api_get(j["next_url"])
        out.extend(j.get("results", []) or [])
    return out


# ----------------------------------------------------------------------------------------
# loaders
# ----------------------------------------------------------------------------------------

def load_minute(ticker: str) -> pd.DataFrame:
    df = pd.read_parquet(DATA / "minute" / f"{ticker}_adj.parquet")
    return df


def load_daily(ticker: str, adjusted: bool = True) -> pd.DataFrame:
    tag = "adj" if adjusted else "unadj"
    df = pd.read_parquet(DATA / "daily" / f"{ticker}_{tag}.parquet")
    return df


def half_days() -> set:
    """Detect early-close sessions from QQQ minute volume: a session is a half-day if the
    13:00-16:00 ET volume is < 10% of the 09:30-13:00 volume (normal days ~ 50-80%)."""
    p = DATA / "half_days.csv"
    if p.exists():
        return set(pd.to_datetime(pd.read_csv(p)["date"]).dt.date)
    df = load_minute("QQQ")
    et = pd.to_datetime(df["t"], unit="ms", utc=True).dt.tz_convert(TZ)
    mins = et.dt.hour * 60 + et.dt.minute
    d = et.dt.date
    am = df["v"].where((mins >= 570) & (mins < 780), 0).groupby(d).sum()
    pm = df["v"].where((mins >= 780) & (mins < 960), 0).groupby(d).sum()
    ratio = pm / am.replace(0, np.nan)
    hd = sorted(ratio[ratio < 0.10].index)
    pd.DataFrame({"date": hd}).to_csv(p, index=False)
    return set(hd)


def build_panel(ticker: str, start: str = DL_START, end: str = DL_END, force: bool = False) -> dict:
    """Dense RTH panel [n_days, 390] of o,h,l,c,v,vw (adjusted), plus price points p[n_days, 391],
    has-trade mask, unadjusted factor per day, official adjusted prior close and close.
    Half-days are excluded. Cached as npz."""
    cache = DATA / "panels" / f"{ticker}.npz"
    cache.parent.mkdir(exist_ok=True)
    if cache.exists() and not force:
        z = np.load(cache, allow_pickle=True)
        P = {k: z[k] for k in z.files}
        P["dates"] = pd.to_datetime(P["dates"]).date
        return _slice(P, start, end)
    df = load_minute(ticker)
    et = pd.to_datetime(df["t"], unit="ms", utc=True).dt.tz_convert(TZ)
    mins = (et.dt.hour * 60 + et.dt.minute).to_numpy()
    rth = (mins >= 570) & (mins < 960)
    df = df.loc[rth].copy()
    df["date"] = et[rth].dt.date.to_numpy()
    df["m"] = mins[rth] - 570
    hd = half_days()
    df = df[~df["date"].isin(hd)]
    # trading days = days where QQQ has RTH bars (common calendar); use this ticker's own days
    dates = np.array(sorted(df["date"].unique()))
    di = {d: i for i, d in enumerate(dates)}
    n = len(dates)
    arr = {}
    rows = df["date"].map(di).to_numpy()
    cols = df["m"].to_numpy()
    for f in ["o", "h", "l", "c", "v", "vw"]:
        a = np.full((n, NBARS), np.nan)
        a[rows, cols] = df[f].to_numpy(dtype=float)
        arr[f] = a
    has = ~np.isnan(arr["c"])
    # forward fill within day; for leading missing bars back-fill with first open
    c = pd.DataFrame(arr["c"]).ffill(axis=1).to_numpy()
    o_first = pd.DataFrame(arr["o"]).bfill(axis=1).to_numpy()[:, 0]
    c = np.where(np.isnan(c), o_first[:, None], c)
    prev_c = np.concatenate([o_first[:, None], c[:, :-1]], axis=1)
    o = np.where(has, arr["o"], prev_c)
    h = np.where(has, arr["h"], prev_c)
    l = np.where(has, arr["l"], prev_c)
    v = np.where(has, arr["v"], 0.0)
    vw = np.where(has, arr["vw"], prev_c)
    p = np.concatenate([o[:, :1], c], axis=1)  # 391 price points
    # daily official closes (adjusted) and unadjusted factor
    dA = load_daily(ticker, True)
    dU = load_daily(ticker, False)
    dA["date"] = pd.to_datetime(dA["t"], unit="ms", utc=True).dt.tz_convert(TZ).dt.date
    dU["date"] = pd.to_datetime(dU["t"], unit="ms", utc=True).dt.tz_convert(TZ).dt.date
    dA = dA.set_index("date").sort_index()
    dU = dU.set_index("date").sort_index()
    fac = (dU["c"] / dA["c"]).reindex(dates).to_numpy()
    close_off = dA["c"].reindex(dates).to_numpy()
    prevclose = dA["c"].shift(1).reindex(dates).to_numpy()  # previous trading day's official close
    P = dict(dates=np.array(dates), o=o, h=h, l=l, c=c, v=v, vw=vw, p=p, has=has,
             fac=fac, close_off=close_off, prevclose=prevclose)
    np.savez_compressed(cache, **{k: (np.array([str(x) for x in val]) if k == "dates" else val)
                                  for k, val in P.items()})
    return _slice(P, start, end)


def _slice(P: dict, start: str, end: str) -> dict:
    d = pd.to_datetime(pd.Series(P["dates"]))
    m = ((d >= pd.Timestamp(start)) & (d <= pd.Timestamp(end))).to_numpy()
    return {k: (v[m] if isinstance(v, np.ndarray) and v.shape[:1] == m.shape else v) for k, v in P.items()}


def align(panels: dict) -> dict:
    """Restrict several panels to their common dates."""
    common = None
    for P in panels.values():
        s = set(P["dates"])
        common = s if common is None else common & s
    out = {}
    for k, P in panels.items():
        m = np.array([d in common for d in P["dates"]])
        out[k] = {kk: (vv[m] if isinstance(vv, np.ndarray) and vv.shape[:1] == m.shape else vv)
                  for kk, vv in P.items()}
    return out


def tod_bucket_labels(width: int = 30) -> list:
    labs = []
    for s in range(0, NBARS, width):
        a = 570 + s
        b = 570 + s + width
        labs.append(f"{a // 60:02d}:{a % 60:02d}-{b // 60:02d}:{b % 60:02d}")
    return labs


def in_window(dates, win) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates))
    return ((d >= pd.Timestamp(win[0])) & (d <= pd.Timestamp(win[1]))).to_numpy()


def save_csv(df: pd.DataFrame, name: str, index: bool = False) -> Path:
    p = OUT / name
    df.to_csv(p, index=index, float_format="%.6g")
    return p


# ----------------------------------------------------------------------------------------
# plotting (reference palette from the dataviz skill; colour follows the ticker)
# ----------------------------------------------------------------------------------------
COLORS = {"SOXL": "#2a78d6", "SOXS": "#eb6834", "SOXX": "#1baf7a", "SMH": "#eda100",
          "NVDA": "#e87ba4", "TQQQ": "#008300", "QQQ": "#4a3aa7", "extra": "#e34948"}
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.8,
        "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold", "legend.frameon": False,
        "figure.dpi": 110,
    })
    return plt
