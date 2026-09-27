"""Shared helpers for the SOXL/SOXS microstructure study (Massive API, formerly Polygon.io).

Authentication is injected by the network proxy; no apiKey parameter is added here.
All raw/cached data goes under /home/user/SOXL-SOXS/data/microstructure/ (gitignored).
"""
from __future__ import annotations

import os
import random
import threading
import time
from pathlib import Path

import numpy as np
import orjson
import pandas as pd
import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

BASE = "https://api.massive.com"
REPO = Path("/home/user/SOXL-SOXS")
SCRIPT_DIR = REPO / "analysis" / "microstructure"
OUT = SCRIPT_DIR / "output"
DATA = REPO / "data" / "microstructure"
for _d in (OUT, DATA):
    _d.mkdir(parents=True, exist_ok=True)

ET = "America/New_York"
TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "TQQQ", "SQQQ", "QQQ", "SPY"]
COST_TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "TQQQ", "SQQQ", "QQQ"]

# ---------------------------------------------------------------- HTTP layer
_MAX_CONC = int(os.environ.get("MS_MAX_CONC", "6"))
_sem = threading.BoundedSemaphore(_MAX_CONC)
_local = threading.local()
_stats = {"requests": 0, "retries": 0, "bytes": 0}
_stats_lock = threading.Lock()


def _session() -> requests.Session:
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers["Accept-Encoding"] = "gzip"
        _local.s = s
    return s


def get_json(url: str, params: dict | None = None, max_tries: int = 10) -> dict:
    """GET with retry/backoff on 429/5xx/network errors. Global concurrency cap."""
    if not url.startswith("http"):
        url = BASE + url
    delay = 1.0
    for attempt in range(max_tries):
        try:
            with _sem:
                r = _session().get(url, params=params, timeout=180)
            if r.status_code == 200:
                with _stats_lock:
                    _stats["requests"] += 1
                    _stats["bytes"] += len(r.content)
                return orjson.loads(r.content)
            if r.status_code in (429, 500, 502, 503, 504, 520, 522, 524):
                with _stats_lock:
                    _stats["retries"] += 1
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.replace(".", "").isdigit() else delay
                time.sleep(wait + random.random())
                delay = min(delay * 2, 60)
                continue
            raise RuntimeError(f"HTTP {r.status_code} for {url} {params}: {r.text[:300]}")
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as e:
            with _stats_lock:
                _stats["retries"] += 1
            time.sleep(delay + random.random())
            delay = min(delay * 2, 60)
    raise RuntimeError(f"giving up on {url} {params}")


def iter_pages(url: str, params: dict | None = None):
    """Yield the 'results' list of every page, following next_url."""
    j = get_json(url, params)
    while True:
        res = j.get("results") or []
        if res:
            yield res
        nxt = j.get("next_url")
        if not nxt:
            return
        j = get_json(nxt)


def http_stats() -> dict:
    with _stats_lock:
        return dict(_stats)


# ---------------------------------------------------------------- time helpers
def et_to_utc_ns(day: str, hhmm: str) -> int:
    """'2026-09-25', '09:30' (or '09:30:00') ET -> ns since epoch UTC (DST aware)."""
    if len(hhmm) == 5:
        hhmm = hhmm + ":00"
    ts = pd.Timestamp(f"{day} {hhmm}").tz_localize(ET)
    return int(ts.value)


def ns_to_iso(ns: int) -> str:
    """ns since epoch -> RFC3339 UTC with ns precision (as accepted by the API)."""
    ts = pd.Timestamp(ns, unit="ns", tz="UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ns % 1_000_000_000:09d}Z"


def hhmm_to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")[:2]
    return int(h) * 60 + int(m)


def min_to_hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


# ---------------------------------------------------------------- fetchers
QUOTE_COLS = ["t", "bid", "ask", "bsz", "asz", "bex", "aex", "cond"]
TRADE_COLS = ["t", "price", "size", "ex", "cond", "trf"]


def fetch_quotes(ticker: str, start_ns: int, end_ns: int) -> pd.DataFrame:
    """NBBO quotes in [start_ns, end_ns). Returns compact columnar frame."""
    params = {
        "timestamp.gte": ns_to_iso(start_ns),
        "timestamp.lt": ns_to_iso(end_ns),
        "limit": 50000,
        "sort": "timestamp",
        "order": "asc",
    }
    chunks = []
    for res in iter_pages(f"/v3/quotes/{ticker}", params):
        n = len(res)
        t = np.fromiter((q.get("sip_timestamp", 0) for q in res), dtype=np.int64, count=n)
        bid = np.fromiter((q.get("bid_price", np.nan) or np.nan for q in res), dtype=np.float64, count=n)
        ask = np.fromiter((q.get("ask_price", np.nan) or np.nan for q in res), dtype=np.float64, count=n)
        bsz = np.fromiter((q.get("bid_size", 0) or 0 for q in res), dtype=np.float64, count=n)
        asz = np.fromiter((q.get("ask_size", 0) or 0 for q in res), dtype=np.float64, count=n)
        bex = np.fromiter((q.get("bid_exchange", 0) or 0 for q in res), dtype=np.int16, count=n)
        aex = np.fromiter((q.get("ask_exchange", 0) or 0 for q in res), dtype=np.int16, count=n)
        # first quote condition code (1 = regular two-sided open, 43 = LULD pause, ...)
        cond = np.fromiter(((q.get("conditions") or [0])[0] for q in res), dtype=np.int16, count=n)
        chunks.append(pd.DataFrame({"t": t, "bid": bid, "ask": ask, "bsz": bsz, "asz": asz,
                                    "bex": bex, "aex": aex, "cond": cond}))
    if not chunks:
        return pd.DataFrame({c: pd.Series(dtype="float64") for c in QUOTE_COLS})
    return pd.concat(chunks, ignore_index=True)


def _cond_code(conds) -> int:
    """Pack up to 7 condition codes into one int64 (8 bits each; codes < 256)."""
    if not conds:
        return 0
    v = 0
    for i, c in enumerate(sorted(conds)[:7]):
        v |= (int(c) & 0xFF) << (8 * i)
    return v


def unpack_conds(v: int) -> list[int]:
    out = []
    while v:
        out.append(v & 0xFF)
        v >>= 8
    return out


def fetch_trades(ticker: str, start_ns: int, end_ns: int) -> pd.DataFrame:
    params = {
        "timestamp.gte": ns_to_iso(start_ns),
        "timestamp.lt": ns_to_iso(end_ns),
        "limit": 50000,
        "sort": "timestamp",
        "order": "asc",
    }
    chunks = []
    for res in iter_pages(f"/v3/trades/{ticker}", params):
        n = len(res)
        t = np.fromiter((q.get("sip_timestamp", 0) for q in res), dtype=np.int64, count=n)
        price = np.fromiter((q.get("price", np.nan) for q in res), dtype=np.float64, count=n)
        size = np.fromiter((float(q.get("decimal_size") or q.get("size") or 0) for q in res), dtype=np.float64, count=n)
        ex = np.fromiter((q.get("exchange", 0) or 0 for q in res), dtype=np.int16, count=n)
        cond = np.fromiter((_cond_code(q.get("conditions")) for q in res), dtype=np.int64, count=n)
        trf = np.fromiter((q.get("trf_id", 0) or 0 for q in res), dtype=np.int16, count=n)
        chunks.append(pd.DataFrame({"t": t, "price": price, "size": size, "ex": ex, "cond": cond, "trf": trf}))
    if not chunks:
        return pd.DataFrame({c: pd.Series(dtype="float64") for c in TRADE_COLS})
    return pd.concat(chunks, ignore_index=True)


def fetch_aggs(ticker: str, mult: int, span: str, frm: str, to: str, adjusted: bool) -> pd.DataFrame:
    url = f"/v2/aggs/ticker/{ticker}/range/{mult}/{span}/{frm}/{to}"
    params = {"adjusted": "true" if adjusted else "false", "sort": "asc", "limit": 50000}
    rows = []
    for res in iter_pages(url, params):
        rows.extend(res)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df


def has_cond(cond_packed: np.ndarray, code: int) -> np.ndarray:
    c = np.asarray(cond_packed, dtype=np.int64)
    out = np.zeros(len(c), dtype=bool)
    for i in range(7):
        out |= ((c >> (8 * i)) & 0xFF) == code
    return out


# ---------------------------------------------------------------- sample design
# Stress days were chosen from the data (script 01 bars): largest |close-to-close| moves / daily ranges of
# SOXL and NVDA between 2025-03-25 and 2026-09-25, plus the April-2025 days named in the brief.
# 2025-11-20 and 2026-08-27 are the first sessions after NVDA quarterly filings accepted 2025-11-19 21:36 UTC and
# 2026-08-26 20:36 UTC (/vX/reference/financials acceptance_datetime).
_STRESS_ORIG = ["2025-04-03", "2025-04-04", "2025-04-07", "2025-04-09",
                "2026-02-06", "2026-06-05", "2026-06-09", "2026-08-27"]
_STRESS_EXTRA = ["2025-11-20"]  # added after the first design; not used for the normal-day exclusion (keeps normal days fixed)
STRESS_DAYS = sorted(_STRESS_ORIG + _STRESS_EXTRA)
RECENT_DAYS = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25"]
PERIODS = [("2022-01-01", "2022-12-31", 5), ("2023-01-01", "2023-12-31", 5),
           ("2024-01-01", "2024-12-31", 5), ("2025-01-01", "2025-09-25", 4),
           ("2025-09-26", "2026-09-18", 13)]


def trading_days_and_halfdays():
    m = pd.read_parquet(DATA / "bars" / "SPY_min_raw.parquet", columns=["t"])
    et = pd.to_datetime(m["t"], unit="ms", utc=True).dt.tz_convert(ET)
    mm = et.dt.hour * 60 + et.dt.minute
    d = et.dt.strftime("%Y-%m-%d")
    rth = (mm >= 570) & (mm < 960)
    last = mm[rth].groupby(d[rth]).max()
    days = sorted(last.index)
    half = sorted(last[last < 900].index)
    return days, half


def sample_days() -> pd.DataFrame:
    """Deterministic, evenly spaced (by trading-day index) normal days per period + recent + stress."""
    days, half = trading_days_and_halfdays()
    excl = set(half) | set(_STRESS_ORIG) | set(RECENT_DAYS)
    rows = []
    for lo, hi, k in PERIODS:
        cand = [x for x in days if lo <= x <= hi and x not in excl]
        n = len(cand)
        for i in range(k):
            rows.append({"day": cand[int((i + 0.5) * n / k)], "category": "normal", "period": f"{lo}..{hi}", "idx": i})
    for x in RECENT_DAYS:
        rows.append({"day": x, "category": "recent", "period": "last5", "idx": 0})
    for x in STRESS_DAYS:
        rows.append({"day": x, "category": "stress", "period": "stress", "idx": 0})
    df = pd.DataFrame(rows)
    df["year"] = df["day"].str[:4].astype(int)
    # phase 1 = quick first pass (recent days + ~2 normal days per period) for an early cost table
    df["phase"] = 2
    df.loc[df.category == "recent", "phase"] = 1
    df.loc[(df.category == "normal") & (df.idx.isin([1, 3])) & (df.period != PERIODS[-1][0] + ".." + PERIODS[-1][1]), "phase"] = 1
    df.loc[(df.category == "normal") & (df.idx.isin([2, 6, 10])) & (df.period == PERIODS[-1][0] + ".." + PERIODS[-1][1]), "phase"] = 1
    return df.sort_values("day").reset_index(drop=True)


def window_plan(day: str) -> list[dict]:
    """Window schedule (minutes after ET midnight). Same schedule for every ticker on a given day.

    rth   : one 10-min quote window per 30-min RTH bucket at a random 5-min-aligned offset (0..20);
            trades are taken from the first 5 minutes so that the mid 5 min later is inside the quote window.
    open5 : fixed 09:30-09:35 quotes (trades 09:29:30-09:35, to catch the opening auction print)
    close5: fixed 15:55-16:00 quotes and trades
    cauc  : fixed 16:00-16:01 trades only (closing auction print)
    pre/post: one 5-min window per extended-hours stratum at a random 5-min-aligned offset
    """
    rng = np.random.default_rng(int(day.replace("-", "")))
    W = []
    for b in range(13):
        bs = 570 + 30 * b
        off = int(rng.choice([0, 5, 10, 15, 20]))
        W.append(dict(kind="rth", stratum=(bs, bs + 30), q0=bs + off, q1=bs + off + 10, t0=bs + off, t1=bs + off + 5))
    W.append(dict(kind="open5", stratum=(570, 575), q0=570, q1=575, t0=569.5, t1=575))
    W.append(dict(kind="close5", stratum=(955, 960), q0=955, q1=960, t0=955, t1=960))
    W.append(dict(kind="cauc", stratum=(960, 961), q0=None, q1=None, t0=960, t1=961))
    for kind, strata in (("pre", [(240, 420), (420, 480), (480, 540), (540, 570)]),
                         ("post", [(960, 1020), (1020, 1080), (1080, 1200)])):
        for a, b_ in strata:
            n = (b_ - a) // 5
            off = int(rng.integers(0, n)) * 5
            W.append(dict(kind=kind, stratum=(a, b_), q0=a + off, q1=a + off + 5, t0=a + off, t1=a + off + 5))
    for i, w in enumerate(W):
        w["wid"] = i
    return W


# ---------------------------------------------------------------- chart style (dataviz skill: focus + context)
# SOXL/SOXS use validated categorical slots 1-2 (#2a78d6 blue, #eb6834 orange; validator: all checks pass, light).
# The 7 comparison tickers are context lines in one gray with direct labels (no 9-hue categorical palette).
FOCUS_COLORS = {"SOXL": "#2a78d6", "SOXS": "#eb6834"}
CONTEXT_GRAY = "#a3a29c"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3de"


def style_ax(ax):
    ax.grid(True, color=GRID, lw=0.6, which="major")
    ax.grid(False, which="minor")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9b8b2")
        ax.spines[s].set_linewidth(0.6)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=8, width=0.6)
    ax.yaxis.label.set_color(TEXT_SECONDARY)
    ax.xaxis.label.set_color(TEXT_SECONDARY)
    ax.title.set_color("#0b0b0b")


def focus_lines(ax, series: dict, label_ends: bool = True, logy: bool = False):
    """series: {ticker: (x, y)}. Peers first in gray (direct-labelled), focus tickers on top."""
    from matplotlib.lines import Line2D
    ends = []
    for T, (x, y) in series.items():
        if T in FOCUS_COLORS:
            continue
        ax.plot(x, y, color=CONTEXT_GRAY, lw=0.9, zorder=2)
        if label_ends and len(x):
            ends.append((T, x[-1], y[-1], TEXT_SECONDARY))
    for T in ("SOXL", "SOXS"):
        if T in series:
            x, y = series[T]
            ax.plot(x, y, color=FOCUS_COLORS[T], lw=2.0, zorder=3)
            if label_ends and len(x):
                ends.append((T, x[-1], y[-1], FOCUS_COLORS[T]))
    # simple de-overlap of end labels (in axis-fraction space)
    if label_ends and ends:
        ymin, ymax = ax.get_ylim()
        def frac(v):
            if logy:
                return (np.log10(max(v, 1e-12)) - np.log10(ymin)) / (np.log10(ymax) - np.log10(ymin))
            return (v - ymin) / (ymax - ymin)
        ends.sort(key=lambda e: frac(e[2]))
        placed = []
        for T, xe, ye, c in ends:
            f = frac(ye)
            if placed and f - placed[-1] < 0.035:
                f = placed[-1] + 0.035
            placed.append(f)
            ax.annotate(T, xy=(xe, ye), xycoords="data", xytext=(1.005, f), textcoords="axes fraction",
                        fontsize=7.5, color=c if T in FOCUS_COLORS else TEXT_SECONDARY, va="center",
                        fontweight="bold" if T in FOCUS_COLORS else "normal",
                        arrowprops=dict(arrowstyle="-", color="#d0cfca", lw=0.5))
    if logy:
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: f"{v:g}" if f"{v:g}".lstrip("0.")[:1] in ("2", "5") else ""))
    handles = [Line2D([0], [0], color=FOCUS_COLORS["SOXL"], lw=2, label="SOXL"),
               Line2D([0], [0], color=FOCUS_COLORS["SOXS"], lw=2, label="SOXS"),
               Line2D([0], [0], color=CONTEXT_GRAY, lw=0.9, label="comparison tickers (labelled at right)")]
    ax.legend(handles=handles, fontsize=7.5, frameon=False, loc="best")
    style_ax(ax)
