# SOXL-SOXS

Research repository on the intraday behavior of the Direxion Daily Semiconductor Bull/Bear 3X ETFs
(SOXL / SOXS). All market data comes from the Massive REST API (formerly Polygon.io,
`https://api.massive.com`), and every reported number is computed from downloaded data.

## Layout

| path | what it holds |
|---|---|
| `soxlab/` | Python package for tracking and backtesting: data download/cache, trading calendar, data-quality checks, features that don't look ahead, cost model, backtest harness, behavior probes, daily tracker. See [`soxlab/README.md`](soxlab/README.md) for the data dictionary and usage. |
| `scripts/` | Runnable entry points for `soxlab`: `download_data.py`, `probe_endpoints.py`, `probe_options_history.py`, `estimate_spreads.py`, `run_quality.py`, `daily_tracker.py`, `run_battery.py` |
| `tests/` | pytest suite for `soxlab`: harness timing, stop-first resolution, flat-by-15:55, costs, DST, feature truncation (look-ahead) tests |
| `analysis/behavior/` | Standalone scripts and outputs profiling SOXL/SOXS intraday price behavior (volatility, events, direction, day types, VWAP/close, linkage, extended hours) |
| `analysis/microstructure/` | Standalone scripts and outputs on spreads, depth, auctions, trade conditions and volume profiles. Writes `output/cost_model_halfspread.csv`, which `soxlab` reads as its half-spread source. |
| `analysis/backtests/` | `output/` holds the `soxlab` results: endpoint inventory, data-quality report, feature dictionary, daily tracker, behavior-probe battery tables and charts |
| `research_notes/` | Research notes (markdown) behind the report, one file per workstream |
| `reports/` | Final synthesized report(s) |
| `data/` | Local caches: `data/soxlab/` for this toolkit, other subfolders for the other analyses. Gitignored and rebuilt by the download scripts. |

## Quick start

```bash
cd /home/user/SOXL-SOXS
pip install pytest

# 1. data (idempotent; ~5 min for 8 tickers x 2019-01 -> 2026-09, adjusted + unadjusted 1-min bars)
python scripts/download_data.py
python scripts/download_data.py --update          # later: incremental refresh

# 2. inventory and quality
python scripts/probe_endpoints.py                 # HTTP status + earliest/latest date per endpoint (paced, ~20 min)
python scripts/run_quality.py                     # analysis/backtests/output/data_quality_report.md

# 3. tracking
python scripts/daily_tracker.py                   # history: one row per day per ticker
python scripts/daily_tracker.py --live --interval 60   # intraday polling (REST minute aggs + real-time snapshot)

# 4. backtests
python scripts/run_battery.py                     # behavior-probe battery (IS 2022-01..2024-09, OOS 2024-10..2026-09)
python scripts/run_battery.py --stages 5          # re-draw charts / multiple-testing table only

# 5. tests
python -m pytest -q tests
```

Authentication is injected by the network proxy in this environment. Elsewhere, add your key in `soxlab/api.py`,
either as the `apiKey` query parameter or as an `Authorization: Bearer` header.
