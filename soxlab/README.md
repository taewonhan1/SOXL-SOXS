# soxlab — SOXL / SOXS intraday data, feature, backtest and tracking toolkit

`soxlab` downloads and caches Massive (formerly Polygon.io) market data for SOXL, SOXS and their drivers,
checks data quality, builds a set of intraday features that don't look ahead, runs bar-level backtests with a
cost model, and produces a daily behavior tracker. Every number the toolkit reports is computed from data
pulled from the API. Anything that is an assumption is marked as one in the code (`soxlab/config.py`) and below.

## Quick start

```bash
cd /home/user/SOXL-SOXS
pip install pytest                                   # only extra dependency (pandas, numpy, pyarrow, scipy, matplotlib preinstalled)
python scripts/download_data.py                      # ~5 min: 1-min bars (adj + unadj), daily bars, splits, dividends, calendar
python scripts/download_data.py --update             # incremental: re-fetches the last month + any missing month
python scripts/probe_endpoints.py                    # endpoint inventory -> analysis/backtests/output/endpoint_inventory.csv (~20 min, paced)
python scripts/probe_options_history.py              # options history depth (paced)
python scripts/estimate_spreads.py                   # fallback half-spreads from a light NBBO sample
python scripts/run_quality.py                        # data-quality report -> analysis/backtests/output/data_quality_report.md
python scripts/daily_tracker.py                      # one row per day per ticker -> daily_tracker_SOXL_SOXS.csv
python scripts/daily_tracker.py --live               # today's session so far (REST polling), --interval 60 to loop
python scripts/run_battery.py                        # behavior-probe battery (~15-20 min; --stages 1,2,3,4,5) -> battery_*.csv / *.png
python -m pytest -q -p no:cacheprovider tests       # 32 tests: harness timing, stop-first, costs, DST, look-ahead
```

Authentication: the REST base URL is `https://api.massive.com`. In this environment the network proxy
injects the API key, so the client never sends an `apiKey` parameter. Concurrency is capped at 4 threads (hard
limit 6, `SOXLAB_MAX_CONCURRENCY`). Requests are retried with exponential backoff on 429 and 5xx. Options, indices and
futures calls are rate-limited per minute on this key, so the probe scripts space them out to five or fewer per minute.

## Package layout

| module | contents |
|---|---|
| `config.py` | paths, universe (`SOXL SOXS SOXX SMH NVDA QQQ TQQQ SQQQ`), sessions, IS/OOS dates, cost assumptions, fee schedules |
| `api.py` | REST client: retry/backoff, `next_url` pagination, bounded thread pool |
| `data.py` | monthly-chunked 1-min bar download/cache, daily bars, splits/dividends, `Panel` (dense 09:30–15:59 arrays) |
| `calendar.py` | trading days (from QQQ daily bars), half-day detection from minute volume, event flags |
| `quality.py` | coverage/missing minutes, integrity, raw re-fetch vs cache, outliers, split checks, SOXL–SOXS consistency, daily-vs-minute reconciliation |
| `features.py` | features that don't look ahead + `data_dictionary()` |
| `costs.py` | half-spread table (cents → bps at the unadjusted trade price), commissions, SEC/FINRA fees |
| `backtest.py` | execution engine, metrics, walk-forward, random-entry baseline, lag/shuffle helpers |
| `strategies.py` | behavior-probe signal generators + `PROBES` registry (canonical params + IS grids) |
| `tracker.py` | daily tracker (history + live) |
| `pipeline.py` | `load_context()` → calendar, panels, official closes, pre-market summaries, features |

## Cache layout (`data/soxlab/`, gitignored)

```
bars_1min/{adjusted|unadjusted}/{TICKER}/{YYYY-MM}.parquet   t (bar start, UTC ms), o h l c v vw n
bars_1day/{adjusted|unadjusted}/{TICKER}.parquet             full daily history (2010-03-11 for SOXL/SOXS)
reference/splits_*.parquet, dividends_*.parquet, calendar.parquet, conditions_stocks.parquet, manifest.json, probe_raw/
nbbo_sample/                                                 raw /v3/quotes windows for the fallback spread estimate
cache/panel_*.npz, battery_trades_canonical.parquet          derived arrays / trade lists
```

`manifest.json` records rows, last bar and download time per ticker/adjustment/month. `--update` extends the end
date to the latest weekday. It re-downloads the last month and any month that is missing or incomplete, and never
touches earlier months that are already complete.

## Data conventions and quirks (verified on this account; details in `analysis/backtests/output/data_quality_report.md`)

* **Timestamps.** Aggregate `t` = bar start in UTC epoch ms, and a minute bar covers [t, t+60 s). Converting to
  America/New_York handles DST: the 09:30 ET bar is 14:30 UTC under EST and 13:30 UTC under EDT. Ticks use `sip_timestamp` (ns UTC).
* **Sessions.** Minute bars span 04:00–19:59 ET. The regular session is 09:30–15:59 (12:59 on early-close days,
  which are detected from data). The official close (the closing-auction print) is the daily-bar close. It is **not** the
  15:59 bar close, and the closing-cross volume appears in the daily bar but in no minute bar.
* **Missing minutes.** A bar exists only if an eligible trade printed. `Panel` forward-fills missing minutes with the
  previous close and volume 0, and flags them `present=False`. It never back-fills.
* **Bar construction.** Odd lots, Form T, average-price and similar prints count toward bar volume and `vw` but not
  toward OHLC in the regular session. Pre/post-market bars are built from Form T prints. `vw` can lie outside [l, h].
* **Adjusted vs unadjusted.** `adjusted=true` applies split adjustments only (the factor changes only on split dates).
  Adjusted SOXS prices in early years run into the millions, and its adjusted volume becomes fractional.
  Returns are computed on adjusted bars, which within a day equal unadjusted returns. Per-share costs use
  **unadjusted** prices.
* **Fractional volume.** Non-integer share volume appears in unadjusted bars from 2026-02-23 onward, for all 8 tickers.
* **Aggregates `limit`.** The limit counts the *base* aggregates. `limit=1` on hour bars can return no bar at all.
* **Sort syntax.** The newer `/stocks/v1/*` endpoints use `sort=field.asc|field.desc`. The `order` parameter is ignored there.

## Feature data dictionary

A value at (day d, bar j) uses only bars 0..j of day d, pre-market bars of day d, and data from earlier days.
Signals are filled at the open of bar j+1. `tests/test_no_lookahead.py` recomputes every feature on data cut off at
(d*, j*) and requires identical values (and shows the `label_*` columns fail that test). The full list is also in
`analysis/backtests/output/feature_dictionary.csv`.

| name | definition | granularity | look-ahead-safe |
|---|---|---|---|
| ret_1m | log(c_j / c_{j-1}); bar 0 uses log(c_0/o_0) | 1-min | yes |
| ret_{5,15,30,60}m | log(c_j / c_{j-k}); NaN until k bars into the session (no overnight mixing) | 1-min | yes |
| ret_since_open | log(c_j / o_0), o_0 = 09:30 bar open | 1-min | yes |
| true_range_1m[_bps] | max(h_j, c_{j-1}) - min(l_j, c_{j-1}) (bps: / c_j) | 1-min | yes |
| atr14_1m[_bps] | Wilder ATR(14) of 1-min true range, reset each session | 1-min | yes |
| rv_30m / rv_30m_ann | sqrt(sum of squared 1-min log returns, last 30 bars); annualised x sqrt(252*390/30) | 1-min | yes |
| atr14_d / atr14_d_pct | Wilder ATR(14) of daily true range (RTH high/low vs prior official close) through day d-1 | daily | yes |
| rv20_d_ann | stdev of the 20 prior daily close-to-close log returns x sqrt(252) | daily | yes |
| vwap | session VWAP from 09:30 = cumsum(vw*v)/cumsum(v) over bars 0..j | 1-min | yes |
| vwap_sd, vwap_up{1,2,3}, vwap_dn{1,2,3} | volume-weighted stdev of bar vw around VWAP; bands = vwap ± k·sd | 1-min | yes |
| dist_vwap_bps / dist_vwap_sd | (c_j/vwap_j - 1)·1e4 ; (c_j - vwap_j)/vwap_sd_j | 1-min | yes |
| vwap_cross_count | cumulative sign changes of (c - vwap) since the open | 1-min | yes |
| or{5,15,30}_high / _low / _size_bps | high/low of the first N regular bars; NaN until bar N-1 has closed | 1-min | yes |
| pm_high / pm_low / pm_volume / pm_ret | pre-market (04:00–09:29) high, low, volume, last/prior official close - 1 | daily | yes |
| pd_high / pd_low / pd_close | prior session RTH high/low (minute bars) and prior official close (daily bar) | daily | yes |
| gap / gap_atr / flag_large_gap | o_0/pd_close - 1 ; (o_0 - pd_close)/atr14_d ; abs(gap) > 1 ATR | daily (from bar 0) | yes |
| dist_pd_high_bps / dist_pd_low_bps | (c_j/pd_high - 1)·1e4 ; (c_j/pd_low - 1)·1e4 | 1-min | yes |
| ret_since_prev_close | c_j / pd_close - 1 | 1-min | yes |
| cum_volume | cumulative RTH volume through bar j | 1-min | yes |
| rvol_tod | cum_volume_j / mean(cum_volume at bar j over the prior 20 sessions) | 1-min | yes |
| cumvol_share | cum_volume_j / mean(total RTH volume of the prior 20 sessions) | 1-min | yes |
| rvol_1m | v_j / mean(v at bar j over the prior 20 sessions) | 1-min | yes |
| ema9_1m / ema21_1m / ema_diff_1m_bps | EMA(9)/EMA(21) of 1-min closes (session reset); difference in bps | 1-min | yes |
| ema9_5m / ema21_5m / ema_diff_5m_bps | EMAs of 5-min closes, updated when each 5-min bar completes | 5-min on 1-min grid | yes |
| {SOXX,NVDA,QQQ,SMH}_ret_1m[_lag1,_lag2] | driver 1-min log return, and lagged by 1 or 2 bars | 1-min | yes |
| {driver}_ret_5m / {driver}_ret_since_prev_close | driver 5-min log return ; driver c_j / prior official close - 1 | 1-min | yes |
| idx_ret_since_prev_close (r) | index-proxy return since its prior official close (SOXX for SOXL/SOXS; ASSUMPTION: SOXX as tradable proxy) | 1-min | yes |
| lev_implied | L(1+r)/(1+L·r): exposure/NAV of a daily-reset L× fund after index move r (L=+3 SOXL, -3 SOXS) | 1-min | yes |
| tracking_gap_bps | (ret_since_prev_close - L·r)·1e4 | 1-min | yes |
| lev_realized | ret_since_prev_close / r when abs(r) > 0.25% | 1-min | yes |
| soxl_soxs_div_bps | (SOXL + SOXS return since prior official close)·1e4, 0 under perfect ∓3× tracking | 1-min | yes |
| soxl_soxs_ret1m_sum_bps | (SOXL + SOXS 1-min log return)·1e4 | 1-min | yes |
| minute_of_session / minutes_to_close | bar index j (0 = 09:30) ; bars left in the session | 1-min | yes |
| dow | day of week (0 = Monday) | daily | yes |
| flag_is_half_day / flag_pre_holiday / flag_post_holiday | 13:00 close ; next / previous weekday is a holiday | daily | yes |
| flag_month_end / flag_month_start / flag_quarter_end | calendar position of the session | daily | yes |
| flag_monthly_opex / flag_quad_witching | 3rd Friday (or prior trading day) ; the same in Mar/Jun/Sep/Dec | daily | yes |
| flag_split / flag_exdiv | split execution / ex-dividend date of the ticker (/v3/reference) | daily | yes |
| label_fwd_ret_1m / _5m / _to_close | **future** returns: research labels only | 1-min | **NO** |

## Cost model (`costs.py`)

The model charges **half-spread per side + per-share commission per side + SEC Section 31 fee and FINRA TAF on sells**
(long exits and short-sale entries). Costs are expressed in bps of notional per trade.

* **Half-spread.** Taken from `analysis/microstructure/output/cost_model_halfspread.csv` (ticker × year × 30-min ET
  bucket, produced by the microstructure analysis) when that file exists. The **cents** column is converted with the
  **unadjusted price at trade time**: `half_bps = median_spread_cents / 2 / 100 / price_unadj × 1e4`. When the file is
  missing, the fallback is `analysis/backtests/output/halfspread_estimate_nbbo_sample.csv` from `scripts/estimate_spreads.py`:
  10 days × 5 five-minute `/v3/quotes` windows × SOXL/SOXS, time-weighted, with locked/crossed quotes dropped. A missing
  year falls back to the nearest year, and a missing bucket to the nearest bucket.
  *Provenance of the published battery:* it ran against an earlier draft of that table (sha256 `96aafb46…`), saved
  verbatim as `analysis/backtests/output/cost_table_used_by_battery.csv`. Among SOXL/SOXS rows it differs from the
  final table only in SOXL 2026 10:00–10:30 (median spread 5¢ vs 6¢). Reproduce the published numbers with
  `python scripts/run_battery.py --cost-table analysis/backtests/output/cost_table_used_by_battery.csv`.
* **Commission.** $0.0035/share/side. ASSUMPTION: a typical per-share broker tier. `avg_net_bps_zero_commission` in
  the battery output shows the zero-commission case.
* **SEC Section 31 fee** (USD per USD 1M of sales): 5.10 through 2022-05-13; 22.90 from 2022-05-14; 8.00 from
  2023-02-27; 27.80 from 2024-05-22; 0.00 from 2025-05-14; 20.60 from 2026-04-04. Sources: FINRA information notices
  ([2022](https://www.finra.org/rules-guidance/notices/information-notice-042122),
  [2023](https://www.finra.org/rules-guidance/notices/information-notice-021423),
  [2024](https://www.finra.org/sites/default/files/2024-05/Information-Notice-050124.pdf),
  [2025](https://www.finra.org/rules-guidance/notices/information-notice-20250424),
  [2026](https://www.finra.org/rules-guidance/notices/information-notice-20260317)) and the SEC FY2026 advisory
  (https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2). Egress to sec.gov and finra.org was blocked from this
  session, so these values come from search-result extracts of those pages.
* **FINRA TAF** (per share sold, per-trade cap): 0.000130 (2021), 0.000145 (2022), 0.000166/cap 8.30 (2024),
  0.000195/cap 9.79 (2026) (https://www.finra.org/rules-guidance/guidance/trading-activity-fee). The 2021 and 2022 caps
  are assumptions; the cap never binds at the $25k notional used.
* Not modelled: market impact beyond the half-spread, queue position, borrow fees for intraday shorts, and slippage on
  stop orders beyond the bar-level fill rule.

## Backtest harness (`backtest.py`)

* A signal at the **close of bar j** fills at the **open of bar j+1**. Exit signals are handled the same way.
* Take-profit and stop are checked intra-bar from the entry bar onward, using bar high/low. If both are touched in the
  same bar, the **stop fills first**. A stop that is gapped through at a bar open fills at that worse open.
* Positions are **flat by 15:55 ET**: forced exit at the 15:55 bar open, or 12:55 on 13:00 early-close days. No entry
  may fill at or after that time.
* The engine holds one position at a time per instrument. Supported modes are long/short (`SOXL L/S`, `SOXS L/S`) and
  **switch** (a bullish signal goes long SOXL, a bearish one goes long SOXS). Shorting SOXL is the `-1` side of `SOXL L/S`.
* Metrics:
  * trades, win rate (net), average gross/net/cost bps per trade, and profit factor (gross and net)
  * Sharpe: daily sum of trade returns on a fixed notional, including zero days, × √252
  * t-stat, total and annualised return, max drawdown of the additive daily P&L (% of notional)
  * exposure (minutes held / session minutes), average holding time
* `walk_forward()` selects a parameter set on each train window and reports it on the next test window. The battery
  uses rolling 24-month train / 6-month test windows.
* `random_entry_baseline()` uses random entry times and **random sides** on the same days, with the same holding
  times. Keeping the strategy's side would leak information: a random entry placed before the signal inherits its
  direction, and realized holding times encode whether the trade worked.
* `lag_entries()` and `shift_signalset()` build the lag -1 / 0 / +1 diagnostics; `shuffle_days()` builds the
  day-shuffled null.

## Behavior probes (`strategies.py`, canonical parameters fixed a priori)

| probe | rule |
|---|---|
| orb5 / orb15 / orb30 | first close outside the N-min opening range; stop at the opposite side; exit 15:55 |
| vwap_reversion | close crosses beyond the ±2σ VWAP band → fade; exit at VWAP; stop at the 3σ band; max 60 min |
| vwap_trend | close crosses VWAP after 09:45 → follow; reverse on the next cross |
| mom/rev_1m_z3 | 1-min abs(return) > 3σ (σ from the prior 60 min) after 10:00 → with/against it; hold 5 min |
| mom/rev_5m_z3 | 5-min abs(return) > 3σ√5 → with/against it; hold 15 min |
| ema_1m / ema_5m | EMA(9)/EMA(21) crossover on 1-min / 5-min closes; always reverse |
| last30_day / last30_first30 | sign of return prior close→15:30 (or →10:00); trade 15:30 open → 15:55 open |
| leadlag_nvda / leadlag_soxx | driver 1-min abs(move) > 2σ → trade the ETF in the implied direction next open; hold 1 min |
| gap_fill | abs(gap) > 0.5 daily ATR → fade at 09:31; target prior close; stop 1 gap beyond the open |

## Daily tracker and live tracking

`scripts/daily_tracker.py` writes one row per day per ticker with the following fields:
* open/high/low/close, prior close, gap, range %, true range and ATR, TR/ATR
* opening-range sizes and the first break of the 30-min range
* VWAP crosses and close-vs-VWAP, trend-day flag (|close-open| ≥ 60% of range and TR ≥ 1 ATR), close location
* time of high and low
* RTH, pre-market and daily-bar volume, 20-day relative volume, 1-min realized vol
* index-proxy return, implied leverage at the close, tracking gap, SOXL–SOXS divergence
* modelled spread

Live tracking:

* **REST polling** (`--live [--interval N]`): each poll requests `/v2/aggs/ticker/{T}/range/1/minute/{today}/{today}`
  plus `/v3/snapshot?ticker.any_of=SOXL,SOXS`. The snapshot's `last_quote.timeframe` reads `REAL-TIME` on this
  account, and it supplies the live spread.
* **WebSocket** (not run here; the key is injected only into proxied REST calls, so a WebSocket client needs the raw
  key). Connect to `wss://socket.massive.com/stocks` (real-time) or `wss://delayed.massive.com/stocks`. Send
  `{"action":"auth","params":"<KEY>"}`, then `{"action":"subscribe","params":"AM.SOXL,AM.SOXS,A.SOXL,Q.SOXL,T.SOXL"}`.
  The channels are `AM` = minute aggregates, `A` = second aggregates, `T` = trades, `Q` = NBBO quotes, and `LULD`.
  Feed and market enums: https://github.com/massive-com/client-python/blob/master/massive/websocket/models/common.py.
  An `AM` message carries `sym, v, o, c, h, l, a (VWAP), s (start ms), e (end ms)`, and no bar is emitted for a
  minute without eligible trades (https://massive.com/docs/websocket/stocks/aggregates-per-minute). Feed each `AM`
  message into `tracker.day_row()` to update the same fields incrementally.
* **Flat files** (bulk history, not run): S3-compatible endpoint `https://files.massive.com`, e.g. dataset
  `us_stocks_sip/minute_aggs_v1` (daily files) (https://massive.com/docs/flat-files/stocks/overview).

## Tests

`python -m pytest -q -p no:cacheprovider tests` (32 tests; 29 on synthetic data with no network, plus 3 real-data tests that are skipped
when the cache is absent):
* the fill is always at the next bar open
* stop-first when both levels are touched, and gap-through stop fills
* flat by 15:55 and 12:55 on early-close days
* on iid random-walk data, a signal from the just-closed bar has no edge, while a deliberately look-ahead fill does
* on AR(1) data the edge decays with one extra bar of delay and disappears when days are shuffled
* cost units and sell-side fees; costs use unadjusted prices
* DST conversion; half-day detection; every probe emits valid signals
* truncation-invariance of all 97 features that don't look ahead, and detection of the look-ahead labels
* the same truncation test on real cached SOXL/SOXS bars (2023-12 → 2024-03, 3 cut points)
