# SOXL/SOXS intraday strategy research plan

**Status: plan only. Nothing below has been run.** Written 2026-09-28, building on
[reports/SOXL and SOXS intraday behavior.md](reports/SOXL%20and%20SOXS%20intraday%20behavior.md).

**Goal:** find mechanical intraday rules on SOXL's 1-minute chart that clear trading costs on data they were not
fitted to. Bullish signals are traded with SOXL and bearish signals with SOXS.

---

## 1. Rules that apply to every study

| Topic | Rule |
|---|---|
| Signal chart | SOXL 1-minute regular-hours bars (09:30–15:59). Decide at a bar's close, enter at the next bar's open. |
| Instruments | Bullish → buy SOXL. Bearish → buy SOXS, **only if SOXS's unadjusted prior close is ≥ $10** (one cent ≤ 10 bps). Below $10 the bearish signal is logged but not traded (variant in Study 8: short SOXL instead). |
| Stops/targets | Always set on **SOXL's chart**. A SOXS position exits when SOXL hits the level ("mirror stop"). This avoids leverage-drift mismatch between the two funds. |
| Time | Flat by 15:55 unless a rule says otherwise. One position at a time. |
| Size | Fixed $25,000 per trade for comparisons (results in bps per trade). |
| Intrabar ambiguity | If one minute touches both the stop and the target, assume the stop hit first. |
| Look-ahead | Every input is computed only from bars already closed at the decision time (including relative volume). |

**Shared definitions**
- **σ(window):** the RMS of SOXL's 1-minute returns in the same clock window over the prior 20 sessions.
- **VWAP:** session VWAP from 09:30, regular hours only.
- **ATR14:** Wilder ATR of the daily true range through the prior day.
- **RVOLk:** volume in the first k minutes divided by the average volume of the same k minutes over the prior 14 sessions.

**Cost cases** (all three are reported for every study)
- **A:** measured half-spread per side for that half-hour and year, converted at the unadjusted price, plus SEC and FINRA fees on sells. $0 commission.
- **B:** case A plus $0.0035 per share per side.
- **Q:** the actual bid/ask quote at the entry and exit second, plus case B's fees. Required for anything that trades between 09:30 and 10:00.

---

## 2. Validation and pass/fail

| Period | Dates | Use |
|---|---|---|
| Development | 2022-01-03 → 2024-09-30 | Build and choose |
| Validation | 2024-10-01 → 2025-12-31 | Judge; no re-tuning |
| Holdout | 2026-01-02 → 2026-09-25 | One look per idea, only after validation passes |
| Pre-sample | 2019-01-02 → 2021-12-31 | Extra check. Older index and more missing minutes, so treat as a sanity check |
| Forward | 2026-09-28 onward | Paper trading |

**Caveat for Studies 1 and 2:** both leads were found in the 2022–2026 data, so development, validation and holdout
results for them are descriptive only. Their decisive tests are:
- the 2019–21 data
- the same rule on other tickers
- forward paper trading

**Cross-checks for every rule:**
- Run the same rule on **SOXX and SMH**. A semis effect should show the same sign at about 1/3 of SOXL's size.
- Run it on **NVDA, QQQ and TQQQ** as controls. If it works there too it is market-wide. If it works only on SOXL, treat it as suspect.

**A rule passes only if all of the following hold:**
1. Net ≥ **+5 bps per trade** in cost case B (SOXL legs; SOXS legs reported separately), and net > 0 in case Q.
2. In validation: day-clustered **t ≥ 2** and positive in **≥ 60% of quarters**.
3. It survives the **Benjamini–Hochberg correction at q ≤ 0.10**, counted across every variant run so far in this plan.
4. It is robust:
   - Entering one minute late keeps at least 50% of the gross edge.
   - The neighbouring parameter value does not flip the sign.
5. SOXX/SMH show the same sign, for semis effects.
6. Holdout net ≥ 0, looked at once.
7. Forward: at least 60 paper trades, with the mean net inside validation's 95% confidence interval.

A rule that fails any step is dropped and not re-tuned. The result is still logged.

**Output of every study:**
- A registry entry, committed before the run.
- A trades CSV.
- A summary CSV (variant × period × side × cost case).
- An equity chart.
- One verdict line in `analysis/strategies/RESULTS.md`.

---

## 3. Phase 0: groundwork (before any strategy test)

| # | Item | What it is | Size |
|---|---|---|---|
| 0.1 | Variant registry | `analysis/strategies/REGISTRY.md`: the exact rule text and variant list for each study, committed before it runs. The commit time proves the rule wasn't fitted after the fact. | Small |
| 0.2 | Quote-based fill model | For each entry and exit, pull the bid/ask at that second from Massive `/v3/quotes` (only around trade times, not whole days). Fill marketable orders at the ask/bid. | Medium |
| 0.3 | Event calendar | Dates for: <br>• NVDA, AMD, AVGO and MU earnings <br>• FOMC <br>• CPI <br>Covers 2019–2026, built from official sources. These were blocked in the analysis session, so a user-supplied CSV is the fallback. | Small–Medium |
| 0.4 | Regime tracker + paper log | Daily monitors (see Study 9) and a paper-trade log. | Small |
| 0.5 | Extra data | SPY 1-minute bars 2019–2026, used to sanity-check the Study 4 implementation against the published result. | Small |

---

## 4. Phase 1: leads from our own SOXL data

### Study 1: Late-day fade

**Evidence (2024–26):** the last 30 minutes moved against SOXL's day move in every bucket of SOXX's day move.

| SOXX day move | Under 1% | 1–2% | 2–3% | 3%+ |
|---|---|---|---|---|
| SOXL, last 30 min vs day's direction | −24 bps | −27 bps | −46 bps | −33 bps |

- The effect appears in SOXX and SMH at about 1/3 of the size.
- It does not appear in NVDA alone, and QQQ/TQQQ continue on big days.
- It trades at the cheapest time of day: spread ≈ 0.08 of a 1-minute move.
- **Risk:** it was momentum in 2020–21 and weak in 2022–24, so it depends on regime.

**Rules**
1. At the close of the 15:29 bar:
   - D = SOXL's return since the prior official close.
   - R = SOXX's return since the prior close.
2. Trade only if |R| ≥ **1.0%** (variant: 2.0%).
3. **Regime gate:** trade only if the trailing 120-session OLS slope of (15:30→close return) on (09:30→15:30 return) is **< 0**, computed through the prior day. Variant: gate off.
4. Enter at the **15:30 open, against D.** If D > 0, buy SOXS; if D < 0, buy SOXL.
5. **Stop:** an adverse move of 1.5 × the RMS of SOXL's 15:30–16:00 returns over the prior 20 sessions.
6. **Exits:**
   - E1: 15:55 open.
   - E2: 15:59 bar close.
   - E3: official close via MOC, on SOXL legs only. SOXS's closing auction is only 0.12% of its daily volume.

**Variants:** 2 thresholds × 3 exits × gate on/off = **12**.
**Extra checks:**
- 2019–21, expected to fail; this confirms the regime gate matters.
- SOXX/SMH, same sign.
- Controls: NVDA, QQQ and TQQQ.

### Study 2: Opening burst continuation

**Evidence (2024–26):** after a 1-minute move of at least 2σ between 09:31 and 10:00, the next minute averaged:

| Ticker | Next-minute move | Continued | t |
|---|---|---|---|
| SOXL | +8.4 bps | 55% | 3.8 |
| SOXX | +2.4 bps | 55% | 3.2 |
| SMH | +1.5 bps | 55% | 2.3 |
| NVDA, QQQ, TQQQ | +0.4 to +1.7 bps | | not significant |

- It happened about 1.6 times a day on SOXL.
- For moves of at least 3σ, SOXL's next minute averaged +13 bps.
- **Risk:** only +2.9 bps in 2022–24, and it fades after the first minute.

**Rules**
1. z = the 1-minute return ÷ σ(09:30–10:00).
2. Trigger: a bar closing between **09:31 and 09:58** with |z| ≥ **2** (variant: 3).
3. Enter at the next open in the same direction.
4. Exit after **1 minute** (variant: 3 minutes, with a stop at 1σ adverse). No stop on the 1-minute hold.
5. At most 3 trades a day, with no overlap.
6. **Filters, one at a time:**
   - F0: none.
   - F1: the trigger bar's volume is ≥ 2× the prior 20-session average for that minute.
   - F2: the trigger bar closes in its top 25% (up moves) or bottom 25% (down moves).
   - F3: the move's direction matches the sign of the overnight gap.
7. **Cost case Q is mandatory.** At the open the spread is about 6 bps quoted and 3 bps effective, so the expected net edge is only about +4–5 bps.

**Variants:** 2 thresholds × 2 holds × 4 filters = **16**.
**Extra checks:** 2019–21; SOXX/SMH; controls NVDA, QQQ, TQQQ.

---

## 5. Phase 2: published strategies adapted to SOXL

### Study 3: Opening-range breakout

**Evidence:**
- Our 15-minute version made +24 bps per trade after costs in 2024–26 (SOXL only). It is fragile (t 1.19) and lost 13 bps per trade before costs in 2026 to date.
- The published 5-minute version on QQQ/TQQQ (Zarattini & Aziz 2023) won 24% of trades and averaged +0.13R per trade with 10R targets.
- Independent replications reproduce the result before costs, but it breaks even at about 2.2¢/share of slippage on QQQ and nets about zero on index futures.
- Restricting it to days with unusual early volume ("stocks in play", Zarattini, Barbon & Aziz 2024) reported a Sharpe ratio of 2.8.

**Designs**
- **A (15-minute baseline):**
  - The opening range is the high/low of 09:30–09:44.
  - From 09:45, the first 1-minute close outside the range triggers entry at the next open.
  - The stop is at the far side of the range. Exit at 15:55. One trade a day.
- **B (5-minute candle, as published):**
  - The first candle is 09:30–09:34. Trade only if its body is ≥ 10% of its range.
  - Trade in the candle's direction at the 09:35 open.
  - The stop is at the other side of that candle. The target is 10× the risk; otherwise exit at 15:55.
- **C (in play):** A or B, taken only when RVOL5 ≥ 1.0 / 1.5 / 2.0.
- **D (published tight stop):** A or B with RVOL5 ≥ 1.0 and the stop at entry ∓ 0.10 × SOXL's ATR14.
- **E (filters on A):**
  - E1: the opening-range size is between the 20th and 80th percentile of the trailing 60 sessions.
  - E2: the prior day's range is ≥ the 60th percentile of the trailing 60 sessions.
- **F (exit):** A and B, but after +1R exit on a 1-minute close back through VWAP.

**Variants:** A, B, 3 for C on A, 3 for C on B, 2 for D, 2 for E, 2 for F = **14**.
Longs and shorts are reported separately, because SOXL's 10× rally flatters the long side.
**Extra checks:** TQQQ/QQQ (the published instruments; B should come out positive before costs) and SOXX/SMH.

### Study 4: Noise-boundary momentum (not yet tested on SOXL)

**Evidence:**
- On SPY from 2007 to 2024 this made +1,985% net, 19.6% a year, with a Sharpe of 1.33, after $0.0035 + $0.001 per share of costs (Zarattini, Aziz & Barbon 2024).
- A follow-up reports that VWAP-based exits improved it (Maróy 2025). That result used parameter optimization, so treat it with caution.

**Rules**
1. For each minute t: σ_move(t) = the average over the prior 14 sessions of |price(t) ÷ that day's open − 1|.
2. Upper band = max(today's open, prior close) × (1 + k·σ_move(t)).
3. Lower band = min(today's open, prior close) × (1 − k·σ_move(t)).
4. Check **only at 10:00, 10:30, …, 15:30**:
   - A close above the upper band means buy SOXL.
   - A close below the lower band means buy SOXS.
   - An opposite signal exits the current position and reverses.
5. **Trailing exit:**
   - Exit longs when SOXL closes below the higher of the upper band and VWAP.
   - Exit shorts when SOXL closes above the lower of the lower band and VWAP.
6. Flat at 15:55.

**Variants:** k ∈ {1.0, 1.5} × stop checked {every minute, half-hour marks only} = **4**.
**Extra check:** SPY must reproduce the published sign before SOXL results are trusted.

---

## 6. Phase 3: filters on the rules that survive

### Study 5: Big-day gate

**Evidence (2024–26):**
- After a top-20% range day, the next day's median range was 10.4%. After a bottom-20% day it was 5.9%.
- Days after earnings and FOMC days run 1.2–1.45× the normal range.

**Gates, tested on each rule that survives Studies 1–4:**
- **G1:** the prior day's range is ≥ the 60th percentile of the trailing 60 sessions.
- **G2:** RVOL15 ≥ 1.5 for rules that decide after 09:45; RVOL5 ≥ 1.5 for earlier ones.
- **G3:** event day. This is the session after NVDA/AMD/AVGO/MU earnings, an FOMC day or a CPI day. It needs item 0.3.
- **G4:** G1 or G2 or G3.

Keep a gate only if it improves net per trade in **both** development and validation.

**Side check (descriptive):** compare the next-day range after NR7 days (the narrowest range in 7) with other days. This is Crabel's contraction→expansion idea, which our range-clustering data argues against.

**Variants:** 4 per surviving rule.

---

## 7. Phase 4: setups and chart patterns

### Study 6: Failed-break fade at key levels

**Evidence (2024–26):**
- 72–83% of first breaks of the pre-market high or low trade back through the level within 15 minutes.
- But the day still closes beyond the pre-market high on 60% of break days, and beyond the low on 44%. So any edge is short-lived, and failed lows look more promising than failed highs.
- This is an intraday version of Raschke & Connors' Turtle Soup.

**Rules**
1. Levels: the pre-market high/low (04:00–09:29) and the prior day's regular-hours high/low.
2. Window: 09:30–10:30.
3. **Break:** a 1-minute high ≥ the level + $0.01 (mirror for lows).
4. **Failure:** within the next 10 bars, a 1-minute close back on the other side of the level.
5. Enter at the next open, against the break. A failed high means buy SOXS; a failed low means buy SOXL.
6. **Stop:** the extreme reached since the break, ± 0.1%.
7. **Targets:** T1 = 1R, or T2 = VWAP, whichever variant applies. Time stop: 20 minutes.
8. One trade per level per day.

**Variants:** 2 level types × 2 targets = **4**. Failed highs and failed lows are reported separately.

### Study 7: 1-minute chart patterns, tested only in context

**Why lower priority:** runs of same-coloured candles are random, and big candles are a coin flip after 10:00.

**Patterns**
- **Engulfing:** the candle's body covers the prior opposite-coloured body, and is ≥ 1.5× the median body of the last 20 candles.
- **Hammer / shooting star:**
  - The rejection wick is ≥ 2× the body.
  - The other wick is ≤ 25% of the range.
  - The range is ≥ 1.5× the median range of the last 20 candles.
- **Inside-bar break:** a candle sits entirely inside the prior candle. Enter on a close beyond the prior candle's high or low.
- **Flag:**
  - An impulse of 3–10 candles moves ≥ 2.5σ·√n, with ≥ 70% of candles the same colour.
  - It is followed by a 3–10 candle pullback retracing 25–60% on lower volume.
  - Enter on a close beyond the pullback. The stop is beyond the pullback's other end.
  - Target: the impulse length, otherwise a 30-minute time stop.
- **Squeeze:**
  - The 20-candle Bollinger band width (2σ) is at its lowest of the last 120 candles.
  - Enter on the first close outside the bands. The stop is the middle band.
  - 30-minute time stop.

**Contexts**
- C1: the first 30 minutes.
- C2: within 0.1% of the pre-market high/low, prior-day high/low, or 15-minute opening-range high/low.
- C3: beyond VWAP ± 2σ.

**Method**
1. **Stage 1, development data only.** Run an event study of the moves at +1, +5, +15 and +30 minutes from the next open, against random entries at the same time of day.
2. **Stage 2.** Only patterns clearing +5 bps net with t ≥ 2 get full rule backtests and validation.

**Variants:** 5 patterns × 3 contexts = **15**.

---

## 8. Phase 5: execution

### Study 8: Execution upgrades (only for rules that pass)

- **X1:** a limit order at the midpoint for 10 seconds, then cross the spread.
- **X2:** a limit order at the near side + 1 tick for 10 seconds, then cross.
- **Simulation:** use real quotes and trades. Count a fill only if a trade prints at or through the limit.
- **Measurements:**
  - Fill rate.
  - Cost saved.
  - Adverse selection: how filled trades turn out compared with unfilled ones.
- **Why:** SOXL's spread is about 5¢ wide at ~$150, so this could save 1–2 bps per trade. That matters most for Study 2.
- **Bearish leg when SOXS is below $10:**
  - S1: skip the trade.
  - S2: short SOXL instead, assuming shares are available to borrow.

**Variants:** 2 order types + 2 bearish-leg options, per surviving rule.

---

## 9. Phase 6: forward testing and monitoring

### Study 9: Paper trading and regime monitors

- **Paper log.** For each rule from the day it passes validation, record:
  - the signal time
  - the intended fill
  - the actual bid/ask at that second
  - the outcome
- **Daily monitors:**
  - Late-day slope over the trailing 120 sessions, for SOXL and SOXX. This is Study 1's gate.
  - Opening-burst next-minute mean over the trailing 60 sessions.
  - SOXS's unadjusted price and relative tick, which gates the SOXS leg.
  - SOXL's share of time at a one-tick spread over the last 20 days. This shows the spread regime.
  - Each live rule's net per trade over its last 60 trades.
- **Pause rule (declared now):** pause a rule when its rolling 60-trade net is < 0 **and** t < −1. Resume only after a fresh 60-trade paper sample is ≥ 0.

---

## 10. Variant count (for the multiple-testing correction)

| Study | Variants |
|---|---|
| 1 Late-day fade | 12 |
| 2 Opening burst | 16 |
| 3 Opening-range breakout | 14 |
| 4 Noise boundary | 4 |
| 6 Failed-break fade | 4 |
| 7 Chart patterns (stage 1) | 15 |
| **Fixed total** | **65** |
| 5 Big-day gate | + 4 per surviving rule |
| 8 Execution | + 4 per surviving rule |

---

## 11. Order and dependencies

| Step | Work | Needs | Size |
|---|---|---|---|
| 1 | Phase 0: registry, fill model, tracker/log, SPY data | none | Medium |
| 2 | Event calendar (0.3) | none (runs alongside step 1) | Small–Medium |
| 3 | Study 1: late-day fade | registry | Small |
| 4 | Study 2: opening burst | fill model | Small |
| 5 | Study 3: opening-range breakout | registry | Small |
| 6 | Study 4: noise boundary | SPY data | Medium |
| 7 | Study 5: big-day gate on survivors | event calendar, steps 3–6 | Small |
| 8 | Studies 6 and 7, as one batch | registry | Medium |
| 9 | Study 8: execution on survivors | fill model | Large |
| 10 | Study 9: paper trading and monitors | runs from step 3 onward | Small, ongoing |

**Out of scope for now:**
- Overnight holds.
- Options- or futures-based signals (history on this account starts in late 2024).
- Order-book depth beyond the best bid/ask.
- Machine-learning models. These come later, once rule baselines exist to beat.

---

## Sources for the published rules

- Zarattini & Aziz (2023), *Can Day Trading Really Be Profitable?*: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622>. Rule summary: <https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/>
- Independent replications of that ORB:
  - <https://github.com/giovannibrusco/zarattini-2023-orb-qqq>
  - <https://www.mql5.com/en/blogs/post/776235>
- Zarattini, Barbon & Aziz (2024), *A Profitable Day Trading Strategy for the U.S. Equity Market*: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284>. Rule summary: <https://quantifiedstrategies.substack.com/p/how-to-trade-stocks-in-play>
- Zarattini, Aziz & Barbon (2024), *Beat the Market: An Effective Intraday Momentum Strategy for SPY*: <https://ssrn.com/abstract=4824172>. Summaries:
  - <https://concretumgroup.substack.com/p/beat-the-market-with-intraday-momentum>
  - <https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/>
- Maróy (2025), *Improvements to Intraday Momentum Strategies*: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349>
- Crabel NR7: <https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/narrow-range-day-nr7>
- Turtle Soup (Raschke & Connors):
  - <https://www.mql5.com/en/articles/2717>
  - <https://www.turtletrader.com/trader-raschke/>

The SOXL figures quoted above come from `analysis/behavior/output/`, `analysis/microstructure/output/` and
`analysis/backtests/output/` in this repository.
