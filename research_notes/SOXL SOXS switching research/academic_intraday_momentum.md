# Intraday momentum, opening-range breakouts and leveraged-ETF end-of-day effects: academic and practitioner evidence for trading SOXL/SOXS with the day's move

*Method note (applies to every section).* Current as of 2026-10-03. The network proxy blocked SSRN, ScienceDirect, Wiley, RePEc/IDEAS, arXiv, Erasmus/Notre Dame/St. Gallen repositories, the Fed and BIS sites, Concretum, CXO Advisory, dev.to and mql5. The primary PDFs therefore could not be opened. Paper numbers come from search-engine extracts of abstracts and from secondary summaries; anything seen only in a secondary summary is marked **(secondary)**. Public GitHub replication repositories were reachable and were read in full (README, spec, conclusions, reports). Measurements made inside this repository are marked **[repo]** and linked to their files. "WP" means working paper. All SOXL/SOXS flow arithmetic is my own and appears under Inferences. The session's shared web-search budget ran out before every figure could be cross-checked, so treat the Gaps lists as a to-verify list.

## 1. Market intraday momentum: Gao, Han, Li & Zhou (2018) and follow-ups in other markets

### Takeaway
In SPY over 1993–2013, the return from the prior close to 10:00 ET predicts the 15:30–16:00 return. R² is 1.6% in-sample (2.6% when the 15:00–15:30 return is added) and 1.4%/2.0% out-of-sample, which is enough for a 6.67%/yr last-half-hour timing strategy with a Sharpe ratio of about 1.08. The effect is strongest on volatile, high-volume, recession and macro-news days. Follow-ups find the same pattern in ruble FX, Chinese stocks, Chinese commodity futures and 12 of 16 developed equity markets. However, the out-of-sample record on US index futures is weak (Rosa 2022), and QQQ, the tech-heavy index, had the lowest out-of-sample R² (0.70%) in Gao et al.'s own cross-ETF test.

### Cited Findings

#### Gao, Han, Li & Zhou, "Market intraday momentum" (WP 2014–15; published J. Financial Economics 129(2):394–414, August 2018)
- **Publication.** JFE vol. 129, issue 2, pp. 394–414, August 2018, DOI 10.1016/j.jfineco.2018.05.009. It circulated as an SSRN working paper titled "Intraday Momentum: The First Half-Hour Return Predicts the Last Half-Hour Return" — [Semantic Scholar](https://www.semanticscholar.org/paper/Market-intraday-momentum-Gao-Han/eb5931b46eb39831d053babe7bfed0f4687f0cea); [WashU profile](https://profiles.wustl.edu/en/publications/market-intraday-momentum/); [SSRN 2440866](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866); [SSRN 2552752](https://www.ssrn.com/abstract=2552752); [2015 WP PDF mirror](https://www.smallake.kr/wp-content/uploads/2015/01/SSRN-id2440866.pdf)
- **Data and signal.** SPY intraday data from February 1, 1993 to December 31, 2013.
  - Predictor: the "first half-hour return on the market since the previous day's market close", i.e. prior close to 10:00 ET, so the overnight gap is included.
  - Target: the last half-hour return (15:30–16:00).
  - Sources: [SSRN abstract](https://www.ssrn.com/abstract=2552752); [JFE version PDF (search extract)](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf)
- **In-sample fit.**
  - Using the first half-hour alone, R² = 1.6%, a level that "matches or exceeds typical predictive R²s at the monthly frequency."
  - Adding the 12th half-hour (15:00–15:30) raises R² to 2.6%.
  - Sources: [SSRN 2552752](https://www.ssrn.com/abstract=2552752); [ResearchGate](https://www.researchgate.net/publication/272303487_Intraday_Momentum_The_First_Half-Hour_Return_Predicts_the_Last_Half-Hour_Return)
- **Out-of-sample R².** 1.4% with the first half-hour alone and 2.0% when combined with the 12th half-hour — [JFE PDF (search extract)](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf)
- **Economic value.** The timing strategy goes long SPY in the last half-hour when the first-half-hour return is positive and short when it is negative.
  - It averaged 6.67%/yr with a 6.19% standard deviation, a Sharpe ratio of about 1.08.
  - Buy-and-hold earned 6.04%/yr with a Sharpe ratio of 0.29.
  - The certainty-equivalent gain is 6.02%/yr.
  - Sources: [QuantifiedStrategies note (secondary)](https://substack.com/@quantifiedstrategies/note/c-151224359); [paper PDF (search extract)](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf)
- **Costs.** The outperformance "remains significant even after accounting for transaction costs," helped by lower costs after 2001 decimalization — [paper (search extract)](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf)
- **When it is stronger.** Predictability is "stronger on more volatile days, on higher volume days, on recession days, and on major macroeconomic news release days." The recession days fall within the 2008–09 crisis, which is inside the sample — [SSRN abstract](https://www.ssrn.com/abstract=2552752)
- **Other ETFs.**
  - Tested: DIA, QQQ and IWM (domestic); EEM, FXI, EFA and VWO (international); XLF and IYR (sectors); TLT (bonds).
  - In-sample R² ranges from **1.81% (TLT) to 11.77% (IYR)**.
  - Out-of-sample R² ranges from **0.70% (QQQ) to 6.53% (EEM)**.
  - Source: [paper (search extract)](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf)

#### Follow-ups in other markets
- **Elaut, Frömmel & Lampaert, "Intraday momentum in FX markets: Disentangling informed trading from liquidity provision"** (WP 2015, SSRN 2694985; J. Financial Markets 37:35–51, 2018).
  - Data: RUB–USD transaction-level data from the Moscow Interbank Currency Exchange (MICEX), 2005–2014, in a market with explicit trading hours.
  - Finding: a significantly positive relation between first and last half-hour returns.
  - Explanation: they find no support for strategic informed trading. Instead, the momentum "is induced by risk aversion to overnight holdings among liquidity providers."
  - Sources: [IDEAS](https://ideas.repec.org/a/eee/finmar/v37y2018icp35-51.html); [SSRN 2694985](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2694985)
- **Zhang, Ma & Zhu, "Intraday momentum and stock return predictability: Evidence from China"** (Economic Modelling 76:319–329, 2019).
  - Chinese stock market. The first and/or second-to-last half-hour returns "significantly predict" the last-period return both in- and out-of-sample.
  - R² "increases markedly with volatility."
  - One extract adds that momentum was "much stronger during the non-GFC period." This conflicts with the US recession result, so it should be checked against the paper.
  - Sources: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0264999318306692); [IDEAS citations page](https://ideas.repec.org/r/eee/ecmode/v76y2019icp319-329.html)
- **Jin, Kearney, Li & Yang, "Intraday time-series momentum: Evidence from China"** (J. Futures Markets 40(4):632–650, 2020; online 2019; DOI 10.1002/fut.22084).
  - Four Chinese commodity futures: copper, steel, soybean and soybean meal.
  - The first half-hour return positively predicts the last half-hour return in all four.
  - Sources: [QUB repository](https://pure.qub.ac.uk/en/publications/intraday-time-series-momentum-evidence-from-china); [EconPapers](http://econpapers.repec.org/RePEc:wly:jfutmk:v:40:y:2020:i:4:p:632-650)
- **Li, Sakkas & Urquhart, "Intraday time series momentum: Global evidence and links to market characteristics"** (WP 2019, SSRN 3460965; J. Financial Markets, published online 2021).
  - Coverage: 16 developed markets. The first half-hour predicts the last half-hour in 12 of the 16.
  - Profitability: intraday time-series momentum (ITSM) is significant in- and out-of-sample. Average returns of strategies conditioned on liquidity, information-arrival and individualism characteristics are 1.19%, 1.92% and 0.89% per annum.
  - When it is stronger: when liquidity is low, volatility is high and information arrives discretely.
  - Cross-country: the US first half-hour return predicts other markets' last half-hours in an "economically exploitable" way.
  - Sources: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S138641812100001X); [SSRN 3460965](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3460965); [accepted version](https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf)
- **Rosa, "Understanding intraday momentum strategies"** (J. Futures Markets 42(12):2218–2234, December 2022, DOI 10.1002/fut.22375).
  - Signal: the overnight return predicts the last half-hour. Per one extract, the instrument is S&P 500 E-mini futures.
  - Main result: **"the predictability disappears in the out-of-sample period."**
  - A Markov-switching model finds two regimes, in which predictability "depends on the strength of the signal." A threshold strategy beats an always-on strategy.
  - Sources: [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375); [EconPapers](https://econpapers.repec.org/RePEc:wly:jfutmk:v:42:y:2022:i:12:p:2218-2234)
- **Other follow-ups (located, details not retrieved):**
  - crude oil futures — [Economic Modelling 95:374–384, 2021](https://ideas.repec.org/a/eee/ecmode/v95y2021icp374-384.html)
  - VIX futures — [J. Banking & Finance, 2022](https://www.sciencedirect.com/science/article/abs/pii/S0378426622003260)
  - bonds — ["Bond intraday momentum", JBEF 31, 2021](https://ideas.repec.org:443/a/eee/beexfi/v31y2021ics2214635021000599.html)
  - investor behavior — ["Intraday time-series momentum and investor trading behavior", JBEF 31, 2021](https://ideas.repec.org/a/eee/beexfi/v31y2021ics2214635021001015.html)
  - Chinese stocks — ["Intraday momentum and reversal in Chinese stock market", FRL 30:83–88, 2019](https://ideas.repec.org/a/eee/finlet/v30y2019icp83-88.html)
  - Bitcoin — [accepted version, 2021](https://centaur.reading.ac.uk/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf)
  - high-frequency trading and intraday momentum — [EFMA 2023](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2023-UK/papers/EFMA%202023_stage-4455_question-Full%20Paper_id-31.pdf)
- **Related.** Li, Yuan & Zhou, "Systematic Momentum: A New Class of Price Patterns" (Management Science 72:7254–7278, 2026; SSRN revised June 2025): a stock's systematic return component shows momentum "intraday, daily, weekly, and monthly" — [INFORMS](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.08236); [SSRN 4062260](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4062260)

### Inferences
- **Size in basis points.** 6.67%/yr over about 252 sessions is roughly **2.6 bps of SPY per day**. An index effect of that size passed through a 3× fund would be about 8 bps gross per day, against an effective spread near 1 bp per side for SOXL **[repo]** ([report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md)). If the classic effect existed in the semiconductor index at its 1993–2013 SPY strength, costs would not kill it. The binding question is whether it still exists (see §5).
- **Sector pattern.** The highest in-sample R² in Gao et al. was IYR's (11.77%), and real estate is the sector where Bai, Bond & Hatch (§2) found REIT LETF rebalancing moving late-day prices in the same era. That fits an LETF-flow channel: the sectors whose leveraged products are large relative to sector liquidity show the strongest pattern. Semiconductors in 2026 fit that profile (SOXL is the largest sector LETF). But QQQ, the closest proxy for tech, had the weakest out-of-sample R² (0.70%), so the 1993–2013 evidence does not support assuming strong momentum in tech/semis.
- **More than one mechanism.** The cross-market results point to several drivers: overnight-risk aversion of liquidity providers in FX (Elaut), volatility and illiquidity (Li et al.), and hedging demand (Baltussen, §2). No single mechanism has to hold for semiconductors.

### Gaps
- Primary PDFs were blocked, so the following were not verified: Gao et al.'s slope coefficients and t-statistics, subperiod tables (e.g., pre- vs post-2003), the R² for each individual ETF beyond the two endpoints (XLF's is missing), and the cost assumptions behind "significant after costs."
- Not retrieved: Elaut et al.'s R²/strategy value, Zhang–Ma–Zhu's R² levels and exact target window, Jin et al.'s effect sizes, Rosa's sample dates and instrument (E-mini per one extract only), and the journal volume/issue year for Li–Sakkas–Urquhart (2021 online vs 2022 issue).
- No academic study was found that tests Gao et al.'s first-half-hour → last-half-hour signal on semiconductor indices (SOX/ICESEMI), SMH/SOXX or SOXL/SOXS. The only such test is internal **[repo]** (see §5).

## 2. Mechanisms: hedging demand (option gamma and leveraged-ETF rebalancing), the LETF rebalancing formula, and its size for SOXL/SOXS in 2026

### Takeaway
The leading explanation for late-day momentum is hedging demand from short-gamma positions: option dealers who are short gamma, and leveraged/inverse ETFs. Baltussen et al. (JFE 2021) document late-day momentum in more than 60 futures markets (1974–2020) and tie it to negative gamma and LETF flows. Barbon et al. find that a 1-SD rise in LETF rebalancing flow raises last-30-minute stock returns by 430% of their mean, with reversal at the next open. Against that, Ivanov & Lenkey show that fund flows cut LETF rebalancing by up to 85%, and Barbon et al. find the LETF effect shrinking over time.

For SOXL and SOXS the required trade is L(L−1)·A·r, i.e. **6·A·r and 12·A·r, both with the sign of the day's move**. At 2026 AUM, a 3% semiconductor day implies roughly **$3.6–5.4B (central about $4.0B)** of same-direction index exposure to trade near the close, before any offset from flows.

### Cited Findings

#### Baltussen, Da, Lammers & Martens, "Hedging demand and market intraday momentum" (WP 2020–21, SSRN 3760365; JFE 142(1):377–403, October 2021)
- **Data and signal.** Intraday returns on more than 60 futures across equities, bonds, commodities and currencies, 1974–2020. The return from the previous close to 30 minutes before the close (rest of day, ROD) positively predicts the last-30-minute return (L30). This is "economically and statistically highly significant" and "reverts over the next days" — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21001598); [SSRN 3760365](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365); [Erasmus](https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/)
- **Strategy.** A simple intraday momentum strategy earns annualized Sharpe ratios of **0.87–1.73 at the asset-class level** — [SSRN abstract via search](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365); [paper PDF](https://academicweb.nd.edu/~zda/intramom.pdf)
- **Mechanism.** Hedging short gamma requires trading in the direction of the price move.
  - Option channel: using a direct proxy of negative gamma exposure (NGE), index momentum is present when NGE is negative and "becomes stronger when NGE becomes more negative."
  - LETF channel: "strong cross-sectional and time-series evidence that leveraged ETFs' hedging demand on a particular index drives the magnitude of its market intraday momentum."
  - Stock level: the gamma effects also appear in individual stocks' returns into the close.
  - Sources: [paper PDF](https://academicweb.nd.edu/~zda/intramom.pdf); [ResearchGate](https://www.researchgate.net/publication/351315710_Hedging_demand_and_market_intraday_momentum)
- **Historical LETF share of the close.** At the end of February 2009, LETF rebalancing was **16.8% (50.2%) of market-on-close volume on a 1% (5%) market day**. This is Cheng & Madhavan's (2009) estimate as quoted in the hedging-demand literature — [Baltussen et al. PDF (search extract)](https://academicweb.nd.edu/~zda/intramom.pdf); [Cheng & Madhavan (ResearchGate)](https://www.researchgate.net/publication/228231757_The_Dynamics_of_Leveraged_and_Inverse_Exchange-Traded_Funds)

#### Barbon, Beckmeyer, Buraschi & Moerke
Versions:
- "The Role of Leveraged ETFs and Option Market Imbalances on End-of-Day Price Dynamics" (SSRN 3925725, 2021; FMA Derivatives 2021)
- "Leveraged ETFs, Option Market Imbalances, and End-of-Day Price Dynamics" (Northern Finance Association version)
- "Liquidity Provision to Leveraged ETFs and Equity Options Rebalancing Flows: Evidence from End-of-Day Stock Prices" (SFI RP 22-40, 2022; FoFI 2022)

Findings:
- **2021 version.**
  - LETFs and option market makers must delta-hedge. This produces momentum or reversal "depending on the size of the demand pressure versus market prevailing liquidity."
  - A large negative (positive) aggregate gamma, relative to average dollar volume, produces "economically and statistically significant end-of-day momentum (reversal)."
  - "The effect generated by leveraged ETFs is even larger."
  - LETFs hedge "during the last half hour before market close."
  - The effect "quickly reverts at the next day's open." It is non-informational.
  - Sources: [NFA abstract](https://portal.northernfinanceassociation.org/viewp.php?n=2240036708); [SSRN 3925725](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725); [FMA PDF](https://fmai.memberclicks.net/assets/docs/Derivatives2021/beckmeyer_etf_options.pdf)
- **2022 version, effect sizes.**
  - A 1-SD increase in option gamma "depresses end-of-day returns by −113% of the average return in the last thirty minutes."
  - A 1-SD increase in LETF rebalancing flows "increases end-of-day returns by **430%** of the average return in the last half hour."
  - Both effects dissipate within the next trading day.
  - Sources: [IDEAS RP 22-40](https://ideas.repec.org/p/chf/rpseri/rp2240.html); [FoFI 2022 PDF](https://wp.lancs.ac.uk/fofi2022/files/2022/08/FoFI-2022-027-Mathis-Moerke.pdf); [Barbon page](https://abarbon.com/papers/liquidity-provision-to-leveraged-etfs-and-equity-options-rebalancing-flows)
- **Liquidity provision and decay.**
  - LETF flows are "perfectly predictable" because of the strict mandate, so they "attract more liquidity provision" and have "shorter-lived" price effects.
  - Option market makers hedge "almost immediately" after early-day jumps, whereas LETF rebalancing "is unrelated to intraday jumps and takes place solely end-of-day."
  - "Gamma effects are persistent throughout the sample, while those stemming from leveraged ETFs are **decreasing significantly over time**."
  - Source: [SSRN 3925725 (search extract)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725)

#### Option-gamma channel (other evidence)
- **Park & Zhao, "Inelastic Hedging Demand and Intraday Momentum"** (NFA paper; AFA submission dated June 2, 2024 as "Where does gamma hedge drive the intraday market move?").
  - Delta-hedging short gamma becomes inelastic once dealers' P&L leaves the gamma/theta break-even range, and this "exacerbates intraday momentum."
  - Using option holdings data, intraday momentum is stronger when active option traders are short gamma.
  - Dealers often keep hedging rather than unwinding.
  - Sources: [NFA](https://portal.northernfinanceassociation.org/viewp.php?n=2240183764); [AFA](https://afajof.org/management/viewp.php?n=129472)
- **0DTE-era dealer gamma.** Two related papers: Dim, Eraker & Vilkov, "0DTEs: Trading, Gamma Risk and Volatility Propagation" (SSRN 4692190, 2024), and Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov, "Do S&P500 Options Increase Market Volatility? Evidence from 0DTEs" (SSRN 5641974, c. 2025). Findings as summarized across both:
  - Market makers' net inventory gamma "is on average positive and negatively related to future intraday volatility."
  - Positive (negative) dealer gamma "strengthens intraday price reversal (momentum)."
  - Days with 0DTE options show lower realized S&P 500 volatility.
  - Sources: [SSRN 4692190](https://ssrn.com/abstract=4692190); [SSRN 5641974](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974); [Quantpedia summary](https://quantpedia.com/do-sp500-0dtes-options-increase-market-volatility/)
- **Baltussen, Da & Soebhag, "End-of-Day Reversal"** (WP, SSRN 5039009, November 2024; EFMA 2024; 2nd place, Quantpedia Awards 2025).
  - Individual stocks show a sharp *cross-sectional* reversal in the last 30 minutes. It is "distinct from market intraday momentum" and concentrated in intraday losers.
  - The bottom decile of intraday losers gained about 400% over 27 years. A reported six-factor alpha is 14.71 bps/day (t = 27.20); the exact portfolio definition is not verified.
  - It is not explained by liquidity or gamma hedging. The drivers are attention-driven retail buying and short-sellers' end-of-day risk management.
  - Sources: [SSRN 5039009](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009); [EUR news](https://www.eur.nl/en/news/end-day-reversal-pattern-second-place-quantpedia-awards-2025); [Alpha Architect (secondary)](https://alphaarchitect.com/end-of-trading/)

#### Leveraged-ETF rebalancing literature
- **Cheng & Madhavan, "The Dynamics of Leveraged and Inverse Exchange-Traded Funds"** (J. Investment Management 7(4), Q4 2009; SSRN 1539120).
  - LETFs always rebalance in the benchmark's direction. Because L(L−1) > 0 for both long and inverse leverage, "trading demands by long and inverse ETFs do not offset, but instead reinforce each other."
  - Daily re-leveraging "can exacerbate volatility towards the close."
  - The MOC-share estimates (16.8%/50.2%) are given above.
  - Sources: [ResearchGate](https://www.researchgate.net/publication/228231757_The_Dynamics_of_Leveraged_and_Inverse_Exchange-Traded_Funds); [SSRN 1539120](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1539120)
- **Tuzun, "Are Leveraged and Inverse ETFs the New Portfolio Insurers?"** (Fed FEDS WP 2013-48, 2013).
  - "A 1% increase in broad stock-market indexes induces LETFs to originate rebalancing flows equivalent to **$1.04 billion** worth of stock."
  - The positive-feedback rebalancing resembles the 1987 portfolio insurance.
  - Price-insensitive, concentrated trading produced price reactions and extra volatility in underlying stocks, contributing to volatility in 2008–09 and in H2 2011.
  - Sources: [FEDS abstract](https://www.federalreserve.gov/pubs/feds/2013/201348/201348abs.html); [FEDS page](https://www.federalreserve.gov/econres/feds/are-leveraged-and-inverse-etfs-the-new-portfolio-insurers.htm); [IDEAS](https://ideas.repec.org/p/fip/fedgfe/2013-48.html)
- **Bai, Bond & Hatch, "The Impact of Leveraged and Inverse ETFs on Underlying Real Estate Returns"** (WP December 2013, SSRN 2373357; Real Estate Economics 43(1):37–66, 2015; a companion WP covers underlying stocks, SSRN 1716999).
  - Sample: six real-estate LETFs and 63 REIT stocks.
  - Late-day LETF rebalancing "significantly moves the price of component stocks, increases their volatility," and contributes to price momentum. Part of the impact reverses in the next day's first hour.
  - The impact is largest for "smaller, less actively traded, more volatile stocks." The evidence is "consistent with predatory trading by strategic investors."
  - Sources: [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/1540-6229.12061); [SSRN 2373357](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2373357); [SSRN 1716999](https://dx.doi.org/10.2139/ssrn.1716999)
- **Shum, Hejazi, Haryanto & Rodier, "Intraday share price volatility and leveraged ETF rebalancing"** (WP October 2012; Review of Finance 20(6):2379–2409, 2016).
  - Published version: 346 large-cap stocks. End-of-day volatility is significantly correlated with the ratio of potential rebalancing trades to total volume. The impacts are "not all economically significant, but largest during the most volatile days." The paper discusses predatory trading.
  - 2012 WP version (June 2006 – July 2011), via CXO (secondary):
    - Estimated aggregate LETF rebalancing explains about **one-third of late-day stock volatility**, and **over 50% on days when the market is up or down at least 3% by 3:30 pm**.
    - A front-running strategy keyed to the market move by 2:45 pm made **0.60% gross per trade, 104% cumulative**, with 44 of 128 trades (34%) losing.
    - A 2:30 pm variant using estimated rebalancing size made **0.66% per trade, 119% cumulative**.
    - Results are gross of costs.
  - Sources: [ResearchGate (RoF)](https://www.researchgate.net/publication/310445082_Intraday_share_price_volatility_and_leveraged_ETF_rebalancing); [ResearchGate (WP)](https://www.researchgate.net/publication/256036436_Intraday_Share_Price_Volatility_and_Leveraged_ETF_Rebalancing); [CXO summary (secondary)](https://www.cxoadvisory.com/volatility-effects/front-running-leveraged-etfs-at-the-end-of-the-day/); [U of T repository](https://utoronto.scholaris.ca/server/api/core/bitstreams/55d149e5-bf5c-4211-a446-6326d2397019/content)
- **Ivanov & Lenkey** (Fed FEDS 2014-106, "Are Concerns About Leveraged ETFs Overblown?", 2014; published as "Do leveraged ETFs really amplify late-day returns and volatility?", J. Financial Markets 41:36–56, November 2018).
  - Capital flows "can lower ETF rebalancing demand and completely eliminate it in the limit."
  - US equity LETFs, 2006–2014: flows "substantially reduce ETF rebalancing demand, even during periods of severe market stress." Index returns generate **up to 85% less rebalancing** once flows are counted.
  - After accounting for flows and risk factors, the impact on late-day returns and volatility is "economically insignificant."
  - Sources: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418117302604); [SSRN 2504012](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2504012); [SSRN 2544657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2544657); [IDEAS](https://ideas.repec.org/a/eee/finmar/v41y2018icp36-56.html)
- **Todorov, "Passive funds affect prices: evidence from the most ETF-dominated asset classes"** (BIS WP 952, 2021; earlier LSE job-market paper "Passive Funds Actively Affect Prices: Evidence from the Largest ETF Markets").
  - Covers VIX futures and commodities, not equities.
  - Splits ETF trading demand into leverage, calendar and flow rebalancing. **Leverage rebalancing has the largest effect** on the ETF-related price component; it "amplifies price changes" because funds must buy after rises and sell after falls.
  - Trading against ETFs "is risky", and rebalancing creates unhedgeable risks for counterparties.
  - Sources: [BIS WP 952](https://www.bis.org/publ/work952.pdf); [IDEAS](https://ideas.repec.org/p/bis/biswps/952.html); [JMP PDF](https://ktodorov.com/files/research/Todorov_JMP_Main_text.pdf)
- **Jain, Mishra, Pagano & Rodriguez, "Of Seesaws and Swings"** (SSRN 2022; EFMA 2024; updated 2025).
  - The interplay of LETF fund flows and index-return autocorrelation (the "see-saw") moderates or amplifies rebalancing demand.
  - Investor disagreement can damp volatility in stressful markets, and part of the amplified volatility is informational.
  - Sources: [SSRN 4038544](https://doi.org/10.2139/ssrn.4038544); [EFMA 2024 PDF](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/LETF20231228EFMA.pdf)
- **Zhao, "Preying on Leveraged ETFs"** (arXiv 2608.03703; v1 August 4, 2026, v3 August 24, 2026; marked preliminary; the author discloses AI research assistance).
  - Model: an LETF's mandated rebalance is sized by the day's return, which creates upward-sloping demand at the close. Rational arbitrageurs "pre-position, enlarge the fund's order, and liquidate into the demand they have induced."
  - Setting: 16 Korean single-stock LETFs on Samsung Electronics and SK Hynix, launched May 27, 2026. All traded below their listing price within six weeks; the worst was down 43%.
  - Per the companion notes: Korean stocks tracked by LETFs reversed about 75% of their first-day response to pre-open US news by the next close. Rebalancing raised SK Hynix's annualized volatility from 100.0% to 136.7% over nine weeks and cost its LETF holders 17.6%.
  - Sources: [arXiv abstract](https://arxiv.org/abs/2608.03703); [arXiv v3](https://arxiv.org/html/2608.03703v3); [companion notes](../SOXL%20and%20SOXS%20intraday%20behavior/mechanics_and_external_data.md)

#### SOXL/SOXS 2026 inputs
- **SOXL size (aggregator snapshots, all search extracts that differ by date and definition).**
  - Net assets $16.95B (total assets $24.13B) as of April 30, 2026
  - Net assets $19.31B on Yahoo as of October 1, 2026
  - AUM $23.90B (TradingView), $25.16B (StockAnalysis) and $26.11B (Danelfin)
  - Sources: [Fintel](https://fintel.io/s/us/soxl); [Yahoo](https://finance.yahoo.com/quote/SOXL/); [TradingView](https://www.tradingview.com/symbols/AMEX-SOXL/); [StockAnalysis](https://stockanalysis.com/etf/soxl/); [Danelfin](https://danelfin.com/etf/SOXL)
  - Earlier: $13.6B on December 15, 2025 — [24/7 Wall St](https://247wallst.com/investing/2025/12/15/soxls-13-6-billion-fund-faces-rebalancing-drag-as-memory-cycle-enters-critical-phase/)
- **SOXS size (snapshots).** $1.4B (Yahoo), $1.49B (Danelfin), $1.80B (Dividend Data), $1.82B (TradingView) — [Yahoo](https://finance.yahoo.com/quote/SOXS/); [Danelfin](https://danelfin.com/etf/SOXS); [Dividend Data](https://www.dividenddata.com/funds/soxs); [TradingView](https://www.tradingview.com/symbols/AMEX-SOXS/)
- **Index and exposure.**
  - Index: the ICE (NYSE) Semiconductor Index since August 25, 2021.
  - Exposure: SOXL holds stocks plus total-return swaps; SOXS holds short swaps. Direxion "rebalances exposure daily by buying or selling swaps."
  - Top weights (late September 2026, SOXX as proxy): NVDA ~9.4%, MU ~8.9%, AMD ~8.2%, AVGO ~7.5%; most other names 4–5%.
  - Sources: [companion notes](../SOXL%20and%20SOXS%20intraday%20behavior/mechanics_and_external_data.md); [Direxion FAQ](https://www.direxion.com/frequently-asked-questions); [TipRanks SOXX holdings](https://www.tipranks.com/etf/soxx/holdings)
- **Market-wide LETF rebalancing in 2026 (Benzinga citing Bloomberg, July 2026, via companion notes).**
  - Daily LETF rebalancing flows reached a record **$50B**, 1.60% of S&P 500 futures volume.
  - Total LETF assets were $193B.
  - "More than $50 billion of leveraged ETF assets is now concentrated in semiconductor-focused products."
  - Sources: [Benzinga](https://www.benzinga.com/etfs/broad-u-s-equity-etfs/26/07/60264868/leveraged-etf-rebalancing-hits-50-billion-as-traders-warn-of-a-powerful-force-now-driving-us-market-volatility)
  - A Bloomberg Odd Lots analyst argues the roughly $200B LETF cohort now "overwhelm[s] the long gamma from overwriting" funds — [24/7 Wall St, July 10, 2026](https://247wallst.com/investing/2026/07/10/analyst-reveals-how-200-billion-in-leveraged-etfs-could-amplify-the-next-market-selloff/)
- **SOXL flows are large and often contrarian.** SOXL reportedly had **$9.6B of outflows in April 2026 despite a 164.3% return** that month (search extract; not verified on the page) — [Morningstar](https://www.morningstar.com/funds/semiconductor-rally-lifted-april-etf-flows-167-billion). A single-day $332M inflow is also reported — [ETF Action](https://www.etfaction.com/semiconductor-shifts-soxl-accumulates-amid-nvdl-redemptions/)
- **[repo] Trading activity.** Over the three months to 2026-09-25, SOXL averaged **$8.73B/day** of traded value and SOXS $2.82B/day. SOXL's last 30 minutes carry 12.8–13.2% of its regular-hours minute volume, and its closing auction 1.77% of daily volume; SOXS's auction carries 0.12% — [report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md)

### Inferences
- **Rebalancing formula (Cheng & Madhavan; derivation).** Let A₀ be the prior-close NAV and r the index return since that close.
  - Exposure drifts from L·A₀ to L·A₀(1+r). NAV becomes A₀(1+L·r), so target exposure is L·A₀(1+L·r).
  - Required trade = **L(L−1)·A₀·r**.
  - SOXL (L = 3): **+6·A₀·r**. SOXS (L = −3): **+12·A₀·r**. Both are buys on up days and sells on down days.
  - With net creations F (in dollars) at the same close, the trade becomes **L(L−1)·A₀·r + L·F**: SOXL 6A₀r + 3F, SOXS 12A₀r − 3F. Contrarian flows therefore offset rebalancing in both funds. SOXL outflows after up days cut its buying; SOXS inflows after up days force it to add short exposure. This is the channel Ivanov & Lenkey measure (up to 85% offset).
- **Size at 2026 AUM.** SOXL $17–26B (central $19.3B, Yahoo Oct 1, 2026); SOXS $1.4–1.8B (central $1.5B). Gross, before flow offsets:

  | Semis index move by the close | SOXL 6·A·r | SOXS 12·A·r | Combined, central (range) |
  |---|---|---|---|
  | ±1% | $1.02–1.57B (central $1.16B) | $0.17–0.22B ($0.18B) | **$1.34B** ($1.19–1.78B) |
  | **±3%** | **$3.06–4.70B ($3.48B)** | **$0.50–0.66B ($0.54B)** | **$4.02B ($3.56–5.35B)** |
  | ±5% | $5.10–7.83B ($5.79B) | $0.84–1.09B ($0.90B) | $6.69B ($5.94–8.93B) |

- **Per stock on a 3% day.** At central AUM and late-September weights, the $4.0B splits into roughly NVDA $0.38B, MU $0.36B, AMD $0.33B and AVGO $0.30B, plus about $0.16B for each 4%-weight constituent. Much of it is executed by swap dealers hedging changes in swap notional rather than by the funds directly.
- **Benchmarks.**
  - SOXL+SOXS alone now generate about $1.3B per 1% semiconductor move, which exceeds Tuzun's **$1.04B per 1% move for the entire US LETF complex in 2012**.
  - The 3%-day figure equals about 46% of SOXL's own average daily traded value. The comparison is only illustrative, because the hedge trades in index constituents and swaps, not in SOXL shares.
  - At the Ivanov–Lenkey upper-bound offset (85%), the net 3%-day trade would fall to about **$0.6B**.
- **Whole semiconductor LETF complex (rough).**
  - Assumptions: semiconductor-focused LETF assets are about $50B (Benzinga). SOXL $19.3B (×6) and SOXS $1.5B (×12). The remaining roughly $29B is assumed to be mostly 2× long single-stock funds (×2) whose underlyings move with the index.
  - Result: aggregate rebalancing of about **$190B × r**, i.e. roughly **$5.8B on a 3% semiconductor day**, all in the direction of the move.
  - This is an order-of-magnitude figure only. The fund mix and the stock-vs-index co-movement are assumptions.
- **What the literature implies for the price effect.** Literature implies a late-day push in the day's direction, concentrated in the final 30 minutes and the closing auction (Barbon et al.), reverting by the next open (Barbon et al.; Bai et al.). The push will be smaller when:
  - flows are contrarian (Ivanov & Lenkey)
  - liquidity providers anticipate the flow (Barbon et al.'s decay; Shum et al.'s front-running)
  - dealers are long gamma (0DTE papers)
  
  Zhao's 2026 model goes further: anticipatory trading moves the price in the rebalancing direction *before* the close and unwinds into it, so the visible price effect can show up earlier in the afternoon and reverse at or after the close.

### Gaps
- Not retrieved: Barbon et al.'s sample (stocks, years) and the dollar size of a 1-SD LETF flow; Baltussen et al.'s slope coefficients, R² values and NGE construction; Park & Zhao's effect sizes.
- **Todorov.** I found no Todorov paper specifically on "the cost of LETF rebalancing" for equity LETFs. The Todorov work located (BIS WP 952) studies VIX and commodity ETPs. If the intended reference is different, it was not found.
- **Official AUM.** Official Direxion figures for SOXL/SOXS net assets, shares outstanding and swap notional in September–October 2026 were not accessible. The AUM range spans $17–26B because aggregators differ in date and definition (net vs total assets).
- **Missing denominators.** Closing-auction and last-30-minute dollar volume for NVDA/MU/AMD/AVGO and the other constituents, needed to express the $4B as a share of liquidity.
- **Missing gamma and flow data.** Semiconductor-specific dealer gamma (SMH/SOXX/NVDA options), and the timing of SOXL/SOXS flows relative to the close (same-day creation cut-offs vs T+1), which governs the offset in the L·F term.
- **Hedging internals.** How much of the rebalancing swap dealers net internally (e.g., across SOXL, single-stock LETF and option books) before trading in the market. No public source found.

## 3. Practitioner/academic day-trading papers: Zarattini and co-authors (ORB on QQQ/TQQQ, stocks in play, SPY noise area) and 2025–2026 follow-ups

### Takeaway
The Concretum/Zarattini working papers (none peer-reviewed) report very large backtested profits:
- 5-minute ORB on QQQ/TQQQ, 2016–2023: TQQQ 1,484% vs 169% for QQQ buy-and-hold
- ORB on "stocks in play": over 1,600%, Sharpe 2.81
- SPY noise-area momentum, 2007–2024: 1,985%, 19.6%/yr, Sharpe 1.33

Independent replications in 2025–2026 reproduce the gross results but show:
- the QQQ ORB edge sits inside the bid-ask spread (break-even at about 2.2¢/share of slippage)
- it was mostly a 2022 phenomenon
- on five indices it is net zero (January 2015 – June 2026)
- the SPY noise-area strategy lost money in 2025 (−4.9%) and 2026 to July (−12.9%)

No 2025–2026 Concretum paper applying these models to leveraged ETFs other than the 2023 TQQQ ORB was found.

### Cited Findings

#### Zarattini & Aziz, "Can Day Trading Really Be Profitable? Evidence of Sustainable Long-term Profits from Opening Range Breakout (ORB) Day Trading Strategy vs. Benchmark in the US Stock Market" (WP, SSRN 4416622; first posted April 10, 2023, revised April 21, 2025)
- **Data and rule.** QQQ (and TQQQ) 5-minute bars, January 2016 – February 2023.
  - Entry: trade the direction of the first 5-minute candle (no trade on a doji), entering at the open of the second candle (09:35).
  - Stop: the other side of the first candle (1R).
  - Exit: a target of 10R or the session close.
  - Sizing: risk 1% of equity per trade, capped at 4× leverage (the FINRA day-trading limit), starting with $25,000.
  - Sources: [SSRN 4416622](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622); [replication README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq); [mql5 summary, September 25, 2026 (secondary)](https://www.mql5.com/en/blogs/post/776235)
- **Costs assumed.** Commission of $0.0005/share per side and **no slippage** ("we assumed no slippage in fills"). There is no out-of-sample period — [replication figure map](https://github.com/giovannibrusco/zarattini-2023-orb-qqq/blob/main/docs/FIGURE_MAP.md); [replication README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Reported results.**
  - QQQ: 1,795 trades, Sharpe 1.12, 24% hit rate, +0.13R per trade, about 33%/yr with 4× leverage — [replication README](https://github.com/giovannibrusco/zarattini-2023-orb-qqq); [mql5 (secondary)](https://www.mql5.com/en/blogs/post/776235)
  - One summary gives QQQ total return 675%, annualized alpha 33% and Sharpe 1.13 — [The Robust Trader (secondary)](https://therobusttrader.com/can-day-trading-really-be-profitable-rules-backtest-statistics-performance-analysis/)
  - **TQQQ: 1,484% (2016–2023) vs 169% for QQQ buy-and-hold**, with annualized alpha of about 47–48%. The two summaries differ on the alpha — [Concretum](https://concretumgroup.com/can-day-trading-really-be-profitable/); [Concretum Substack](https://concretumgroup.substack.com/p/can-day-trading-be-profitable); [The Robust Trader (secondary)](https://therobusttrader.com/can-day-trading-really-be-profitable-rules-backtest-statistics-performance-analysis/)
  - The paper used TQQQ to "overcome leverage constraints."

#### Zarattini, Barbon & Aziz, "A Profitable Day Trading Strategy For The U.S. Equity Market" (WP, SSRN 4729284; first posted February 16, 2024, revised April 29, 2025; SFI Research Paper 24-98)
- **Data and rule.** 5-minute ORB on more than 7,000 US stocks, 2016–2023. The strategy is restricted to "Stocks in Play", i.e. stocks with abnormally high relative volume, mostly on company news, trading the top 20 each day.
- **Results.**
  - "Total net performance of over 1,600%, with a Sharpe ratio of 2.81, and an annualized alpha of 36%," vs 198% for the S&P 500.
  - Sources: [SSRN 4729284](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284); [IDEAS RP 24-98](https://ideas.repec.org/p/chf/rpseri/rp2498.html)
- **Later check (secondary, weak).**
  - QuantConnect's replication reports only 2016: Sharpe 2.396 vs 0.836 for SPY, on the 1,000 most liquid stocks.
  - Community testing found fees took about 25% of P&L with a 17% win rate.
  - No post-2023 results were reported.
  - Sources: [GitHub issue summarizing QC research](https://github.com/jsboige/CoursIA/issues/16355); [QuantConnect](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/)

#### Zarattini, Aziz & Barbon, "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)" (WP, SSRN 4824172; first posted May 10, 2024, revised April 29, 2025; SFI Research Paper 24-97)
- **Noise area (exact rule, from a replication spec that transcribes the paper).**
  - σ_t is the mean over the last 14 days of |P_{d,t}/Open_d − 1| at each minute-of-day t.
  - UpperBound_t = max(Open, prior Close)·(1+σ_t) and LowerBound_t = min(Open, prior Close)·(1−σ_t). The overnight gap therefore widens the band.
  - Sources: [replication SPEC](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/SPEC.md); [SSRN 4824172](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172)
- **Trading rules.**
  - Checks only at HH:00 and HH:30 (10:00–15:30). Go long above the upper band and short below the lower band; flips are allowed.
  - Exit ("final" variant): leave a long if price falls below max(VWAP, UpperBound), mirrored for shorts.
  - Flat at 16:00.
  - Sizing: 2% daily volatility target (14-day volatility), maximum leverage 4×.
  - Commission: IB's $0.0035/share.
  - Sources: [replication SPEC](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/SPEC.md); [Concretum page](https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/)
- **Results.**
  - May 2007 to early 2024: **1,985% total return net of costs, 19.6% annualized, Sharpe 1.33** — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172); [SFI](https://www.sfi.ch/en/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy)
  - The paper tests volatility regimes and whether dealer gamma imbalance predicts profitability — [SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172)
  - Per the replicator's reading of the paper: Sharpe rises with volatility (about 3.5 when VIX > 40); 2008 inflates the results; 2012–2015 was a multi-year weak stretch before recovery — [replication SPEC](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/SPEC.md); [replication CONCLUSIONS](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/CONCLUSIONS.md)
  - A reviewer notes QuantConnect results using the real bid/ask spread trail the paper, while a "no spread" simulation reproduces it — [Quant Macro review (secondary)](https://quantmacro.substack.com/p/paper-review-an-effective-intraday)

#### Maróy, "Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies" (WP, SSRN 5095349; posted January 21, 2025, revised January 27, 2025)
- Optimizes all parameters and tests VWAP, VWAP & Ladder and Ladder exits on the SPY noise-boundary strategy. Reports **Sharpe over 3.0 and annualized returns over 50%**. These are in-sample optimization results — [SSRN 5095349](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349)
- An independent, pre-registered 27-variant grid on SPY (October 2020 – December 2023 in-sample) found the paper's original configuration (final exit, 14-day lookback, 30-minute checks) had the best in-sample Sharpe, 1.73 (Deflated Sharpe 0.972). Out-of-sample (January 2024 → July 2026) it made **Sharpe 0.16, CAGR +1.3%, max drawdown −24.2%, expectancy −0.17 bps/trade**, and no Maróy variant beat it — [replication Maróy report](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/reports/maroy_experiment.md)

#### Concretum/Zarattini output in 2025–2026 (practitioner, not peer-reviewed)
- "Intraday Hedging Strategies: When Intraday Trend Following Meets Passive Equity Portfolios" (interview, March 23, 2026): intraday trend models on the DAX and Nikkei, a "24-hour portfolio," and intraday trend-following as a convex overlay on passive beta — [Concretum Substack](https://concretumgroup.substack.com/p/intraday-hedging-strategies)
- "QuanTip: Improving Performance with Fast Alphas; A Tactical Overlay for Intraday Trend Trading" (Pagani & Zarattini, SSRN) — [Concretum](https://concretumgroup.com/quantip-improving-performance-with-fast-alphas-a-tactical-overlay-for-intraday-trend-trading/)
- Other posts: "Intraday Trend Following With 0DTE Options", "Can VIX Improve Intraday Trend Following?" and "Conditional Profitability of Intraday Shorts" — [0DTE post](https://concretumgroup.substack.com/p/intraday-trend-following-with-0dte); [VIX post](https://concretumgroup.substack.com/p/can-vix-improve-intraday-trend-following); [shorts](https://concretumgroup.com/conditional-profitability-of-intraday-shorts/); [papers list](https://concretumgroup.com/papers/)
- Self-reported live result: Concretum's SPY intraday trend-following program made +5.70% in December 2024 and **+32.20% for 2024** (unaudited) — [Concretum on X](https://x.com/ConcretumR/status/1874756318931644894)

#### Independent replications and out-of-sample evidence (practitioner, 2025–2026)
- **QQQ ORB replication (GitHub, 2026).**
  - Reproduces 1,775 trades (paper: 1,795) with Sharpe 1.06 (paper: 1.12) and gross edge of $0.070/share.
  - With $0.02/share entry slippage plus $0.04 on stops, net P&L falls from **$138,639 to $4,860** (Sharpe 0.23, CAGR 2.7%, max drawdown 43.9%). QQQ buy-and-hold had Sharpe 0.72 and CAGR 15.3%.
  - Net P&L crosses zero at **~2.2¢/share** of slippage, while QQQ's spread is about 1¢.
  - **2022 accounts for 76% of the NQ-filtered P&L and 38% of the plain replication's.**
  - Exit mix: about 75% of trades hit the stop, about 22% exit at the close and 2–3% hit the 10R target.
  - No data after February 2023.
  - Source: [giovannibrusco/zarattini-2023-orb-qqq](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- **Five-index ORB replication (mql5 blog, September 25, 2026; secondary).**
  - The unchanged rule on minute data for NQ, SPX, Dow, DAX and FTSE CFDs, January 2015 – June 2026, 2,899–2,937 sessions per market.
  - Gross result on NQ is **+0.131R**, matching the paper.
  - **Net, no market is distinguishable from zero, and four of five are negative.**
  - Source: [mql5](https://www.mql5.com/en/blogs/post/776235)
- **SPY/ES noise-area replication (GitHub, July 2026).**
  - Data: SPY July 2020 – July 2026 (Alpaca IEX) and ES May 2024 – July 2026.
  - 2020–26: Sharpe 1.11, alpha +16.7%/yr (t 2.85), beta ≈ 0; win rate 41%, payoff 1.69, **+2.6 bps/trade**.
  - **2022: +25.8% vs SPY −19.5%.** 2020–24: Sharpe 1.4–2.0 per year, alpha 23–28%.
  - **2025: −4.9% (Sharpe −0.27). 2026 to July: −12.9% (Sharpe −1.91).**
  - ES "final" from May 30, 2024 to July 10, 2026: Sharpe −0.07, CAGR −2.1%. The ES and SPY versions correlate at 0.97, so the data feed is not the cause.
  - Costs are about 0.4 bps per round trip, versus −0.6 bps/trade expectancy, so costs are not the cause either.
  - The replicator calls the edge "compressed" but not provably dead, given the paper's own 2012–2015 lull.
  - Sources: [README](https://github.com/giovannibrusco/zarattini-2024-momentum-spy); [CONCLUSIONS](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/CONCLUSIONS.md); [ES validation](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/reports/validation_es.md)
- **Earlier ES replication (Quantitativo, January 2025, as cited in the SPEC).** About +2 bps/trade, win rate about 36%, payoff about 2.1 — [replication SPEC](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/SPEC.md)

### Inferences
- **What drives the headline returns.** The headline numbers combine a small per-trade edge (a few bps on SPY; about $0.07/share gross on QQQ ORB) with up to 4× leverage, and in TQQQ's case a 3× product on top. Using a leveraged ETF scales the edge and the costs per dollar of exposure equally. In bps of the underlying, though, the 3× product's spread is about a third as large, which is why ORB-on-TQQQ looks better than ORB-on-QQQ at the same commission.
- **Relevance to SOXL.** SOXL has a 3× multiplier, about a 7% median daily range and an effective spread of about 1 bp per side **[repo]**. The cost hurdle that kills QQQ ORB at 2.2¢/share is therefore much lower for SOXL in relative terms. The open question is whether a directional edge exists at all. The repo's own test found a 15-minute ORB on SOXL net +24.1 bps/trade out of sample (t 1.19, not significant after multiple-testing correction, negative in 2026 to date); 5-minute and 30-minute ORBs were +4.5 and +10.8 bps net out of sample — [report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md)
- **Regime dependence.** The ORB and noise-area profits cluster in high-volatility bear or crash regimes (2008, 2020, 2022), which fits "Sharpe rises with VIX." These strategies behave like intraday trend-following that is long volatility. They are not a stable unconditional edge.
- **Overfitting risk.** Parameter optimization (Maróy) adds in-sample Sharpe but none out of sample in the one disciplined test. Any SOXL adaptation should fix parameters before testing.

### Gaps
- No 2025–2026 Concretum/Zarattini paper applying the noise-area model to QQQ/TQQQ, SOXL or any other leveraged ETF was found. The search budget ran out before the Concretum papers page could be checked exhaustively.
- Not verified: the ORB paper's exact TQQQ alpha (47% vs 48%), its QQQ total return (675% per one secondary summary), the TQQQ Sharpe and drawdown, and Beat the Market's exact slippage assumption (only the $0.0035/share commission was confirmed, via the replication spec).
- No independent out-of-sample (2024–2026) test of the stocks-in-play ORB was found.
- The replications are non-peer-reviewed GitHub/blog work. The SPY replication uses IEX-only data (about 3% of volume), although it cross-validates against ES.

## 4. Studies of leveraged ETFs' own intraday price behavior and predictability

### Takeaway
The academic LETF literature studies how LETF rebalancing affects the *underlying* stocks near the close (Cheng & Madhavan, Tuzun, Bai et al., Shum et al., Ivanov & Lenkey, Barbon et al., Zhao 2026). It does not study intraday momentum in LETF share prices themselves. The key results:
- Rebalancing explains about a third of late-day volatility (over half on ±3% days) in 2006–2011.
- It supported profitable front-running of 0.60–0.66% per trade gross.
- It reverses by the next morning.
- Flows can offset up to 85% of it.

No study of SOXL/SOXS intraday predictability was found. This repository's own measurements show SOXL's last 30 minutes and closing auction leaning *against* the day's move in 2024–26.

### Cited Findings
- **Late-day volatility and front-running (Shum et al.).** 2006–2011: LETF rebalancing explained about a third of late-day volatility, and over half on ±3% days by 3:30 pm. A 2:45 pm front-running rule made 0.60% gross per trade (104% cumulative over 128 trades); a 2:30 pm size-aware rule made 0.66% per trade (119% cumulative) — [CXO (secondary)](https://www.cxoadvisory.com/volatility-effects/front-running-leveraged-etfs-at-the-end-of-the-day/); [ResearchGate](https://www.researchgate.net/publication/310445082_Intraday_share_price_volatility_and_leveraged_ETF_rebalancing)
- **Sector LETFs and small or illiquid constituents (Bai, Bond & Hatch).** Real-estate LETFs moved REIT prices late in the day, with partial reversal in the next day's first hour. The effect was biggest in smaller, less-traded, more volatile stocks — [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/1540-6229.12061)
- **Predictable flows attract liquidity (Barbon et al.).** LETF rebalancing is solely end-of-day and unrelated to intraday jumps. Because it is predictable, it attracts liquidity, and its price effect is shorter-lived and declining over time — [SSRN 3925725](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725)
- **Flows offset (Ivanov & Lenkey).** Up to 85% less rebalancing once flows are counted; "economically insignificant" late-day effects after controls (2006–2014) — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418117302604)
- **Predatory pre-positioning (Zhao 2026, Korea).** Single-stock LETFs on Samsung and SK Hynix; arbitrageurs pre-position ahead of closing rebalances — [arXiv](https://arxiv.org/abs/2608.03703)
- **Related end-of-day ETP flow studies (located, details not retrieved):**
  - "The stock market impact of volatility hedging: Evidence from end-of-day trading by VIX ETPs" — [JBF 180, 2025](https://ideas.repec.org/a/eee/jbfina/v180y2025ics0378426625001761.html)
  - "The market impact of predictable flows: Evidence from leveraged VIX products" — [JBF, 2021](https://www.sciencedirect.com/science/article/abs/pii/S0378426621002363)
  - "Impact of leveraged ETF trading on the market quality of component stocks" — [NAJEF, 2014](https://www.sciencedirect.com/science/article/abs/pii/S1062940814000059)
  - Charupat & Miu, "The pricing and performance of leveraged exchange-traded funds" — [JBF 35(4), 2011](https://www.sciencedirect.com/science/article/abs/pii/S0378426610003444)
  - Survey: "The market impact of leveraged ETFs: A survey of the literature" — [QFE 2024](http://www.aimspress.com/article/doi/10.3934/QFE.2024031?viewType=HTML)
- **Daily exposure deviations (Bianchi & Goldberg 2026, via companion notes).** In 2022–23, about a third of the gap between 2×/3× S&P funds' results and a constant-leverage benchmark came from the covariance between the funds' deviations from constant leverage and the index return. Real funds do not hold exact leverage — [arXiv 2604.27287](https://arxiv.org/abs/2604.27287)
- **[repo] SOXL/SOXS 2024–26 measurements.** All from the [report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md); supporting files: [close_intraday_momentum_ghlz.csv](../../analysis/behavior/output/close_intraday_momentum_ghlz.csv), [close_letf_rebalancing_by_index_move.csv](../../analysis/behavior/output/close_letf_rebalancing_by_index_move.csv), [close_late_day_regressions.csv](../../analysis/behavior/output/close_late_day_regressions.csv)
  - Intraday beta to SOXX is +3.00 for SOXL and −3.02 for SOXS, and follows the leverage-drift formula L(1+r)/(1+L·r).
  - Gao et al.'s first-half-hour signal is absent: slope −0.019, t −0.8 for SOXL.
  - SOXL's last 30 minutes lean *against* the 09:30–15:30 move: slope −0.043, t −2.4, the same sign on only 43% of days.
  - On the 73 days when SOXX had moved 2–3% by 15:30, SOXL's last 30 minutes continued the day's move only **32.9%** of the time.
  - The closing auction prints a median 6.2 bps (SOXL) and 11.1 bps (SOXS) from the last trade, against the day's move (t −6.9).
  - By contrast, QQQ-driven TQQQ continued on 56% of its few 3%+ days.

### Inferences
- **LETF share prices inherit the index's predictability.** A LETF share price is, to first order, a deterministic function of the index path since the prior close: effective leverage L(1+r)/(1+L·r) plus small premium/discount noise. Any late-day momentum or reversal in LETF shares is therefore essentially the underlying index's, scaled by effective leverage. That is why the literature studies the underlying. For SOXL/SOXS the relevant evidence is about semiconductor stocks and the ICE index near the close.
- **SOXL's close looks anticipated, not pushed.** The repo pattern fits the "anticipated flow" view (Barbon et al.'s decay, Shum et al.'s front-running, Zhao's pre-positioning) rather than the "naive price pressure" view (Tuzun, Bai et al.): continuation is rare in SOXL's last 30 minutes, and the closing auction prints against the day. On this reading, liquidity providers pre-position for the predictable rebalance and supply into it at the close, as Zhao's model predicts.

### Gaps
- No peer-reviewed or working-paper study of intraday predictability in SOXL/SOXS, in semiconductor LETFs generally, or in LETF share prices as such was found.
- No study measures how much of SOXL/SOXS rebalancing is executed in the closing auction versus the last 30 minutes versus over the counter through swap dealers.
- The details of the VIX ETP, NAJEF and JBF LETF studies, and of the QFE survey, could not be retrieved because their domains were blocked.

## 5. Did intraday momentum weaken or strengthen after publication, or by regime (2008, 2020, 2022)?

### Takeaway
By regime, the evidence is consistent: momentum is stronger in high-volatility, recession, news-heavy, illiquid and negative-gamma conditions (2008–09, 2020, 2022).

Over time, it has weakened in US index data:
- Rosa (2022) finds it disappears out of sample.
- A 2024 Bayesian study finds it "diminished over time."
- Barbon et al. find LETF effects declining.
- 0DTE-era dealer long gamma predicts reversal.
- A 2022–2026 SPX test shows a flat slope (+0.006, t 0.6).
- The noise-area replication lost money in 2025–26, and the ORB is net zero on five indices.

SOXL's close flipped from momentum in 2020–21 to reversal since 2023 **[repo]**, even as LETF rebalancing hit records.

### Cited Findings

#### Stronger in volatile, crisis and negative-gamma regimes
- Gao et al.: stronger on volatile, high-volume, recession and macro-news days (1993–2013, including 2008–09) — [SSRN](https://www.ssrn.com/abstract=2552752)
- Li, Sakkas & Urquhart: stronger when volatility is high and liquidity low — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S138641812100001X)
- Zhang, Ma & Zhu: R² rises with volatility in China — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0264999318306692)
- Baltussen et al.: stronger when dealer gamma is more negative — [paper PDF](https://academicweb.nd.edu/~zda/intramom.pdf)
- Shum et al.: LETF share of late-day volatility exceeds 50% on ±3% days — [CXO (secondary)](https://www.cxoadvisory.com/volatility-effects/front-running-leveraged-etfs-at-the-end-of-the-day/)
- Tuzun: LETFs added volatility in 2008–09 and H2 2011 — [FEDS](https://www.federalreserve.gov/pubs/feds/2013/201348/201348abs.html)
- Ivanov & Lenkey counterpoint: flows offset rebalancing "even during periods of severe market stress" — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418117302604)
- Beat the Market: Sharpe rises with VIX (about 3.5 when VIX > 40), and 2008 inflates the full-sample results (replicator's reading) — [replication SPEC](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/SPEC.md)
- Replication: **2022 +25.8% while SPY fell 19.5%** — [replication](https://github.com/giovannibrusco/zarattini-2024-momentum-spy)
- QQQ ORB: 2022 provides 76% of filtered P&L. The 2020 COVID crash and 2022 selloff are "where most of the active edge is actually made", though the NQ-filtered variant lost money in 2017, 2020 and early 2023 — [ORB replication](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)

#### Weaker after publication and in the 0DTE era
- **Rosa (2022).** "The predictability disappears in the out-of-sample period"; it is regime-dependent and needs a signal-strength threshold — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375)
- **"Market Predictability Before the Closing Bell Rings"** (Risks 12(11):180, 2024). A Bayesian Student-t regression on the last 30 minutes finds "well-studied factors such as overnight effects and intraday momentum have diminished over time" — [MDPI](https://www.mdpi.com/2227-9091/12/11/180)
- **Barbon et al.** LETF-driven end-of-day effects are "decreasing significantly over time"; gamma effects persist — [SSRN 3925725](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725)
- **0DTE papers.** Dealer net gamma is on average positive, which favors reversal and damps momentum and volatility — [SSRN 4692190](https://ssrn.com/abstract=4692190); [SSRN 5641974](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974)
- **FirmTape (practitioner blog, 2026), SPX, 1,085 sessions, April 14, 2022 – August 20, 2026.**
  - Last-30-minute return regressed on the rest-of-day return gives slope **+0.006 (t +0.6)**, flat in every year with alternating signs.
  - Conditional on a "tape-signed" 0DTE dealer book read at 15:30, short-gamma closes add a slope of **+0.055 (t +3.1)**.
  - But only 15% of sessions are short-gamma, and the 40-session holdout contains four such days.
  - Source: [dev.to/FirmTape (secondary, vendor)](https://dev.to/firmtape/intraday-momentum-is-dead-in-the-0dte-era-we-measured-it-on-1085-spx-sessions-43g0)
- **Noise-area strategy after publication.**
  - SPY: 2025 −4.9%, 2026 to July −12.9%.
  - Out-of-sample January 2024 → July 2026: Sharpe 0.16.
  - ES (May 2024 – July 2026): Sharpe −0.07.
  - Sources: [CONCLUSIONS](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/docs/CONCLUSIONS.md); [Maróy report](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/reports/maroy_experiment.md); [ES report](https://github.com/giovannibrusco/zarattini-2024-momentum-spy/blob/main/reports/validation_es.md)
- **ORB after publication.** Net zero on five indices over January 2015 – June 2026 — [mql5 (secondary)](https://www.mql5.com/en/blogs/post/776235)
- **Cross-sectional reversal.** Single stocks show end-of-day reversal driven by retail attention and short-seller risk management (Baltussen, Da & Soebhag, 2024) — [SSRN 5039009](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009)
- **Counter-claims.**
  - Concretum reports +32.2% live in 2024 for its SPY intraday trend program (self-reported) — [X](https://x.com/ConcretumR/status/1874756318931644894)
  - A 2026 market commentary argues LETF growth has tilted market gamma negative, which would imply stronger momentum — [24/7 Wall St](https://247wallst.com/investing/2026/07/10/analyst-reveals-how-200-billion-in-leveraged-etfs-could-amplify-the-next-market-selloff/)

#### This repository's SOXL/SOXX measurements
- **Close regressions.**
  - Gao et al.'s first-half-hour signal in 2024–26: slope −0.019 (t −0.8) for SOXL. The joint first + 12th half-hour regression has R² 0.69%, with both slopes negative.
  - Last 30 minutes on the 09:30–15:30 move: −0.043 (t −2.4) in 2024–26, versus −0.006 (t −0.5) in 2022–24.
  - The slope was negative in 17 of 19 quarters, and SOXX shows the same.
  - Sources: [report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md); [close_intraday_momentum_ghlz.csv](../../analysis/behavior/output/close_intraday_momentum_ghlz.csv)
- **Baltussen-style probe.**
  - Rule: trade SOXL in the last 30 minutes on the sign of the prior close→15:30 move.
  - Result: **−31.2 bps/trade net out of sample (October 2024 – September 2026), t −5.26**.
  - The report summarizes this as "momentum in 2020–21 became reversal."
  - Source: [report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md)
- **NVDA differs.** NVDA's quarterly slope of last 30 minutes on 09:30–15:30 averaged +0.023, positive in 79% of 19 quarters — [stability_persistence_summary.csv](../../analysis/behavior/output/stability_persistence_summary.csv)

### Inferences
- **Two-sided timeline.** Intraday momentum in US indices was strong in 1993–2013 and in crisis years (2008, 2020, 2022), and faded after about 2022–2023. Three causes fit the evidence:
  1. Dealers became net long gamma through 0DTE and longer-dated options rolling into expiry.
  2. Liquidity providers learned to anticipate predictable LETF flows.
  3. The publications themselves invited arbitrage.
  
  The record 2026 LETF rebalancing volumes have not revived it at the index level (SPX) or in semiconductors (SOXL/SOXX).
- **When it might return.** A regime with dealers short gamma, VIX above 30–40 and disorderly selling (2008/2020/2022-style) would be the most likely setting for "trade with the day's move into the close" to work again. The FirmTape conditional result (+0.055, t 3.1 on short-gamma closes) is the only post-2022 evidence that a gamma filter recovers it, and it rests on few days.
- **Signal for SOXL/SOXS.** In the current regime, the documented late-day signal for SOXL/SOXS points the *other* way: the last 30 minutes and the closing auction lean against the day. A switching strategy that holds the day's winner (SOXL on up days, SOXS on down days) into the close has fought this headwind in 2024–26 **[repo]**.

### Gaps
- The FirmTape and replication results are non-peer-reviewed. No peer-reviewed paper covering 2023–2026 US market intraday momentum was found.
- Not verified: Baltussen et al.'s subperiod results (e.g., whether momentum strengthened in the 2010s as LETF/option AUM grew), and Gao et al.'s own subperiod splits.
- No published evidence on how intraday momentum behaved specifically in semiconductors during 2008, 2020 or 2022.
- Whether the SOXL reversal survives a stressed, short-gamma regime is untested: the repo's 2022–24 window had a near-zero slope rather than momentum.

## 6. Synthesis: documented mechanisms and their size for semiconductors / SOXL–SOXS

### Takeaway
Four mechanisms could make "trade with the day's move" pay in SOXL/SOXS:
1. **LETF rebalancing.** Mechanically the largest: about $4B of same-direction semiconductor exposure on a 3% day from SOXL/SOXS alone, and on the order of $6B for the whole semiconductor LETF complex.
2. **Option dealers' short-gamma hedging.** Size unknown for semiconductors; negative only some of the time in the 0DTE era.
3. **Overnight-risk-averse liquidity providers and information diffusion** (Gao, Elaut).
4. **Intraday trend-following and breakout behavior** (ORB, noise area).

The evidence says these flows are now largely anticipated and offset: by contrarian fund flows, by liquidity provision and front-running, and by positive dealer gamma. Measured continuation into the close is absent or reversed in SOXL in 2024–26. Earlier-in-the-day trend capture (ORB, noise-area) survives only gross, regime-dependently and with fragile statistics.

### Cited Findings
- **Mechanism magnitudes in the literature.**
  - LETF flows: 1-SD LETF flow adds 430% of the mean last-30-minute return; 1-SD dealer gamma subtracts 113% (Barbon et al.) — [IDEAS RP 22-40](https://ideas.repec.org/p/chf/rpseri/rp2240.html)
  - LETF share of late-day volatility: about one-third, over half on ±3% days (Shum et al., 2006–2011) — [CXO (secondary)](https://www.cxoadvisory.com/volatility-effects/front-running-leveraged-etfs-at-the-end-of-the-day/)
  - 2009 share of the close: 16.8% / 50.2% of MOC volume on 1% / 5% days (Cheng & Madhavan via Baltussen et al.) — [Baltussen PDF](https://academicweb.nd.edu/~zda/intramom.pdf)
  - Flow offset: up to 85% (Ivanov & Lenkey) — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418117302604)
  - Timing strategy: Sharpe 0.87–1.73 across asset classes (Baltussen et al.) — [SSRN 3760365](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365)
  - SPY timing: 6.67%/yr, about 2.6 bps/day (Gao et al.) — [paper (search extract)](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf)
- **2026 scale.**
  - LETF rebalancing: a record $50B/day market-wide; more than $50B of semiconductor-focused LETF assets — [Benzinga](https://www.benzinga.com/etfs/broad-u-s-equity-etfs/26/07/60264868/leveraged-etf-rebalancing-hits-50-billion-as-traders-warn-of-a-powerful-force-now-driving-us-market-volatility)
  - SOXL net assets about $17–26B; SOXS about $1.4–1.8B — [Yahoo SOXL](https://finance.yahoo.com/quote/SOXL/); [TradingView SOXS](https://www.tradingview.com/symbols/AMEX-SOXS/)
- **Semiconductor-specific prices [repo].**
  - No first-half-hour momentum.
  - The last 30 minutes reverse the day (slope −0.043, t −2.4).
  - 32.9% continuation on 2–3% SOXX days.
  - The auction prints against the day.
  - The Baltussen-style SOXL probe lost 31.2 bps/trade net out of sample.
  - The 15-minute ORB made +24.1 bps/trade net out of sample (t 1.19).
  - Source: [report](../../reports/SOXL%20and%20SOXS%20intraday%20behavior.md)

### Inferences
- **LETF rebalancing.**
  - Size: about $1.3B per 1% semiconductor move ($4.0B at 3%, $6.7B at 5%), concentrated in NVDA, MU, AMD and AVGO at about $0.3–0.4B each on a 3% day, plus other semiconductor LETFs.
  - Direction: always with the day.
  - Timing: last 30 minutes and the close (Barbon et al.).
  - Price effect today: the repo's SOXL measurements suggest it is fully anticipated. Liquidity providers appear to pre-position earlier and supply into the close, leaving a net reversal in the last 30 minutes and the auction, which fits Zhao (2026) and Barbon et al.'s decay result.
  - Practical implication: the rebalancing flow is a reason to expect **closing-auction and last-30-minute reversal risk** for a with-the-day position held into the close, not a tailwind.
- **Option gamma.**
  - Direction and size for semiconductors are unknown. The S&P evidence says dealers are net long gamma most days in the 0DTE era, which favors reversal. Single-stock option books on NVDA/AMD/MU/AVGO may differ.
  - This is the only channel with fresh (but thin) evidence of conditional momentum: short-gamma SPX closes, slope +0.055 (t 3.1).
  - A dealer-gamma state variable for SMH/SOXX/NVDA would be the most promising conditioning filter to test, but it needs an options data source the repo lacks before late 2024.
- **Morning-to-afternoon trend (ORB, noise area).**
  - The gross edge is real in high-volatility years, with SPY and QQQ edges of a few bps per trade.
  - For SOXL, the 3× scale and about 1 bp effective spread make the cost hurdle relatively low.
  - But the post-2024 out-of-sample record is negative for SPY (2025–26), the QQQ ORB edge was 2022-concentrated, and the repo's SOXL ORB is not significant and negative in 2026.
- **Expected magnitude for a SOXL/SOXS with-the-day switch.**
  - Base case: in the current (2024–26) regime, literature plus repo data point to zero to negative expected excess return from holding the day's direction into the close (about −30 bps/trade net for the late-day version), and a small, statistically weak positive from morning breakout entries.
  - The academic effect sizes that would make it work (R² 1.6–2.6%, about 2.6 bps/day on SPY at 1× in 1993–2013; 430%-of-mean LETF pushes before 2020) belong to an earlier regime.
  - When to revisit: when volatility regimes shift (VIX above 30–40, dealers short gamma, bear-market selling), which is when every source agrees momentum strengthens.

### Gaps
- Missing semiconductor-specific inputs: dealer gamma for the constituents and for SMH/SOXX options, closing-auction volume for the index constituents, and the timing of SOXL/SOXS creations and redemptions. Without these, the $4B estimate cannot be turned into an expected price impact in bps.
- No published study isolates semiconductors or SOXL/SOXS. All SOXL-specific evidence is this repository's own 2022–2026 measurement, with a short representative-regime history (SOXL's current microstructure dates only to about April 2026).
- Several key numbers come from search extracts or GitHub replications rather than the primary PDFs, which were blocked. Verify before citing in a final report: Gao et al.'s out-of-sample R², the other-ETF R² endpoints and the timing-strategy statistics; Barbon et al.'s 430% / −113%; and Shum et al.'s WP-version strategy returns.
