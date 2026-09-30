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
- **The underlying effect is established; a profit after costs is not.** Going with SOXL's morning move beats picking a side at random by 0.2–0.3% a trade in each of 2011–2018, 2019–2025 and 2026 (random-direction test, p ≈ 0.002). Costs took most of that before 2026. What is left after costs (+0.07% a trade on average over 2011–2026) is not distinguishable from zero (reality check, p ≈ 0.2). See "Luck check" under "Live trend odds".

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
- `intraday_trend_odds/`: live odds by check time and move so far (`odds.csv` per era, `pooled.csv`), how much of trend days' move is done at each check, the flip-at-the-open test, and the luck check (`luck_check*.csv`).
- `output/`: the supplementary spread table and the event calendar.
- Trade-level files: `data/research/trades/` (gitignored, reproducible).
- Re-run a study: `cd scripts/research && python run_studyN.py`, then `python evaluate_all.py`.
  - For Studies 10–12, also run `python scalp_breakdown.py`.
