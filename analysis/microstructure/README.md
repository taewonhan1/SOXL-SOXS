# SOXL / SOXS market microstructure study

Measures spreads, depth, quote dynamics, trade flow, execution quality and tick-size constraints for
SOXL and SOXS against SOXX, SMH, NVDA, TQQQ, SQQQ, QQQ and SPY, using Massive API (formerly Polygon.io)
NBBO quotes, trades and aggregates. Data end: Friday 2026-09-25. All times are America/New_York.

## Re-running

Authentication is injected by the network proxy (no apiKey parameter). Set
`REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt` if TLS errors appear. Python 3 with pandas, numpy, pyarrow,
orjson, requests and matplotlib. Every step caches under `data/microstructure/` (gitignored) and skips work
that is already cached, so an interrupted run can simply be restarted.

```bash
cd analysis/microstructure
python3 01_fetch_bars.py                    # daily bars (adj + unadj), 1-min bars (unadj), splits, ticker reference   ~2 min
python3 02_tick_windows.py --phase 1        # windowed NBBO quotes + trades, first 16 sample days x 9 tickers         ~30 min
python3 02_tick_windows.py --phase 2        # remaining 29 sample days                                               ~50 min
python3 03_fullday.py                       # full-session quotes + trades, SOXL & SOXS, 9 days                     ~12 min
python3 04_bars_analysis.py                 # activity, relative tick, 1-min tick stats, volume profile, RTH gaps   ~3 min
python3 05_tick_analysis.py                 # everything else incl. cost_model_halfspread.csv                       ~10 min
python3 05_tick_analysis.py --cost-only     # only regenerate the cost table (fast)
python3 06_checks.py                        # NBBO size granularity, condition census, gap verification, LULD flags
```

Wall-clock times above are for 2 worker threads per process; the download steps are CPU-bound in JSON parsing,
so several processes with disjoint `--tickers` (or reversed `--days` lists) finish faster than one process with
many threads. Files are written atomically per ticker-day, so overlapping processes are safe.

`02` and `03` accept `--workers` (default 4 and 2; keep the total at or below about 6 concurrent requests,
since other analysts share the API) and `--tickers` / `--days` filters.

## Sampling design (ms_common.py)

* **Sample days** (`output/sample_days.csv`): evenly spaced trading days (by trading-day index, half-days excluded)
  - 5 in each of 2022, 2023 and 2024, 4 in 2025-01-01..2025-09-25, 13 in 2025-09-26..2026-09-18,
  the last 5 trading days 2026-09-21..25 ("recent"), and 8 stress days chosen from the daily bars
  (largest SOXL / NVDA absolute moves or ranges since 2025-03-25: 2025-04-03, 04-04, 04-07, 04-09, 2026-02-06,
  2026-06-05, 2026-06-09, 2026-08-27) plus 2025-11-20, added afterwards as the first session after an NVDA
  quarterly filing (acceptance times in `output/nvda_filing_dates.csv`, from `/vX/reference/financials`; 2026-08-27 is
  likewise the session after the 2026-08-26 filing). Stress days are excluded from the cost table and the "normal"
  groups; 2025-11-20 does not enter the normal-day selection, so the normal days are unchanged by its addition.
* **Analysis groups** (column `group` in the output tables): `y2022`...`y2026` = normal + recent days of that calendar
  year; `last12m` = normal + recent days from 2025-09-26; `since_2026-07-15` = normal + recent days on/after the
  last SOXS reverse split (the current price regime: 2026-08-10, 2026-09-04, 2026-09-21..25); `normal18m` = normal +
  recent days since 2025-03-25 (stress baseline); `stress`; `last5`.
* **Windows per day** (identical for all tickers on a day): for each of the 13 RTH half-hour buckets, one 10-minute
  NBBO window at a random 5-minute-aligned offset (0-20 min, seeded by the date); trades are taken from the first
  5 minutes of that window so that the mid 1 and 5 minutes later lies inside the quote window. Fixed windows:
  09:30-09:35 (trades from 09:29:30, to catch the opening auction), 15:55-16:00, and 16:00-16:01 trades only
  (closing auction). Extended hours: one random 5-minute window in each of 04:00-07:00, 07:00-08:00,
  08:00-09:00, 09:00-09:30, 16:00-17:00, 17:00-18:00 and 18:00-20:00.
* The NBBO in effect at a window start is seeded with the last quote before the window (ignored if older than 30 min).
* Full-session data (04:00-20:00) for SOXL and SOXS on 2022-09-14, 2023-09-13, 2024-09-12, 2025-08-25 and
  2026-09-21..25 (`03_fullday.py`) are used for exact whole-day statistics and to validate the windows
  (`output/window_validation_fullday.csv`).

## Output charts

`activity_trend.png` (monthly $ volume, trades/day, relative tick), `tick_constraint_scatter.png` (relative tick vs
share of zero-change 1-minute bars, ticker-months), `volume_profile.png` (1-minute RTH volume shares),
`spread_by_time_of_day.png`, `depth_by_time_of_day.png`, `spread_to_vol.png` (current regime group),
`spread_regimes_by_day.png` (SOXL/SOXS per sample day 2022-2026), `stress_vs_normal.png`,
`fullday_spread_profile.png` (SOXL/SOXS full-session minute-by-minute spread, 2026-09-21..25).

## Definitions

* Quoted spread = ask - bid of the NBBO (`/v3/quotes`), time-weighted by how long each NBBO state lasted.
  Locked (spread = 0) and crossed (< 0) states and one-sided quotes are excluded from spread statistics and
  reported separately. bps = spread / midpoint x 10,000; half-spread = spread / 2.
* One tick = $0.01 (all tickers trade above $1). Half-penny = a spread that is an odd multiple of $0.005;
  sub-penny quote = a bid or ask not on the $0.01 grid.
* Depth = displayed NBBO bid/ask size in shares (and x price in $), time-weighted. It is only the size at the
  best price on the displayed protected quotes; odd-lot quotes, hidden and midpoint liquidity are not in the NBBO.
* Quote dynamics: NBBO messages per second, NBBO price changes per second (bid or ask price changed), and the
  duration of NBBO price states (time between consecutive price changes; left/right-censored states dropped).
* Effective spread = 2 x |price - mid| / mid, mid = NBBO midpoint prevailing strictly before the trade's SIP
  timestamp. Trades are signed with the Lee-Ready rule (quote rule; midpoint trades by the tick test within
  the window). Realized spread (h) = 2 d (price - mid(t+h)) / mid; price impact (h) = 2 d (mid(t+h) - mid) / mid,
  h = 60 s and 300 s. Only regular continuous-session trades are used: trades carrying any of the condition
  codes 2, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 25, 28, 29, 32, 33, 38, 52, 53, 55 are excluded
  (average-price, cash, auction/cross, derivatively priced, extended-hours, out-of-sequence, prior-reference,
  contingent/QCT, official open/close prints). "dw" = dollar-weighted, "tw" = trade-weighted.
* Auctions: opening auction = trade on the primary listing exchange (NYSE Arca id 11 for SOXL, SOXS, SPY;
  Nasdaq id 12 for the others) carrying condition 17 (Market Center Opening Trade) or 25 (Opening Prints);
  closing auction = primary-exchange trade with condition 8 (Closing Prints) or 19 (Market Center Closing Trade).
  The companion zero-volume "official open/close" prints (conditions 16/15) are excluded. Share of daily volume
  uses the daily-bar volume, which equals the sum of all trade sizes excluding conditions 15/16/38 (checked on
  SOXS 2023-09-13: 59,746,166 vs 59,746,164 shares).
* Odd lot = trade flagged with condition 37 by the SIP (also reported: size < 100 shares).
* Massive 1-minute bars omit the closing-auction print and minutes containing only odd-lot trades; they are
  used for volume profiles (RTH continuous trading), 1-minute tick statistics and trading-gap detection only.

## Cost table: output/cost_model_halfspread.csv

Columns (fixed): `ticker, year, bucket_start_et, bucket_end_et, median_spread_cents, mean_spread_cents,
median_half_spread_bps, mean_half_spread_bps, n_obs`.

* Tickers SOXL, SOXS, SOXX, SMH, NVDA, TQQQ, SQQQ, QQQ; years 2022-2026 (2026 = through 2026-09-25).
* Rows per ticker-year: thirteen RTH 30-minute buckets (09:30-10:00 ... 15:30-16:00), one pre-market row
  (04:00-09:30) and one after-hours row (16:00-20:00).
* Statistics are time-weighted over NBBO states in the sampled windows of normal + recent sample days of that
  calendar year (stress days excluded). Median = time-weighted median. The pre-market and after-hours rows are
  stratified: each extended-hours stratum is weighted by its clock length, so 04:00-07:00 carries 180/330 of the
  pre-market weight. Finer strata (04:00-07:00, 07:00-08:00, 08:00-09:00, 09:00-09:30, 16:00-17:00,
  17:00-18:00, 18:00-20:00) with n_days, p90 and one-tick share are in `cost_model_halfspread_detail.csv`.
* `n_obs` = number of NBBO quote messages observed inside the sampled windows for that ticker-year-bucket
  (not independent observations; see `n_days` / `n_5min_subwindows` in the detail file).
* For tick-constrained instruments the spread in cents is stable (1 cent) while bps move with the price level,
  so a year pooling days at different prices can have a median bps that sits at one price regime; the mean,
  or `median_spread_cents / 2 / price` at the backtest's own price, is the more stable input.
