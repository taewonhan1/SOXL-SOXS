# SOXL and SOXS intraday price behavior: a measured behavior profile (Massive minute and second data)

Notation used throughout: **2022–24** = secondary window 2022-01-03..2024-09-30 (685 full sessions); **2024–26** = primary window 2024-10-01..2026-09-25 (493 full sessions). "A → B" means 2022–24 value → 2024–26 value. All numbers were computed from Massive API data pulled for this study by the scripts in `analysis/behavior/`; every bullet links the CSV (and names the script) behind it. Links are relative to this notes file.

## 0. Data, sample, conventions and caveats (applies to every section)

### Takeaway
The data covers 1,187 regular sessions per ticker (2022-01-03 → 2026-09-25) for SOXL, SOXS, SOXX, SMH, NVDA, TQQQ, SQQQ and QQQ. Minute-bar coverage in regular hours is essentially complete. Returns use split-adjusted prices, with prior closes also adjusted for distributions. Half-days were detected and excluded from intraday statistics. The main measurement confound is that SOXS spent 424 of 1,178 full sessions below $10 (unadjusted), where 1 cent is ≥10 bps of price. That price discreteness shapes its 1–15-minute statistics.

### Cited Findings
- Source data: 1-minute aggregates (04:00–20:00 ET, `adjusted=true`), daily bars (adjusted and unadjusted), 1-hour bars (NVDA/AVGO/AMD/MU), 1-second bars (SOXL, SOXS, SOXX, SMH, NVDA, QQQ; 10 sessions 2026-09-14..2026-09-25), splits/dividends reference; 559 download jobs, 0 errors — [01_download.py](../../analysis/behavior/01_download.py) (raw cache in `data/behavior/`, gitignored).
- 1,187 sessions per ticker in 2022-01-03..2026-09-25, no missing daily bars. Median RTH minute-bar coverage is 100% for all tickers except SOXX (99.7%, 1st percentile 82%). SOXS's 1st-percentile coverage is 99.7%. — [data_coverage.csv](../../analysis/behavior/output/data_coverage.csv) (02_build_panel.py)
- Daily-bar open/high/low equal the minute-derived RTH open/high/low on 99.1–100% of days, depending on ticker and field. The official (daily-bar) close differs from the last trade before 16:00 by a median of 8.8 bps for SOXL, 9.9 bps for SOXS, 2.3 bps for SOXX and 0.8 bps for QQQ. — [data_coverage.csv](../../analysis/behavior/output/data_coverage.csv)
- Auction prints are not in minute bars. On 2026-09-25 the SOXL closing cross (1,038,341 shares at $151.45, 16:00:01.02 ET, NYSE Arca) is absent from the 16:00 minute bar, whose volume was 17,117 shares, and the daily-bar close equals the cross price. The daily-bar open ($149.24) was the first eligible regular trade, not the opening-cross print ($149.33). RTH minute-bar volume is a median 89.8% (SOXL) and 91.8% (SOXS) of daily-bar volume; all-session minute volume is 99.3% and 99.9%. — [data_auction_print_check.csv](../../analysis/behavior/output/data_auction_print_check.csv) (02b_auction_check.py); [data_coverage.csv](../../analysis/behavior/output/data_coverage.csv)
- 10 half-days were detected (QQQ 13:05–16:00 volume < 15% of 09:30–13:00 volume): 2021-11-26, 2022-11-25, 2023-07-03, 2023-11-24, 2024-07-03, 2024-11-29, 2024-12-24, 2025-07-03, 2025-11-28, 2025-12-24. They are excluded from intraday statistics. — [half_days.csv](../../analysis/behavior/output/half_days.csv)
- Splits inside the window: SOXS reverse splits on 2022-03-28 (1:10), 2024-04-15 (1:10), 2026-03-05 (1:20) and 2026-07-15 (1:10); SQQQ 1:5 on 2022-01-13, 2024-11-07 and 2025-11-20; TQQQ 2:1 on 2022-01-13 and 2025-11-20; NVDA 10:1 on 2024-06-10; SOXX 3:1 on 2024-03-07; SMH 2:1 on 2023-05-05. SOXL has none in the window. The adjusted series show no artificial gaps on SOXS split dates. — Massive `/v3/reference/splits` (cached by 01_download.py); check in 02_build_panel.py
- Unadjusted price ranges in the window: SOXL $6.93–$300.77, SOXS $1.59–$80.05. Median unadjusted price is $22.97 → $36.21 for SOXL and $20.51 → $12.89 for SOXS. A 1-cent tick is a median 4.35 → 2.76 bps of price for SOXL and 4.88 → 7.76 bps for SOXS. — [data_coverage.csv](../../analysis/behavior/output/data_coverage.csv); [close_last10min_and_auction.csv](../../analysis/behavior/output/close_last10min_and_auction.csv)
- Full sessions with 1 cent ≥ 10 bps of the prior unadjusted close: SOXS 424 (median tick 21.2 bps); SOXL 44 (median 11.0 bps). — [dir_tick_size_stratified.csv](../../analysis/behavior/output/dir_tick_size_stratified.csv) (05_direction.py)
- Official FOMC/CPI schedules could not be fetched: federalreserve.gov, bls.gov, fred.stlouisfed.org and usinflationcalculator.com are blocked by the session's egress policy. Catalyst dates were therefore **detected from reactions**:
  - FOMC: QQQ volume spike at 14:00–14:05 plus a 14:30–14:45 press-conference burst; 35 days detected, 28 "high-confidence".
  - Mid-month 08:30 release days ("likely CPI", PPI possible): 52 days.
  - Earnings (next session after an after-hours volume spike in both the 16:00–20:00 and 17:00–20:00 windows): NVDA 19, AMD 19, MU 19, AVGO 17.
  - From 2023-11 onward, 10 of 12 NVDA picks fall on the same day as an SEC 10-Q/10-K acceptance timestamp from `/vX/reference/financials`. That count includes one pick (2025-01-29) that was replaced by the acceptance date 2025-02-26 under a documented rule. Earlier picks have no nearby acceptance record in the endpoint's data.
  - [events_all_detected.csv](../../analysis/behavior/output/events_all_detected.csv), [events_fomc_detected.csv](../../analysis/behavior/output/events_fomc_detected.csv), [events_earnings_detected.csv](../../analysis/behavior/output/events_earnings_detected.csv) (04_events.py)
- Search-result summaries of BLS schedule pages state that CPI is typically released in the second week of the month. This is the basis for the day-10–15 window. — [BLS CPI schedule (search result; page not reachable)](https://www.bls.gov/schedule/news_release/cpi.htm)

### Inferences
- Returns are built from last-trade prices (minute-bar closes). They contain bid–ask bounce, which matters most when the tick is large relative to price, i.e., low-priced SOXS and SQQQ. Every 1–15-minute statistic for SOXS must be read against its price level (sections 2 and 10).
- Volume-share statistics describe minute-bar (continuous-trading) volume. Closing-auction volume is excluded, so the end-of-day volume share of the funds' true total is understated.

### Gaps
- No NBBO/midquote-based returns were computed. Midquote returns would separate price-discreteness bounce from true price dynamics for SOXS; they were not pulled here to limit API load.
- The FOMC detections include likely misclassifications in 2025–2026: lower-confidence picks 2025-06-11, 2026-01-15 (a Thursday) and 2026-04-01, and no detection near late July 2024 or early November 2024. "CPI" days may include PPI days. AVGO picks before mid-2023 look unreliable (a Monday and a Friday pick; missed quarters).
- SOXX is used as the proxy for the index SOXL/SOXS track. The funds' own benchmark index level was not available in the API pull.

## 1. Volatility and range

### Takeaway
SOXL and SOXS have near-identical range statistics: a median daily high–low range of 6.7–7.4% of the open, ATR(14) around 8.5–9%, and a range above 5% on 75–82% of days. That is about 3× SOXX, 2.5× NVDA and 5× QQQ. Intraday volatility is strongly U-shaped: the first 5 minutes are about 4× as volatile as the quietest midday 5 minutes. SOXL and SOXS volume is front-loaded, while SOXX and QQQ volume is back-loaded into the close. Daily range clusters strongly (lag-1 autocorrelation 0.31 → 0.53). Catalyst days are measurably wider in 2022–24 (FOMC ×1.38 of the trailing median) but less distinct in 2024–26.

### Cited Findings
- **Daily range** ((H−L)/Open, full days), median (p10–p90), 2022–24 → 2024–26 ([vol_daily_range_atr.csv](../../analysis/behavior/output/vol_daily_range_atr.csv), 03_volatility.py):
  - SOXL: 7.35% (4.37–12.70) → 6.68% (3.85–13.33)
  - SOXS: 7.35% (4.32–12.54) → 6.98% (3.89–13.24)
  - Comparators: SOXX 2.41 → 2.23%; SMH 2.34 → 2.13%; NVDA 3.78 → 2.79%; TQQQ 4.66 → 3.62%; SQQQ 4.71 → 3.65%; QQQ 1.57 → 1.23%
- **ATR(14)%** (Wilder smoothing of true range as % of the prior close), median (p10–p90), same source:
  - SOXL: 8.54 (6.72–12.07) → 9.04 (6.48–16.17)
  - SOXS: 8.54 (6.73–12.16) → 9.09 (6.51–16.19)
- **Share of days with range above 3 / 5 / 8 / 10%**, same source:
  - SOXL: 98.7 / 82.2 / 40.7 / 22.2% → 96.2 / 74.6 / 38.1 / 23.1%
  - SOXS: 98.4 / 82.5 / 42.5 / 22.9% → 96.4 / 76.9 / 38.7 / 23.7%
  - Comparators: SOXX >5% on 5.1 → 7.9% of days; QQQ >3% on 9.5 → 4.7% of days
- Close-to-close volatility (annualized) is 109 → 126% for SOXL and 110 → 128% for SOXS. — [vol_daily_range_atr.csv](../../analysis/behavior/output/vol_daily_range_atr.csv)
- **Realized volatility by horizon** (SOXL, RMS of non-overlapping RTH returns; 1-min 267,150 → 192,270 intervals). — [vol_realized_by_horizon.csv](../../analysis/behavior/output/vol_realized_by_horizon.csv)
  - RMS: 1-min 26.5 → 28.9 bps; 5-min 59.9 → 65.9 bps; 15-min 100.4 → 116.8 bps; 30-min 144.8 → 162.3 bps; 60-min 207.2 → 227.8 bps.
  - Annualized: 83 → 91% (1-min) and 84 → 92% (60-min).
  - The ratio of h-minute variance to h × 1-minute variance, in non-overlapping blocks from the open, is 0.96–1.09 at 5–60 minutes.
  - SOXS 1-min RMS is 27.0 → 30.6 bps.
  - The overnight (prior close → open) component annualizes to 62 → 86% for SOXL; RTH open → close annualizes to 89 → 94%.
- **U-shape, 30-minute buckets** ([vol_ushape_30min.csv](../../analysis/behavior/output/vol_ushape_30min.csv); chart [ushape_30min_primary.png](../../analysis/behavior/output/ushape_30min_primary.png)):
  - SOXL RMS 30-min return: 09:30–10:00 = 252 → 302 bps vs a midday minimum of 107 bps (12:30, 2022–24) and 109 bps (14:30, 2024–26).
  - Share of RTH minute volume, first 30 minutes: SOXL 17.9 → 19.7%, SOXS 17.2 → 18.6%.
  - Share of RTH minute volume, last 30 minutes: SOXL 9.2 → 12.8%, SOXS 8.9 → 8.3%, SOXX 17.2 → 18.0%, QQQ 14.4 → 14.0%.
- **U-shape, 5-minute buckets** ([vol_ushape_5min.csv](../../analysis/behavior/output/vol_ushape_5min.csv)):
  - SOXL first-5-minute RMS is 143.5 → 157.7 bps vs a minimum of 37.9 bps (12:55) / 39.4 bps (14:50), a ratio of 3.8 → 4.0. The ratio is 3.7–4.1 for SOXS and SOXX and 2.8 for QQQ.
  - SOXL minute-volume share of the first 5 minutes is 4.7 → 5.1%, vs 0.65–0.76% at the quietest 5-minute bucket.
- The 2024–26 30-minute profile has a bump at 13:00–13:30 (SOXS 164 bps vs 110 bps at 12:30; QQQ 32 vs 22 bps). It coincides with the sample's largest 1-minute move (SOXL +8.98% at 13:19 on 2025-04-09). — [vol_ushape_30min.csv](../../analysis/behavior/output/vol_ushape_30min.csv); [tails_top10_moves.csv](../../analysis/behavior/output/tails_top10_moves.csv)
- **Volatility clustering** (SOXL daily range) ([vol_clustering_range_acf.csv](../../analysis/behavior/output/vol_clustering_range_acf.csv)):
  - Autocorrelation at lag 1 is 0.31 → 0.53, at lag 5 0.31 → 0.26, and at lag 20 0.28 → 0.11. AR(1) R² is 0.10 → 0.28.
  - Median next-day range is 8.99 → 10.41% after top-quintile range days vs 6.01 → 5.88% after bottom-quintile days. SOXS figures are nearly identical (lag-1 0.32 → 0.53).
- **Weekday** ([vol_weekday.csv](../../analysis/behavior/output/vol_weekday.csv)):
  - 2022–24: Thursday is the widest SOXL day (median 8.36% vs Monday 6.67%). Range relative to the trailing 20-day median is 1.11 on Thursday vs 0.91 on Monday (Kruskal–Wallis p = 0.002).
  - 2024–26: no weekday effect (p = 0.53; medians 6.08% Monday to 6.97% Thursday).
- **Catalyst days**, SOXL. "Relative range" is range divided by the trailing 20-day median; non-event days are at 0.977 → 0.968, with medians 7.16 → 6.62% (n = 597 → 430). Mann–Whitney tests are against non-event days. — [vol_catalyst_days.csv](../../analysis/behavior/output/vol_catalyst_days.csv)

| Catalyst (detected) | n (2022–24 / 2024–26) | Median range, 2022–24 | Relative, 2022–24 | p, 2022–24 | Median range, 2024–26 | Relative, 2024–26 | p, 2024–26 |
|---|---|---|---|---|---|---|---|
| FOMC high-confidence | 20 / 8 | 10.97% | 1.38 | <0.001 | 6.68% | 1.15 | 0.15 |
| Day after NVDA earnings | 11 / 8 | 9.66% | 1.24 | 0.065 | 7.97% | 1.33 | 0.20 |
| Day after AMD earnings | 11 / 8 | 9.26% | 1.41 | 0.019 | 9.93% | 1.32 | 0.040 |
| Day after AVGO earnings | 9 / 8 | 6.26% | 1.00 | 0.63 | 10.24% | 1.45 | 0.084 |
| Day after MU earnings | 11 / 8 | 9.45% | 1.03 | 0.47 | 6.45% | 1.14 | 0.66 |
| Mid-month 08:30 (likely CPI) | 33 / 19 | 8.85% | 1.24 | 0.021 | 6.07% | 0.92 | 0.54 |

- On the day after NVDA earnings, SOXL's median |overnight gap| was 5.71% (2022–24) vs 2.33% on non-event days. — [vol_catalyst_days.csv](../../analysis/behavior/output/vol_catalyst_days.csv)

### Inferences
- SOXL and SOXS carry the same volatility budget. Per unit of time, most of the day's price movement is available in the first 30–60 minutes and again late in the session.
- SOXL/SOXS continuous-trading volume is relatively heaviest at the open. For SOXX and QQQ it is heaviest into the close.
- Range persistence is strong enough that the prior day's range is informative about today's range. This is a conditional-volatility fact, not a direction fact.
- The macro-catalyst effect was large in the 2022 inflation/FOMC regime and weaker in 2024–26, when non-scheduled news (tariff days, 2026 semis swings) drove the widest days.
- Catalyst sets are small (n = 8–33 per window) and detected rather than scheduled. FOMC/CPI detection selects days with large QQQ volume bursts, which biases their ranges upward.

### Gaps
- Range on catalyst days uses detected dates, not official calendars (see section 0).

## 2. Directional structure at scalping horizons (1–120 minutes)

### Takeaway
At 1–30-minute horizons SOXL behaves very close to a random walk:
- Autocorrelations are within about ±0.03, and DFA α is ≈ 0.51, equal to the shuffled benchmark.
- After >2σ moves, continuation is 48.5–50.3% at every horizon for SOXL, and mean follow-through is within ±3 bps.
- Run lengths are slightly shorter than random.
- There is mild but statistically detectable mean reversion in 2024–26: deseasonalized VR(15) = 0.974 and VR(60) = 0.945, both outside a sign-randomized null band.

SOXS shows much stronger apparent mean reversion (VR(60) = 0.82 in 2024–26), but this is almost entirely price discreteness on low-priced days. At a $20–50 price SOXS is statistically indistinguishable from SOXL.

### Cited Findings
- **Lag-1 autocorrelation of non-overlapping h-minute returns** (RTH, full days, first bar excluded), robust t in brackets ([dir_autocorr_by_horizon.csv](../../analysis/behavior/output/dir_autocorr_by_horizon.csv), 05_direction.py):
  - SOXL raw: 1-min +0.014 [4.0] → +0.010 [1.8]; 2-min −0.008 → +0.013; 5-min −0.027 [−3.7] → −0.009 [−0.6]; 15-min +0.016 → −0.021; 30-min −0.009 → 0.000
  - SOXL deseasonalized (day- and time-of-day-standardized): 1-min −0.002 [−0.9] → −0.006 [−2.2]; 5-min −0.020 [−4.1] → −0.019 [−3.0]; 15-min +0.005 → −0.023 [−2.1]; 30-min +0.004 → −0.025 [−1.7]
  - SOXS deseasonalized: 1-min −0.030 [−13.7] → −0.066 [−24.7]; 5-min −0.029 → −0.032
  - Deseasonalized 5-minute autocorrelation is negative for all 8 tickers in both windows, between −0.017 and −0.036.
- **1-minute autocorrelation at lags 1–5** is within ±0.035 for every ticker. The largest is SOXS lag-1 in 2024–26 at −0.033. — [dir_autocorr_1min_lags.csv](../../analysis/behavior/output/dir_autocorr_1min_lags.csv)
- **Lo–MacKinlay variance ratios** (overlapping q-sums of deseasonalized 1-min returns, heteroskedasticity-robust z*), q = 2, 5, 15, 30, 60, 120 ([dir_variance_ratios.csv](../../analysis/behavior/output/dir_variance_ratios.csv); chart [variance_ratios.png](../../analysis/behavior/output/variance_ratios.png)):
  - SOXL 2022–24: 0.998, 0.988, 0.981, 0.992, 1.002, 1.033 (z(15) = −2.1, z(60) = +0.1)
  - SOXL 2024–26: 0.994, 0.992, 0.974, 0.958, 0.945, 0.937 (z(15) = −2.3, z(60) = −2.5)
  - SOXS: VR(60) 0.938 [z −3.5] → 0.818 [z −8.5]
  - QQQ 2024–26: VR(60) 0.905 [z −4.3]
- **Sign-randomized null** (keeps every minute's |return|, 20 draws): SOXL 2024–26 VR(15) is 0.974 vs a null mean of 1.005 (95% band 0.987–1.021). VR(60) is 0.945 vs 1.019 (0.978–1.074). In 2022–24 VR(60) is 1.002 vs 0.989, inside the band. — [dir_vr_signrandom_null.csv](../../analysis/behavior/output/dir_vr_signrandom_null.csv) (05b_vr_null_check.py)
- **Non-overlapping raw VR(60)** (every minute weighted once, day-bootstrap 95% CI): SOXL 1.00 [0.95–1.07] → 0.98 [0.88–1.07]. — [dir_variance_ratios.csv](../../analysis/behavior/output/dir_variance_ratios.csv)
- **Methodological note:** overlapping VR on raw returns is biased downward by the U-shape (the edge minutes of the day are under-weighted). For SOXL 2024–26 the raw overlapping VR(120) is 0.847 vs 0.937 deseasonalized. — [dir_variance_ratios.csv](../../analysis/behavior/output/dir_variance_ratios.csv) (column `VR_overlap_raw_BIASED_by_Ushape`)
- **By time of day** ([dir_variance_ratios_by_time_of_day.csv](../../analysis/behavior/output/dir_variance_ratios_by_time_of_day.csv); [dir_autocorr_by_time_of_day.csv](../../analysis/behavior/output/dir_autocorr_by_time_of_day.csv)):
  - SOXL 2024–26, 15:30–16:00: deseasonalized VR(15) = 1.12 (z 3.0) and VR(5) = 1.05 (z 2.5).
  - SOXL 2024–26, midday buckets: VR(15) 0.91–0.96 (z −0.5 to −2.6).
  - SOXL 2022–24: no bucket above z = 1.4.
  - SOXS: VR below 1 in every bucket, with z down to −7.4 in 2024–26.
  - SOXL raw 1-min autocorrelation is positive early: 09:30 bucket +0.032 (t 2.6) in 2024–26, 10:30 bucket +0.039 (t 4.2) in 2022–24.
- **DFA-1** (deseasonalized 1-min returns, scales 5–129 minutes) ([dir_dfa_hurst.csv](../../analysis/behavior/output/dir_dfa_hurst.csv)):
  - SOXL α = 0.514 (shuffled 0.520) → 0.515 (0.522); SOXS 0.504 (0.521) → 0.493 (0.518).
  - All 8 tickers fall between 0.493 and 0.516.
  - SOXS midday 60-minute blocks in 2024–26 have α 0.515–0.537 vs shuffled 0.551–0.571.
- **After large moves** (|z| ≥ 2, with σ taken from the same 30-minute bucket over the prior 20 sessions, so no look-ahead; forward windows end by 16:00) ([dir_continuation_after_large_moves.csv](../../analysis/behavior/output/dir_continuation_after_large_moves.csv)):
  - SOXL 1-min events (13,464 → 10,185): signed forward return +0.8/+1.1/+0.2/+1.6 bps → +0.5/+2.1/+1.2/+0.5 bps at 1/5/15/30 minutes; continuation 49.3–50.0% → 48.5–50.0%.
  - SOXL 5-min events (2,800 → 2,112): 15-minute follow-through −3.2 bps (t −1.3) → +2.4 bps (t 0.7); continuation 49.3% → 50.3%.
  - Opening half-hour exception, 2024–26: SOXL 1-min |z| ≥ 2 events in 09:31–10:00 (n = 789) show +8.4 bps next-minute follow-through (t 3.8) and 55.2% continuation. In 2022–24 the same figure is +2.9 bps (t 1.6).
  - SOXS 2024–26, 10:00–15:30: −3.0 bps next minute (t −4.6), 45.2% continuation.
- **Run lengths** of consecutive same-sign 1-min returns (zeros removed), mean (within-day shuffle) ([dir_run_lengths.csv](../../analysis/behavior/output/dir_run_lengths.csv)):
  - SOXL 1.980 (2.000) → 1.981 (1.995). P(run ≥ 5) = 5.8% (6.2%) → 6.0% (6.2%); P(run ≥ 8) = 0.6% (0.8%) → 0.7% (0.7%). Longest run 17 minutes.
  - SOXS 1.948 (1.995) → 1.915 (1.993).
  - Zero-return minutes: SOXL 2.85 → 1.92%; SOXS 4.33 → 5.28%.
- **Efficiency ratio** |net| / Σ|1-min moves|, observed vs sign-randomized, paired t in brackets ([dir_efficiency_ratio.csv](../../analysis/behavior/output/dir_efficiency_ratio.csv)):
  - SOXL full day: ratio 1.087 [2.8] → 0.972 [−0.8]; median ER 0.049 → 0.046 vs random 0.056/0.057.
  - SOXL 2024–26 hourly blocks 10:30–14:30: 0.92–0.95 [−1.6 to −2.5]. Last 30 minutes: 1.047 [1.6] → 1.146 [3.9].
  - SOXS 2024–26 midday blocks: 0.84–0.88 [−3.6 to −5.2].
- **Tick-size stratification** (deseasonalized, all periods) ([dir_tick_size_stratified.csv](../../analysis/behavior/output/dir_tick_size_stratified.csv)):
  - SOXS on days with tick ≥ 10 bps (n = 424): lag-1 autocorrelation −0.105 (t −38.7); VR(5) 0.818, VR(15) 0.763, VR(60) 0.741; 8.1% zero-return minutes.
  - SOXS at tick 2–5 bps (n = 438): autocorrelation −0.002 (t −0.7); VR(60) 0.995.
  - SQQQ at tick ≥ 10 bps: autocorrelation −0.088, VR(60) 0.76.
  - SOXL at tick ≥ 10 bps (n = 44): autocorrelation −0.017.
  - Across 19 quarters, SOXS's median tick (bps) correlates −0.855 with its 1-min autocorrelation and −0.871 with VR(15). — [stability_tick_size_vs_microstructure.csv](../../analysis/behavior/output/stability_tick_size_vs_microstructure.csv)

### Inferences
- There is no sizeable momentum or reversal structure at 1–30 minutes in SOXL. Conditional follow-through after large moves amounts to a few bps on moves that are themselves tens of bps. That is small relative to the 29 bps 1-minute RMS.
- The persistent, economically small features are:
  - slightly negative 5-minute autocorrelation (shared by all 8 tickers, so market-wide, not LETF-specific);
  - mild mean reversion at 15–60 minutes in 2024–26, also present in QQQ, TQQQ and SOXX, so it is a market-regime feature;
  - trending within the final 30 minutes in 2024–26;
  - brief 1-minute continuation of large moves in the opening half hour of 2024–26.
- SOXS's bounce and mean reversion is a property of its printed price when the price is low (large tick relative to price), not of the underlying semiconductor index. After reverse splits raise its price, SOXS's path statistics converge to SOXL's.

### Gaps
- Midquote-based versions of these statistics were not computed (see section 0), so bid–ask bounce is not fully removed for SOXL either. SOXL's zero-return share is 1.9–2.9%.

## 3. Day types and high/low timing

### Takeaway
Trend days are a minority and are not more frequent than a random-walk benchmark:
- About 15–21% of days are trend days: body ≥ 70% of the range and a close in the extreme 15% in the body's direction.
- About 29–32% are range days (body ≤ 30%).
- Closes at an extreme of the range were more frequent than random in 2022–24 (44% vs 40%) and less frequent in 2024–26 (35% vs 38%).

The day's high or low is set in the first 60 minutes on 84–87% of days. That is 4–6 points above a benchmark that already contains the U-shaped volatility profile.

### Cited Findings
- **SOXL day types**, 2022–24 → 2024–26 ([day_types.csv](../../analysis/behavior/output/day_types.csv), 06_daytypes_open.py):
  - Trend days: 19.4 → 15.2%
  - Range days (body ≤ 0.3): 29.6 → 32.0%
  - Close in top or bottom 15% of range (official OHLC): 39.6 → 30.8%
  - Closing-price-path version vs sign-randomized benchmark: 44.1% (39.6%) → 35.1% (38.0%)
  - Body ≥ 0.7, close-path version vs benchmark: 31.8% (26.6%) → 25.4% (26.1%)
- **SOXS day types:** trend days 21.0 → 17.0%; range days 28.6 → 32.0%. **QQQ:** trend days 21.6 → 19.5%. — [day_types.csv](../../analysis/behavior/output/day_types.csv)
- **SOXL high/low timing**, with the sign-randomized benchmark in brackets ([day_types.csv](../../analysis/behavior/output/day_types.csv)):
  - High or low set in the first 30 minutes: 69.9% (65.2%) → 73.6% (68.9%)
  - In the first 60 minutes: 84.1% (79.8%) → 86.8% (82.5%)
  - In the last 30 minutes: 31.5% (30.8%) → 24.5% (29.5%)
  - Both high and low in the first 60 minutes: 6.3% → 12.2%
- **15-minute buckets** ([day_hod_lod_timing_15min.csv](../../analysis/behavior/output/day_hod_lod_timing_15min.csv); chart [hod_lod_timing_primary.png](../../analysis/behavior/output/hod_lod_timing_primary.png)):
  - SOXL high of day in 09:30–09:45: 27.7 → 27.4% of days; low of day: 28.6 → 34.3% (benchmark 25.5–27.6%).
  - SOXL 15:45–16:00: high 13.4 → 12.2%, low 10.9 → 7.9%.
  - SOXS 2024–26 mirrors this: high of day in 09:30–09:45 on 34.7% of days, low on 28.8%.

### Inferences
- Most days are not clean one-directional sessions. The distribution of day shapes is close to what a random walk with the same volatility profile generates, with a mild regime shift from slightly trend-heavy (2022–24) to slightly range-heavy (2024–26).
- The very high share of extremes set in the first hour is mostly mechanical (the opening volatility burst). The excess over the benchmark is 4–6 percentage points.
- SOXL's low and SOXS's high are more often set at the open in 2024–26. This reflects the up-drift of semis in that window.

### Gaps
- Day types were not conditioned on catalysts or the gap. Those conditional splits were not computed.

## 4. Opening behavior: gaps, gap fills, opening range, first hour

### Takeaway
Overnight gaps are large: median |gap| 2.4 → 2.8%, above 5% on 17 → 29% of days. Same-day gap fills depend on gap size measured in ATR, almost identically across all 8 tickers: about 90% below 0.1 ATR, 73–74% at 0.1–0.25 ATR, 43–53% at 0.25–0.5 ATR, 21–29% at 0.5–1 ATR, and 8–15% above 1 ATR.

The first 30 minutes cover 51 → 57% of the day's range. Breakouts of the 30-minute opening range close beyond the break level on 50–54% of days, which is close to a coin flip. The first hour carries 62 → 71% of the range and about 30–33% of minute-bar volume.

### Cited Findings
- **SOXL gap distribution** (open / dividend-adjusted prior close) ([open_gap_distribution.csv](../../analysis/behavior/output/open_gap_distribution.csv), 06_daytypes_open.py):
  - Median |gap|: 2.39 → 2.81%
  - p10 / p90: −4.59 / +4.70% → −5.56 / +6.54%
  - Share of days with |gap| above 1 / 2 / 3 / 5%: 77.7 / 57.1 / 40.0 / 16.8% → 81.3 / 63.5 / 45.6 / 28.8%
  - Median |gap| as a fraction of the prior ATR: 0.27 → 0.31
  - SOXS median |gap|: 2.38 → 2.82%. SOXX: 0.81 → 0.95%. QQQ: 0.45 → 0.43%.
- **SOXL same-day gap fill** (prior close touched during RTH), fill rate with n in brackets ([open_gap_fill_rates.csv](../../analysis/behavior/output/open_gap_fill_rates.csv)):

| Gap size (|gap| / prior ATR) | 2022–24 | 2024–26 |
|---|---|---|
| 0.03–0.1 | 90.7% (97) | 90.0% (50) |
| 0.1–0.25 | 74.3% (183) | 72.7% (121) |
| 0.25–0.5 | 52.8% (218) | 43.4% (152) |
| 0.5–1 | 28.6% (126) | 21.2% (118) |
| ≥1 | 15.0% (20) | 7.7% (26) |

| Gap size (% of price) | 2022–24 | 2024–26 |
|---|---|---|
| 0.5–1% | 89.7% | 87.2% |
| 1–2% | 75.2% | 70.5% |
| 2–3% | 61.5% | 51.1% |
| 3–5% | 44.0% | 37.3% |
| >5% | 27.0% (115) | 21.8% (142) |

  - In ATR units the 0.25–0.5 ATR fill rates are similar for SOXX (50.0 → 46.2%) and QQQ (54.5 → 44.6%).
- **Opening range** size and share of the full-day range, SOXL ([open_opening_range.csv](../../analysis/behavior/output/open_opening_range.csv)):

| Opening range | Median size, 2022–24 | Median size, 2024–26 | Share of day range, 2022–24 | Share of day range, 2024–26 |
|---|---|---|---|---|
| First 5 minutes | 1.98% | 2.07% | 0.27 | 0.31 |
| First 15 minutes | 2.85% | 2.96% | 0.40 | 0.45 |
| First 30 minutes | 3.61% | 3.69% | 0.51 | 0.57 |
| First 60 minutes | 4.50% | 4.58% | 0.62 | 0.71 |

- **30-minute opening-range breaks**, SOXL 2022–24 → 2024–26 ([open_opening_range.csv](../../analysis/behavior/output/open_opening_range.csv)):
  - Range broken on 98.1 → 96.4% of days; median first break at 38 minutes after the open.
  - First break up 47.9 → 52.7%, down 50.2 → 43.6%. Both sides broken 30.1 → 26.4%.
  - Close beyond the first-break level: 54.0 → 49.7%.
  - Median maximum favourable / adverse excursion from the break level to the close: 2.71 / 2.23% → 2.20 / 2.22%. Within 60 minutes: 1.46 / 1.24% → 1.40 / 1.17%, with the favourable excursion larger on 52.8 → 54.7% of days.
  - 5-minute opening range: both sides broken 58.7 → 56.2%; close beyond the first-break level 54.3 → 51.8%.
- **First hour** ([open_opening_range.csv](../../analysis/behavior/output/open_opening_range.csv), `first_hour_summary` rows):
  - Median share of the day's range: SOXL 0.62 → 0.71; QQQ 0.57 → 0.63.
  - Share of RTH minute volume: SOXL 0.30 → 0.33; first 30 minutes alone 0.18 → 0.20.

### Inferences
- A large part of SOXL/SOXS's daily move happens overnight (median |gap| ≈ 0.3 ATR). The gap-fill profile is a volatility-scaling fact common to all tickers, not a SOXL/SOXS-specific tendency.
- Opening-range breakouts have no reliable directional follow-through in 2024–26: close beyond the level 49.7%, and favourable vs adverse excursions nearly equal. In 2022–24 there was a small tilt toward follow-through (54%).

### Gaps
- Gap fills were not split by pre-market activity or by catalyst days.

## 5. VWAP behavior

### Takeaway
SOXL's typical distance from session VWAP is about 120–130 bps, which equals 0.13–0.15 ATR, the same as every comparator in ATR units. VWAP-crossing frequency is indistinguishable from a random walk: about 6.4–6.9 crosses per day with a 0.02-ATR band vs 6.5–7.1 random. After a close beyond VWAP ± 1σ, price returns to VWAP less often than under a random walk (for example 25% vs 29–30% within 30 minutes), so VWAP is not a mean-reversion attractor. Price stays on one side of VWAP after 10:30 on 16% of days, about the random rate.

### Cited Findings
- **Distance from VWAP** after 10:00, SOXL ([vwap_behaviour.csv](../../analysis/behavior/output/vwap_behaviour.csv), 07_vwap_close.py; by time of day in [vwap_distance_by_time_of_day.csv](../../analysis/behavior/output/vwap_distance_by_time_of_day.csv)):
  - Median |distance| 132 → 119 bps (0.15 → 0.13 ATR); p90 353 → 349 bps (0.38 → 0.37 ATR).
  - Median 1σ VWAP band at 12:00: 134 → 130 bps.
  - All 8 tickers have median |distance| of 0.12–0.16 ATR.
- **VWAP crosses per day**, SOXL: raw median 12 → 13 (mean 14.4 → 14.9 vs random 14.8 → 14.2). With a ±0.02-ATR hysteresis band: mean 6.90 → 6.39 vs random 7.05 → 6.50. — [vwap_behaviour.csv](../../analysis/behavior/output/vwap_behaviour.csv)
- **Return to VWAP after a fresh close beyond VWAP ± 1σ**, SOXL (7,168 → 5,043 events, 10:00–15:00) ([vwap_behaviour.csv](../../analysis/behavior/output/vwap_behaviour.csv)):
  - Measured by high/low touch, within 15 / 30 / 60 minutes: 17.6 / 29.3 / 44.1% → 18.4 / 30.2 / 44.5%.
  - Measured by close: 13.8 / 25.1 / 39.7% → 14.2 / 25.3 / 39.1%, vs random 17.2 / 30.4 / 45.5% → 16.9 / 29.0 / 43.2%.
- **Return to VWAP after ± 2σ**, SOXL (2,892 → 1,772 events) ([vwap_behaviour.csv](../../analysis/behavior/output/vwap_behaviour.csv)):
  - By touch: 5.6 / 13.0 / 25.1% → 6.3 / 14.1 / 25.5%.
  - By close: 4.1 / 10.7 / 21.6% → 4.8 / 11.3 / 21.9%, vs random 5.1 / 12.4 / 23.8% → 5.4 / 12.6 / 22.5%.
- **One side of VWAP after 10:30** (closes only): SOXL 16.5 → 15.6% vs random 16.0 → 17.6%. With no high/low touch at all: 13.6 → 12.0%. SOXS 15.0 → 13.8%. — [vwap_behaviour.csv](../../analysis/behavior/output/vwap_behaviour.csv)

### Inferences
- VWAP distance scales with volatility: in ATR units SOXL/SOXS look like any other ticker.
- The below-random revisit rates are consistent with the daily directional (news or drift) component. They are consistent with the full-day efficiency ratio above 1 in 2022–24 (section 2). They do not indicate VWAP "magnetism" at 15–60 minutes.

### Gaps
- The VWAP comparison uses close-based touches for the benchmark. The benchmark has no intra-minute highs and lows, so the touch-based observed rates are shown only for reference.

## 6. Closing behavior: GHLZ intraday-momentum test, late-day flows, 15:50–16:00, closing auction

### Takeaway
- **Intraday momentum:** the Gao–Han–Li–Zhou intraday-momentum pattern is absent in SOXL, SOXS and SOXX. The first-half-hour slope is about −0.02 and not significant.
- **Late-day reversal, 2024–26:** SOXL's last 30 minutes lean toward reversing the day's 09:30–15:30 move (slope −0.043, t −2.4; same sign on only 43% of days). The sign of this slope is negative in 17 of 19 quarters.
- **Rebalancing-flow test:** on big index-move days, late-day moves are larger but not more continuation-prone. In 2024–26 they reversed more often (33–45% same-direction), the opposite of what LETF rebalancing-driven continuation would predict.
- **15:50–16:00 and the auction:** 15:50–16:00 is about 1.3–1.4× more volatile per minute than the preceding 50 minutes. The closing auction prints a median 6–11 bps away from the last pre-16:00 trade, systematically against the day's move.

### Cited Findings
- **Reference result being tested:** GHLZ (2018) found, in S&P 500 ETF data 1993–2013, that the first half-hour return (measured from the previous close) predicts the last half-hour return. — [SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866); [EconPapers, JFE 129(2):394–414](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414)
- **Last 30 minutes (15:30 → official close) regressions**, Newey–West 5 lags ([close_intraday_momentum_ghlz.csv](../../analysis/behavior/output/close_intraday_momentum_ghlz.csv), 07_vwap_close.py):
  - On prior close → 10:00: SOXL slope −0.022 (t −1.7; R² 0.5%) → −0.019 (t −0.8); SOXS −0.006 → −0.013; SOXX −0.010 → −0.013. No ticker shows a positive significant slope.
  - On 09:30–15:30: SOXL −0.006 (t −0.5) → −0.043 (t −2.4; R² 2.4%; same sign on 42.7% of days).
  - On 15:00–15:30 (the 12th half-hour): QQQ +0.174 (t 2.4), NVDA +0.171 (t 3.0) and TQQQ +0.172 (t 2.3) in 2022–24. SOXL +0.103 (t 1.4) → −0.062 (t −0.6).
- The quarterly SOXL slope of last-30 on 09:30–15:30 is negative in 17 of 19 quarters (mean −0.033, range −0.096 to +0.084). — [stability_persistence_summary.csv](../../analysis/behavior/output/stability_persistence_summary.csv)
- **Late-day behavior by SOXX's prior close → 15:30 move** (bins <1%, 1–2%, 2–3%, ≥3%; n = 173 / 137 / 73 / 110 in 2024–26) ([close_letf_rebalancing_by_index_move.csv](../../analysis/behavior/output/close_letf_rebalancing_by_index_move.csv)):
  - SOXL last-30 in the same direction as its own day move: 42.8 / 36.5 / 32.9 / 44.5% in 2024–26, vs 50.4 / 49.2 / 46.5 / 47.9% in 2022–24.
  - SOXX, same measure: 44.5 / 38.7 / 32.9 / 45.5% in 2024–26.
  - SOXL mean |last-30| rises with the index move: 86 / 107 / 115 / 157 bps.
  - QQQ-driven TQQQ on ≥3% QQQ days: 55.6% (n = 27) → 56.3% (n = 16) same-direction.
- **15:50–16:00 activity** ([close_last10min_and_auction.csv](../../analysis/behavior/output/close_last10min_and_auction.csv)):
  - 15:50–15:59 carries 4.5 → 7.3% of SOXL RTH minute volume; 15:30–15:59 carries 9.0 → 12.5%.
  - SOXX equivalents: 9.4 → 11.0% and 16.6 → 17.1%.
  - SOXL 1-minute RMS in 15:50–15:59 is 1.27× → 1.41× that of 15:00–15:49.
- **Closing-auction jump** (official close vs last pre-16:00 trade) ([close_last10min_and_auction.csv](../../analysis/behavior/output/close_last10min_and_auction.csv)):
  - Median |jump|: SOXL 11.1 → 6.2 bps (p90 27.4 → 22.5; p99 59.4 → 49.6); SOXS 9.5 → 11.1 bps (p90 25.4 → 32.2); SOXX 3.0 → 1.6; QQQ 1.0 → 0.7.
- **Jump direction** ([close_late_day_regressions.csv](../../analysis/behavior/output/close_late_day_regressions.csv); [close_letf_rebalancing_by_index_move.csv](../../analysis/behavior/output/close_letf_rebalancing_by_index_move.csv)):
  - Slope of the jump on the prior close → 15:59 return: SOXL −0.016 (t −15.4) → −0.006 (t −6.9); SOXS −0.008 (t −8.1) → −0.008 (t −7.5).
  - Slope on the 15:50 → 15:59 move: SOXL −0.068 (t −7.8) → −0.026 (t −4.8).
  - Mean signed jump against the day's direction on ≥3% SOXX days: SOXL −17.5 bps (n = 117) → −5.3 bps (n = 110).

### Inferences
- There is no evidence that the first half hour sets up the close in these funds. Where late-day structure exists in 2024–26, it is a partial reversal of the day's move, visible in SOXX as well, so it originates in the semiconductor complex rather than in the funds.
- Late-day moves scale with the day's index move (larger on big days) but are not more directional in the rebalancing direction. The data does not show LETF end-of-day rebalancing as an observable continuation effect in SOXX or SOXL prices at 15:30–16:00.
- The final print (closing auction) tends to give back part of the last-10-minute move. The official close sits systematically closer to the day's prior-close anchor than the last continuous trade.

### Gaps
- Imbalance-message data (15:50 closing imbalances) was not pulled, so the auction jump cannot be attributed to published imbalances.

## 7. Driver linkage, intraday leverage drift, lead–lag, SOXL–SOXS symmetry

### Takeaway
- **Betas:** SOXL/SOXS 5-minute beta to SOXX is +3.00 / −3.02 in 2024–26 (correlation 0.99 / −0.97).
- **Leverage drift:** the effective beta follows the leverage-drift formula L(1+r)/(1+L·r), with r the index return since the prior close, almost exactly. SOXL's beta falls from 3.41 to 2.63 as SOXX moves from −5% to +5% on the day; SOXS's magnitude rises from 2.41 to 4.24.
- **Lead–lag:** at 1-second resolution nothing leads SOXL. NVDA, SOXX, SMH and QQQ all peak at lag 0 on every one of 10 sessions. At 1-minute resolution SOXX is, if anything, the laggard.
- **SOXL–SOXS symmetry:** the pair mirror each other closely intraday (1-minute correlation −0.92 to −0.96; intraday divergence change median 5 bps). Large divergences are carry-overs from dislocated closing prints.

### Cited Findings
- **Betas and correlations**, 1-min / 5-min / daily, 2022–24 → 2024–26 ([link_betas_correlations.csv](../../analysis/behavior/output/link_betas_correlations.csv), 08_linkage.py):
  - SOXL vs SOXX: 2.69 (ρ 0.899) / 2.96 (0.977) / 2.97 (0.998) → 2.95 (0.975) / 3.00 (0.992) / 2.97 (0.997)
  - SOXL vs SMH, 1-min: 2.99 (0.964) → 3.15 (0.963)
  - SOXL vs NVDA, 1-min: 1.58 (0.828) → 1.84 (0.695)
  - SOXL vs QQQ, 1-min: 3.90 (0.880) → 4.66 (0.845)
  - SOXS vs SOXX, 1-min: −2.69 (−0.884) → −2.95 (−0.919); 5-min −2.95 (−0.971) → −3.02 (−0.970)
  - TQQQ vs QQQ, 1-min: 3.01 (0.993) → 2.99 (0.994)
- **Leverage drift**, 5-minute beta binned by SOXX's return since the prior close at the start of each interval, observed vs theory ([link_leverage_drift_beta_bins.csv](../../analysis/behavior/output/link_leverage_drift_beta_bins.csv); chart [leverage_drift_beta.png](../../analysis/behavior/output/leverage_drift_beta.png)):

| Fund | Window | SOXX ≈ −5% | SOXX ≈ 0% | SOXX ≈ +5% |
|---|---|---|---|---|
| SOXL | 2022–24 | 3.28 (theory 3.33) | 2.94 (3.00) | 2.72 (2.76) |
| SOXL | 2024–26 | 3.41 (3.36) | 2.97 (3.00) | 2.63 (2.74) |
| SOXS | 2022–24 | −2.47 (−2.50) | −2.95 (−3.00) | −3.59 (−3.65) |
| SOXS | 2024–26 | −2.41 (−2.47) | −2.98 (−3.00) | −4.24 (−3.71) |

  - The 2022–24 end bins are centred at −4.8% / +4.6%; the 2024–26 end bins at −5.1% / +5.0%.
- **Interaction regression** y = a + b·x + c·x·r: SOXL c = −5.50 (SE 0.19) → −5.84 (0.15) vs first-order theory −6; SOXS c = −11.07 (0.20) → −13.56 (0.60) vs theory −12. — [link_leverage_drift_regression.csv](../../analysis/behavior/output/link_leverage_drift_regression.csv)
- **Since-close tracking at 15:30:** the slope of the fund's return since the prior close on SOXX's is 2.992 → 2.975 for SOXL and −2.997 → −2.994 for SOXS. Median |deviation from L·r| is 13.6 → 11.1 bps (SOXL) and 17.0 → 16.4 bps (SOXS). — [link_since_close_tracking_1530.csv](../../analysis/behavior/output/link_since_close_tracking_1530.csv)
- **1-minute lead–lag** (cross-correlations, lags −5..+5 minutes) ([link_leadlag_1min.csv](../../analysis/behavior/output/link_leadlag_1min.csv)):
  - Off-lag correlations are at most 0.093.
  - SOXX lagging SOXL by 1 minute: 0.093 → 0.027.
  - NVDA leading SOXL by 1 minute: 0.023 → 0.012.
  - NVDA leading SOXX by 1 minute: 0.085 in 2022–24.
- **1-second lead–lag** (Hayashi–Yoshida, asynchronous; 10 sessions 2026-09-14..09-25, 09:35–15:55) ([link_leadlag_1sec_summary.csv](../../analysis/behavior/output/link_leadlag_1sec_summary.csv); chart [leadlag_1sec_hy.png](../../analysis/behavior/output/leadlag_1sec_hy.png)):
  - The correlation peak is at 0 s for every pair on all 10 days.
  - Lag-0 correlation with SOXL: SOXX 0.723, SMH 0.690, QQQ 0.584, NVDA 0.378. SOXL–SOXS: −0.726.
  - ±1 s (driver leads vs lags): SOXX→SOXL 0.328 vs 0.292 (lead–lag ratio 1.39); SMH 0.326 vs 0.322 (1.14); QQQ 0.120 vs 0.126 (0.88); NVDA 0.061 vs 0.069 (0.71).
- **Staleness artifact:** a naive forward-filled 1-second grid shows NVDA "leading" SOXX (lead–lag ratio 12.7) and SMH (26.4). SOXX and SMH trade in only 46% / 47% of RTH seconds, vs SOXL 83%, SOXS 74%, QQQ 83% and NVDA 93%. The Hayashi–Yoshida estimator removes this (lead–lag ratio 0.64 / 0.86). The method was validated on synthetic data with a known 3-second lead, which it recovered. — [link_leadlag_1sec_summary.csv](../../analysis/behavior/output/link_leadlag_1sec_summary.csv); [link_second_bar_coverage.csv](../../analysis/behavior/output/link_second_bar_coverage.csv)
- **SOXL vs SOXS mirror** ([link_soxl_soxs_mirror.csv](../../analysis/behavior/output/link_soxl_soxs_mirror.csv)):
  - Correlation: 1-min −0.956 → −0.917; 5-min −0.985 → −0.959. 1-min slope −0.97 in both windows.
  - Minutes in which both move the same direction: 7.2 → 10.1%. Median |r_SOXS| / |r_SOXL| per minute: 1.02 → 1.06.
  - Divergence R_SOXL + R_SOXS since the prior close (theory ≈ 0): median |·| 13.8 → 14.7 bps; p99 70 → 103 bps; above 50 bps in 3.4 → 6.3% of minutes.
  - Change in divergence since 09:35: median 4.9 → 5.6 bps, p99 30 → 49 bps.
  - Daily close-to-close sum: median |·| 16.8 → 19.1 bps.
- **Divergence episodes** (≥3 consecutive minutes above 100 bps): 4 in 2022–24, 30 in 2024–26. The largest are whole-day carry-overs on 2026-06-29 (268 bps), 2025-04-08 (232 bps) and 2022-10-03 (166 bps). — [link_soxl_soxs_divergence_episodes.csv](../../analysis/behavior/output/link_soxl_soxs_divergence_episodes.csv)
- These follow prior-day closing dislocations. On 2025-04-07 SOXL's official close was 194.8 bps below its last pre-close trade; on 2022-09-30 it was 102.1 bps above. — [tails_closing_dislocations_gt100bps.csv](../../analysis/behavior/output/tails_closing_dislocations_gt100bps.csv)

### Inferences
- SOXL's intraday sensitivity to the semis complex is not a constant 3. It is 3(1+r)/(1+3r), so SOXL's per-minute beta shrinks on up days and grows on down days. SOXS's sensitivity magnitude grows on up days (about −4.2 at +5%) and shrinks on down days. This asymmetry is structural and was measured with high precision in both windows.
- NVDA is only about 38% (1-second) to 70–83% (1–5-minute) correlated with SOXL. SOXL tracks the diversified semis basket (SOXX/SMH, correlation 0.96–0.99), not NVDA alone.
- At the resolution of trade prints (1 second), there is no measurable delay between ETF and driver price discovery.

### Gaps
- The 1-second analysis covers only 10 recent sessions, when SOXL was priced at about $100–$150. Earlier regimes (lower prices, 2022) were not tested at 1-second resolution.
- NBBO-based lead–lag was not computed.

## 8. Extended hours

### Takeaway
SOXL and SOXS trade in almost every pre-market minute: a median 325 → 330 of 330 minutes. The pre-market range is a median 4.1 → 4.3% of the prior close, 54 → 62% of the RTH range, and pre-market carries 6 → 9% of all-session minute volume. That share is 3–5× SOXX's and more than twice QQQ's. The regular session takes out the pre-market high on 61–64% of days and the low on 61–68%. First breaks of these levels mostly happen in the first 15 minutes and usually trade back inside the level within 15 minutes (72–83%).

### Cited Findings
- **Pre-market** ([ext_hours_summary.csv](../../analysis/behavior/output/ext_hours_summary.csv), 09_exthours_tails.py):
  - SOXL range: median 4.06 → 4.33% of the prior close (p90 7.29 → 9.18%); SOXS 4.08 → 4.41%.
  - Ratio to the RTH range: SOXL 0.54 → 0.62.
  - Volume share (median, minute bars): SOXL 6.2 → 8.9%, SOXS 5.5 → 7.6%, TQQQ 4.5 → 7.3%, NVDA 1.8 → 3.4%, QQQ 2.9 → 3.6%, SOXX 0.7 → 1.8%.
  - Minutes with bars (median): SOXL 325 → 330; SOXX 15 → 98.
- **After-hours** ([ext_hours_summary.csv](../../analysis/behavior/output/ext_hours_summary.csv)):
  - SOXL range: median 1.35 → 1.63% of the close (p90 3.63 → 4.79%).
  - Volume share: SOXL 1.5 → 2.35%, SOXS 1.4 → 2.0%, QQQ 5.2 → 5.4%.
- **Regular session vs the pre-market range**, SOXL ([ext_hours_summary.csv](../../analysis/behavior/output/ext_hours_summary.csv)):
  - Takes out the pre-market high on 63.9 → 61.5% of days and the low on 67.6 → 60.9%.
  - Both 33.3 → 26.0%; neither 1.8 → 3.7%.
  - Opens outside the pre-market range on ≤1.2% of days.
- **At the first RTH break of the pre-market high**, SOXL (n = 429 → 299) ([ext_hours_pm_level_breaks.csv](../../analysis/behavior/output/ext_hours_pm_level_breaks.csv)):
  - 63.4 → 67.6% of breaks occur in the first 15 minutes.
  - Price closes back below the level within 15 minutes 79.4 → 72.2% of the time.
  - 30-minute favourable / adverse excursion: 1.21 / 1.09% → 1.37 / 1.07%.
  - The day closes above the level 56.2 → 59.5% of the time.
- **Pre-market low breaks**, SOXL (n = 453 → 296): back inside within 15 minutes 80.6 → 82.8%; the day closes below the level 50.8 → 44.3%. — [ext_hours_pm_level_breaks.csv](../../analysis/behavior/output/ext_hours_pm_level_breaks.csv)

### Inferences
- Pre-market in SOXL/SOXS is a genuinely traded session (continuous prints, 6–9% of volume) that discovers a large part of the day's move before 09:30.
- Pre-market extremes are usually exceeded early in RTH, and the first break is usually retested within minutes. Follow-through beyond the level is roughly even.

### Gaps
- Pre-market statistics use minute bars, with no spread or depth. Liquidity quality in pre-market is covered by the microstructure notes, not here.

## 9. Tails and discontinuities

### Takeaway
- **Frequency:** SOXL/SOXS make at least one 1-minute move above 1% on 62–70% of sessions (2.7 → 4.6 per day on average) and above 2% on 6–13% of sessions. SOXX and QQQ almost never do.
- **Extremes:** the largest 1-minute moves are +8.98% (SOXL) and −10.71% (SOXS) at 13:19 on 2025-04-09. Five-minute moves reach about ±19–21%.
- **Halts:** no multi-minute trading gaps (halts) were detected in SOXL or SOXS RTH minute bars in 1,187 sessions.
- **Closing prints:** two SOXL closing prints deviated by more than 100 bps from the last continuous trade.

### Cited Findings
- **Frequency of large 1-minute moves**, all sessions ([tails_frequency.csv](../../analysis/behavior/output/tails_frequency.csv), 09_exthours_tails.py):
  - SOXL |1-min| > 1%: 0.69 → 1.18% of minutes; 2.7 → 4.6 per day; on 62.4 → 66.1% of days.
  - SOXL > 2%: 0.03 → 0.10% of minutes; on 6.2 → 12.9% of days. > 3%: 1.6 → 1.8% of days. > 5%: 0.29 → 0.40% of days.
  - SOXS > 2%: on 6.7 → 12.9% of days. SOXX > 1%: 0.005 → 0.016% of minutes.
  - SOXL p99 / p99.9 of |1-min|: 90 / 156 bps → 106 / 197 bps.
  - Share of SOXL's > 1% minutes that fall in the first 15 minutes: 35.5 → 27.9%.
- **Largest SOXL 1-minute moves** ([tails_top10_moves.csv](../../analysis/behavior/output/tails_top10_moves.csv)):
  - +8.98% at 13:19 on 2025-04-09
  - +6.14% at 10:10 on 2025-04-07
  - −4.96% at 09:40 on 2024-08-05
  - −4.93% at 14:36 on 2022-11-02
  - −4.35% at 14:00 on 2022-09-21
  - +3.96% at 14:00 on 2024-09-18
- **Largest SOXS 1-minute moves:** −10.71% at 13:19 on 2025-04-09; +8.21% at 10:18 on 2025-04-07. — [tails_top10_moves.csv](../../analysis/behavior/output/tails_top10_moves.csv)
- **Largest rolling 5-minute moves:** SOXL +18.78% (window ending 10:13 on 2025-04-07) and +17.29% (ending 13:23 on 2025-04-09); SOXS −20.66% and −19.60%. — [tails_top10_moves.csv](../../analysis/behavior/output/tails_top10_moves.csv)
- Five of SOXL's ten largest 2022–24 1-minute moves fall at 14:00–14:38 ET on detected FOMC days: 2022-06-15 (+4.02%), 2022-09-21, 2022-11-02, 2022-12-14 (−3.53%) and 2024-09-18. — [tails_top10_moves.csv](../../analysis/behavior/output/tails_top10_moves.csv); [events_fomc_detected.csv](../../analysis/behavior/output/events_fomc_detected.csv)
- **Halts:** zero runs of ≥5 consecutive missing RTH minute bars for SOXL, SOXS, SMH, NVDA, TQQQ, SQQQ or QQQ. — [tails_rth_minute_bar_gaps_ge5min.csv](../../analysis/behavior/output/tails_rth_minute_bar_gaps_ge5min.csv)
  - SOXX has 18 such runs (5–7 minutes, midday, 2022-08-08..2024-01-16), all illiquidity gaps with ≤0.11% price change across the gap and no other ticker missing.
  - Dates: 2022-08-08, 2022-12-07, 2023-01-17, 2023-03-31, 2023-05-05, 2023-05-12, 2023-05-19, 2023-07-25, 2023-11-07, 2023-11-13, 2023-11-17, 2023-11-24, 2023-11-30, 2023-12-19, 2023-12-26, 2023-12-28, 2023-12-29, 2024-01-16.
- **Closing-print dislocations above 100 bps:** SOXL on 2022-09-30 (+102 bps; next-day gap +2.5%) and 2025-04-07 (−195 bps; next-day gap +13.8%). None for SOXS. — [tails_closing_dislocations_gt100bps.csv](../../analysis/behavior/output/tails_closing_dislocations_gt100bps.csv)

### Inferences
- Tail moves in SOXL/SOXS cluster at macro and news timestamps: FOMC 14:00–14:40 in 2022, and the April 2025 tariff headlines. They became about twice as frequent in 2024–26.
- Minute bars never went dark for 5 or more minutes in SOXL/SOXS, so tail risk shows up as price jumps within continuous trading, not as trading pauses.

### Gaps
- LULD pauses shorter than 5 minutes would not be detected by the ≥5-minute rule. The official halt list (exchange data) was not accessed.

## 10. Stability: 2022–24 vs 2024–26 and across 19 quarters

### Takeaway
**Persistent** across windows and quarters:
- the structural leverage beta and leverage drift;
- the SOXL–SOXS mirror;
- the volatility U-shape and early-session extremes;
- near-random-walk behavior at 1–30 minutes (small negative 5-minute autocorrelation);
- gap-fill dependence on gap size in ATR units;
- no GHLZ momentum.

**Regime-dependent:**
- the volatility level (quarterly median range 4.7–10.3%);
- 15–60-minute mean reversion (2024–26 only);
- trend-day frequency (9.5–38.7% by quarter);
- opening-range follow-through (41–64%);
- the late-day reversal magnitude;
- the pre-market volume share, which is rising;
- all of SOXS's 1–15-minute microstructure statistics, which move with its price level and tick size.

### Cited Findings
- **SOXL across 19 quarters, 2022Q1–2026Q3** ([stability_quarterly_metrics.csv](../../analysis/behavior/output/stability_quarterly_metrics.csv); [stability_persistence_summary.csv](../../analysis/behavior/output/stability_persistence_summary.csv), 10_stability_scorecard.py; chart [stability_quarterly.png](../../analysis/behavior/output/stability_quarterly.png)):
  - Median range: 4.65% (2025Q3) to 10.16% (2022Q1).
  - 5-minute beta to SOXX: 2.89–3.06.
  - High or low set in the first 60 minutes: 69.4–95.2%.
  - Deseasonalized 5-min autocorrelation: negative in 17 of 19 quarters (mean −0.018).
  - VR(15) below 1 in 14 of 19 quarters (range 0.888–1.038). VR(60) ranges 0.810–1.179.
  - Trend days: 9.5–38.7%.
  - Opening-range close-beyond-break: 41.0–63.9%, above 50% in 12 of 19 quarters.
  - Gap fill for 0.1–0.5 ATR gaps: 50.0–68.2%.
  - VWAP crosses (band): 5.6–8.2 per day.
  - Last-30 on 09:30–15:30 slope: negative in 17 of 19 quarters.
  - Pre-market volume share: 2.8% (2022Q1) to 13.8% (2026Q3).
- **SOXL primary-minus-secondary difference**, in units of the quarterly standard deviation: gap-fill rate −1.18, pre-market share +1.25, beta +1.07, VR(60) −0.59, trend-day share −0.65, opening-range follow-through −0.67. — [stability_persistence_summary.csv](../../analysis/behavior/output/stability_persistence_summary.csv)
- **SOXS across quarters** ([stability_quarterly_metrics.csv](../../analysis/behavior/output/stability_quarterly_metrics.csv)):
  - Deseasonalized 1-min autocorrelation ranges +0.013 to −0.175; VR(15) ranges 1.015 to 0.647.
  - Median tick ranges 1.9 to 46.1 bps; zero-return minutes range 1.7 to 10.5%.
  - Worst quarter: 2026Q1, just before the 2026-03-05 1:20 reverse split (tick 46.1 bps, autocorrelation −0.175, VR(15) 0.647).
  - 2026Q3, after the 2026-07-15 reverse split: tick 2.2 bps, autocorrelation −0.010, VR(15) 0.924.
- **Tick size vs microstructure**, correlation across quarters: SOXS −0.855 (1-min autocorrelation) and −0.871 (VR(15)); SQQQ −0.796 and −0.760; SOXL −0.286 and −0.017. — [stability_tick_size_vs_microstructure.csv](../../analysis/behavior/output/stability_tick_size_vs_microstructure.csv)
- **Window-level shifts**, SOXL 2022–24 → 2024–26 ([scorecard_secondary.csv](../../analysis/behavior/output/scorecard_secondary.csv); [scorecard_primary.csv](../../analysis/behavior/output/scorecard_primary.csv)):
  - Full-day efficiency ratio vs random: 1.087 → 0.972.
  - Close at an extreme of the range: 44.1 → 35.1% (random ≈ 38–40%).
  - VR(60): 1.002 → 0.945.
  - Days with a |1-min| > 2% move: 6.2 → 12.9%.

### Inferences
- The fund-structure behaviors (leverage, drift, mirror, continuous trading) are stable facts. Directional or path-shape tendencies are small and flip sign or size between regimes. The 2024–26 window was choppier intraday (mean-reverting at 15–60 minutes, fewer extreme closes) but had more frequent tail minutes.
- For SOXS, any path statistic below about 15 minutes depends on where its price sits relative to its reverse-split cycle.

### Gaps
- Quarterly samples are about 60 sessions each. Quarter-level estimates of VR, trend share and slopes have wide sampling error, so persistence is judged by sign counts and ranges rather than formal tests per quarter.

## 11. Comparison scorecard

### Takeaway
SOXL and SOXS are distinct from every comparator in three respects:
- volatility level (about 3× SOXX, 2× TQQQ and 5× QQQ by range and 1-minute RMS);
- overnight/pre-market share of movement;
- frequency of large 1-minute moves.

In volatility-normalized path statistics (autocorrelation, VR, DFA, run lengths, day types, VWAP behavior, gap fills in ATR, high/low timing, opening-range follow-through) SOXL is statistically similar to SOXX and QQQ. SOXS differs from SOXL mainly through price discreteness.

### Cited Findings
- Scorecard, 2024–26 (the full set of rows is in [scorecard_primary.csv](../../analysis/behavior/output/scorecard_primary.csv); the source CSV for each row is listed in the sections above):

| Metric | SOXL | SOXS | SOXX | SMH | NVDA | TQQQ | SQQQ | QQQ |
|---|---|---|---|---|---|---|---|---|
| daily range % median (p10-p90) | 6.68 (3.85-13.33) | 6.98 (3.89-13.24) | 2.23 (1.29-4.47) | 2.13 (1.25-4.03) | 2.79 (1.73-5.11) | 3.62 (2.11-6.95) | 3.65 (2.11-7.01) | 1.23 (0.71-2.29) |
| ATR14 % median | 9.04 | 9.09 | 3.02 | 2.88 | 3.47 | 4.69 | 4.70 | 1.58 |
| % days range >5% / >10% | 74.6 / 23.1 | 76.9 / 23.7 | 7.9 / 0.8 | 6.3 / 0.6 | 11.0 / 1.2 | 27.0 / 2.6 | 27.2 / 2.6 | 1.0 / 0.2 |
| 1-min RMS return (bps) | 28.9 | 30.6 | 9.5 | 8.8 | 11.0 | 15.7 | 16.0 | 5.2 |
| overnight ann. vol (%) | 85.8 | 86.8 | 28.8 | 26.7 | 27.8 | 41.8 | 41.6 | 13.9 |
| AC 1-min deseas. [t] | -0.006 [-2.2] | -0.066 [-24.7] | -0.009 [-3.1] | -0.005 [-1.9] | +0.000 [+0.0] | -0.013 [-4.5] | -0.035 [-12.8] | -0.012 [-4.1] |
| AC 5-min deseas. [t] | -0.019 [-3.0] | -0.032 [-5.0] | -0.018 [-2.8] | -0.024 [-3.6] | -0.030 [-4.4] | -0.032 [-5.1] | -0.036 [-5.9] | -0.033 [-5.3] |
| VR(15) deseas. [z] | 0.974 [-2.3] | 0.852 [-13.5] | 0.974 [-2.3] | 0.971 [-2.6] | 0.960 [-3.6] | 0.942 [-5.1] | 0.901 [-8.9] | 0.941 [-5.2] |
| VR(60) deseas. [z] | 0.945 [-2.5] | 0.818 [-8.5] | 0.944 [-2.5] | 0.928 [-3.2] | 0.931 [-3.1] | 0.904 [-4.3] | 0.865 [-6.2] | 0.905 [-4.3] |
| DFA alpha (shuffled) | 0.515 (0.522) | 0.493 (0.518) | 0.515 (0.521) | 0.515 (0.522) | 0.513 (0.520) | 0.509 (0.522) | 0.503 (0.520) | 0.509 (0.520) |
| after 1-min z≥2: fwd 5m bps [% cont.] | +2.1 [50.0] | -1.5 [47.7] | +0.4 [49.7] | -0.0 [49.0] | -0.2 [49.6] | -0.6 [49.2] | -1.1 [48.8] | -0.3 [48.8] |
| mean run length 1-min (shuffled) | 1.981 (1.995) | 1.915 (1.993) | 1.974 (1.998) | 1.991 (2.000) | 1.988 (1.990) | 1.975 (1.999) | 1.948 (1.994) | 1.983 (1.999) |
| % zero-return minutes | 1.92 | 5.28 | 2.14 | 1.82 | 1.09 | 1.92 | 3.38 | 1.40 |
| efficiency ratio full day: obs/random | 0.972 | 0.949 | 0.983 | 0.976 | 0.976 | 1.036 | 1.021 | 1.038 |
| trend days % | 15.2 | 17.0 | 16.2 | 15.6 | 17.0 | 19.5 | 19.5 | 19.5 |
| range days % (body<=0.3) | 32.0 | 32.0 | 31.4 | 32.9 | 30.2 | 27.8 | 28.6 | 27.6 |
| HOD or LOD in first 60 min %: obs (random) | 86.8 (82.5) | 87.4 (81.1) | 86.8 (83.3) | 86.8 (82.9) | 88.6 (83.8) | 82.8 (76.5) | 83.0 (76.1) | 82.4 (76.9) |
| median abs gap % | 2.81 | 2.82 | 0.95 | 0.87 | 0.93 | 1.30 | 1.30 | 0.43 |
| gap fill % (0.25-0.5 ATR gaps) | 43.4 | 46.2 | 46.2 | 43.0 | 38.8 | 44.8 | 44.7 | 44.6 |
| OR30: close beyond 1st break % | 49.7 | 50.8 | 49.9 | 50.5 | 51.2 | 54.9 | 54.6 | 55.3 |
| first-hour share of day range | 0.71 | 0.71 | 0.72 | 0.71 | 0.72 | 0.64 | 0.64 | 0.63 |
| VWAP crosses/day, 0.02-ATR band: obs (random) | 6.39 (6.50) | 7.06 (6.99) | 6.54 (6.58) | 6.57 (6.81) | 6.32 (6.36) | 6.59 (6.67) | 6.66 (7.03) | 6.32 (6.79) |
| revisit VWAP <=30m after 1-sd: obs (random) % | 25.3 (29.0) | 27.7 (30.3) | 26.8 (29.4) | 25.1 (29.8) | 21.2 (26.7) | 26.0 (31.8) | 26.6 (33.0) | 25.7 (31.7) |
| last30 ~ first half-hour (GHLZ) slope [t] | -0.019 [-0.8] | -0.013 [-0.8] | -0.013 [-0.7] | -0.013 [-0.7] | -0.011 [-0.6] | -0.008 [-0.4] | -0.001 [-0.1] | +0.002 [+0.1] |
| last30 ~ 09:30-15:30 slope [t] | -0.043 [-2.4] | -0.005 [-0.2] | -0.031 [-1.7] | -0.020 [-1.1] | +0.015 [+0.8] | -0.001 [-0.0] | +0.013 [+0.5] | +0.010 [+0.4] |
| median abs closing-auction jump bps | 6.2 | 11.1 | 1.6 | 1.5 | 2.2 | 1.8 | 2.7 | 0.7 |
| 5-min beta / corr vs SOXX (SOXX row: vs QQQ) | +3.00 / +0.992 | -3.02 / -0.970 | +1.58 / +0.856 | +0.90 / +0.978 | +0.79 / +0.706 | +1.40 / +0.856 | -1.40 / -0.848 | +0.46 / +0.856 |
| pre-market vol share % (median) | 8.9 | 7.6 | 1.8 | 1.3 | 3.4 | 7.3 | 7.1 | 3.6 |
| % days with a 1-min move >2% | 12.9 | 12.9 | 0.4 | 0.4 | 0.4 | 1.8 | 1.2 | 0.2 |
| median unadjusted price $ / 1-cent tick (bps) | 36.21 / 2.76 | 12.89 / 7.76 | 269.83 / 0.37 | 325.10 / 0.31 | 178.07 / 0.56 | 73.56 / 1.36 | 33.72 / 2.97 | 588.50 / 0.17 |

- Scorecard, 2022–24, selected rows ([scorecard_secondary.csv](../../analysis/behavior/output/scorecard_secondary.csv)):

| Metric | SOXL | SOXS | SOXX | SMH | NVDA | TQQQ | SQQQ | QQQ |
|---|---|---|---|---|---|---|---|---|
| daily range % median | 7.35 | 7.35 | 2.41 | 2.34 | 3.78 | 4.66 | 4.71 | 1.57 |
| 1-min RMS (bps) | 26.5 | 27.0 | 8.9 | 8.6 | 13.9 | 18.1 | 18.1 | 6.0 |
| AC 5-min deseas. | -0.020 | -0.029 | -0.017 | -0.019 | -0.027 | -0.021 | -0.029 | -0.019 |
| VR(60) deseas. [z] | 1.002 [+0.1] | 0.938 [-3.5] | 0.993 [-0.4] | 1.001 [+0.0] | 0.948 [-2.8] | 0.993 [-0.4] | 0.929 [-4.0] | 1.003 [+0.2] |
| efficiency ratio full day obs/random | 1.087 | 1.075 | 1.084 | 1.107 | 1.056 | 1.123 | 1.101 | 1.128 |
| trend days % | 19.4 | 21.0 | 22.0 | 21.5 | 21.6 | 21.0 | 21.8 | 21.6 |
| OR30: close beyond 1st break % | 54.0 | 54.4 | 56.1 | 55.2 | 53.2 | 54.7 | 54.5 | 55.3 |
| gap fill % (0.25-0.5 ATR) | 52.8 | 51.4 | 50.0 | 54.0 | 51.8 | 53.3 | 55.7 | 54.5 |
| median abs gap % | 2.39 | 2.38 | 0.81 | 0.82 | 1.06 | 1.32 | 1.33 | 0.45 |
| 5-min beta / corr vs SOXX | +2.96 / +0.977 | -2.95 / -0.971 | (vs QQQ) +1.28 / +0.875 | +0.95 / +0.970 | +1.32 / +0.831 | +1.80 / +0.875 | -1.79 / -0.872 | +0.60 / +0.875 |
| median abs closing-auction jump bps | 11.1 | 9.5 | 3.0 | 1.9 | 1.4 | 3.7 | 4.7 | 1.0 |
| % days with a 1-min move >2% | 6.2 | 6.7 | 0.0 | 0.0 | 0.4 | 1.7 | 1.7 | 0.0 |
| median unadjusted price $ / tick bps | 22.97 / 4.35 | 20.51 / 4.88 | 414.94 / 0.24 | 220.80 / 0.45 | 245.07 / 0.41 | 39.89 / 2.51 | 23.09 / 4.33 | 357.68 / 0.28 |

### Inferences
- Leverage multiplies the volatility budget roughly in proportion (3× SOXX), but it does not add serial structure. Normalized path behavior of SOXL is the semis/Nasdaq complex's behavior, scaled.
- TQQQ/SQQQ are the closest behavioral analogues (same mechanics). They have lower volatility (range about half of SOXL's), slightly more trend and opening-range follow-through in 2024–26, and a larger share of extremes outside the first hour.

### Gaps
- Scorecard values are point estimates. Standard errors are available for AC (t), VR (z) and non-overlapping VR (CI) in the underlying CSVs, but not for day-type shares or VWAP rates beyond the random benchmark.

## Behavior verdict: what the data says about intraday suitability

### Takeaway
**Favourable, measured, stable behaviors for short-horizon trading:**
- a very large intraday movement budget: median range about 7%, 1-minute RMS about 29 bps, 3× SOXX;
- movement concentrated at predictable times: the opening hour carries about 62–71% of the range, and the day's high or low falls in the first hour on 84–87% of days;
- effectively continuous trading from 04:00, including pre-market, with no detected halts;
- a precise, formula-driven link to the semis basket (beta ≈ 3, correlation 0.99 at 5 minutes, leverage drift as theory predicts);
- no measurable lag versus drivers at 1-second resolution;
- a tight SOXL–SOXS mirror.

**Unfavourable behaviors:**
- no exploitable serial dependence at 1–30 minutes: autocorrelation ≈ 0, VR within 3–6% of 1, DFA ≈ shuffled, continuation after 2σ moves ≈ 50%, runs ≈ random;
- opening-range breakouts, VWAP crosses and VWAP reversion that are indistinguishable from, or weaker than, random;
- mild mean reversion and choppier midday paths in 2024–26;
- no GHLZ momentum, and a late-day reversal tendency;
- large overnight gaps that move a big share of the day's range before the open;
- fat tails (1-minute moves above 2% on 6–13% of days, up to about ±9–11%, 5-minute moves up to about ±19–21%);
- closing-auction prints that differ from the last trade by 6–11 bps (median), and occasionally by more than 100 bps.

**SOXL vs SOXS:** identical volatility, range, gap and day-type profiles. They differ in:
- SOXS's asymmetric leverage drift (sensitivity grows on up days, to about −4.2 at +5%, while SOXL's shrinks);
- SOXS's printed-price path, which is bounce- and discreteness-dominated whenever its price is low. That was the case for 424 of 1,178 sessions, when 1-minute autocorrelation was −0.105 and VR(60) 0.74; SOXS behaves like SOXL once its price is $20–50;
- SOXS trades in fewer seconds (74% vs 83%) and carries less closing volume.

### Cited Findings
- Movement budget: median daily range 7.35 → 6.68% (SOXL) and 7.35 → 6.98% (SOXS); 1-minute RMS 26.5 → 28.9 bps; range above 5% on 82 → 75% of days. — [vol_daily_range_atr.csv](../../analysis/behavior/output/vol_daily_range_atr.csv); [vol_realized_by_horizon.csv](../../analysis/behavior/output/vol_realized_by_horizon.csv)
- Timing concentration: first hour = 0.62 → 0.71 of the day's range; high or low in the first 60 minutes on 84.1 → 86.8% of days (benchmark 79.8 → 82.5%); first-5-minute volatility 3.8–4.0× the midday minimum. — [open_opening_range.csv](../../analysis/behavior/output/open_opening_range.csv); [day_types.csv](../../analysis/behavior/output/day_types.csv); [vol_ushape_5min.csv](../../analysis/behavior/output/vol_ushape_5min.csv)
- Continuity: RTH minute-bar coverage 100%; trades in 83% (SOXL) and 74% (SOXS) of RTH seconds; pre-market bars in 325–330 of 330 minutes; zero ≥5-minute RTH bar gaps. — [data_coverage.csv](../../analysis/behavior/output/data_coverage.csv); [link_second_bar_coverage.csv](../../analysis/behavior/output/link_second_bar_coverage.csv); [ext_hours_summary.csv](../../analysis/behavior/output/ext_hours_summary.csv); [tails_rth_minute_bar_gaps_ge5min.csv](../../analysis/behavior/output/tails_rth_minute_bar_gaps_ge5min.csv)
- Driver linkage: 5-minute beta +3.00 / −3.02 (correlation 0.992 / −0.970); leverage-drift interaction −5.84 (theory −6) for SOXL and −13.56 (theory −12) for SOXS; 1-second Hayashi–Yoshida peak at 0 s for all pairs on all 10 days. — [link_betas_correlations.csv](../../analysis/behavior/output/link_betas_correlations.csv); [link_leverage_drift_regression.csv](../../analysis/behavior/output/link_leverage_drift_regression.csv); [link_leadlag_1sec_summary.csv](../../analysis/behavior/output/link_leadlag_1sec_summary.csv)
- No serial dependence ([dir_autocorr_by_horizon.csv](../../analysis/behavior/output/dir_autocorr_by_horizon.csv); [dir_variance_ratios.csv](../../analysis/behavior/output/dir_variance_ratios.csv); [dir_dfa_hurst.csv](../../analysis/behavior/output/dir_dfa_hurst.csv); [dir_continuation_after_large_moves.csv](../../analysis/behavior/output/dir_continuation_after_large_moves.csv); [dir_run_lengths.csv](../../analysis/behavior/output/dir_run_lengths.csv)):
  - SOXL deseasonalized autocorrelation: 1-min −0.002 → −0.006; 5-min −0.020 → −0.019.
  - VR(15): 0.981 → 0.974.
  - DFA α: 0.514 → 0.515 (shuffled 0.520 → 0.522).
  - Continuation after 1-minute 2σ moves: 50.0% at 5 minutes in both windows.
  - Mean run length: 1.98 vs 2.00 random.
- Opening range, VWAP and close ([open_opening_range.csv](../../analysis/behavior/output/open_opening_range.csv); [vwap_behaviour.csv](../../analysis/behavior/output/vwap_behaviour.csv); [close_intraday_momentum_ghlz.csv](../../analysis/behavior/output/close_intraday_momentum_ghlz.csv)):
  - 30-minute opening-range close beyond the break level: 54.0 → 49.7%.
  - VWAP crosses: 6.90 / 6.39 per day vs random 7.05 / 6.50.
  - 30-minute VWAP revisit after a 1σ close: 25.1 / 25.3% vs random 30.4 / 29.0%.
  - GHLZ slope: −0.022 → −0.019 (n.s.); 09:30–15:30 → last-30 slope −0.043 (t −2.4) in 2024–26.
- Gaps and tails ([open_gap_distribution.csv](../../analysis/behavior/output/open_gap_distribution.csv); [tails_frequency.csv](../../analysis/behavior/output/tails_frequency.csv); [tails_top10_moves.csv](../../analysis/behavior/output/tails_top10_moves.csv); [close_last10min_and_auction.csv](../../analysis/behavior/output/close_last10min_and_auction.csv); [tails_closing_dislocations_gt100bps.csv](../../analysis/behavior/output/tails_closing_dislocations_gt100bps.csv)):
  - Median |gap| 2.39 → 2.81%; above 5% on 16.8 → 28.8% of days.
  - A 1-minute move above 2% on 6.2 → 12.9% of days; largest 1-minute moves +8.98% (SOXL) and −10.71% (SOXS).
  - Median |auction jump| 11.1 → 6.2 bps (SOXL) and 9.5 → 11.1 bps (SOXS); two SOXL closing dislocations above 100 bps.
- SOXL vs SOXS ([link_leverage_drift_beta_bins.csv](../../analysis/behavior/output/link_leverage_drift_beta_bins.csv); [dir_tick_size_stratified.csv](../../analysis/behavior/output/dir_tick_size_stratified.csv); [close_last10min_and_auction.csv](../../analysis/behavior/output/close_last10min_and_auction.csv); [link_second_bar_coverage.csv](../../analysis/behavior/output/link_second_bar_coverage.csv); [link_soxl_soxs_mirror.csv](../../analysis/behavior/output/link_soxl_soxs_mirror.csv)):
  - Beta at SOXX ≈ +5% on the day: SOXL 2.63, SOXS −4.24. At −5%: 3.41 and −2.41.
  - SOXS at tick ≥ 10 bps: autocorrelation −0.105, VR(60) 0.741. At 2–5 bps: −0.002 and 0.995.
  - 15:30–15:59 share of minute volume: SOXL 12.5% vs SOXS 8.0% in 2024–26.
  - Share of RTH seconds with trades: 83% vs 74%.
  - Intraday mirror divergence change: median 4.9 → 5.6 bps.

### Inferences
- **Favourable for short-horizon trading, by behavior alone:**
  - (a) the amount and timing of movement — large, and concentrated in the first hour and near the close;
  - (b) the mechanical, well-measured relationship to the semis basket, including the leverage-drift formula;
  - (c) continuous prints and absence of halts;
  - (d) the SOXL/SOXS mirror.
- **Unfavourable:**
  - (a) the absence of statistically meaningful persistence or reversal at 1–30 minutes — the path is nearly a random walk scaled up 3×, and the few significant tendencies are regime-dependent and small (a few bps);
  - (b) the large share of movement delivered by overnight gaps and by rare jump minutes;
  - (c) close-print behavior that differs from continuous trading.
- **SOXL vs SOXS:**
  - SOXL's printed price path is the cleaner of the two at 1–15 minutes whenever SOXS is low-priced.
  - The two are equivalent in range and timing.
  - They differ structurally in how their index sensitivity changes as the day's semis move accumulates.

### Gaps
- All statements are about price behavior in last-trade minute and second bars. Quote-based spreads, depth and execution quality (which determine how much of the measured movement is capturable) are outside this study's scope; they are covered by the separate microstructure/liquidity notes.
- Multiple testing: dozens of statistics were computed per ticker and window, so isolated |t| ≈ 2 results should be treated as weak evidence unless they persist across quarters (flagged in section 10).
