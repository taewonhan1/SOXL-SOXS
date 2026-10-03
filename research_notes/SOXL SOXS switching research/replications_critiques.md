# Independent replications, out-of-sample tests and critiques: intraday momentum, opening-range breakout (ORB) and leveraged-ETF switching strategies

*Notes compiled 2026-10-03. **Access limits:** the egress proxy blocked many relevant domains: mql5.com, danfin.net, quantconnect.com, paperswithbacktest.com, cxoadvisory.com, quantitativo.com, newsletter.huntgathertrade.com, *.substack.com, arxiv.org, mdpi.com, diva-portal.org, efmaefm.org, cmtassociation.org and composer.trade. Findings from those pages come from search-result snippets and are marked **(snippet)**. GitHub was reachable, so the GitHub replications were read in full from their README and report files. The session's web-search budget (200 of 200) ran out before a few attributions could be cross-checked. Those are marked **(attribution unverified)**. Dates for GitHub repositories come from GitHub's API (created/updated).*

---

## 1. Zarattini & Aziz (2023) 5-minute ORB on QQQ/TQQQ: what independent replications found

### Takeaway
Independent replications reproduce the paper's gross result almost exactly (Sharpe 1.06 vs 1.12; +0.131R vs +0.13R). The edge sits inside the bid-ask spread, though. Net PnL hits break-even at about 2.2¢/share of entry slippage on QQQ. At $0.02/share the Sharpe falls to 0.23. Across five index CFDs over 2015–2026, net returns are indistinguishable from zero. The one component that survives costs (an NQ pre-market confirmation filter) makes 76% of its PnL in 2022 alone.

### Cited Findings
**Original claim (baseline for comparison)**
- The paper was first posted 2023-04-10 (SSRN 4416622) and covers 2016–2023. It reports an annualized alpha of 33% net of commissions on QQQ. The TQQQ version returned 1,484% over 2016–2023, against 169% for QQQ buy-and-hold — [SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622)
- The paper's fill assumption is quoted as "we assumed no slippage in fills" and called "the single load-bearing input behind its headline result" — [giovannibrusco/zarattini-2023-orb-qqq README (created 2025-10-10, updated 2026-09-30)](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)

**giovannibrusco/zarattini-2023-orb-qqq (GitHub; created 2025-10-10, last updated 2026-09-30)**
- **Data and rules.** QQQ 5-minute bars, Jan 2016 to Feb 2023, $25,000 starting capital. The trade goes long or short in the direction of the 09:30–09:35 bar, enters at 09:35, stops at the other side of that bar, and exits at +10R or the close. Position size is min(1% equity / $R, 4 × equity / entry) — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Replication with no slippage.** 1,775 trades (paper: 1,795), Sharpe 1.06 (paper: 1.12), net PnL $138,639, CAGR 30.4%, max drawdown 22.4%, gross $0.070/share, per-trade t-stat 1.79 — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **With costs.** Adding $0.02/share entry slippage and $0.04/share stop slippage gives net PnL $4,860, t 0.52, Sharpe 0.23, CAGR 2.7% and max drawdown 43.9% — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Break-even slippage.** "net PnL crosses zero at ~2.2¢/share" of entry slippage, with stop slippage modeled at 2×. The author adds: "Since QQQ's bid-ask spread is ~1¢, this is not a comfortable margin — it is an edge that survives or dies on execution quality" — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **How trades exit.** The +10R target is hit on only about 2–3% of trades. About 75% exit at the stop and about 22% go flat at the close: "In practice this is intraday momentum-continuation with a 1R stop" — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **NQ 09:25 confirmation filter (after slippage).** 844 trades, $0.125/share, t = 2.05, Sharpe 0.77, CAGR 15.6%, max drawdown 31.1%. A placebo using QQQ's own 09:25 bar gave $0.079/share, t = 1.27 (not significant), Sharpe 0.57 — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **No strategy-level edge over buy-and-hold is established.** The filtered strategy's Sharpe is 0.77, against 0.72 for QQQ buy-and-hold (CAGR 15.3%, max drawdown 35.6%). Their bootstrap 95% confidence intervals overlap: [0.05, 1.41] vs [−0.03, 1.47]. Final equity was $69k for the filtered strategy after slippage, $69k for QQQ buy-and-hold, and $164k for the no-slippage replication — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Depends on one regime.** "2022 alone is 76% of the filtered PnL (and 38% of the replication)." The filter loses money in 2017, 2020 and early 2023, and "the sharp 2023 drawdown also hints the edge was already decaying" — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Limitations the author states.** The filter was selected in-sample. There is no data after Feb 2023. Stop slippage is flat. The author also notes a conflict of interest (the original authors run day-trading education businesses) and that "published ORB results are known to concentrate in 2020–2022 — which this replication independently confirms" — [README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)

**mql5 blog, "The opening-range breakout paper, replicated on five indices: gross reproduced, net zero" (2026-09-25) (snippet)**
- The rule was tested unchanged on NQ, SPX, Dow, DAX and FTSE CFDs, using cash sessions from Jan 2015 to Jun 2026, with 2,899–2,937 sessions per market — [mql5 blog](https://www.mql5.com/en/blogs/post/776235)
- The snippet text reads: "Gross yes: +0.131 R on NQ, matching the paper's results. Net no: no market is distinguishable from zero, with four of five markets showing negative returns." The post notes the original "charged commission but no spread and no slippage, and had no out-of-sample period." The snippet may paraphrase the post — [mql5 blog](https://www.mql5.com/en/blogs/post/776235)

**danfin.net, "Opening Range Breakout Research: What Two Day-Trading Papers Actually Found" (undated) (snippet)**
- The post cites this paper as "Zarattini & Aziz, 2025". It says the direction of QQQ's first five minutes historically continued "under a low win rate with large occasional winners and heavy dependence on leverage." It also says "the Nasdaq-ETF model assumes no slippage, and its 9,350% variant comes from a parameter search," and that neither paper tests NQ futures, US100 CFDs or a prop-firm evaluation — [danfin.net](https://danfin.net/opening-range-breakout-research)

**paperswithbacktest, "ORB Trading Strategy: What Replication Shows" (undated) (snippet; attribution unverified)**
- A search-result summary of the ORB replication sources reported that, "replicated on common data across 2010–2026, the strategy produced a full-sample Sharpe ratio of −0.06, with a Sharpe of −0.84 in the out-of-sample period after publication." The same summary said ORB trades about 250 round trips a year, so "at realistic 2–4 basis points per round trip in a liquid ETF, that consumes 5–10% of capital annually in frictions alone." This page is the most likely origin, but it was blocked and the attribution could not be verified — [paperswithbacktest](https://paperswithbacktest.com/strategies/orb-trading-strategy)

**Mesfin, "Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures: A Systematic Falsification Study" (SSRN 6709401 / arXiv 2605.04004, Apr–May 2026) (snippet)**
- The study tests 14 common OHLCV intraday signal families on MNQ. None passes all five tests at once: walk-forward out-of-sample, T ≥ 2.0, N ≥ 30, positive net return after a fixed 2-point round-trip friction, and consistency across years. The largest gross edges are about 0.07–1.50 points per trade, below the assumed cost — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6709401); [arXiv](https://arxiv.org/pdf/2605.04004)
- An ORB long entered at bar+15 (opening range 09:30–09:55, six 5-minute bars) gave T = 0.88 on 447 out-of-sample trades, mean net +2.82 points. By year: +2.43 in 2023, +7.04 in 2024, +15.05 in part of 2025 — [arXiv (snippet)](https://arxiv.org/pdf/2605.04004)
- Two other signals serve as positive controls showing the method can detect a real edge: RTH Confluence (T = 5.83, N = 538) and London Session Signal B (T = 5.15, N = 289) — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6709401)

**CXO Advisory (paywalled/blocked)**
- CXO reviewed the April 2023 QQQ 5-minute ORB paper in "Day Trading with an Opening Range Breakout Strategy" (review date not visible) — [CXO](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/). A search-result summary of CXO pages carried CXO's general caution: "Intraday return patterns are not very reliable, and average return variations are very small compared to probable costs of exploitation." Which CXO page this comes from is uncertain; it is probably one of its intraday-behavior studies — [CXO](https://www.cxoadvisory.com/calendar-effects/recent-intraday-u-s-stock-market-behavior/)

**Other GitHub replications without numbers in their READMEs**
- alfredoberlose: QQQ 2016–2024 with $0.0005/share commission. Results are shown only as a chart — [repo (created 2025-05-27)](https://github.com/alfredoberlose/ORB-Day_Trading_Strategy-QQQ)
- nicholas-campeti: replication with dynamic slippage, using IBKR and Databento data. The README states no numbers — [repo (created 2026-02-19)](https://github.com/nicholas-campeti/Can-Day-Trading-Really-Be-Profitable-Analysis-and-Optimization)

### Inferences
- The headline result depends on assuming zero slippage. A gross edge of $0.07/share on QQQ, which traded at very roughly $100–$400 over 2016–2023, is only a few basis points per trade. That is about the size of one or two QQQ spreads plus stop slippage.
- The TQQQ "1,484%" figure applies 3× leverage to the same thin per-trade edge. Leverage does not create edge, and the per-share costs of a cheaper, more volatile 3× product are a larger share of price.
- **Arithmetic for SOXL/SOXS (not sourced data):** a 1¢ tick is 4 bps on a $25 share and 2.5 bps on a $40 share, but only about 0.25 bps on a $400 QQQ share. An ORB edge of a few bps per trade on QQQ would therefore need to be several times larger in bps on SOXL to survive one tick of slippage per side.
- The mql5 result (net zero on 5 markets, 2015–2026), the unverified −0.84 post-publication Sharpe, and the dependence on 2022 together suggest the published result is mostly a 2020–2022 high-volatility-regime effect. It does not look like a structural edge.

### Gaps
- I could not read in full a post-publication (2023–2026) QQQ/TQQQ replication that includes costs. The mql5, paperswithbacktest and danfin pages were blocked, so their numbers are snippet-level.
- I found no replication of the TQQQ variant that models realistic TQQQ spreads and stop slippage.
- The "9,350%" variant (danfin) and the "Zarattini & Aziz, 2025" publication date could not be verified.
- The CXO review's own critique text is paywalled or blocked.

---

## 2. Zarattini, Barbon & Aziz (2024) "stocks in play" ORB: what replications found

### Takeaway
The paper's own data show that a plain 5-minute ORB applied across the market is weak (Sharpe 0.48, below the S&P 500). Almost all of the reported edge comes from restricting trades to the 20 stocks with the highest opening relative volume. Independent replications do find a large in-sample edge, but they are thin or biased:
- QuantConnect published only one year (2016).
- A GitHub replication shows the result is dominated by modeling choices. The intra-bar fill order alone swings the Sharpe by 6.39.
- It also has survivor bias, and its live paper trading saw stop slippage of 3–5R on gap-throughs.

No clean post-publication (2024–2026) test with realistic costs was found.

### Cited Findings
**Original claim (baseline)**
- The paper was posted in Feb 2024 (SSRN 4729284) and covers more than 7,000 US stocks over 2016–2023. Restricting to Stocks in Play produced "more than 1,600% in total net return... a Sharpe ratio of 2.81 and an annualized alpha of 36%," against 198% for the S&P 500. A plain 5-minute ORB applied across the market gave "about 3.2% annual return, roughly 6.6% annualized volatility, and a Sharpe ratio of 0.48, which underperforms the S&P 500 benchmark" — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284); [Concretum Group](https://concretumgroup.com/a-profitable-day-trading-strategy-for-the-u-s-equity-market/)
- **Selection filters.** Opening price above $5. Average daily volume of at least 1,000,000 shares over the last 14 days. 14-day ATR above $0.50. Opening-range relative volume of at least 100% and among the top 20 — [CXO review "Intraday Trading of Overactive Stocks via Opening Range Breakout" (snippet)](https://www.cxoadvisory.com/individual-investing/intraday-trading-of-overactive-stocks-via-opening-range-breakout/)
- danfin summarizes the paper's own finding: "a plain ORB was weak, and that selecting the day's most unusually active stocks by opening relative volume did almost all the work" — [danfin.net (snippet)](https://danfin.net/opening-range-breakout-research)

**QuantConnect research post #18444, "Opening Range Breakout for Stocks in Play" (date not visible; blocked) (snippet)**
- The post reports a Sharpe of 2.396 and beta of −0.042 from a backtest covering 2016 only, on a universe of 1,000 liquid stocks trading the 20 most "in play" names. SPY's Sharpe that year was 0.836 — [QuantConnect (snippet)](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/)
- A GitHub issue summarizing that post notes no CAGR, drawdown or out-of-sample test was reported, and that 2017–2023 were missing. Citing "community feedback," it says fees consume about 25% of PnL and the win rate is 17% — [jsboige/CoursIA issue #16355](https://github.com/jsboige/CoursIA/issues/16355)

**hsaeed22058/strategy-backtest (GitHub; created 2026-07-23): a replication that switches each bias control on and off and measures it**
- **Data.** 259 US equities from 2016-01 to 2026-05. Intraday 5-minute bars come from a single venue (IEX via Alpaca); daily data come from Yahoo — [README](https://github.com/hsaeed22058/strategy-backtest)
- **Replication of the paper's rules.** Sharpe 2.98, or 2.72 after correcting a split-adjustment bug (paper: 2.81). The stop-fill stress assumption alone is "worth 1.52 Sharpe"; without it the run is 4.50. The standard error of a Sharpe near 3 over ten years is about ±0.7 — [README](https://github.com/hsaeed22058/strategy-backtest)
- **Sharpe progression as controls are added (bigger edge, but with heavy caveats).** Adding exit variants and picking the best with hindsight gives 15.54. Removing the benefit of the doubt inside each bar gives 8.54. Walk-forward selection gives 9.80. Point-in-time S&P 500 membership plus walk-forward gives 7.33 (7.28 after the split correction). Returns are measured on a fixed $25k risk base without compounding — [README](https://github.com/hsaeed22058/strategy-backtest)
- **Fragile to modeling choices.** "Intra-bar ordering is worth 6.39 Sharpe of the 6.99 drop," while 2 bp exit slippage plus 25 bp borrow is worth only 0.61. "Which order a 5-minute bar visited its own high and low is a bigger modelling decision than the entire cost stack" — [README](https://github.com/hsaeed22058/strategy-backtest)
- **A data bug that drove most of the profit.** Daily bars were split-adjusted but intraday bars were not, so 4.3% of trades (1,797) had stops sized off an ATR up to 40× too small. Those trades "produce 63% of total R" — [README](https://github.com/hsaeed22058/strategy-backtest)
- **Live execution evidence.** "A later live paper-trading deployment of this strategy saw stop-market fills in thin names slip **3 to 5 R** past the stop on gap-throughs — far worse than modelled" (the model assumed 10–25% of R) — [README](https://github.com/hsaeed22058/strategy-backtest)
- **Survivor bias.** The ticker list was "assembled in 2026 from names Yahoo still served." Only 9 of the 148 names that left the index between 2016 and 2025 are present. The author calls this "the single largest remaining bias." A broader Russell-3000-scale run reached Sharpe 10.79 but "carries the identical currently-listed-only caveat" — [README](https://github.com/hsaeed22058/strategy-backtest)

### Inferences
- The robust finding is that the ORB signal by itself is weak (Sharpe 0.48 market-wide, per the paper). Any edge depends on catalyst-driven, abnormal-volume stocks. This mechanism does not carry over to a single pair of leveraged ETFs such as SOXL/SOXS, which are not "stocks in play" chosen from a cross-section.
- Sharpe ratios of 3 to 15 on 5-minute bars are mainly measurements of assumptions: intra-bar ordering, stop fills, survivor bias and split handling. A single live paper-trading observation of 3–5R stop slippage on gap-throughs is direct evidence that bar-based backtests overstate this strategy.

### Gaps
- I found no independent post-publication (2024–2026) test with a full delisting-inclusive universe and realistic costs.
- QuantConnect's full post, and whether it later extended beyond 2016, could not be read.
- I found no independent break-even slippage figure (cents or bps per share) for stocks-in-play ORB.

---

## 3. Zarattini, Aziz & Barbon (2024) "Beat the Market" SPY noise-area momentum: what replications found

### Takeaway
This is the best-replicated of the three Concretum papers. Several independent code bases reproduce the in-sample Sharpe of about 1.1–1.34 with the paper's costs. All rigorous post-publication tests show sharp decay:
- PazSheimy: out-of-sample Sharpe 0.39 (May 2024 – Mar 2026), against 1.34 in-sample.
- codecat-ops: a frozen out-of-sample period from 2024 gave Sharpe 0.16. Calendar 2025 had a Sharpe of −0.27 and 2026 to date −1.91.
- The ES-futures version had a Sharpe of −0.07 from May 2024 to Jul 2026.

Parameter optimization (Maróy 2025, Sharpe > 3 claimed) and walk-forward re-selection do not rescue it. The strategy was strong over 2020–2024, including a +25.8% return in 2022 while SPY fell 19.5%.

### Cited Findings
**Original claim (baseline)**
- The paper (SSRN 4824172, 2024-05-10) reports a 1,985% total return, 19.6% annualized, and Sharpe 1.33 over 2007–2024 — [Maróy SSRN abstract page (snippet)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349). Other reported figures are 14.3% volatility, a 43% hit ratio and a 25% max drawdown — [PazSheimy README](https://github.com/PazSheimy/spy-intraday-momentum-oos)
- **Rules.** The noise area is the open ± the 14-day average absolute move from the open at each minute, anchored to the previous close to handle gaps. Signals are checked every 30 minutes from 10:00 to 15:30. Exit is a trailing stop at the band or VWAP, and the position is flat at the close. Size targets 2% daily volatility, capped at 4× — [patrickobirmingham-eng/POB-CL-DT PR #13](https://github.com/patrickobirmingham-eng/POB-CL-DT/pull/13)

**PazSheimy/spy-intraday-momentum-oos (GitHub plus a working paper by Paz Serpa, 2026; created 2026-08-15, updated 2026-10-01)**
- Uses independent IQFeed 1-minute data. Costs are $0.0035/share commission plus $0.001/share slippage. The out-of-sample split is 2024-05-01 — [README](https://github.com/PazSheimy/spy-intraday-momentum-oos)
- In-sample replication (2015–2024): 19.8% annualized, 14.3% volatility, **Sharpe 1.34**, hit ratio 44.8%, max drawdown 26.2% — [README](https://github.com/PazSheimy/spy-intraday-momentum-oos)
- **Out-of-sample (May 2024 – Mar 2026):** 4.8% annualized, 14.7% volatility, **Sharpe 0.39**, hit ratio 45.0%, max drawdown 18.5%. It "underperforms SPY buy-and-hold," and "the out-of-sample decline in risk-adjusted returns is statistically significant (Sharpe test, p < 0.001)" — [README](https://github.com/PazSheimy/spy-intraday-momentum-oos)

**giovannibrusco/zarattini-2024-momentum-spy (GitHub; created 2026-07-08, updated 2026-10-01; conclusions dated 2026-07), mirrored as codecat-ops/zarattini-2024-momentum-spy**
- **SPY, 2020-07-27 to 2026-07-08 (Alpaca IEX feed; IB commission $0.0035/share, $0.35 minimum, as in the paper; baseline slippage 0).** The "final" variant returned 139.6% total, 15.89% CAGR, Sharpe 1.11, max drawdown −24.2%. Alpha was 16.7% a year (t 2.85) and beta −0.06, over 1,379 trades with a 41% win rate, payoff 1.69 and expectancy of +2.58 bps per trade. SPY buy-and-hold returned 130.5% total, 15.14% CAGR, Sharpe 0.93, max drawdown −25.4% — [validation report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md)
- **Per year (strategy vs SPY):**

| Year | Strategy | Sharpe | SPY |
|---|---|---|---|
| 2020 (partial) | +9.2% | 1.45 | — |
| 2021 | +30.6% | 2.03 | — |
| 2022 | +25.8% | 1.7 | −19.5% |
| 2023 | +29.3% | 2.0 | — |
| 2024 | +24.8% | 1.51 | — |
| 2025 | −4.9% | −0.27 | +16.3% |
| 2026 YTD | −12.9% | −1.91 | +9.3% |

  Source: [validation report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md)
- **By VIX level.** Sharpe was 2.37 when VIX < 15 (262 days), 0.5 at 15–20 (636 days), 1.35 at 20–30 (515 days), and −0.01 at 30–40 (74 days) — [validation report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md)
- **Slippage sensitivity.** At $0.000/share: Sharpe 1.11, CAGR 15.9%, expectancy 2.58 bps. At $0.005: Sharpe 1.02, CAGR 14.5%, 2.37 bps. At $0.010: Sharpe 0.94, CAGR 13.2%, 2.16 bps — [validation report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md)
- **ES futures, 2024-05-30 to 2026-07-10 (0.25-tick slippage, $0.85 commission plus $1.40 fees).** The "final" variant had Sharpe −0.07, CAGR −2.1% and max drawdown −22.7%. The "base" variant had Sharpe 0.52 and CAGR 7.8%. ES buy-and-hold had Sharpe 0.93 and CAGR 14.0%. At 1-tick slippage the "final" Sharpe is −0.27. "Costs are not the cause of the negative result (~0.4 bps/round trip at 0.25 tick): it is the signal that does not pay in this period." ES and SPY daily returns correlate at 0.97, which rules out a data-feed artifact — [ES validation report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation_es.md)
- **Maróy-style grid (27 variants, frozen protocol).** In-sample (2020-10 to 2023-12), the winner was the paper's own configuration (final/14/30) with Sharpe 1.73 and Deflated Sharpe Ratio 0.972 (N = 27; expected maximum Sharpe under the null 0.71). **Out-of-sample (2024-01-01 onward) Sharpe was 0.16**, CAGR +1.3%, expectancy −0.17 bps — [Maróy experiment report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/maroy_experiment.md)
- **Walk-forward (quarterly re-selection, 2021-10 to 2026-07).** Sharpe 0.57 (CAGR 7.9%, max drawdown −27.6%) against 0.92 (CAGR 12.7%) for the paper's fixed configuration, with 14 switches out of 19 re-selections — [walk-forward report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/walkforward_experiment.md)
- **Author's verdict.** The strategy is "a REAL strategy in the sample studied... but with an edge currently compressed to zero or below. It is NOT allocable today." The paper itself "shows multi-year weak stretches (2012-2015) followed by recovery," so "regime pause" vs "edge arbitraged away" is unresolved — [CONCLUSIONS.md](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/docs/CONCLUSIONS.md)

**Maróy (2025), "Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies" (SSRN 5095349)**
- Claims "Sharpe ratios over 3.0 and annualized returns of over 50%" using VWAP, VWAP & Ladder, and Ladder exits plus optimization of all parameters — [SSRN (snippet)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349)
- One critique says the paper "is highly optimized and only has results on 1 instrument in a short time period." This comes from a search-result summary whose source page could not be identified (possibly the Hunt Gather Trade newsletter; attribution unverified) — [Hunt Gather Trade (blocked)](https://newsletter.huntgathertrade.com/p/intraday-momentum-researched-based). Under a disciplined protocol, the 27-variant grid did not promote any optimized variant (see above).

**Quantitativo, "Intraday Momentum for ES and NQ" (undated) (snippet)**
- Heavily modified version: ES futures instead of SPY, a 90-day lookback instead of 14, a 3% daily volatility target instead of 2%, and an 8× leverage cap instead of 4×. Reports "up to 24.3% annual return on NQ futures with a Sharpe ratio of 1.67," and 22.4% when combined with ES and a long-only component — [Quantitativo](https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq)
- Its trade-level figures on ES (+2 bps per trade, 36% win rate, payoff 2.1) are cited as consistent with the GitHub replication — [validation report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md)

**Conflicting positive claim**
- AleksandarMilosavljevic/intraday-trading-strategy (created 2026-04-22) uses Alpaca SPY data from Jan 2016 to Dec 2025, adds "improvements," and states that "the final strategy realized a Sharpe Ratio of 1.34, 24% annualized return and 17% annualized volatility over the out-of-sample period." The README does not define that period, and it conflicts with the three tests above — [repo](https://github.com/AleksandarMilosavljevic/intraday-trading-strategy)

**CXO Advisory**
- Reviewed the May 2024 paper under the title "Complex Intraday Time Series Momentum Strategy Applied to SPY" (review text paywalled or blocked) — [CXO](https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/)

### Inferences
- **Break-even slippage (my extrapolation, not stated by any author).** Expectancy falls about 0.21 bps per $0.005/share step of slippage, from 2.58 bps. A linear extrapolation puts SPY break-even near about $0.06/share, or roughly 1.3 bps at a ~$450 SPY price. That is comfortably above SPY's spread, so the 2025–2026 failure is a signal failure, not a cost failure, as the ES report concludes.
- The per-trade edge (+2–3 bps on SPY) is far below one tick on a low-priced 3× ETF. The same rule on SOXL/SOXS would need a proportionally larger gross edge.
- Profile: the strategy is "long volatility" (+25.8% in 2022). It works best in trending, high-dispersion years and has failed during the 2025–2026 regime. Two years of out-of-sample data cannot separate decay from a regime pause.

### Gaps
- No replicator had 2007–2019 minute data. The paper's weak 2012–2015 stretch has not been independently reproduced.
- The Hunt Gather Trade, Quantitativo, quantmacro Substack and QuantConnect forum (thread 17091) write-ups were blocked. Their numbers and dates are snippet-level or missing.
- Concretum's own post-publication performance updates, if any exist, were not found.

---

## 4. Gao, Han, Li & Zhou (2018) market intraday momentum: did it persist out of sample?

### Takeaway
The effect generalized broadly *within* the original 1974–2020-era samples:
- 60+ futures (Baltussen et al. 2021).
- 16 developed markets, in and out of sample (Li, Sakkas & Urquhart 2022).

Tests focused on the post-publication period find it weakened or gone in US equities:
- Rosa (2022): "predictability disappears in the out-of-sample period" and depends on regime.
- Zhang & Hua (2024): intraday momentum and overnight effects "have diminished over time."
- An EFMA 2024 paper: the US last-half-hour pattern is about 75% weaker out of sample.
- Mesfin (2026): no OHLCV intraday signal on MNQ clears realistic friction.

The original economic size was small: a timing Sharpe of 1.08 on about 6.7% a year *before costs*.

### Cited Findings
**Original result**
- SPY from 1993-02-01 to 2013-12-31. The first half-hour return (measured from the previous close to 10:00) predicts the last half-hour return. Predictability is stronger on more volatile days, higher-volume days, recession days and some macroeconomic announcement days — [SSRN 2440866](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866); [JFE 129(2), 2018](https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351)
- Predictive R² is 1.6% in-sample and 1.4% out-of-sample. The timing strategy averages 6.67% a year with 6.19% standard deviation, a Sharpe of 1.08, against 0.29 for daily buy-and-hold. These figures are before transaction costs — [Market Intraday Momentum (ResearchGate)](https://www.researchgate.net/publication/325364670_Market_Intraday_Momentum)

**Generalizations across instruments and countries**
- Baltussen, Da, Lammers & Martens, JFE 142(1), Oct 2021: across "over 60 futures on equities, bonds, commodities, and currencies between 1974 and 2020," they find "strong market intraday momentum everywhere." The last 30 minutes is predicted by the rest-of-day return, and the effect "reverts over the next days." They tie it to gamma hedging by options market makers and by leveraged ETFs — [SSRN 3760365](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365); [author PDF](https://www3.nd.edu/~zda/intramom.pdf)
- Li, Sakkas & Urquhart, Journal of Financial Markets 57 (2022), article 100619: across 16 developed markets, intraday time-series momentum "is economically sizable and statistically significant both in- and out-of-sample in most countries." It is stronger when liquidity is low, volatility is high and new information is discrete — [University of Birmingham record](https://research.birmingham.ac.uk/en/publications/intraday-time-series-momentum-global-evidence-and-links-to-market/); [accepted version](https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf)
- Pacific-Basin Finance Journal 80 (2023) 102086, on APAC markets: there is "some evidence of intraday momentum in individual stocks" but "weak predictability compared to larger markets such as the U.S." Where the effect exists, it "tends to be weaker in the COVID-19 crisis period, especially for the Chinese market." This is from a search summary; the attribution to this APAC paper is inferred from the result list — [Monash open-access PDF (snippet)](https://researchmgt.monash.edu/ws/files/519509174/494419119_oa.pdf)

**Decay and out-of-sample failures**
- Rosa, Journal of Futures Markets 42(12), Dec 2022, pp. 2218–2234, studies the out-of-sample performance of the variant where the overnight return predicts the last half-hour. "The predictability disappears in the out-of-sample period." A Markov-switching model finds two regimes, with predictability depending on signal strength. "Assessing return predictability in calendar time may lead to false conclusions," and a threshold strategy beats an always-on one — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375); [EconPapers](https://econpapers.repec.org/RePEc:wly:jfutmk:v:42:y:2022:i:12:p:2218-2234)
- Zhang & Hua, "Market Predictability Before the Closing Bell Rings," *Risks* 12(11), Nov 2024: using Bayesian regression with Student-t errors on the US market's last 30 minutes, they find "well-studied factors such as overnight effects and intraday momentum have diminished over time." New factors such as "lunchtime returns during boring days" are significant instead — [MDPI (snippet)](https://www.mdpi.com/2227-9091/12/11/180); [DOI](https://doi.org/10.3390/risks12110180)
- "Interday Cross-Sectional Momentum: Global Evidence and Determinants" (EFMA 2024 Lisbon): "comparing the last half-hour U.S. evidence from 2010 to out-of-sample evidence, the strength of the pattern has weakened by about 75%," though "the pattern is still present in the U.S., albeit weaker than in previous studies." The exact comparison periods could not be verified (snippet) — [EFMA PDF](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/Interday_Cross_Sectional_Momentum.pdf)
- Mesfin (2026), on MNQ futures: none of 14 OHLCV intraday signal families clears walk-forward out-of-sample testing plus a 2-point round-trip friction. Gross edges are 0.07–1.50 points per trade — [SSRN 6709401](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6709401)

### Inferences
- The *mechanism* evidence (gamma and leveraged-ETF rebalancing flows into the close) is strong and has wide coverage up to 2020. *Tradability* evidence after 2013 in US equities points to decay. The original pre-cost Sharpe of 1.08 came from a very small daily signal (R² of about 1.6%), so even modest costs or decay can erase it.
- Because Baltussen et al. tie the effect partly to leveraged-ETF hedging flows, the effect is a mechanism to *monitor* in SOXL/SOXS (end-of-day rebalancing) rather than a reliable standalone signal. Rosa's regime finding suggests any use should be conditioned on high-volatility or strong-signal days.

### Gaps
- I found no paper or blog that reports net-of-cost results for the exact Gao et al. SPY rule on 2014–2026 data. The diva-portal and Klagenfurt theses and the TapeScript and harbourfrontquant blogs were blocked.
- Found by title only, not read: "Delta-hedging demand and intraday momentum: Evidence from China" ([Physica A 2022](https://ideas.repec.org/a/eee/phsmap/v600y2022ics0378437122003624.html)); "End-of-Day Reversal" by Baltussen, Da & Soebhag ([PDF](https://www3.nd.edu/~zda/EOD.pdf)), whose title suggests a reversal pattern at the close in recent data; and "Intraday momentum in the VIX futures market" ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426622003260)).

---

## 5. Daily leveraged-ETF switching rules: replications and critiques (Gayed & Bilello 200-day MA; Composer TQQQ FTLT; RSI mean reversion on 3× ETFs)

### Takeaway
- **Gayed & Bilello's 200-day MA rule** replicates as a *drawdown reducer*. Post-publication and out-of-universe tests show it usually does not beat buy-and-hold on return.
  - A pre-registered 2026 test on 18 new ETFs: "No arm passes." The trend filter cut drawdowns on all 18 but lowered returns on 13.
  - Post-publication US (2016–26): 12.8% vs 14.1% for buy-and-hold.
  - A RealTest replication on TQQQ: the 200-day filter cut max drawdown from −81.6% to −57.2%, but ending wealth fell from $3.96M to $1.12M because of whipsaw.
- **Composer FTLT-style symphonies** publicize "out-of-sample" returns of 50–120% a year. Those figures are platform-computed since-creation statistics from 2022–2025 bull markets, with obvious selection bias. I found no independent rigorous replication.
- **RSI mean reversion on 3× ETFs:** I found no rigorous independent out-of-sample study, only vendor and blog backtests.

### Cited Findings
**Gayed & Bilello (2016), "Leverage for the Long Run" (2016 Charles H. Dow Award)**
- **Rule.** Hold the leveraged S&P 500 when it is above its 200-day SMA. Otherwise rotate to T-bills — [CXO review (snippet)](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/); [original PDF (blocked)](https://cmtassociation.org/wp-content/uploads/2025/08/2016-gayed-bilello.pdf). The Dow Award is confirmed by [setup4alpha (snippet)](https://setup4alpha.substack.com/p/tested-award-winning-trading-strategy-realtest).
- **In-sample results (Oct 1928 – Oct 2015, assuming 1% a year leverage cost)** — [CXO review (snippet)](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/):
  - The 2× 200-day SMA strategy had a Sharpe of 0.51, against 0.30 for buy-and-hold.
  - Max drawdown was −86% for S&P 500 total-return buy-and-hold and −99% for constant daily 2× leverage.
  - From $10,000, terminal values were $19 million for the index, and $270 million, $39 billion and $9 trillion for the increasingly leveraged rotation scenarios.
- **Critique (Proactive Advisor Magazine, undated).** The moving-average rule beats buy-and-hold in absolute terms in only 49% of rolling 3-year periods, though it has positive alpha in 69%. It underperforms in strong bull markets (the 1990s, 2002–2007, 2009–2015), "and the differential increases when commissions, slippage, and taxes are incorporated." The method "breaks down in situations where you get whipsaw" (snippet) — [Proactive Advisor Magazine](https://proactiveadvisormagazine.com/moving-averages-leverage-long-run/)
- **Pre-registered replication (RafaelPF07/evotrader PR #4, protocol committed 2026-09-22 before results; financing at T-bills + 1%)** — [PR #4](https://github.com/RafaelPF07/evotrader/pull/4):

| Universe | Buy-and-hold (CAGR / Sharpe / max DD) | 2× trend + 1.5× leverage (CAGR / Sharpe / max DD) |
|---|---|---|
| Development (US ETFs, data cut at 2021) | 10.6% / 0.64 / −43% | 10.5% / 0.74 / −21% |
| 5 new sector ETFs | 8.9% / 0.47 / −49% | 5.4% / 0.30 / −40% |
| 13 new country ETFs | 9.3% / 0.44 / −64% | 10.6% / 0.56 / −31% |

  - Post-publication US (2016–26, not formally judged): 12.8% vs 14.1% for buy-and-hold.
  - "No arm passes." The trend filter "consistently reduced maximum drawdowns across all 18 new instruments but lowered returns on 13 of them — leverage compensation proved insufficient except during severe crashes."
- **setup4alpha, "I Tested the Award-Winning Trading Strategy in RealTest" (undated) (snippet).** The test applied the rule to SPY, QQQ, SSO, UPRO and TQQQ, with SPY and QQQ as signal ETFs — [setup4alpha](https://setup4alpha.substack.com/p/tested-award-winning-trading-strategy-realtest):
  - On QQQ, the filter cut the worst drawdown from −80.14% to −27.02% and raised CAGR to 10.40% from 8.19% for buy-and-hold.
  - On TQQQ, buy-and-hold grew $10,000 to about $3.96 million with a −81.61% max drawdown. The moving-average version reached about $1.12 million with a −57.19% max drawdown. The test period is not visible in the snippet; it is presumably TQQQ's 2010+ history.
  - The author's explanation: "A slow trend filter can sell after a large decline has already happened, then buy back after the strongest part of the recovery... With a 3x ETF, it can be extremely expensive, and whipsaw is the reason."
- **Gayed's own follow-up.** The Lead-Lag Report of 2021-08-20 is titled "Leverage Has Worked For Large Caps, Small Caps Not So Much. Here's Why" (title only) — [Seeking Alpha](https://seekingalpha.com/mp/1302-the-lead-lag-report/articles/5629818-august-20-2021-leverage-has-worked-for-large-caps-small-caps-not-so-much-here-s-why)

**HEDGEFUNDIE's "excellent adventure" (UPRO/TMF 55/45; Bogleheads, 2019 on): a popular leveraged-ETF rule that failed when its regime assumption broke**
- In 2022, stocks and long Treasuries fell together, breaking the strategy's core hedge assumption. TMF had a 1-for-10 reverse split in 2022. Reported max drawdown was 70.58%, with CAGR of 24.63% vs 14.79% for SPY since May 2009 (snippet; attribution among the result pages unverified, probably etfportfolioblueprint) — [etfportfolioblueprint](https://etfportfolioblueprint.com/posts/hedgefundie-s-excellent-adventure-a-3x-leveraged-etf-portfolio); [Bogleheads thread](https://www.bogleheads.org/forum/viewtopic.php?t=288192)

**Composer "TQQQ For The Long Term" (FTLT) symphonies (composer.trade blocked) (snippets)**
- **Rules (one common version).** When SPY is above its 200-day average, hold TQQQ (some variants 80% TQQQ plus 20% SOXL), but switch to UVXY if TQQQ's 10-day RSI is above 79. When SPY is below its 200-day average, buy 3× bulls (TECL or UPRO) on deep dips (RSI below about 30); otherwise hold SQQQ or TLT depending on the short-term trend — [Composer FTLT with SOXL](https://www.composer.trade/trading-strategies/tqqq-ftlt-with-a-bit-of-soxl-and--V8PMHSkT4yH87TLz2B7K)
- **Origin and marketing.** The strategy was "originally shared on Reddit by a Composer power user named Dereck Nielsen." "From June 2022 to present, this strategy has returned over +400% with 82% annualized returns." A simplified version was backtested to the 1970s — [Benzinga Composer review (undated; affiliate-style review)](https://benzinga.com/money/composer-review)
- **Platform-reported "out-of-sample" figures:**
  - TQQQ FTLT 2.0: about 49% a year vs about 22% for SPY — [Composer](https://www.composer.trade/trading-strategies/tqqq-ftlt-20-iM4mdWcn3DPeUNZPsYNW)
  - FTLT with SOXL: about 80.8% a year, Calmar 1.56, Sharpe 1.17, vs about 20.9% — [Composer](https://www.composer.trade/trading-strategies/tqqq-ftlt-with-a-bit-of-soxl-and--V8PMHSkT4yH87TLz2B7K)
  - 1.5× T/QQQ FTLT 5/2/25: about 66.6% vs about 33.7% — [Composer](https://www.composer.trade/trading-strategies/15x-tqqq-ftlt-5225-qBnnyWPpwbpSumnD234N)
- **How Composer's out-of-sample statistics work.** A search summary of Composer's documentation stated that "when editing symphony conditions, Composer preserves your out-of-sample (OOS) date, so your backtest stays intact." Which Composer page says this is unverified — [Composer What's New](https://www.composer.trade/whats-new); [Composer Backtest Basics](https://help.composer.trade/article/67-backtest-basics)
- **Live vs backtest.** A review notes that "one dual-momentum strategy underperformed its backtest by roughly 3–4 percentage points annualized when run live on Composer" (undated) — [alphagaindaily Composer review](https://alphagaindaily.com/en/blog/composer-ai-trading-platform-review)

**RSI mean reversion on 3× ETFs (low-quality evidence only)**
- A Composer "Simple TQQQ RSI mean reversion" symphony exists. A search summary reported an RSI-driven TQQQ/UVXY rotation with about 30% a year "out-of-sample" vs about 17% for SPY, but max drawdown of about 58% vs 19% (attribution among the Composer pages unverified) — [Composer](https://www.composer.trade/trading-strategies/simple-tqqq-rsi-mean-reversion-4hcYKZBIjhZo3Yg0NTQk)
- Generic RSI(2) blog claims (not leveraged-ETF-specific; attribution among the result pages unverified):
  - A walk-forward efficiency of 0.78 — [backtesteverything](https://www.backtesteverything.com/blog/rsi-mean-reversion-strategy-complete-backtest)
  - A win rate of 81% in the 2009–2021 bull market vs 58% in bear-market trades — [toptradingstrategy](https://toptradingstrategy.com/strategy/rsi-2-mean-reversion)
  - That the strategy "continues to perform well after the book was published," but has a poor annualized return because trades are infrequent and "would easily be beaten by a simple buy and hold" when traded alone in one market — [QuantifiedStrategies RSI-2](https://www.quantifiedstrategies.com/rsi-2-strategy/); [EasyLanguage Mastery](https://easylanguagemastery.com/strategies/connors-2-period-rsi-update-2019/)

### Inferences
- The robust, replicated property of 200-day-MA leverage rules is *risk reduction in prolonged crashes* (1929-style, 2000–02, 2008, 2022), not return enhancement. With 3× daily-reset products, whipsaw around the MA in V-shaped selloffs is very costly; the TQQQ RealTest result kept only 28% of buy-and-hold ending wealth.
- FTLT-type symphonies combine many conditional branches (MA filters, RSI thresholds such as 79 and 30, UVXY, SQQQ and TLT branches) chosen on 2010s–2020s data. By Bailey et al.'s logic (Section 6), the number of implicit trials far exceeds what about 15 years of daily data can support. Their "OOS" records cover a mostly bullish 2022–2025 window, are self-reported by the platform, and are subject to survivorship: popular symphonies are popular *because* they did well. If Composer keeps the OOS date when a symphony's rules are edited, its "OOS" record can also include rule changes made after seeing that data, so it is not a clean out-of-sample test.
- A SOXL/SOXS switching rule built from MA and RSI thresholds would face the same issues. Treat any backtest Sharpe as heavily deflated, and require a pre-registered out-of-sample period, as evotrader did.

### Gaps
- I found no rigorous independent out-of-sample study of Composer FTLT symphonies, or of RSI mean reversion on 3× ETFs specifically. composer.trade, Reddit and Substack pages were blocked or not found.
- The original Gayed & Bilello PDF (cmtassociation.org) was blocked, so the 3× results and whipsaw statistics are not quoted directly.
- I found no published post-2016 live track record of Gayed's own leveraged-rotation implementations.

---

## 6. Post-publication decay and data snooping: how much to trust backtests (brief context)

### Takeaway
Across hundreds of published anomalies and thousands of trading algorithms, returns shrink sharply out of sample: about 26% from statistical bias alone, 58% after publication, and a median 73% fall in Sharpe from backtest to live. Most published factors fail stricter t-hurdles. In-sample Sharpe barely predicts out-of-sample Sharpe (R² < 0.025). The ORB and noise-area replications above follow the same pattern.

### Cited Findings
- **McLean & Pontiff (Journal of Finance 71(1), 2016, pp. 5–32).** Across 97 predictors, portfolio returns are "26% lower out-of-sample and 58% lower post-publication," implying a 32% decline from publication-informed trading. The decline is larger for predictors with higher in-sample returns — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365); [SSRN 2156623](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2156623)
- **Harvey, Liu & Zhu (Review of Financial Studies 29(1), Jan 2016).** At least 316 published factors. A new factor should clear a t-statistic above 3.0, and "most claimed research findings in financial economics are likely false" — [RFS](https://academic.oup.com/rfs/article/29/1/5/1843824); [NBER w20592](https://www.nber.org/papers/w20592)
- **Hou, Xue & Zhang (Review of Financial Studies 33(5), May 2020).** With microcaps mitigated, 65% of 452 anomalies fail |t| ≥ 1.96, as do 96% of the trading-frictions category. At the multiple-testing hurdle of 2.78, 82.1% fail — [RFS](https://academic.oup.com/rfs/article-abstract/33/5/2019/5236964); [SSRN 3275496](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3275496)
- **Bailey, Borwein, López de Prado & Zhu (Probability of Backtest Overfitting, 2017).** With only five years of daily data, "no more than 45 variations of a strategy should be tried," or the in-sample Sharpe is likely to be at least 1.0 by chance even when the true out-of-sample Sharpe is zero. The paper proposes combinatorially symmetric cross-validation to estimate the probability of backtest overfitting — [eScholarship](https://escholarship.org/uc/item/4w1110bb); [LBL PDF](https://escholarship.org/content/qt2329p290/qt2329p290.pdf); [Statistical Overfitting and Backtest Performance](https://sdm.lbl.gov/oapapers/ssrn-id2507040-bailey.pdf)
- **Bailey & López de Prado (2014), "The Deflated Sharpe Ratio."** It corrects the Sharpe ratio for selection bias across multiple trials and for non-normal returns — [PDF](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf). Applied example: the Beat-the-Market grid winner *passed* the DSR test (0.972 with N = 27) yet had an out-of-sample Sharpe of 0.16. Deflation guards against selection bias, not against regime change — [Maróy experiment report](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/maroy_experiment.md)
- **Wiecki, Campbell, Lent & Stauth (Quantopian, Mar 2016).** Across 888 algorithms with at least 6 months out of sample, backtest Sharpe "offer[s] little value in predicting out-of-sample performance (R² < 0.025)." More backtesting led to a larger gap. Volatility and drawdown were more predictive, and a machine-learning model on backtest features reached R² = 0.17 — [Semantic Scholar](https://www.semanticscholar.org/paper/All-That-Glitters-Is-Not-Gold:-Comparing-Backtest-a-Wiecki-Campbell/b028c2d0b2145e85d543fb21ad3fcf896c932ab5); [Quantpedia summary](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/)
- **Suhonen, Lennkh & Perez (Journal of Portfolio Management 43(2), Winter 2017).** Across 215 commercially promoted alternative-beta strategies, the median Sharpe was 1.20 in backtest and 0.31 live, a "median 73% deterioration." The most complex strategies decayed more than 30 percentage points more than the simplest — [JPM](https://www.pm-research.com/content/iijpormgmt/43/2/90); [Aalto](https://research.aalto.fi/en/publications/quantifying-backtest-overfitting-in-alternative-beta-strategies)

### Inferences
- A reasonable prior for a published intraday or leveraged-ETF rule: expect at least half the backtested excess return to vanish, and more for complex, high-in-sample-Sharpe rules. Section 3's Beat-the-Market results (in-sample Sharpe about 1.3, out of sample 0.16–0.39) fall in or beyond this range.
- For SOXL/SOXS research, count *all* variants tried, including thresholds, windows and exits. Deflate the Sharpe accordingly. Keep an untouched forward period, as the giovannibrusco and evotrader repos do.

### Gaps
- I found no study that measures post-publication decay specifically for *intraday* technical rules as a class. The evidence here is from cross-sectional anomalies, commercial strategies and individual replications.

---

## 7. Retail day-trader outcomes: base rates (brief)

### Takeaway
In the two most complete datasets (all Taiwan day traders, 1992–2006; all Brazilian mini-index futures day traders, 2013–2017), fewer than 1% earn predictable profits after fees. 97% of Brazilians who persisted for more than 300 days lost money.

### Cited Findings
- **Barber, Lee, Liu & Odean, "The Cross-Section of Speculator Skill: Evidence from Day Trading" (Journal of Financial Markets, 2014).** Covers all Taiwan Stock Exchange day traders from 1992 to 2006, with 3.7 billion transactions. Most day traders lose money, and "less than 1% of day traders are able to outperform consistently." The study documents large cross-sectional differences in before- and after-fee returns — [Berkeley PDF](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/The%20Cross-Section%20of%20Speculator%20Skill.pdf); [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418113000190); [SSRN 529063](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=529063)
- **Barber, Lee, Liu & Odean, "Do Individual Day Traders Make Money? Evidence from Taiwan" (working paper, 2004).** Heavy day traders made daily gross profits of NT$36.4 million but daily net losses of NT$68.9 million after costs. The reported average loss is 23.9 bps a day net of fees. "Only two out of ten make money; fewer do so consistently" (search-summary figures; attribution to this paper vs the 2014 paper not fully verified) — [Berkeley PDF](https://faculty.haas.berkeley.edu/odean/papers/Day%20Traders/Day%20Trade%20040330.pdf); [Yale behavioral-finance copy](http://www.econ.yale.edu/~shiller/behfin/2004-04-10/barber-lee-liu-odean.pdf)
- **Chague, De-Losso & Giovannetti, "Day Trading for a Living?" (SSRN 3423101, 2019).** Covers 19,646 individuals who began day trading Brazilian equity index futures between 2013 and 2015, tracked to 2017. "97% of all individuals who persisted for more than 300 days lost money." Only 1.1% earned more than the Brazilian minimum wage, and only 0.5% earned more than a bank teller's starting salary. The top individual earned US$310 a day with a standard deviation of US$2,560. There was "no evidence of learning" — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101); [ResearchGate](https://www.researchgate.net/publication/334630772_Day_Trading_for_a_Living)

### Inferences
- These base rates match the replication evidence above. Gross intraday signals often exist, but after spreads, slippage and fees, almost nobody captures them persistently. An intraday SOXL/SOXS strategy should be presumed unprofitable after costs until a pre-registered forward test shows otherwise.

### Gaps
- I found no comparable full-population study of US retail day traders in leveraged ETFs specifically.

---

## 8. Cross-cutting synthesis: what survives costs, what decayed, regime dependence, break-even costs

### Takeaway
None of the published intraday rules reviewed here has shown a robust edge that survives costs in independent post-publication data.
- **QQQ 5-minute ORB:** break-even at about 2.2¢/share, net zero on 5 indices over 2015–2026, and dependent on 2022.
- **Stocks-in-play ORB:** large in-sample edges, but dominated by fill-model, survivor-bias and stop-slippage assumptions.
- **Beat the Market:** survives costs in-sample (2020–2024), but the signal itself decayed in 2025–2026 (out-of-sample Sharpe 0.16–0.39; ES −0.07).
- **Gao et al.:** generalized historically but weakened or disappeared out of sample in recent US data.
- **Daily leveraged-ETF MA rules:** reliably reduce drawdowns but generally fail to beat buy-and-hold on return out of sample.

### Cited Findings
| Strategy | In-sample claim | Independent replication (in-sample) | Post-publication / out-of-sample | Break-even cost evidence | Regime dependence |
|---|---|---|---|---|---|
| QQQ 5-min ORB (Zarattini & Aziz, Apr 2023) | Alpha 33%/yr net of commissions; TQQQ 1,484% (2016–23) [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622) | Sharpe 1.06 vs 1.12 [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq); +0.131R gross on NQ [mql5](https://www.mql5.com/en/blogs/post/776235) | Net indistinguishable from zero on NQ/SPX/Dow/DAX/FTSE, 2015–2026 [mql5](https://www.mql5.com/en/blogs/post/776235); post-publication Sharpe −0.84 (attribution unverified) [paperswithbacktest](https://paperswithbacktest.com/strategies/orb-trading-strategy) | About 2.2¢/share entry (stop at 2×); QQQ spread about 1¢; Sharpe 0.23 at 2¢ [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq) | 76% of filtered PnL from 2022; losses in 2017, 2020, early 2023 [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq) |
| Stocks-in-play ORB (Zarattini, Barbon & Aziz, Feb 2024) | >1,600%, Sharpe 2.81, alpha 36% (2016–23); plain ORB Sharpe 0.48 [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284) | Sharpe 2.72–2.98 (259 tickers) [hsaeed22058](https://github.com/hsaeed22058/strategy-backtest); 2.396 for 2016 only [QuantConnect (snippet)](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/) | No clean post-publication test found | Live paper trading: stop fills slipped 3–5R on gap-throughs; intra-bar fill order alone worth 6.39 Sharpe [hsaeed22058](https://github.com/hsaeed22058/strategy-backtest) | Not established |
| Beat the Market (Zarattini, Aziz & Barbon, May 2024) | Sharpe 1.33, 19.6%/yr (2007–24) [SSRN via Maróy page](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349) | Sharpe 1.34 (2015–24, IQFeed) [PazSheimy](https://github.com/PazSheimy/spy-intraday-momentum-oos); 1.11 (2020–26, IEX) [codecat-ops](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md) | Sharpe 0.39 (May 2024 – Mar 2026, p < 0.001) [PazSheimy](https://github.com/PazSheimy/spy-intraday-momentum-oos); 0.16 (2024 on) [Maróy experiment](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/maroy_experiment.md); 2025 −0.27, 2026 YTD −1.91; ES −0.07 [validation](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md), [ES](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation_es.md) | Sharpe 1.11 → 0.94 at $0.01/share; ES costs about 0.4 bps/round trip vs −0.61 bps expectancy (signal, not cost, failed) [validation](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation.md), [ES](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/reports/validation_es.md) | Strong 2020–24, +25.8% in 2022; weak 2012–15 in the paper; fails 2025–26 [CONCLUSIONS](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/docs/CONCLUSIONS.md) |
| Market intraday momentum (Gao et al., JFE 2018) | Timing Sharpe 1.08, 6.67%/yr before costs (1993–2013) [ResearchGate](https://www.researchgate.net/publication/325364670_Market_Intraday_Momentum) | 60+ futures 1974–2020 [Baltussen et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365); 16 countries, also out of sample [Li et al.](https://research.birmingham.ac.uk/en/publications/intraday-time-series-momentum-global-evidence-and-links-to-market/) | "Disappears in the out-of-sample period" [Rosa 2022](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375); "diminished over time" [Zhang & Hua 2024](https://www.mdpi.com/2227-9091/12/11/180); about 75% weaker [EFMA 2024](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/Interday_Cross_Sectional_Momentum.pdf) | MNQ OHLCV signals: gross 0.07–1.50 points vs 2-point friction [Mesfin 2026](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6709401) | Stronger on volatile, high-volume, recession and news days [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866); regime-switching [Rosa](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375) |
| 200-day MA plus leverage (Gayed & Bilello, 2016) | 2× rule Sharpe 0.51 vs 0.30 (1928–2015) [CXO (snippet)](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/) | Lower drawdowns in all 18 new ETFs [evotrader](https://github.com/RafaelPF07/evotrader/pull/4) | "No arm passes"; US 2016–26 12.8% vs 14.1% buy-and-hold [evotrader](https://github.com/RafaelPF07/evotrader/pull/4); TQQQ ending wealth $1.12M vs $3.96M [setup4alpha](https://setup4alpha.substack.com/p/tested-award-winning-trading-strategy-realtest) | Whipsaw is the dominant cost for 3× products [setup4alpha](https://setup4alpha.substack.com/p/tested-award-winning-trading-strategy-realtest) | Helps in prolonged crashes; lags in bull markets [Proactive Advisor](https://proactiveadvisormagazine.com/moving-averages-leverage-long-run/) |
| Composer TQQQ FTLT (Reddit/Composer, about 2022) | +400%, 82%/yr since June 2022 (marketing) [Benzinga](https://benzinga.com/money/composer-review) | None independent | Platform "OOS" figures of 49–81%/yr [Composer](https://www.composer.trade/trading-strategies/tqqq-ftlt-with-a-bit-of-soxl-and--V8PMHSkT4yH87TLz2B7K); OOS date kept when rules are edited [Composer](https://www.composer.trade/whats-new) | Not reported | Bull-market 2022–25 out-of-sample window |

### Inferences
- **What holds up.**
  - Mechanism-level evidence that intraday trends continue into the close on volatile days (Baltussen et al., Li et al.), with a plausible hedging-flow driver.
  - Drawdown reduction from slow trend filters.
  - The fact that ORB edges concentrate in a few catalyst or high-volatility names and days.
- **What does not.** Headline returns built on zero slippage, hindsight-chosen exits, survivor-biased universes or optimized parameters. Every post-2023 out-of-sample number found for Beat the Market and QQQ ORB is at or near zero.
- **Implication for a SOXL/SOXS intraday or switching design.**
  - Measured per-trade edges of a few bps at most must clear a tick that is a much larger share of a low-priced 3× ETF's price. The 3× product also amplifies regime dependence.
  - Any candidate should be judged on a pre-registered forward period, with the Sharpe deflated for the number of variants tried.
  - Explicitly check results with 2020 and 2022 removed, since those two years dominate most published intraday momentum and ORB backtests.

### Gaps
- Six post-publication or independent test write-ups could only be read as snippets, because their domains were blocked: mql5 (2026-09-25), paperswithbacktest, danfin, QuantConnect, CXO, and Quantitativo/Hunt Gather Trade.
- No source reported break-even slippage specifically for TQQQ, SOXL or SOXS versions of these rules.
