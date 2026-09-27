# SOXL and SOXS market microstructure and liquidity: spreads, depth, trade flow and tick constraints (Massive NBBO quotes, trades and bars, Jan-2022 to 2026-09-25)

All numbers below were computed from data pulled from the Massive API (formerly Polygon.io: `/v3/quotes`, `/v3/trades`, `/v2/aggs`, `/v3/reference/splits`, `/v3/reference/tickers`, `/v3/reference/conditions`, `/vX/reference/financials`) by the scripts in [analysis/microstructure/](../../analysis/microstructure/README.md). Every cited file is in `analysis/microstructure/output/`. Times are America/New_York. "RTH" = 09:30-16:00; "current regime" = the 7 normal sample days on or after the last SOXS reverse split (2026-08-10, 2026-09-04, 2026-09-21..25); cents and ticks are the same thing because every ticker trades above $1 with a $0.01 tick.

## 0. Data coverage, sampling design and caveats

### Takeaway
The tick-level statistics rest on 439.6 million NBBO messages and 66.1 million trades in systematically sampled windows on 46 days x 9 tickers, plus 30.4 million NBBO messages and 9.66 million trades from full sessions of SOXL and SOXS on 9 days; the windowed spread estimates reproduce full-session truth with a median absolute error of 0.2%.

### Cited Findings
- Bars: unadjusted and split-adjusted daily bars 2021-01-04..2026-09-25 (1,439 sessions per ticker) and unadjusted 1-minute bars 2022-01-03..2026-09-25 (04:00-20:00, e.g. 1,112,680 SOXL bars); the 9 half-days (13:00 close) are excluded from minute-bar statistics — [01_fetch_bars.py](../../analysis/microstructure/01_fetch_bars.py), [04_bars_analysis.py](../../analysis/microstructure/04_bars_analysis.py)
- Sample days: 5 evenly spaced trading days in each of 2022, 2023, 2024; 4 in 2025-01-01..2025-09-25; 13 in 2025-09-26..2026-09-18; the last 5 trading days 2026-09-21..25; and 9 stress days (2025-04-03, 04-04, 04-07, 04-09, 2025-11-20, 2026-02-06, 2026-06-05, 2026-06-09, 2026-08-27). Calendar-year sample sizes for normal+recent days: 5 / 5 / 5 / 8 / 14 (2022..2026) — [sample_days.csv](../../analysis/microstructure/output/sample_days.csv)
- 2025-11-20 and 2026-08-27 are the first sessions after NVDA quarterly filings accepted 2025-11-19 21:36 UTC and 2026-08-26 20:36 UTC (after the 16:00 ET close) — [nvda_filing_dates.csv](../../analysis/microstructure/output/nvda_filing_dates.csv) (`/vX/reference/financials` acceptance_datetime)
- Windows per sample day (identical for all tickers): one 10-minute NBBO window at a random 5-minute-aligned offset inside each of the 13 RTH half-hours (trades from its first 5 minutes, so the mid 1 and 5 minutes later is observed), fixed windows 09:30-09:35 and 15:55-16:00, a 16:00-16:01 trades window for the closing auction, and one random 5-minute window in each extended-hours stratum (04:00-07:00, 07:00-08:00, 08:00-09:00, 09:00-09:30, 16:00-17:00, 17:00-18:00, 18:00-20:00). RTH windows cover 130 of 390 minutes per day — [ms_common.py](../../analysis/microstructure/ms_common.py), [02_tick_windows.py](../../analysis/microstructure/02_tick_windows.py)
- Messages processed in the windows: NBBO 439,557,252 (QQQ 101.3M, SPY 89.6M, TQQQ 62.9M, SQQQ 49.3M, NVDA 45.1M, SOXL 34.5M, SOXS 22.4M, SMH 17.9M, SOXX 16.5M); trades stored 66,077,890 (NVDA 24.1M, SOXL 9.72M, SPY 9.23M, QQQ 7.92M, TQQQ 5.37M, SQQQ 3.02M, SOXS 2.79M, SMH 2.06M, SOXX 1.89M) — [02_tick_windows.py](../../analysis/microstructure/02_tick_windows.py) outputs under `data/microstructure/tick/`
- Full sessions (04:00-20:00) for SOXL and SOXS on 2022-09-14, 2023-09-13, 2024-09-12, 2025-08-25 and 2026-09-21..25: 30,427,979 NBBO messages and 9,662,640 trades — [03_fullday.py](../../analysis/microstructure/03_fullday.py), [fullday_soxl_soxs_summary.csv](../../analysis/microstructure/output/fullday_soxl_soxs_summary.csv)
- Validation: windowed vs full-session time-weighted mean spread for 234 SOXL/SOXS bucket-days: median absolute relative error 0.2%, mean 3.4%, 75th percentile 4.4%, maximum 45%; per-bucket mean absolute error 7.4-8.7% on the fluid SOXL days of 2026-09-21..25, 8.2% for SOXS on 2022-09-14 (also multi-tick), and 0-3.9% on the other days, when the spread was mostly one tick — [window_validation_fullday.csv](../../analysis/microstructure/output/window_validation_fullday.csv)
- Daily-bar volume equals the sum of trade sizes excluding the zero-volume official open/close/corrected-close prints (conditions 16/15/38) to within 2 shares (SOXS 2023-09-13: 59,746,164 vs 59,746,166); 1-minute bars omit the closing-auction print and minutes containing only odd-lot trades (SOXS 2023-09-13 16:00 bar 12,568 shares vs 126,193 in trades; minute bars sum to 98.25% of daily volume for SOXL and 87.2% for NVDA over the last 12 months) — [volume_session_split.csv](../../analysis/microstructure/output/volume_session_split.csv), [README](../../analysis/microstructure/README.md)
- Trades printed outside the prevailing NBBO (quote strictly before the trade's SIP timestamp), current regime: SOXS 2.4%, SOXL 3.7%, SOXX 4.6%, SMH 4.3%, TQQQ 4.0%, SQQQ 2.4%, SPY 6.8%, NVDA 9.2%, QQQ 13.0% of eligible RTH trades — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- In every sampled window, NBBO sizes for SPY, QQQ, SOXX and SMH are multiples of 100 shares up to the 2025-10-09 sample day and are not multiples of 100 on 80-93% of 1-second snapshots from the 2025-11-04 sample day onward; the ticker reference lists round_lot 40 for these four and 100 for SOXL, SOXS, NVDA, TQQQ and SQQQ — [nbbo_size_granularity_by_day.csv](../../analysis/microstructure/output/nbbo_size_granularity_by_day.csv), [price_levels.csv](../../analysis/microstructure/output/price_levels.csv)

### Inferences
- The NBBO measures only the best displayed round-lot prices: odd-lot quotes inside the NBBO, hidden and midpoint orders, and depth beyond the best price are invisible here. With SOXL at ~$150, one round lot is ~$15,000 of stock, so part of the tradable interest inside the spread is not captured.
- Timestamp misalignment between trade reports and quote updates inflates measured effective spreads most for the busiest names (QQQ, NVDA, SPY); SOXL and SOXS are less affected (under 4% of trades outside the quote).
- Pooled 12-month statistics mix price regimes (SOXL $30.81-$300.77, SOXS $1.59-$73.15 over the last 12 months), so bps figures for pooled groups are regime mixtures; the "current regime" group is the clean description of how the two funds trade today, at the cost of only 7 days.
- The drop of 100-share NBBO granularity for the four >$250 tickers between 2025-10-09 and 2025-11-04 means displayed-depth comparisons for those names across that date are not like-for-like.

### Gaps
- No depth-of-book (only the NBBO), no odd-lot quote feed, no order-level data: queue position, hidden liquidity and cost of walking the book for large orders could not be measured.
- Windowed sampling covers one-third of RTH time on 46 days; the current-regime group has 7 days. Year groups 2022-2024 rest on 5 days each.

## 1. Price level and activity: prices, splits, share/dollar volume, trade counts and the trend since 2022

### Takeaway
SOXL closed at $151.45 on 2026-09-25 after a 12-month range of $30.81-$300.77 with no split since 2021, and it now trades ~$8.7bn and ~1.1M trades per day (3-month average), about 6x its 2022 dollar volume. SOXS closed at $32.43 after 1:20 (2026-03-05) and 1:10 (2026-07-15) reverse splits and trades ~$2.8bn and ~0.46M trades per day; its unadjusted share volume is not comparable over time.

### Cited Findings
- Unadjusted closes 2026-09-25: SOXL $151.45, SOXS $32.43, SOXX $572.68, SMH $606.56, NVDA $225.07, TQQQ $79.60, SQQQ $33.75, QQQ $744.50, SPY $771.35 — [price_levels.csv](../../analysis/microstructure/output/price_levels.csv)
- Last-12-month unadjusted closes: SOXL low $30.81 (2025-11-20), high $300.77 (2026-06-22); SOXS low $1.59 (2026-02-25), high $73.15 (2026-07-29); split-adjusted SOXS range $32.40-$1,062.00 — [price_levels.csv](../../analysis/microstructure/output/price_levels.csv), [01_fetch_bars.py](../../analysis/microstructure/01_fetch_bars.py)
- Splits (`/v3/reference/splits`): SOXL forward 1:4 on 2015-05-20 and 1:15 on 2021-03-02, none since. SOXS reverse splits 5:1 (2011-02-24), 4:1 (2013-08-20), 4:1 (2015-05-20), 5:1 (2017-05-01), 10:1 (2019-06-28), 12:1 (2020-08-28), 10:1 (2022-03-28), 10:1 (2024-04-15), 20:1 (2026-03-05), 10:1 (2026-07-15). Peers: NVDA 1:10 forward 2024-06-10; SMH 1:2 2023-05-05; SOXX 1:3 2024-03-07 plus a 1:3 entry with execution_date 2026-11-05 (after the data end); TQQQ 1:2 forward on 2022-01-13 and 2025-11-20; SQQQ 5:1 reverse on 2022-01-13, 2024-11-07 and 2025-11-20 — [splits.csv](../../analysis/microstructure/output/splits.csv)

Average daily activity from daily bars (unadjusted; windows end 2026-09-25; 3m = 64 sessions from 2026-06-26, 6m = 127 from 2026-03-26, 12m = 251 from 2025-09-26):

| Ticker | Shares/day 3m / 6m / 12m (M) | $ volume/day 3m / 6m / 12m ($bn) | Trades/day 3m / 6m / 12m (k) | Avg trade 3m (shares / $) |
|---|---|---|---|---|
| SOXL | 63.5 / 66.7 / 76.6 | 8.73 / 9.29 / 6.78 | 1,114 / 1,226 / 1,069 | 57.6 / $7,841 |
| SOXS | 175.2 / 267.0 / 317.5 | 2.82 / 2.85 / 2.09 | 464 / 440 / 309 | 451 / $6,269 |
| SOXX | 8.7 / 8.8 / 7.9 | 4.68 / 4.58 / 3.40 | 251 / 270 / 227 | 34.4 / $18,453 |
| SMH | 9.3 / 9.8 / 8.9 | 5.31 / 5.42 / 4.22 | 238 / 255 / 222 | 37.3 / $21,393 |
| NVDA | 125.5 / 143.4 / 162.9 | 26.64 / 29.79 / 31.82 | 2,421 / 2,395 / 2,520 | 51.9 / $11,015 |
| TQQQ | 56.7 / 69.0 / 77.3 | 4.05 / 4.67 / 5.07 | 380 / 418 / 433 | 152.5 / $10,965 |
| SQQQ | 50.3 / 57.4 / 69.6 | 1.99 / 2.62 / 2.86 | 171 / 207 / 229 | 313.2 / $12,223 |
| QQQ | 36.3 / 41.9 / 50.9 | 25.84 / 28.91 / 32.75 | 675 / 754 / 883 | 53.5 / $38,162 |
| SPY | 45.1 / 52.0 / 67.5 | 34.10 / 38.07 / 47.15 | 602 / 692 / 903 | 74.5 / $56,470 |

Source: [activity_windows.csv](../../analysis/microstructure/output/activity_windows.csv) (04_bars_analysis.py)

- Trend, average daily $ volume by calendar year 2022 / 2023 / 2024 / 2025 / 2026 YTD: SOXL $1.33bn / $1.30bn / $2.86bn / $2.81bn / $7.93bn; SOXS $0.64bn / $0.74bn / $0.97bn / $1.24bn / $2.43bn; NVDA $10.0bn / $17.3bn / $37.9bn / $32.5bn / $30.9bn; TQQQ $5.37bn / $3.90bn / $3.73bn / $5.57bn / $4.82bn; SOXX $0.53bn / $0.45bn / $0.80bn / $1.45bn / $3.93bn; SMH $1.36bn / $1.07bn / $1.77bn / $2.16bn / $4.80bn — [activity_yearly.csv](../../analysis/microstructure/output/activity_yearly.csv)
- Trades per day by year: SOXL 318k / 275k / 527k / 603k / 1,188k; SOXS 110k / 146k / 178k / 183k / 368k; average SOXL trade 233 shares ($4,171) in 2022 vs 61 shares ($6,676) in 2026 — [activity_yearly.csv](../../analysis/microstructure/output/activity_yearly.csv)
- Mean unadjusted SOXL close by year: $23.15 / $19.59 / $39.41 / $27.87 / $121.12; SOXS $38.83 / $14.60 / $19.14 / $12.17 / $22.06 — [activity_yearly.csv](../../analysis/microstructure/output/activity_yearly.csv)
- Peak months: SOXL June 2026 at $13.83bn/day and 1.59M trades/day; SOXS June 2026 at $3.61bn/day, trades peak July 2026 at 539k/day — [activity_monthly.csv](../../analysis/microstructure/output/activity_monthly.csv), chart [activity_trend.png](../../analysis/microstructure/output/activity_trend.png)

### Inferences
- In dollar terms SOXL's recent activity is close to SOXX and SMH combined (3-month $8.73bn vs $9.99bn) and one quarter to one third of NVDA's ($26.64bn); SOXS carries about one third of SOXL's dollar volume and ~40% of its trade count.
- SOXL's rise in price without a split mechanically shrank its average trade in shares (233 -> 61) while the dollar size of the average trade rose; trade count, not share count, is the comparable activity measure across 2022-2026 for SOXL, and dollar volume is the only comparable volume measure for SOXS.

### Gaps
- Shares outstanding / creation-redemption flows were not pulled; the reference endpoint gives one current value (SOXL 166.2M, SOXS 53.4M shares) — [price_levels.csv](../../analysis/microstructure/output/price_levels.csv).

## 2. Quoted spreads by time of day (cents, bps, one-tick share, half-penny increments)

### Takeaway
In the current regime SOXL quotes a multi-tick spread (time-weighted mean 5.06 cents = 3.66 bps; at one tick only 4.9% of RTH time) that narrows from ~11.6 cents in the first five minutes to ~2.1 cents in the last five; SOXS is pinned at one tick (mean 1.18 cents = 3.16 bps; 86.8% of RTH time at one tick, 98-99% after 15:00). No ticker quoted a half-penny or any sub-penny price in any sampled window, including 2026.

### Cited Findings
RTH time-weighted NBBO spread, current regime (7 days), locked/crossed and one-sided states excluded:

| Ticker | Mid price | Mean (cents) | Median / p90 (cents) | Mean (bps) | Median / p90 (bps) | % time at 1 tick | % time >= 5 ticks |
|---|---|---|---|---|---|---|---|
| SOXL | $139.57 | 5.06 | 4 / 9 | 3.66 | 2.97 / 6.74 | 4.9 | 46.2 |
| SOXS | $37.35 | 1.18 | 1 / 2 | 3.16 | 2.94 / 4.56 | 86.8 | 0.0 |
| SOXX | $553.31 | 10.92 | 10 / 17 | 1.97 | 1.87 / 3.12 | 0.3 | 93.7 |
| SMH | $591.14 | 10.70 | 10 / 18 | 1.81 | 1.66 / 3.01 | 0.4 | 89.5 |
| NVDA | $225.56 | 1.88 | 2 / 3 | 0.84 | 0.88 / 1.34 | 37.9 | 1.5 |
| TQQQ | $77.19 | 1.01 | 1 / 1 | 1.31 | 1.28 / 1.39 | 99.1 | 0.0 |
| SQQQ | $35.36 | 1.00 | 1 / 1 | 2.84 | 2.90 / 2.96 | 100.0 | 0.0 |
| QQQ | $735.34 | 2.17 | 2 / 3 | 0.30 | 0.27 / 0.42 | 29.0 | 2.3 |
| SPY | $770.55 | 1.81 | 2 / 3 | 0.24 | 0.26 / 0.39 | 37.1 | 0.1 |

Source: [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv) (group `since_2026-07-15`, session `rth`, 09:30-16:00; 05_tick_analysis.py)

SOXL and SOXS by bucket, current regime (time-weighted mean cents / mean bps / % time at one tick):

| Bucket (ET) | SOXL | SOXS |
|---|---|---|
| 04:00-07:00 | 8.37 c / 6.02 bps / 1.2% | 1.76 c / 4.50 bps / 60.3% |
| 07:00-08:00 | 9.40 / 6.77 / 0.2% | 1.56 / 4.01 / 74.1% |
| 08:00-09:00 | 7.91 / 5.74 / 1.3% | 1.42 / 3.63 / 75.1% |
| 09:00-09:30 | 8.72 / 6.43 / 0.4% | 1.72 / 4.34 / 68.8% |
| 09:30-09:35 (fixed) | 11.62 / 8.48 / 0.8% | 2.59 / 6.66 / 26.3% |
| 09:30-10:00 | 8.42 / 6.08 / 0.6% | 1.68 / 4.44 / 52.8% |
| 10:00-10:30 | 6.65 / 4.79 / 1.8% | 1.31 / 3.47 / 78.2% |
| 10:30-11:00 | 6.28 / 4.56 / 0.7% | 1.24 / 3.27 / 84.6% |
| 11:00-11:30 | 5.59 / 4.08 / 1.6% | 1.22 / 3.22 / 86.3% |
| 11:30-12:00 | 4.82 / 3.51 / 3.2% | 1.12 / 2.99 / 90.0% |
| 12:00-12:30 | 5.18 / 3.73 / 3.1% | 1.17 / 3.15 / 85.9% |
| 12:30-13:00 | 4.97 / 3.57 / 4.1% | 1.13 / 3.04 / 90.2% |
| 13:00-13:30 | 4.98 / 3.62 / 2.9% | 1.17 / 3.15 / 85.4% |
| 13:30-14:00 | 4.69 / 3.40 / 3.5% | 1.11 / 2.99 / 90.3% |
| 14:00-14:30 | 4.21 / 3.06 / 8.6% | 1.08 / 2.93 / 92.1% |
| 14:30-15:00 | 3.88 / 2.79 / 8.7% | 1.04 / 2.83 / 96.3% |
| 15:00-15:30 | 3.28 / 2.35 / 8.6% | 1.02 / 2.80 / 98.0% |
| 15:30-16:00 | 2.80 / 2.02 / 16.1% | 1.01 / 2.79 / 98.9% |
| 15:55-16:00 (fixed) | 2.10 / 1.52 / 45.0% | 1.01 / 2.79 / 99.0% |
| 16:00-17:00 | 6.41 / 4.59 / 2.7% | 1.74 / 4.54 / 62.2% |
| 17:00-18:00 | 6.52 / 4.63 / 6.3% | 2.58 / 6.65 / 37.8% |
| 18:00-20:00 | 6.06 / 4.30 / 6.4% | 2.16 / 5.73 / 39.3% |

Source: [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv); chart [spread_by_time_of_day.png](../../analysis/microstructure/output/spread_by_time_of_day.png)

- Medians / p90 by bucket, SOXL current regime: 09:30-10:00 median 8 c, p90 14 c (5.43 / 10.16 bps); 12:00-12:30 median 4 c, p90 10 c; 15:30-16:00 median 3 c, p90 5 c (1.98 / 3.43 bps); first 5 minutes median 11 c, p90 18 c — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- Full-session check with every quote, RTH 2026-09-21..25: SOXL time-weighted mean 2.99 / 3.35 / 5.66 / 4.81 / 4.56 cents (2.16-3.93 bps; one-tick share 1.9-10.6%); SOXS 1.04 / 1.02 / 1.03 / 1.08 / 1.08 cents (2.87-3.32 bps; one-tick share 92.9-98.4%). Minute-by-minute: SOXL falls from ~13 cents at 09:30 to ~2 cents before 16:00 — [fullday_soxl_soxs_summary.csv](../../analysis/microstructure/output/fullday_soxl_soxs_summary.csv), [fullday_minute_spread_profile_2026-09-21_25.csv](../../analysis/microstructure/output/fullday_minute_spread_profile_2026-09-21_25.csv), chart [fullday_spread_profile.png](../../analysis/microstructure/output/fullday_spread_profile.png)
- Trend (RTH, normal days, time-weighted mean cents / bps / % time one tick): SOXL 2022 1.03 / 6.14 / 98.2%; 2023 1.00 / 5.11 / 99.7%; 2024 1.02 / 2.91 / 97.8%; 2025 1.00 / 3.83 / 99.9%; 2026 7.25 / 4.49 / 18.3%. SOXS 2022 2.65 / 8.87 / 45.5%; 2023 1.00 / 8.44 / 99.7%; 2024 1.07 / 7.14 / 92.8%; 2025 1.01 / 18.93 / 99.3%; 2026 1.09 / 14.36 / 93.2% — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv), chart [spread_regimes_by_day.png](../../analysis/microstructure/output/spread_regimes_by_day.png)
- Pooled last-12-months (18 normal days) SOXS: mean 17.66 bps vs median 10.86 bps and p90 53.68 bps, reflecting days quoted at one cent on a sub-$5 price — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- Peers, first 5 minutes vs 12:00-12:30 (current regime, mean cents / bps): NVDA 5.45 / 2.42 vs 1.83 / 0.81; QQQ 3.97 / 0.54 vs 2.41 / 0.33; SPY 2.37 / 0.31 vs 1.91 / 0.25; SOXX 25.26 / 4.60 vs 11.56 / 2.08; SMH 32.52 / 5.52 vs 11.13 / 1.88; TQQQ 1.17 / 1.53 vs 1.02 / 1.33; SQQQ 1.01 / 2.85 vs 1.00 / 2.84. Pre-market 04:00-09:30 (stratified): SOXX 50.69 c (9.25 bps), SMH 82.44 c (13.95 bps), NVDA 8.07 c (3.57 bps), QQQ 5.62 c (0.77 bps), TQQQ 1.33 c (1.72 bps) — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- Locked NBBO: 0.0% of two-sided RTH time for SOXL and 0.2% for SOXS in the current regime; crossed 0.0% for every ticker — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- Half-penny / sub-penny: 0 NBBO messages with a bid or ask off the $0.01 grid and 0 seconds with an odd-multiple-of-$0.005 spread across all 439,557,252 sampled NBBO messages (all 9 tickers, 2022-2026, including the 14 sample days of 2026) — [tick_constraint_summary.csv](../../analysis/microstructure/output/tick_constraint_summary.csv) (`n_subpenny_quotes_all_sessions`, `share_time_halfpenny_spread_all_sessions`)

### Inferences
- SOXL's intraday spread path is steep and nearly monotone (about 3x from the first half hour to the last, 5.5x from the first five minutes to the last five); SOXS's is flat at the one-cent floor after 10:30, with the only material widening in the first half hour and after 17:00.
- In bps, SOXL (3.66) and SOXS (3.16) are now close in RTH; SOXL is cheaper late in the day (2.0 bps after 15:30 vs 2.8 for SOXS) and dearer in the morning (6.1 vs 4.4 bps in 09:30-10:00).
- For both funds pre-market spreads are close to first-half-hour RTH levels (SOXL ~8-9 cents, SOXS ~1.4-1.8 cents), unlike SOXX/SMH whose pre-market spreads are 4-8x their midday level.

### Gaps
- The absence of half-penny quotes is an observation over the sampled windows only (439.6M NBBO messages); the 30.4M full-session SOXL/SOXS quotes were not separately scanned for sub-penny prices.

## 3. Depth and quote dynamics (NBBO size, update rate, persistence of the inside quote)

### Takeaway
SOXL shows thin, fast-changing displayed quotes (~290-330 shares = $40-46k per side, 22.8 NBBO price changes per second, time-weighted median life of an NBBO price pair 0.29 s), while SOXS shows deeper, slower queues (~1,700-1,900 shares = $60-67k per side, 7.8 price changes per second, time-weighted median life 1.5 s).

### Cited Findings
RTH, current regime (time-weighted NBBO size; message and price-change rates per second; NBBO price-state durations between consecutive bid-or-ask price changes):

| Ticker | Bid / ask size (shares) | Bid / ask ($k) | Median of window medians, bid (shares / $k) | NBBO msgs/s | Price changes/s | State duration median / p90 (ms, per state) | Time-weighted median state (ms) | States < 1 ms |
|---|---|---|---|---|---|---|---|---|
| SOXL | 290 / 331 | 40.3 / 46.0 | 200 / 23.1 | 59.2 | 22.8 | 0.87 / 111 | 291 | 51.3% |
| SOXS | 1,707 / 1,893 | 60.3 / 66.7 | 1,200 / 41.9 | 82.0 | 7.8 | 0.40 / 229 | 1,507 | 57.4% |
| SOXX | 103 / 121 | 57.3 / 67.1 | 80 / 41.4 | 34.4 | 14.8 | 1.20 / 158 | 517 | 48.6% |
| SMH | 106 / 109 | 62.5 / 64.6 | 80 / 46.3 | 36.6 | 20.3 | 2.26 / 110 | 327 | 44.1% |
| NVDA | 471 / 468 | 106.2 / 105.6 | 400 / 89.9 | 76.0 | 15.9 | 0.53 / 134 | 573 | 57.3% |
| TQQQ | 3,876 / 3,364 | 297.4 / 259.5 | 3,450 / 260.7 | 126.9 | 9.1 | 0.11 / 184 | 1,532 | 68.3% |
| SQQQ | 17,989 / 20,137 | 632.9 / 708.9 | 17,800 / 635.9 | 53.2 | 0.7 | 1.10 / 3,568 | 7,944 | 49.9% |
| QQQ | 294 / 367 | 215.9 / 269.9 | 160 / 119.0 | 148.6 | 28.3 | 2.14 / 78 | 248 | 42.7% |
| SPY | 324 / 371 | 249.5 / 286.3 | 240 / 184.8 | 99.1 | 14.0 | 1.13 / 177 | 544 | 48.8% |

Source: [depth_by_bucket.csv](../../analysis/microstructure/output/depth_by_bucket.csv), [quote_dynamics_by_bucket.csv](../../analysis/microstructure/output/quote_dynamics_by_bucket.csv) (05_tick_analysis.py)

- SOXL depth by time of day (bid / ask $k, current regime): 09:30-10:00 42.2 / 48.9; 12:00-12:30 38.6 / 56.9; 15:30-16:00 57.1 / 48.4; last 5 minutes 88.4 / 258.9; pre-market strata 28.9-42.6 bid; after-hours 33.7-45.0 bid. SOXS: 09:30-10:00 34.7 / 30.8; 11:00-11:30 62.3 / 72.6; 14:00-14:30 80.3 / 112.8; 15:30-16:00 82.0 / 79.8; last 5 minutes 107.8 / 129.9; pre-market 21.1-33.0 bid — [depth_by_bucket.csv](../../analysis/microstructure/output/depth_by_bucket.csv), chart [depth_by_time_of_day.png](../../analysis/microstructure/output/depth_by_time_of_day.png)
- In 2022 (SOXL ~$22), SOXL's time-weighted displayed size was 7,705 / 7,852 shares ($103k / $106k) with 2.9 price changes per second and a 3.2 s time-weighted median state — [depth_by_bucket.csv](../../analysis/microstructure/output/depth_by_bucket.csv), [quote_dynamics_by_bucket.csv](../../analysis/microstructure/output/quote_dynamics_by_bucket.csv)
- SOXL quote activity by time (msgs/s / price changes/s, current regime): 09:30-10:00 93.2 / 41.9; 12:00-12:30 61.4 / 26.3; 15:30-16:00 83.5 / 24.0; pre-market 6.0 / 3.9; after-hours 1.35 / 0.83; time-weighted median state 135 ms at 09:30-10:00, 459-461 ms at 14:00-15:00, 1.05-1.57 s pre-market, 3.7-10.0 s after-hours. SOXS time-weighted median state 311 ms at 09:30-10:00 and 3.3 s at 14:00-15:00 — [quote_dynamics_by_bucket.csv](../../analysis/microstructure/output/quote_dynamics_by_bucket.csv)
- Displayed bid size divided by total RTH traded shares per second in the same windows (all venues, both sides): SOXL 0.14 s (2,114 shares/s, 34.8 trades/s), SOXS 0.68 s (2,508 shares/s, 13.6 trades/s), NVDA 0.14 s, QQQ 0.22 s, SPY 0.24 s, SOXX 0.37 s, SMH 0.38 s, TQQQ 1.79 s, SQQQ 8.59 s — [tick_constraint_summary.csv](../../analysis/microstructure/output/tick_constraint_summary.csv) (`queue_turnover_sec_bid`)

### Inferences
- More than half of all NBBO price states last under 1 ms for every ticker (flickering quotes), so "how long the inside quote persists" depends on the weighting: at a random moment in RTH, the SOXL NBBO price pair in force lasts ~0.3 s in total (median), the SOXS pair ~1.5 s.
- SOXS's deeper displayed queue relative to its trading rate (0.68 s of volume vs 0.14 s for SOXL) and its lower price-change rate are the quote-level signature of a tick-constrained book; SOXL's book looks like NVDA's (thin, fast).

### Gaps
- Depth beyond the NBBO, odd-lot quotes and hidden size are not in the data; the $-depth figures understate available liquidity at and near the touch by an unknown amount.

## 4. Volume and trade flow: intraday profile, auctions, trade sizes, odd lots

### Takeaway
SOXL and SOXS carry unusually large extended-hours volume (pre-market ~10% of volume over 12 months, 10-26% on 2026-09-21..25), a front-loaded U-shape (first 30 minutes ~20% of RTH minute-bar volume) and small auctions (SOXL close ~1.8%, SOXS ~0.1% of daily volume). SOXL's flow is dominated by small trades (median 20 shares; 79% odd lots); SOXS trades are larger in shares (median 75) with 53% odd lots.

### Cited Findings
- Session split of minute-bar volume, 2025-09-26..2026-09-25 (249 full days): SOXL pre-market 10.7% / RTH 85.9% / after-hours 3.4%; SOXS 10.0 / 87.0 / 2.9; TQQQ 8.4% pre; SQQQ 8.5% pre; NVDA 3.5%; QQQ 4.1%; SOXX 2.8%; SPY 2.3%; SMH 2.1% pre — [volume_session_split.csv](../../analysis/microstructure/output/volume_session_split.csv)
- U-shape (share of 09:30-15:59 minute-bar volume): first 30 minutes SOXL 20.5%, SOXS 19.3%, NVDA 18.0%, SPY 12.4%; last 30 minutes (excluding the closing auction) SOXL 13.2%, SOXS 7.4%, SPY 19.3%; 12:00-13:00 SOXL 9.8%, SOXS 11.0%. SOXL's 09:30 minute holds 1.84% and its quietest minute (14:24) 0.11% of RTH volume. Minute volume steps up at 15:30 for SOXL (4.0x the 15:29 minute) and at 15:50 for SOXL (2.3x), SOXS (2.8x), TQQQ (3.4x) and SQQQ (3.5x) — [volume_profile_minute.csv](../../analysis/microstructure/output/volume_profile_minute.csv), chart [volume_profile.png](../../analysis/microstructure/output/volume_profile.png)
- Full-session trades 2026-09-21..25 (share of all-session volume): SOXL pre-market 10.7-17.0%, opening auction 0.24-0.65%, continuous RTH 78.5-84.7%, closing auction 0.87-2.50%, after-hours 1.8-4.6%; SOXS pre-market 13.0-26.4%, opening auction 0.12-0.26%, closing auction 0.05-0.23%, after-hours 2.0-4.3% — [fullday_soxl_soxs_summary.csv](../../analysis/microstructure/output/fullday_soxl_soxs_summary.csv)
- Auction identification: primary-exchange trade (NYSE Arca, id 11, for SOXL, SOXS, SPY; Nasdaq, id 12, for the others) with condition 17 (Market Center Opening Trade) or 25 (Opening Prints) for the open and 8 (Closing Prints) or 19 (Market Center Closing Trade) for the close; the matching zero-volume official prints 16/15 are excluded. Both prints were found on all 46 days for all 9 tickers, time-stamped 09:30:00.016-09:30:02.547 and 16:00:00.001-16:00:01.972 (e.g. SOXL 2026-09-25: open 198,682 shares at 09:30:00.293, close 1,038,341 shares at 16:00:01.020) — [auctions_by_day.csv](../../analysis/microstructure/output/auctions_by_day.csv), [05_tick_analysis.py](../../analysis/microstructure/05_tick_analysis.py), `/v3/reference/conditions`

Auction share of daily volume (median over sample days; daily-bar volume denominator):

| Ticker | Open, 2022-25 normal (19 d) | Open, last-12m normal (18 d) | Close, 2022-25 normal | Close, last-12m normal (mean; max) | Median close auction $, last 12m |
|---|---|---|---|---|---|
| SOXL | 0.39% | 0.34% | 0.55% | 1.77% (2.01%; 5.67%) | $106.5M |
| SOXS | 0.30% | 0.15% | 0.11% | 0.12% (0.13%; 0.26%) | $2.16M |
| SOXX | 0.49% | 0.46% | 1.14% | 1.86% (2.12%; 5.35%) | $70.3M |
| SMH | 0.30% | 0.40% | 0.93% | 1.48% (1.51%; 4.06%) | $51.6M |
| NVDA | 0.53% | 0.88% | 3.35% | 10.37% (10.47%; 18.67%) | $2.77bn |
| TQQQ | 0.22% | 0.37% | 0.18% | 0.43% (0.46%; 0.92%) | $18.9M |
| SQQQ | 0.20% | 0.17% | 0.06% | 0.12% (0.12%; 0.28%) | $2.22M |
| QQQ | 0.31% | 0.28% | 0.86% | 1.22% (1.52%; 5.18%) | $313.9M |
| SPY | 0.28% | 0.21% | 1.88% | 2.36% (2.33%; 4.72%) | $958.6M |

Source: [auctions_summary.csv](../../analysis/microstructure/output/auctions_summary.csv), [auctions_by_day.csv](../../analysis/microstructure/output/auctions_by_day.csv)

Trade-size distribution, RTH rotating windows, current regime (all trades excluding zero-volume prints):

| | SOXL | SOXS | TQQQ | SQQQ | NVDA | QQQ | SPY |
|---|---|---|---|---|---|---|---|
| Trades sampled | 950,384 | 370,568 | 354,544 | 148,049 | 2,509,459 | 685,407 | 658,191 |
| Median / mean size (shares) | 20 / 60.7 | 75 / 184.8 | 50 / 167.2 | 90 / 386.3 | 0.16 / 37.0 | 10 / 53.4 | 25 / 56.4 |
| p90 / p99 (shares) | 100 / 603 | 375 / 2,000 | 385 / 2,000 | 992 / 5,000 | 100 / 499 | 100 / 467 | 100 / 500 |
| Volume-weighted median (shares) | 140 | 600 | 604 | 2,000 | 225 | 200 | 120 |
| Median trade ($) | 2,998 | 2,674 | 3,918 | 3,177 | 36 | 7,420 | 19,202 |
| Odd-lot flag (cond. 37): % trades / % volume | 79.4 / 27.7 | 53.4 / 7.4 | 56.5 / 6.1 | 50.7 / 2.2 | 87.8 / 18.5 | 65.6 / 7.8 | 55.0 / 7.8 |
| Fractional-share trades (% trades) | 3.2 | 2.5 | 5.4 | 2.3 | 53.6 | 28.9 | 16.3 |
| Off-exchange (TRF): % trades / % volume | 32.6 / 44.3 | 37.9 / 49.9 | 44.2 / 49.0 | 45.2 / 47.6 | 73.0 / 54.2 | 54.5 / 37.9 | 47.4 / 40.0 |
| Sub-penny trade price (% trades) | 17.7 | 27.1 | 34.2 | 38.8 | 61.9 | 38.4 | 30.2 |
| Intermarket sweep (cond. 14, % trades) | 35.7 | 30.3 | 25.9 | 27.4 | 13.6 | 21.3 | 20.2 |

Source: [trade_size_oddlot.csv](../../analysis/microstructure/output/trade_size_oddlot.csv) (group `since_2026-07-15`, sample `RTH rotating windows`)

- Size buckets, SOXL (% of trades / % of volume): 1-99 shares 76.2 / 27.7; 100 shares 12.2 / 20.1; 101-499 6.8 / 24.3; 500-999 1.0 / 10.6; 1,000-4,999 0.5 / 13.7; 5,000-9,999 <0.1 / 1.8; >=10,000 <0.1 / 1.7. SOXS: 1-99 50.9 / 7.4; 100 19.8 / 10.7; 101-499 19.7 / 26.0; 500-999 3.9 / 13.4; 1,000-4,999 2.9 / 27.5; 5,000-9,999 0.2 / 7.6; >=10,000 0.1 / 7.4 — [trade_size_oddlot.csv](../../analysis/microstructure/output/trade_size_oddlot.csv)
- Full-session RTH trades, 2026-09-21..25: SOXL odd lots 76.5-81.0% of trades and 24.4-29.6% of volume, median trade 20-21 shares; SOXS 44.8-54.7% of trades and 5.4-6.5% of volume. On 2022-09-14 SOXL odd lots were 42.0% of trades and 3.0% of volume with a 100-share median — [fullday_soxl_soxs_summary.csv](../../analysis/microstructure/output/fullday_soxl_soxs_summary.csv)
- Extended hours (current regime): SOXL pre-market windows 88.3% odd-lot trades (39.4% of volume), median 13 shares; SOXS pre-market 59.3% (13.1%), median 63 shares — [trade_size_oddlot.csv](../../analysis/microstructure/output/trade_size_oddlot.csv)

### Inferences
- The open is where SOXL/SOXS volume concentrates within RTH, while the close is comparatively light: SOXS's last 30 minutes (7.4%) plus its closing auction (~0.1%) are a much smaller share of volume than for SPY (19.3% + ~2.4%) or NVDA (closing auction ~10%).
- SOXL's order flow is fragmented into small odd-lot prints (half of trades are 20 shares or less, ~$3,000); larger trades print mostly off-exchange (the off-exchange share of trades rises from 27% for 1-99-share trades to 70% for 1,000-4,999 and 81% for 5,000-9,999 shares, see section 5).

### Gaps
- Retail vs institutional attribution of trades is not in the data (TRF prints combine wholesaler, ATS and other off-exchange executions).

## 5. Execution quality: effective spread, realized spread and price impact

### Takeaway
In the current regime SOXL's dollar-weighted effective spread is 1.89 bps (2.64 cents; 61% of the quoted spread at trade time) and SOXS's is 2.32 bps (0.85 cents; 78% of quoted). For both, the average midquote moves in the direction of the trade by more than the effective half-spread within 60 s (realized spread -0.67 bps SOXL, -0.47 bps SOXS), with lit trades carrying far more short-horizon impact than off-exchange trades for SOXL.

### Cited Findings
Eligible RTH trades in the rotating windows, current regime; Lee-Ready signing (quote rule; midpoint trades by tick test); "dw" = dollar-weighted:

| Ticker | Trades | Effective dw (bps / cents) | Effective median (bps) | Quoted at trade (bps) | Eff / quoted | At mid / inside / at quote / outside (%) | Realized 60 s / impact 60 s (bps) | Realized 300 s / impact 300 s (bps) |
|---|---|---|---|---|---|---|---|---|
| SOXL | 941,095 | 1.89 / 2.64 | 0.86 | 3.08 | 0.61 | 21.5 / 36.5 / 38.7 / 3.7 | -0.67 / 2.56 | -0.31 / 2.20 |
| SOXS | 364,861 | 2.32 / 0.85 | 2.66 | 2.97 | 0.78 | 24.7 / 14.1 / 64.8 / 2.4 | -0.47 / 2.79 | -2.09 / 4.41 |
| SOXX | 234,251 | 1.13 / 6.27 | 0.71 | 1.68 | 0.67 | 20.4 / 41.8 / 33.4 / 4.6 | 0.03 / 1.10 | 0.14 / 0.99 |
| SMH | 217,764 | 1.08 / 6.41 | 0.51 | 1.50 | 0.72 | 21.9 / 41.2 / 32.9 / 4.3 | 0.78 / 0.30 | 1.24 / -0.16 |
| NVDA | 2,416,324 | 0.56 / 1.26 | 0.45 | 0.85 | 0.66 | 16.5 / 52.4 / 22.6 / 9.2 | 0.46 / 0.10 | 0.45 / 0.11 |
| TQQQ | 346,178 | 1.19 / 0.92 | 1.26 | 1.23 | 0.97 | 25.9 / 15.2 / 61.4 / 4.0 | -0.68 / 1.87 | -1.10 / 2.29 |
| SQQQ | 145,287 | 2.45 / 0.86 | 2.68 | 2.63 | 0.93 | 28.7 / 16.6 / 59.0 / 2.4 | -0.01 / 2.46 | 0.72 / 1.74 |
| QQQ | 661,835 | 0.24 / 1.77 | 0.14 | 0.25 | 0.96 | 19.4 / 25.9 / 43.4 / 13.0 | -0.08 / 0.32 | -0.15 / 0.39 |
| SPY | 629,690 | 0.18 / 1.42 | 0.13 | 0.21 | 0.89 | 28.1 / 17.4 / 49.0 / 6.8 | 0.03 / 0.16 | 0.15 / 0.04 |

Source: [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv) (bucket `RTH all`, venue `all`; 05_tick_analysis.py). Excluded conditions: 2, 7, 8, 9, 10, 12, 13, 15-22, 25, 28, 29, 32, 33, 38, 52, 53, 55 (see [README](../../analysis/microstructure/README.md)).

- Signing: the quote rule signs 78.5% of SOXL and 75.3% of SOXS eligible trades; the tick test signs essentially all of the rest; Lee-Ready buys are 50.9% (SOXL) and 48.2% (SOXS) of signed trades — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- By venue, SOXL current regime: lit exchanges 638,203 trades, effective 1.78 bps (eff/quoted 0.71), realized / impact at 60 s -2.55 / +4.32 bps and at 300 s -2.19 / +3.97; off-exchange (TRF) 302,892 trades, effective 2.02 bps (eff/quoted 0.53), realized / impact at 60 s +1.65 / +0.37 and at 300 s +2.02 / 0.00. SOXS: lit 2.33 bps (impact 60 s 3.21), TRF 2.31 bps (impact 60 s 2.36) — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- By time of day (dw effective bps / cents): SOXL first 5 minutes 5.08 / 7.04; 09:30-10:00 3.19 / 4.41; 11:30-12:00 1.42 / 1.99; 15:00-15:30 0.96 / 1.35; 15:30-16:00 0.91 / 1.30; last 5 minutes 1.17 / 1.57. SOXS first 5 minutes 3.79 / 1.49; 09:30-10:00 2.90 / 1.11; midday 2.0-2.4 / 0.74-0.82; 15:30-16:00 2.15 / 0.75 — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- By trade size, SOXL (dw effective bps; realized / impact at 300 s): 1-99 shares 1.62 (2.54 / -0.92); 100 shares 1.64 (-0.37 / 2.01); 101-499 1.96 (-1.78 / 3.74); 500-999 2.08 (-1.92 / 4.00); 1,000-4,999 2.39 (-1.70 / 4.09); 5,000-9,999 2.60 (-4.35 / 6.95; 158 trades); fractional (<1 share) 3.22 (all off-exchange). SOXS: 2.17-2.30 bps from 1 to 4,999 shares, 2.58 for 5,000-9,999, 2.94 for >=10,000 (304 trades). Off-exchange share of SOXL trades rises from 27.0% (1-99 shares) to 70.2% (1,000-4,999) and 81.0% (5,000-9,999) — [effective_spread_by_size.csv](../../analysis/microstructure/output/effective_spread_by_size.csv)
- History (dw effective bps / cents; eff/quoted): SOXL 2022 4.48 / 0.83 (0.83); 2023 4.09 / 0.80 (0.85); 2024 2.38 / 0.82 (0.86); 2025 2.81 / 0.78 (0.83); 2026 2.65 / 4.42 (0.63). SOXS 2022 4.58 / 1.64 (0.77); 2023 6.07 / 0.78 (0.84); 2024 4.70 / 0.80 (0.84); 2025 15.06 / 0.79 (0.81); 2026 9.34 / 0.81 (0.79) — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- Full sessions (every RTH trade, 2026-09-21..25): SOXL effective 1.16-1.77 bps dw (eff/quoted 0.56-0.66); SOXS 2.07-2.38 bps (0.75-0.79) — [fullday_soxl_soxs_summary.csv](../../analysis/microstructure/output/fullday_soxl_soxs_summary.csv)

### Inferences
- SOXL's multi-tick spread leaves room for executions inside the quote (58% of trades at the midpoint or strictly inside the spread vs 39% for SOXS), which is why its effective/quoted ratio (0.61) is far below SOXS's (0.78) and the tick-constrained TQQQ/SQQQ/QQQ/SPY (0.89-0.97).
- In cents SOXS's effective spread is the tick-size floor (0.85 cents on a 1-cent quote); in bps it is set by the price level, so the same microstructure cost 15.06 bps in 2025 (price ~$12) and 2.32 bps now.
- The split between lit trades (large positive 60-s impact, negative realized spread) and off-exchange trades (near-zero impact, positive realized spread) for SOXL is the usual segmentation of informed/aggressive lit flow from internalized flow; SOXS shows a much weaker version of it.

### Gaps
- Realized spreads and price impacts are noisy at the day/window level: one current-regime window (12:00-12:30) alone shows SOXL realized -11.85 / impact +13.55 bps at 60 s — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv); with 7 current-regime days the pooled impact figures carry wide, unquantified uncertainty (trades within a window are not independent).
- Effective spreads for the most active tickers are biased up by quote/trade timestamp misalignment (section 0); no latency adjustment was attempted.

## 6. Tick-size constraint: tick-constrained or fluid?

### Takeaway
SOXL was tick-constrained through 2025 (spread at one tick 97.8-99.9% of RTH time; yearly mean relative tick 2.7-6.0 bps) and has been fluid since its price moved above ~$100 in 2026 (one tick 4.9% of time, ~5 ticks mean spread, 1.4% zero-change minutes, relative tick 0.66 bps at the last close). SOXS is tick-constrained (one tick 86.8% of RTH time, ~1.2 ticks mean spread, relative tick 3.08 bps), and the severity of its constraint swings with the reverse-split cycle (relative tick 45-55 bps before the March-2026 split).

### Cited Findings
- Relative tick ($0.01 / close) at 2026-09-25: SOXL 0.66 bps, SOXS 3.08, SQQQ 2.96, TQQQ 1.26, NVDA 0.44, SOXX 0.175, SMH 0.165, QQQ 0.134, SPY 0.130 — [price_levels.csv](../../analysis/microstructure/output/price_levels.csv)
- Relative tick over time (monthly mean of daily values): SOXL 5.98 bps (2022 average), 5.43 (2023), 2.68 (2024), 4.24 (2025), 1.08 (2026); monthly 3.30 bps in Sep-2025 ($30.34 average close), 0.42 in Jun-2026 ($239.05), 0.82 in Sep-2026 ($121.86). SOXS yearly 7.08 / 8.19 / 9.87 / 13.82 / 18.00 bps; monthly 45.5 bps in Jan-2026 ($2.20), 54.9 in Feb-2026 ($1.82), 2.86 in Mar-2026 after the 1:20 split, 21.1 in Jun-2026 ($4.73), 2.21 in Aug-2026 after the 1:10 split — [relative_tick_monthly.csv](../../analysis/microstructure/output/relative_tick_monthly.csv), [minbar_tick_stats_monthly.csv](../../analysis/microstructure/output/minbar_tick_stats_monthly.csv), chart [activity_trend.png](../../analysis/microstructure/output/activity_trend.png)

1-minute bars, RTH close-to-close changes in ticks (half-days excluded):

| Ticker | Period | Zero-change share | 1-tick share | Mean abs. change (ticks) | Median (ticks) | Mean price |
|---|---|---|---|---|---|---|
| SOXL | 2022 | 8.5% | 18.8% | 5.3 | 3.0 | $23.19 |
| SOXL | 2023 | 11.4% | 24.7% | 2.9 | 2.0 | $19.54 |
| SOXL | 2025 | 8.2% | 19.6% | 4.4 | 3.0 | $27.78 |
| SOXL | last 3m (from 2026-06-26) | 1.4% | 3.3% | 32.2 | 19.9 | $141.44 |
| SOXS | 2025 | 25.7% | 34.4% | 2.6 | 1.0 | $12.32 |
| SOXS | last 12m | 26.5% | 30.1% | 3.7 | 1.0 | $17.30 |
| SOXS | last 3m | 8.2% | 16.1% | 8.3 | 4.5 | $38.73 |
| TQQQ | last 3m | 5.1% | 13.3% | 6.3 | 4.3 | $72.02 |
| SQQQ | last 3m | 10.0% | 23.0% | 3.6 | 2.5 | $39.26 |
| NVDA | last 3m | 2.5% | 6.6% | 12.6 | 8.6 | $212.88 |
| SOXX | last 3m | 0.9% | 2.4% | 39.5 | 26.0 | $537.97 |
| SMH | last 3m | 1.1% | 2.3% | 36.1 | 24.0 | $574.48 |
| QQQ | last 3m | 1.7% | 4.3% | 21.1 | 14.0 | $713.97 |
| SPY | last 3m | 2.3% | 6.1% | 13.4 | 9.5 | $758.66 |

Source: [minbar_tick_stats.csv](../../analysis/microstructure/output/minbar_tick_stats.csv) (04_bars_analysis.py)

- SOXS monthly zero-change share: 58.0% in Jan-2026 (mean move 0.45 ticks per minute) and 53.6% in Feb-2026; 10.3% in Mar-2026; 21.9% in Jun-2026; 3.7% in Aug-2026 and 5.1% in Sep-2026. SOXL: 10.1% in Sep-2025, 0.6% in Jun-2026 (mean 77.7 ticks per minute), 2.0% in Sep-2026 — [minbar_tick_stats_monthly.csv](../../analysis/microstructure/output/minbar_tick_stats_monthly.csv), chart [tick_constraint_scatter.png](../../analysis/microstructure/output/tick_constraint_scatter.png)
- Quoted-spread view (RTH, current regime): mean spread in ticks SOXL 5.06, SOXS 1.18, TQQQ 1.01, SQQQ 1.00, NVDA 1.88, SPY 1.81, QQQ 2.17, SOXX 10.92, SMH 10.70; share of RTH time at one tick 4.9% / 86.8% / 99.1% / 100% / 37.9% / 37.1% / 29.0% / 0.3% / 0.4% — [tick_constraint_summary.csv](../../analysis/microstructure/output/tick_constraint_summary.csv)
- Per sample day, SOXL's one-tick share was 90.4-100% on every normal day from 2022-02-08 to 2025-12-31 (closes $10.60-$55.36), 56.6-76.6% on 2026-01-29, 2026-02-26 and 2026-03-25 ($57-$70), and 0.2-11.1% on every normal day from 2026-04-21 ($98.09) on. SOXS's was 0.2-24.5% on 2022-04-21, 07-05 and 09-14 ($51-$72 after the Mar-2022 split), 67.3% on 2024-04-18 ($41.27, three days after the Apr-2024 split), 41.9% on 2026-08-10 ($45.21), 91.0-99.1% on 2026-09-04..25, and 85-100% on every other normal sample day — [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv), chart [spread_regimes_by_day.png](../../analysis/microstructure/output/spread_regimes_by_day.png)

### Inferences
- Classification from these measures: fluid (spread rarely one tick, 5-11 ticks mean) = SOXL since Apr-2026, SOXX, SMH; intermediate (1.8-2.2 ticks mean, one tick 29-38% of the time, relative tick 0.13-0.44 bps, <3% unchanged minutes) = NVDA, QQQ, SPY; tick-constrained (one tick 87-100% of the time) = SOXS, TQQQ, SQQQ. Among the three constrained names SOXS spends the least time at one tick (86.8% vs 99.1% and 100%), while its unchanged-minute share (8.2%, last 3 months) lies between TQQQ (5.1%) and SQQQ (10.0%).
- The tick-constraint status of both funds is price-driven and changes quickly: SOXL went from ~75% one-tick time on 2026-03-25 ($57) to 11% on 2026-04-21 ($98) and 1.6% on 2026-05-15 ($164); SOXS jumps between regimes at each reverse split (relative tick ~55 bps -> ~3 bps on 2026-03-05, ~21 bps -> ~2-3 bps on 2026-07-15).

### Gaps
- Tick-constraint measures on the sampled days are point estimates per day; a daily series of one-tick shares for every session would need full-day quotes for all ~1,190 sessions.

## 7. Spread-to-volatility ratio by time of day

### Takeaway
Measured as quoted spread (bps) divided by the standard deviation of 1-minute returns (bps), SOXL (0.12) and SOXS (0.10) sit with NVDA (0.10), TQQQ (0.11) and SPY (0.10) and well below SQQQ (0.23), SMH (0.21) and SOXX (0.19); for SOXL and SOXS the ratio is lowest in the first and last half hours (0.07-0.11) and highest around 13:30 (0.18-0.20) because volatility falls faster than the spread into midday and rises again into the close.

### Cited Findings
RTH, current regime. Numerator: time-weighted quoted spread (bps) in the sampled windows. Denominators: (a) sd of 1-minute and 5-minute NBBO-mid log returns within the same windows (910 and 182 returns per ticker); (b) sd of 1-minute and non-overlapping 5-minute trade-price returns from 1-minute bars over all 52 sessions since 2026-07-15:

| Ticker | Spread (bps) | sd 1-min mid / bar (bps) | Spread / sd 1-min, mid / bar | sd 5-min mid / bar (bps) | Spread / sd 5-min, mid / bar |
|---|---|---|---|---|---|
| SOXL | 3.66 | 22.9 / 31.4 | 0.160 / 0.116 | 55.6 / 70.6 | 0.066 / 0.052 |
| SOXS | 3.16 | 23.1 / 30.7 | 0.137 / 0.103 | 55.7 / 69.6 | 0.057 / 0.045 |
| SOXX | 1.97 | 7.7 / 10.3 | 0.257 / 0.191 | 18.6 / 23.3 | 0.106 / 0.085 |
| SMH | 1.81 | 6.4 / 8.8 | 0.282 / 0.207 | 15.1 / 19.7 | 0.120 / 0.092 |
| NVDA | 0.84 | 6.6 / 8.5 | 0.126 / 0.098 | 13.9 / 18.3 | 0.060 / 0.046 |
| TQQQ | 1.31 | 9.7 / 12.3 | 0.135 / 0.106 | 21.9 / 27.6 | 0.060 / 0.048 |
| SQQQ | 2.84 | 9.9 / 12.3 | 0.286 / 0.231 | 23.6 / 27.4 | 0.120 / 0.103 |
| QQQ | 0.30 | 3.3 / 4.1 | 0.089 / 0.072 | 7.9 / 9.2 | 0.037 / 0.032 |
| SPY | 0.24 | 2.3 / 2.5 | 0.101 / 0.095 | 5.4 / 5.5 | 0.043 / 0.043 |

Source: [spread_to_vol.csv](../../analysis/microstructure/output/spread_to_vol.csv) (bucket 09:30-16:00, group `since_2026-07-15`), [minbar_vol_by_bucket.csv](../../analysis/microstructure/output/minbar_vol_by_bucket.csv)

- By bucket (spread bps / bar-based sd 1-min bps = ratio), SOXL: 09:30 6.08 / 60.4 = 0.101; 10:00 4.79 / 46.5 = 0.103; 11:00 4.08 / 31.8 = 0.128; 12:00 3.73 / 25.0 = 0.149; 13:00 3.62 / 19.3 = 0.187; 13:30 3.40 / 17.2 = 0.197; 14:30 2.79 / 19.1 = 0.146; 15:00 2.35 / 23.0 = 0.102; 15:30 2.02 / 26.0 = 0.078. SOXS: 09:30 4.44 / 60.3 = 0.074; 10:00 0.077; 11:00 0.102; 12:00 0.133; 13:30 0.182; 15:00 0.122; 15:30 0.113. 5-minute ratios for SOXL run from 0.031 (15:30) and 0.043 (09:30) to 0.092 (13:30) — [spread_to_vol.csv](../../analysis/microstructure/output/spread_to_vol.csv), chart [spread_to_vol.png](../../analysis/microstructure/output/spread_to_vol.png)
- 1-minute trade-price return volatility over the last 12 months (all 249 sessions): SOXL 30.8 bps, SOXS 32.7, TQQQ 14.4, SQQQ 14.3, SOXX 10.1, NVDA 9.5, SMH 9.0, QQQ 4.8, SPY 3.4; 5-minute: SOXL 68.1, SOXS 67.8 — [minbar_vol_by_bucket.csv](../../analysis/microstructure/output/minbar_vol_by_bucket.csv)

### Inferences
- Relative to the size of a typical 1-minute move, SOXL and SOXS are about as cheap to cross as NVDA and SPY and cheaper than the unlevered semiconductor ETFs (SOXX, SMH), whose spreads are wide relative to their lower volatility.
- The ratio's intraday shape (low at the open and close, high at 13:00-14:00) is common to all nine tickers; for SOXL the late-day ratio (0.078 at 15:30) is the lowest of the day because the spread keeps narrowing into the close while volatility rises again.

### Gaps
- The mid-return denominator rests on 7 sampled days (70 one-minute returns per bucket); the bar-based denominator includes bid-ask bounce and uses trade prices. Both are reported; neither is corrected for intraday jumps.

## 8. Stress behavior and trading halts

### Takeaway
On stress days, spreads widened in bps and depth changed in ways that depend on the tick regime: at a sub-$13 price in April 2025 SOXL stayed pinned at one cent (8-11 bps) with 1-minute volatility of 50-124 bps, while at ~$180-200 in June 2026 its spread widened to 24-26 cents (11.6-13.7 bps, 4-5x the normal-day median) with displayed dollar depth at or above normal. No trading halts or LULD pauses were found for SOXL or SOXS in 2024-2026.

### Cited Findings
RTH per stress day (sampled windows; daily return from split-adjusted closes, range from daily high/low):

| Day | SOXL ret / range | SOXL close | SOXL spread (c / bps / p90 bps) | SOXL one-tick | SOXL bid / ask depth ($k) | SOXL sd 1-min mid (bps) | SOXL eff (bps) | SOXS spread (c / bps) | SOXS one-tick | SOXS sd 1-min (bps) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2025-04-03 | -29.8% / 23.9% | $11.41 | 1.00 / 8.18 / 8.63 | 100% | 180 / 234 | 49.8 | 6.32 | 1.06 / 3.01 | 93.9% | 32.7 |
| 2025-04-04 | -23.5% / 27.6% | $8.73 | 1.00 / 11.09 / 11.35 | 100% | 168 / 113 | 68.0 | 8.13 | 1.57 / 3.52 | 47.7% | 46.9 |
| 2025-04-07 | +4.8% / 52.0% | $9.15 | 1.00 / 11.20 / 11.61 | 99.9% | 119 / 157 | 124.3 | 9.61 | 3.84 / 8.80 | 4.7% | 130.7 |
| 2025-04-09 | +54.8% / 59.1% | $12.77 | 1.00 / 10.23 / 11.62 | 100% | 184 / 215 | 115.4 | 7.46 | 2.27 / 6.58 | 17.8% | 207.1 |
| 2025-11-20 | -14.3% / 28.9% | $30.81 | 1.00 / 2.92 / 3.11 | 99.8% | 53 / 52 | 51.3 | 2.52 | 1.00 / 23.38 | 100% | 49.0 |
| 2026-02-06 | +16.0% / 11.8% | $61.75 | 1.36 / 2.27 / 3.44 | 76.1% | 38 / 41 | 31.0 | 2.11 | 1.00 / 51.88 | 100% | 34.8 |
| 2026-06-05 | -30.5% / 28.5% | $182.54 | 23.83 / 11.57 / 18.73 | 3.9% | 123 / 76 | 74.1 | 5.75 | 1.00 / 15.80 | 100% | 49.4 |
| 2026-06-09 | -4.6% / 46.6% | $201.68 | 26.36 / 13.65 / 20.52 | 0.3% | 65 / 58 | 87.4 | 7.15 | 1.00 / 16.41 | 100% | 72.9 |
| 2026-08-27 | +5.5% / 6.1% | $123.05 | 5.44 / 4.49 / 6.67 | 2.1% | 42 / 71 | 24.6 | 2.06 | 1.30 / 2.81 | 77.9% | 27.1 |
| 2026-09-24 (recent) | +0.1% / 7.5% | $146.33 | 5.04 / 3.54 / 5.54 | 1.2% | 31 / 32 | 30.9 | 1.86 | 1.09 / 3.18 | 91.0% | 29.0 |
| Normal days since 2025-03-25 (median of 21) | - | $98.09 | 2.50 / 2.94 / 4.03 | 11.1% | 48 / 50 | 24.7 | 1.85 | 1.00 / 10.48 | 100% | 24.7 |

Source: [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv), [stress_vs_normal.csv](../../analysis/microstructure/output/stress_vs_normal.csv); chart [stress_vs_normal.png](../../analysis/microstructure/output/stress_vs_normal.png)

- SOXL on 2026-06-09: session high $231.02 at 09:47, low $157.56 at 12:40 (-31.8% from the high), close $201.68, with a 1-minute bar in every RTH minute — [04_bars_analysis.py](../../analysis/microstructure/04_bars_analysis.py) minute bars (`data/microstructure/bars/SOXL_min_raw.parquet`)
- SOXS on 2025-04-09: -56.0% close-to-close with a 148% intraday range; spread 2.27 cents (6.58 bps, p90 10.36 bps), depth $22.6k / $18.9k, 1-minute mid volatility 207 bps. SOXS stress days at prices of $1.87-$6.84 (2025-11-20, 2026-02-06, 2026-06-05, 2026-06-09) stayed at one cent 100% of the time, i.e. 15.8-51.9 bps, with $0.78-2.40M displayed per side — [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv)
- Peers on stress days vs normal median: NVDA RTH spread 0.67-2.39 bps vs 0.78; TQQQ 1.39-2.79 bps vs 1.38; QQQ pooled stress 0.62 bps vs 0.30 (current regime); SPY 0.47 vs 0.24 — [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv), [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- Quote activity on stress days: SOXL 41.2-311.6 NBBO msgs/s (91.8-311.6 on the five stress days with closes of $31 or less) vs 64.8 normal median; SOXS 25.9-174.1 msgs/s vs 49.2 — [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv), [stress_vs_normal.csv](../../analysis/microstructure/output/stress_vs_normal.csv)
- Halts: no RTH gap of 2 or more consecutive minutes without a 1-minute bar in 2024-01-02..2026-09-25 for SOXL, SOXS, SMH, NVDA, TQQQ, SQQQ, QQQ or SPY. SOXX had 69 such gaps of 2-5 minutes (mostly Jan-Feb 2024); all 11 gaps of 3+ minutes contain 15-88 raw trades (odd-lot and ISO prints, conditions 14/37/41) with at most 38 s between trades, i.e. no halt. Quote condition 43 (LULD trading pause) appears in 0 of the 439.6M sampled NBBO messages, including all stress-day windows — [rth_trade_gaps_2024_2026.csv](../../analysis/microstructure/output/rth_trade_gaps_2024_2026.csv), [rth_gap_verification.csv](../../analysis/microstructure/output/rth_gap_verification.csv), [luld_quote_flags.csv](../../analysis/microstructure/output/luld_quote_flags.csv) (06_checks.py)

### Inferences
- In the tick-constrained regime the one-cent floor absorbed the stress: SOXL's quoted spread did not widen at all on the April-2025 crash/rally days (one tick, 8-11 bps at closes of $8.73-$12.77) while 1-minute volatility was 2-5x the normal-day median; effective spreads of 6.3-9.6 bps on those days are mostly the one-cent tick at that price level, not stress-driven widening.
- In the fluid regime the spread itself carries the stress: on 2026-06-05 and 06-09 SOXL's RTH spread was 4-5x the normal-day median in bps with p90 near 20 bps; the bid-side depth on 06-09 ($65k) was not lower than normal in dollars, so the widening was in price, not in displayed size.
- SOXS's cost in bps on stress days is dominated by its price level at the time (51.9 bps on 2026-02-06 at $1.87) rather than by stress-driven widening.

### Gaps
- Stress days were chosen on realized outcomes (largest moves), so they are not a random sample of high-volatility days; 9 days x one 10-minute window per half-hour is a thin sample of intraday stress dynamics, and the most extreme minutes of a day (e.g. the 12:40 low on 2026-06-09) may fall outside the sampled windows.
- Minute-bar gap detection cannot see halts shorter than about 2 minutes; LULD flags were checked only inside the sampled windows.

## 9. Cost table for backtesting

### Takeaway
[cost_model_halfspread.csv](../../analysis/microstructure/output/cost_model_halfspread.csv) holds 600 rows (8 tickers x 5 years x 15 buckets) with the exact columns `ticker, year, bucket_start_et, bucket_end_et, median_spread_cents, mean_spread_cents, median_half_spread_bps, mean_half_spread_bps, n_obs`; for 2026 it gives SOXL a mean half-spread of 3.36 bps at 09:30-10:00 falling to 1.45 bps at 15:30-16:00, and SOXS a one-cent median spread in every bucket.

### Cited Findings
- Coverage: SOXL, SOXS, SOXX, SMH, NVDA, TQQQ, SQQQ, QQQ; years 2022-2026 (2026 through 2026-09-25); rows per ticker-year: 13 RTH half-hours plus 04:00-09:30 and 16:00-20:00; no missing values. Built from normal + recent sample days only (5 / 5 / 5 / 8 / 14 days for 2022..2026; stress days excluded) — [cost_model_halfspread.csv](../../analysis/microstructure/output/cost_model_halfspread.csv), [cost_model_halfspread_detail.csv](../../analysis/microstructure/output/cost_model_halfspread_detail.csv), [05_tick_analysis.py](../../analysis/microstructure/05_tick_analysis.py)
- Definitions: time-weighted over NBBO states in the sampled windows (locked/crossed/one-sided excluded); median = time-weighted median; half-spread bps = (ask-bid)/2/mid x 10^4. Pre-market and after-hours rows are stratified (each extended-hours stratum weighted by its clock length: 04:00-07:00 = 180/330 of the pre-market weight). `n_obs` = number of NBBO quote messages in the pooled windows (not independent observations); `n_days`, sampled seconds, p90 and one-tick share per row, plus finer extended-hours strata, are in the detail file — [README](../../analysis/microstructure/README.md)
- A first version (all tickers and years, from the first download pass of 15-16 sample days per ticker) was written early and then overwritten by the final version built from all 37 normal/recent days — [02_tick_windows.py](../../analysis/microstructure/02_tick_windows.py) phase design, [README](../../analysis/microstructure/README.md)
- Selected 2026 rows (median cents / mean cents / median half bps / mean half bps / n_obs): SOXL 04:00-09:30 8 / 10.73 / 2.97 / 3.56 / 97,707; 09:30-10:00 7 / 10.84 / 2.66 / 3.36 / 1,053,401; 12:00-12:30 4 / 7.70 / 1.63 / 2.36 / 682,261; 15:30-16:00 2 / 4.60 / 0.99 / 1.45 / 790,459; 16:00-20:00 5 / 5.73 / 1.91 / 2.29 / 20,118. SOXS 09:30-10:00 1 / 1.35 / 2.85 / 7.81; 15:30-16:00 1 / 1.01 / 1.54 / 7.08. TQQQ 09:30-10:00 1 / 1.05 / 0.67 / 0.77 — [cost_model_halfspread.csv](../../analysis/microstructure/output/cost_model_halfspread.csv)
- Selected 2022 rows: SOXL 09:30-10:00 1 / 1.39 / 3.69 / 3.50; 12:00-12:30 1 / 1.00 / 3.77 / 3.04; SOXS 09:30-10:00 3 / 3.90 / 4.47 / 5.42 — [cost_model_halfspread.csv](../../analysis/microstructure/output/cost_model_halfspread.csv)
- Current-regime equivalents (7 days since 2026-07-15; mean half-spread = mean spread bps / 2): SOXL RTH 1.83 bps (3.04 at 09:30-10:00, 1.01 at 15:30-16:00); SOXS RTH 1.58 bps (2.22 at 09:30-10:00, 1.39 at 15:30-16:00) — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)

### Inferences
- The 2026 SOXS rows pool days at $1.8-$45, so mean half-spread bps (7-8 bps) is a mixture of regimes while the median bps sits at whichever regime holds most sampled time; for a tick-constrained ticker the stable input is `median_spread_cents` (1 cent) divided by 2 and by the backtest's own price. The same applies to SOXL in 2022-2025 (one cent at $8-$70).
- The quoted half-spread overstates the realized cost of small marketable orders by the price improvement measured in section 5 (effective/quoted 0.61 for SOXL, 0.78 for SOXS in the current regime).

### Gaps
- The table contains quoted half-spreads only; it has no size dependence, no price impact and no stress-day rows (stress-day levels are in section 8).

## Microstructure verdict: what the data says about intraday tradability

### Takeaway
Both funds are among the most actively traded instruments in the comparison set, trade continuously with no halts in 2024-2026, and show RTH effective spreads of about 2 bps today (1.89 and 2.32 bps, i.e. roughly 1 bp per side) with a quoted spread that is ~0.10-0.12 of a typical 1-minute move; SOXL is now a fluid, thin-book, fast-quote market whose cost falls steeply through the day, while SOXS is a tick-constrained, deep-queue market whose cost is fixed at one cent and whose bps cost is dictated by where it sits in its reverse-split cycle.

### Cited Findings
Properties favourable to short-horizon trading:
- Activity and continuity: SOXL ~$8.7bn and 1.11M trades per day (3m), SOXS ~$2.8bn and 0.46M; 1-minute bars exist for all but 0.000-0.025% of full-day RTH minutes in 2022-2026 and there is no RTH gap of 2+ minutes in 2024-2026; no halts and no LULD pauses found — [activity_windows.csv](../../analysis/microstructure/output/activity_windows.csv), [minbar_tick_stats.csv](../../analysis/microstructure/output/minbar_tick_stats.csv), [rth_trade_gaps_2024_2026.csv](../../analysis/microstructure/output/rth_trade_gaps_2024_2026.csv), [luld_quote_flags.csv](../../analysis/microstructure/output/luld_quote_flags.csv)
- Cost relative to movement: RTH quoted spread 3.66 bps (SOXL) and 3.16 bps (SOXS) against 1-minute volatility of ~31 bps; spread / sd(1-min) 0.116 and 0.103, spread / sd(5-min) 0.052 and 0.045 — in line with NVDA, TQQQ and SPY — [spread_to_vol.csv](../../analysis/microstructure/output/spread_to_vol.csv)
- Price improvement: effective spread 1.89 bps (SOXL, 61% of quoted) and 2.32 bps (SOXS, 78%); 21.5% / 24.7% of trades at the midpoint — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- SOXL late session: 2.02 bps quoted and 0.91 bps effective in 15:30-16:00, 1.52 bps quoted in the last five minutes — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv), [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- Extended hours are active: pre-market ~10% of 12-month volume for both (10.7-26.4% on 2026-09-21..25), with pre-market spreads close to first-half-hour RTH levels (SOXL ~8-9 cents, SOXS ~1.4-1.8 cents) — [volume_session_split.csv](../../analysis/microstructure/output/volume_session_split.csv), [fullday_soxl_soxs_summary.csv](../../analysis/microstructure/output/fullday_soxl_soxs_summary.csv), [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- SOXS queue depth and stability: 1,707 / 1,893 shares ($60k / $67k) at the NBBO, 7.8 price changes per second, 1.5 s time-weighted state life, 99% of time at one tick after 15:00 — [depth_by_bucket.csv](../../analysis/microstructure/output/depth_by_bucket.csv), [quote_dynamics_by_bucket.csv](../../analysis/microstructure/output/quote_dynamics_by_bucket.csv)

Properties unfavourable to short-horizon trading:
- Adverse short-horizon price moves after trades: realized spread at 60 s is negative for both (SOXL -0.67 bps, SOXS -0.47 bps) with price impact 2.56 / 2.79 bps; for SOXL lit trades, impact 4.32 bps at 60 s; SOXL 300-s impact rises with size from 2.0 bps (100 shares) to 4.1 bps (1,000-4,999) and 7.0 bps (5,000-9,999) — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv), [effective_spread_by_size.csv](../../analysis/microstructure/output/effective_spread_by_size.csv)
- SOXL at the open: 11.62 cents (8.48 bps) quoted and 5.08 bps effective in 09:30-09:35; 8.42 cents (6.08 bps) over 09:30-10:00 — [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv), [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- SOXL displayed depth is thin and fleeting: $40-46k per side, ~0.14 s of traded volume, 51% of NBBO price states shorter than 1 ms, 0.29 s time-weighted median state — [depth_by_bucket.csv](../../analysis/microstructure/output/depth_by_bucket.csv), [quote_dynamics_by_bucket.csv](../../analysis/microstructure/output/quote_dynamics_by_bucket.csv), [tick_constraint_summary.csv](../../analysis/microstructure/output/tick_constraint_summary.csv)
- SOXL stress widening in the fluid regime: 11.6-13.7 bps RTH spread (p90 18.7-20.5 bps) on 2026-06-05/09 vs 2.94 bps normal median — [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv)
- SOXS tick floor and price-level dependence: a one-cent spread is ~3 bps at the current ~$32-46, but SOXS's RTH quoted spread was 14.6-57.4 bps on the 13 sampled days when it traded at $1.72-$6.86 (2025-08-25..2026-02-26 and 2026-06-05..2026-07-14); 26.5% of 1-minute bars unchanged over the last 12 months (8.2% in the last 3 months) — [sample_day_summary.csv](../../analysis/microstructure/output/sample_day_summary.csv), [minbar_tick_stats.csv](../../analysis/microstructure/output/minbar_tick_stats.csv)
- Small, fragmented flow: SOXL median trade 20 shares and 79% odd lots; odd-lot quotes and hidden liquidity are outside the NBBO — [trade_size_oddlot.csv](../../analysis/microstructure/output/trade_size_oddlot.csv)

How SOXL and SOXS differ (current regime unless stated):

| Property | SOXL | SOXS |
|---|---|---|
| Price 2026-09-25 / relative tick | $151.45 / 0.66 bps | $32.43 / 3.08 bps |
| Regime | fluid (one tick 4.9% of RTH time; 5.06 ticks mean) | tick-constrained (one tick 86.8%; 1.18 ticks) |
| RTH quoted spread, mean | 5.06 c = 3.66 bps | 1.18 c = 3.16 bps |
| Open (09:30-10:00) / close (15:30-16:00) quoted | 6.08 / 2.02 bps | 4.44 / 2.79 bps |
| Effective (dw) / eff-to-quoted | 1.89 bps / 0.61 | 2.32 bps / 0.78 |
| Displayed depth per side | $40-46k (290-331 sh) | $60-67k (1,707-1,893 sh) |
| NBBO price changes per second / time-weighted state life | 22.8 / 0.29 s | 7.8 / 1.5 s |
| 1-min bars unchanged (last 3m) / mean move | 1.4% / 32.2 ticks | 8.2% / 8.3 ticks |
| Spread / sd(1-min), bar-based | 0.116 | 0.103 |
| $ volume per day (3m) / trades per day | $8.73bn / 1.11M | $2.82bn / 0.46M |
| Median trade / odd-lot share of trades | 20 sh / 79% | 75 sh / 53% |
| Closing auction share of daily volume (last-12m median) | 1.77% | 0.12% |
| Price impact 60 s / 300 s | 2.56 / 2.20 bps | 2.79 / 4.41 bps |

Sources: [price_levels.csv](../../analysis/microstructure/output/price_levels.csv), [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv), [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv), [depth_by_bucket.csv](../../analysis/microstructure/output/depth_by_bucket.csv), [quote_dynamics_by_bucket.csv](../../analysis/microstructure/output/quote_dynamics_by_bucket.csv), [minbar_tick_stats.csv](../../analysis/microstructure/output/minbar_tick_stats.csv), [spread_to_vol.csv](../../analysis/microstructure/output/spread_to_vol.csv), [activity_windows.csv](../../analysis/microstructure/output/activity_windows.csv), [trade_size_oddlot.csv](../../analysis/microstructure/output/trade_size_oddlot.csv), [auctions_summary.csv](../../analysis/microstructure/output/auctions_summary.csv)

### Inferences
- For SOXL, time of day is the dominant cost variable (quoted spread falls ~3x from 09:30-10:00 to 15:30-16:00 in bps); for SOXS, price level (position in the reverse-split cycle) is the dominant cost variable and time of day matters mainly in the first half hour.
- SOXL's fluid book gives more room for price improvement but offers little displayed size; SOXS's constrained book offers more displayed size per dollar traded but no price increments inside the spread, so fills at the touch depend on queue position rather than on price.
- Both regimes are properties of the current price levels rather than of the funds: on every 2022-2025 normal sample day (closes $10.60-$55.36) SOXL spent at least 90% of RTH time at one tick, and SOXS has moved between ~2 bps and >50 bps relative tick within single reverse-split cycles.

### Gaps
- Queue-position dynamics, fill probabilities for passive orders, and the cost of orders larger than the displayed NBBO size could not be measured without depth-of-book and order-level data.
- The current-regime description rests on 7 sampled days (plus 5 full sessions for SOXL/SOXS); statistics sensitive to a few events (realized spread, price impact, 5-minute volatility) are the least stable figures in these notes.
