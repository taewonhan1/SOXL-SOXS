# SOXL and SOXS intraday behavior: data elements, a tracking/backtesting toolkit, and a first behavior-probe battery

Scope: which Massive API data elements exist under this account for tracking and backtesting SOXL/SOXS intraday, the
`soxlab` toolkit built on them (`/home/user/SOXL-SOXS/soxlab/`, `scripts/`, `tests/`), and what a standard battery of
behavior-probe backtests shows. Every number below was pulled from the API on 2026-09-27 or computed from those pulls.
Local citations name the output file and the script that produced it. Paths are relative to this notes file, so
`../../analysis/backtests/output/` is the toolkit's output folder. Assumptions are labelled as such.

## 1. Which data elements exist for SOXL/SOXS under this account, and how deep and fine-grained are they?

### Takeaway
The stock entitlement is complete for this purpose:
* second, minute, hour and day aggregates, raw trades and full NBBO quotes for both tickers
* history back to the 2010-03-11 listing, current through 2026-09-25
* snapshots flagged `REAL-TIME`
* technical indicators, splits, dividends, point-in-time shares outstanding, short interest/volume and market status

Everything around the stocks is thinner:
* **Options**: aggregates only, for about the last 2 years. Trades, quotes and the greeks/IV/OI snapshot return 403.
* **Indices**: I:SOX/I:NDX from 2023-02-15. I:SPX returns 403, and there is no ICE Semiconductor Index or SOXL/SOXS iNAV.
* **Futures**: aggregates from about 2024-09-28. Trades, quotes and snapshot return 403.
* **Not entitled (403)**: ETF Global (holdings/flows) and Benzinga news.
* **Rate limits**: options, indices and futures calls are capped per minute.

### Cited Findings
- **Probe coverage**: 217 rows in total. 207 base probes (165 returned HTTP 200 and 42 returned 403 in the final paced
  run) plus 10 as-of options history checks (4 returned 200, 6 returned 403) — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv) (`scripts/probe_endpoints.py`, `scripts/probe_options_history.py`).
- **Aggregates (`/v2/aggs/ticker/{T}/range/1/{second|minute|hour|day}/…`)** return 200 for SOXL and SOXS, adjusted
  and unadjusted.
  - Earliest bars fall on 2010-03-11: SOXL's first second and minute bars at 09:56:59/09:56 ET, SOXS's at 09:57:13/09:57.
  - Latest minute bar: 2026-09-25 19:59 ET.
  - Earliest daily bar: 2010-03-11 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
  - `/v2/aggs/ticker/{T}/prev`, `/v1/open-close/{T}/{date}` and grouped daily
    (12,591 US tickers on 2026-09-25) all return 200. For SOXL on 2026-09-25, open-close returned open 149.24,
    close 151.45, `preMarket` 151.2 and `afterHours` 151.75. `/v1/summaries` returns 403 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **Ticks**: `/v3/trades` and `/v3/quotes` (NBBO) return 200 for both tickers.
  - Earliest trade: 2010-03-11 09:56:59 (SOXL) and 09:57:13 (SOXS).
  - Earliest NBBO quote: 10:32:26 (SOXL) and 15:05:11 (SOXS) the same day.
  - Latest ticks: 2026-09-25 ~20:00 ET.
  - `/v2/last/trade` and `/v2/last/nbbo` return 200 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
  - Pagination handled windows of up to 118,735 quotes in 5 minutes (SOXS, 2026-03-11 10:30) — [halfspread_estimate_nbbo_sample.csv](../../analysis/backtests/output/halfspread_estimate_nbbo_sample.csv) (`scripts/estimate_spreads.py`; raw window files in `data/soxlab/nbbo_sample/`).
- **Snapshots (live or delayed)**:
  - `/v2/snapshot/locale/us/markets/stocks/tickers/{T}` and `/v3/snapshot?ticker.any_of=…` return 200.
  - The v3 snapshot's `last_quote.timeframe` and `last_trade.timeframe` read `"REAL-TIME"`. On Sunday 2026-09-27 it
    returned SOXL bid 151.68 / ask 151.75 and last trade 151.45 from the 2026-09-25 session.
  - Evidence: `data/soxlab/reference/probe_raw/snapshot_v3_unified_SOXL.json`; `scripts/daily_tracker.py --live --date 2026-09-25` output (snapshot spread 7¢ SOXL / 5¢ SOXS, `REAL-TIME`).
- **Technical indicators** (`/v1/indicators/{sma,ema,rsi,macd}/{T}`) return 200 at minute and day timespans.
  - First minute values: 2010-03-11 10:09–10:22 (after warm-up). First daily values: 2010-03-30 to 2010-04-16.
  - Latest values: 2026-09-25 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **Reference data** (all 200):
  - **Ticker details with a `date` parameter** give point-in-time shares outstanding. SOXL: 6,050,000 (2019-01-02),
    84,600,000 (2022-01-03), 256,649,999 (2024-01-02), 175,700,060 (2026-09-25). SOXS: 4,059,999; 40,850,000;
    172,420,000; 35,118,272 on the same dates — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
  - **Splits** (`/v3/reference/splits`, identical in `/stocks/v1/splits`). SOXL has 2 records: 2015-05-20 (1→4) and
    2021-03-02 (1→15). SOXS has 10 reverse splits, including 2019-06-28 (10→1), 2020-08-28 (12→1), 2022-03-28 (10→1),
    2024-04-15 (10→1), 2026-03-05 (20→1) and 2026-07-15 (10→1) — [dq_splits.csv](../../analysis/backtests/output/dq_splits.csv); [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
  - **Other reference endpoints**:
    - dividends: 32 SOXL and 26 SOXS records
    - `/vX/reference/tickers/{T}/events`: a single `ticker_change` on 2010-03-11
    - short interest: 2017-12-29 → 2026-09-15
    - daily short volume: 2024-02-06 → 2026-09-25
    - `/vX/reference/financials`: empty for these ETFs
    - Source: [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
  - The `/stocks/v1/*` endpoints need `sort=field.asc|desc`. With `sort=settlement_date&order=desc`, the earliest
    record (2017-12-29) came back instead of the latest (2026-09-15) — `scripts/probe_endpoints.py` (re-test in session log).
- **Market status and holidays**: `/v1/marketstatus/now` and `/v1/marketstatus/upcoming` return 200. `upcoming` lists
  NYSE early closes on 2026-11-27 and 2026-12-24 (14:30–18:00 UTC) and closures such as 2026-11-26 and 2026-12-25 —
  [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv). Historical half-days are not an
  endpoint. The toolkit detects 15 of them (2019–2025) from minute volume — [data_quality_report.md](../../analysis/backtests/output/data_quality_report.md) (`scripts/run_quality.py`).
- **News** (`/v2/reference/news?ticker=`) returns 200.
  - SOXL: earliest article 2021-05-21, latest 2026-09-14, 10 articles in the 365 days to 2026-09-27.
  - SOXS: 2021-05-03 to 2026-02-23, 2 articles in the past year.
  - `/benzinga/v2/news` returns 403 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **ETF Global add-on** (`/etf-global/v1/{constituents,fund-flows,profiles,analytics,taxonomies}`, paths from the
  official client): all 403, "not entitled" — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv); [client source](https://github.com/massive-com/client-python/blob/master/massive/rest/etf_global.py).
- **Options on SOXL/SOXS**:
  - Entitled: the contracts reference (≥1,000 active contracts each; expired contracts listed back to the 2010-06-19
    expiry) and options aggregates (minute/day).
  - Aggregates cover only a rolling ~2-year window. As-of checks on near-the-money calls returned 403 for 2023-06-01,
    2024-06-03 and 2024-09-03, and bars for 2024-10-01 and 2025-01-02.
  - Not entitled (403): options trades, quotes, the chain snapshot (greeks/IV/open interest) and single-contract snapshots.
  - Source: [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv) (`scripts/probe_options_history.py`).
  - Post-reverse-split SOXS options carry adjusted roots, e.g. `O:SOXS1270115C00001000` and `O:SOXS1250117C00022000` — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **Indices**:
  - I:SOX and I:NDX minute and day aggregates return 200 from 2023-02-15 (latest 2026-09-25 16:00). I:SPX returns 403,
    as does `/v3/snapshot/indices`. Index SMA returns 200.
  - A catalog search (`market=indices`) finds PHLX/Nasdaq/Dow Jones semiconductor indices (I:SOX, I:ESOX, I:GSOX,
    I:ASOX, I:DJUSSC, …) and ProShares semiconductor iNAVs (I:USDIV, I:SSGIV).
  - Searches for "Direxion", "SOXL", "SOXS" and "ICE Semiconductor" return nothing — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv); session query of `/v3/reference/tickers?market=indices`.
- **Futures** (paths `/futures/v1/{aggs/{ticker},contracts,products,schedules,market-status,snapshot,trades,quotes,exchanges}`
  from the official client [futures.py](https://github.com/massive-com/client-python/blob/master/massive/rest/futures.py)):
  - products, contracts, schedules, market-status, exchanges and aggregates return 200.
  - The front contracts on 2026-09-25 were NQZ6/ESZ6. NQZ6 1-min bars start 2025-10-01; NQZ4/ESZ4 daily bars start
    2024-09-28; NQZ3/ESZ3 return nothing.
  - Futures trades, quotes and snapshot return 403.
  - `/futures/v1/contracts` is point-in-time: one row per as-of date, so it needs `date=`.
  - Source: [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **Rate limits**: the first unpaced probe got HTTP 429 "You've exceeded the maximum requests per minute" on
  index/futures calls. The final probe paced options/indices/futures at ≤5 calls/min and got no 429s. The 1,488
  monthly stock minute-bar downloads (4 threads) completed in 300 s — `scripts/probe_endpoints.py` (PACED set), `data/soxlab/download.log`.
- **WebSockets** (documented, not run):
  - URL form `wss://{feed}/{market}`, e.g. `wss://socket.massive.com/stocks` (real-time) or
    `wss://delayed.massive.com/stocks`.
  - Auth `{"action":"auth","params":KEY}`, subscribe `{"action":"subscribe","params":"AM.SOXL,…"}`.
  - Event types: `AM` (minute agg), `A` (second agg), `T`, `Q`, `LULD`, `NOI`, `FMV`.
  - Sources: [client websocket models](https://github.com/massive-com/client-python/blob/master/massive/websocket/models/common.py); [client websocket __init__.py](https://github.com/massive-com/client-python/blob/master/massive/websocket/__init__.py).
  - An `AM` message carries `sym, v, o, c, h, l, a, s, e`, and no bar is emitted for a minute without eligible trades — [Massive docs: Aggregates (Per Minute)](https://massive.com/docs/websocket/stocks/aggregates-per-minute).
- **Flat files** (documented, not run): S3-compatible endpoint `https://files.massive.com`, e.g. dataset
  `us_stocks_sip/minute_aggs_v1` delivered as daily files — [Massive flat files overview](https://massive.com/docs/flat-files/stocks/overview); [Massive flat-files blog](https://massive.com/blog/flat-files).
- **Benchmark**: SOXL/SOXS track 3× / −3× the daily return of the ICE (NYSE) Semiconductor Index since 2021-08-25 (PHLX
  SOX before). SOXX tracks the same index — [Direxion product page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs), as compiled in the fund-mechanics notes (mechanics_and_external_data.md).

### Inferences
- The stocks side alone is enough for everything the brief asks: minute and second bars, full tick/NBBO history from
  listing, real-time snapshots, splits and calendar signals. None of the probes depends on the limited families.
- There is no exchange-computed intraday fair value for SOXL/SOXS on this account: no iNAV, no ICE index. The best
  available fair-value proxy is 3 × SOXX (same index) or I:SOX (a different index, and only from 2023-02-15). The
  toolkit therefore uses SOXX, labelled as an assumption.
- Options and futures cannot support backtests before about 2024-09/10 on this plan. Options-flow, gamma or
  futures-lead studies would have only about two years of aggregate bars, with no quotes and no greeks.

### Gaps
- Real-time latency was not measured during market hours: the probe ran on a Sunday. The `REAL-TIME` flag is the only
  evidence. `daily_tracker.py --live` can measure the lag of the last bar against the wall clock on a trading day.
- WebSocket and flat-file access were not exercised. The proxy injects the key only into REST calls, and the brief did
  not require it.
- Historical SOXL.IV / iNAV data, holdings and fund flows were not found under this account.

## 2. What data quirks matter for SOXL/SOXS intraday work, with concrete examples?

### Takeaway
Minute bars are complete and reproducible for SOXL and SOXS from 2022 onward: essentially 0% missing regular-session
minutes, no duplicates, and a re-fetch matched the cache exactly. There are still quirks to handle:
* bars are timestamped at bar start (UTC ms)
* zero-trade minutes are simply absent
* odd lots are excluded from OHLC, while Form-T prints form the extended-hours bars
* the closing cross is in the daily bar but in no minute bar
* fractional share volume appears from 2026-02-23
* SOXS reverse splits make adjusted prices enormous and adjusted volume fractional
* SOXX, the index proxy, has gaps in 2022–2023

### Cited Findings
- **Timestamps and DST**: `t` is the bar start in UTC ms. The 09:30 ET bar is `t=1772807400000` (14:30 UTC) on
  2026-03-06 (EST) and `t=1773063000000` (13:30 UTC) on 2026-03-09 (EDT); similarly 13:30 UTC on 2025-10-31 and
  14:30 UTC on 2025-11-03 — [data_quality_report.md §7](../../analysis/backtests/output/data_quality_report.md). A unit
  test fixes this conversion — `tests/test_data.py::test_bar_start_utc_ms_to_et_across_dst`.
- **Session coverage**: minute bars span 04:00–19:59 ET. SOXL averaged 328.1 pre-market and 233.5 post-market bars per
  day in 2025 (28.4 and 14.9 in 2019). Extended-hours volume share rose from 2.2% (2019) to 14.9% (2026) for SOXL and
  to 17.8% (2026) for SOXS — [dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv).
- **Missing (zero-trade) minutes** (share of RTH minutes without a bar):
  - SOXL: 11.24% (2019), 6.65% (2020), 1.46% (2021), then 0.000–0.004% in 2022–2026.
  - SOXS: 4.13% → 0.025% (2022) → 0.
  - SOXX (the index proxy): 3.57% (2022), 7.12% (2023), 0.82% (2024), 0.13% (2025), 0 (2026).
  - Source: [dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv); [dq_rth_missing_minutes.png](../../analysis/backtests/output/dq_rth_missing_minutes.png).
  - The 0.06% gap in 2020 for QQQ/TQQQ/NVDA is exactly the four market-wide circuit-breaker halts: 2020-03-09
    09:34→09:49, 03-12 09:35→09:50, 03-16 09:30→09:45 and 03-18 12:56→13:11, 14 missing bars each (session check on
    cached QQQ bars).
- **Integrity**: 0 duplicate timestamps, 0 bars off the minute grid, 0 bars with high/low inconsistent with open/close
  and 0 non-positive volumes across the 11,089,176 cached unadjusted bars (the adjusted set has the same count) ([dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv)).
  Re-fetching 12 ticker-months raw (SOXL/SOXS/SOXX × 2019-06, 2022-03, 2024-04, 2026-07) produced 0 raw duplicates,
  0 rows missing on either side and 0 value mismatches — [dq_raw_duplicate_sample.csv](../../analysis/backtests/output/dq_raw_duplicate_sample.csv).
- **Outliers**: using "isolated spikes" (|1-min log return| > 5% followed by an opposite > 5% move), there were 0 in
  the regular session for all 8 tickers and 28 (SOXL) / 25 (SOXS) in extended hours, e.g. SOXL 2020-03-17 08:15–08:19
  — [dq_outliers.csv](../../analysis/backtests/output/dq_outliers.csv); [dq_outlier_examples.csv](../../analysis/backtests/output/dq_outlier_examples.csv).
- **Split adjustment** (`adjusted=true` is split-only):
  - The unadjusted/adjusted factor changes only on split dates: 0 off-date changes for all 7 tickers with splits
    (`/v3/reference/splits?ticker=QQQ` returned no records).
  - At each split the unadjusted open/prior-close ratio matches the split ratio, e.g. SOXS 2026-07-15 expected 10,
    observed 9.633 (4.28 → 41.23); SOXL 2021-03-02 expected 0.0667, observed 0.0673 (638.4 → 42.94). The adjusted
    ratios look like normal gaps (0.9633, 1.009) — [dq_splits.csv](../../analysis/backtests/output/dq_splits.csv).
  - Because of ten reverse splits, adjusted SOXS prices in 2020 are ~$5–8 million and adjusted volumes fall below 1
    share (e.g. 2020-02-04 08:23 close 5.21e6, volume 0.521) — [dq_outlier_examples.csv](../../analysis/backtests/output/dq_outlier_examples.csv).
  - Volume and per-share costs therefore need **unadjusted** bars. Intraday returns are identical in both series.
- **Fractional share volume**: in unadjusted bars, non-integer volume first appears at 2026-02-23 08:00 ET for all 8
  tickers at once, with none before. In 2026 it affects 62.9% of SOXL bars and 45.4% of SOXS bars —
  [data_quality_report.md §1](../../analysis/backtests/output/data_quality_report.md); session check. Trades carry `decimal_size`.
  - In the 2026-09-25 10:15 minute there were 235 fractional SOXL prints (1,126.8 shares) — [dq_bar_rebuild.csv](../../analysis/backtests/output/dq_bar_rebuild.csv).
- **Condition codes excluded from bars**: under the `/v3/reference/conditions` consolidated rules:
  - Odd Lot (37), Form T/Extended Hours (12), Average Price (2), Cash Sale (7), Next Day (20), Price Variation (21),
    Seller (29), Contingent (52) and QCT (53) update volume only.
  - Market Center Official Open (16) and Official Close (15) update nothing.
  - Out-of-sequence (32/33), Derivatively Priced (10) and Bunched Sold (5) update high/low and volume but not
    open/close.
  - Source: [data_quality_report.md §7](../../analysis/backtests/output/data_quality_report.md).
- **Bar rebuild from trades**:
  - SOXL and SOXS 10:15 bars on 2026-09-25 rebuilt from `/v3/trades` under these rules match `/v2/aggs` exactly.
    SOXL: o 149.81, h 149.82, l 148.31, c 149.09, v 543,154, from 7,613 prints of which 5,859 were odd lots.
  - Letting odd lots in would change SOXL's high to 149.87 and close to 149.07.
  - A pre-market bar (04:30) matches only if Form-T prints count toward OHLC, so extended-hours bars are Form-T bars —
    [dq_bar_rebuild.csv](../../analysis/backtests/output/dq_bar_rebuild.csv).
  - Relatedly, bar `vw` falls outside [low, high] in 0.014% of SOXL RTH bars but 6.76% of extended-hours bars (2025) —
    [dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv).
- **Opening and closing crosses** (2026-09-25, NYSE Arca = exchange 11):
  - **Open**: 198,682 SOXL at 149.33 [17, 41] at 09:30:00.293, plus a duplicate record [16]. 84,900 SOXS at 32.93 at
    09:30:00.161.
  - **Close**: 1,038,341 SOXL at 151.45 [8, 41] at **16:00:01.020**, plus a duplicate [15]. 78,519 SOXS at 32.43 at
    16:00:00.234.
  - The daily-bar close equals the cross price (151.45 / 32.43). The 15:59 minute bar closed at 151.35 / 32.46. The
    daily-bar open (149.24) is the first eligible trade, not the opening-cross price (149.33) — [dq_auction_prints.csv](../../analysis/backtests/output/dq_auction_prints.csv); [data_quality_report.md §7](../../analysis/backtests/output/data_quality_report.md).
  - Daily volume minus the sum of all minute-bar volume exceeds the closing-cross size by only 0.1–4.1% on 6/6 SOXL
    test days, e.g. 3,193,214 vs 3,188,420 on 2025-03-12. So the closing cross is in the daily bar and in no minute
    bar. For SOXS the difference is 1.005–1.36× the cross size, meaning other prints are also excluded from minute
    bars — [dq_closing_cross_vs_bars.csv](../../analysis/backtests/output/dq_closing_cross_vs_bars.csv).
  - The official close differed from the last RTH minute close on 91.7% (SOXL) / 85.8% (SOXS) of days, with a median
    absolute gap of 7.1 / 9.5 bps — [dq_daily_vs_minute.csv](../../analysis/backtests/output/dq_daily_vs_minute.csv).
- **Half-days**: 15 early closes were detected (2019-07-03, 2019-11-29, 2019-12-24, 2020-11-27, 2020-12-24, 2021-11-26,
  2022-11-25, 2023-07-03, 2023-11-24, 2024-07-03, 2024-11-29, 2024-12-24, 2025-07-03, 2025-11-28, 2025-12-24). On
  2025-11-28 SOXL had 210 bars and 50.3 M shares from 09:30 to 12:59, then 1 bar (2.2 M shares, the closing cross
  window) from 13:00 to 15:59 — [data_quality_report.md §7](../../analysis/backtests/output/data_quality_report.md).
- **SOXL vs SOXS consistency**:
  - Daily correlation −0.988 to −1.000 per year. The slope of SOXS on SOXL is −0.999 to −1.037; of SOXL on SOXX,
    2.853–2.995.
  - 1-min return correlation rose from −0.840 (2019) to −0.962 (2023), then −0.910 (2026).
  - The since-close divergence (SOXL+SOXS, bps) has p5/p95 of −51.3/+34.0 in 2022 and −59.2/+52.1 in 2026 — [dq_soxl_soxs_consistency.csv](../../analysis/backtests/output/dq_soxl_soxs_consistency.csv).
- **API mechanics**: on aggregates, `limit` counts base (minute) aggregates, so `limit=1` on hour bars can return zero
  hour bars (the probe needed `limit=50000`). The newer endpoints ignore `order` and need `sort=field.asc|desc` —
  [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv) notes; `scripts/probe_endpoints.py`.

### Inferences
- 2022 onward is the window where SOXL/SOXS minute coverage is essentially complete. In 2019–2021, 1.5–11% of SOXL
  RTH minutes are missing, which biases volatility and fill assumptions if the gaps are ignored.
- Lead–lag work with SOXX as the driver is contaminated by stale SOXX prints in 2022–2023 (3.6–7.1% missing minutes).
  NVDA and QQQ are cleaner drivers at the minute level.
- Signals that reference "the close" depend on whether the 15:59 bar or the official close is meant. The two differ
  by a median of 7–10 bps, and the closing-cross volume is invisible in minute bars.

### Gaps
- Late-reported trades and corrections after the session were not audited beyond the reproducibility re-fetch.
- Whether Massive changed the fractional-volume convention retroactively was not examined: the cache was built in
  one pass on 2026-09-27.

## 3. What does the toolkit provide, and how is it validated?

### Takeaway
`soxlab` covers the full chain:
* reproducible downloads of 8 tickers × 2019-01 → 2026-09, adjusted and unadjusted (884 MB of parquet, ~5 min), with
  incremental updates
* data-quality checks
* 97 features that don't look ahead, plus 3 labelled future-return labels
* a cost-aware next-bar-open backtester with stop-first resolution, flat by 15:55, walk-forward, a random baseline and
  lag/shuffle diagnostics
* a daily tracker with a live mode

32 tests pass, including truncation-invariance look-ahead tests on synthetic and real data.

### Cited Findings
- **Data layer** (`soxlab/data.py`, `scripts/download_data.py`):
  - 1,488 monthly parquet files (8 tickers × adjusted/unadjusted × 93 months). The full download script (reference,
    daily, minute) completed in 300 s.
  - Bar counts: SOXL 1,485,107; SOXS 1,416,425; SOXX 841,659; SMH 898,052; NVDA 1,468,029; QQQ 1,628,529; TQQQ
    1,672,740; SQQQ 1,678,635.
  - Daily bars from 2010, splits, dividends and a 1,944-day calendar with 15 half-days.
  - `--update` re-fetches the last and any incomplete month, tracked in `reference/manifest.json`.
  - Source: `data/soxlab/download.log`; `data/soxlab/reference/manifest.json`.
- **Panel builder**: dense 09:30–15:59 arrays that forward-fill only causally. The first version back-filled a missing
  09:30 bar from a later bar; this was found and removed before any backtest — `soxlab/data.py::build_panel`.
- **Features and dictionary**: 39 dictionary rows (38 look-ahead-safe, 1 label row) cover the 97 look-ahead-safe
  columns plus 3 `label_*` columns — [feature_dictionary.csv](../../analysis/backtests/output/feature_dictionary.csv); `soxlab/README.md`.
  - **Implied intraday leverage** L(1+r)/(1+L·r), with r = SOXX return since the prior close. Over 2022–2026 at 15:30
    its p5/p50/p95 is 2.788/2.993/3.268 for SOXL and −3.540/−3.014/−2.578 for SOXS.
  - The **realized since-close multiple** (|r| > 0.25%) has median 2.986 for SOXL (IQR 2.905–3.054) and −2.991 for SOXS.
  - The since-close **tracking gap** vs L·r has median −4.5 bps for SOXL and +10.1 bps for SOXS at 15:30.
  - Source: [feature_leverage_tracking_stats.csv](../../analysis/backtests/output/feature_leverage_tracking_stats.csv).
- **Cost model**:
  - Half-spread from the microstructure file, using the cents column converted at the unadjusted trade price
    (file mtime and sha256 recorded in [battery_run_info.json](../../analysis/backtests/output/battery_run_info.json)).
  - Commission: $0.0035/share/side (ASSUMPTION).
  - SEC Section 31: $5.10 → $22.90 (2022-05-14) → $8.00 (2023-02-27) → $27.80 (2024-05-22) → $0.00 (2025-05-14) →
    $20.60 (2026-04-04) per $1M — [FINRA notice 2022](https://www.finra.org/rules-guidance/notices/information-notice-042122); [FINRA notice 2023](https://www.finra.org/rules-guidance/notices/information-notice-021423); [FINRA notice 2024](https://www.finra.org/sites/default/files/2024-05/Information-Notice-050124.pdf); [FINRA notice 2025](https://www.finra.org/rules-guidance/notices/information-notice-20250424); [SEC FY2026 advisory](https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2). These values come from search extracts; sec.gov and finra.org were blocked for direct fetch.
  - FINRA TAF: $0.000166/share (cap $8.30) → $0.000195 (cap $9.79) from 2026-01-01 — [FINRA TAF](https://www.finra.org/rules-guidance/guidance/trading-activity-fee).
  - My light NBBO sample (10 days × 5 windows) agrees with the microstructure table: SOXL median 1¢ in 2022–2025
    (2–4¢ in 2026); SOXS mostly 1¢ — [halfspread_estimate_nbbo_sample.csv](../../analysis/backtests/output/halfspread_estimate_nbbo_sample.csv).
  - **Average round-trip cost** over the canonical battery trades, by year:

| ticker | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| SOXL | 10.4 | 9.4 | 4.8 | 7.5 | 4.2 |
| SOXS | 18.4 | 14.3 | 17.5 | 24.3 | 32.2 |

    SOXS costs are dominated by its low unadjusted price: median trade price was $7.76 in 2025, where 1¢ and
    $0.0035/share are large in bps (session computation from `data/soxlab/cache/battery_trades_canonical.parquet`).
- **Harness** (`soxlab/backtest.py`):
  - Fills at the next bar open; stop-first when both levels are touched; gap-through stops fill at the open.
  - Flat by 15:55 (12:55 on half-days).
  - Modes: long/short per ticker, and a SOXL/SOXS switch.
  - Outputs: metrics, walk-forward, a random-entry baseline, and lag/shuffle helpers.
  - An independent re-computation of the last-30-minute probe outside the harness reproduced the harness gross (SOXL IS
    −3.49 vs −3.49 bps; OOS −25.61 vs −25.66; SOXS −2.49/−19.13 identical) (session check).
- **Tests**: `python -m pytest -q tests` → 32 passed:
  - 29 synthetic tests: next-open fills, stop-first, gap-through, flat-by-15:55/12:55, iid no-edge vs a look-ahead fill,
    AR(1) lag decay and shuffle null, cost units and sell-side fees, unadjusted-price costs, DST, half-day detection,
    probe wiring, truncation invariance at 7 cut points × 2 tickers, and the labels failing that test.
  - 3 real-data truncation tests on cached 2023-12 → 2024-03 SOXL/SOXS bars.
  - Source: `tests/`.
- **Tracker** (`scripts/daily_tracker.py`): 3,888 rows (SOXL+SOXS, 2019-01-02 → 2026-09-25) with 42 fields. For
  2026-09-25:
  - SOXL: range 4.45%, gap +1.99%, OR30 3.45%, 16 VWAP crosses, high 12:10 / low 10:17, RTH volume 46.5 M, relative
    volume 0.98, implied leverage at the close 2.93, tracking gap −7.2 bps.
  - SOXS: 12 VWAP crosses, relative volume 1.21.
  - The `--live` mode reproduces a session from the API and adds the real-time snapshot spread.
  - Source: [daily_tracker_SOXL_SOXS.csv](../../analysis/backtests/output/daily_tracker_SOXL_SOXS.csv).
  - Median SOXL daily range runs from 4.7% (2019) to 9.2% (2022). Trend days by the tracker's rule are 18–28% of
    SOXL days and 13–26% of SOXS days per year. The most frequent time of the RTH high is 09:30 (221 SOXL days, 265
    SOXS days) and the next most frequent is 15:59 (123 / 85).

### Inferences
- The toolkit can re-derive every published number from raw pulls. Rebuilding the cache takes minutes, and the look-ahead
  safety of the features is enforced by tests rather than asserted.
- Costs vary about 8× across ticker-years (4.2–32.2 bps round trip), mostly because the unadjusted price level moves
  through splits and trends. A constant-bps cost assumption would misstate SOXS results badly.

### Gaps
- The microstructure half-spread table comes from 2 sample days per year. For SOXS it may misstate costs in the parts
  of a year before or after a reverse split, when the cents spread applied to a very different price level.
- Commission is an assumption. The battery also reports a zero-commission net column (`avg_net_bps_zero_commission`).

## 4. What does the behavior-probe battery reveal about which intraday behaviors persist out of sample?

### Takeaway
Only opening-range breakout follow-through produced a positive gross return in both the in-sample and out-of-sample
periods for both SOXL and SOXS. It is also the only probe with a positive net return in both periods: SOXL
long/short for all three windows, and the switch mode for the 15-minute window. Even so, the out-of-sample net
t-statistic is at most 1.19, 2026 year-to-date is negative, and no positive result survives multiple-testing
adjustment.

The other behaviors split into three groups:
* **Real but smaller than costs.** 1-min EMA trend persistence earns +2–3 bps gross against 6–8.5 bps round-trip cost on SOXL.
* **Unstable.** Reversal or momentum after large moves, gap fill and VWAP-trend change sign between periods.
* **Changed character.** Last-30-minute momentum in 2020–2021 became reversal from 2023 onward.

Minute-level lead–lag from NVDA/SOXX/QQQ to SOXL is about 0.01–0.02 in correlation and cannot be traded at the next
bar's open.

### Cited Findings
- **Design.**
  - The battery runs 16 probes × 3 modes: SOXL long/short, SOXS long/short, and a switch (bullish → long SOXL,
    bearish → long SOXS), all on its own trade-price minute bars.
  - Every trade fills at the next bar open. Costs are half-spread per side (cents → bps at the unadjusted price) plus
    $0.0035/share per side plus SEC/TAF on sells, and positions are flat by 15:55.
  - Parameters were fixed before any run (`soxlab/strategies.py::PROBES`).
  - IS 2022-01-03 → 2024-09-30 has 689 sessions; OOS 2024-10-01 → 2026-09-25 has 498 (session counts from `data/soxlab/reference/calendar.parquet`).
  - Each summary row also carries:
    - win rate and profit factor (gross and net)
    - max drawdown of the additive daily P&L, as % of one notional
    - exposure (share of RTH minutes in a position) and average hold
  - Example, orb15 SOXL L/S OOS: win rate 43.3%, net profit factor 1.17, max drawdown 90.4% of notional, exposure
    66.5%, average hold 261 min. For ema_1m SOXL OOS the same fields are 28.0%, 0.88, 354.5%, 85.1% and 20 min.
  - Source: [battery_summary.csv](../../analysis/backtests/output/battery_summary.csv); [battery_run_info.json](../../analysis/backtests/output/battery_run_info.json) (`scripts/run_battery.py`).
- **Canonical results** (average bps per trade, all sides). The t-statistic is on daily net P&L:

| probe | mode | IS trades | IS gross | IS net | OOS trades | OOS gross | OOS net | OOS Sharpe net | OOS t (daily) |
|---|---|---|---|---|---|---|---|---|---|
| orb5 | SOXL L/S | 688 | +27.9 | +19.4 | 497 | +11.1 | +4.5 | +0.19 | +0.26 |
| orb5 | SOXS L/S | 688 | +25.8 | +6.5 | 497 | +3.5 | -21.0 | -0.87 | -1.22 |
| orb5 | switch | 688 | +27.7 | +14.4 | 497 | +7.7 | -6.2 | -0.26 | -0.37 |
| orb15 | SOXL L/S | 686 | +35.1 | +26.6 | 492 | +30.4 | +24.1 | +0.85 | +1.19 |
| orb15 | SOXS L/S | 686 | +30.7 | +12.2 | 492 | +20.5 | -3.8 | -0.13 | -0.19 |
| orb15 | switch | 686 | +33.6 | +19.8 | 492 | +23.4 | +9.1 | +0.34 | +0.47 |
| orb30 | SOXL L/S | 671 | +26.8 | +18.3 | 476 | +16.9 | +10.8 | +0.40 | +0.56 |
| orb30 | SOXS L/S | 668 | +30.1 | +12.6 | 474 | +15.4 | -8.7 | -0.31 | -0.43 |
| orb30 | switch | 671 | +26.0 | +12.8 | 476 | +13.5 | -0.5 | -0.02 | -0.02 |
| vwap_reversion | SOXL L/S | 2120 | -0.7 | -9.0 | 1352 | -4.3 | -10.8 | -2.09 | -2.94 |
| vwap_reversion | SOXS L/S | 2151 | -1.6 | -20.6 | 1450 | -0.4 | -25.2 | -4.82 | -6.78 |
| vwap_reversion | switch | 2147 | -2.1 | -15.5 | 1377 | -3.5 | -17.4 | -3.20 | -4.50 |
| vwap_trend | SOXL L/S | 8904 | +1.5 | -6.9 | 6649 | -0.9 | -7.3 | -2.91 | -4.09 |
| vwap_trend | SOXS L/S | 9223 | +1.9 | -16.5 | 7446 | -0.8 | -29.0 | -7.00 | -9.85 |
| vwap_trend | switch | 8904 | +1.3 | -11.8 | 6649 | -0.9 | -16.4 | -5.54 | -7.79 |
| mom_1m_z3 | SOXL L/S | 1412 | +2.4 | -5.9 | 1157 | -0.9 | -6.9 | -1.68 | -2.36 |
| mom_1m_z3 | SOXS L/S | 1340 | +3.0 | -13.3 | 1049 | -0.9 | -21.7 | -4.49 | -6.31 |
| mom_1m_z3 | switch | 1473 | +2.7 | -11.8 | 1200 | -0.2 | -16.9 | -4.15 | -5.84 |
| rev_1m_z3 | SOXL L/S | 1412 | -2.4 | -10.6 | 1157 | +0.9 | -5.1 | -1.23 | -1.74 |
| rev_1m_z3 | SOXS L/S | 1340 | -3.0 | -19.3 | 1049 | +0.9 | -19.9 | -3.98 | -5.60 |
| rev_1m_z3 | switch | 1473 | -2.0 | -13.1 | 1200 | -0.5 | -14.0 | -4.16 | -5.85 |
| mom_5m_z3 | SOXL L/S | 544 | -3.2 | -11.2 | 433 | +13.4 | +7.1 | +0.63 | +0.89 |
| mom_5m_z3 | SOXS L/S | 453 | -4.5 | -18.4 | 329 | +16.3 | +1.4 | +0.10 | +0.14 |
| mom_5m_z3 | switch | 561 | -1.8 | -17.4 | 447 | +11.3 | -5.0 | -0.47 | -0.66 |
| rev_5m_z3 | SOXL L/S | 544 | +3.2 | -4.8 | 433 | -13.4 | -19.7 | -1.71 | -2.41 |
| rev_5m_z3 | SOXS L/S | 453 | +4.5 | -9.4 | 329 | -16.3 | -31.1 | -2.24 | -3.14 |
| rev_5m_z3 | switch | 561 | +2.5 | -7.6 | 447 | -14.1 | -26.2 | -2.00 | -2.81 |
| ema_1m | SOXL L/S | 10837 | +2.7 | -5.8 | 8023 | +2.0 | -4.0 | -2.21 | -3.10 |
| ema_1m | SOXS L/S | 11049 | +2.4 | -15.3 | 8555 | +0.7 | -26.1 | -8.51 | -11.97 |
| ema_1m | switch | 10837 | +2.5 | -10.4 | 8023 | +1.9 | -13.5 | -6.37 | -8.95 |
| ema_5m | SOXL L/S | 1764 | +1.8 | -6.6 | 1315 | +2.4 | -3.6 | -0.38 | -0.54 |
| ema_5m | SOXS L/S | 1779 | +1.5 | -15.6 | 1310 | +4.4 | -20.0 | -1.98 | -2.79 |
| ema_5m | switch | 1764 | +1.2 | -11.5 | 1315 | +2.4 | -12.8 | -1.31 | -1.85 |
| last30_day | SOXL L/S | 689 | -3.5 | -11.9 | 497 | -25.7 | -31.2 | -3.74 | -5.26 |
| last30_day | SOXS L/S | 686 | -2.5 | -20.1 | 498 | -19.1 | -43.6 | -5.23 | -7.35 |
| last30_day | switch | 689 | -3.9 | -16.3 | 497 | -22.5 | -36.4 | -4.81 | -6.76 |
| last30_first30 | SOXL L/S | 686 | -3.7 | -12.1 | 495 | -14.6 | -20.2 | -2.38 | -3.34 |
| last30_first30 | SOXS L/S | 688 | -3.8 | -21.4 | 495 | -8.1 | -32.5 | -3.83 | -5.38 |
| last30_first30 | switch | 686 | -4.3 | -17.0 | 495 | -11.9 | -25.4 | -3.22 | -4.52 |
| leadlag_nvda | SOXL L/S | 9930 | +0.5 | -7.9 | 7154 | -0.5 | -6.4 | -12.34 | -17.35 |
| leadlag_nvda | SOXS L/S | 9930 | +0.6 | -16.6 | 7154 | -0.0 | -24.2 | -14.63 | -20.57 |
| leadlag_nvda | switch | 9930 | +0.6 | -12.5 | 7154 | -0.2 | -15.4 | -16.30 | -22.91 |
| leadlag_soxx | SOXL L/S | 10589 | +0.0 | -8.4 | 7095 | -0.1 | -6.1 | -11.76 | -16.53 |
| leadlag_soxx | SOXS L/S | 10589 | +0.1 | -16.8 | 7095 | +0.6 | -23.3 | -14.83 | -20.85 |
| leadlag_soxx | switch | 10589 | +0.2 | -13.2 | 7095 | +0.4 | -15.6 | -15.80 | -22.21 |
| gap_fill | SOXL L/S | 139 | -34.3 | -42.1 | 146 | -10.7 | -16.9 | -0.27 | -0.38 |
| gap_fill | SOXS L/S | 128 | -54.7 | -72.0 | 108 | +46.2 | +23.2 | +0.31 | +0.44 |
| gap_fill | switch | 139 | -46.8 | -61.6 | 146 | -24.0 | -45.2 | -0.70 | -0.98 |

  Source: [battery_summary.csv](../../analysis/backtests/output/battery_summary.csv); chart [battery_is_vs_oos.png](../../analysis/backtests/output/battery_is_vs_oos.png); equity curves [battery_equity_curves.png](../../analysis/backtests/output/battery_equity_curves.png).
- **Yearly breakdown** (gross / net bps per trade; 2019–2021 are pre-sample years never used for selection; 2026 is
  year-to-date). The half-spread table starts in 2022, so net values for 2019–2021 use the nearest-year (2022) cents
  spread at those years' prices:

| probe | mode | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| orb5 | SOXL L/S | +12.4 / +11.2 | -0.5 / -1.4 | +14.9 / +11.5 | +37.0 / +26.6 | +20.2 / +10.7 | +29.9 / +25.1 | +14.0 / +6.5 | -3.5 / -9.3 |
| orb5 | SOXS L/S | +10.5 / -17.6 | +0.5 / -30.3 | +14.6 / -30.8 | +31.8 / +8.1 | +23.3 / +9.2 | +25.2 / +8.1 | +9.2 / -14.6 | -16.1 / -47.2 |
| orb15 | SOXL L/S | +2.2 / +1.0 | -4.1 / -5.0 | +44.7 / +41.3 | +51.6 / +41.2 | +22.1 / +12.6 | +32.1 / +27.3 | +61.2 / +53.8 | -13.1 / -18.1 |
| orb15 | SOXS L/S | +3.8 / -22.5 | -4.4 / -33.2 | +44.5 / +2.6 | +48.7 / +26.9 | +15.1 / +1.1 | +30.6 / +13.6 | +49.2 / +25.8 | -24.5 / -55.5 |
| orb30 | SOXL L/S | +2.4 / +1.1 | -12.4 / -13.3 | +22.3 / +18.8 | +48.4 / +38.1 | +9.0 / -0.5 | +25.7 / +20.9 | +44.3 / +36.9 | -29.2 / -33.4 |
| orb30 | SOXS L/S | +3.2 / -20.6 | -4.7 / -30.0 | +19.9 / -17.7 | +53.7 / +34.5 | +13.3 / -0.7 | +25.6 / +8.5 | +46.9 / +23.5 | -36.8 / -67.3 |
| vwap_reversion | SOXL L/S | -2.6 / -3.8 | -1.1 / -2.1 | -3.5 / -6.9 | -1.7 / -11.7 | +1.1 / -8.4 | +0.5 / -4.2 | -5.1 / -12.7 | -7.4 / -12.6 |
| vwap_reversion | SOXS L/S | +0.2 / -23.7 | -2.0 / -29.4 | -5.9 / -44.6 | -2.2 / -24.6 | +1.4 / -12.7 | -3.6 / -22.2 | -1.8 / -26.0 | +1.3 / -29.1 |
| vwap_trend | SOXL L/S | -0.6 / -1.8 | +6.2 / +5.4 | +4.6 / +1.1 | +4.9 / -5.5 | -0.5 / -9.9 | +0.0 / -4.8 | -0.6 / -8.2 | -1.6 / -6.3 |
| vwap_trend | SOXS L/S | +0.1 / -25.1 | +6.2 / -19.6 | +4.5 / -34.5 | +6.0 / -13.5 | -0.9 / -15.7 | +0.0 / -18.5 | -0.3 / -27.4 | -1.0 / -38.1 |
| mom_1m_z3 | SOXL L/S | +1.7 / +0.5 | +3.2 / +2.3 | -1.5 / -4.7 | -0.2 / -10.5 | -0.6 / -10.2 | +6.9 / +2.2 | -1.2 / -8.8 | -1.1 / -5.1 |
| mom_1m_z3 | SOXS L/S | +2.2 / -16.9 | +5.8 / -17.3 | -1.3 / -35.0 | +4.1 / -14.2 | -0.9 / -14.7 | +5.0 / -9.6 | -3.9 / -25.5 | +2.0 / -21.4 |
| rev_1m_z3 | SOXL L/S | -1.7 / -2.9 | -3.2 / -4.1 | +1.5 / -1.8 | +0.2 / -10.2 | +0.6 / -8.9 | -6.9 / -11.6 | +1.2 / -6.4 | +1.1 / -2.9 |
| rev_1m_z3 | SOXS L/S | -2.2 / -21.2 | -5.8 / -29.0 | +1.3 / -32.3 | -4.1 / -22.4 | +0.9 / -12.9 | -5.0 / -19.5 | +3.9 / -17.6 | -2.0 / -25.5 |
| mom_5m_z3 | SOXL L/S | +2.2 / +1.0 | +5.5 / +4.6 | -1.5 / -5.0 | -2.7 / -12.6 | -10.6 / -20.0 | +8.2 / +3.4 | +16.3 / +8.6 | +5.1 / +1.1 |
| mom_5m_z3 | SOXS L/S | +6.8 / -10.7 | +10.7 / -10.8 | +1.2 / -32.1 | +0.9 / -13.2 | -16.7 / -30.0 | +7.0 / -5.5 | +19.6 / +1.8 | +11.1 / -2.1 |
| rev_5m_z3 | SOXL L/S | -2.2 / -3.3 | -5.5 / -6.5 | +1.5 / -2.1 | +2.7 / -7.1 | +10.6 / +1.2 | -8.2 / -13.0 | -16.3 / -24.1 | -5.1 / -9.1 |
| rev_5m_z3 | SOXS L/S | -6.8 / -24.2 | -10.7 / -32.2 | -1.2 / -34.5 | -0.9 / -15.0 | +16.7 / +3.3 | -7.0 / -19.5 | -19.6 / -37.4 | -11.1 / -24.3 |
| ema_1m | SOXL L/S | -1.2 / -2.4 | +3.0 / +2.1 | -0.3 / -3.8 | +4.0 / -6.7 | +0.4 / -8.9 | +2.9 / -1.9 | +3.0 / -4.4 | +1.7 / -2.5 |
| ema_1m | SOXS L/S | -0.6 / -23.1 | +2.4 / -22.6 | +0.1 / -36.3 | +3.4 / -14.7 | +0.7 / -13.6 | +1.8 / -16.3 | +1.8 / -23.1 | +0.4 / -35.4 |
| ema_5m | SOXL L/S | -6.3 / -7.5 | +10.8 / +10.0 | +11.5 / +8.0 | -2.8 / -13.3 | +10.9 / +1.6 | -1.0 / -5.8 | +3.5 / -4.1 | +0.3 / -3.6 |
| ema_5m | SOXS L/S | -3.7 / -27.0 | +7.4 / -17.2 | +11.7 / -24.1 | -4.3 / -21.5 | +11.6 / -2.8 | -2.0 / -19.5 | +8.6 / -14.9 | -0.0 / -31.2 |
| last30_day | SOXL L/S | -2.9 / -4.1 | +30.6 / +29.7 | +15.7 / +12.3 | +4.0 / -6.4 | -11.7 / -21.1 | -9.8 / -14.6 | -29.8 / -37.2 | -18.2 / -21.3 |
| last30_day | SOXS L/S | -3.4 / -27.3 | +31.9 / +6.2 | +17.7 / -20.4 | +4.0 / -15.3 | -11.0 / -25.0 | -7.5 / -24.4 | -22.8 / -46.6 | -10.6 / -41.6 |
| last30_first30 | SOXL L/S | -1.5 / -2.7 | +17.5 / +16.6 | +3.5 / +0.0 | -7.7 / -18.1 | -5.3 / -14.7 | -3.0 / -7.8 | -21.0 / -28.4 | -3.0 / -6.1 |
| last30_first30 | SOXS L/S | -2.1 / -25.8 | +21.6 / -4.0 | +5.0 / -33.2 | -9.3 / -28.7 | -5.2 / -19.3 | +0.4 / -16.7 | -11.7 / -35.5 | -0.9 / -31.7 |
| leadlag_nvda | SOXL L/S | +1.2 / -0.0 | +2.6 / +1.6 | +0.3 / -3.2 | +1.9 / -8.3 | -0.6 / -10.0 | +0.0 / -4.8 | -0.9 / -8.3 | -0.0 / -4.0 |
| leadlag_nvda | SOXS L/S | +1.2 / -20.4 | +2.6 / -21.1 | +0.8 / -34.4 | +1.8 / -16.2 | -0.6 / -14.7 | +0.4 / -16.9 | -0.3 / -24.0 | +0.6 / -29.6 |
| leadlag_soxx | SOXL L/S | +0.7 / -0.4 | +1.4 / +0.5 | +0.7 / -2.8 | +0.9 / -9.3 | -0.9 / -10.3 | -0.0 / -4.8 | -0.4 / -7.9 | +0.4 / -3.6 |
| leadlag_soxx | SOXS L/S | +0.8 / -20.5 | +1.5 / -22.3 | +1.3 / -33.3 | +1.0 / -16.4 | -0.9 / -15.1 | +0.0 / -17.0 | +0.4 / -22.8 | +1.3 / -29.3 |
| gap_fill | SOXL L/S | +17.6 / +16.4 | -39.5 / -40.4 | -53.8 / -56.5 | -116.0 / -126.8 | -16.5 / -25.5 | -6.5 / -11.2 | -21.4 / -28.6 | +6.0 / +0.6 |
| gap_fill | SOXS L/S | +24.7 / -8.4 | -20.5 / -38.5 | -75.6 / -122.1 | -194.3 / -212.5 | +45.2 / +31.1 | +8.1 / -8.6 | +66.4 / +44.4 | +42.6 / +14.3 |

  Source: [battery_yearly.csv](../../analysis/backtests/output/battery_yearly.csv).
- **Breakout follow-through (ORB 5/15/30).**
  - **Gross.** All 12 ticker × window × period cells are positive. IS: SOXL +27.9/+35.1/+26.8, SOXS +25.8/+30.7/+30.1.
    OOS: SOXL +11.1/+30.4/+16.9, SOXS +3.5/+20.5/+15.4 bps.
  - **Noise.** The per-trade gross standard error is 15–20 bps; daily gross t-statistics are 1.72–2.28 IS and 0.20–1.50 OOS.
  - **Both sides contribute on SOXL** (orb15 gross by side): IS long +55.7 / short +16.2; OOS long +40.8 / short +18.3 —
    [battery_summary.csv](../../analysis/backtests/output/battery_summary.csv) (side rows).
  - **Net OOS.** SOXL +4.5/+24.1/+10.8, SOXS −21.0/−3.8/−8.7, switch (orb15) +9.1.
  - **Against the random-side null** (same days and holding times, random entry time and direction, 100 draws), orb15
    ranks at the 98th (IS) and 97th (OOS) percentile for SOXL and the 100th/86th for SOXS. orb5 and orb30 rank at the
    76th/78th percentile OOS for SOXL — [battery_random_baseline.csv](../../analysis/backtests/output/battery_random_baseline.csv).
  - **Walk-forward.** Rolling 24-month train / 6-month test, 10 windows, 2022-01 → 2026-09: orb15 SOXL stitched net
    +20.9 bps/trade (Sharpe 0.88, t 1.91); SOXS +2.6.
  - **In-sample selection.** Choosing between "no target" and "2R target" on IS picked the 2R target, which delivered
    OOS net +12.3 bps (SOXL), below the canonical +24.1 — [battery_walkforward.csv](../../analysis/backtests/output/battery_walkforward.csv); [battery_is_selected_oos.csv](../../analysis/backtests/output/battery_is_selected_oos.csv).
  - **Timing.** One extra bar of delay lowers orb15 SOXL gross from 33.2 to 25.2 bps (2022–2026) — [battery_timing_diagnostics.csv](../../analysis/backtests/output/battery_timing_diagnostics.csv).
  - **By year** (orb15 SOXL gross): 2019 +2.2, 2020 −4.1, 2021 +44.7, 2022 +51.6, 2023 +22.1, 2024 +32.1, 2025 +61.2,
    2026 year-to-date −13.1.
- **Mean reversion.**
  - **VWAP ±2σ reversion** (exit at VWAP, stop at 3σ, ≤60 min): gross IS −0.7 (SOXL) / −1.6 (SOXS), OOS −4.3 / −0.4
    bps. It sits at the 14th–48th percentile of the random null, and net is −9 to −25.
  - **Reversal after a >3σ 1-min move** (hold 5 min): gross IS −2.35 / −2.97, then OOS +0.90 / +0.89. The sign flips.
  - **Reversal after a >3σ 5-min move** (hold 15): IS +3.2 / +4.5, then OOS −13.4 / −16.3 (1st–2nd percentile of the
    null OOS). The sign flips.
  - **Gap fill** (abs(gap) > 0.5 ATR, 108–146 trades per period): SOXL gross IS −34.3, OOS −10.7; SOXS −54.7, then
    +46.3. The per-trade SE is 44–53 bps. In 2022, fading gaps lost −116 (SOXL) and −194 (SOXS) bps gross per trade.
  - Source: [battery_summary.csv](../../analysis/backtests/output/battery_summary.csv); [battery_random_baseline.csv](../../analysis/backtests/output/battery_random_baseline.csv); [battery_yearly.csv](../../analysis/backtests/output/battery_yearly.csv).
- **Momentum / trend.**
  - **EMA(9/21) 1-min crossover.** Gross IS +2.73 (SOXL, t 2.75) / +2.40 (SOXS, t 2.50); OOS +1.99 (t 1.60) / +0.75
    (t 0.59), over roughly 8,000–11,000 trades per period. It ranks at the 99th/97th percentile of the random null
    (SOXL IS/OOS) and is positive in 6 of 8 calendar years for SOXL.
    - Average round-trip cost is 8.5 (IS) and 6.0 (OOS) bps for SOXL, so net is −5.8 / −4.0.
    - With zero commission, OOS net is still −1.9 (SOXL) and −15.2 (SOXS).
  - **EMA 5-min**: gross +1.8 / +2.4 (SOXL) with SE 4.5–6.3 bps, indistinguishable from zero.
  - **VWAP trend-follow**: gross +1.5 IS, −0.9 OOS (SOXL).
  - **Momentum after a >3σ 1-min move**: +2.35 IS, −0.90 OOS.
  - **Momentum after a >3σ 5-min move**: −3.2 IS, +13.4 OOS (t 1.66). The sign flips.
  - **Last-30-minute momentum** (sign of the prior close → 15:30 return; trade 15:30 → 15:55 open):
    - SOXL gross −3.5 IS (t −0.75) and −25.7 OOS (t −4.34); SOXS −2.5 and −19.1 (t −3.32). This is reversal, not momentum.
    - SOXL by year: +30.6 (2020), +15.7 (2021), +4.0 (2022), −11.7 (2023), −9.8 (2024), −29.8 (2025), −18.2 (2026).
    - The first-30-minute signal variant shows the same pattern (SOXL IS −3.7, OOS −14.6).
    - A re-computation outside the harness reproduced these gross values (−3.49 / −25.61).
    - Source: [battery_summary.csv](../../analysis/backtests/output/battery_summary.csv); [battery_yearly.csv](../../analysis/backtests/output/battery_yearly.csv).
- **Lead–lag** (driver move → SOXL next minute).
  - **Contemporaneous 1-min correlation of SOXL** with NVDA / SOXX / QQQ is 0.83 / 0.91 / 0.88 IS and 0.69 / 0.98 /
    0.85 OOS.
  - **Driver leading by one minute**: 0.023 / 0.019 / 0.022 IS and 0.012 / 0.014 / 0.011 OOS.
  - **SOXX lagging SOXL by one minute**: 0.087 IS and 0.026 OOS. SOXX follows SOXL, consistent with SOXX's missing
    minutes.
  - Source: [leadlag_xcorr.csv](../../analysis/backtests/output/leadlag_xcorr.csv); [leadlag_xcorr.png](../../analysis/backtests/output/leadlag_xcorr.png).
  - **The probe** (driver >2σ 1-min move → trade the ETF at the next open, hold 1 min):
    - NVDA→SOXL gross +0.48 IS (t 1.89) and −0.48 OOS; SOXX→SOXL 0.00 / −0.08.
    - Net is −6 to −8 (SOXL) and −16 to −24 (SOXS).
    - The same signal filled at the signal bar's own open, which is look-ahead and not tradable, would earn +38.7
      (NVDA) and +44.1 (SOXX) bps gross — [battery_timing_diagnostics.csv](../../analysis/backtests/output/battery_timing_diagnostics.csv).
- **Harness sanity on real data** (2022–2026, gross bps). The look-ahead fill (lag −1) inflates every
  short-horizon signal; for example, momentum after a 1-min move goes from +0.9 to +69.3 and EMA 1-min from +2.4 to
  +36.0. Day-shuffled signals give −2.4 to +5.6 bps for every probe except ORB and gap fill, whose per-trade noise
  is ±15–53 bps — [battery_timing_diagnostics.csv](../../analysis/backtests/output/battery_timing_diagnostics.csv).
- **Multiple testing** (48 canonical tests per period, daily t → normal p, Benjamini–Hochberg):
  - OOS: 7 of 48 have positive net. The best is orb15 SOXL L/S (t 1.19, p 0.23, BH q 0.33). None has q < 0.30.
    30 are significantly *negative* (q < 0.05), driven by costs.
  - IS: 9 positive net, all ORB; the best is orb15 SOXL (t 1.73, q 0.12).
  - Source: [battery_multiple_testing.csv](../../analysis/backtests/output/battery_multiple_testing.csv).

### Inferences
- Two probes rank at or above the 97th percentile of the random-side null in both periods for SOXL: orb15 (98th/97th)
  and ema_1m (99th/97th, gross). Neither is established beyond noise after multiple-testing adjustment.
- The EMA effect is persistent but sub-cost: the harness finds a gross edge of +2–3 bps per trade, against a 4–10 bps
  round-trip cost floor for SOXL.
- SOXS results are systematically worse net, even where gross is similar, because its low unadjusted price makes 1¢
  spreads and per-share commissions expensive in bps. The same signal is cheaper to express through SOXL (long/short
  or switch).
- The last-30-minute result is the clearest behavior *change*: 2020–2021 momentum, 2023–2026 reversal. The evidence
  fits a regime-dependent effect better than a stable anomaly in either direction.
- Minute bars cannot see lead–lag between these tickers: the information shows up within the same minute.
  Sub-minute (second bars or trades) data would be needed to test it properly, and the account has that data.

### Gaps
- Stops are checked on bar high/low, which exclude odd lots. The timing of intra-bar stop/target touches is unknown.
- ORB's SOXL result coincides with a strongly rising SOXL price. Unadjusted SOXL went from $30.81 to $300.77 in the
  12 months to 2026-09-25 per the microstructure price table
  ([price_levels.csv](../../analysis/microstructure/output/price_levels.csv)). Separating breakout follow-through from
  drift needs a longer or more varied sample.
- No regime conditioning was tried: volatility buckets, events, or gap size × ORB. Conditioning adds tests and so
  multiple-testing burden.

## 5. What are the limitations of these minute-bar backtests?

### Takeaway
The harness is deliberately conservative about timing: next-bar-open fills, stop-first, and flat before the close.
It still approximates execution with trade-price bars and sampled spreads. It has no queue, fill-probability,
partial-fill or impact model. The battery ran 96 canonical tests plus grids, so any single positive result must be
read against the multiple-testing tables.

### Cited Findings
- **Fill assumptions.**
  - Entries and exits fill at the next bar's open, meaning the first eligible trade of that minute, plus a modelled
    half-spread per side.
  - Stops fill at the stop level, or at a worse gapped open. Targets fill at the level, or at a better gapped open.
  - If a bar touches both, the stop is assumed first.
  - Source: `soxlab/backtest.py`; tests `test_stop_first_when_both_touched`, `test_stop_gap_through_fills_at_open`.
- **Trade-price bars, not quotes.**
  - Bar OHLC excludes odd lots (77% of prints in the SOXL 10:15 sample minute) and the closing cross. Extended-hours
    bars are Form-T prints.
  - A bar open may therefore sit at the bid or the ask, and the half-spread adjustment is an average, not
    trade-specific — [dq_bar_rebuild.csv](../../analysis/backtests/output/dq_bar_rebuild.csv); [data_quality_report.md](../../analysis/backtests/output/data_quality_report.md).
- **No queue modelling, no partial fills, no market impact.** The trade notional is fixed at $25,000 (ASSUMPTION). No
  borrow or locate cost is charged for intraday shorts. LULD halts are not modelled beyond missing bars —
  `soxlab/config.py`; `soxlab/costs.py`.
- **Spread-sample risk.**
  - The half-spread table comes from 2 sample days per ticker-year, in 30-minute buckets.
  - Around SOXS reverse splits, the price level within a year differs by up to 20×. A per-year cents figure can then
    misstate bps costs.
  - A separate 10-day NBBO sample reproduced the same median cents (1¢ for SOXL 2022–2025) —
    [halfspread_estimate_nbbo_sample.csv](../../analysis/backtests/output/halfspread_estimate_nbbo_sample.csv).
- **Multiple testing and selection.**
  - 16 probes × 3 modes × 2 periods = 96 canonical rows, plus grids of 1–8 variants per probe and 10 walk-forward
    windows. BH/Bonferroni adjustments are in [battery_multiple_testing.csv](../../analysis/backtests/output/battery_multiple_testing.csv).
  - In-sample selection did not beat the canonical parameters OOS for ORB (orb15 SOXL +12.3 vs +24.1 net) —
    [battery_is_selected_oos.csv](../../analysis/backtests/output/battery_is_selected_oos.csv).
- **Null design matters.** A first version of the random-entry baseline kept each trade's side and realized holding
  time. It produced impossible "random" returns (+68 to +170 bps gross for ORB across the two flawed variants)
  because the side and hold encode the signal's outcome. The published null uses random sides — `soxlab/backtest.py::random_entry_baseline` docstring.
- **Sample and regime.**
  - Only about 2.7 years IS and 2 years OOS.
  - SOXL's price path in the OOS was extreme: $30.81 → $300.77 unadjusted within 12 months.
  - 2019–2021 minute data has 1.5–11% missing SOXL minutes, so pre-2022 years are informative only as a
    robustness check — [dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv).
- **Index proxy.** Intraday leverage and tracking features use SOXX as the index. SOXX had 3.6–7.1% missing RTH minutes
  in 2022–2023 and lags SOXL by about a minute (corr 0.087 at k = −1, IS) — [dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv); [leadlag_xcorr.csv](../../analysis/backtests/output/leadlag_xcorr.csv).

### Inferences
- Positive-looking minute-bar results of the size seen here (tens of bps per trade with SE ~15–20 bps) need either
  much longer samples or tick-level fill simulation before they can be distinguished from noise and drift.
- For the short-horizon probes (1–5 minute holds), the harness's cost floor exceeds every gross effect found.
  Conclusions about them are therefore more sensitive to fill and cost modelling (for example, passive limit fills)
  than to signal parameters.

### Gaps
- There is no trade-level (quote-conditioned) execution simulation. The `/v3/quotes` data needed for one exists on
  this account, but was only sampled for spreads.
- The effect of the 15:55 flat rule, which excludes the closing auction and last 5 minutes, was not compared with a
  hold-to-close variant.
- Cost-table provenance (added by the coordinator after this analyst's session ended): the battery used an earlier
  draft of `analysis/microstructure/output/cost_model_halfspread.csv` (sha256 96aafb46…, saved verbatim as
  `analysis/backtests/output/cost_table_used_by_battery.csv`). Among SOXL/SOXS rows the only difference from the final
  table is SOXL 2026 10:00–10:30 (median spread 5¢ → 6¢, ≈ +0.33 bp per side at ~$150). That bucket touches only
  2026 SOXL trades, so reported net figures would move by well under 1 bp per affected trade and no conclusion
  changes. `scripts/run_battery.py --cost-table <path>` reproduces the published run exactly.

## Data and backtest verdict: is there enough to track and backtest?

### Takeaway
Yes, for SOXL/SOXS intraday tracking and minute-level backtesting. The account provides:
* second-, minute- and day-level bars and full tick/NBBO history from the 2010 listing, current to 2026-09-25
* real-time snapshots
* splits, calendar signals and short data

Since 2022 the data is clean: about 0% missing RTH minutes, no duplicates, a re-fetch reproduced the cache exactly,
and split factors change only on split dates. `soxlab` turns this into a reproducible, look-ahead-tested pipeline
with a realistic cost model and a daily tracker.

There is not enough for:
* options-, futures- or index-driven studies before about 2024-09 (2023-02 for I:SOX)
* an intraday fair value: no iNAV and no ICE index
* holdings or flow data

The first battery found one behavior with consistent positive gross follow-through (opening-range breakouts). It is
not statistically established after adjustment and was negative in 2026 year-to-date. The rest are sub-cost, unstable
or regime-dependent.

### Cited Findings
- **Stock entitlement is complete.** 200s on aggregates (second→day), trades, NBBO quotes, snapshots (`REAL-TIME`),
  indicators and reference data. Earliest records are 2010-03-11 for both tickers — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **Data quality 2022+**: 0.000–0.025% missing RTH minutes (SOXL/SOXS), 0 duplicates, 0 mismatches on re-fetch, 0
  off-date split-factor changes — [dq_coverage.csv](../../analysis/backtests/output/dq_coverage.csv); [dq_raw_duplicate_sample.csv](../../analysis/backtests/output/dq_raw_duplicate_sample.csv); [dq_splits.csv](../../analysis/backtests/output/dq_splits.csv).
- **Limited families.**
  - Options aggregates reach back about 2 years (403 before about 2024-09/10). Options trades, quotes and greeks return 403.
  - Futures aggregates start about 2024-09-28. Indices (I:SOX/I:NDX) start 2023-02-15.
  - ETF Global and Benzinga return 403.
  - Source: [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
- **Toolkit.**
  - 32 passing tests, including feature truncation invariance on real data.
  - End-to-end runs: download 300 s; quality report ~100–115 s; tracker 44 s; battery stages 133 s (1–2) + 493 s (3,
    100 draws) + ~60 s (4) + 22 s (5).
  - Source: `tests/`; `data/soxlab/*.log`.
- **Battery**: best OOS net is orb15 SOXL L/S +24.1 bps/trade (t 1.19, BH q 0.33). The 1-min EMA gross edge of +2.0
  (OOS) is below the 6.0 bps average cost. Last-30-minute behavior flipped from momentum (2020–21) to reversal
  (2023–26) — [battery_summary.csv](../../analysis/backtests/output/battery_summary.csv); [battery_multiple_testing.csv](../../analysis/backtests/output/battery_multiple_testing.csv); [battery_yearly.csv](../../analysis/backtests/output/battery_yearly.csv).

### Inferences
- **Tracking.** The data and tracker support daily and live monitoring of SOXL/SOXS without further purchases. Live
  work would run on REST polling today, or on WebSockets with a raw key. The missing pieces are an iNAV/ICE-index feed
  for premium/discount and holdings/flows.
- **Backtesting.**
  - Minute-level hypotheses: sufficient.
  - Sub-minute execution and lead–lag questions: the data exists (trades/quotes/second bars), but the harness would
    need a tick-level fill model.
  - Anything options- or futures-driven: insufficient history on this plan.

### Gaps
- Real-time latency during market hours, WebSocket behavior and flat-file access were not verified in this session.
- The behavior evidence covers 2022–2026 with one IS/OOS split. Longer out-of-sample accumulation, which the tracker
  and `--update` support, is the main missing ingredient for firmer conclusions.

