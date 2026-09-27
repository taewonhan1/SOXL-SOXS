# SOXL / SOXS intraday behavior profile

Scripts that measure how SOXL and SOXS move within the trading day, side by side with SOXX, SMH, NVDA, TQQQ, SQQQ
and QQQ. All numbers come from Massive API (formerly Polygon.io) aggregates pulled by `01_download.py`.
The research notes are in `research_notes/SOXL and SOXS intraday behavior/price_behavior.md`.

## Re-run (from this directory)

```bash
python3 01_download.py         # ~5 min, 4 concurrent requests, idempotent; caches to data/behavior/ (gitignored)
python3 02_build_panel.py      # ~3 min: calendar, half-day detection, RTH minute matrices, daily/session tables
python3 04_events.py           # catalyst dates detected from price/volume reactions (run before 03)
python3 03_volatility.py       # range/ATR, realized vol by horizon, U-shape, clustering, weekday, catalyst days
python3 05_direction.py        # autocorrelation, variance ratios, DFA, large-move continuation, runs, efficiency ratio
python3 05b_vr_null_check.py   # variance ratios under a sign-randomised null (robustness)
python3 06_daytypes_open.py    # day types, high/low timing, gaps and gap fills, opening range, first hour
python3 07_vwap_close.py       # VWAP behaviour, GHLZ intraday momentum, late-day / LETF-rebalancing tests, closing auction
python3 08_linkage.py          # betas, leverage drift, 1-min and 1-second (Hayashi-Yoshida) lead-lag, SOXL-SOXS mirror
python3 09_exthours_tails.py   # pre-/after-hours, tails, RTH bar gaps (halt candidates), closing dislocations
python3 10_stability_scorecard.py  # quarterly stability, persistence summary, scorecards
```

Requirements: Python 3 with pandas, numpy, scipy, statsmodels, pyarrow, matplotlib, requests. Authentication is injected
by the network proxy (no API key parameter). If TLS errors appear, set `REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt`.

## Conventions

- Windows: secondary 2022-01-03..2024-09-30 (685 full sessions), primary 2024-10-01..2026-09-25 (493 full sessions).
  2021-11/12 is downloaded only as warm-up for ATR and trailing baselines.
- Times are America/New_York. RTH = 09:30-16:00 minute bars (bar-start times 09:30..15:59); pre-market 04:00-09:30;
  after-hours 16:00-20:00. Half-days are detected from the QQQ afternoon/morning volume ratio (< 0.15) and excluded
  from intraday statistics.
- Returns use split-adjusted prices (`adjusted=true`); prior closes are additionally adjusted for cash distributions on
  ex-dates. Price-level statements (tick size in bps) use unadjusted daily closes.
- "Official close" = daily-bar close (closing auction); the last RTH minute close is the last trade before 16:00.
- Minute bars exclude opening/closing auction prints, so volume shares refer to minute-bar volume.
- Random-walk benchmarks: sign-randomised minute paths (each day's |1-min returns| in their original time order, random
  signs) or within-day shuffles, as stated in each script docstring.

## Outputs (`output/`)

CSV tables named by topic prefix (`vol_`, `dir_`, `day_`, `open_`, `vwap_`, `close_`, `link_`, `ext_`, `tails_`,
`stability_`, `scorecard_`, `events_`, `data_coverage.csv`, `half_days.csv`) and PNG charts
(`ushape_30min_primary.png`, `variance_ratios.png`, `hod_lod_timing_primary.png`, `leverage_drift_beta.png`,
`leadlag_1sec_hy.png`, `stability_quarterly.png`).
