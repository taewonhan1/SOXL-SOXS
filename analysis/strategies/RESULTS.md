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

## What is being tracked forward

`scripts/research/paper_log.py` runs after each close and appends to `paper_log.csv`. The tracked rules are:

| Rule | What it is |
|---|---|
| S3-01 | 15-minute opening-range breakout. Bearish legs use SOXS when it is ≥ $10. |
| S8-01 | The same breakout, with bearish legs as short SOXL. |
| S4-02 | Noise-boundary momentum, k = 1.0, trailing exits checked at half-hour marks. |
| S4-04 | Noise-boundary momentum, k = 1.5, trailing exits checked at half-hour marks. |
| S1-06 | Late-day fade on days SOXX moved ≥ 1%, exit at the official close. Regime watch only. |

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
- `output/`: the supplementary spread table and the event calendar.
- Trade-level files: `data/research/trades/` (gitignored, reproducible).
- Re-run a study: `cd scripts/research && python run_studyN.py`, then `python evaluate_all.py`.
  - For Studies 10–12, also run `python scalp_breakdown.py`.
