"""Shared helpers for the SOXL/SOXS liquidity study.

- Massive (formerly Polygon.io) REST client with retry/backoff + next_url pagination.
  Authentication is injected by the network proxy, so no apiKey is ever added here.
- Paths: raw/cached data -> <repo>/data/liquidity (gitignored);
         small result tables/charts -> <repo>/analysis/liquidity/output
- Ticker metadata (leverage, round lot) and time helpers (America/New_York).
"""
from __future__ import annotations

import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

try:
    import orjson as _json

    def _loads(b: bytes):
        return _json.loads(b)
except Exception:  # pragma: no cover - fallback
    import json as _json

    def _loads(b: bytes):
        return _json.loads(b)

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

BASE = "https://api.massive.com"
REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data" / "liquidity"
OUT = Path(__file__).resolve().parent / "output"
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

ET = "America/New_York"

# leverage = |daily target multiple|; round_lot from /v3/reference/tickers (2026-09-27)
TICKERS = {
    "SOXL": dict(lev=3, side=+1, underlying="semis", round_lot=100),
    "SOXS": dict(lev=3, side=-1, underlying="semis", round_lot=100),
    "SOXX": dict(lev=1, side=+1, underlying="semis", round_lot=40),
    "SMH": dict(lev=1, side=+1, underlying="semis", round_lot=40),
    "NVDA": dict(lev=1, side=+1, underlying="NVDA", round_lot=100),
    "TQQQ": dict(lev=3, side=+1, underlying="Nasdaq-100", round_lot=100),
    "SQQQ": dict(lev=3, side=-1, underlying="Nasdaq-100", round_lot=100),
    "QQQ": dict(lev=1, side=+1, underlying="Nasdaq-100", round_lot=40),
    "SPY": dict(lev=1, side=+1, underlying="S&P 500", round_lot=40),
    "USD": dict(lev=2, side=+1, underlying="semis", round_lot=100),
    "NVDL": dict(lev=2, side=+1, underlying="NVDA", round_lot=100),
}
CORE = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "TQQQ", "SQQQ", "QQQ", "SPY"]
OPTIONAL = ["USD", "NVDL"]
ALL = CORE + OPTIONAL

_session: requests.Session | None = None


def session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        ad = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=8)
        s.mount("https://", ad)
        s.headers.update({"Accept-Encoding": "gzip, deflate"})
        _session = s
    return _session


def get_json(url: str, params: dict | None = None, max_retries: int = 10) -> dict:
    """GET with exponential backoff on 429/5xx/network errors."""
    if not url.startswith("http"):
        url = BASE + url
    last = None
    for attempt in range(max_retries):
        try:
            r = session().get(url, params=params, timeout=180)
        except requests.RequestException as e:  # network hiccup
            last = repr(e)
            time.sleep(min(60, 2 ** attempt) + random.random())
            continue
        if r.status_code == 200:
            return _loads(r.content)
        if r.status_code in (429, 500, 502, 503, 504):
            last = f"HTTP {r.status_code}"
            ra = r.headers.get("Retry-After")
            wait = float(ra) if ra and ra.replace(".", "", 1).isdigit() else min(60, 2 ** attempt)
            time.sleep(wait + random.random())
            continue
        raise RuntimeError(f"HTTP {r.status_code} for {url} {params}: {r.text[:300]}")
    raise RuntimeError(f"max retries exceeded for {url} {params}: {last}")


def paginate(path: str, params: dict | None = None):
    """Yield the `results` list of each page, following next_url."""
    j = get_json(path, params)
    yield j.get("results") or []
    while j.get("next_url"):
        j = get_json(j["next_url"])
        yield j.get("results") or []


def aggs(ticker: str, mult: int, timespan: str, start: str, end: str, adjusted: bool = True) -> pd.DataFrame:
    rows = []
    for page in paginate(
        f"/v2/aggs/ticker/{ticker}/range/{mult}/{timespan}/{start}/{end}",
        {"adjusted": "true" if adjusted else "false", "sort": "asc", "limit": 50000},
    ):
        rows.extend(page)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["ts_utc"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["ts_et"] = df["ts_utc"].dt.tz_convert(ET)
    return df


def et_to_utc_iso(day: str, hhmm: str) -> str:
    """'2026-09-25','09:30' (America/New_York) -> '2026-09-25T13:30:00Z' (DST aware)."""
    ts = pd.Timestamp(f"{day} {hhmm}", tz=ET).tz_convert("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def et_to_ns(day: str, hhmm: str) -> int:
    return int(pd.Timestamp(f"{day} {hhmm}", tz=ET).tz_convert("UTC").value)


def wquantile(values: np.ndarray, weights: np.ndarray, qs) -> np.ndarray:
    """Weighted quantiles (weights = time durations)."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    m = np.isfinite(values) & (weights > 0)
    values, weights = values[m], weights[m]
    if values.size == 0:
        return np.full(len(np.atleast_1d(qs)), np.nan)
    o = np.argsort(values)
    v, w = values[o], weights[o]
    cw = np.cumsum(w)
    cw /= cw[-1]
    return np.array([v[min(np.searchsorted(cw, q, side="left"), len(v) - 1)] for q in np.atleast_1d(qs)])
