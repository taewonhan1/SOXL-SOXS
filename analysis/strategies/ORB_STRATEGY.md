# SOXL/SOXS 15-minute breakout: playbook (Strategy S13)

**Status: not proven yet.**
- The rules were designed on 2019 → Sep 2024 and checked on Oct 2024 → Dec 2025.
- The one-time test on the sealed Jan–Sep 2026 data and forward paper trading are still to come.
- The locked definition is in [REGISTRY.md](REGISTRY.md) (Strategy S13).
- The evidence is in [RESULTS.md](RESULTS.md) and `orb_strategy/`.

All levels are read off SOXL's 1-minute chart, including for SOXS trades.

## Rules (S13-A)

**Before the open**
1. Note SOXL's prior close and SOXS's prior close.
   - Bearish trades need SOXS ≥ $10. If SOXS is below $10, skip bearish breaks.

**09:30–09:45**
2. Mark **H** and **L**, the high and low of SOXL's first 15 one-minute bars (09:30:00–09:44:59).
3. Note the **gap**: SOXL's 09:30 open ÷ prior close − 1.

**From 09:45**
4. Wait for the **first 1-minute close** above H (up-break) or below L (down-break).
   - A wick through the level does not count.
   - Only the first break of the day counts: one trade a day.
5. **Skip** the break if it goes against a gap of more than 1%, meaning the stock gapped up more than 1% and breaks down, or gapped down more than 1% and breaks up.
6. **Enter** at the next minute's open.
   - Up-break: buy SOXL.
   - Down-break: buy SOXS.

**Managing the trade**
7. **Stop.** The typical distance is 2–3.5% of SOXL's price.
   - SOXL long: exit if SOXL trades at L.
   - SOXS long: exit if SOXL trades at H.
8. **At 11:00:** if the trade is not in profit, exit right away. This does not apply to trades entered after 11:00.
9. **Otherwise hold** and exit at 15:55 (12:55 on half-days).
   - No profit target.
   - Do not move the stop.

**S13-B** is the same without step 8. It has a higher win rate, larger losers and a deeper drawdown.

## Position size

- Risk a fixed dollar amount per trade: shares = dollar risk ÷ (entry − stop).
  - Example: risk $400 with a SOXL entry of $30.00 and L at $29.20. That is $0.80 of risk per share, so 500 shares ($15,000).
  - For SOXS, use the same percentage distance on SOXS's price.
- Stops can gap. The worst single loss of the unfiltered rule was −18.6%, on March 17, 2020.

## What to expect

2019–2025, after spread, $0.0035/share and fees. Bearish trades use SOXS.

|  | S13-A (with the 11:00 time stop) | S13-B (without it) |
|---|---|---|
| Trades a year | about 128 (2–3 a week) | about 128 |
| Win rate | 40% | 48% |
| Average win / average loss | +3.4% / −1.6% | +3.2% / −2.2% |
| Average per trade | +0.38% | +0.38% |
| 2019–21 / 2022–24 / Oct 2024–Dec 2025 | +0.25% / +0.40% / +0.60% | +0.29% / +0.40% / +0.51% |
| Worst drawdown (sum of trades, % of one position) | −48% | −62% |
| Longest losing streak | 13 trades | 8 trades |
| Losing years | 2020 (−0.06% a trade) | 2020 (−0.06% a trade) |

**Where the profit comes from.** Trend days, when the semis index moves 2% or more open-to-close, make about 1 day in 5. On those days the first break points the right way 85% of the time and the trade averages about +3.6%. Quiet days lose, which is why most trades are small losers.

## Tested and rejected (don't add these)

- **Profit targets at 2R or 3R** cut the trend-day winners. With a 2R target, the Oct 2024–Dec 2025 result fell from +0.39% to +0.12% per trade (short-SOXL execution).
- **Moving the stop to break-even after +1R** cost about 0.04–0.05% per trade in the design years and lowered the win rate to 42–43%.
- **A tighter stop at the middle of the range** dropped the win rate to 32% and cut profit by more than half.
- **A breakout-minute volume filter** halved the number of trades without improving the design-period result.

## Optional (unproven)

- A larger size when QQQ's prior close is below its 50-day average. S13-A made +0.72% per trade in that regime and +0.24% otherwise.

## Tracking

- After each close, run `python scripts/research/paper_log.py`. It logs S13-A and S13-B forward from 2026-09-28, next to the earlier near-miss rules.
- Judge the rule after 60 trades, roughly 6 months.
