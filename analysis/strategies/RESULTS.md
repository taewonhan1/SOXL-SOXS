# Strategy research results: pre-registered studies 1–9

Run 2026-09-28. The rules were fixed in [REGISTRY.md](REGISTRY.md) before any study ran, as shown by the git history.
[RESEARCH_PLAN.md](../../RESEARCH_PLAN.md) describes the plan. Every number below comes from the per-study CSVs in this folder.

## Bottom line

**No rule passed the pre-registered bar.**
- 70 variants were tested across Studies 1–6 and 8, plus 60 pattern screens in Study 7.
- None meets criteria 1–5.
- None survives the Benjamini–Hochberg correction: the smallest q is 0.43, against a required 0.10.
- The **2026 holdout (Jan–Sep 2026) has not been opened for any rule.** It is still available as a one-time test.

The main failure is statistical significance in the 15-month validation window. Two rule families were consistently positive after costs in both development and validation, and passed every robustness and cross-ticker check except significance:
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

## Why nothing passed

Validation per-trade standard deviations were:
- about 440–460 bps for the breakout rules (S3-01, S8-01)
- about 300 bps for S4-04

With the validation trade counts (125–308), t ≥ 2 needs a mean of about +52–56 bps per trade. The best rules made +43 to +49.

At the same edge and trade rate, about 4–5 more months of trades would clear t ≥ 2. Forward paper trading supplies exactly that.

Multiple testing works against every individual result too. The smallest one-sided p (0.030) becomes q = 0.43 after correcting for 70 variants.

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
- `output/`: the supplementary spread table and the event calendar.
- Trade-level files: `data/research/trades/` (gitignored, reproducible).
- Re-run a study: `cd scripts/research && python run_studyN.py`, then `python evaluate_all.py`.
