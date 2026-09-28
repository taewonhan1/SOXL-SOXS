# Pre-registered variant registry

This file fixes every rule, parameter, neighbour, cross-check and pass criterion **before any
study is run**. Its git commit time is the proof of that. Studies 5 and 8 depend on which variants
survive, so they get their own registry entries, each committed before that study runs.

- Plan: [RESEARCH_PLAN.md](../../RESEARCH_PLAN.md)
- Code: `soxlab/research/` (rules in `rules.py`, execution and costs in `engine.py`, statistics in `common.py`)

---

## 0. Global conventions

**Charts and timing**
- The signal chart is the regular-session 1-minute panel: bars 0..389 = 09:30..15:59 ET, split-adjusted.
- A decision at bar j's close is filled at bar j+1's open. Inputs use only bars ≤ j, pre-market bars, and prior days.

**Execution in switch mode (SOXL signals)**
- Bullish → long SOXL.
- Bearish → long SOXS, only if SOXS's **unadjusted prior official close ≥ $10**. Otherwise the trade is skipped and counted.
- Stops, targets and exits are evaluated on SOXL's chart. The SOXS leg exits at the same bar and kind.
- For an intrabar SOXL level P, the SOXS fill is SOXS_entry × (2 − P/pcL) / (2 − SOXL_entry/pcL), clipped to that SOXS bar's low–high.
- One position at a time. $25k per trade. Results are in bps per trade.
- Default exit is flat at the open of bar n_min − 5 (15:55; 12:55 on half-days).

**Intrabar rules**
- If a bar touches both the stop and the target, the stop wins.
- A bar that opens beyond a level fills at that open.
- Close-based exits fill at the next open.

**Cost cases**
- **A:** half-spread per side from the spread table (bucket × year × unadjusted price) + SEC Section 31 and FINRA TAF on sells. $0 commission.
- **B:** A + $0.0035/share/side.
- **Q:** real NBBO at the fill second. Buys at the ask, sells at the bid. Stop exits at the level ∓ the prevailing half-spread. Target exits at the level. Auction exits at the official close. Plus case-B commission and fees.
- An official-close (auction) exit pays no exit half-spread in A/B.
- Spread table sources:
  - 2022–2026: `analysis/microstructure/output/cost_model_halfspread.csv`
  - 2019–2021 and SPY: `analysis/strategies/output/cost_table_supplement.csv`

**Periods**

| Period | Dates |
|---|---|
| pre | 2019-01-02 → 2021-12-31 |
| dev | 2022-01-03 → 2024-09-30 |
| val | 2024-10-01 → 2025-12-31 |
| hold | 2026-01-02 → 2026-09-25 |

- Holdout results are not tabulated for any variant until it passes criteria 1–5 including BH.
- Forward = paper trading from 2026-09-28.

**Pass criteria (validation, side = all)**
1. Case-B mean net ≥ **+5 bps/trade**, and case-Q mean net > 0. Q is computed for every Study 2 variant, and for any other variant before its holdout look.
2. Case-B day-clustered **t ≥ 2**, and **≥ 60%** of calendar quarters with trades have a positive mean net.
3. **Benjamini–Hochberg q ≤ 0.10** across all registered variants. The p-value is one-sided, from the case-B day-clustered t with G−1 df, where G = days with trades.
4. **Robustness (case B):**
   - (a) Entering one bar later keeps ≥ 50% of the base mean gross (base gross must be > 0).
   - (b) The pre-declared neighbour's mean net is > 0.
5. **Cross-check:** SOXX and SMH, run L/S on their own charts with the same rule, have a validation mean gross of the same sign as SOXL's.
6. **Holdout:** case-B mean net ≥ 0. Looked at once, only after 1–5 pass.
7. **Forward:** ≥ 60 paper trades. Pending.

**Extra requirements for Studies 1 and 2**
- Their effects were found in 2022–2026 data.
- They must also show case-B mean net > 0 in **pre** (2019–21).
- SOXX and SMH must show the same gross sign in pre and dev.

**Multiple-testing family:** the 65 fixed variants below, plus every Study 5/7/8 variant that is later registered and run.

**Cross-check and control tickers**
- The same rule is run L/S on each ticker's own chart.
- Index proxy: SOXX for SOXX, SMH and NVDA; QQQ for QQQ and TQQQ; SPY for SPY.
- Each ticker's own spread table is used.

---

## Study 1: late-day fade (12 variants)

**Rules**
- **Days:** full sessions only.
- **Inputs at the 15:29 bar close (bar 359):**
  - D = SOXL c[359] / prior official close − 1.
  - R = SOXX c[359] / SOXX prior official close − 1.
- **Filter:** |R| ≥ thr, and D ≠ 0.
- **Gate (when on):**
  - Trade only if the OLS slope of y on x over the prior 120 full sessions is < 0 (needs ≥ 60 sessions).
  - x = c[359]/open − 1; y = c[389]/c[359] − 1.
- **Direction:** s = −sign(D).
- **Entry:** open of bar 360 (15:30).
- **Stop:** 1.5 × σ30 adverse from the entry price. σ30 = RMS of y over the prior 20 full sessions (needs ≥ 15).
- **Exits:**
  - E1: open of bar 385 (15:55).
  - E2: close of bar 389 (15:59).
  - E3: official close (closing auction) for SOXL legs. SOXS legs use E2, because SOXS's closing auction is tiny. In L/S cross-checks E3 uses the official close for both sides.

| ID | thr | exit | gate |
|---|---|---|---|
| S1-01 | 1.0% | E1 | on |
| S1-02 | 1.0% | E1 | off |
| S1-03 | 1.0% | E2 | on |
| S1-04 | 1.0% | E2 | off |
| S1-05 | 1.0% | E3 | on |
| S1-06 | 1.0% | E3 | off |
| S1-07 | 2.0% | E1 | on |
| S1-08 | 2.0% | E1 | off |
| S1-09 | 2.0% | E2 | on |
| S1-10 | 2.0% | E2 | off |
| S1-11 | 2.0% | E3 | on |
| S1-12 | 2.0% | E3 | off |

- **Neighbour:** thr = 1.5%, same exit and gate.
- **Delay:** entry at bar 361.
- **Cross-checks:** SOXX, SMH, NVDA, QQQ, TQQQ, each with its own D, its own gate and its index proxy's R.

## Study 2: opening burst continuation (16 variants)

**Rules**
- σ = √(mean r²) of SOXL 1-minute simple returns on bars 1..29 (09:31–09:59) over the prior 20 sessions (needs ≥ 15).
- z = r_t / σ, for trigger bars t = 1..28.
- **Trigger:** |z| ≥ k.
- **Entry:** open of bar t+1, direction = sign(r_t).
- **Exit:** open of bar t+1+hold.
  - hold = 3 adds a stop at 1σ adverse from entry.
  - hold = 1 has no stop.
- Trades may not overlap, judged by the planned exit bar. At most 3 per day.
- **Filters:**
  - F0: none.
  - F1: the trigger bar's volume ≥ 2× the prior-20-session mean volume of that minute.
  - F2: close location (c−l)/(h−l) ≥ 0.75 for up triggers, ≤ 0.25 for down triggers.
  - F3: sign(r_t) = sign(overnight gap). Gap = first open / prior official close − 1.

**Variant order:** k ∈ {2, 3}, then hold ∈ {1, 3}, then filter ∈ {F0, F1, F2, F3}.

| ID | k | hold | filter |
|---|---|---|---|
| S2-01 | 2 | 1 | F0 |
| S2-02 | 2 | 1 | F1 |
| S2-03 | 2 | 1 | F2 |
| S2-04 | 2 | 1 | F3 |
| S2-05 | 2 | 3 | F0 |
| S2-06 | 2 | 3 | F1 |
| S2-07 | 2 | 3 | F2 |
| S2-08 | 2 | 3 | F3 |
| S2-09 | 3 | 1 | F0 |
| S2-10 | 3 | 1 | F1 |
| S2-11 | 3 | 1 | F2 |
| S2-12 | 3 | 1 | F3 |
| S2-13 | 3 | 3 | F0 |
| S2-14 | 3 | 3 | F1 |
| S2-15 | 3 | 3 | F2 |
| S2-16 | 3 | 3 | F3 |

- **Neighbour:** k + 0.5.
- **Delay:** entry at bar t+2.
- **Case Q:** computed for every variant.
- **Cross-checks:** SOXX, SMH, NVDA, QQQ, TQQQ.

## Study 3: opening-range breakout (14 variants)

**Design A (15-minute range)**
- Opening range (OR) = high and low of bars 0..14.
- Trigger: the first close outside the range on bars 15..tx−2.
- Entry: next open.
- Stop: the opposite OR side.
- Exit: open of bar n_min − 5.

**Design B (first 5-minute candle)**
- Candle: open of bar 0 → close of bar 4, with its high H and low L.
- Skip if the body is < 10% of the range.
- Entry: open of bar 5, in the candle's direction.
- Stop: L for longs, H for shorts.
- Target: 10R.
- Exit: open of bar n_min − 5.

**Modifiers**
- **RVOL5** = volume of bars 0..4 ÷ the prior-14-session mean of the same.
- **ATR stop** = entry ∓ 0.10 × SOXL's daily ATR14 through the prior day. B's 10R target is measured from this stop.
- **E1:** OR size within the prior 60 sessions' 20th–80th percentile (needs ≥ 40 sessions).
- **E2:** the prior day's range ≥ the 60th percentile of the 60 sessions ending the prior day.
- **Trail:** after +1R is touched, exit at the next open once a close crosses back through VWAP. The original stop stays in force.
- Trades whose entry is already beyond the stop are skipped.

| ID | Design | RVOL5 ≥ | Other |
|---|---|---|---|
| S3-01 | A | – | – |
| S3-02 | B | – | – |
| S3-03 | A | 1.0 | – |
| S3-04 | A | 1.5 | – |
| S3-05 | A | 2.0 | – |
| S3-06 | B | 1.0 | – |
| S3-07 | B | 1.5 | – |
| S3-08 | B | 2.0 | – |
| S3-09 | A | 1.0 | ATR stop 0.10 |
| S3-10 | B | 1.0 | ATR stop 0.10 |
| S3-11 | A | – | E1 |
| S3-12 | A | – | E2 |
| S3-13 | A | – | trail after +1R |
| S3-14 | B | – | trail after +1R |

**Neighbours**
- S3-01: 20-minute OR.
- S3-02: 10-minute candle.
- RVOL variants: θ + 0.25.
- ATR variants: 0.15.
- S3-11: 15th–85th percentile band.
- S3-12: 50th percentile.
- Trail variants: +1.5R.

**Delay:** +1 bar.
**Cross-checks:** SOXX, SMH, NVDA, QQQ, TQQQ.

## Study 4: noise-boundary momentum (4 variants)

**Rules**
- **Days:** full sessions only.
- σ_move[t] = mean over the prior 14 full sessions of |c[t]/open − 1|.
- UB = max(open, prior close) × (1 + k·σ_move[t]).
- LB = min(open, prior close) × (1 − k·σ_move[t]).
- **Check bars:** 29, 59, …, 359 (10:00 … 15:30).
- **Entries and reversals:** at a check bar, a close > UB means long; < LB means short. If that differs from the current position, exit (if in one) and enter at the next open.
- **Trailing exit (otherwise):** exit a long at the next open when the close < max(UB, VWAP); exit a short when the close > min(LB, VWAP).
  - M = checked every bar.
  - H = checked only at check bars.
- **Flat:** open of bar 385. No entry at or after it.

| ID | k | Trailing check |
|---|---|---|
| S4-01 | 1.0 | M |
| S4-02 | 1.0 | H |
| S4-03 | 1.5 | M |
| S4-04 | 1.5 | H |

- **Neighbour:** k + 0.25.
- **Delay:** entry at bar t+2.
- **SPY sanity check:** all four variants run L/S on SPY. Mean gross over pre+dev+val > 0 is required before the SOXL results are trusted. Otherwise report "did not reproduce".
- **Cross-checks:** SOXX, SMH, NVDA, QQQ, TQQQ.

## Study 5: big-day gates (exploratory; registered 2026-09-28 before running)

**Why exploratory:** no variant from Studies 1–4 passed criteria 1–5. The main failure was validation t < 2.
- The gates are therefore run as diagnostics on the four near-misses.
- A near-miss here means a validation case-B net ≥ +5 bps that passed robustness (c4) and cross-checks (c5): S3-01, S3-13, S4-02 and S4-04.
- These results **cannot** make a rule pass. They are counted in the BH family.

**Gates** (day-level, known before the rule's first decision)
- **G1:** the prior day's regular-session range ≥ the 60th percentile of the 60 sessions ending the prior day.
- **G2:** RVOL15 = volume of bars 0..14 ÷ the prior-14-session mean of the same, ≥ 1.5. All four rules decide at or after 09:45.
- **G3:** event day, meaning any of:
  - (a) The session after an NVDA, AMD, AVGO or MU earnings release. Detected causally: that stock's after-hours (16:00–20:00) volume on day d−1 ≥ 5× its median over the prior 60 sessions.
  - (b) A scheduled FOMC statement day, from the list below.
  - (c) An 08:30 macro-release day: QQQ's 08:30 1-minute bar volume ≥ 5× its median over the prior 60 sessions. This is a CPI proxy, because official CPI calendars were unreachable from this session. It also catches payrolls and PPI.
- **G4:** G1 or G2 or G3.

**FOMC statement days used by G3(b)**

| Year | Dates |
|---|---|
| 2019 | 01-30, 03-20, 05-01, 06-19, 07-31, 09-18, 10-30, 12-11 |
| 2020 | 01-29, 04-29, 06-10, 07-29, 09-16, 11-05, 12-16 (the March 2020 emergency actions are excluded) |
| 2021 | 01-27, 03-17, 04-28, 06-16, 07-28, 09-22, 11-03, 12-15 |
| 2022 | 01-26, 03-16, 05-04, 06-15, 07-27, 09-21, 11-02, 12-14 |
| 2023 | 02-01, 03-22, 05-03, 06-14, 07-26, 09-20, 11-01, 12-13 |
| 2024 | 01-31, 03-20, 05-01, 06-12, 07-31, 09-18, 11-07, 12-18 |
| 2025 | 01-29, 03-19, 05-07, 06-18, 07-30, 09-17, 10-29, 12-10 |
| 2026 | 01-28, 03-18, 04-29, 06-17, 07-29, 09-16 |

**Variants:** S5-01..S5-16, rule-major (S3-01, S3-13, S4-02, S4-04) × gate (G1, G2, G3, G4).

**Decision rule:** a gate is "kept" only if it raises case-B mean net per trade versus the ungated rule in both dev and val.

**Descriptive side check:** SOXL's next-day range after NR7 days versus other days, 2022–2026.

## Study 6: failed-break fade (4 variants)

**Levels**
- PM = pre-market high/low (04:00–09:29, needs ≥ 5 pre-market bars).
- PD = prior regular-session high/low.

**Break and failure**
- **Failed high:** a bar in 0..59 has high ≥ level + $0.01 (unadjusted cent). Failure = within that bar or the next 10, a close < level. Direction: bearish.
- **Failed low:** mirror image, low ≤ level − $0.01 and a close > level. Direction: bullish.

**Trade**
- **Entry:** open after the failure bar.
- **Stop:** the extreme since the break × (1 ± 0.1%).
- **Target:**
  - T1 = 1R.
  - T2 = VWAP at the failure bar. There is no target if VWAP is not on the profitable side.
- **Time stop:** 20 minutes, capped at the 15:55 flat.
- At most one trade per level per day, and one position at a time.

| ID | Levels | Target |
|---|---|---|
| S6-01 | PM | T1 |
| S6-02 | PM | T2 |
| S6-03 | PD | T1 |
| S6-04 | PD | T2 |

- **Neighbour:** failure window 15 bars.
- **Delay:** +1 bar.
- **Reporting:** failed highs (bear) and failed lows (bull) are also reported separately.
- **Cross-checks:** SOXX, SMH, NVDA, QQQ, TQQQ.

## Study 7: 1-minute chart patterns (15 stage-1 combinations × 4 horizons)

**Stage 1 (development period only)**
- Uses signal-chart (SOXL) returns from the next bar's open, at +1, +5, +15 and +30 minutes, signed by the pattern direction.
- **Excess** = signed return − the pattern direction × the mean return of the same bar and horizon over all development days (time-of-day baseline).
- **Net** = excess − the case-B SOXL round-trip cost at that time.
- A combination passes stage 1 if, at some horizon, all three hold:
  - net ≥ +5 bps
  - day-clustered t ≥ 2
  - BH q ≤ 0.10 across all 60 stage-1 tests
- Passing combinations become stage-2 variants S7-xx:
  - Entry at the next open in the pattern direction.
  - Stop = the pattern extreme ∓ 0.1%.
  - Flags keep their measured-move target. Squeezes use the middle band as the stop.
  - Time exit at the passing horizon.
  - Full criteria in switch mode.

**Patterns** (bullish form; bearish is the mirror)
- **Engulfing:**
  - Bar t−1 red, bar t green.
  - o_t ≤ c_{t−1} and c_t ≥ o_{t−1}.
  - |c_t − o_t| ≥ 1.5 × the median |c − o| of bars t−20..t−1.
  - Extreme = min(l_{t−1}, l_t).
- **Hammer:**
  - Lower wick ≥ 2 × body, where body = max(|c − o|, one cent).
  - Upper wick ≤ 0.25 × range.
  - Range ≥ 1.5 × the median range of bars t−20..t−1.
  - Extreme = l_t.
  - The shooting star is the mirror.
- **Inside-bar break:**
  - Bar t−1 lies inside bar t−2.
  - Trigger: c_t > h_{t−2}.
  - Extreme = l_{t−1}.
- **Flag:**
  - Impulse of n ∈ [3, 10] bars with net move ≥ 2.5·σ_tod·√n and ≥ 70% same-colour bars.
  - σ_tod = RMS of SOXL 1-minute returns in the same half-hour over the prior 20 sessions.
  - Then a pullback of m ∈ [3, 10] bars retracing 25–60% of the impulse, with a lower mean volume than the impulse.
  - Trigger: c_t > the pullback's maximum high.
  - Extreme = the pullback's low.
  - Target = entry + the impulse's price move.
- **Squeeze:**
  - 20-bar Bollinger bands (SMA ± 2 sd of closes).
  - Width at t−1 = the minimum of bars t−120..t−1, within the session.
  - Trigger: the first close above the upper band.
  - Stop = the middle band.
  - No events before bar 121.

**Contexts** (at the trigger bar)
- **C1:** bars 0..29.
- **C2:** the close is within 0.1% of any of PM high/low, PD high/low, or OR15 high/low (OR15 only from bar 15).
- **C3:** |c − VWAP| ≥ 2 VWAP-σ.

## Study 8: execution (exploratory; registered 2026-09-28 before running)

There are no survivors, so this also runs on the four near-misses (S3-01, S3-13, S4-02, S4-04).

- **S8-01..S8-04:** the bearish leg is **short SOXL** on every day (switch_short mode) instead of SOXS with the $10 rule. Borrow cost is assumed zero for intraday shorts.
- **X1/X2 (limit entries): deferred, not run.**
  - The near-miss rules trade at most about once a day, at 09:45–15:30.
  - SOXL's measured half-spread there is about 1–3 bps, against 20–57 bps gross per trade.
  - The fill-model upgrade would be second-order, and it only matters for a rule that passes.
- These results cannot make a rule pass. They are counted in the BH family.

## Studies 10–12: 1-minute momentum scalps (registered 2026-09-28 before running)

Requested setups: Hitchhiker-like (Study 10), Bone Zone-like (Study 11) and bull/bear-flag-like (Study 12)
momentum scalps on the 1-minute chart. The rules are SMB-inspired, not copies of any published or in-house rule
set. They were fixed before any of their returns were computed. Before registering, only the number of setups per
period was checked, to make sure each rule trades often enough to be tested.

**Common to Studies 10–12**
- **Signal chart:** SOXL 1-minute bars. Tick = $0.01 unadjusted.
- **Execution:** switch mode, as in §0. Bearish signals go to SOXS when its prior close is ≥ $10; otherwise they are skipped.
- **Stop-order entries** ("stop" variants):
  - Fill inside the trigger bar at the order level, or at that bar's open if it opens beyond the level.
  - For SOXS, the fill is mirrored from the SOXL level, anchored at the bar open and clipped to the SOXS bar's low–high.
  - On the entry bar, a touched protective stop counts as hit (after the fill) and no target can fill.
- **Close-confirm entries** ("close" variants): enter at the open of the bar after the trigger bar closes.
- **σ_tod:** RMS of 1-minute returns in the same half-hour bucket over the prior 20 sessions (≥ 15 required).
- **EMAs:** 1-minute closes, reset each session.
- **Exit schemes.** Every scheme keeps the initial stop and is flat by the §0 flat bar (15:55).
  - **X2R:** target entry ± 2R; time exit at the open of e+30.
  - **XT:** target = retest of the impulse extreme if it is ≥ 1R away, else 2R; time exit e+30.
  - **XS:** target 1R; time exit e+10.
  - **XM:** target = entry ± pole height (measured move); time exit e+60.
  - **XSO (scale-out):** two equal legs.
    - Leg A: target 1R, time exit e+30.
    - Leg B: no target; exits at the next open after a 1-minute close through the trail EMA; time exit e+60.
    - The trade's result is the average of the two legs.
- **Positions:** one at a time. A scale-out position is open until both legs are out. At most 3 signals a day (Studies 11–12). Study 10 takes only the first setup of the day.
- **Robustness (criterion 4):**
  - Delay = one bar later: a stop entry becomes the next bar's open, and a close entry becomes the open two bars after the trigger.
  - The neighbour is listed per study.
- **Cross-checks:** SOXX, SMH, NVDA, QQQ and TQQQ, run L/S on their own charts.
- **Case Q:** computed for the validation trades of every variant. A stop entry fills at the level + the prevailing half-spread, with the NBBO taken at the entry bar's open.
- **Case S (stress, reported, not a pass criterion):** case B plus 1 cent of extra slippage on every stop-order fill, meaning stop entries and stop-loss exits.
- **Status:** confirmatory. Pass criteria 1–5 are as in §0. The BH family is every registered variant: 70 already run + 24 here = 94. The within-family q over the 24 is also reported, as secondary.
- **Also reported (descriptive):** bull vs bear legs, entry time of day, and setups per day.

### Study 10: Hitchhiker-like opening drive → consolidation → breakout (12 variants)
- **σ_open:** RMS of 1-minute returns over bars 1..29 (09:31–09:59) in the prior 20 sessions. This is the typical opening-minute move.
- **Long setup at bar t** (t = 5 .. window end):
  - Drive: the high of bars 0..t−1 (HOD) is ≥ open × (1 + 3.0 × σ_open).
  - Consolidation: the bars after the HOD bar up to t−1. There are 3–15 of them, and their lowest low gives back ≤ 40% of (HOD − open).
  - Trigger, "stop": buy stop at HOD + 1 tick, filled in bar t.
  - Trigger, "close": bar t closes above the HOD.
  - Stop: consolidation low − 1 tick.
- **Short setup:** the mirror, using the low of day.
- **Selection:** the first setup of the day only. At each bar the long side is checked first.
- **Trail EMA (XSO leg B):** EMA9.

| ID | Breakout by (window end) | Entry | Exit |
|---|---|---|---|
| S10-01 | 09:59 (bar 29) | stop | X2R |
| S10-02 | 09:59 | stop | XSO |
| S10-03 | 09:59 | close | X2R |
| S10-04 | 09:59 | close | XSO |
| S10-05 | 10:14 (bar 44) | stop | X2R |
| S10-06 | 10:14 | stop | XSO |
| S10-07 | 10:14 | close | X2R |
| S10-08 | 10:14 | close | XSO |
| S10-09 | 10:29 (bar 59) | stop | X2R |
| S10-10 | 10:29 | stop | XSO |
| S10-11 | 10:29 | close | X2R |
| S10-12 | 10:29 | close | XSO |

**Neighbour:** drive threshold 2.5 × σ_open.

### Study 11: Bone Zone-like pullback into the EMA9/EMA21 band (6 variants)
- **Long trigger bar t** (t = 30 .. 360, i.e. 10:00–15:30):
  - Trend: EMA9 > EMA21 at bar t.
  - Bar t is green and closes ≥ EMA21.
- **Impulse:**
  - Peak = the highest high of bars t−11..t−1. The pullback is t−1−peak bars long, and must be 2–10 bars.
  - Base = the lowest low of the 16 bars ending at the peak. There must be ≥ 3 bars from base to peak.
  - Gain: peak/base − 1 ≥ 2.5 × σ_tod(peak) × √(bars from base to peak).
- **Pullback** (bars after the peak up to t−1):
  - At least one low touches EMA9.
  - No close is below EMA21.
  - The lowest low gives back ≤ 50% of the impulse.
  - Its mean volume per bar is ≤ 0.9 × the impulse's (base to peak).
- **Selection:** each impulse peak is used once, at its first valid trigger.
- **Stop:** 1 tick below the lower of the pullback low and bar t's low.
- **Entry, "close":** open of t+1.
- **Entry, "stop":** buy stop 1 tick above bar t's high, working for bars t+1..t+3. It is cancelled if the protective stop trades first.
- **Short setup:** the mirror, with EMA9 < EMA21.
- **Trail EMA (XSO leg B):** EMA21.

| ID | Entry | Exit |
|---|---|---|
| S11-01 | close | XT |
| S11-02 | close | XS |
| S11-03 | close | XSO |
| S11-04 | stop | XT |
| S11-05 | stop | XS |
| S11-06 | stop | XSO |

**Neighbour:** impulse threshold 2.0 × σ_tod × √bars.

### Study 12: bull/bear-flag-like continuation (6 variants)
- **Bull flag, trigger bar t** (t = 10 .. 360, i.e. 09:40–15:30):
  - Pole top = the highest high of bars t−13..t−1, counting from the open if that is earlier. The flag is the bars after the top up to t−1, and must be 3–12 bars.
  - Pole: base = the lowest low of the 16 bars ending at the top, counting from the open if earlier. There must be ≥ 3 bars from base to top, and the height (as a return) must be ≥ 2.5 × σ_tod(top) × √bars.
  - Flag: its lowest low retraces ≤ 50% of the pole, and its mean volume per bar is ≤ 0.9 × the pole's.
  - Resistance line: anchored at the pole top, through the flag high that keeps every flag high on or below it. Its slope is ≤ 0.
  - Trigger level = max(line at t, bar t−1's high).
- **Entry, "stop":** buy stop 1 tick above the trigger level, filled in bar t.
- **Entry, "close":** bar t closes above the trigger level; enter at the open of t+1.
- **Stop:** 1 tick below the flag low. For close entries, also below bar t's low.
- **Bear flag:** the mirror, with a support line through the lows.
- **Selection:** each pole top is used once.
- **Trail EMA (XSO leg B):** EMA9.

| ID | Entry | Exit |
|---|---|---|
| S12-01 | stop | XM |
| S12-02 | stop | X2R |
| S12-03 | stop | XSO |
| S12-04 | close | XM |
| S12-05 | close | X2R |
| S12-06 | close | XSO |

**Neighbour:** pole threshold 2.0 × σ_tod × √bars.

## Study 9: monitors and paper log

No statistical test. See the plan.
