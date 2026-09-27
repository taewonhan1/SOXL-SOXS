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
- **Probe coverage**: 207 probes plus 10 as-of options checks. 165 returned HTTP 200 and 42 returned 403 in the final
  paced run — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv) (`scripts/probe_endpoints.py`, `scripts/probe_options_history.py`).
- **Aggregates (`/v2/aggs/ticker/{T}/range/1/{second|minute|hour|day}/…`)** return 200 for SOXL and SOXS, adjusted
  and unadjusted.
  - Earliest bars fall on 2010-03-11: SOXL's first second and minute bars at 09:56:59/09:56 ET, SOXS's at 09:57:13/09:57.
  - Latest minute bar: 2026-09-25 19:59 ET.
  - Earliest daily bar: 2010-03-11 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
  - `/v2/aggs/ticker/{T}/prev`, `/v1/open-close/{T}/{date}` (includes `preMarket`/`afterHours` fields) and grouped daily
    (12,591 US tickers on 2026-09-25) all return 200. `/v1/summaries` returns 403 — [endpoint_inventory.csv](../../analysis/backtests/output/endpoint_inventory.csv).
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
    (QQQ had none).
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
- Use 2022+ for SOXL/SOXS minute studies: coverage is essentially complete. In 2019–2021, 1.5–11% of SOXL RTH
  minutes are missing, which biases volatility and fill assumptions if the gaps are ignored.
- Lead–lag work with SOXX as the driver is contaminated by stale SOXX prints in 2022–2023 (3.6–7.1% missing minutes).
  NVDA and QQQ are cleaner drivers at the minute level.
- Any "close" signal must choose between the 15:59 bar and the official close. They differ by a median of 7–10 bps,
  and the closing-cross volume is invisible in minute bars.

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

<!-- SECTION 4 AND VERDICT APPENDED BELOW -->
