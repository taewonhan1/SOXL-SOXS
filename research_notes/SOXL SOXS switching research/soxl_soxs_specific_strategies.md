# Published SOXL/SOXS switching and two-sided trading methods (intraday to a few weeks), as of 2026-10-03

Scope: published, findable rules for moving between SOXL and SOXS (or between SOXL and cash/other assets with a SOXS leg) on intraday-to-few-week horizons. For each method the notes give the rules, the claimed results, any independent test, and red flags. US-listed SOXL/SOXS only; Korean-language commentary is included.

**How the sources were reached (applies to every section).** The proxy blocked direct fetching of composer.trade, tradingview.com, seekingalpha.com, tickeron.com, benzinga.com, reddit.com, namu.wiki, naver.com, tistory, mt.co.kr and most other news and blog sites. WebSearch also refused reddit.com outright ("domain not accessible to our user agent"). The session's 200-call WebSearch budget ran out partway through. So:
- Details for Composer, TradingView, Seeking Alpha, Tickeron, Collective2, Pair Trading Lab and the Korean news sites come from **search-result snippets and summaries**, not full pages. Treat these as second-hand. The summaries sometimes mixed up numbers; these cases are flagged.
- **YouTube** was reachable. Video titles, publish dates and full descriptions were read directly through YouTube's own endpoints. Transcripts could not be read.
- **Public GitHub repositories** were cloned and read directly.
- Price facts for 2022, April 2025 and 2026 were **checked against the project's own daily bars** (`/home/user/SOXL-SOXS/data/soxlab/bars_1day/adjusted/{SOXL,SOXS,SOXX}.parquet`, 2010-03-11 to 2026-09-25). These are marked "verified (local data)".
- The project's own GitHub repo (github.com/taewonhan1/SOXL-SOXS) came up in searches. It was not used as an external source.

## Q1. What concrete SOXL<->SOXS switching rules have been published, with exact rules and claimed numbers?

### Takeaway
- **Composer symphonies.** The published, rule-explicit SOXL<->SOXS switchers are almost all daily close-to-close systems. Examples: "SOXL/SOXS" (fade 10-day surges of more than 31% or 25%), "SOXX Group", "SOXL RSI Strategy" and "SOXL Growth v2.4.5 RL" (a decision tree with RSI, volatility and drawdown thresholds tuned to four decimal places).
- **Intraday scripts.** The only explicit intraday SOXL/SOXS rules found are the TradingView "SOXL Breakout" overlay and an open-source Korean KIS-API bot. That bot added a VWAP-based SOXL/SOXS "dual momentum" flip and then removed the SOXS side 12 days later.
- **Claimed results.** Vendors either publish no numbers or very large ones (Tickeron +551% annualized at 79% win rate; Pair Trading Lab +1,379% in 2023; a ratio-chart idea claiming "5X annually"). None of these come with costs, borrow fees or an out-of-sample audit.
- **The one live tracked record** is Collective2's "AI SOXL SOXS intraday". It finished at -2.1% with a -37.9% maximum drawdown and stopped trading.

### Cited Findings

#### A. Composer.trade symphonies (daily rebalanced; content from search snippets because composer.trade is blocked)
- **"SOXL/SOXS"** (author and date unknown).
  - Rules: every day, check the **10-day move** of SOXL and SOXS.
    - If SOXL rose **more than 31%** over 10 days, switch to SOXS (betting on a pullback).
    - If SOXS rose **more than 25%**, buy SOXL (betting on a bounce).
    - If neither, and SOXL RSI is **below 31**, buy TECL (3x tech).
    - Otherwise hold BOXX (a T-bill-like ETF).
  - Composer's own description: "fades extreme 10-day moves… flips to the opposite side after big surges". It is tagged "contrarian mean-reversion".
  - Claimed returns: none appeared in the snippets.
  - Sources: [Composer SOXL/SOXS](https://www.composer.trade/trading-strategies/soxlsoxs-zBYLpDcWNegfd8j46tfs); [same page, contrarian tag](https://www.composer.trade/trading-strategies/soxlsoxs-zBYLpDcWNegfd8j46tfs?q=contrarian+mean-reversion)
- **"SOXL RSI Strategy"**.
  - Rules: a daily tactical semiconductor strategy that "rides SOXL in uptrends, buys deep dips, and shifts to SOXS, bonds, T-bills, or UVXY when momentum weakens or overheats". It uses RSI, moving averages and "big day" triggers. The exact thresholds were not visible in the snippets.
  - Claimed out-of-sample (OOS) results: annualized return about **25.3%** versus SPY's 20.2%, drawdown about **18.8%**, beta 0.54, Calmar about 1.35. The OOS window was not shown.
  - Source: [Composer SOXL RSI Strategy](https://www.composer.trade/trading-strategies/soxl-rsi-strategy-XJKF0TG7NrcX33NQrfyW)
- **"SOXX Group"**.
  - Rules: "Buys SOXL after sharp drops, flips to SOXS after big spikes, and uses an RSI 'heat gauge' plus VIX/market checks." Daily, "very aggressive", semiconductor-only.
  - Claimed results: OOS Sharpe about **1.55** versus about 1.33 for the S&P 500, but maximum drawdown **68.96%**.
  - Sources: [Composer SOXX Group](https://www.composer.trade/trading-strategies/soxx-group-7PBSP926Mp40r6bPnP0j); [same, leveraged-ETF tag](https://www.composer.trade/trading-strategies/soxx-group-7PBSP926Mp40r6bPnP0j?q=leveraged+ETFs)
- **"SOXX Trend Following"**. A 50/50 blend of a slow and a faster trend rule on SOXX: hold SOXX in an uptrend, otherwise SHV (cash-like). It has no SOXS leg and is included only because the brief named it. Source: [Composer SOXX Trend Following](https://www.composer.trade/trading-strategies/soxx-trend-following-EuYlSCqgDqiAeYWP2SQC)
- **"SOXL Growth v2.4.5 RL"**.
  - Composer description: a "daily, rules-based swing strategy in 3x tech/semis/S&P/Treasury ETFs… in good times it piles into the fastest winners; in stress it flips to inverse ETFs". Bull legs: SOXL, TQQQ, SPXL, TMF. Inverse legs: SOXS, SQQQ, SPXS, TMV. Inputs: volatility, RSI, recent return and drawdown. Source: [Composer SOXL Growth v2.4.5 RL](https://www.composer.trade/trading-strategies/soxl-growth-v245-rl-CW8oWU12S6vEvn2Hh7jD)
  - **Exact decision tree, from a third-party Python port** (GitHub user IznogoudQc, code moved from a production PythonAnywhere job on 2026-05-01). The port's comment says "Achat/vente à la clôture du jour du signal" (buy/sell at the close of the signal day). Source: [IznogoudQc/soxl-growth, SOXL_Growth_v245RL.py](https://github.com/IznogoudQc/soxl-growth)
    - **Branch A: SOXL's 60-day maximum drawdown is 50% or more.**
      - If TQQQ's 14-day standard deviation (std) is 18 or less:
        - If TQQQ's 100-day std is 3.8 or less, hold the top 2 of SOXL/TQQQ/SPXL by 21-day return.
        - Otherwise, if TQQQ RSI(30) is 50 or more: hold **SOXS** if TQQQ's 30-day std is 5.8 or more, else SPXL.
        - Otherwise (RSI below 50):
          - If TQQQ's 8-day return is -20% or worse, hold SOXL.
          - Else, if TQQQ's 200-day max drawdown is 85% or less, hold the bottom 2 of TMV/SQQQ/SPXS by 3-day return; else hold SOXL.
      - If TQQQ's 14-day std is above 18:
        - If TQQQ's 30-day return is -10% or worse, hold the bottom 2 of TMV/SQQQ/SPXS.
        - Otherwise hold the top 3 of SOXL/TQQQ/TMF/SPXL by 21-day return.
    - **Branch B: SOXL's 60-day maximum drawdown is below 50%.**
      - If SOXL RSI(32) is 62.1995 or less:
        - If SOXL's 105-day std is 4.9228 or less, hold **SOXL**.
        - Otherwise, if SOXL RSI(30) is 57.49 or more: hold **SOXS** if SOXL's 30-day std is 5.4135 or more, else the top 3 bull ETFs.
        - Otherwise:
          - If SOXL's 32-day return is -12% or worse, hold SOXL.
          - Else, if SOXL's 250-day max drawdown is 71% or less, hold **SOXS**; else hold SOXL.
      - If SOXL RSI(32) is above 62.2, hold **SOXS** if SPXL RSI(32) is 50 or more; otherwise hold the top 3 bull ETFs.
    - The port's backtest starts in 2020 and has **no commission or slippage terms**. Its strategy and backtest docs are empty templates.
- **Other Composer symphonies with SOXL/SOXS legs whose rules were not retrievable:**
  - [SOXX RSI Machin, updated from Mr D](https://www.composer.trade/trading-strategies/-soxx-rsi-machin-updated-from-mr-d-2mrBJuLeQBzyrP673efl?q=contrarian+momentum)
  - [TQQQ FTLT with a bit of SOXL and 🧦](https://www.composer.trade/trading-strategies/tqqq-ftlt-with-a-bit-of-soxl-and--V8PMHSkT4yH87TLz2B7K?q=RSI+&+moving+average+signals=)
  - [TCCC Basic Logic: VIX volatility and limit SOXL exposure](https://www.composer.trade/trading-strategies/tccc-basic-logic-vix-volatility-and-limit-soxl-exposure-gyE2roZftlbcUF07IvA2)
  - [BB V3.0.4.2a merged with v2 TEC/SOX/HIB Baller](https://www.composer.trade/trading-strategies/bb-v3042a-merged-with-v2-tecsoxhib-baller-uvxy-and-v1-new-soxl-baller-3HtenzDBOEtuQOeiTAyZ?q=Swing+trading)
  - [V2 Beat the Market (SOXX/SOXL mod)](https://www.composer.trade/trading-strategies/v2-beat-the-market-michael-b-mod-replace-qqq-and-qld-with-soxx-and-soxl-OTwSyij1wp8AlrLDNrs9?q=QQQ%29)

#### B. TradingView scripts and ideas (content from search snippets because tradingview.com is blocked)
- **"SOXL Breakout"** (open-source indicator; author and date not visible). It is a day-trading overlay for leveraged ETFs on the **5-minute** chart.
  - Levels: at **09:25 ET** it captures the premarket open and draws a **TRIGGER** at a configurable percentage above that open (**default +1.41%**). When price touches the trigger during regular hours (RTH), it opens a simulated long.
  - Stop: **-8% below the trigger** by default. The stop is active at any time while in a position, including the next day's premarket.
  - Exit: the default is to auto-sell at the **next day's 09:20 ET open price**. This makes it an overnight-hold breakout.
  - Sizing: account size times a deploy percentage, rounded down to 100 shares.
  - **SOXS leg:** if the trigger was never hit during RTH on a **Monday, Thursday or Friday**, it draws a "SOXS ENTRY" line at the **15:55 close** as a bearish inverse entry.
  - Claimed results: none found.
  - Sources: [TradingView SOXL Breakout](https://tr.tradingview.com/script/a0OFHNAL-SOXL-Breakout); [es.tradingview SOXL scripts list](https://es.tradingview.com/scripts/amex:soxl/)
- **"SOXL Trend Surge v3.0.2 – Profit-Only Runner"** (open-source; long-only, no SOXS).
  - Entry: all of the following must hold:
    - price above the 200 EMA, and outside a small buffer zone around it;
    - Supertrend bullish;
    - ATR rising;
    - volume above its 20-bar average;
    - trades only between **9 AM and 2 PM ET**.
  - Exit: take partial profit at **+2×ATR** if the trade has been held at least 2 bars, then trail the rest at **1.5×ATR**. There is **no hard stop**. Holds can run "multiple days to even several months".
  - Backtest range: **May 8, 2020 – May 23, 2025**.
  - Sources: [TradingView Trend Surge v3.0.2](https://www.tradingview.com/script/9O8nW0Mu-SOXL-Trend-Surge-v3-0-2-Profit-Only-Runner/); variant [Refined Reality Runner](https://it.tradingview.com/script/y3aNnbnH-SOXL-Trend-Surge-v3-0-2-Refined-Reality-Runner)
- **"SOXL Trend Surge v4.2 – Tiered Exit + BE Buffer"** (by MrStockaton; **45-minute** chart).
  - Entry: all of the following must hold:
    - price above the 200 EMA by at least 0.5%;
    - Supertrend bullish, ATR rising, volume above its 20-bar SMA;
    - **VIX below 28**;
    - a 15-bar cooldown since the last exit (**80 bars after a losing trade**);
    - entries only between **14:00 and 19:00 UTC** (about 10 AM to 3 PM ET).
  - Exits:
    - 33% of the position at **1.5×ATR**;
    - 33% at **3.0×ATR**;
    - the last 33% on a 1.5×ATR trailing stop;
    - after the first tier fills, a breakeven stop at entry + 0.3×ATR;
    - **forced full exit if VIX rises above 35**.
  - Disclosed results: **maximum intrabar drawdown $680.78, or -84.3% of peak equity**. In **2022 it averaged -$33.74 per trade, about -$490 on a $500 starting account**.
  - Source: [TradingView Trend Surge v4.2](https://www.tradingview.com/script/8awiG47H-SOXL-Trend-Surge-v4-2-Tiered-Exit-BE-Buffer/)
- **"Galac III SOXL"** (invite-only; long-only swing). Uses adaptive EMAs as a trend filter, relative-volume confirmation, volatility-adjusted position sizing and dynamic take-profit/stop-loss. Parameters and results were not visible. Sources: [kr.tradingview Galac III](https://kr.tradingview.com/script/lSFguPn0-Galac-III-SOXL); [it.tradingview Galac III](https://it.tradingview.com/script/lSFguPn0-Galac-III-SOXL)
- **"SOXS to SOXL ratio – DAILY CHART"** (idea; author and date unknown).
  - Rule: plot the SOXS/SOXL price ratio. "When the ratio is on a downtrend, this signals to Sell SOXS or BUY SOXL or a combination of each." Use the ratio to "temporarily buy some SOXS" during corrections, and set an alert for when the ratio "changes trend direction at a pivot".
  - Claim: "could yield 5X annually… with little effort". No backtest was shown.
  - Sources: [vn.tradingview idea Arn254Rl](https://vn.tradingview.com/chart/SOXS/Arn254Rl-SOXS-to-SOXL-ratio-DAILY-CHART); [kr mirror](https://kr.tradingview.com/chart/SOXS/Arn254Rl-SOXS-to-SOXL-ratio-DAILY-CHART)
- **Other TradingView ideas found by title** (content not retrieved):
  - "SOXL / SOXS, this ratio analysis shows when to trade each" ([cn.tradingview COVPE6Ub](https://cn.tradingview.com/chart/SOXL/COVPE6Ub-SOXL-SOXS-this-ratio-analysis-shows-when-to-trade-each))
  - "SOXS goes LONG Inversing SOXL": "SOXS on the 30-minute chart has reversed from a trend down to an early uptrend" ([my.tradingview Nqg3qT8q](https://my.tradingview.com/chart/SOXS/Nqg3qT8q-SOXS-goes-LONG-Inversing-SOXL))
  - "Why Bear Shares are NOT Investments" ([tw.tradingview qlOiKewL](https://tw.tradingview.com/chart/SOXS/qlOiKewL-Why-Bear-Shares-are-NOT-Investments))

#### C. Seeking Alpha, blogs and newsletters (snippets; exact dates mostly not retrievable)
- **"SOXL And SOXS: Shorting Both Produces An Attractive Pair Trade"** (SA article 4629572).
  - Rule: **short both SOXL and SOXS**, because "their long-term decay rates significantly outpace their average cost to borrow fees". The main driver is beta slippage, and rising semiconductor volatility speeds up decay in choppy markets.
  - No backtest numbers were visible.
  - Source: [Seeking Alpha 4629572](https://seekingalpha.com/article/4629572-soxl-and-soxs-pair-trade-shorting-both)
- **"SOXS: Betting Time Is Over, Switching Over To SOXL"** (SA 4817157; by Tech Stock Pros / Tech Contrarians).
  - A discretionary switch: take profits on SOXS and move to SOXL **ahead of Nvidia earnings and a potential rate cut**. The authors call the pullback a "healthy and mild correction" and say SOXS is riskier than SOXL.
  - Sources: [Seeking Alpha 4817157](https://seekingalpha.com/article/4817157-soxs-betting-time-is-over-switching-over-to-soxl); [public.com news listing](https://public.com/stocks/soxs/news/2)
- **"SOXL Semiconductor Bull 3X ETF: Watch Nothing But Price Action"** (SA 4882803).
  - Rule: a **22-day versus 200-day simple moving average** timing rule on SOXL (SOXL or out, not SOXS). It trades about **1.5 times a year**.
  - Claim: turned **$10,000 into about $2.1 million "since 2002"**.
  - SOXL launched in March 2010, so the pre-2010 part must be simulated.
  - Source: [Seeking Alpha 4882803](https://seekingalpha.com/article/4882803-soxl-semiconductor-bull-3x-etf-watch-nothing-but-price-action)
- **Seeking Alpha articles against holding SOXS:**
  - "SOXS: Resist The Temptation To Short Semiconductor Stocks With Inverse Levered ETFs" ([SA 4673367](https://seekingalpha.com/article/4673367-soxs-resist-temptation-to-short-semiconductor-stocks-inverse-levered-etfs))
  - "SOXS: Amortizing Fund That Should Be Avoided" ([SA 4723607](https://seekingalpha.com/article/4723607-soxs-amortizing-fund-that-should-be-avoided))
- **Other SOXL-only or pair titles** (content not retrieved):
  - [SOXS-SOXX pair, SA 4466956](https://seekingalpha.com/article/4466956-surf-supply-chain-ripples-with-soxs-soxx-pair)
  - [SOXL: The Trend Is Your Friend, SA 4827532](https://seekingalpha.com/article/4827532-soxl-the-trend-is-your-friend)
  - [SOXL: Levered Semiconductor Funds Are Living On Borrowed Time, SA 4919774](https://seekingalpha.com/article/4919774-soxl-levered-semiconductor-funds-are-living-on-borrowed-time)
  - [SOXL: Volatility Is Crushing The Leveraged Semiconductor Funds, SA 4949285](https://seekingalpha.com/article/4949285-soxl-volatility-is-crushing-the-leveraged-semiconductor-funds)
- **"Betting Against Semiconductors: Contrarian Play or Sucker Play?"** (AOL syndication).
  - Rule of thumb: buy inverse leveraged ETFs **only in extreme overbought conditions** and hold **"no more than a week (one day is often long enough)"**.
  - Example given: from July 10 to August 29, SOXX barely moved (246.5 to 245.33) while SOXL fell from 26.63 to 26.04.
  - Source: [AOL article](https://www.aol.com/articles/betting-against-semiconductors-contrarian-play-120332469.html)
- **Brian Cellars Substack (comment thread).** A practitioner remark: "it's almost always best to let it run till at least 10 o'clock"; buying SOXL with a tight stop "can work well, but hasn't had a lot of success consistently". The context could not be read. Source: [briancellars.substack.com](https://briancellars.substack.com/p/getting-ready-for-the-next-market/comments)
- **Quantified Strategies.** No SOXL- or SOXS-specific strategy surfaced. The site publishes general rule-based ETF strategies such as SPY and QQQ overnight systems. Source: [QuantifiedStrategies 200 strategies](https://www.quantifiedstrategies.com/trading-strategies-free/)
- **Benzinga.** A "Zinger Key Points" page (benzinga.com/z/28993954) came up repeatedly for SOXL/SOXS day-trading queries, but its content could not be retrieved. Source: [Benzinga z/28993954](https://benzinga.com/z/28993954)

#### D. Signal vendors, AI bots and marketing-style claims
- **Tickeron.**
  - "AI Trading Agent" on SOXL using **5-minute** signals: **551% annualized return, 79.22% win rate**. Neither the period nor costs were visible. Source: [Tickeron SOXL deep dive](https://tickeron.com/trading-investing-101/soxl-a-deep-dive-into-trading-performance-and-aidriven-strategies/)
  - Sister claim: "META/SOXS AI Bot Earns +154% with 5-Minute Trade Signals". Source: [Tickeron META/SOXS](https://tickeron.com/trading-investing-101/metasoxs-trading-results-aipowered-double-agent-delivers-154-annualized-return/)
  - "7 AI-Driven Strategies with Inverse ETFs Like SOXS" (title only). Source: [Tickeron blog](https://tickeron.com/blogs/how-to-profit-in-bear-markets-7-ai-driven-strategies-with-inverse-etfs-like-soxs-11526/)
- **Collective2 "AI SOXL SOXS intraday"** (manager QuantTiger; started **March 2021**; $140 a month; subscriber cap).
  - **Cumulative return -2.1%, maximum drawdown 37.9%.**
  - In 2021: 176 trades, **47.2% win rate, profit factor 1.0**, 6.3% winning months.
  - Last trade **1,592 days** before the snapshot, so the system is no longer active.
  - Source: [Collective2 134901681](https://collective2.com/details/134901681)
- **Pair Trading Lab (user-configured SOXL vs SOXS backtests).**
  - Ratio model: entry threshold 2.00, exit 0.00, maximum hold 20 days, EMA 15, std 15.
  - Residual model: entry 1.70, exit -0.50, maximum hold 60 days, regression period 15. Results for **calendar 2023**: final equity $147,902.46, **ROI 1,379.02%, CAGR 1,423.84%, maximum drawdown 67.83%, Sharpe 2.557**.
  - Sources: [PTL backtest ZSnF](https://www.pairtradinglab.com/backtests/ZSnF_H7tmV5PiTUG); [PTL backtest Zyvw](https://pairtradinglab.com/backtests/Zyvw45TNkt40ChdL)
- **Stock Traders Daily** publishes templated SOXL "rule-based strategy" press releases ("How To Trade (SOXL)", "Price-Driven Insight from (SOXL) for Rule-Based Strategy"). Their content was not retrieved. Sources: [STD How To Trade SOXL](https://news.stocktradersdaily.com/news_release/39/How+To+Trade+(SOXL)_042925065202.html); [STD Price-Driven Insight](https://news.stocktradersdaily.com/news_release/9/Price-Driven_Insight_from_SOXL_for_Rule-Based_Strategy_093026120601_1790741161.html)

#### E. Short-both and "decay harvest" variants
- **"Man in the Mirror" (Rob Bezdjian's "Handsome Rob" model), backtested by GitHub user lordzub (repo updated 2025-07-23).**
  - Rules:
    - short **$1,000 of SOXL and $1,500 of SOXS** at the same time;
    - **rebalance quarterly** (January, April, July, October) back to the target dollar values;
    - add to a short within the quarter whenever its value falls **below 90% of target**.
  - Notebook output for **2010-03 to 2025-01**:
    - total return **18,494%**;
    - average quarterly return 9.69%, quarterly volatility 10.32%;
    - **maximum drawdown -15.09%** (measured on quarterly marks);
    - **88.14% winning quarters**; best quarter +59.93% (Q1 2020), worst -8.11%.
  - No borrow fees or commissions are modeled.
  - Source: [lordzub/HandsomeRob](https://github.com/lordzub/HandsomeRob)

#### F. Open-source rule sets on GitHub (read directly)
- **Korean KIS-API bot "AVWAP 암살자" (AVWAP "assassin") with SOXL/SOXS dual momentum** (pipios4006-boop; latest commit 2026-10-02). Rules are taken from the repo's concept document "V44 차세대 AVWAP 듀얼 모멘텀 스나이퍼" and `version_history.py`.
  - **Time rules:**
    - no entries before **10:00 ET**, because the first 30 minutes are treated as whipsaw;
    - no new entries after **15:00 ET**;
    - flat at **15:55 ET** whatever the profit or loss, with no further trades that day. This was later moved to a full exit at **15:25 ET** (V57.02, 2026-05-09) with a random 0–180-second jitter (V66.00).
  - **Direction rule:**
    - **SOXL** if the day's running VWAP is above the **prior day's VWAP** AND the **5-minute average VWAP** is above the running VWAP;
    - **SOXS** if both inequalities are reversed.
    - V40.00 (2026-04-28) first used a 10:20 ET regime check on the 60-day vs 120-day MA. V40.06 replaced it the same day with the prior-day-VWAP versus current-VWAP comparison plus the direction of the day's candle so far.
  - **Chase filter:** no entry if the move from the day's low has already used up most of ATR5. V62.00 blocks entries when less than 30% of ATR5 "remains".
  - **Targets and stops:**
    - V32.00 (2026-04-27): **+2.0% target and -6.0% hard stop**; the first -6% hit shuts trading down for the day.
    - Later versions: a fixed +4% target, then user-set targets, then an **ATR5-based dynamic stop** (V62.01).
    - No re-entry until price returns to the VWAP baseline (V40.05).
  - Claimed backtest at V32.00: **"+1,134% compounded, 84% win rate"**.
  - **What happened to the SOXS side:**
    - V42.00 (2026-04-28) demoted SOXS to a "shadow" ticker.
    - **V61.00 (2026-05-10) removed the SOXS dual-momentum logic completely** and kept a "single long (SOXL) momentum architecture".
    - V97.x (September 2026) added premarket VWAP-breakout rules: no entry before 04:07 ET, and before 04:30 ET price must hold above VWAP for at least one minute.
  - Sources: [pipios4006-boop/KIS-API-Python-Trading-Bot-Example](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example) (`version_history.py`, `차세대 avwap 프롬프트.txt`); a related issue titled "암살자 롱(SOXL)과 숏(SOXS)의 듀얼 운영에 대한 고찰에 대한 다섯번째 이야기" ("fifth note on running assassin long SOXL and short SOXS together") — [issue #239](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example/issues/239), not readable here.
- **"SiliconCycle v1"** (axesprayor; March 2026; inspired by "Malik's Whitelight" TQQQ/SQQQ method). A daily SOXL/SOXS/cash system driven by ^SOX.
  - **Long (SOXL) sub-systems:**
    - S1: SOX above its 20-, 50- and 200-day SMAs;
    - S2: above the 50 and 200 with Bollinger %B (BB%) between 30% and 70%;
    - S3: above the 200 with BB% below 0;
    - S4: above the 200 and 50 but below the 20;
    - S5: above the 200 but below the 50;
    - S6: within 2% above the 200-day SMA.
  - **Short (SOXS) sub-systems:**
    - S7: SOX below the 200- and 50-day SMAs and the lower Bollinger band, with 20-day rate of change below -4% (code uses -3%);
    - S8: BB% above 105%.
  - **Boost:** S9 adds weight when the SOX/QQQ ratio is rising and SOX is above its 50-day SMA.
  - **Volatility scalar:** position is multiplied down as the 20-day/252-day realized-volatility ratio rises (1.00 / 0.85 / 0.65 / 0.40).
  - Reported results, 2010-03-11 to 2026-03-27:
    - baseline: **Sharpe 0.431, CAGR 8.9%, maximum drawdown -76.6%, 40.3% win rate, 3,035 trades**;
    - best after Claude-driven "AutoImprover" tuning: **Sharpe 0.494, CAGR 12.6%, maximum drawdown -74.8%**;
    - the "targets" of 24–28% CAGR are explicitly "**projected… not backtested**".
  - Its equity was **-51.3%** below the $162,071 high (set 2024-03-07) as of 2026-03-27. **No SOXS signal had fired since 2025-05-12.**
  - Source: [axesprayor/siliconcycle-strategy](https://github.com/axesprayor/siliconcycle-strategy) (`program_sc.md`, `docs/STRATEGY_DEEP_DIVE_SC.md`)
- **Smaller personal projects:**
  - **samhovan18** (Aug 2026, dry-run only, Robinhood): regime from SMH versus its 50-day MA. Base 30% allocation to SOXL or SOXS, tilted by SMH's percentage distance from the MA. Hold 1 day, or 2 days if SMH is more than 5% from the MA. 5% stop. Runs at 15:50–16:05 ET. Source: [samhovan18/soxl-soxs-fdx-algo](https://github.com/samhovan18/soxl-soxs-fdx-algo)
  - **mrpink970** "4-ETF trading plan" (SOXL/SOXS/TQQQ/SQQQ momentum score). 12% trailing stop; trades only when the absolute score is 2.0 or more; exit if up less than 3% after 3 days. Its forward record is in Q4. Source: [mrpink970/4-etf-trading-plan](https://github.com/mrpink970/4-etf-trading-plan)
  - **bmf-san** (Japanese) SOXL/SOXS dashboard: 4-indicator signal scoring, MACD/RSI/MA-cross backtests with a 5 bps fee parameter, and a long-both decay simulator. Source: [bmf-san/soxs_soxl_analyzer](https://github.com/bmf-san/soxs_soxl_analyzer)
  - A Korean repo titled "SOXX 레짐 분류 기반 SOXL/SOXS 자동매매 봇 (토스증권 Open API)" ("SOXX regime-classification SOXL/SOXS auto-trading bot, Toss Securities Open API"). It is not publicly cloneable. Source: [DoUn11/new-soxl-soxs-bot-KR](https://github.com/DoUn11/new-soxl-soxs-bot-KR)

### Inferences
- **Most "switching" rules are daily-bar systems.** Every Composer symphony and the SiliconCycle, SOXL Growth and samhovan18 rules decide on daily data (often at or near the close). They are not intraday flip rules. The only published intraday SOXL<->SOXS flip logic found is:
  - the "SOXL Breakout" overlay's 15:55 SOXS line (a time-of-week fade);
  - the Korean KIS bot's VWAP dual-momentum rule. Its own author dropped the SOXS side within about 12 days of adding it (2026-04-28 to 2026-05-10).
- **Overfitting signs.** Thresholds such as 62.1995, 4.9228 and 5.4135 in SOXL Growth, 31%/25% in SOXL/SOXS, and 1.41% in SOXL Breakout look like numbers fitted to past data. SiliconCycle was explicitly tuned on its own full history by an automated loop, and its own repo says the only out-of-sample target numbers are "not backtested".
- **The only live record failed.** Collective2's QuantTiger system was an intraday SOXL/SOXS strategy with independent trade tracking. It made about nothing (profit factor 1.0, -2.1%) and stopped. Every big-number claim (Tickeron 551%, PTL 1,379%, "5X annually", +1,134%) comes from the vendor or author, with no costs and no out-of-sample period.
- **Short-both is a different trade.** "Short SOXL + SOXS" (Seeking Alpha; Man in the Mirror) harvests volatility decay rather than switching direction. Its backtests leave out borrow costs and availability, recalls, and the squeeze risk inside a quarter. Those are the main real-world costs of that trade.

### Gaps
- **Blocked sources.** No full page from composer.trade, tradingview.com, seekingalpha.com, tickeron.com or benzinga.com could be read. Composer's OOS windows, trade counts, creation dates and full logic trees (except SOXL Growth through the port) are missing. So are the authors and dates of the TradingView scripts, Seeking Alpha publication dates, and any Tickeron methodology.
- **SOXL/SOXS (Composer) and SOXX Group** OOS return figures were not in the snippets (SOXX Group gives Sharpe and drawdown only).
- **Independent backtests not readable.** Tradiecapital's "SOXL Backtest: Can RSI Pullback Signals Hold Up After Costs?" ([link](https://www.tradiecapital.com/blog/backtests/soxl-ema-rsi-atr-pullback-strategy-backtest)) and Vestinda's SOXL backtesting and day-trading pages ([backtesting](https://www.vestinda.com/academy/soxl-backtesting-a-comprehensive-analysis-of-direxion-daily-semiconductor-bull-x-shares), [day trading](https://www.vestinda.com/academy/soxl-day-trading-boost-your-profits-with-x-shares)) may contain independent, cost-aware tests, but both were blocked.
- **Investing.com.** No SOXL/SOXS switching material was found.
- **Out-of-scope crypto products.** Crypto-exchange "SOXL" perpetual futures posts (KuCoin) are not US-listed ETFs and were not catalogued.

## Q2. What do Reddit communities and YouTube/day-trading educators say about flipping SOXL/SOXS intraday? (rules of thumb, warnings)

### Takeaway
- **Reddit could not be accessed at all**, so no Reddit-specific rules or warnings are reported.
- **YouTube educators.** English-language educators rarely publish concrete intraday SOXL<->SOXS flip rules. What they do publish is mostly:
  - timing filters: wait until 10:00, use weekly signals, wait for cycle or Elliott-wave confirmation;
  - "don't trade the earnings gap";
  - warnings about decay and leverage.
- **Korean creators** are more explicit about flipping ("스위칭", "롱숏와리가리" = long/short flip-flopping, "합성매매" = synthetic/two-sided trading). But the material is mostly discretionary, macro- or earnings-driven, and often sold through paid rooms or e-books.
- **The concrete intraday triggers that do appear in public sources:**
  - a 10:00 ET start and a no-entry window late in the day;
  - VWAP versus prior-day VWAP;
  - a percentage trigger above the 09:25 open;
  - a reversal on the 30-minute chart;
  - SOXS/SOXL ratio pivots;
  - switching around Nvidia earnings.

### Cited Findings

#### Reddit
- WebSearch refused reddit.com ("The following domains are not accessible to our user agent: ['reddit.com']"), and fetching through the proxy also failed. No r/Daytrading, r/LETFs, r/wallstreetbets, r/stocks or r/SOXL content could be collected.

#### English YouTube educators (descriptions read directly; transcripts unavailable)
- **Maverick Trading** (prop-firm recruiting channel).
  - "How pros trade leveraged ETFs like $SOXL" (2022-10-31): leveraged ETFs "need to be traded properly". No rules in the description. [YouTube huT6RzIo2N0](https://www.youtube.com/watch?v=huT6RzIo2N0)
  - "3 Strategies for Trading SOXS" (2022-11-07): promises "3 proven strategies", with no specifics in the description. [YouTube 3Mu6jB_6F-A](https://www.youtube.com/watch?v=3Mu6jB_6F-A)
- **AutoPilot Trading (Dennis Wilborn)**, "How to trade SOXL & TQQQ without watching charts all day" (premiered 2026-07-21; about 22k views).
  - Rules: a daily and weekly "pre-flight" check; **weekly TSI and MACD signals**; "**wait for Friday confirmation** before acting on a weekly signal"; and "trading without watching the open".
  - This is a swing approach, sold alongside a paid service and book.
  - [YouTube lgcnC2XRf2Y](https://www.youtube.com/watch?v=lgcnC2XRf2Y)
- **Market Turning Points**, "Why a Cycle-Driven SOXL Trading Strategy Beats Chasing Chip Earnings and Headlines" (2026-05-05).
  - Warnings: traders get trapped when they "buy around chip earnings and gap opens", "mistake news reaction for structural opportunity", "ignore volatility decay in choppy action" and "size up before confirmation".
  - Rules: use the intermediate cycle with "2/3, 3/5, and 4/7 crossovers"; "sometimes the right SOXL trade is no SOXL trade".
  - [YouTube c8LuCPxNLrA](https://www.youtube.com/watch?v=c8LuCPxNLrA)
- **Tony's Market Update**, Elliott-wave analysis (2026-08-30).
  - Charts SOXS separately from SOXL, SOXX and the SOX index to see whether they agree.
  - Will "never buy the bottom on SOXL without seeing five waves up, a three-wave pullback, and a break of the prior high first".
  - [YouTube H5VG8pplPYk](https://www.youtube.com/watch?v=H5VG8pplPYk)
- **Formula Institute** (2024-07-28): "Do not enter the market yet… Instead of catching the bottom, we will enter the market when the market recovers." [YouTube x0yVktqg5xI](https://www.youtube.com/watch?v=x0yVktqg5xI)
- **Options Trading IQ**, "Why SOXL Is a Trap for Retail Investors" (2025-06-18). Covers daily rebalancing and volatility decay, and quotes **SOXL Sharpe -0.41 versus SMH 0.19** (period not stated). [YouTube AgfcEtB2oM0](https://www.youtube.com/watch?v=AgfcEtB2oM0)
- **Arcadia Trading**, "Master Day Trading with 3x ETFs for $500 Daily" (2023-07-09). Day-trades TQQQ/SQQQ/SPXL/SPXS/SOXL/SOXS "without margin… get in and get out". Marketing framing, no rules in the description. [YouTube S_BvzmUYNnQ](https://www.youtube.com/watch?v=S_BvzmUYNnQ)
- **BeachBum Trading** (2023-07-21): prefers SOXL to NVDA and is "watching SOXL for potential entry points". [YouTube ocDM7sE4euI](https://www.youtube.com/watch?v=ocDM7sE4euI)
- **TQQQ Challenge** (long-only "SOXL Surge Strategy").
  - Rules: "8 key principles for buying dips and selling peaks"; never sell more than 50%; "SOXL hits its cycle lows when SOXX is near the SMA 200".
  - Records the 2026 crashes; see Q4.
  - [YouTube WCd8HJJT8bg (2026-05-01)](https://www.youtube.com/watch?v=WCd8HJJT8bg); [YouTube PvNAQefEyeI (2026-09-04)](https://www.youtube.com/watch?v=PvNAQefEyeI)

#### Korean YouTube and forums on flipping (descriptions read directly)
- **미부기 (Mibugi)**, "SOXL 이때 살 생각입니다 (SOXS → SOXL 스위칭)" ("When I plan to buy SOXL — switching from SOXS to SOXL", 2026-07-30; about 13k views).
  - The switch is discretionary and macro-driven. Chapters cover the Dow daily chart, SPX options, the **30-year bond yield** (monthly), **big-tech earnings**, the SOXX daily chart and "V-shaped rebound".
  - [YouTube QEAC1F3NQdc](https://www.youtube.com/watch?v=QEAC1F3NQdc)
  - Same creator, "SOXL SOXS 5월 이렇게 하세요" ("Do this with SOXL/SOXS in May", 2026-05-07), covering the INTC monthly chart, SOXX weekly chart, NVDA daily chart and NVDA/TSLA options. [YouTube SWlcpAPV3mw](https://www.youtube.com/watch?v=SWlcpAPV3mw)
- **짜투리 Market TV**, "SOXL 위험구간 대응하시고 SOXS 예상 스위칭 구간 분석" ("Handle the SOXL danger zone; analysis of the expected SOXS switching zone", 2022-07-30). Rule: switch toward SOXS near a short-term high. [YouTube _xWzjUzN0wo](https://www.youtube.com/watch?v=_xWzjUzN0wo)
- **양매매윤**, "SOXL VS SOXS 합성매매" ("synthetic/two-sided trading", 2023-06-01 and 2023-06-07). Runs paid KakaoTalk rooms for "3-minute chart day trading: 5 patterns + volume" and "US 3x ETF synthetic trading (TQQQ vs SQQQ, SOXL vs SOXS)". [YouTube ieMveH9g994](https://www.youtube.com/watch?v=ieMveH9g994); [YouTube rk5XyUT0yUc](https://www.youtube.com/watch?v=rk5XyUT0yUc)
- **유랑월천** daily logs of SOXL/SOXS "롱숏와리가리" (long-short flip-flopping) scalping, 2023. One week is titled "주간단타매매 망했다" ("weekly day trading blew up"). [YouTube wqvxSXPIhDE](https://www.youtube.com/watch?v=wqvxSXPIhDE)
- **Warnings from Korean creators:**
  - **영끌로그**, "단타로 하루 150만원 벌었을 때 멈췄어야 했습니다" ("I should have stopped when I made 1.5 million won in a day", 2026-06-13). A SOXL day-trading loss of "several million won", driven by greed and averaging down (물타기). [YouTube DjACPgr34Pw](https://www.youtube.com/watch?v=DjACPgr34Pw)
  - **SOXL 연구소**, "단타/차트 유튜버들이 절대로 계좌를 까서 수익률을 오픈하지 못하는 진짜 이유" ("The real reason day-trading/chart YouTubers never open their account returns", 2026-09-28). [YouTube m5FSqdN8JcQ](https://www.youtube.com/watch?v=m5FSqdN8JcQ)
- **Korean e-book: "미국주식 급등주 1분봉 단타 – 중급편 (SOXL, SOXS)"** ("US stock 1-minute-chart day trading – intermediate, SOXL/SOXS").
  - Published **2026-04-23**; 95,000 won; about 322 pages.
  - "12 strategies combining 1-minute chart patterns of Nasdaq/QQQ and moving averages".
  - Claims a "verified win rate of over 80% in actual trading".
  - Sources: [kmong 690378](https://kmong.com/gig/690378); [yes24 189183205](https://www.yes24.com/product/goods/189183205?ReviewYn=Y)
- **Korean Q&A and blog warnings:**
  - SOXL/SOXS day trading can work in a range-bound market but widens losses long-term ([a-ha.io Q&A](https://www.a-ha.io/questions/42a1d174dbc140c9a8926df010e2713f)).
  - "Daily 3x" means "it never promised 3x over several days". Leverage decay "eats about 30% of SOXS a year" ([hannipmoney](https://hannipmoney.ghost.io/soxx-soxl-soxs-chai/)).
  - A Blind thread, "Soxl이랑 soxs로 단타 치는 사람 있어?" ("Anyone day-trading SOXL and SOXS?"); title only ([Blind](https://www.teamblind.com/kr/post/Soxl%EC%9D%B4%EB%9E%91-soxs%EB%A1%9C-%EB%8B%A8%ED%83%80-%EC%B9%98%EB%8A%94-%EC%82%AC%EB%9E%8C-%EC%9E%88%EC%96%B4-zaswhzAd)).

#### Concrete intraday flip triggers found in public sources
- **Time-of-day:**
  - no entries before **10:00 ET** and none after **15:00 ET**; flat by 15:25 or 15:55 ([KIS bot](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example));
  - "let it run till at least 10 o'clock" ([Brian Cellars](https://briancellars.substack.com/p/getting-ready-for-the-next-market/comments));
  - TradingView Trend Surge restricts entries to 9–14 ET (v3.0.2) or about 10–15 ET (v4.2) ([v3.0.2](https://www.tradingview.com/script/9O8nW0Mu-SOXL-Trend-Surge-v3-0-2-Profit-Only-Runner/); [v4.2](https://www.tradingview.com/script/8awiG47H-SOXL-Trend-Surge-v4-2-Tiered-Exit-BE-Buffer/)).
- **VWAP:**
  - long SOXL when the day's VWAP is above the prior day's VWAP and the 5-minute VWAP is above the day's VWAP; SOXS on the mirror condition;
  - no re-entry until price is back at VWAP;
  - premarket VWAP hold for one minute before 04:30 ET.
  - Source: [KIS bot](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example)
- **Premarket open and percentage trigger:** 09:25 open plus 1.41%, stop 8% below; SOXS line at the 15:55 close on Monday, Thursday and Friday when the trigger is never hit ([SOXL Breakout](https://tr.tradingview.com/script/a0OFHNAL-SOXL-Breakout)).
- **Reversal on a higher intraday timeframe:** SOXS reversing from downtrend to early uptrend on the 30-minute chart ([TradingView Nqg3qT8q](https://my.tradingview.com/chart/SOXS/Nqg3qT8q-SOXS-goes-LONG-Inversing-SOXL)).
- **Ratio pivot:** switch when the SOXS/SOXL ratio changes trend at a pivot ([TradingView Arn254Rl](https://vn.tradingview.com/chart/SOXS/Arn254Rl-SOXS-to-SOXL-ratio-DAILY-CHART)).
- **Earnings and news:**
  - switch out of SOXS into SOXL ahead of NVDA earnings ([SA 4817157](https://seekingalpha.com/article/4817157-soxs-betting-time-is-over-switching-over-to-soxl));
  - the opposite view: avoid buying "around chip earnings and gap opens" ([Market Turning Points](https://www.youtube.com/watch?v=c8LuCPxNLrA)).
- **Volatility gates:** no entries when VIX is 28 or higher; forced exit when VIX is above 35 ([Trend Surge v4.2](https://www.tradingview.com/script/8awiG47H-SOXL-Trend-Surge-v4-2-Tiered-Exit-BE-Buffer/)).
- **Overbought-only inverse entries, held one day to one week** ([AOL](https://www.aol.com/articles/betting-against-semiconductors-contrarian-play-120332469.html)).

### Inferences
- **Common rules of thumb** across sources:
  - avoid the first 30 minutes;
  - use VWAP (or the prior day's VWAP) as the direction filter;
  - stop opening new trades in the last hour and go flat before the close;
  - treat SOXS as a short-hold tactical tool, not a position;
  - be careful around NVDA and chip earnings gaps.
  None of these sources provides a cost-inclusive statistical test of these rules on SOXL/SOXS.
- **Common warnings:**
  - volatility decay and daily reset;
  - SOXS is structurally riskier to hold than SOXL;
  - averaging down and greed after a winning day;
  - educators who do not show their account statements;
  - sign-up funnels (prop-firm recruiting, paid rooms, e-books, memberships).
- **Silence on short-side flips.** Educators rarely give rules for flipping to SOXS intraday. The one coded Korean attempt dropped the short side within two weeks. This suggests practitioners find the SOXS side harder to make work than the SOXL side in the post-2023 uptrend.

### Gaps
- **Reddit.** All Reddit material (r/Daytrading, r/LETFs, r/wallstreetbets, r/stocks, r/SOXL) is missing because of access blocks. Whether an r/SOXL subreddit exists could not be confirmed.
- **YouTube transcripts.** Unavailable (YouTube's transcript endpoint returned "Precondition check failed"). Rules spoken in the videos, as opposed to written in descriptions, are not captured.
- **Paid material.** No primary content was retrieved for prior-day high/low or opening-range rules applied to SOXL/SOXS by named educators. The only opening-range-like rule found is the SOXL Breakout premarket-open trigger.

## Q3. Korean retail methods: are there widely followed switching methods (e.g., 무한매수법, VR), and what are their rules?

### Takeaway
- **The most widely followed Korean SOXL methods are not SOXL<->SOXS switching systems.** They are long-only systems that split purchases and take profit mechanically:
  - **라오어 무한매수법** ("Laoer's infinite buying method"): 20 or 40 splits, limit-on-close (LOC) buys, a "star point" (별지점) profit target, and quarter-sell and reverse modes;
  - **떨사오팔** ("buy when it falls, sell when it rises"; grid trading);
  - **표준편차 매매** ("standard-deviation trading");
  - moving-average lump buy/sell rules.
- **VR (밸류 리밸런싱, value rebalancing)** is Laoer's long-term TQQQ-plus-cash method, not a SOXS switch.
- **Explicit SOXL/SOXS "스위칭" (switching) by Korean retail is common in practice.** Korean flow data show mass buying of SOXL dips and SOXS after rallies. In 2026 the SOXS side was painful (SOXS -63% to -95%).
- **Scale:** Korean investors held about **$5.2 billion of SOXL, 27% of the fund**.

### Cited Findings

#### Scale of Korean ownership and switching flows
- Korean investors held **$5.238 billion (about 7.14 trillion won) of SOXL**, equal to **27.1% of SOXL's $19.30 billion market cap**, as of "the end of last month" (article date not visible). [Sisa Journal](https://www.sisajournal.com/news/articleView.html?idxno=385924)
  - Related headlines: "SOXL 보유 30% 돌파" ("Korean ownership of SOXL passes 30%") ([keyzard](https://keyzard.cc/views/nb/NTowMThuZ2Ztbm1lZW1ta2xmbGpnamtpaQ)); "올 상반기 반도체 3배 ETF 71조원 사고팔았다" ("71 trillion won of 3x semiconductor ETFs bought and sold this half-year") ([Daum](https://v.daum.net/v/0bLgfhztWd)).
- **2026-03-26 to 03-30:** Korean retail **net-bought $1.163 billion of SOXL while it fell 28.8%**, then **net-sold $903 million during the +28.7% rebound** on 03-31 to 04-01. The news snippet says "2월" (February), which is a typo; the March dates and both percentages are verified (local data: 03-25 to 03-30 close -28.8%, 03-30 to 04-01 +28.7%). [Money Today 2026-04-06](https://www.mt.co.kr/world/2026/04/06/2026040612250035085)
- **2026-04-16 to 04-22:** SOXS was the top Korean net buy (**$80.86 million**). SOXS had fallen **62.7%** since it entered the top-10 list in the February 2–8 window, and **35.4% in April 16–24 alone**, while the SOX index rose for **18 straight sessions** (March 31 – April 24). Verified (local data): SOXX up 18 consecutive sessions; SOXS -35.4% from the April 15 close to the April 24 close. [Money Today 2026-04-27](https://www.mt.co.kr/world/2026/04/27/2026042712151283577)
- **Mid-September 2026:**
  - Korean retail bought **$456.77 million of SOXL** on September 10–16 after a **17.0% one-day drop** on September 14. SOXL then rose **18.9% over September 17–18**. Verified (local data: -17.0% on 09-14; 103.97 to 123.67). [Supple.kr](https://supple.kr/news/cmuay73vh003z13xo16y9fwz4)
  - SOXL net buys were **$823.51 million** on September 14–17. [E-Today](https://www.etoday.co.kr/news/view/2627461)
  - Investors then took SOXL profits after a **+40.7%** run and made SOXS the **top net buy ($164.6 million) on September 17–23**. Verified (local data): SOXL +40.7% from the 09-16 close to the 09-23 close; SOXS kept falling to 32.43 by 09-25. [Money Today 2026-09-28](https://www.mt.co.kr/world/2026/09/28/2026092718122290284)
- **Other flow headlines:**
  - 2026-06-15: 2.6 trillion won into 3x leverage in 5 days after a chip selloff ([Nate](https://m.news.nate.com/view/20260615n31429)).
  - 2026-05-18: "공포에 투자하는 서학개미의 도박…'반도체 하락'에 3배 베팅" ("Korean retail's fear-driven gamble: 3x bets on a semiconductor fall") ([Newsway](https://newsway.co.kr/news/view?ud=2026051813210033245)).
  - 2026-09-30: "반도체는 '3배 인버스' 베팅 손바꿈" ("semiconductor bets rotate into 3x inverse") ([Metro Seoul](https://www.metroseoul.co.kr/article/20260930500311)).
  - Korean investors bought both SOXL and SOXS while sentiment wavered ([Seoul Economic signalm](https://signalm.sedaily.com/NewsView/2GSPUM07YT/GA03)).
  - A YouTube market recap for 2026-04-28 cites SOXL 278.9 billion won versus SOXS 262.3 billion won in Korean fintech holdings, a "semiconductor civil war" ([케이트렌드 US](https://www.youtube.com/watch?v=sbrnshRNCVU)).
- **July 2026** SOXL net buys of **$3.786 billion** (top net buy) appear in a search summary. The exact article could not be pinned down; it may be [Herald Economy](https://biz.heraldcorp.com/article/10829003) or [Nate](https://m.news.nate.com/view/20260614n08537). Treat as unconfirmed.

#### 라오어 무한매수법 (Laoer's infinite buying method)
- **Core rules (original book version):**
  - split capital into **40 parts**;
  - buy daily at the close with LOC (limit-on-close) orders, buying more when price is below the average cost and less when above;
  - sell everything at a fixed profit target (**+10%** for TQQQ), then restart.
  - Applied to TQQQ, SOXL and others.
  - Sources (search-summary level): [Namu Wiki](https://namu.wiki/w/%EB%9D%BC%EC%98%A4%EC%96%B4%EC%9D%98%20%EB%AF%B8%EA%B5%AD%EC%A3%BC%EC%8B%9D%20%EB%AC%B4%ED%95%9C%EB%A7%A4%EC%88%98%EB%B2%95); [revieworld](https://revieworld.co.kr/400)
- **V3.0 rules for SOXL (20 splits).** T is the number of one-part buys made so far.
  - **Star percentage (별%) = 20 − 2T** for SOXL (15 − 1.5T for TQQQ). **Star point (별지점) = average cost × (1 + 별%)**.
  - **When T is 19 or less:** sell 1/4 of the position with an LOC order at the star point ("quarter sell"), and the other 3/4 with a limit order at **+20%** for SOXL (+15% for TQQQ).
  - **Quarter mode (T between 19 and 20):** sell 1/4 at the close (MOC) and 3/4 with a limit order. No buy on quarter-sell days. The star percentage is fixed at -15% for TQQQ and -20% for SOXL, which is the value of 20 − 2T at T = 20.
  - Sources: [pbdfinance V2.2/V3.0 summary (2024-09)](https://www.pbdfinance.com/2024/09/v22-v30.html); [sulsunggachi V3.0 guide](https://sulsunggachi.com/%eb%9d%bc%ec%98%a4%ec%96%b4-%eb%ac%b4%ed%95%9c%eb%a7%a4%ec%88%98%eb%b2%95-tqqq/); V4.0 also exists ([quantstack V4.0](https://quantstack.app/infinite/v4-0-normal/))
- **Laoer's own SOXL videos:** "SOXL 소액 무한매수법 The Start" (small-account version, $10,000 principal, live stream 2023-07-13; about 50k views) and "SOXL 무한매수법 V3.0 시작합니다" ("Starting SOXL infinite buying V3.0", 2024-06-30). The official Naver café is cafe.naver.com/infinitebuying. Sources: [YouTube l_2v9aMwljk](https://www.youtube.com/watch?v=l_2v9aMwljk); [YouTube vSPVUuQrSXw](https://www.youtube.com/watch?v=vSPVUuQrSXw); [Laoer channel](https://www.youtube.com/channel/UCAJG-gfrf72nN7XQ495i_HA)
- **"리버스모드" (reverse mode)**, the rule once the splits run out. From the KIS bot repo's `리버스모드.txt`:
  - It starts when **T is above 19 (20 splits) or above 39 (40 splits)**, even if some cash is left.
  - **Day 1:** sell 1/10 of the shares (20-split) or 1/20 (40-split) with a market-on-close (MOC) order. No buy.
  - **Following days:** try to sell 1/10 or 1/20 of the previous day's holdings with an LOC order at the star point.
  - **From day 2:** buy (remaining cash + sale proceeds)/4 with an LOC order below the star point ("quarter buy").
  - Source: [KIS-API-Python-Trading-Bot-Example](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example)
- **Practitioner outcomes:**
  - "무한매수법 6개월째" ("six months into infinite buying", 2026-09-20): "TQQQ is starting to show escape potential; **SOXL is still in a long fight**" after the creator increased capital ([YouTube aY1SruwTSak](https://www.youtube.com/watch?v=aY1SruwTSak)).
  - A custom version on SOXL perpetual futures on crypto exchanges (outside US-listed scope): 100,000 USDT, 2x leverage, 40 splits, 10% take-profit, backtested at "1–2% a month" ([Threads @mizoorang](https://www.threads.com/@mizoorang/post/Dahyd2dk7V7)).
- **Criticism and risk notes:**
  - "라오어 무한매수법 <- 개소리 책이다" ("Laoer's infinite buying is a nonsense book"; [FMKorea](https://www.fmkorea.com/?top=Y&mid=stock&category=2997204381&order_type=desc&page=3692&document_srl=9276126981)).
  - "TQQQ, SOXL 무한 매수법으로 투자하면 무조건 돈 번다?" ("Do you always make money with infinite buying on TQQQ/SOXL?", 2026-04-24; [YouTube f5O6VwsEFxc](https://www.youtube.com/watch?v=f5O6VwsEFxc)).
  - In long declines the splits run out and unrealized losses grow, and 3x products suffer volatility drag even in sideways markets ([Penguin Quant Lab backtester](https://penglab.net/strategies/infinite-buying)).
  - A comparison of quarter-sell versus plain 10% sell in crashes ([YouTube 3toLI-1FJfk, 2025-12-06](https://www.youtube.com/watch?v=3toLI-1FJfk)).
- **Infinite-buying bot that tried SOXS:** the KIS open-source bot built on this method briefly added a SOXS "dual momentum" mode on 2026-04-28 and removed it permanently on 2026-05-10 (see Q1-F). [KIS bot version_history.py](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example)

#### VR (밸류 리밸런싱, value rebalancing)
- Laoer's **long-term** method: rebalance between **TQQQ and a cash pool** by selling what has risen and buying what has fallen. It is the long-term companion to the short-term infinite buying method. The current version is "VR 5.0".
- Sources: [TheoryDB book review (2022-10-15)](https://theorydb.github.io/review/2022/10/15/review-book-value-rebalancing/); [quantstack VR 5.0](https://quantstack.app/vr/); [brunch essay](https://brunch.co.kr/@jm5h/10)
- No SOXL- or SOXS-specific VR rule set was found.

#### 떨사오팔 ("buy when it falls, sell when it rises") variants
- **Blind post "나만의 soxl매매법" ("my own SOXL trading method").**
  - Start 50% SOXL and 50% VOO.
  - If SOXL rises **+5%**, sell **10%** of SOXL into VOO; if it rises **+10%**, sell **20%**.
  - If SOXL falls **-5%**, move **10% of VOO** into SOXL; if it falls **-10%**, move **20%**.
  - Trade once a day around **1 AM Korea time**; use 5% steps when SOXL moves less than 5%.
  - Source: [Blind](https://www.teamblind.com/kr/post/%EB%82%98%EB%A7%8C%EC%9D%98-soxl%EB%A7%A4%EB%A7%A4%EB%B2%95-%ED%95%9C%EB%B2%88-%EB%B4%90%EC%A4%98-YmWRfuao)
- **매매동반자 (Trading Companions) 떨사오팔 grid bot (LS Securities).**
  - Backtest **2010-04-05 to 2026-08-14** (16.4 years, 4,117 trading days):
    - **CAGR 49.3%** versus SOXL buy-and-hold 37.7%;
    - maximum drawdown **-17.6% on realized (closed) results** but **-33.9% marked to market**, versus -90.5% for buy-and-hold;
    - **85.2% win rate, 1,341 trades, average hold 7.1 days**;
    - every year positive;
    - assumes **fills at the close, with no slippage, unfilled orders or taxes**.
  - The -33.9% mark-to-market drawdown **actually occurred on 2026-07-29**.
  - Split-count variants: 9 splits gives CAGR 36.8%, realized drawdown -13.9%, mark-to-market -27.3%.
  - The author has run it since the second half of 2022; students since 2024.
  - The earlier claim (2026-05-26, data to May 2026) was **CAGR +55%, drawdown -16.9%**.
  - Sells an e-book ("SOXL 연 49%, 그런데 -34%를 견뎌야 합니다" — "SOXL at 49% a year, but you must endure -34%") and bots.
  - Sources: [YouTube iSEIypwB2o0 (2026-09-24)](https://www.youtube.com/watch?v=iSEIypwB2o0); [YouTube cMQaL5-13mU (2026-05-26)](https://www.youtube.com/watch?v=cMQaL5-13mU); [YouTube G0aajJIvPJk backtester (2026-06-09)](https://www.youtube.com/watch?v=G0aajJIvPJk)
  - Benchmark check: verified (local data). SOXL buy-and-hold CAGR is **37.7%** from 2010-04-05 to 2026-08-14 (4,117 days), and the worst drawdown is **-90.5%** (2021-12-27 to 2022-10-14).
- **"Smart split" improvement of 떨사오팔** (퀀트는 게만아, 2024-08-07): Python auto-trading. [YouTube sPWl9yY5mUk](https://www.youtube.com/watch?v=sPWl9yY5mUk)

#### Other Korean SOXL systems
- **제도권주식분석 (ETF STUDIO), "표준편차 매매" (standard-deviation trading).** Rules are behind a paid VIP membership with "real-time standard deviation trading". Videos:
  - "이 숫자만 외우면 SOXL은 돈복사기가 됩니다. 4년간 완성한 잃지 않는 매매법" ("Memorize this one number and SOXL becomes a money copier — a never-lose method built over 4 years", 2025-10-02; about 107k views);
  - "절대 잃지 않는 표준편차 매수법" ("never-lose standard-deviation buying method", 2025-07-19);
  - "SOXL 26년 3월 돈복사 전략. 매도후 55불부터 새로 합니다. 수량 반드시 반으로 줄이세요" ("March 2026 SOXL money-copy strategy: restart from $55 after selling, cut size in half", 2026-02-26).
  - Sources: [YouTube oej-i87Cjyw](https://www.youtube.com/watch?v=oej-i87Cjyw); [YouTube d_iH36uHSjU](https://www.youtube.com/watch?v=d_iH36uHSjU); [YouTube zDuMbmhvcFQ](https://www.youtube.com/watch?v=zDuMbmhvcFQ)
- **드래곤피그 (Dragonpig), "SOXL 200일 매매법" ("SOXL 200-day method", 2024-04-21).**
  - Accumulate **$2,000 at a time**, and do lump sells and lump buys based on the moving averages (120-day and 200-day).
  - Runs alongside an automated grid bot that takes stop-losses.
  - [YouTube 1Cw2ikq4Q7A](https://www.youtube.com/watch?v=1Cw2ikq4Q7A)
- **타이드퀀트 (Tide Quant).** "공세와 방어를 오가는 SOXL 규칙 기반 분할매매 시스템" ("rules-based SOXL split trading that alternates between offense and defense"). Four strategies, a daily LOC/MOC order sheet, no broker connection. [tide-quant.com](https://tide-quant.com/)
- **Threads rule of thumb:** buy SOXL only after a **-80% drawdown from peak**, in split purchases. [Threads @ky._.u_n](https://www.threads.com/@ky._.u_n/post/DICpGQ5TSSl)

### Inferences
- **Not switching systems.** The "widely followed" Korean methods are long-only SOXL accumulation systems with mechanical exits, executed at the close with LOC/MOC orders. They match the overnight trading hours Korean retail can actually trade. None defines a rule for when to switch to SOXS. Korean SOXL-to-SOXS switching appears to be discretionary and crowd-driven:
  - buy SOXL after sharp drops;
  - after a rally, take profits and buy SOXS.
- **The crowd SOXS timing lost in 2026.** Flow reports show the SOXL dip-buying worked well in March–April and September 2026. The SOXS legs did not (SOXS -63% from the February entry window to April 24).
- **Vendor-reported performance.** Korean method performance is almost always reported by the method's seller (e-book, bot, membership). The 떨사오팔 author is unusually transparent: it reports both realized and mark-to-market drawdowns, gives the benchmark (which checks out), and provides backtest code. But its fill-at-close, no-slippage assumptions, and the change in headline CAGR from 55% to 49.3% after July 2026, show how much the results depend on the regime.

### Gaps
- **Source pages not read.** Naver café and blog posts (the main Korean sources), Namu Wiki, Tistory, and most news article bodies could not be fetched. Infinite-buying rules come from search summaries and one GitHub text file, not from Laoer's book. The V2.2 and V4.0 exact formulas were not captured.
- **VR formula.** The VR 5.0 formula (how V is computed, band width, pool contribution) was not retrieved, and no SOXL-specific VR variant was found.
- **Paid rule sets.** The rules behind the standard-deviation method, Tide Quant's four strategies and the 1-minute-chart e-book are paywalled.
- **Ownership figures.** The date of the $5.238 billion / 27.1% SOXL-ownership figure is not confirmed, and the "30% ownership" headline was not verified.

## Q4. Has any of this been independently backtested or audited, and what happened in 2022, April 2025 and 2026?

### Takeaway
- **No independent audit was found for any published SOXL<->SOXS switching rule.** The closest things to independent evidence:
  - Collective2's tracked record of an intraday SOXL/SOXS AI system: -2.1%, profit factor 1.0, abandoned;
  - a public forward paper-trading log of a SOXL/SOXS/TQQQ/SQQQ rotation system (Apr–Sep 2026): 39 trades, 46% win rate, net loss despite catching a +138% SOXL move.
- **Backtests vs. regime outcomes.** Every other number is the author's own in-sample backtest. The project's daily data show why such numbers do not hold up:
  - **2022:** SOXL lost 90.5% peak to trough, yet SOXS gained only +15.5% for the year.
  - **April 2025:** SOXL fell 49% in four sessions, then rose 55% in one day, while SOXS lost 56% that day.
  - **2026:** SOXL rose 260% year-to-date, but with a -69% crash (June 22 to July 29) and 47 sessions of more than ±10%, and SOXS lost 95%.

### Cited Findings

#### Independent or forward evidence
- **Collective2 QuantTiger "AI SOXL SOXS intraday"** (third-party tracked from March 2021). **-2.1% cumulative, -37.9% maximum drawdown.** In 2021: 176 trades, 47.2% win rate, profit factor 1.0. Inactive (last trade 1,592 days before the snapshot). [Collective2](https://collective2.com/details/134901681)
- **mrpink970 4-ETF forward paper log** (SOXL/SOXS/TQQQ/SQQQ; repo updated 2026-10-03).
  - **39 trades from 2026-04-03 to 2026-09-28:**
    - **46.2% win rate**;
    - average gain +19.7%, average loss -12.2%;
    - largest gain **+137.9%** (SOXL $46.06 on 04-03 to $109.56 on 04-28);
    - largest loss -24.6%;
    - **total gross P/L -$1,047.11**.
  - Every trade was in the "bull" regime; **SOXS and SQQQ were never traded**.
  - June–August 2026 whipsaws repeatedly hit the 12% trailing stop on drops of 15–25%.
  - Source: [mrpink970/4-etf-trading-plan, etf_paper_trade_log.csv and etf_paper_performance.csv](https://github.com/mrpink970/4-etf-trading-plan)
- **SiliconCycle** (own backtest, not independent; 2010-03-11 to 2026-03-27). CAGR 8.9–12.6%, maximum drawdown -74.8% to -76.6%, Sharpe 0.43–0.49. The authors label the higher targets "not backtested", and the live-mark equity was -51.3% from its high in March 2026. [axesprayor/siliconcycle-strategy](https://github.com/axesprayor/siliconcycle-strategy)
- **TradingView "SOXL Trend Surge v4.2"** (author-disclosed). **-84.3% maximum intrabar drawdown**; 2022 averaged -$33.74 per trade, about -$490 on a $500 account. [TradingView v4.2](https://www.tradingview.com/script/8awiG47H-SOXL-Trend-Surge-v4-2-Tiered-Exit-BE-Buffer/)
- **Third-party re-implementations exist but publish no audited results:**
  - Composer "SOXL Growth v2.4.5 RL" port, close-to-close and cost-free ([IznogoudQc/soxl-growth](https://github.com/IznogoudQc/soxl-growth));
  - "Man in the Mirror" short-both backtest, no borrow costs ([lordzub/HandsomeRob](https://github.com/lordzub/HandsomeRob));
  - the Penguin Quant Lab infinite-buying backtester is an independent tool, but its SOXL outputs were not retrieved ([penglab](https://penglab.net/strategies/infinite-buying)).

#### 2022 semiconductor bear market (verified, local data)
- SOXL peaked at a **$72.99 close on 2021-12-27** and bottomed at **$6.93 on 2022-10-14: -90.5%**. SOXX fell **-46.2%** over the same window.
- Calendar 2022: **SOXX -35.8%, SOXL -85.8%, SOXS only +15.5%**.
- In 2023 SOXL rose **+224.7%** and SOXS fell **-85.3%**.
- Strategy-specific 2022 evidence:
  - Trend Surge v4.2 lost money on average in 2022 ([TradingView](https://www.tradingview.com/script/8awiG47H-SOXL-Trend-Surge-v4-2-Tiered-Exit-BE-Buffer/));
  - 2022 SOXL "-80% or more from peak" is cited against infinite-buying-style dip-buying ([search summary citing happist](https://happist.com/601549/%EC%84%9C%ED%95%99%EA%B0%9C%EB%AF%B8-%ED%95%84%EB%8F%85-%EB%A0%88%EB%B2%84%EB%A6%AC%EC%A7%80-etfsoxl-%EC%9E%A5%ED%88%AC%EA%B0%80-%EC%9C%84%ED%97%98%ED%95%9C-%EC%88%98%ED%95%99%EC%A0%81-%EC%9D%B4));
  - 떨사오팔 claims every year positive, including 2022, which is not independently verified ([YouTube iSEIypwB2o0](https://www.youtube.com/watch?v=iSEIypwB2o0)).

#### April 2025 tariff crash (verified, local data)
- **SOXL:**
  - 2025-04-02 close $16.26, 04-03 $11.41, 04-04 $8.73, 04-08 $8.25: **-49.3%** from April 2 to April 8;
  - **+54.8% on April 9** (tariff pause);
  - **-24.6% on April 10**.
- **SOXX** fell 18.3% from April 2 to April 8 and rose 18.6% on April 9.
- **SOXS** rose **+65.8%** from April 2 to April 8, then fell **-56.0% on April 9**.
- **Korean retail:** net-bought **$1.720 billion** of US stocks on April 3–9, 2025, the second-largest since January 2022, including **$524.59 million of SOXL**. The report's numbers match the local data. A $69.03 million SOXS net sell appears in the same search summary but may be conflated with a 2026 figure. [Nate / Money Today 2025-04-14](https://news.nate.com/view/20250414n34266)
- Related: "패닉셀 직전에 SOXL 투자, 2일만에 반토막" ("Bought SOXL just before the panic sell — halved in two days", 2025-04-07). [Money Today](https://news.mt.co.kr/mtview.php?no=2025040712122483889)
- SiliconCycle's last SOXS signal was on **2025-05-12**; it stayed long or cash afterwards. [SiliconCycle deep dive](https://github.com/axesprayor/siliconcycle-strategy)

#### 2026 semiconductor rally and crashes (verified, local data unless noted)
- **Year to date (2025-12-31 to 2026-09-25): SOXX +90.2%, SOXL +260.3%, SOXS -94.8%.**
- **The path:**
  - SOXL fell to **$40.62** on 03-30 (03-25 to 03-30: -28.8%).
  - SOXX rose **18 straight sessions** from 03-31 to 04-24.
  - SOXL hit an **all-time high of $302.00 intraday / $300.77 close on 2026-06-22**, then fell **-23.1% the next day**.
  - From 06-22 to 07-29: **SOXL -69.4%** (to $91.99), **SOXX -29.0%**, **SOXS +121.7%**.
  - Worst SOXL day: **-30.5% on 2026-06-05**.
  - **47 of 183 sessions in 2026 had SOXL moves of more than ±10%.**
- **YouTuber accounts:**
  - "SOXL crashed 45% for the THIRD time in 2026… March 30th ($72 to $39), June 9th ($284 to $157), and now July 2nd ($302 to $168)" ([TQQQ Challenge 2026-07-02](https://www.youtube.com/watch?v=dgOIszKiD9w)).
  - "SOXL crashed 70% from its all-time high of $302 to $91 in one month during the July 2026 AI stock crash that triggered margin calls" ([TQQQ Challenge 2026-08-06](https://www.youtube.com/watch?v=6VBwg337YOE)).
  - "SOXL is down 63% from its **July** high of $302 while the SOX index is down 22%" ([Tony's Market Update 2026-08-30](https://www.youtube.com/watch?v=H5VG8pplPYk)). The high was actually on June 22 (local data).
- **What happened to the methods in 2026:**
  - **SOXS-side bets:** -62.7% from the February entry window ([Money Today 2026-04-27](https://www.mt.co.kr/world/2026/04/27/2026042712151283577)).
  - **KIS bot:** removed SOXS logic on 2026-05-10 ([KIS bot](https://github.com/pipios4006-boop/KIS-API-Python-Trading-Bot-Example)).
  - **떨사오팔:** hit its -33.9% mark-to-market drawdown on 2026-07-29 ([YouTube iSEIypwB2o0](https://www.youtube.com/watch?v=iSEIypwB2o0)).
  - **Infinite-buying practitioner:** "SOXL still in a long fight" in September 2026 ([YouTube aY1SruwTSak](https://www.youtube.com/watch?v=aY1SruwTSak)).
  - **mrpink970 paper system:** net loss over April–September 2026 ([mrpink970](https://github.com/mrpink970/4-etf-trading-plan)).
  - **SiliconCycle:** monthly returns Oct 2025 +32.7%, Nov -11.8%, Dec -3.9%, Jan 2026 +38.6%, Feb -8.1%, Mar -11.4% ([SiliconCycle](https://github.com/axesprayor/siliconcycle-strategy)).
  - **Korean dip buyers:** made +28.7% in two days in early April and +18.9% in two days in September; SOXS buyers after the September 16–23 rally were wrong as SOXL kept rising ([Money Today 2026-04-06](https://www.mt.co.kr/world/2026/04/06/2026040612250035085); [Supple](https://supple.kr/news/cmuay73vh003z13xo16y9fwz4); [Money Today 2026-09-28](https://www.mt.co.kr/world/2026/09/28/2026092718122290284)).

### Inferences
- **Holding SOXS paid little even in a bear market, and badly in a bull market.** In 2022, with SOX down 36% for the year and 46% peak to trough, SOXS made only +15.5% for the year. In 2026 it lost 95%. Any switching rule that holds SOXS for more than a few days must time entries precisely. Rules that "flip after a big surge" (Composer SOXL/SOXS fades 10-day moves above 31%) would have been repeatedly run over in the 18-day straight rally of April 2026 and the September 2026 rebound.
- **Big up days cluster right after crashes.** April 9, 2025 and July 30, 2026 (+24.7%) both followed sharp drops. Mean-reversion flips into SOXS after a crash, or into SOXL after a pop, carry one-day risks of 25–56% that the published backtests (closing fills, no gaps or slippage) do not model.
- **None of these claims is credible yet.** No published method has a clean, independent, cost-inclusive out-of-sample record through all three episodes. Treat every catalogued claim as unproven until it is re-tested on the project's own data with realistic costs.

### Gaps
- **No independent re-tests found.** No independent re-test of the Composer SOXL/SOXS rule or of SOXX Group was found. The OOS figures Composer shows are platform-computed and could not be read in full.
- **No 2026 updates.** None of the vendor claims (Tickeron, the SOXL Breakout overlay, the ratio-chart idea) was updated for 2026.
- **Missing return series.** Infinite-buying SOXL backtests by year (2022, 2025, 2026) were not retrievable from Penguin Quant Lab or Naver.
- **Possible independent tests not readable.** Tradiecapital's cost-aware SOXL RSI-pullback backtest and Vestinda's SOXL backtests may be independent tests, but their content was blocked.
