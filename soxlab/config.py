"""Central configuration: paths, universe, session constants and cost assumptions.

Every number here that is an *assumption* (not pulled from data) is labelled as such.
"""
from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("SOXLAB_DATA_DIR", REPO_ROOT / "data" / "soxlab"))
OUTPUT_DIR = Path(os.environ.get("SOXLAB_OUTPUT_DIR", REPO_ROOT / "analysis" / "backtests" / "output"))
MICRO_COST_FILE = REPO_ROOT / "analysis" / "microstructure" / "output" / "cost_model_halfspread.csv"

BARS_DIR = DATA_DIR / "bars_1min"          # bars_1min/{adjusted|unadjusted}/{TICKER}/{YYYY-MM}.parquet
DAILY_DIR = DATA_DIR / "bars_1day"         # bars_1day/{adjusted|unadjusted}/{TICKER}.parquet
REF_DIR = DATA_DIR / "reference"           # splits, calendar, conditions, probe raw json
NBBO_DIR = DATA_DIR / "nbbo_sample"        # light NBBO sample used for the fallback spread estimate
CACHE_DIR = DATA_DIR / "cache"             # derived panels / features

# --------------------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------------------
API_BASE = "https://api.massive.com"
# Auth is injected by the network proxy - never add an apiKey parameter.
MAX_CONCURRENCY = int(os.environ.get("SOXLAB_MAX_CONCURRENCY", "4"))  # hard cap 6 (shared API)

# --------------------------------------------------------------------------------------
# Universe and history
# --------------------------------------------------------------------------------------
TICKERS = ["SOXL", "SOXS", "SOXX", "SMH", "NVDA", "QQQ", "TQQQ", "SQQQ"]
TRADED = ["SOXL", "SOXS"]
DRIVERS = ["SOXX", "NVDA", "QQQ", "SMH"]
HISTORY_START = "2019-01-01"
HISTORY_END = "2026-09-25"

# Nominal daily leverage (from the funds' names: "Daily ... Bull 3X" / "Bear 3X").
LEVERAGE = {"SOXL": 3.0, "SOXS": -3.0, "TQQQ": 3.0, "SQQQ": -3.0,
            "SOXX": 1.0, "SMH": 1.0, "NVDA": 1.0, "QQQ": 1.0}
# Unleveraged proxy for the underlying index of each leveraged fund (ASSUMPTION: SOXX used as the
# tradeable proxy of the semiconductor index SOXL/SOXS track; QQQ for TQQQ/SQQQ).
INDEX_PROXY = {"SOXL": "SOXX", "SOXS": "SOXX", "TQQQ": "QQQ", "SQQQ": "QQQ"}

# --------------------------------------------------------------------------------------
# Session constants (America/New_York)
# --------------------------------------------------------------------------------------
TZ = "America/New_York"
EXT_START_MIN = 4 * 60          # 04:00 ET  (minute-of-day)
RTH_START_MIN = 9 * 60 + 30     # 09:30 ET
RTH_END_MIN = 16 * 60           # 16:00 ET  (exclusive; last regular bar starts 15:59)
HALF_DAY_END_MIN = 13 * 60      # 13:00 ET  on early-close days
EXT_END_MIN = 20 * 60           # 20:00 ET  (exclusive)
N_RTH = RTH_END_MIN - RTH_START_MIN            # 390 regular-session minutes
FLAT_BEFORE_CLOSE_MIN = 5       # flat by 15:55 ET (5 minutes before the close; 12:55 on half-days)

# In-sample / out-of-sample split for the behavior-probe battery (fixed a priori by the brief)
IS_START, IS_END = "2022-01-01", "2024-09-30"
OOS_START, OOS_END = "2024-10-01", "2026-09-25"

# --------------------------------------------------------------------------------------
# Cost assumptions (ASSUMPTIONS unless noted; all overridable from the CLI)
# --------------------------------------------------------------------------------------
COMMISSION_PER_SHARE = 0.0035   # USD per share per side (ASSUMPTION: typical per-share broker tier)
TRADE_NOTIONAL = 25_000.0       # USD notional per trade used to convert per-share / capped fees (ASSUMPTION)
# SEC Section 31 fee (USD per USD 1,000,000 of sale proceeds) - schedule by effective date.
# Rates/dates as published in SEC fee-rate advisories and FINRA information notices (URLs in
# soxlab/README.md). Applied to sells only (long exits and short-sale entries).
SEC_FEE_SCHEDULE = [
    ("2021-01-01", 5.10),      # FY2021 rate, in force until 2022-05-13
    ("2022-05-14", 22.90),
    ("2023-02-27", 8.00),
    ("2024-05-22", 27.80),
    ("2025-05-14", 0.00),
    ("2026-04-04", 20.60),
]
# FINRA Trading Activity Fee (USD per share sold, per-trade cap USD) - schedule by effective date.
# 2021 0.000130 -> 2022 0.000145 -> 2024 0.000166 (cap 8.30) -> 2026 0.000195 (cap 9.79).
# The 2021/2022 caps (6.49 / 7.27) are ASSUMPTIONS; at TRADE_NOTIONAL the cap never binds.
FINRA_TAF_SCHEDULE = [
    ("2021-01-01", 0.000130, 6.49),
    ("2022-01-01", 0.000145, 7.27),
    ("2024-01-01", 0.000166, 8.30),
    ("2026-01-01", 0.000195, 9.79),
]
