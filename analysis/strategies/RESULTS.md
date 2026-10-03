# Strategy research results: pre-registered studies 1–12

Run 2026-09-28. The rules were fixed in [REGISTRY.md](REGISTRY.md) before any study ran, as shown by the git history.
[RESEARCH_PLAN.md](../../RESEARCH_PLAN.md) describes the plan for Studies 1–9. Studies 10–12 were requested afterwards:
1-minute Hitchhiker-, Bone Zone- and flag-like momentum scalps. They were registered in REGISTRY.md and committed before
running. Every number below comes from the per-study CSVs in this folder.

## Bottom line

**No rule passed the pre-registered bar.**
- 94 variants were tested across Studies 1–6, 8 and 10–12, plus 60 pattern screens in Study 7.
- None meets criteria 1–5.
- None survives the Benjamini–Hochberg correction across all 94. The smallest q is 0.58, against a required 0.10. Within Studies 1–8 alone it is 0.43.
- The **2026 holdout (Jan–Sep 2026) has not been opened for any rule.** It is still available as a one-time test.
- **Independent test on 2011–2018** (downloaded later; no rule had seen it). The breakout, noise-boundary and late-day-fade rules all lost money after costs there, and so did the best combination picked on 2019–2025. Their intraday momentum edge is specific to the post-2019 period (see "Best-combination search and the 2011–2018 test").
- **The 2026 holdout has now been opened, once**, for the final strategy S15 (the plain 15-minute breakout).
  - It failed the pre-registered test: −1.9 bps per trade after costs (case Q −1.3), over 143 trades.
  - The kill-switch version lost −65 bps per trade.
- **Conclusion:** no rule found in this project has a demonstrated edge on data it was not fitted to.
- **The underlying effect is established; a profit after costs is not.** Going with SOXL's morning move beats picking a side at random by 0.2–0.3% a trade in each of 2011–2018, 2019–2025 and 2026 (random-direction test, p ≈ 0.002). Most of it is on the SOXL side (up moves, p ≈ 0.005). SOXS on down moves paid only after moves of 3% or more. Costs took most of that before 2026. What is left after costs (+0.07% a trade on average over 2011–2026) is not distinguishable from zero (reality check, p ≈ 0.2). See "Luck check" under "Live trend odds".
- **Trend days can be ranked at 10:30; the move after 10:30 cannot (Study T3, FAIL).** Across 128 technical inputs and 6,906 combinations:
  - SOXX's own move and breadth across the big chip stocks tell trend days apart (AUC about 0.7 on unseen years).
  - RSI, yesterday's high/low, pivots and moving averages carry nothing.
  - No input or combination reliably predicted SOXL's move from 10:30 to the close.

**The 1-minute momentum scalps (Studies 10–12, 24 variants) fail differently from the near-misses: they have no edge before costs.**
- In validation, Bone Zone-like and flag-like entries on SOXL's 1-minute chart capture −10 to +3 bps gross per trade on average.
- Hitchhiker-like entries range from −24 to +17 bps gross. The positive ones rest on 44–105 validation trades, and they lose in 2022–24.
- They pay about 7 bps per round trip.
- 21 of the 24 lose after costs in validation, and none is significant (within-family q = 1.0).
- The Bone Zone-like and flag-like rules lose in almost every year from 2019 to 2025.
- SOXL is not too expensive to scalp. Stops sit 45–105 bps away, so costs are only 7–17% of the risk per trade. These particular entries simply do not predict the next few minutes.

For Studies 1–8, the main failure is statistical significance in the 15-month validation window. Two rule families were consistently positive after costs in both development and validation, and passed every robustness and cross-ticker check except significance:
- The **15-minute opening-range breakout** (Study 3).
- **Noise-boundary momentum** (Study 4).

They are now in forward paper trading.

## Study by study

Numbers are case-B net bps per trade: measured spreads plus $0.0035/share and fees.
- **val** = 2024-10-01 → 2025-12-31.
- **dev** = 2022-01-03 → 2024-09-30.
- **pre** = 2019-01-02 → 2021-12-31.

| Study | Best variant | val net (t) | dev net | pre net | Verdict |
|---|---|---|---|---|---|
| 1 Late-day fade | S1-06 (\|SOXX\| ≥ 1%, auction exit, no gate) | +26.1 (1.50) | +0.3 | −26.4 | **Fail.** Positive in val for all 12 variants, but the pre-sample loses (−15 to −44, t down to −4.2), and the regime gate did not switch it off in 2019–21. Regime-dependent. |
| 2 Opening burst | S2-09 (k = 3, 1-min hold) | +1.6 (0.17) | −4.3 | −5.6 | **Fail.** Entering at the next minute's open captures about +3.6 bps against about 7.7 bps of costs. Real-quote fills match case B. The close-to-close effect found earlier cannot be traded. |
| 3 Opening-range breakout | S3-01 (15-minute range, stop at the other side) | **+48.9 (1.74)** | +30.1 (t 1.85) | +0.2 | **Near-miss.** Positive in 100% of validation quarters. It keeps 92% of its edge with a one-minute-late entry, the neighbour (20-min range) makes +41.9, and SOXX and SMH are positive too. It fails only t ≥ 2 and BH. The published 5-minute-candle version does not transfer (+3.0). |
| 4 Noise-boundary momentum | S4-04 (k = 1.5, half-hour checks) | +27.8 (1.02) | +24.5 | +5.4 | **Near-miss.** All 4 variants are positive in dev and val (S4-02: dev t 2.16). The implementation reproduces the published SPY result: on SPY, mean gross +1.6 to +4.1 bps, t 1.8–3.5. It fails t ≥ 2 and BH. |
| 5 Big-day gates (exploratory) | S5-02 (breakout + early volume ≥ 1.5×) | +263 (1.64) | +110 | −59 | **Diagnostic only.** The early-volume gate raises the breakout's per-trade result sharply, but on only 32 validation trades, and 2019–21 loses. Other gates do not help both periods. NR7 does not predict a bigger next day (7.1% vs 7.4% median range, p = 0.40). |
| 6 Failed-break fade | S6-02 (pre-market levels, VWAP target) | +6.2 (0.69) | −8.3 | −3.5 | **Fail.** Fading failed prior-day high/low breaks loses −28 to −36 (t −2.2 to −3.1). |
| 7 Chart patterns | — | — | — | — | **Fail.** 0 of 60 stage-1 tests pass (pattern × context × horizon). No combination shows even a significant positive edge before costs. |
| 8 Execution (exploratory) | S8-01 (breakout, short SOXL for bearish legs) | **+49.3 (1.89)** | +26.6 | +2.3 | **Diagnostic only.** Replacing SOXS with short SOXL adds about 60 validation trades that the $10 SOXS rule used to skip. This is the highest validation t of any rule. Limit-order entries were deferred as second-order. |
| 9 Monitors and paper log | — | — | — | — | Built. Forward testing starts 2026-09-28. |
| 10 Hitchhiker-like | S10-02 (breakout by 09:59, buy-stop entry, half at 1R + EMA9 trail) | +9.3 (0.65) | −16.7 | +1.1 | **Fail.** 44 validation trades. In 2022–24, 11 of 12 variants lose and the 12th is flat (+0.1). Close-confirmed entries lose −7 to −31 in validation. |
| 11 Bone Zone-like | S11-03 (next-open entry, half at 1R + EMA21 trail) | −11.4 (−2.91) | −7.0 | −4.7 | **Fail.** All 6 variants lose in all three periods (validation t −2.3 to −3.7). Gross is about 0 or negative on both bull and bear legs. |
| 12 Flag-like | S12-01 (buy-stop on the trendline break, measured-move target) | −4.6 (−0.79) | −6.1 | −5.2 | **Fail.** Best of 6. Gross is +2.8 bps, below the ~7 bps cost. The other five lose −8 to −17 in validation. |

## Why nothing passed

Validation per-trade standard deviations were:
- about 440–460 bps for the breakout rules (S3-01, S8-01)
- about 300 bps for S4-04

With the validation trade counts (125–308), t ≥ 2 needs a mean of about +52–56 bps per trade. The best rules made +43 to +49.

At the same edge and trade rate, about 4–5 more months of trades would clear t ≥ 2. Forward paper trading supplies exactly that.

Multiple testing works against every individual result too. The smallest one-sided p (0.030) becomes q = 0.43 after correcting for 70 variants, and 0.58 after correcting for all 94 variants.

The Studies 10–12 scalps fail for a different reason: their mean is negative, not just too small to be significant.

## Studies 10–12: 1-minute momentum scalps

The rules are in [REGISTRY.md](REGISTRY.md): pole or impulse, pause or pullback, trigger, stop, exits, neighbours and delay.
Per-variant numbers are in `study10_hitchhiker/`, `study11_bone_zone/` and `study12_flags/`. The breakdowns are in `scalps_breakdown/`.

**How many setups SOXL gives.** One-position-at-a-time counts, validation (Oct 2024 → Dec 2025, 315 sessions):

| Setup | Trades in validation | Median hold |
|---|---|---|
| Hitchhiker-like (first setup of the day) | 35–105, depending on the breakout deadline (09:59 / 10:14 / 10:29) | 11–19 min |
| Bone Zone-like | 347–408 (about 1.1–1.3 a day) | 2–11 min |
| Flag-like | 370–450 (about 1.2–1.4 a day) | 8–18 min |

**Risk per trade vs cost.** Setup geometry only (`scalps_breakdown/setup_geometry.csv`):

| Setup | Median stop distance R (validation) | Round trip, case B | Cost as a share of R |
|---|---|---|---|
| Hitchhiker-like, buy-stop | 85 bps | 5.9 bps | 7% |
| Bone Zone-like, next-open entry | 44 bps | 6.2 bps | 15% |
| Bone Zone-like, buy-stop | 58 bps | 6.2 bps | 11% |
| Flag-like, buy-stop | 55 bps | 6.2 bps | 11% |
| Flag-like, close entry | 67 bps | 6.2 bps | 10% |

**Why they fail.** Numbers are validation, case B.
- **No directional edge in the entries.**
  - Bone Zone-like: all 6 variants have gross −2.5 to −9.8 bps.
  - Flag-like: gross −9.6 to +2.8.
  - The Bone Zone-like next-open version with a 2R-or-retest target (S11-01) wins 34% of trades. Target exits average +83 bps net and stop-outs −61 bps. With those payoffs, breaking even needs a hit rate of roughly 42%.
- **Bearish legs, which trade SOXS, are the worst.** In validation, bear flags lose −17 to −31 bps per trade. Bearish Bone Zone-like legs lose −9 to −26.
- **Entries.**
  - For Hitchhiker-like breakouts, waiting for a 1-minute close above the high is much worse than a resting buy-stop: −7 to −31 against −9 to +9 in validation. The close-confirmed entry pays up after the breakout minute.
  - For Bone Zone-like pullbacks, the buy-stop above the trigger candle is worse than taking the next open.
- **Fill risk.** Case Q (real NBBO) is within about 1 bp of case B throughout. Case S, with one extra cent per stop-order fill, costs another 1–7 bps.
- **No stable pocket.**
  - By year: the Hitchhiker-like rule made money in 2019 in all 12 variants and lost in 2020 in all 12. After that it was mixed.
  - Bone Zone-like and flag-like lose in almost every year.
  - By time of day, no bucket is positive in all three periods. For example, flag close-entries in 09:30–10:00 made +24 bps in 2022–24, but −11 in 2019–21 and −14 in validation. These splits are exploratory.
- **Cross-checks.** In validation on SOXX and SMH, the Bone Zone-like and flag-like rules are within ±3 bps gross, and the Hitchhiker-like rules range from −14 to +7. The absence of an edge is not specific to the leveraged ETF.

## Exploratory: what separated the winning scalps (Studies 10–12)

Script: `scripts/research/scalp_winners.py`. Outputs: `scalps_winners/`.
- Coverage: 2019–2025 only, per period. Nothing here was pre-registered.
- Features: the look-ahead-tested data elements (`soxlab/features.py`), sampled at the last completed bar before entry, plus the setup's shape.

**Winners exist, but not often enough.** 23–42% of trades win, and the average win is larger than the average loss:

| Setup | Win rate | Average win | Average loss |
|---|---|---|---|
| Bone Zone-like | 34–38% | +72 to +96 bps | −45 to −72 bps |
| Flag-like | 23–31% | +145 to +174 bps | −52 to −84 bps |
| Hitchhiker-like | 35–42% | +100 to +141 bps | −81 to −107 bps |

The single best trades made +4% to +19%. The winners still do not cover the more frequent losers.

**Which data elements separated winners from losers.** 41 elements × 6 rule versions = 248 tests, each checked in 2019–21, 2022–24 and 2025 separately.
- **Only one relationship holds up** (same sign in all three periods, BH q ≤ 0.10): for Hitchhiker-like breakouts, whether the trade goes the same way as the opening gap.
  - Related elements say the same thing: the pre-market move, and price already beyond the prior day's high (for longs) or low (for shorts).
  - The rank correlation with the trade result is +0.13 to +0.24 in each period, for the close-entry version.
- **Split by gap direction, across all 12 Hitchhiker-like variants:**
  - Against the gap, every variant loses in every period: −7 to −70 bps per trade.
  - With the gap, 4 variants are positive in all three periods. These are the close-confirmed entries with breakouts by 09:59 or 10:14.
  - The best is S10-03: +15 (2019–21), +24 (2022–24) and +27 (2025) bps per trade, over 89 trades (pooled t 1.6).
- **By gap size** (`scalps_winners/gap_size_buckets.csv`, measured in the trade's direction; SOXL's median |gap| is about 2%):
  - A 1–3% gap is the sweet spot. All 12 variants are positive in all three periods: +8 to +58 bps per trade, win rate 52–65%, 37–118 trades each, t 1.0–3.3.
  - Gaps larger than 3% lose in all 12 variants (−10 to −18).
  - Trades against the gap lose in all 12 variants.
  - Gaps of 0–1% are mixed.
  - The bucket edges were fixed at round numbers before the results were seen, but the split itself is post-hoc.
- **Bone Zone-like and flag-like:** no element holds up. Going with the gap does not help them either; with-gap trades lose −5 to −11 bps.
- **Elements that do not separate winners in any setup:**
  - VWAP distance, relative volume, EMA9/21 trend, time of day.
  - SOXX, NVDA and QQQ short-term moves.
  - 1-minute, 30-minute and daily volatility.
  - Impulse size, pullback depth, volume dry-up, stop size, trade number and event days.
- **Combined model:** using all elements, fitted on 2022–24 only, it does not pick winners in 2019–21 or 2025. AUC is 0.45–0.61, where 0.5 is a coin flip.
- **Status:** these findings are post-hoc. A gap-direction Hitchhiker needs its own pre-registered test on unseen data: the sealed 2026 holdout, or forward trades.

## Exploratory: trend and medium days

Script: `scripts/research/trend_days.py`. Outputs: `trend_days/`.
- Coverage: 2019–2025 only. Nothing here was pre-registered.
- Day type is the SOXX open→close move: quiet < 1%, medium 1–2%, trend ≥ 2%. It is known only after the close.
- Mix of days: trend 16–27%, medium 26–30%, quiet 44–57%, depending on the period.

**What made money on each day type** (net bps per trade, 2019–2025):

| Rule | Trend days | Medium days | Quiet days |
|---|---|---|---|
| 15-min opening-range breakout (S3-01) | **+361** (79% winners) | +41 (63%) | −144 (24%) |
| Same, bearish = short SOXL (S8-01) | **+398** | +45 | −149 |
| Noise-boundary momentum (S4-02) | +173 | −18 | −89 |
| Hitchhiker-like (S10-05 / S10-07) | +42 / +44 | −19 / −17 | −36 / −41 |
| Flag-like (S12-01) | +15 | −7 | −16 |
| Bone Zone-like (S11-01) | −1 | −7 | −14 |
| Late-day fade (S1-06) | −47 | −16 | +49 |

- **Direction:** on trend days the breakout's first break points the right way 85% of the time. On medium days it is 79%, and on quiet days 61%.
- **Entry time:**
  - On trend days, the earliest breaks (09:45–10:00) are the best: +388 bps, 81% winners.
  - On medium days, later breaks are the best: +77 (10:00–10:30) and +137 (10:30–12:00), against +17 for 09:45–10:00.
- **Medium days by period:** the breakout's result on medium days is +82 (2019–21), −4 (2022–24) and +50 (2025).

**What is knowable in advance.** `trend_days/conditions.csv` gives the share of trend days and the breakout's result per condition and period.
- **More trend days in all three periods:**

  | Condition | Share of trend days | Other days |
  |---|---|---|
  | High recent-volatility regime (SOXL's 20-day median range in its top third) | 35% | 10% in the calmest third |
  | QQQ below its 50-day average | 36% | 14% above it |
  | Wide first-15-minute range | 35% | — |
  | Heavy pre-market volume or range | 27–33% | — |
  | Big early drive or heavy first-15-minute volume | 28–31% | — |

- **The breakout does better in all three periods under only one condition:** QQQ below its 50-day average. It made +8 / +39 / +172 against −2 / +23 / +12 when QQQ was above.
  - The 2019–21 difference is small and rests on about ten January-2019 trades.
  - An earlier version of this analysis counted early-2019 sessions, which had no 50-day history yet, as "below". The average is now taken from QQQ's daily history back to 2010.
- **The other conditions** raise the odds of a trend day, but the breakout's result under them was negative in 2019–21.
- **Combined detector:** an L2 logistic model fitted on two periods and scored on the third.
  - Out-of-sample AUC for trend days is 0.66–0.70 at 09:30 and 0.69–0.73 at 09:45.
  - Its top third of days holds 33–37% trend days, against 9–10% in its bottom third.
  - The breakout on the top third made +40 to +45 bps per trade (t 2.0–2.1), against +4 to +10 on the rest.
  - That is not uniform by period. With the 09:30 model the top third was positive in every period (+10 / +36 / +98), but it lost to the bottom third in 2022–24. With the 09:45 model it was −15 in 2019–21.
- **Status:** post-hoc. The QQQ-below-50-day filter repeats an earlier exploratory finding, so it is not independent confirmation.

## Exploratory: when to take the 15-minute breakout

Script: `scripts/research/orb_conditions.py`. Outputs: `orb_conditions/`.
- Scope: every S3-01 trade, described by what was known when its trigger bar closed. 2019–2025 only.
- About 50 buckets were examined, so single buckets can look good by chance.

**Better or worse than the rest in all three periods** (net bps per trade, 2019–21 / 2022–24 / 2025):

| Signal | Condition | Result | Rest |
|---|---|---|---|
| Take | QQQ below its 50-day average | +8 / +39 / +172 | −2 / +23 / +12 |
| Take | Breakout-minute volume ≥ 3× normal for that minute (60% winners, about 21 trades a year) | +84 / +54 / +612 | — |
| Skip | Break against a gap larger than 1% (36% of trades) | −49 / +12 / +44 | +29 / +41 / +52 |
| Skip | Breakout-minute volume < 1.5× normal (54% of trades) | −20 / +25 / +13 | +19 / +37 / +114 |

**Stable, but not better than the rest in every period:**
- Pre-market moved the same way as the break: +44 / +46 / +46. Opposite: −44 / +12 / +53.
- A 1–3% gap in the break's direction: +42 / +43 / +43.
- Chip-earnings reaction days: +61 / +32 / +45.

**No consistent effect:** trigger time, opening-range size, how far the trigger bar closed beyond the range, NVDA/QQQ direction at the trigger, weekday, and CPI/jobs or FOMC days.

**Filters applied:**

| Filter | 2019–21 | 2022–24 | 2025 | Pooled | Trades a year | 7-year total |
|---|---|---|---|---|---|---|
| All breaks, as tested | +0 | +30 | +49 | +21 (t 2.1) | about 200 | +296% |
| Skip breaks against a >1% gap | +29 | +40 | +51 | +38 (t 3.1) | about 128 | +338% |
| Only when the pre-market moved the same way | +44 | +46 | +46 | +45 (t 3.2) | about 103 | +328% |
| Skip both skip conditions | +45 | +39 | +109 | +51 (t 2.7) | about 63 | +227% |

The 7-year total is the sum of per-trade results, in % of one position.

**Bearish execution on the same signals** (days SOXS ≥ $10):
- Buy SOXS: +5 bps per trade (−23 / +7 / +60).
- Short SOXL: +9 (−24 / +11 / +77).
- Shorting SOXL also trades the 345 signals skipped while SOXS was under $10. Those made +10 per trade.

**Status:** post-hoc. The gap and pre-market direction effect matches the Hitchhiker-like finding: trades that go with the overnight move do better. That is two setups agreeing, but it still needs a test on unseen data.

## Strategy S13: final breakout rules (locked before the 2026 holdout)

Playbook: [ORB_STRATEGY.md](ORB_STRATEGY.md). Definition: [REGISTRY.md](REGISTRY.md), Strategy S13. Design grid: `orb_strategy/`.
- **How it was chosen:** stops, targets and trade management were picked from 144 configurations on 2019 → Sep 2024 only. Oct 2024 → Dec 2025 served as the check.
- **Rules:**
  - Skip breaks against a gap larger than 1%.
  - Stop at the other side of the 15-minute range.
  - Exit at 11:00 if the trade is not in profit.
  - Otherwise hold to 15:55.
  - No target and no stop moves.
- **Results, bearish via SOXS:** +25 / +40 / +60 bps per trade (2019–21 / 2022–24 / Oct 2024–Dec 2025). Win rate 40%, worst drawdown −48% of one position. The as-tested breakout had 47% and −146%.
- **What the design data rejected:**
  - Profit targets (2R, 3R, half at 2R) lowered results, most of all in the check period.
  - Break-even stop moves cost about 4–5 bps per trade.
  - A mid-range stop cut the win rate to 32%.
  - The breakout-volume filter did not add to the gap filter.
- **Win rate:** no configuration reached a 55% win rate on the design sample. This breakout's win rate stays at about 40–50%, and its profit comes from the size of trend-day winners.

## Best-combination search and the 2011–2018 test

Scripts: `scripts/research/orb_best.py` (search, and the one-time `--deep` test) and `deep_diagnostics.py`. Outputs: `orb_best/`.
- **Deep-history data:** minute bars from 2010–2018 (`download_deep_history.py`) and NBBO spread samples for SOXL/SOXS in 2011–2018.
- **Search:** 480 combinations of everything considered, on 2019–2025, with the selection rule fixed in advance:
  - range: 15, 20 or 30 minutes;
  - filters: gap direction, pre-market direction, breakout-minute volume;
  - stop at the range, or capped at 4%;
  - time stop: none, 10:30, 11:00 or 12:00;
  - exit: hold, or half off at 2R;
  - bearish execution: SOXS or short SOXL.
- **The pick (S14-A):** 15-minute range, trade only when the pre-market moved in the break's direction, stop capped at 4%, 12:00 time stop, hold to 15:55.
  - 2019–2025: +46 / +47 / +56 bps per trade by period, t 3.65.
  - It was registered before the deep test.

**2011-06 → 2018 (never used before), case B with that era's measured spreads:**

| Rule | Trades a year | Win rate | Net per trade | t | Positive years |
|---|---|---|---|---|---|
| S14-A (the pick) | 67 | 34% | −16 bps | −1.5 | 2 of 8 |
| S14-B (high win rate) | 68 | 45% | −5 | −0.4 | 3 of 8 |
| Plain 15-minute breakout (S3-01) | 237 | 43% | −12 | −2.0 | 0 of 8 |
| S13-A | 165 | 34% | −16 | −2.7 | 1 of 8 |
| Noise-boundary momentum, k = 1.0 / 1.5 | 226 / 135 | 33% / 34% | −10 / −10 | −2.5 / −2.0 | 1 of 8 / 2 of 8 |
| Late-day fade (S1-06) | 96 | 35% | −28 | −8.1 | 0 of 8 |

**Why:**
- **The edge before costs was about three times smaller.** The plain breakout made +10 bps gross in 2011–2018, against +30 in 2019–2025. Noise-boundary momentum made +9 against +25.
- **Costs were more than twice as high:** 21 bps per round trip, against 9. Measured half-spreads were 5–10 bps then, against 1–3 now.
- **Trend days were rarer.** They made up 10% of breakout trades, against 22%. SOXL's median daily range was 3.6–4.9% in 2012–2017, against 6–10% in 2020–2025.
- **The breakout itself still worked on trend days** (+345 bps a trade), but it lost on the far more common quiet days.
- **The filters and exits picked on 2019–2025 did not generalise.** S14-A's gross in 2011–2018 was +4.5 bps, against +10 for the plain rule.
- **No volatility-regime cut-off rescues 2011–2018.** The plain breakout lost in every bucket of SOXL's trailing 20-day range.
- **A performance switch** (trade only while the previous 60 signals averaged > 0) made 2019–2025 better (+36 bps per trade, against +21) and halved the 2011–2018 loss in total (−104%, against −207%), but its trades there still averaged −20 bps.

**Conclusion:** no rule in this project made money after costs in both eras. SOXL's intraday momentum is positive before costs in both, but it only beat costs after 2019, when it was stronger and trading was cheaper. Any live use of the breakout is a bet that the post-2019 conditions continue. The 2026 holdout test and forward paper trading are the checks on that.

## Final strategy S15 and the 2026 holdout test (opened once)

Script: `scripts/research/holdout_test.py`. Outputs: `holdout_2026/`. The rules and pass criteria were registered in REGISTRY.md (commit c715100) before the holdout was opened.

| Rule, 2026-01-02 → 2026-09-25 | Trades | Win rate | Net per trade (case B) | t | Case Q | Gross |
|---|---|---|---|---|---|---|
| **S15 = plain 15-minute breakout (primary)** | 143 | 43% | **−1.9 bps** | −0.06 | −1.3 | +4.0 |
| S15-K (60-signal kill switch) | 60 | 37% | −65.5 | −1.29 | −64.9 | −59.4 |
| S8-01 (bearish = short SOXL) | 184 | 41% | −18.9 | −0.60 | −18.1 | −13.1 |
| S4-02 / S4-04 (noise-boundary momentum) | 103 / 56 | 31% / 36% | +2.7 / +6.4 | 0.14 / 0.25 | +2.9 / +6.3 | +7.7 / +11.3 |
| S13-A / S14-A | 81 / 76 | 35% / 34% | −9.4 / −6.8 | −0.26 / −0.19 | −8.8 / −5.9 | −3.7 / −1.1 |

- **Verdict: S15 fails.** Its registered pass criterion was case B ≥ 0 and case Q ≥ 0.
- **2026 was not a quiet year.** 31% of days were trend days and 28% were medium days, yet the breakout only broke even before costs.
- **Month to month it swung widely:** −105 bps per trade in February, +132 in March, −127 in April.
- **The kill switch was on for 42% of 2026 signals**, including the losing April, and it is off at the end of the holdout.

**Overall:**
- The breakout's 2019–2025 edge did not appear in 2011–2018 or in 2026.
- The filtered and optimised variants did no better out of sample.
- The only rules that were positive in 2026 (noise-boundary momentum, t 0.1–0.25) lost in 2011–2018.
- On this evidence, none of the tested intraday rules is a demonstrated edge for real money.
- They stay in the forward paper log so any change can be seen.

## Midday trend check (S16): the first idea positive in all three eras

Script: `scripts/research/midday_trend.py`. Outputs: `midday_trend/`.
- **The rule:** at a check time, if SOXL has already moved at least k% from its open, go with the move and hold to 15:55.
  - Up moves are bought as SOXL; down moves as SOXS.
  - Optionally, a stop exits if SOXL gets back to its opening price.
- **The grid:** 24 cells, fixed before running, all reported. Check at 11:00 / 12:00 / 13:00; k = 2 / 3 / 4 / 6%; stop none or at the open.

| | 2011–2018 | 2019–2025 | 2026 |
|---|---|---|---|
| Average over all 24 cells: gross / cost / net (bps per trade) | +29 / 17 / **+12** | +15 / 9 / **+7** | +14 / 4 / **+10** |
| Share of cells with net > 0 | 71% | 88% | 58% |
| S16 = 11:00, ±3%, stop at the open: net (t) | **+12.9 (0.8)** | **+20.4 (1.2)** | **+18.0 (0.4)** |
| S16: win rate / trades a year | 52% / 45 | 53% / 66 | 56% / 87 |

- **Positive in all three eras:** 8 of the 24 cells.
- **Unlike the opening breakout,** this effect was positive after costs in 2011–2018 too. It is small (+0.1–0.2% per trade), and each cell on its own is weak (t ≤ 1.3).
- **Registered as S16** and added to the forward paper log. No untouched history remains for this rule family.

## Live trend odds: what the move so far says about the rest of the day

Script: `scripts/research/intraday_trend_odds.py`. Outputs: `intraday_trend_odds/`.
- **Why:** a trend day (SOXX open→close ≥ 2%) is only known at the close. This is the version you can read live: SOXL's move from its 09:30 open at a given time, and what followed.
- **Setup:**
  - Checks at 10:00, 10:30, 11:00, 11:30, 12:00, 13:00 and 14:00 (bar closes).
  - Move buckets: 1–2 / 2–3 / 3–4 / 4–6 / ≥ 6%, either way.
  - "Going with it" means entering at the next minute's open (SOXL for up, SOXS for down) and exiting at 15:55, with case B costs. It runs with no stop, and again with a stop if SOXL gets back to its open.
- **Coverage:** all 35 cells are reported for 2011–2018, 2019–2025 and 2026, in `odds.csv` (per era) and `pooled.csv`. Exploratory: the grid was fixed, but no rule was selected in advance.

**Chance the day ends as a trend day in the move's direction** (pooled 2011–2026; per era in `odds.csv`):

| Move from the open | 10:00 | 10:30 | 11:00 | 12:00 | 13:00 | 14:00 |
|---|---|---|---|---|---|---|
| 1–2% | 10% | 6% | 5% | 4% | 3% | 2% |
| 2–3% | 16% | 12% | 11% | 8% | 5% | 3% |
| 3–4% | 26% | 25% | 23% | 14% | 11% | 8% |
| 4–6% | 43% | 44% | 37% | 34% | 31% | 30% |
| ≥ 6% | 69% | 69% | 71% | 80% | 82% | 82% |

**Riding the move to 15:55 barely pays.** From any check, SOXL keeps going the same way to the close 50–63% of the time. Net per trade going with the move, pooled, no stop (bold = positive in all three eras):

| Move from the open | 10:00 | 10:30 | 11:00 | 12:00 | 13:00 | 14:00 |
|---|---|---|---|---|---|---|
| 1–2% | −0.11% | −0.14% | −0.09% | +0.00% | +0.06% | −0.10% |
| 2–3% | +0.22% | +0.05% | +0.11% | +0.04% | −0.10% | −0.12% |
| 3–4% | **+0.38%** | **+0.44%** | **+0.24%** | −0.01% | −0.13% | −0.05% |
| 4–6% | +0.36% | +0.12% | −0.10% | +0.13% | +0.07% | **+0.10%** |
| ≥ 6% | −0.04% | −0.00% | **+0.13%** | +0.02% | +0.24% | +0.12% |

- **Positive in all three eras:** 7 of the 35 cells with no stop, and 4 of 35 with the stop at the open. What chance would give depends on the question (see the luck check below): about 1 if the morning direction carried no information, and about 4 if the net edge were exactly zero.
- **The one coherent cluster is a 3–4% move between 10:00 and 11:00.** With the stop at the open, 2011–2018 / 2019–2025 / 2026:

  | Check | Net per trade by era | Note |
  |---|---|---|
  | 10:00 | +0.19% / +0.43% / +0.27% | |
  | 10:30 | +0.29% / +0.36% / +0.88% | Pooled: +0.36% a trade, 52% winners, t 2.1, about 23 trades a year |
  | 11:00 | +0.27% / +0.44% / −0.95% | 2026 is 13 trades |

  It was found by looking at 70 cells, so it is a lead, not proof.
- **Chasing a move of 6% or more at 10:00–10:30 does not pay.** 69% of those days end as trend days that way, yet riding from there averages 0%. The trend-day label comes mostly from the move already made.
- **1–2% moves carry no information:** 48–51% winners, and the average is about zero (−0.14% to +0.15%).

**How much is left on the days that do end as trend days** (SOXL, medians, `trend_day_move_done.csv`, ranges over 2011–2018 and 2019–2025):

| Check | 10:00 | 10:30 | 11:00 | 11:30 | 12:00 | 13:00 | 14:00 |
|---|---|---|---|---|---|---|---|
| Share of the day's move already done | 26–27% | 38–41% | 46% | 54–56% | 60–62% | 68–71% | 79–81% |
| SOXL move still to come | 5.5–6.2% | 4.6–5.0% | 4.1–4.5% | 3.8% | 3.2% | 2.5–2.6% | 1.6–1.7% |

- 2026 was front-loaded: 44% of the move was done by 10:00 and 62% by 11:00.
- **So on real trend days there is plenty left at 10:30–11:00. The problem is picking them.** At that point only a quarter to a half of the days showing a 3–6% move become trend days, and the rest give back.

**Flipping sides when SOXL closes back through its open** (`flip_at_open.csv`):
- The setup: SOXL first moves k% one way, then a 1-minute close lands back through the open by 14:30.
- The trade: take the other side at the next open and hold to 15:55, with no stop.

| First move | 2011–2018 | 2019–2025 | 2026 |
|---|---|---|---|
| 2% | −0.21% (47% win, 56 a year) | +0.29% (53%, 77 a year) | −0.99% (39%, 103 a year) |
| 3% | −0.34% (48%, 22 a year) | −0.01% (52%, 42 a year) | −0.31% (44%, 66 a year) |
| 4% | −0.05% (51%, 6 a year) | −0.38% (51%, 22 a year) | +0.35% (46%, 36 a year) |

- The open cross is not a reliable switch signal. A move that fails usually leads to chop, not a trend the other way.
- **By direction** (`flip_at_open_by_direction.csv`), pooled over 2011–2026:
  - Flipping into SOXS after a failed up move lost on average at every threshold: −0.14% (2% first move), −0.23% (3%) and −0.44% (4%) a trade. The 2026 cells that made money rest on 12 and 5 trades.
  - Flipping into SOXL after a failed down move made +0.07% after a 2% move and lost −0.10% and −0.09% after 3% and 4%.
- **Status:** exploratory. S16 (11:00, ≥ 3%, stop at the open) remains the forward-tracked version of this idea.

**Luck check** (`scripts/research/luck_check.py`, `luck_check.csv`, `luck_check_by_era.csv`; 2,000 runs per null, no-stop cells). It asks two different questions:
1. **Does the morning move's direction carry information?** Each day's side is flipped at random, with real costs and skips, and the same flip at every check time.
2. **Does the result beat zero after costs?** White's reality check: every cell is recentred to a zero mean, days are resampled within each era, and the whole 35-cell search is redone.

| Statistic | Observed | (1) Random side: typical / 95th pct / share as good | (2) Zero net edge: typical / 95th pct / share as good |
|---|---|---|---|
| Average net over the 35 cells | +6.8 bps | −14.5 / −2.4 / **0.2%** | 0 / +11.8 / 20% |
| Cells positive in all three eras | 7 | 1 / 4 / **0.4%** | 4 / 10 / 20% |
| Best cell's t (11:30, 2–3%) | 2.21 | 1.07 / 2.19 / **4.4%** | 1.98 / 3.05 / 33% |

| Era | Average net, going with the move | Average net, random side (mostly costs) | What the direction is worth |
|---|---|---|---|
| 2011–2018 | +8.8 bps | −20.4 | **+29** |
| 2019–2025 | +6.3 | −12.8 | **+19** |
| 2026 | +25.9 | +5.3 | **+21** |

- **The continuation is real and steady.** Going with the morning move is worth about 0.2–0.3% a trade over a random side in every era, and a random side almost never matches it (p ≈ 0.002).
- **The profit after costs is not established.** Before 2026, costs took most of the continuation. The net that is left (+0.07% a trade over 2011–2026) would appear by luck about one time in five. The best single cell is what a 35-cell search finds by luck about one time in three.
- **Costs are now much smaller.** In 2026 a random side about broke even, so most of the continuation was left over. If the continuation stays at its 15-year level, current costs leave roughly +0.15–0.25% a trade. That is a forecast, not a result.

**By side** (`luck_check_by_side.csv`, `luck_check_side_size_time.csv`; no stop, hold to 15:55, after costs). The signal is always SOXL's move from its 09:30 open.

| Average over the 35 cells | 2011–2018 | 2019–2025 | 2026 | Random-side test |
|---|---|---|---|---|
| Up move → buy SOXL | +0.17% | +0.06% | +0.44% | p ≈ 0.005 |
| Down move → buy SOXS | +0.01% | +0.08% | −0.24% | p ≈ 0.07 |
| Fade an up move (buy SOXS) | −0.61% | −0.45% | −0.57% | |
| Fade a down move (buy SOXL) | −0.39% | −0.24% | +0.14% | |

| Per signal, checks 10:00–11:00 (win rate) | 2011–2018 | 2019–2025 | 2026 |
|---|---|---|---|
| Up ≥ 3% → buy SOXL | +0.12% (58%) | +0.18% (54%) | +0.60% (60%) |
| Up 1–3% → buy SOXL | −0.01% (53%) | +0.11% (57%) | +0.64% (51%) |
| Down ≥ 3% → buy SOXS | +0.11% (49%) | +0.27% (57%) | +0.34% (58%) |
| Down 1–3% → buy SOXS | −0.10% (45%) | −0.12% (46%) | −1.19% (41%) |

- **The established part is the SOXL side.** SOXS on its own is not established, because small down moves (1–3%) tend to bounce.
- **Down moves of 3% or more by 10:00–11:00 did continue:** SOXS was positive in all three eras.
- **Fading loses.** Buying SOXS into an up move lost about 0.5% a trade in every era. Buying SOXL into a down move lost before 2026.
- **Small samples:** the 2026 down side is small (224 signals over all cells). A day counts once for each check time it qualifies at.

## Knowing earlier: pre-open flags for trend days (exploratory)

Script: `scripts/research/trend_day_predictors.py`. Outputs: `trend_day_predictors/`.
- Every condition is built from trailing data only. The 2026 run loads history from October 2024, so the 1-year volatility comparison is defined for every 2026 session. An earlier version loaded too little history, which left that flag off until about March 2026.
- The flags come from the 2019–2025 conditions analysis above. The thresholds are round numbers fixed for this run. 2011–2018 and 2026 played no part in choosing the flags.

**The four pre-open flags**, each known by 09:30:
1. SOXL's median daily range over the last 20 sessions is at least 1.2× its median over the last 250.
2. Yesterday was a trend day.
3. QQQ's prior close is below its 50-day average.
4. SOXL's gap is at least half its typical (20-day median) daily range.

**Share of days that ended as trend days**, 2011–2018 / 2019–2025 / 2026:

| Pre-open flags | Trend-day rate | Share of days |
|---|---|---|
| All days | 10% / 20% / 31% | — |
| 0 flags | 4% / 12% / 6% | 47% / 37% / 9% |
| 1 | 10% / 17% / 26% | 31% / 34% / 27% |
| 2 | 16% / 30% / 31% | 16% / 17% / 36% |
| 3 or 4 | **35% / 43% / 44%** | 6% / 12% / 27% |

- **Each flag on its own raises the odds in all three eras.** The strongest are a hot volatility regime (19% / 36% / 37% against 5% / 13% / 13% in a calm one) and QQQ below its 50-day average (21% / 36% / 33% against 5% / 14% / 29%).
- **By 09:45:** a first-15-minute range at least 1.25× its 20-day average gives 16% / 31% / 46% trend days, against 6% / 15% / 19% when it is narrow.
- **Busy pre-market and event days help less.** These are measurable from 2019 only: busy pre-market 28% / 36%, event days 23% / 36%.

**The 10:30 rule (SOXL 3–4% from its open at 10:30, stop at the open) by pre-open flags** (`rule_1030_by_flags.csv`):

| Pre-open flags | 2011–2018 | 2019–2025 | 2026 | Pooled |
|---|---|---|---|---|
| 2 or more | +0.72% (40 trades) | +0.55% (69) | +1.37% (10) | **+0.67%** (119) |
| 0–1 | +0.10% (88) | +0.26% (133) | +0.07% (6) | +0.19% (227) |

- The rule did better on days with two or more pre-open flags in every era. The 09:45 score, which adds the first-15-minute range, separates less well: +0.26% against +0.32% in 2011–2018.
- **Status:** a slice of a post-hoc rule, about 8 trades a year, and 2026 rests on 16 trades. Not forward-tested.

## Stop placement for the 10:30 rule (exploratory)

Script: `scripts/research/rule_1030_stops.py`. Outputs: `rule_1030_stops/`.
- The rule: SOXL 3–4% from its open at 10:30, go with it, exit 15:55. Each stop variant is tested on the same 346 trades over 2011–2026, case B.

| Stop | Average stop distance | Average per trade | Win rate | Worst | Max drawdown | Per unit of risk (R) | R by era |
|---|---|---|---|---|---|---|---|
| None | — | +0.44% | 54% | −15.3% | −57% | — | — |
| SOXL's open (as found) | 3.5% | +0.36% | 52% | −4.3% | −31% | 0.10 | 0.07 / 0.11 / 0.22 |
| Fixed 3% | 3.0% | +0.36% | 51% | −3.5% | −27% | 0.12 | 0.11 / 0.14 / 0.03 |
| Fixed 2.5% | 2.5% | +0.35% | 49% | −3.0% | −23% | 0.14 | 0.11 / 0.17 / −0.08 |
| Fixed 2% | 2.0% | +0.26% | 44% | −2.6% | −22% | 0.13 | 0.12 / 0.15 / 0.01 |
| Half the morning move retraced | 1.7% | +0.25% | 42% | −2.5% | −17% | 0.14 | 0.13 / 0.16 / 0.08 |
| Fixed 1.5% | 1.5% | +0.26% | 39% | −2.2% | −18% | **0.18** | 0.15 / 0.20 / 0.14 |
| Fixed 1% | 1.0% | +0.13% | 30% | −1.7% | −30% | 0.13 | 0.11 / 0.17 / −0.33 |

- **Same position size every trade:** the wide stops (the open, or 2.5–3%) earn the most per trade. Tighter stops get shaken out by ordinary SOXL noise: 55% of trades are stopped at 1.5%, and 68% at 1%.
- **Same dollar risk every trade:** a 1.5% stop earns the most per unit of risk (0.18 R, positive in every era), but needs a position about 2.3× larger.
- **Stop slippage:** an extra 1 cent per stop fill (case S) costs only 0.01–0.02% a trade.
- **Status:** seven variants tried on the same data; exploratory.

**Combined with the pre-open flags** (two or more of the four flags in "Knowing earlier"):

| Days, stop | Trades | Win rate | Average per trade | Per unit of risk (R) | Worst | Max drawdown | R by era |
|---|---|---|---|---|---|---|---|
| All days, open stop (as found) | 346 | 52% | +0.36% | 0.10 | −4.3% | −31% | 0.07 / 0.11 / 0.22 |
| All days, fixed 1.5% | 346 | 39% | +0.26% | 0.18 | −2.2% | −18% | 0.15 / 0.20 / 0.14 |
| 2+ flags, open stop | 119 | 54% | +0.67% | 0.18 | −4.3% | −23% | 0.18 / 0.16 / 0.37 |
| 2+ flags, fixed 1.5% | 119 | 34% | +0.40% | **0.27** | −2.2% | −17% | 0.31 / 0.27 / 0.05 |

- **The combination earns the most per unit of risk, but it trades only about 8 times a year.** Taking every setup with the 1.5% stop earns more in total, because days with 0–1 flags still made 0.13 R.
- **In 2026 the 1.5% stop was too tight for flagged days:** 0.05 R against 0.37 R with the open stop, over 10 trades. SOXL's daily ranges in 2026 were the widest in the sample.

**Sizing plans with the 1.5% stop** (`sizing_plans_1p5_stop.csv`; 1 R = the dollar risk of one unit):

| Plan | Trades | R a year | Max drawdown | Worst year | Losing years | Total ÷ max drawdown | R per unit by era |
|---|---|---|---|---|---|---|---|
| Every setup, 1 unit | 346 | +4.0 | −12.2 R | −3.6 R | 4 of 16 | **5.0** | 0.15 / 0.20 / 0.14 |
| 2+ flag days only | 119 | +2.1 | −11.7 R | −7.5 R | 3 of 14 | 2.7 | 0.31 / 0.27 / 0.05 |
| Every setup, 1.5 units on 2+ flag days | 346 | +5.0 | −16.8 R | −5.9 R | 4 of 16 | 4.6 | 0.17 / 0.21 / 0.12 |
| Every setup, 2 units on 2+ flag days | 346 | +6.1 | −21.4 R | −9.6 R | 4 of 16 | 4.3 | 0.19 / 0.22 / 0.11 |

- Taking every setup at the same risk has the best ratio of profit to drawdown and the most even results across eras.
- Sizing up on flagged days adds profit, but adds drawdown faster. Risking more on every trade would do the same job with a better ratio.

## Catching the trend earlier (exploratory)

Script: `scripts/research/early_trend.py`. Outputs: `early_trend/`.

**How early the direction shows, on days that end as trend days** (hindsight; `direction_on_trend_days.csv`). Share of trend days on which the direction was already right, 2011–2018 / 2019–2025 / 2026:

| Seen at | Direction right | Already 2%+ that way on SOXL |
|---|---|---|
| Opening gap | 52% / 54% / 47% | — |
| 09:35 | 75% / 67% / 72% | 21% / 17% / 30% |
| 09:45 | 81% / 77% / 75% | 38% / 37% / 53% |
| 10:00 | 85% / 82% / 88% | 49% / 55% / 70% |
| 10:30 | 91% / 86% / 95% | 68% / 70% / 84% |

- **The gap's direction says nothing about the trend's direction.**
- **The move from the open does:** it is right on about four in five eventual trend days by 09:45. Early moves on days that stay quiet are the false starts.

**Earlier entries with the 1.5% stop** (`entries.csv`; 24 cells, all reported). Before 10:30, going with the move paid only when it agreed with the opening gap. Moves against the gap lost at 09:45 and 10:00 in most eras.

| Entry | With the gap: R by era | Against the gap: R by era |
|---|---|---|
| 09:45, 2–3% | 0.04 / 0.42 / 0.51 | −0.39 / 0.37 / −0.07 |
| 10:00, 3–4% | 0.27 / 0.28 / 0.38 | −0.20 / 0.18 / −0.38 |

**Cascade** (`cascade.csv`; designed after seeing the grid above). Take the first that applies, one trade a day, 1.5% stop, exit 15:55:
1. 09:45, SOXL 2–3% from its open in the gap's direction.
2. 10:00, 3–4% in the gap's direction.
3. 10:30, 3–4% either way.

| Plan | Trades a year | Win rate | R a trade | R a year | Max drawdown | R by era |
|---|---|---|---|---|---|---|
| 10:30 rule alone | 23 | 39% | 0.18 | +4.0 | −12.2 R | 0.15 / 0.20 / 0.14 |
| Cascade | 39 | 38% | 0.21 | +8.1 | −25.2 R | 0.07 / 0.30 / 0.39 |

- **What the cascade changes:** it roughly doubles both the yearly profit and the drawdown.
- **Where it comes from:** the early entries carry it after 2019, but they were weak in 2011–2018 (0.04 R at 09:45).
- **Status:** post-hoc, not forward-tested.

## Study T1: early trend-day detector (registered; FAIL)

Registry: REGISTRY.md, "Study T1". Scripts: `scripts/research/download_detector_data.py`, `scripts/research/trend_detector.py`, `scripts/research/trend_detector_stops.py`. Outputs: `trend_detector/`.
- **Inputs:** five pre-open flags and eleven inputs at 09:45 and 10:00:
  - scaled move, gap agreement, path cleanliness, VWAP side;
  - order flow, as tick-level buyer/seller imbalance from every SOXL trade and as a bar-based version;
  - breadth across 23 semis, and the four leaders;
  - VIXY, semis vs QQQ, and break-and-hold of yesterday's high or low.
- **Protocol:** fitted on 2019–2025, judged on 2011–2018 and 2026.
- **Trade:** next-minute entry, fixed 1.5% stop, exit 15:55.

**Verdict: FAIL.** The rules picked by the search and by the logistic model did not beat the simple move-plus-gap baseline in both test periods. Mean R per trade, with the registered 1.5% stop:

| Check | Rule | 2011–2018 | 2019–2025 (fit) | 2026 | Trades a year |
|---|---|---|---|---|---|
| 09:45 | All signals (move ≥ 1%) | −0.07 | +0.12 | +0.13 | 124 / 115 / 140 |
| 09:45 | Move + gap baseline | +0.12 | +0.36 | −0.21 | 20 / 19 / 25 |
| 09:45 | Best search rule (gap + leaders + semis vs QQQ) | +0.14 | +0.79 | −0.65 | 9 / 10 / 16 |
| 09:45 | Logistic, top third | −0.11 | +0.07 | +0.26 | 30 / 40 / 78 |
| 10:00 | All signals | −0.00 | +0.13 | −0.17 | 137 / 127 / 157 |
| 10:00 | Move + gap baseline | +0.03 | +0.24 | −0.51 | 23 / 21 / 15 |
| 10:00 | Best search rule (5 inputs, stage 1 ≥ 2) | +0.24 | +0.73 | −0.60 | 9 / 11 / 30 |
| 10:00 | Logistic, top third | +0.05 | +0.14 | −0.07 | 38 / 45 / 89 |
| 10:00 | Cascade rule (3–4% with the gap), for reference | +0.27 | +0.28 | +0.38 | 8 / 10 / 12 |

**The detector does find trend days.**
- **Logistic accuracy:** AUC on unseen periods is 0.74 / 0.65 at 09:45 and 0.74 / 0.70 at 10:00 (0.5 is a coin flip). Its top third holds 25% / 40% trend days at 10:00, against 12% / 33% for all signals.
- **Inputs that separate trend days in every era** (10:00 signals; trend-day share in the input's top vs bottom training tercile, 2011–2018 / 2019–2025 / 2026):

  | Input | Top tercile | Bottom tercile |
  |---|---|---|
  | Breadth | 25 / 30 / 50% | 8 / 17 / 26% |
  | Semis vs QQQ | 24 / 32 / 42% | 8 / 15 / 27% |
  | Pre-open score 3+ vs 0–1 | 27 / 36 / 40% | 9 / 17 / 23% |
  | Scaled move | 18 / 30 / 56% | 10 / 18 / 20% |
  | VIXY moving against SOXL's move | 19 / 28 / 45% | 10 / 19 / 25% |

- **Inputs that added little:**
  - Tick-level order flow: 12 / 23 / 42% against 10 / 22 / 22%. It helped only in 2026.
  - Break and hold of yesterday's high or low: 14 / 23 / 30% against 11 / 12 / 22% for a failed break.
  - Gap agreement on its own.
- **No input separated the trade results with the 1.5% stop.** Trend days are high-volatility days, and a fixed 1.5% stop gets hit before the trend plays out. The 10:00 search rule held 48% trend days in 2026 and still lost 0.60 R a trade.

**Exploratory follow-up (post-hoc; four stops tried after the failure)** (`stops_exploratory.csv`). Logistic top third against all 10:00 signals, net % per trade, 2011–2018 / 2019–2025 / 2026:

| Stop | Top third | All signals |
|---|---|---|
| Fixed 1.5% | +0.08 / +0.21 / −0.11 | −0.00 / +0.20 / −0.26 |
| SOXL's open | **+0.12 / +0.43 / +0.69** | −0.02 / +0.29 / +0.09 |
| Half the typical daily range | +0.14 / +0.49 / +0.26 | +0.04 / +0.25 / −0.20 |
| None | +0.09 / +0.43 / +0.67 | +0.03 / +0.18 / +0.08 |

- **With room to move, the detector's picks were positive in every era and beat all signals.**
- **Per dollar risked they are weak:** the open stop averages 3.1–4.1% away, giving +0.07 / +0.15 / +0.08 R. That is below the 10:30 rule with a 1.5% stop (0.15 / 0.20 / 0.14 R).
- **The evidence is thin:** t is 0.6 / 1.8 / 1.5, and the worst trade was −16.6%.
- **At 09:45,** only the open stop kept the top third positive in every era (+0.04 / +0.24 / +0.55).

**Conclusion:** extra data identifies trend days better than price alone. Breadth, semis vs QQQ, VIXY and the pre-open flags carry the most information. But in these tests it did not produce more profit per unit of risk than the simple 10:30 rule. The most practical use is as confirmation in a live scanner: favor days with broad participation and semis leading QQQ.

## Study T3: every technical input at 10:30 (registered; FAIL)

Registry: REGISTRY.md, "Study T3" (includes Study T2). Scripts: `scripts/research/trend_t3.py`, plus the exploratory follow-up `scripts/research/trend_t3_followup.py`. Outputs: `trend_t3/`.
- **Signals:** 1,539 mornings with SOXL ≥ 2% from its open at 10:29 (628 / 810 / 101 in 2011–2018 / 2019–2025 / 2026). Trend days among them: 20% / 31% / 48%.
- **Inputs:** 128, all known by 10:29:
  - **Daily technicals through the prior close:** RSI 2/5/14, SMAs 5–200, MACD, Bollinger, stochastic, ADX, ATR, Donchian, 52-week position, streaks, NR4/NR7.
  - **Prior levels:** yesterday's high, low and close; floor pivots; the prior week's high and low; the gap and pre-market.
  - **Intraday technicals:** opening ranges; 1- and 5-minute RSI, EMA and MACD; Bollinger; VWAP; path shape; volume; tick-level order flow.
  - **Context:** 14 other markets, breadth across 23 chip stocks, market regime, the calendar.
- **Searches:**
  - 6,906 two- and three-input rules, ranked once by trend share and once by the move left after 10:30.
  - L1 logistic and LightGBM models for a trend day, and again for "another 2%+ after 10:30".
  - The Study T2 model and score.
- **Protocol:** fitted on 2019–2025 only; judged on 2011–2018 and 2026.

**Verdict: FAIL.** The test needed both of these, in both test periods:
- a trend share at least 1.5× base (30% in 2011–2018, 71% in 2026);
- a bigger move after 10:30 than the rest.

The main attempts below. "Move after 10:30" is SOXL's mean move from 10:30 to 15:55, in %, with no stop. The full table, with mean R, is in REGISTRY.md and `models.csv`.

| Selection | Trend share, 2011–2018 / 2026 | Move after 10:30, picks vs rest, 2011–2018 | Same, 2026 |
|---|---|---|---|
| All ≥ 2% mornings | 20% / 48% | +0.14 | +0.43 |
| Best of 6,906 rules by trend share | 71% / 63% | −0.17 vs +0.15 | −0.74 vs +1.05 |
| Best of 6,906 rules by move after 10:30 | 62% / 60% | −0.09 vs +0.14 | −0.34 vs +0.62 |
| L1 logistic, top third | 46% / 60% | +0.23 vs +0.12 | +0.48 vs +0.35 |
| LightGBM, top third | 58% / 62% | +0.86 vs +0.02 | +0.50 vs +0.33 |
| L1 logistic aimed at "another 2%+", top third | 32% / 51% | +0.46 vs +0.01 | +0.81 vs −0.15 |

**What tells a trend day at 10:30: the size and breadth of the move in the chip stocks themselves.**
- **The models rank trend days well on unseen years:** AUC 0.77 / 0.70 for L1 and 0.75 / 0.71 for LightGBM (0.5 is a coin flip).
- **The signal is broad:** 86 of 128 inputs point the same way in all three periods, against about 32 expected by chance. 68 pass q ≤ 0.10 in training.
- **Strongest single inputs** (AUC, 2011–2018 / 2019–2025 / 2026):

  | Input at 10:29 | AUC |
  |---|---|
  | SOXX's own move from its open | 0.76 / 0.73 / 0.68 |
  | Average move of the 23 chip stocks | 0.75 / 0.72 / 0.68 |
  | Share of the 23 moving > 1% the same way | 0.73 / 0.71 / 0.70 |
  | SMH's move | 0.71 / 0.73 / 0.72 |
  | SOXL's recent volatility (prior ATR %) | 0.69 / 0.65 / 0.64 |
  | SOXX minus SPY | 0.68 / 0.65 / 0.68 |
  | 5-minute EMA 9 vs 21 | 0.67 / 0.68 / 0.57 |
  | XLK's move | 0.65 / 0.66 / 0.61 |

- **A two-input read (exploratory):**
  - Both strong (each in its top training third): SOXX ≥ 1.33% from its open in SOXL's direction, and ≥ 65% of the 23 chip stocks more than 1% from their opens that way. Trend days: 52% / 54% / 69%.
  - Either weak (in its bottom third): SOXX < 0.96% that way, or < 43% of the chips. Trend days: 10% / 16% / 37%.

**The classic chart inputs carry almost no information.** AUC per period (2011–2018 / 2019–2025 / 2026). Below 0.5 means the input points the other way.

| Input | Trend day | Another 2%+ after 10:30 |
|---|---|---|
| Daily RSI 2 | 0.51 / 0.45 / 0.46 | 0.49 / 0.47 / 0.48 |
| Daily RSI 14 | 0.48 / 0.48 / 0.49 | 0.45 / 0.48 / 0.53 |
| Distance from yesterday's close (in ATR) | 0.55 / 0.57 / 0.51 | 0.49 / 0.53 / 0.47 |
| Distance beyond yesterday's high or low | 0.53 / 0.52 / 0.50 | 0.47 / 0.50 / 0.47 |
| Break and hold of yesterday's high or low | 0.51 / 0.50 / 0.52 | 0.47 / 0.49 / 0.50 |
| Position vs the floor pivot | 0.55 / 0.54 / 0.51 | 0.48 / 0.51 / 0.48 |
| Beyond the prior week's high or low | 0.52 / 0.51 / 0.46 | 0.47 / 0.52 / 0.47 |
| Price vs 20-day / 200-day SMA | 0.48 / 0.46 / 0.51 and 0.43 / 0.47 / 0.49 | 0.46 / 0.48 / 0.51 and 0.42 / 0.47 / 0.60 |
| Daily MACD | 0.47 / 0.49 / 0.53 | 0.47 / 0.48 / 0.55 |
| 5-minute RSI 9 | 0.55 / 0.61 / 0.58 | 0.47 / 0.52 / 0.50 |
| Tick-level order flow to 10:00 | 0.50 / 0.50 / 0.62 | 0.49 / 0.52 / 0.54 |

- The intraday RSI and EMA readings separate trend days only because they restate the size of the move.
- Best input of each of the 18 families: `followup_families.csv`.

**Whether the move continues after 10:30 is barely predictable.**
- **Models aimed at "another 2%+ after 10:30"** score AUC 0.62 / 0.54 (L1) and 0.55 / 0.49 (LightGBM) on unseen years.
- **Few inputs hold up:** only 40 of 128 point the same way in all three periods, against about 32 by chance. 16 pass q ≤ 0.10 in training.
- **The ones that hold up are about volatility and regime** (AUC, 2011–2018 / 2019–2025 / 2026):
  - SOXL's recent ATR %: 0.62 / 0.59 / 0.60.
  - The "volatility hot" pre-open flag: 0.58 / 0.57 / 0.58.
  - The biggest 1-minute bar with the move: 0.59 / 0.57 / 0.56.
  - The pre-open flag count: 0.60 / 0.56 / 0.55.
  - QQQ below its 50-day average: 0.58 / 0.57 / 0.53.
- **The size of the move flipped in 2026:** bigger moves at 10:30 had less left. SOXX's move scored 0.60 / 0.56 / 0.40.
- **The best model's picks** (L1 aimed at "another 2%+", top third) went +0.46 / +0.81% after 10:30, against +0.01 / −0.15% for the rest.
  - That is t = 1.3 / 0.9, not significant.
  - With the 1.5% stop: +0.13 / +0.04 R.

**Why spotting a trend day does not pay after 10:30.**
- Take the mornings where both SOXX's move and breadth are in their top third; 52–69% of them become trend days.
  - SOXL's further move from 10:30 to 15:55 averaged +0.23 / +0.31 / +0.28% (median +0.86 / +0.87 / +0.63%).
  - All ≥ 2% mornings averaged +0.14 / +0.37 / +0.43%.
  - With the 1.5% stop: +0.06 / −0.08 / −0.51 R.
- The days that look most like trend days at 10:30 already have the most move done. The ones that fail reverse hard, which is why the mean is well below the median.

**Conclusion**
- **Trend-day odds can be ranked at 10:30.** Use SOXX's own move and how many of the big chip stocks are moving more than 1% with it.
- **The classic chart inputs add nothing to that.** RSI, yesterday's high/low/close, pivots and moving averages carry no useful information here.
- **No input or combination of the 128 reliably predicted SOXL's move after 10:30,** which is the part a trade captures. No filter tested here improved the 10:30 rule (move size alone) in both test periods.

## What is being tracked forward

`scripts/research/paper_log.py` runs after each close and appends to `paper_log.csv`. The tracked rules are:

| Rule | What it is |
|---|---|
| S3-01 | 15-minute opening-range breakout. Bearish legs use SOXS when it is ≥ $10. |
| S8-01 | The same breakout, with bearish legs as short SOXL. |
| S4-02 | Noise-boundary momentum, k = 1.0, trailing exits checked at half-hour marks. |
| S4-04 | Noise-boundary momentum, k = 1.5, trailing exits checked at half-hour marks. |
| S1-06 | Late-day fade on days SOXX moved ≥ 1%, exit at the official close. Regime watch only. |
| S13-A / S13-B | The final breakout rules, with and without the 11:00 time stop (ORB_STRATEGY.md). |
| S16 | Midday trend check: at 11:00, SOXL ≥ 3% from its open, go with it, stop at the open, exit 15:55. |

The log also prints the S15 kill-switch state: ON while the last 60 S3-01 signals average > 0.

**Judging rules**
- Each rule is judged after 60 trades.
- Its forward mean must be > 0 and inside the validation 95% confidence interval.
- A rule is paused if its last 60 trades average < 0 with t < −1.

**Monitors**
- `scripts/research/monitor.py` writes [MONITOR.md](MONITOR.md) and `monitors.csv`.
- It tracks the late-day slope, the opening-burst edge, SOXS's price and tick, SOXL's range, and SOXL's one-cent-spread share.

## Caveats

- **Bar data:** the backtests use 1-minute bars. Bars carry fill risk inside the minute, and SOXS exits are mirrored from SOXL's chart (median mapping error about 5 bps).
- **Validation fills:** case-Q real-quote fills were run for every Study 2 variant and closely match case B.
- **Pre-sample costs:** these come from a 2019–21 NBBO sample (8 days per year). SOXL's pre-split spreads were 13–27¢, and trades before its 2021-03-02 split use 2020 spreads.
- **Study 5's event gate:** it detects earnings from after-hours volume spikes. That catches every one of the 13 known earnings dates checked, but also other after-hours news. CPI days are proxied by the 08:30 QQQ volume burst.
- **Exploratory status:** Studies 5 and 8 ran as exploratory diagnostics on the near-misses because no rule survived. They cannot promote a rule.

## Files

- `verdicts_all.csv`: every variant with its criteria, p-value, BH q and failure reasons.
- `study*/`: per study, `summary.csv`, `verdicts.csv`, `robustness.csv` and `crosscheck.csv`, plus extras:
  - Study 4: `spy_check.csv`
  - Study 5: `gate_decisions.csv`, `nr7_check.csv`
  - Study 7: `stage1.csv`
  - Studies 10–12: summaries also carry case S (stop-slippage stress).
- `scalps_breakdown/`: Studies 10–12 by side, entry time, year, cost case and exit reason, plus `setup_geometry.csv`.
- `scalps_winners/`: exploratory winner-vs-loser analysis for Studies 10–12: per-feature tests, gap alignment and out-of-sample models.
- `trend_days/`: exploratory trend/medium-day analysis: rules by day type, breakout entry timing, pre-open and 09:45 conditions, and the out-of-sample trend-day detector.
- `orb_conditions/`: exploratory take/skip conditions for the 15-minute breakout, and SOXS vs short SOXL on the same bearish signals.
- `orb_strategy/`: stop/target/management design grid for the breakout, and the final S13 rules.
- `orb_best/`: 480-combination search on 2019–2025, the one-time 2011–2018 test, and the deep-history diagnostics.
- `holdout_2026/`: the one-time 2026 holdout test of S15 and the context rules (summary, S15 by month, trades, verdict).
- `midday_trend/`: the midday trend-check grid (24 cells × three eras).
- `trend_detector/`: Study T1 (detector inputs, univariate tables, subset search top 10, logistic model, summary, exploratory stops).
- `trend_t3/`: Study T3 (128-input univariate screen, pair/triple search top 20 by trend share and by the move after 10:30, L1 logistic and LightGBM for both targets, models vs rest, AUCs) and the exploratory follow-up (`followup_*.csv`: continuation screen, best input per family, model top third vs rest, SOXX move × breadth).
- `early_trend/`: how early the direction shows on trend days, earlier entries with and against the gap, and the early-entry cascade.
- `rule_1030_stops/`: stop placement for the 10:30 rule (per trade and per unit of risk, by era).
- `trend_day_predictors/`: trend-day odds by pre-open and 09:45 conditions and hot-flag counts, and the 10:30 rule split by flags.
- `intraday_trend_odds/`: live odds by check time and move so far (`odds.csv` per era, `pooled.csv`), how much of trend days' move is done at each check, the flip-at-the-open test, and the luck check (`luck_check*.csv`).
- `output/`: the supplementary spread table and the event calendar.
- Trade-level files: `data/research/trades/` (gitignored, reproducible).
- Re-run a study: `cd scripts/research && python run_studyN.py`, then `python evaluate_all.py`.
  - For Studies 10–12, also run `python scalp_breakdown.py`.
