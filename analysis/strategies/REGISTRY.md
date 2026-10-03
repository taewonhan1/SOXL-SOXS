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

## Strategy S13: the 15-minute breakout, final rules (locked 2026-09-30, before any 2026 holdout look)

**How the rules were chosen**
- Entry filters come from the exploratory condition analysis (`orb_conditions.py`, 2019–2025).
- Stops, targets and trade management were chosen on 2019-01-02 → 2024-09-30 only. `orb_strategy_design.py` searched 144 configurations.
- Oct 2024 – Dec 2025 was used only as a check.
- The primary rule was picked on the design sample:
  - Among configurations with the same design-sample mean, it had the smaller design drawdown.
  - Targets, break-even stop moves, a tighter (mid-range) stop and the breakout-volume filter did not improve the design sample.

**S13-A (primary).** All levels are on SOXL's regular-session 1-minute chart.
1. **Range:** H and L = the high and low of bars 0..14 (09:30–09:44).
2. **Trigger:** the first bar from bar 15 on that closes above H (bullish) or below L (bearish). One signal per day.
3. **Skip:** the break goes against an opening gap of more than 1%. Gap = SOXL's open ÷ its prior official close − 1, signed by the break direction, and skip if it is < −1%.
4. **Entry:** the next bar's open.
   - Bullish: buy SOXL.
   - Bearish: buy SOXS if its unadjusted prior close is ≥ $10; otherwise skip.
   - A SOXS exit mirrors the SOXL chart as in §0.
5. **Stop:** L for bullish trades, H for bearish trades.
6. **Time stop:** at the close of bar 89 (11:00), exit at the next bar's open if the trade is not in profit on SOXL's chart. Trades entered after 11:00 are unaffected.
7. **Exit:** otherwise at the open of bar n_min − 5 (15:55, or 12:55 on half-days). No profit target and no stop moves.

**S13-B (secondary):** S13-A without the time stop (step 6).

**Holdout test** (one time, only when the user asks): 2026-01-02 → 2026-09-25, case B.
- S13-A passes if its mean net per trade is ≥ 0. S13-B is reported alongside, with S3-01 and S8-01 as references.
- Case Q (real NBBO fills) is computed for the holdout trades.
- Forward paper trading of S13-A and S13-B starts 2026-09-28 (`paper_log.py`).

**Reference, design and check periods** (case B, 2019–2025, bearish via SOXS):
- S13-A: +25 / +40 / +60 bps per trade in pre / dev / val. Win rate 40%, max drawdown −48% of one position.
- S13-B: +29 / +40 / +51. Win rate 48%, max drawdown −62%.

## Strategy S14: best-combination breakout (registered 2026-09-30, before the 2011–2018 test)

**How it was picked**
- `orb_best.py` searched 480 combinations on 2019-01-02 → 2025-12-31, using a rule fixed in its docstring before running:
  - keep combinations averaging at least 60 trades a year;
  - take the highest worst-period mean net per trade across pre, dev and val;
  - break ties by pooled t.
- Combinations:
  - range: 15, 20 or 30 minutes;
  - filter: none, gap, pre-market, gap + volume, or pre-market + volume;
  - stop: at the range, or at the range capped at 4%;
  - time stop: none, 10:30, 11:00 or 12:00;
  - exit: hold, or half off at 2R;
  - bearish execution: SOXS or short SOXL.
- 2011-06-01 → 2018-12-31 has not been used by any rule. The 2026 holdout stays sealed.

**S14-A (the pick):** `15|PM|CAP4|1200|HOLD|SOXS`. All levels are on SOXL's regular-session 1-minute chart.
1. **Range:** H and L = the high and low of bars 0..14 (09:30–09:44).
2. **Trigger:** the first bar from bar 15 on that closes above H (bullish) or below L (bearish). One signal per day.
3. **Filter:** trade only if SOXL's last pre-market trade (04:00–09:29) was above its prior official close for an up-break, or below it for a down-break. A day with no pre-market trade gets no trade.
4. **Entry:** the next bar's open.
   - Bullish: buy SOXL.
   - Bearish: buy SOXS if its unadjusted prior close is ≥ $10; otherwise skip.
5. **Stop:** the other side of the range, but never more than 4% from the SOXL entry price.
6. **Time stop:** at the close of bar 149 (12:00), exit at the next bar's open if the trade is not in profit on SOXL's chart.
7. **Exit:** otherwise at the open of bar n_min − 5 (15:55). No target and no stop moves.

**S14-B (high win rate):** `20|PM|RNG|none|HOLD|SOXS`. This is S14-A with a 20-minute range (bars 0..19), the stop at the other side of the range with no cap, and no time stop.

**Results on the search data** (2019–2025, case B):

| Rule | Trades a year | Win rate | Net bps per trade (pre / dev / val) | Pooled t | Max drawdown |
|---|---|---|---|---|---|
| S14-A | 103 | 44% | +46 / +47 / +56 | 3.65 | −39% |
| S14-B | 102 | 51% | +41 / +38 / +41 | 2.80 | −57% |

**Deep test (run once, next):**
- Window: 2011-06-01 → 2018-12-31, case B, with SOXL/SOXS spreads measured from NBBO samples for those years (2–3× today's).
- Reported: S14-A, the next four combinations, S14-B, and the baselines S3-01 (unfiltered) and S13-A.
- S14-A **holds up** if its mean net per trade is > 0 and at least 5 of the 8 calendar years (2011 partial) are positive.

**Deep-test outcome (2011-06-01 → 2018-12-31, run once on 2026-09-30):** S14-A did **not** hold up.

| Rule | Mean net per trade | t | Positive years |
|---|---|---|---|
| S14-A | −16 bps | −1.5 | 2 of 8 |
| S14-B | −5 bps | — | 3 of 8 |
| S3-01 | −12 bps | — | 0 of 8 |
| S13-A | −16 bps | — | 1 of 8 |

Details: RESULTS.md and `orb_best/`.

## Final strategy S15 and the one-time 2026 holdout test (registered 2026-09-30, before the holdout is opened)

**Why this definition:** the independent 2011–2018 test showed that the filters and exits picked on 2019–2025 did not generalise. The final strategy is therefore the plain rule, plus a kill switch.

**S15 (primary) = S3-01 exactly.** All levels are on SOXL's regular-session 1-minute chart.
1. H and L are the high and low of bars 0..14.
2. The trigger is the first bar from bar 15 on (up to bar n_min − 7) that closes above H or below L. One signal per day.
3. Entry at the next bar's open.
   - Bullish: buy SOXL.
   - Bearish: buy SOXS if its unadjusted prior close is ≥ $10; otherwise skip.
4. The stop is the other side of the range: L for bullish, H for bearish (SOXS mirrored).
5. Exit at the open of bar n_min − 5 (15:55). No filters, no time stop, no target, no stop moves.

**S15-K (secondary) = S15 plus a kill switch.**
- Take signal i only if the mean case-B net result of the previous 60 S15 signals, counted whether traded or not, is > 0.
- Signals are always tracked, even while the switch is off, so the switch can turn back on.

**Holdout test.** Run once: 2026-01-02 → 2026-09-25, all trades whose date falls in that window.
- **Primary: S15.** It passes if its case-B mean net per trade is ≥ 0 **and** its case-Q mean net is ≥ 0. Case Q uses real NBBO fills for entries and exits.
- **Also reported, for context only** (they do not change the verdict): S15-K, S8-01, S4-02, S4-04, S13-A and S14-A.
- **Reported alongside:** trades, win rate, t, results by month, and the share of trend, medium and quiet days in 2026.

**Holdout outcome (opened once on 2026-09-30):** S15 **FAIL**.

| Rule | Trades | Win rate | Case B net per trade | t | Case Q net per trade |
|---|---|---|---|---|---|
| S15 | 143 | 43% | −1.9 bps | −0.06 | −1.3 bps |
| S15-K | 60 | 37% | −65 bps | — | — |

Context rules, case B net per trade: S8-01 −19, S4-02 +3, S4-04 +6, S13-A −9, S14-A −7. Details: `holdout_2026/`.

## Strategy S16: midday trend continuation (registered 2026-09-30; the forward paper log is its test)

All levels are on SOXL's regular-session 1-minute chart.
1. **Check** at the close of the 10:59 candle (11:00): SOXL's move from its 09:30 open.
2. **Entry** at the 11:00 candle's open.
   - If the move is ≥ +3%, buy SOXL.
   - If the move is ≤ −3%, buy SOXS, if its prior close is ≥ $10; otherwise skip.
3. **Stop:** exit if SOXL trades back to its 09:30 opening price.
4. **Exit:** otherwise at the 15:55 candle's open.

**Evidence** (`scripts/research/midday_trend.py`, `midday_trend/`)
- A 24-cell grid was fixed before running and every cell is reported: check time 11:00 / 12:00 / 13:00, move 2 / 3 / 4 / 6%, stop none or at the open. It was run on 2011-06 → 2018, 2019 → 2025 and 2026-01 → 09 at once.
- **All 24 cells, averaged:** +12 / +7 / +10 bps per trade by era. 71% / 88% / 58% of cells are positive. Before costs: +29 / +15 / +14.
- **This cell:** +12.9 / +20.4 / +18.0 bps per trade (t 0.8 / 1.2 / 0.4). Win rate 52% / 53% / 56%. 45 / 66 / 87 trades a year. Pooled: +17 bps over 866 trades.

**Status**
- No untouched history is left for this rule family.
- The test is the forward paper log from 2026-09-28. Judge it after 60 trades.

## Study T1: early trend-day detector (registered 2026-10-03, before any of its new data is downloaded)

**Purpose:** find which combination of early-session data elements best separates real trend days from false starts, so the day's side can be chosen early.

**Signals.**
- Every session from 2011-06-01 to 2026-09-25, at two check times: 09:45 (close of bar 14) and 10:00 (close of bar 29). Each check time is analyzed separately.
- A signal exists when SOXL is at least 1.0% from its 09:30 open at the check. The direction s is the sign of that move.

**Targets.**
- **T1:** a trend day in direction s, meaning SOXX open→close × s ≥ 2%.
- **T2:** the trade result, in R = net % ÷ 1.5.
  - Enter at the next bar's open in direction s. Up moves buy SOXL; down moves buy SOXS if its prior close is ≥ $10.
  - Fixed 1.5% stop from the entry price on SOXL's chart.
  - Exit at 15:55. Case B costs.

**Stage-1 flags** (known at 09:30, direction-free; the score is their count, 0–5):
1. **vol_hot:** SOXL's median daily range over the prior 20 sessions ÷ its median over the prior 250 sessions ≥ 1.2.
2. **yday_trend:** the previous session's SOXX |open→close| ≥ 2%.
3. **qqq_below:** QQQ's prior close is below its 50-day average.
4. **big_gap:** |SOXL open ÷ prior close − 1| ≥ 0.5 × SOXL's prior 20-day median daily range.
5. **open_outside:** SOXL's 09:30 open is above the prior session's regular-hours high or below its low.

**Stage-2 inputs** (at check bar b; each oriented so that higher supports direction s):

| Input | Definition |
|---|---|
| I1 scaled_move | \|move\| ÷ median \|move at bar b\| over the prior 20 sessions |
| I2 gap_agree | 1 if the opening gap's sign equals s, else 0 |
| I3 path_clean | \|c_b − o_0\| ÷ Σ_{i=0..b} \|c_i − c_{i−1}\|, with c_{−1} = o_0 |
| I4 vwap_side | Share of bars 5..b whose close is on the s side of the session VWAP |
| I5a flow_tick | Tick-rule signed dollar volume of SOXL trades from 09:30:00 to the check ÷ total dollar volume, × s |
| I5b flow_bar | Σ sign(c_i − c_{i−1}) × v_i ÷ Σ v_i over bars 0..b, × s |
| I6a breadth | Share of the member list moving with sign s from its own 09:30 open at bar b |
| I6b leaders | Share of NVDA, AVGO, AMD and TSM moving with sign s |
| I7 vix | −s × VIXY's move from its 09:30 open at bar b (%) |
| I8 semis_vs_qqq | s × (SOXX move − QQQ move) at bar b (%) |
| I9 level | +1 if SOXL traded beyond the prior session's high (s = +1) or low (s = −1) and the last 5 one-minute closes (b−4..b) are all beyond it; −1 if it traded beyond it but the close at b is back inside; 0 otherwise |

- **Member list** (fixed; 23 long-lived U.S.-listed semis and ADRs): NVDA, AVGO, AMD, INTC, QCOM, TXN, MU, AMAT, LRCX, KLAC, ADI, MRVL, NXPI, MCHP, ON, SWKS, TER, TSM, ASML, MPWR, ENTG, LSCC, STM.
  - Only members with valid data that day count toward breadth.
  - The list holds only survivors, which is a known approximation of the index's changing membership.

**Protocol.**
- **Train / test split:** train on 2019-01-02 → 2025-12-31. Test on 2011-06-01 → 2018-12-31 and on 2026-01-02 → 2026-09-25. All terciles and thresholds come from the training data only.
- **A. Univariate:** for each input, the T1 rate and mean T2 by training tercile (continuous inputs) or by value (discrete inputs), in all three eras. Reported in full.
- **B1. Additive combinations:**
  - Each input's favorable state is the top training tercile (continuous) or value 1 (I2; I9 = +1). The score is the count of favorable inputs in a subset.
  - Search all subsets of size 1–5 of the 10 stage-2 inputs (I5a and I5b count separately; 637 subsets), each with thresholds score ≥ 1..size, with and without requiring a stage-1 score ≥ 2.
  - A rule needs at least 10 signals a year in training. The rule with the highest training mean R is selected and evaluated once on the test eras. The top 10 training rules are also reported with their test results.
- **B2. Logistic model:** L2-regularized logistic regression of T1 on all stage-2 inputs plus the stage-1 flags, standardized and fitted on training.
  - Reported: test AUC, and the mean R of signals whose predicted probability is in the training top third.
- **B3. Baselines:**
  1. All signals (move ≥ 1%).
  2. Move plus gap: I1 in its top tercile and I2 = 1.
  3. The cascade's early rules: 09:45 2–3% with the gap; 10:00 3–4% with the gap.

**Success:**
- The B1-selected rule or the B2 model must beat baseline 2 in both test eras on both mean R per trade and trend-day share.
- Its mean R must be > 0, with at least 10 trades a year.

**Data downloaded after registration:**
- Adjusted 1-minute bars from 2010-06 to 2026-09 for VIXY and the members.
- SOXL trades from 09:30:00 to 10:00:00 ET for every session, aggregated per minute: tick-rule signed shares and dollars, odd-lot shares, block (≥ $250k) signed dollars, and off-exchange shares. The block and off-exchange fields are stored for later work and are not part of this search.
