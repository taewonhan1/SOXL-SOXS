# Published switching and two-sided trading systems for paired bull/bear leveraged ETFs other than SOXL/SOXS (TQQQ/SQQQ, SPXL/SPXS, UPRO/SPXU, TNA/TZA, LABU/LABD, FAS/FAZ, TECL/TECS, NUGT/DUST)

*Compiled 2026-10-03. **Source-access note for the report writer:** the network proxy blocked direct reads of almost every primary source: SSRN, CMT Association, Concretum Group site and Substack, QuantConnect, QuantifiedStrategies, Reddit, Seeking Alpha, CXO Advisory, Alpha Architect, Allocate Smartly, Quantpedia, mql5, arXiv, TradingView, composer.trade, Substack in general, Bear Bull Traders, MIAX, Nasdaq Trader, nd.edu and others. Only GitHub could be read directly. Each finding is tagged **[D]** when it was read directly from the linked page, or **[S]** when it comes from a search-engine summary or snippet of the linked page. [S] findings are secondary: treat their numbers as "reported in a search summary of that page". The session's shared web-search quota ran out before a few leads could be closed (see Gaps).*

## Q1. What are the best-known bull/bear switching and two-sided systems, and what are their exact rules? (a) intraday vs (b) daily/regime

### Takeaway
The best-documented systems are not native "TQQQ↔SQQQ switches". They are long/short systems on the underlying (QQQ or SPY) that their authors port to TQQQ as a leverage wrapper.
- **(a) Intraday:** Zarattini & Aziz's 5-minute opening-range breakout (ORB) on QQQ/TQQQ (Apr 2023), their VWAP trend system on QQQ/TQQQ (Nov 2023), and Zarattini, Aziz & Barbon's "noise area" intraday momentum on SPY (May 2024), plus Maróy's QQQ variant (Jan 2025).
- **(b) Daily/regime:** Gayed & Bilello's 200-day moving-average "Leverage Rotation Strategy" (2016), which switches between a leveraged index and T-bills and never holds an inverse fund; Composer's "TQQQ For The Long Term" (FTLT) family, which combines SPY's 200-day average with a 10-day RSI and can hold TQQQ, UVXY, TECL, UPRO/SPXL, SQQQ or TLT; and community variants (QuantConnect regime rotation, SPY 200-day SMA with entry/exit buffers, TQQQ/TMF, BTAL/TQQQ).
- **Other pairs:** I found almost nothing published with rules and results for SPXL/SPXS, UPRO/SPXU, TNA/TZA, LABU/LABD, FAS/FAZ, TECL/TECS or NUGT/DUST.

### Cited Findings

#### (a) Intraday systems

**A1. Zarattini & Aziz, "Can Day Trading Really Be Profitable? Evidence of Sustainable Long-term Profits from Opening Range Breakout (ORB) Day Trading Strategy vs. Benchmark in the US Stock Market" (SSRN 4416622; PDF uploaded 18 Apr 2023)**
- Rules [D]:
  - Uses QQQ 5-minute bars.
  - If the 09:30–09:35 candle is bullish, go long at the 09:35 open. If it is bearish, go short. If it is a doji, no trade.
  - The stop is the opposite extreme of the first candle: its low for a long, its high for a short.
  - The target is 10R; otherwise the position is closed at the session close.
  - Position size = min(1% of equity / $R, 4 × equity / entry price). That is 1% risk, capped by the 4× FINRA day-trading buying-power limit.
  - Starting capital is $25,000.
  - Source: [giovannibrusco replication README (GitHub)](https://github.com/giovannibrusco/zarattini-2023-orb-qqq).
- The 09:35 entry, opposite-extreme stop and 10R-or-close exit are also described in [S] [danfin.net](https://danfin.net/opening-range-breakout-research). The no-trade-on-doji rule is in [S] [ORB paper PDF mirror](https://static1.squarespace.com/static/5983d931579fb366729580d8/t/643ed6765176b45506e41a01/1681839734183/SSRN-id4416622.pdf).
- The sample runs Jan 2016–Feb 2023. The authors "introduced the use of TQQQ, a leveraged ETF of QQQ, which allows day traders to fully exploit the benefit of the active strategy while adhering to leverage constraints." — [S] [SSRN 4416622](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622); [S] [Concretum Substack](https://concretumgroup.substack.com/p/can-day-trading-really-be-profitable); [S] [Concretum page](https://concretumgroup.com/can-day-trading-really-be-profitable/)
- In practice the 10R target is "nearly decorative". It is hit on about 2–3% of trades; about 75% of trades exit on the stop and about 22% at the close. The replicator calls it "intraday momentum-continuation with a 1R stop". — [D] [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- There is one trade per day. After a stop-out the system stays flat and does not reverse. — [D] [giovannibrusco flowchart](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- Concretum publishes Python backtest code for the ORB. — [S] [Concretum: Backtesting ORB with Polygon.io](https://concretumgroup.com/backtesting-the-opening-range-breakout-orb-strategy-using-polygon-io/)

**A2. Zarattini & Aziz, "Volume Weighted Average Price (VWAP) The Holy Grail for Day Trading Systems" (SSRN 4631351; circulating by 15 Nov 2023)**
- The rule is always-in trend following: long when price is above the session VWAP, short when it is below.
- Instruments are QQQ and TQQQ, from 2 Jan 2018 to 28 Sep 2023, starting with $25,000.
- Sources: [S] [Bear Bull Traders summary](https://members.bearbulltraders.com/magic-of-vwap-the-holy-grail-of-day-trading-systems/); [S] [Concretum page](https://concretumgroup.com/volume-weighted-average-price-vwap-the-holy-grail-for-day-trading-systems/); [S] [Steve Burns post on X, 15 Nov 2023](https://x.com/SJosephBurns/status/1724761377154142328)
- Concretum presents it as a "VWAP Day Trading Strategy on QQQ and TQQQ". It describes combining a tested intraday signal with leveraged ETFs like TQQQ as "turning brokerage constraints into a design choice rather than a limitation". — [S] [Concretum Substack](https://concretumgroup.substack.com/p/vwap-the-holy-grail-for-day-trading); [S] [Concretum Pills #6](https://concretumgroup.substack.com/p/concretum-pills-6)

**A3. Zarattini, Aziz & Barbon, "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)" (SSRN 4824172; Swiss Finance Institute RP 24-97; 10 May 2024)**
- Rules [D]:
  - The "noise area" is a band around the open. Its width at each minute is the average absolute move from the open at that minute over the prior 14 sessions.
  - The band is anchored to max/min(Open, previous Close) to handle overnight gaps.
  - Inside the band there is no trade. A break above the upper band means long; a break below the lower band means short. Breaks are only checked every 30 minutes.
  - The trailing stop is the tighter of the band and VWAP.
  - Positions are forced flat at 16:00.
  - Sizing targets 2% daily volatility, capped at 4× leverage.
  - Sources: [codecat-ops replication README](https://github.com/codecat-ops/zarattini-2024-momentum-spy); [POB-CL-DT PR #13, 30 Sep 2026](https://github.com/patrickobirmingham-eng/POB-CL-DT/pull/13) (which gives the decision times as 10:00–15:30)
- For longs the trailing stop is max(upper band, VWAP); for shorts it is min(lower band, VWAP). — [S] [QuantConnect forum #17091](https://www.quantconnect.com/forum/discussion/17091/beat-the-market-an-effective-intraday-momentum-strategy-for-s-amp-p500-etf-spy/)
- The authors contrast their approach with academic work that "typically limits trading to the last 30 minutes". Their model "initiates trend-following positions as soon as there is an indication of abnormal demand/supply imbalance". — [S] [SSRN 4824172](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172); [S] [SFI listing](https://www.sfi.ch/en/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy)
- Concretum publishes the bands as the TradingView indicator "Concretum Bands". It also publishes MATLAB and Python/Alpaca backtest code. — [S] [TradingView Concretum Bands](https://www.tradingview.com/script/CUpWCZhe-Concretum-Bands/); [S] [Concretum MATLAB](https://concretumgroup.com/backtesting-riding-intraday-trends-in-us-markets-using-matlab/); [S] [Concretum Python/Alpaca](https://concretumgroup.com/backtesting-7-years-of-free-data-beat-the-market-an-effective-intraday-momentum-strategy-for-the-sp500-etf-spy/)

**A4. Maróy, "Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies" (SSRN 5095349; Jan 2025)**
- Applies the noise-boundary strategy to QQQ. It notes that a more recent paper focused on QQQ "since the results for the strategy are better on QQQ".
- Tests VWAP, VWAP & Ladder, and Ladder exits, with parameter optimization.
- Source: [S] [SSRN 5095349](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349)

**A5. Practitioner TQQQ ORB variant (Trade That Swing; date not shown)**
- Uses a 15-minute opening range on a 5-minute chart, entering on a 5-minute close outside the range.
- The stop is at the midline of the range; reward:risk is 2:1; each trade risks 1% of equity.
- Takes both longs and shorts.
- Source: [S] [Trade That Swing](https://tradethatswing.com/tqqq-orb-strategy-68-backtesting-and-modifying-for-changing-conditions/)

**A6. Pair-handling rule for bull/bear LETF universes (Lumibot "Bull/Bear Leveraged ETF" example; date not shown)**
- "Never hold a long ETF and its inverse on the same index at once (such as TQQQ with SQQQ or UPRO with SPXU) because they cancel each other and both decay". Keep only the side with the larger weight and give it the net weight.
- "When you switch sides on an index, sell the whole opposite side before buying, in the same session."
- The example universe is TQQQ/SQQQ, UPRO/SPXU, UDOW/SDOW, TNA/TZA, TECL/TECS, SOXL/SOXS, WEBL/WEBS, FAS/FAZ, LABU/LABD, ERX/ERY, GUSH/DRIP, DRN/DRV, TMF/TMV and NUGT/DUST. No performance is claimed.
- Sources: [S] [Lumibot docs](https://lumibot.lumiwealth.com/agents_example_bull_bear_leveraged_etf.html); [S] [Lumibot GitHub example](https://github.com/Lumiwealth/lumibot/blob/dev/lumibot/example_strategies/ai_trading_team_bull_bear_leveraged_etf.py)

#### (b) Daily / regime systems

**B1. Gayed & Bilello, "Leverage for the Long Run – A Systematic Approach to Managing Risk and Magnifying Returns in Stocks" (2016 Charles H. Dow Award; CXO dates it March 2016)**
- When the S&P 500 Total Return Index closes above its 200-day SMA, hold the index with 1.25×, 2× or 3× leverage. When it closes below, switch to U.S. Treasury bills. Shorter SMAs are tested for robustness.
- Sources: [S] [CXO Advisory](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/); [S] [paper PDF (CMT Association)](https://cmtassociation.org/wp-content/uploads/2025/08/2016-gayed-bilello.pdf)
- Leverage is reset daily, "the most commonly used time frame in leveraged mutual funds and Exchange Traded Funds". The paper assumes a 1% annual cost of leverage, approximating LETF expense ratios. "The initial analysis ignores costs of switching between stocks and T-bills." — [S] [paper PDF](https://cmtassociation.org/wp-content/uploads/2025/08/2016-gayed-bilello.pdf); [S] [Proactive Advisor Magazine](https://proactiveadvisormagazine.com/moving-averages-leverage-long-run/)
- The bearish leg is T-bills. As summarized, the paper has no inverse or short leg. — [S] [CXO](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/)
- Motivating statistics, as summarized for the paper and related coverage — [S] [paper PDF](https://cmtassociation.org/wp-content/uploads/2025/08/2016-gayed-bilello.pdf):
  - With the S&P 500 above its 200-day average: 14.1% annualized return and 14.7% annualized volatility.
  - Below it: −2.3% return and 26.5% volatility.
  - The index was below its 200-day average 69% of the time during recessions vs 19% during expansions.
- A Gayed newsletter follow-up is titled "Leverage Has Worked For Large Caps, Small Caps Not So Much". This is relevant to TNA/TZA; only the title was retrieved. — [S] [Lead-Lag Report, Seeking Alpha, 20 Aug 2021](https://seekingalpha.com/mp/1302-the-lead-lag-report/articles/5629818-august-20-2021-leverage-has-worked-for-large-caps-small-caps-not-so-much-here-s-why)

**B2. Composer "TQQQ For The Long Term" (FTLT) family (Composer "symphony" by power user Dereck Nielsen, /u/derecknielsen, shared via Reddit; performance quoted "from June 2022")**
- Daily rules as summarized:
  - **SPY above its 200-day SMA:** hold TQQQ. If TQQQ's 10-day RSI is above 79, or SPXL's 10-day RSI is also overbought (≈80+), rotate to UVXY.
  - **SPY below its 200-day SMA:** if oversold (10-day RSI ≈30), buy the dip in TECL, UPRO/SPXL or TQQQ. Otherwise hold SQQQ or TLT, choosing whichever "is stronger".
  - Sources: [S] [Composer: Reddit TQQQ FTLT (60+ RSI mod)](https://www.composer.trade/trading-strategies/reddit-tqqq-for-the-long-term-60-rsi-mod-nWP8uLmaVHGfBS7vh4fx); [S] [Composer: FTLT (Reddit Post Link)](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-reddit-post-link-HukRwDJLlYPLMbrQbua5); [S] [TradingView port "TQQQ for the Long Term (Composer)"](https://my.tradingview.com/script/CiW6StdS-TQQQ-for-the-Long-Term-Composer)
- There are many forks: "Original", "2.0", "V2 BlackSwan MeanRev", "V4", "Full Package", "with a bit of SOXL", "1.5x T/QQQ FTLT 5/2/25", stop-loss/sideways-detection variants, and a "BIL instead of UVXY" long-backtest variant.
  - Sources: [S] [Composer FTLT Original](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-original-WDQzBV4Mse7Zypxk4LtC); [S] [FTLT 2.0](https://www.composer.trade/trading-strategies/tqqq-ftlt-20-iM4mdWcn3DPeUNZPsYNW); [S] [1.5x T/QQQ FTLT 5/2/25](https://www.composer.trade/trading-strategies/15x-tqqq-ftlt-5225-qBnnyWPpwbpSumnD234N); [S] [stop-loss/sideways variant](https://www.composer.trade/trading-strategies/tqqq-ftlt-reddit-link-with-stop-losssideways-market-detection-0001-mm0bwjq3Mo6KkYe5FpYz); [S] [50d/200d + BIL variant](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-reddit-post-link-50d-tqqq200d-tqqq-bil-instead-of-uvxy-and-tqqq-intsead-of-tcel-for-longterm-backtest-compare-gj4k6luYNV0LPIxDKNW3)

**B3. QuantConnect community algorithms**
- **"Regime-Based Tactical Rotation"** — [S] [QuantConnect #19360](https://www.quantconnect.com/forum/discussion/19360/regime-based-tactical-rotation/)
  - TQQQ's own 200-day SMA is the master switch: risk-on above it, risk-off below.
  - A 10-day RSI above 80 counts as overbought and below 31 as oversold.
  - In risk-off it puts 100% into whichever of TLT or SQQQ has the lower 10-day RSI (the "most oversold").
- **"Simple Algo: Trades TQQQ/SQQQ based on volatility"** — [S] [QuantConnect #2278](https://www.quantconnect.com/forum/discussion/2278/simple-algo-trades-tqqq-sqqq-based-on-volatility/)
  - Switches between TQQQ and SQQQ based on volatility.
  - Using QQQ instead of TQQQ as the volatility input "resulted in massive drawdowns".
- **Strategy Library, "Leveraged ETFs with Systematic Risk Management"** — [S] [QuantConnect #8996](https://www.quantconnect.com/forum/discussion/8996/Strategy+Library+Addition:+Leveraged+ETFs+with+Systematic+Risk+Management)
  - Controls risk with simple moving averages.
  - "Rebalancing weekly instead of daily can avoid whipsaws, improve performance and reduce costs."
- **Other threads (no details retrieved):** [S] [QuantConnect #3912 "KISS Principle on TQQQ"](https://www.quantconnect.com/forum/discussion/3912/KISS+Principle+on+TQQQ); [S] [QuantConnect research: ORB for Stocks in Play](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/)

**B4. Other community daily rules**
- **"SPY200SMA +4/−3" and "+5/−3 buffer"** — [S] [TradingView SPY200SMA 4/3](https://jp.tradingview.com/script/bznVflR1-SPY200SMA-4-3-TQQQ-QQQ-STRATEGY); [S] [TradingView 200 SMA 5/3 buffer](https://www.tradingview.com/script/0S8jQcA5-200-SMA-5-3-Buffer-for-SPY-QQQ)
  - Buy TQQQ when SPY is +4% (or +5%) above its 200-day SMA; sell everything when SPY is −3% below it.
  - The buffers are meant to avoid whipsaws in sideways markets.
- **WildWest000 TQQQ/SQQQ "regime" bot (GitHub, data to Jun 2026)** — [D] [WildWest000/tqqq-trading-strategy](https://github.com/WildWest000/tqqq-trading-strategy)
  - The default engine holds TQQQ or cash, using QQQ momentum and volatility scaling, and "never holds SQQQ".
  - Alternative rules engine:
    - Bull (QQQ above its 50-day EMA, or above its 20-day EMA with positive momentum): 100% TQQQ.
    - Neutral: 70% TQQQ, 30% cash.
    - Bear (below both EMAs with negative momentum): 100% cash.
    - Crisis (Bear plus ATR above 1.5× its median): 20% SQQQ, 80% cash.
  - RSI overlays on TQQQ: above 70, hold 75% TQQQ plus a 15% SQQQ hedge; above 80, hold 60% TQQQ plus 25% SQQQ.
  - Signals use the prior close and are executed at the next open.
  - Risk controls: a 25% trailing stop from the equity peak and a 5-day cash cooldown.
- **50/50 TQQQ/TMF** (from Lewis Glenn, 2020, "Long-Term Investing in Triple Leveraged Exchange Traded Funds") — [S] [QuantifiedStrategies](https://www.quantifiedstrategies.com/triple-leveraged-etf-trading-strategy/)
  - Rebalanced every two months.
  - Crash filter: if TQQQ drops 20% or more in one day, move 100% to IEF until it recovers.
- **67% BTAL / 33% TQQQ**, rebalanced once a year on the first trading day of January. — [S] [Algomatic Trading](https://www.algomatictrading.com/post/this-simple-2-etf-strategy-has-outperformed-the-nasdaq-for-13-years); [S] [QuantifiedStrategies repost](https://www.quantifiedstrategies.com/a-simple-2-etf-strategy-that-outperforms-the-nasdaq/)
- **Cesar Alvarez, "UPRO/TQQQ Leveraged ETF Strategy"** (rules not retrievable). — [S] [Alvarez Quant Trading](https://alvarezquanttrading.com/blog/upro-tqqq-leveraged-etf-strategy/)

#### (c) The other pairs (SPXL/SPXS, UPRO/SPXU, TNA/TZA, LABU/LABD, FAS/FAZ, TECL/TECS, NUGT/DUST)
- Searches for TNA/TZA, LABU/LABD and FAS/FAZ switching systems returned only universe lists, issuer product lists and a GitHub PR swapping single-stock ETFs for sector bull/bear pairs. None gave published rules with results. — [S] [Lumibot](https://lumibot.lumiwealth.com/agents_example_bull_bear_leveraged_etf.html); [S] [Direxion LETF list (PDF)](https://www.direxion.com/uploads/Leveraged-and-Inverse-ETF-List.pdf); [S] [karthikl6333/Seek-Track PR #70](https://github.com/karthikl6333/Seek-Track/pull/70)
- For the S&P 3× pairs, results contained no backtest of switching between bull and bear funds on a 200-day signal. The S&P-side publications are leveraged-long vs cash or bonds (e.g., UPRO/TMF). Bear-fund articles on SPXS/SPXU stress decay and short-term use only. — [S] [Seeking Alpha: SPXS](https://seekingalpha.com/article/4855889-spxs-a-3x-inverse-leveraged-strategy-on-the-s-and-p-500); [S] [Seeking Alpha: SPXU risks](https://seekingalpha.com/article/4832366-spxu-understanding-risks-of-3x-leveraged-sp500-etf)
- Pair Trading Lab hosts TQQQ-vs-SQQQ and UPRO-vs-SPXL pairs backtests. These are statistical-arbitrage tests, not switching systems, and their results were not retrievable. — [S] [Pair Trading Lab TQQQ/SQQQ](https://www.pairtradinglab.com/backtests/aPjyNgCINRhNqXF0); [S] [Pair Trading Lab UPRO/SPXL](https://www.pairtradinglab.com/backtests/V5A9uim38XKQfoEU)
- FTLT uses TECL and UPRO/SPXL only as oversold dip-buys inside its TQQQ logic. — [S] [TradingView FTLT port](https://my.tradingview.com/script/CiW6StdS-TQQQ-for-the-Long-Term-Composer)

### Inferences
- The rigorous intraday literature computes signals on QQQ/SPY (sometimes confirmed with NQ/ES futures) and uses TQQQ only to get leverage. For a bull/bear LETF pair, the natural translation is:
  - long signal → long the bull fund;
  - short signal → long the bear fund (or short the bull fund).

  As summarized, none of the papers tests the bear-fund leg on its own.
- The daily systems take one of three approaches to the bear side:
  1. Cash or T-bills: Gayed & Bilello; the WildWest default engine.
  2. A relative-strength choice between the inverse fund and bonds: FTLT; QuantConnect regime rotation.
  3. A partial inverse hedge only in a "crisis" or when overbought: the WildWest rules engine.

  The most-cited academic rule (Gayed & Bilello's Leverage Rotation Strategy) never holds an inverse fund.
- FTLT's RSI(10) thresholds (79/80/30/31) were fit on 2011–2022 data and the family has dozens of forks. Its rules should be treated as heavily data-mined.

### Gaps
- I could not read the SSRN or Concretum PDFs. It is therefore unverified whether the ORB and VWAP papers implemented the TQQQ short side by shorting TQQQ or by buying SQQQ; the summaries just say "short".
- The exact original FTLT logic could not be checked line by line, because composer.trade and TradingView were blocked and versions differ. Unverified items include all thresholds, any secondary moving-average checks, and whether SQQQ vs TLT is chosen by higher or lower RSI.
- For Gayed & Bilello, I could not verify whether execution is at the same close as the signal or the next day, nor whether a Nasdaq-100 variant was tested.
- I found no published switching system with results specifically for TNA/TZA, LABU/LABD, FAS/FAZ, TECL/TECS, NUGT/DUST, SPXL/SPXS or UPRO/SPXU.
- Quantpedia, Alpha Architect and Allocate Smartly coverage could not be checked: the sites were blocked and search returned nothing specific.

## Q2. What results do they claim (period, CAGR, Sharpe, win rate, max drawdown, per-trade edge), and with what cost/slippage assumptions?

### Takeaway
The headline claims are very large:
- ORB on TQQQ: +1,484% over 2016–Feb 2023.
- VWAP system on TQQQ: +8,242% over 2018–Sep 2023, about 116% a year.
- Noise-area momentum on SPY: +1,985% over 2007–early 2024, Sharpe 1.33.
- Gayed & Bilello 3× rule: $10k grows to $9 trillion over 1928–2015.

They rest on thin cost assumptions. The ORB paper assumes $0.0005/share commission and no slippage. The VWAP TQQQ run paid $400,616 of commissions on a $25k start. Gayed & Bilello ignore switching costs. Independent replications put ORB break-even at about 2.2¢/share of slippage, and a related intraday-momentum variant at about 2.2 bps per trade. FTLT's numbers are Composer's own simulations, not audited live P&L.

### Cited Findings

#### Intraday
- **ORB (Jan 2016–Feb 2023)**
  - TQQQ version: 1,484% total return vs 169% for passive QQQ. — [S] [SSRN 4416622](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622); [S] [Concretum](https://concretumgroup.com/can-day-trading-really-be-profitable/)
  - Annualized alpha of 33% net of commissions. — same sources.
  - QQQ total return 676%. — [S] [danfin.net](https://danfin.net/opening-range-breakout-research)
  - Paper Sharpe 1.12 over 1,795 trades. — [D] [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
  - "24% hit rate, +0.13 R per trade and, with 4x leverage, 33% a year on QQQ". — [S] [mql5 blog, 25 Sep 2026](https://www.mql5.com/en/blogs/post/776235)
- **ORB cost assumptions:** commission $0.0005/share, with results stated net of commissions. — [S] [Concretum Substack](https://concretumgroup.substack.com/p/can-day-trading-really-be-profitable). The paper states "we assumed no slippage in fills"; the replicator calls this "the single load-bearing input behind its headline result". — [D] [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **ORB replication on QQQ** — [D] [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)

  | Scenario | Trades | Net PnL | Edge per share | t-stat | Sharpe | CAGR | Max DD |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | No slippage | 1,775 | $138,639 | $0.070 | 1.79 | 1.06 | 30.4% | 22.4% |
  | $0.02/share entry + $0.04/share stop slippage | 1,775 | $4,860 | $0.020 | 0.52 | 0.23 | 2.7% | 43.9% |
  | Slippage + NQ futures 09:25 confirmation filter | 844 | $44,332 | $0.125 | 2.05 | 0.77 | 15.6% | 31.1% |
  | Slippage + QQQ's own 09:25 bar (placebo) | 825 | $25,191 | $0.079 | 1.27 | 0.57 | 10.5% | 27.2% |
  | QQQ buy-and-hold (price only) | — | — | — | — | 0.72 | 15.3% | 35.6% |

  - Break-even is about 2.2¢/share of slippage, against QQQ's roughly 1¢ spread.
  - Bootstrap 95% Sharpe confidence intervals overlap with buy-and-hold: [0.05, 1.41] for the filtered strategy vs [−0.03, 1.47].
- **Sister ORB paper on "Stocks in Play"** (not LETFs): a top-20 portfolio returned over 1,600% net, with Sharpe 2.81 and 36% annualized alpha. — [S] [SSRN 4729284](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284)
- **VWAP system (2 Jan 2018–28 Sep 2023)** — [S] [Bear Bull Traders](https://members.bearbulltraders.com/magic-of-vwap-the-holy-grail-of-day-trading-systems/); [S] [Concretum](https://concretumgroup.com/volume-weighted-average-price-vwap-the-holy-grail-for-day-trading-systems/)
  - QQQ: $25,000 → $192,656 net of commissions (671%), max drawdown 9.4%, Sharpe 2.1. QQQ buy-and-hold returned 126% with a 37% drawdown and Sharpe 0.7.
  - TQQQ: $25,000 → $2,085,417 (8,242%), about 116% a year, with a "comparable" max drawdown.
  - The TQQQ run's commissions totaled $400,616.
  - QuantifiedStrategies summarized the QQQ version as "43% annual returns" (consistent with 671% over about 5.7 years). — [S] [QuantifiedStrategies note](https://substack.com/@quantifiedstrategies/note/c-305945659)
- **Noise area, SPY (2007–early 2024):** 1,985% total return net of costs, 19.6% annualized, Sharpe 1.33. — [S] [SSRN 4824172](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172); [S] [QuantifiedStrategies summary](https://www.quantifiedstrategies.com/intraday-momentum-strategy/)
- **Noise-area trade profile in replications** — [D] [codecat-ops](https://github.com/codecat-ops/zarattini-2024-momentum-spy)
  - SPY 2020–26: +2.6 bps per trade, 41% win rate, payoff 1.69.
  - Quantitativo's ES replication: +2 bps per trade, 36% win rate, payoff 2.1.
  - SPY costs modeled at about 0.4 bps per round trip.
- **Maróy (QQQ, optimized exits):** Sharpe above 3.0 and annualized returns above 50% for the VWAP, VWAP & Ladder and Ladder exits (in-sample). — [S] [SSRN 5095349](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349)
- **Related intraday-momentum variant (BlackSwan Quants "Strategy 4" on SPY, 8-year window, 0 bps slippage)** — [D] [francesco-nicolo replication, commits through Sep 2026](https://github.com/francesco-nicolo/intraday-momentum-replication)
  - 259.2% return, Sharpe 1.036, max drawdown 8.4%, win rate 40%, beta −0.05.
  - Returns collapse to about zero at 2.2 bps of extra slippage per trade. Leveraged buy-and-hold survives about 218 bps.
- **Trade That Swing TQQQ ORB:** about 68% over one year, "including some commissions". — [S] [Trade That Swing](https://tradethatswing.com/tqqq-orb-strategy-68-backtesting-and-modifying-for-changing-conditions/)
- **QQQ ORB statistics (2-year window, 1,301 trades)** — [S] [ORB Setups](https://orbsetups.com/orb-stats/qqq-opening-range-breakout/)
  - Long and short breaks each won about 54% of the time.
  - The 30-minute long break won 58% of 232 trades. The 5-minute long break won 50% vs 53% for the 5-minute short break.
  - All 6 configurations had positive expectancy (cost treatment unstated).
- **WildWest000 on 4-hour bars (Jun 2023–May 2026):** +208% vs +144% for the daily version, Sharpe 1.06 vs 0.86. — [D] [WildWest000](https://github.com/WildWest000/tqqq-trading-strategy)

#### Daily / regime
- **Gayed & Bilello (Oct 1928–Oct 2015)**
  - $10,000 grew to $19M with S&P 500 buy-and-hold, vs $270M at 1.25×, $39B at 2× and $9T at 3×. — [S] [paper PDF](https://cmtassociation.org/wp-content/uploads/2025/08/2016-gayed-bilello.pdf); [S] [CXO](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/)
  - 2× version: Sharpe 0.51 vs 0.30 for buy-and-hold, assuming a 1% annual leverage cost and ignoring switching costs. — [S] [CXO](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/)
  - Unverified provenance: a search summary reports a gross Sharpe of 0.60 and max drawdown of −50% for the strategy, vs Sharpe 0.27 and −99% for constant 2× leverage. It also reports that all leveraged variants had smaller max drawdowns than unleveraged buy-and-hold in the four worst U.S. bear markets. — [S] [paper PDF](https://cmtassociation.org/wp-content/uploads/2025/08/2016-gayed-bilello.pdf)
- **FTLT, Composer-reported "out-of-sample" figures** (performance since each symphony was created; creation dates not visible; all are search snippets):

  | Version | Annualized | S&P/SPY | Other |
  |---|---:|---:|---|
  | ["Reddit Post Link"](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-reddit-post-link-HukRwDJLlYPLMbrQbua5) | ~59.7% | ~20.7% | Calmar ~1.03; another snippet lists "Annualized Return: 170.18%" (likely the backtest) |
  | ["Original"](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-original-WDQzBV4Mse7Zypxk4LtC) | ~56% | ~21% | Calmar ~1.11 |
  | ["FTLT 2.0"](https://www.composer.trade/trading-strategies/tqqq-ftlt-20-iM4mdWcn3DPeUNZPsYNW) | ~49% | ~22% | |
  | ["V4"](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-v4-no-better-qqqsinglestocks-pietros-maneos-10-yr-annualized-return-2694-644-calmar-ratio--sWVH0gg6XDilOgcPElW6) | ~63% | ~23% | Calmar ~1.32 |
  | ["V2 BlackSwan MeanRev"](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-v2-blackswan-meanrev-q3XCm7y3EE7WmGdXvjVj) | ~37.95% | ~17% | Calmar ~0.98 |
  | ["Full Package"](https://www.composer.trade/trading-strategies/tqqq-ftlt-full-package-diceroll-group-shorter-backtest-v2-ftl-oYl8FsMr6BjFgzbUjKoN) | ~119% | ~38% | |
  | ["with a bit of SOXL"](https://www.composer.trade/trading-strategies/tqqq-ftlt-with-a-bit-of-soxl-and--V8PMHSkT4yH87TLz2B7K) | ~80.8% | ~20.9% | Calmar 1.56, Sharpe 1.17 |
  | [60+ RSI mod (page attribution uncertain)](https://www.composer.trade/trading-strategies/reddit-tqqq-for-the-long-term-60-rsi-mod-nWP8uLmaVHGfBS7vh4fx) | ~104% | ~22% | Sharpe ~1.50 vs ~1.38; Calmar ~2.07 |

  - A separate description says FTLT returned "over +400% with an annualized return of 82%" from June 2022 "to today"; the end date is not shown. — [S] [TradingView FTLT port / Composer description](https://my.tradingview.com/script/CiW6StdS-TQQQ-for-the-Long-Term-Composer)
- **WildWest000 (Jan 2020–Jun 2026, $10k start, in-sample, no explicit commission/slippage model)** — [D] [WildWest000](https://github.com/WildWest000/tqqq-trading-strategy)

  | Metric | Strategy | TQQQ buy-and-hold |
  |---|---:|---:|
  | Total return | +917% | +661% |
  | Annualized | 43% | 37% |
  | Max drawdown | −42% | −82% |
  | Sharpe | 0.93 | 0.74 |

- **TQQQ/TMF 50/50:** CAGR 44.9% and total return above 5,800%, with a max end-of-month drawdown of 24.5% vs 49.1% for TQQQ alone. TQQQ alone returned over 10,000% (CAGR 54.4%) over its first 10+ years. — [S] [QuantifiedStrategies](https://www.quantifiedstrategies.com/triple-leveraged-etf-trading-strategy/)
- **BTAL/TQQQ 67/33:** 19.57% CAGR over 2012–2025, max drawdown −15.72%, Sharpe 1.14; beat the Nasdaq in 8 of 13 years. — [S] [Algomatic](https://www.algomatictrading.com/post/this-simple-2-etf-strategy-has-outperformed-the-nasdaq-for-13-years)
- **Alvarez UPRO/TQQQ:** compound annual return 24.4%, max drawdown 54%. — [S] [Alvarez Quant Trading](https://alvarezquanttrading.com/blog/upro-tqqq-leveraged-etf-strategy/)
- **SPY 200-day ±buffer TQQQ scripts:** claim a "~85% win percentage", with no cost assumptions stated. — [S] [TradingView](https://jp.tradingview.com/script/bznVflR1-SPY200SMA-4-3-TQQQ-QQQ-STRATEGY)

### Inferences
- The intraday edges are a few basis points per trade (noise area: +2 to +2.6 bps) or about 7¢/share (ORB on QQQ). That is the same order as one tick of spread. TQQQ/SQQQ have lower prices and wider spreads in relative terms than QQQ, so the TQQQ headline results are probably the most cost-fragile. No slippage-inclusive TQQQ replication was found.
- $400,616 of commissions on a $25k start implies very high turnover in the VWAP TQQQ run. Adding realistic spread and slippage, not just commission, would likely change the result substantially. No replication tested this.
- Composer's "out-of-sample" figures are platform simulations since creation, drawn from many forks. They carry selection and survivorship bias and are not audited live P&L.

### Gaps
- The noise-area paper's exact commission and slippage assumptions could not be confirmed (SSRN was blocked).
- Max drawdown and Sharpe for the ORB-on-TQQQ and VWAP-on-TQQQ variants could not be confirmed beyond "comparable".
- The Gayed & Bilello annualized return, volatility and max drawdown for each leverage level were not retrieved (PDF blocked). Only terminal values and the 2× Sharpe (0.51 vs 0.30) were.
- Rules and numbers could not be retrieved for Alvarez's UPRO/TQQQ strategy, SetupAlpha's "3x Leveraged ETF Strategy: 2,600% Return With 38% Drawdown" ([Medium](https://medium.com/@setupalpha.capital/3x-leveraged-etf-strategy-2-600-return-with-38-drawdown-trading-strategy-rules-f4dad806bc25)), or Brightwork's 200-day-MA LETF article ([link](https://www.brightworkresearch.com/using-letfs-combined-with-the-200-day-moving-average-trading-approach/)).
- No QuantifiedStrategies article dedicated to TQQQ↔SQQQ switching was found; a site-restricted search returned none.

## Q3. Which have out-of-sample or post-publication evidence, and how did they perform in 2022, 2025 and 2026?

### Takeaway
Post-publication evidence comes mostly from independent GitHub and blog replications, and it is unfavorable for the intraday systems:
- **ORB:** reproduces gross but nets about zero after costs, per a replication on five index markets run through June 2026 and published 25 Sep 2026.
- **Noise-area momentum:** strong in 2020–2024 (2022: +25.8% vs SPY −19.5%), then lost money in 2025 (−4.9%) and in 2026 through July (−12.9%).
- **200-day rules:** after 2016 they cut drawdowns but returned less than buy-and-hold over the 2016–2026 bull market.
- **FTLT:** only Composer's own "out-of-sample" numbers exist.

2022 was the best year for most of the intraday long/short systems; it carried most of the ORB profits.

### Cited Findings

#### ORB
- Replication findings through Feb 2023 — [D] [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq):
  - 2022 alone is 76% of the NQ-filtered PnL and 38% of the unfiltered PnL.
  - The filter lost money in 2017, 2020 and early 2023.
  - The sharp 2023 drawdown "hints the edge was already decaying at the end of the sample".
  - "Published ORB results are known to concentrate in 2020–2022."
  - Extending the test to 2023–2026 is listed as an open task.
- 25 Sep 2026 replication on NQ, SPX, Dow, DAX and FTSE CFDs, Jan 2015–Jun 2026, 2,899–2,937 sessions per market — [S] [mql5 blog](https://www.mql5.com/en/blogs/post/776235):
  - Gross: "+0.131 R on NQ, as in the paper".
  - Net: "no market distinguishable from zero, four of five negative".
  - Gross, the rule beats a random direction by +0.10 to +0.13R at |t| ≥ 2 in NQ, DAX and FTSE.
- A 2026 SSRN paper by Mulham Fetna is titled "Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data". Only the title was retrieved. — [S] [SSRN 7428398](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398)
- Micro Nasdaq-100 futures (MNQ) falsification study (May 2026, 2024–2026 data) — [S] [arXiv 2605.04004](https://arxiv.org/pdf/2605.04004):
  - Across 14 intraday signal families, none met all criteria at once: out-of-sample t ≥ 2, at least 30 out-of-sample trades, positive net return after a 2-point round-trip cost, and multi-year stability.
  - The gross edge available with next-bar-open execution was about 0.07–1.50 points, below the 2-point cost.
  - "Gap continuation short" had t = 3.23 and a mean net of +14.52 points, but on only 22 trades.
- Trade That Swing (TQQQ ORB): in the last one to two months of its sample (date not shown), as TQQQ fell, short-only made +5.56% vs −6.31% for long-and-short. — [S] [Trade That Swing](https://tradethatswing.com/tqqq-orb-strategy-68-backtesting-and-modifying-for-changing-conditions/)

#### Noise-area intraday momentum
- codecat-ops replication (SPY Jul 2020–Jul 2026; ES futures May 2024–Jul 2026; closed Jul 2026) — [D] [CONCLUSIONS](https://github.com/codecat-ops/zarattini-2024-momentum-spy/blob/main/docs/CONCLUSIONS.md); [D] [README](https://github.com/codecat-ops/zarattini-2024-momentum-spy):

  | Period | Result |
  |---|---|
  | Full 2020–26 | Sharpe 1.11; alpha +16.7%/yr (t 2.85); beta −0.06 |
  | Each year 2020–2024 | Sharpe 1.4–2.0; alpha 23–28%/yr |
  | 2022 | +25.8% vs SPY −19.5% |
  | 2025 | −4.9% (Sharpe −0.27) |
  | 2026 to July | −12.9% (Sharpe −1.91) |

  - ES returns correlate 0.97 with SPY, so the decline is not a data-feed artifact.
  - Costs of about 0.4 bps per round trip are ruled out as the cause; recent expectancy is about −0.6 bps per trade.
  - Verdict: "NOT allocable today... nor can it be written off as 'dead'". The paper itself shows weak multi-year stretches (2012–2015) followed by recovery.
- Re-optimizing does not rescue it — [D] [codecat-ops](https://github.com/codecat-ops/zarattini-2024-momentum-spy):
  - In a 27-variant grid following Maróy, judged with a Deflated Sharpe Ratio, the in-sample winner was the paper's original configuration.
  - Quarterly walk-forward reselection gave Sharpe 0.57 vs 0.92 for the fixed configuration, switching 14 times in 19 quarters.
  - In 2024–26 the "base" exit beat the paper's "final" exit (Sharpe about 0.7 vs about 0). The author flags this as post hoc.
- A QuantConnect implementation's results were "positive, but not nearly as impressive as in the original paper". — [S] [QuantConnect #17091](https://www.quantconnect.com/forum/discussion/17091/beat-the-market-an-effective-intraday-momentum-strategy-for-s-amp-p500-etf-spy/)
- A post-publication test from June 2024 on SPY and QQQ was set up with consolidated (SIP) minute data, $0.01–$0.02/share slippage and $0.0035/share commission. Its pass criteria were out-of-sample Sharpe ≥ 0.75, positive out-of-sample returns and profits in at least 70% of years. Results were not in the fetched content. — [D] [POB-CL-DT PR #13, 30 Sep 2026](https://github.com/patrickobirmingham-eng/POB-CL-DT/pull/13)

#### VWAP and Maróy
- I found no independent post-publication test of the VWAP QQQ/TQQQ system or of Maróy's QQQ exits. The disciplined re-run of the Maróy grid on SPY did not confirm the improvements. — [D] [codecat-ops](https://github.com/codecat-ops/zarattini-2024-momentum-spy)

#### 200-day moving average / Gayed & Bilello
- RafaelPF07/evotrader PR #4 (22 Sep 2026): 200-day trend filter with 1.5× leverage, borrowing at T-bills + 1%, idle cash earning T-bills; development data through 2021 — [D] [evotrader PR #4](https://github.com/RafaelPF07/evotrader/pull/4)

  | Sample (CAGR / Sharpe / max drawdown) | Buy-and-hold | Trend filter + 1.5× |
  |---|---|---|
  | Development (US ETFs) | 10.6% / 0.64 / −43% | 10.5% / 0.74 / −21% |
  | Sectors (new universe) | 8.9% / 0.47 / −49% | 5.4% / 0.30 / −40% |
  | Countries (new universe) | 9.3% / 0.44 / −64% | 10.6% / 0.56 / −31% |

  - The filter "cut max drawdown on all 18 new ETFs" but lowered returns on 13 of them.
  - Post-publication U.S., 2016–26: "12.8% vs 14.1%, in line with the documented decay of published anomalies". The PR does not label which figure is the strategy.
- SetupAlpha RealTest test of the Gayed & Bilello rule on ETFs (periods not shown) — [S] [SetupAlpha Substack](https://setup4alpha.substack.com/p/tested-award-winning-trading-strategy-realtest):

  | Asset | Buy-and-hold | 200-day rule |
  |---|---|---|
  | SPY (CAGR / max drawdown) | 6.92% / −48.56% | 7.74% / −22.62% |
  | QQQ (CAGR / max drawdown) | 8.19% / −80.14% | 10.40% / −27.02% |
  | TQQQ, $10,000 start (final value / max drawdown) | ~$3.96M / −81.61% | ~$1.12M / −57.19% |

  - The TQQQ figures appeared in a search summary alongside this article; the attribution is likely but unverified.
  - The article warns that a slow filter "can sell after a large decline has already happened, then buy back after the strongest part of the recovery... With a 3x ETF, it can be extremely expensive".
- Henrique Centieiro — [S] [Substack](https://henriquecentieiro.substack.com/p/buy-above-or-below-the-200-ma-the):
  - QQQ with a 200-day MA, 2000–2024: 791% vs 428% buy-and-hold; max drawdown 28.6% vs 83%.
  - TQQQ with a 225-day MA, 2011–2025: 4,067% vs 10,806% buy-and-hold; max drawdown 69.9% vs 81.7%.
- 2025 context: the tariff-driven crash began on 2 Apr 2025, and the tariff pause announced on 9 Apr 2025 produced the largest index gains in years. — [S] [Wikipedia: 2025 stock market crash](https://en.wikipedia.org/wiki/2025_stock_market_crash)
- WildWest000 (in-sample), Jan–May 2025 downturn: strategy +12% vs TQQQ buy-and-hold −11%; max drawdown −19% vs −57%. — [D] [WildWest000](https://github.com/WildWest000/tqqq-trading-strategy)

#### FTLT
- Only Composer-reported "out-of-sample" annualized figures (see Q2) and a "since June 2022: +400%, 82% annualized" claim exist. I found no independent replication and no calendar-year 2022, 2025 or 2026 returns. — [S] [Composer FTLT Original](https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-original-WDQzBV4Mse7Zypxk4LtC); [S] [TradingView port](https://my.tradingview.com/script/CiW6StdS-TQQQ-for-the-Long-Term-Composer)

### Inferences
- Intraday long/short systems on index ETFs make most of their money in high-volatility trending selloffs (2008, 2020, 2022) — the "long volatility" signature. They stall or lose in grinding or choppy markets (ORB in 2017 and 2023; noise area in 2025–2026). For a bull/bear LETF pair, this suggests the bear-fund leg produced much of the historical profit, and that the edge depends on the volatility regime.
- The "12.8% vs 14.1%" figure most plausibly means the trend filter returned 12.8% vs 14.1% for buy-and-hold, given the "in line with decay" wording. The PR does not say so explicitly.
- Daily 200-day rules sidestep long bear markets such as 2022 but pay in V-shaped recoveries such as April 2025, as SetupAlpha warns. No source in this session quantified the 2025 whipsaw for TQQQ, UPRO or SPXL.

### Gaps
- I found no 2025 or 2026 calendar-year returns for: ORB on QQQ/TQQQ specifically, the VWAP system, FTLT, Gayed & Bilello's rule on TQQQ/UPRO/SPXL, or the QuantConnect community algorithms.
- I found no exact 2022 calendar-year return for ORB on TQQQ, VWAP on TQQQ, FTLT, or the 200-day SMA on TQQQ.
- The Fetna (SSRN 7428398) and Quantitativo ES/NQ ([link](https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq)) results were not retrieved: the domains were blocked and the search quota was exhausted.

## Q4. Do any publications address WHEN to flip intraday from the bull fund to the bear fund (vs going flat), and what did they find?

### Takeaway
I found no publication that tests "flip TQQQ→SQQQ" head-to-head against "go flat". The main papers do make different design choices:
- **ORB:** takes one directional trade per day and goes flat after a stop, with no reversal.
- **Noise area:** flat by default. A trailing stop first takes the position flat, and the opposite side is taken only if price breaks the opposite band at a later 30-minute check.
- **VWAP system:** always in the market, flipping at every VWAP cross, with very high turnover.

End-of-day research shows the last 30 minutes tend to continue the day's direction, driven by LETF rebalancing and option-dealer hedging, and that this pressure reverses at the next open.

### Cited Findings
- **ORB:** one entry at 09:35 in the first candle's direction. Exits are only via the stop (−1R), the target (+10R) or the close; there is no intraday reversal. — [D] [giovannibrusco](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Noise area:**
  - The design stays "flat as long as price stays within that zone, only treating price breaks above or below those boundaries as evidence of a genuine intraday trend". — [S] [Concretum Bands / search summary](https://www.tradingview.com/script/CUpWCZhe-Concretum-Bands/)
  - The long trailing stop is max(upper band, VWAP) and the short stop is min(lower band, VWAP). So a long is normally stopped out to flat before a short can trigger below the lower band at a later 30-minute check. — [S] [QuantConnect #17091](https://www.quantconnect.com/forum/discussion/17091/beat-the-market-an-effective-intraday-momentum-strategy-for-s-amp-p500-etf-spy/)
  - The replication engine explicitly models "entry/exit/flip". — [D] [codecat-ops](https://github.com/codecat-ops/zarattini-2024-momentum-spy)
- **Exit choice (when to go flat) has mattered more than entry tweaks recently.** In 2024–26 the "base" exit beat the paper's "final" exit, Sharpe about 0.7 vs about 0 (post hoc). Maróy's VWAP and Ladder exits claimed Sharpe above 3 in-sample. — [D] [codecat-ops](https://github.com/codecat-ops/zarattini-2024-momentum-spy); [S] [SSRN 5095349](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349)
- **VWAP system:** long above VWAP and short below it, i.e., an always-in stop-and-reverse. The TQQQ run paid $400,616 in commissions on a $25,000 start. — [S] [Bear Bull Traders](https://members.bearbulltraders.com/magic-of-vwap-the-holy-grail-of-day-trading-systems/)
- **Rules for handling the pair:** never hold both sides; when switching, sell the entire opposite side before buying, in the same session. — [S] [Lumibot](https://lumibot.lumiwealth.com/agents_example_bull_bear_leveraged_etf.html)
- **WildWest000** deliberately keeps the bear leg in cash in its default engine ("never holds SQQQ"). It uses SQQQ only at 20% in a "crisis" or as a hedge when TQQQ's RSI is overbought. — [D] [WildWest000](https://github.com/WildWest000/tqqq-trading-strategy)
- **Practitioner evidence:** in a falling TQQQ market, short-only beat long-and-short (+5.56% vs −6.31%). — [S] [Trade That Swing](https://tradethatswing.com/tqqq-orb-strategy-68-backtesting-and-modifying-for-changing-conditions/). Over two years, long and short QQQ ORB win rates were about equal (~54%). — [S] [ORB Setups](https://orbsetups.com/orb-stats/qqq-opening-range-breakout/)
- **End-of-day flows:**
  - Last-half-hour market returns show momentum "driven by hedging demand of option market makers and the rebalancing of leveraged ETFs". LETF rebalancing "takes place almost exclusively at the end-of-day", in the same direction as the index's daily move. — [S] [Baltussen, Da, Lammers & Martens, "Hedging demand and market intraday momentum" (PDF)](https://academicweb.nd.edu/~zda/intramom.pdf)
  - The last-30-minute return is positively predicted by the return from the previous close up to that point, and the effect reverts over the next days. — same source.
  - A large negative (positive) aggregate gamma imbalance produces end-of-day momentum (reversal), and the LETF-driven effect is economically larger. The effects "quickly revert at the next day's open". — [S] ["The Role of Leveraged ETFs and Option Market Imbalances on End-of-Day Price Dynamics"](https://www.researchgate.net/publication/355381896_The_Role_of_Leveraged_ETFs_and_Option_Market_Imbalances_on_End-of-Day_Price_Dynamics)
  - See also [S] [Baltussen, Da & Soebhag, "End-of-Day Reversal" (PDF)](https://www3.nd.edu/~zda/EOD.pdf).
- **The noise-area paper** explicitly avoids restricting trading to the last 30 minutes and enters as soon as an imbalance appears. — [S] [SSRN 4824172](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172)
- **MNQ futures:** the only intraday family with a significant net edge was "gap continuation short", and it had only 22 trades. — [S] [arXiv 2605.04004](https://arxiv.org/pdf/2605.04004)

### Inferences
- Once realistic costs are included, the published evidence favors "flat by default; take the opposite fund only on a fresh, independent breakout" (the noise-area design) over mechanical stop-and-reverse (the VWAP design). Each flip pays two spreads, and the per-trade edges are a few basis points.
- For LETF pairs, flipping into the bear fund late on a strongly down day goes with the end-of-day LETF and dealer flows. Holding the bear fund overnight then faces the next-open reversal Baltussen et al. document.
- Staying flat after a stop (the ORB design) avoids repeated whipsaw losses in choppy markets, which is when these systems lose most.

### Gaps
- I found no head-to-head study of "reverse into the bear fund" vs "go flat" for TQQQ/SQQQ or any other LETF pair.
- I could not retrieve a long-only vs short-only vs long/short breakdown for the ORB, VWAP or noise-area papers. That would show how much of each edge comes from the short (bear) side.
- The publication years and final versions of the Baltussen et al. papers were not verified in this session; the PDFs were blocked.

## Q5. Are there publications comparing "buy the inverse ETF" vs "short the bull ETF" for the bearish side (costs, decay, borrow, reverse splits)?

### Takeaway
Only practitioner and forum pieces plus one April 2025 arXiv paper address this. None is a rigorous TQQQ-vs-SQQQ cost study. The recurring points:
1. **Exposure:** within a single day the two are nearly equivalent. Over several days, shorting the bull fund harvests its volatility decay, while a long inverse fund suffers its own decay (but compounds favorably in a smooth decline).
2. **Shorting frictions:** shorting needs a borrow. SQQQ is reportedly under 1% to borrow; one snippet puts TQQQ at about 2–3%. Shorts also need margin and carry unlimited-loss risk.
3. **Reverse splits:** inverse 3× funds reverse-split repeatedly. SQQQ did 1-for-5 on 7 Nov 2024 and again on 20 Nov 2025, which affects historical data, share-count logic and options.
4. **Shorting both funds** to harvest decay is a known but risky trade.

### Cited Findings
- **QuantConnect #2278:** "might be possible to short the opposite leveraged ETF rather than going long due to decay considerations". — [S] [QuantConnect #2278](https://www.quantconnect.com/forum/discussion/2278/simple-algo-trades-tqqq-sqqq-based-on-volatility/). A related thread asks "Why isn't TQQQ opposite of SQQQ?" — [S] [QuantConnect #14247](https://www.quantconnect.com/forum/discussion/14247/why-isn-039-t-tqqq-opposite-of-sqqq/)
- **TradingView idea, "Short SQQQ instead of buying TQQQ / Short TQQQ instead of buying SQQQ":** performance is "up to 3% better by trading the inverse of the intention of the ETF". — [S] [TradingView idea](https://vn.tradingview.com/chart/TQQQ/Ge8Noo5r-Short-SQQ-instead-of-buying-TQQ-Short-TQQ-instead-of-buying-SQQ)
- **Elite Trader, "Long TQQQ vs Short SQQQ":** "SQQQ costs less than 1% to borrow usually". A poster claims more leverage is available via SQQQ because of its lower share price and short-margin treatment. — [S] [Elite Trader](https://www.elitetrader.com/et/threads/long-tqqq-vs-short-sqqq.352452/). See also a Bogleheads thread on shorting SQQQ long-term. — [S] [Bogleheads](https://www.bogleheads.org/forum/viewtopic.php?t=368509)
- **TQQQ borrow fee:** about 2–3% annually in recent data, per a search summary of Fintel. Unverified; borrow fees vary daily. — [S] [Fintel TQQQ](https://fintel.io/ss/us/tqqq)
- **Financing cost inside the bull fund:** TQQQ controls about $3 of exposure per $1 of NAV, the extra $2 coming from swaps. That financing runs about $834 a year per $10,000 invested, on top of the "0.82% fee". — [S] [24/7 Wall St, 23 Sep 2026](https://247wallst.com/investing/etf/2026/09/23/tqqq-pays-interest-on-2-of-every-3-it-holds-the-financing-charge-the-0-82-fee-never-mentions/). An older comparison page lists a 0.95% expense ratio for both TQQQ and SQQQ. The conflict likely reflects fee changes over time. — [S] [Pluang comparison](https://pluang.com/en/compare/sqqq-vs-tqqq)
- **Shorting both funds to harvest decay** — [S] [Seeking Alpha 4629981, "TQQQ And SQQQ: Their NAV Erosion Could Be Your (Combined) Gain"](https://seekingalpha.com/article/4629981-tqqq-and-sqqq-nav-erosion-your-gain):
  - Short TQQQ and SQQQ together; the pair has a "recent annual decay rate of 21.175% and expected returns of around 18%".
  - As TQQQ rises, the TQQQ short grows as a share of the portfolio while the SQQQ short shrinks, so the position needs rebalancing.
  - Related pieces (titles only): [S] [Valuelytica, "Volatility Decay Capturing"](https://valuelytica.substack.com/p/vdc-qqq); [S] [Seeking Alpha instablog, market-neutral-plus LETF shorting](https://seekingalpha.com/instablog/604756-steven-benharris/91413-implementing-a-market-neutral-plus-leveraged-etf-shorting-strategy)
- **Academic framing (Apr 2025):** for leverage β > 1, one unit of the LETF plus β units short the underlying "captures the positive expected compounding effect". For β < 0, "short ETF positions can be substituted with long positions in inverse ETFs". — [S] [arXiv 2504.20116, "Compounding Effects in Leveraged ETFs: Beyond the Volatility Drag Paradigm"](https://arxiv.org/html/2504.20116v1)
- **SQQQ reverse splits:**
  - 1-for-5, effective before the open on 7 Nov 2024; new CUSIP 74347G192. — [S] [Nasdaq Trader ECA2024-536](https://nasdaqtrader.com/TraderNews.aspx?id=ECA2024-536); [S] [MIAX alert, 6 Nov 2024](https://www.miaxglobal.com/alert/2024/11/06/miax-exchange-group-options-markets-corporate-action-alert-proshares-4)
  - 1-for-5, effective before the open on 20 Nov 2025; new CUSIP 74350P675. — [S] [MIAX alert #57665, 18 Nov 2025](https://www.miaxglobal.com/sites/default/files/alert-files/SQQQ1_Reverse_Split_57665.pdf)
- **Other reverse splits and decay:**
  - TZA (−3× Russell 2000) "was scheduled for a 1-for-10 reverse split in mid-July 2026". This is a single secondary source and unverified.
  - The same source says inverse 3× funds reverse-split repeatedly because daily-reset decay pushes their price down, and that decay "usually becomes noticeable after 3–5 trading days".
  - Source: [S] [Curved Trading](https://curvedtrading.com/articles/en/investing/index-leveraged-inverse-etfs/)
  - Direxion has done batch reverse/forward splits (16 ETFs, Mar 2013). — [S] [Benzinga](https://www.benzinga.com/news/13/03/3382855/direxion-announces-reverse-forward-splits-for-16-etfs)
  - A Seeking Alpha article focuses on SQQQ decay and drift. — [S] [Seeking Alpha 4856799](https://seekingalpha.com/article/4856799-leveraged-etf-drift-watch-list-and-focus-on-sqqq)

### Inferences
- For positions opened and closed in the same session, long SQQQ and short TQQQ give nearly the same exposure. They differ in:
  - each fund's spread and liquidity;
  - borrow availability and hard-to-borrow recalls;
  - short-sale circuit-breaker rules, which can block shorting TQQQ on exactly the crash days a bear signal fires (Reg SHO Rule 201 — background knowledge, not verified this session);
  - margin, since brokers typically require elevated short margin for 3× LETFs.

  Long SQQQ avoids all the borrow, locate and short-restriction issues. That is probably why practitioner systems such as FTLT and the QuantConnect rotation use the inverse fund.
- For bear positions held several days, the two diverge:
  - Shorting the bull fund benefits from that fund's volatility decay, but the gain is capped at 100% and the loss is unbounded.
  - A long inverse fund compounds favorably in a smooth decline but decays in choppy markets.

  Which is better depends on the price path. No rigorous TQQQ/SQQQ comparison was found.
- Reverse splits matter operationally: they affect backtests (adjusted vs unadjusted prices), share-count logic and options on the inverse funds.

### Gaps
- I found no peer-reviewed or rigorous empirical study comparing long SQQQ vs short TQQQ (or SPXS vs short SPXL, TZA vs short TNA, etc.) net of borrow, margin and short-sale restrictions.
- Current borrow fees for TQQQ, SPXL, TNA, LABU and the others, and brokers' intraday short-margin rules for 3× LETFs, were not retrievable; the broker and data sites were blocked.
- A full reverse-split history for SPXS, SPXU, TZA, LABD, FAZ, TECS and DUST could not be compiled: issuer and exchange sites were blocked and the search quota was exhausted.
