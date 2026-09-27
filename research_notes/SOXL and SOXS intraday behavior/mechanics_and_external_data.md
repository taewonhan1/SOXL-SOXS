# SOXL and SOXS intraday behavior: fund mechanics, market structure and external data (state as of 2026-09-27)

*Method note (applies to all sections):* the network proxy blocked direct page fetches from this session for direxion.com, sec.gov, theocc.com, ice.com, luldplan.com, stockanalysis.com, finance.yahoo.com and globenewswire.com. Every finding below therefore comes from search-engine extracts of the cited pages, and exact numbers should be re-verified at the primary URL before use. Facts are dated. **[older]** marks facts from before 2025. **[conflict]** marks disagreement between sources. All arithmetic (leverage tables, rebalancing notionals) is my own calculation from the cited inputs and appears under "Inferences".

---

## 1. Index and drivers: what SOXL/SOXS track, methodology, top weights, how exposure is obtained, fund size, expense ratio

### Takeaway
SOXL and SOXS seek +300% and −300% of the *daily* return of the ICE Semiconductor Index, which ICE now brands as the "NYSE Semiconductor Index" (ticker ICESEMI). They have tracked it since August 25, 2021; before that they tracked the PHLX SOX. The index holds the 30 largest US-listed semiconductor companies, weighted by modified float-adjusted market cap, with the top five capped at 8%, all others at 4%, and ADRs capped at 10% in aggregate. In mid-to-late September 2026 (using SOXX, which tracks the same index, as a proxy), NVDA (~9.4%), MU (~8.9%), AMD (~8.2%) and AVGO (~7.5%) move the index most, followed by INTC, MRVL, TSM, AMAT, LRCX and KLAC at about 4–5% each.

SOXL gets its exposure from direct stock holdings plus total-return swaps. SOXS uses short total-return swaps plus cash. SOXL's reported AUM was about $12–14B between December 2025 and March 2026 and grew during the 2026 chip rally (reported range $13–28B; one undated aggregator shows $24.3B). SOXS is about $1.1–1.7B (undated). SOXL's net expense ratio is 0.75%.

### Cited Findings
- **Objective:** SOXL seeks 300% of the daily performance of the ICE Semiconductor Index, and SOXS seeks −300%. Both "seek daily goals and should not be expected to track the underlying index over periods longer than one day" — [Direxion SOXL/SOXS page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs); [etfdb SOXL](https://etfdb.com/etf/SOXL/)
- **Index change [older, 2021]:** "Prior to August 25, 2021, the fund tracked the PHLX Semiconductor Sector Index", so the switch to the ICE Semiconductor Index took effect August 25, 2021 — [Direxion page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs); [stockanalysis SOXL](https://stockanalysis.com/etf/soxl/)
- **Naming:** Yahoo lists the index as "NYSE Semiconductor Index (^ICESEMI)", with a total-return version ^ICESEMIT. NYSE has quote pages for ICESEMI (price), ICESEMIT (total return) and ICESEMIN (net total return). CNBC still labels .ICESEMI "ICE Semiconductor Index". In 2026 Fintel describes SOXL as tracking "3x the daily performance of the NYSE Semiconductor Index", while Direxion's page text (as extracted) says "ICE Semiconductor Index". This is one index under two brand names — [Yahoo ^ICESEMI](https://finance.yahoo.com/quote/%5EICESEMI/history/); [Yahoo ^ICESEMIT](https://finance.yahoo.com/quote/%5EICESEMIT/history/); [NYSE ICESEMI](https://www.nyse.com/quote/index/ICESEMI); [NYSE ICESEMIT](https://www.nyse.com/quote/index/ICESEMIT); [NYSE ICESEMIN](https://www.nyse.com/quote/index/ICESEMIN); [CNBC .ICESEMI](https://www.cnbc.com/quotes/.ICESEMI); [Fintel SOXL](https://fintel.io/s/us/soxl)
- **Methodology [older document, 2022]:** a "rules-based, modified float-adjusted market capitalization-weighted index that tracks the performance of the thirty largest U.S.-listed semiconductor companies." Eligible companies are those classified in the Semiconductors industry of the ICE Uniform Sector Classification: semiconductor makers, LED/OLED users, and semiconductor services/equipment firms such as packaging and testing — [ICE ICEBIO/ICESEMI methodology notice (Jan 28, 2022)](https://www.ice.com/publicdocs/equity_indices/notices/ICEBIO_ICESEMI_Methodology_Updates_20220128.pdf); [ICE Data Indices rules and methodology](https://www.ice.com/publicdocs/data/ICFSFLN_Methodology.pdf)
- **Caps and schedule:** "the weights of the top five securities are capped at 8% and the remaining securities at 4%", ADRs are capped at 10% cumulative, and the index is "reconstituted annually and rebalanced on a quarterly basis" — [TradingView SOXX description](https://www.tradingview.com/symbols/NASDAQ-SOXX/); [iShares SOXX](https://www.ishares.com/us/products/239705/ishares-semiconductor-etf). Another extract of ICE/iShares material gives the dates as annual reconstitution on the 3rd Friday of September and quarterly rebalances on the 3rd Friday of March, June and December — [iShares sector ETF presentation](https://www.ishares.com/us/literature/presentation/ishares-sector-and-industry-etfs.pdf); [ICE methodology](https://www.ice.com/publicdocs/data/ICFSFLN_Methodology.pdf). **[conflict]** The same search also returned "semi-annual reconstitution after the fourth Friday in April and October". That text most likely comes from the different ICE index whose methodology PDF was in the results (ICFSFLN), so I treat it as not applying to ICESEMI.
- **Intraday index data [older, 2022]:** ICE raised ICESEMI's publication frequency from every 15 seconds to every second, effective January 31, 2022 — [ICE notice](https://www.ice.com/publicdocs/equity_indices/notices/ICEBIO_ICESEMI_Methodology_Updates_20220128.pdf)
- **Contrast with the PHLX SOX:** in 2024 Nasdaq changed SOX's caps to 12%, 10% and 8% for the three largest constituents and 4% for the rest. SOX is reconstituted annually in September and rebalanced quarterly — [Nasdaq "Latest Changes to SOX" (Apr 2024)](https://indexes.nasdaqomx.com/docs/202404%20SOX%20Latest%20Changes.pdf); [Nasdaq SOX methodology](https://indexes.nasdaqomx.com/docs/methodology_SOX.pdf)
- **Current top weights, via SOXX as proxy (late Sept 2026):**

  | Stock | Weight |
  |---|---|
  | NVDA | 9.43% |
  | MU | 8.91% |
  | AMD | 8.23% |
  | AVGO | 7.48% |
  | INTC | 5.09% |
  | MRVL | 4.66% |
  | TSM | 4.65% |
  | AMAT | 4.59% |
  | LRCX | 4.27% |
  | KLAC | 4.12% |

  SOXX had 31 holdings as of Sept 14, 2026, the top 10 made up 62.07%, and SOXX's total assets were $43.89B. Sources note that weights vary with capture date — [TipRanks SOXX holdings](https://www.tipranks.com/etf/soxx/holdings); [ChartRow SOXX holdings](https://chartrow.com/quote/soxx/holdings); [SOXX fact sheet (June 30, 2026)](https://www.ishares.com/us/literature/fact-sheet/soxx-ishares-semiconductor-etf-fund-fact-sheet-en-us.pdf)
- **SOXL-level exposure split (Dec 2025, secondary source; denominators unclear):**
  - Micron was "4.5% of SOXL's equity exposure" and Broadcom 6.1%.
  - The top ten made up 40% of equity exposure.
  - SOXL "holds roughly 30% in cash and treasury instruments".
  - Source: [24/7 Wall St, Dec 15, 2025](https://247wallst.com/investing/2025/12/15/soxls-13-6-billion-fund-faces-rebalancing-drag-as-memory-cycle-enters-critical-phase/)
- **How exposure is obtained:** SOXL invests at least 80% of net assets in "financial instruments, such as swap agreements, securities of the index, and ETFs that track the index" — [Direxion page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs); [etfdb](https://etfdb.com/etf/SOXL/). One aggregator lists SOXL with 44 positions (stocks, swaps and cash) — [MarketXLS SOXL holdings](https://marketxls.com/etfs/soxl/holdings). Direxion "rebalances exposure daily by buying or selling swaps" — [Direxion FAQ](https://www.direxion.com/frequently-asked-questions)
- **Swap counterparties [older, N-PORT period ending July 31, 2023]:**
  - Counterparties on Direxion's semiconductor total-return swaps: BNP Paribas, Goldman Sachs, Bank of America Merrill Lynch, J.P. Morgan, UBS Securities LLC, Citibank N.A. and Barclays.
  - The short swaps (SOXS) received 1-month SOFR plus a spread (all-in rates 5.16%–5.84% at that time) and paid the total return of the ICE Semiconductor Index.
  - Earlier swaps (2021–22) referenced 1-month LIBOR.
  - Sources: [Direxion NPORT-P (07/31/2023)](https://www.sec.gov/Archives/edgar/data/1424958/000114554923059576/direxionetfs_73123.htm); [Direxion N-CSR FY2021](https://www.sec.gov/Archives/edgar/data/1424958/000110465922000321/tm213700d1_ncsr.htm)
- **SOXL AUM:**

  | Date | AUM | Source |
  |---|---|---|
  | Dec 15, 2025 | $13.6B | [24/7 Wall St](https://247wallst.com/investing/2025/12/15/soxls-13-6-billion-fund-faces-rebalancing-drag-as-memory-cycle-enters-critical-phase/) |
  | Jan 22, 2026 | $12.68B | [stockanalysis SOXL](https://stockanalysis.com/etf/soxl/) (search extract) |
  | Mar 2, 2026 | $11.86B | [stockanalysis SOXL](https://stockanalysis.com/etf/soxl/) (search extract) |
  | mid-2026 | "between $13 billion and $28 billion", with "year-to-date returns exceeding 50% in 2026" | [Crypto Briefing](https://cryptobriefing.com/leveraged-etfs-record-198b-aum/) |
  | undated | $24.32B | [YCharts SOXL AUM](https://ycharts.com/companies/SOXL/total_assets_under_management) (search snippet) |

  **[conflict]** A TradingView-type snippet showing "AUM 12.10B USD, shares outstanding 494.10M" implies a NAV of about $24.5. That does not match SOXL's late-Sept 2026 price near $150, so it is stale.
- **SOXL flows:**
  - More than $1.28B of inflows on July 8, 2026 — [ETF.com](https://www.etf.com/sections/daily-etf-flows/semiconductor-etfs-roar-back-soxx-pulls-54-billion-single-day)
  - SOXX plus SOXL took in over $2.1B in one day in July 2026 — [Benzinga](https://www.benzinga.com/etfs/sector-etfs/26/07/60576185/quick-spark-semiconductor-etfs-dominate-inflows-as-soxx-soxl-pull-in-over-2-1-billion-in-one-day)
  - Annual history: about −$3B in 2023, +$834M in 2024, and −$6.9B in 2025 through the article date — [ETF.com "Billions Exit Leveraged ETF Giants"](https://www.etf.com/sections/features/why-investors-are-dumping-tqqq-soxl-despite-huge-gains)
- **SOXL price and liquidity:**
  - SOXL traded at $151.35 on Sep 25, 2026 (previous close $146.33), per a search extract — [Fintel](https://fintel.io/s/us/soxl); [Investing.com SOXL](https://www.investing.com/etfs/direxion-dly-semiconductor-bull-3x)
  - Three-month average daily volume was 81.40M shares, or $4.51B, as of March 2026 — [Options Analysis Suite](https://www.optionsanalysissuite.com/etf/soxl/options-chain)
- **SOXS size [conflict, both undated]:** $1.74B per TradingView; another aggregator in the same search showed $1.12B — [TradingView SOXS](https://www.tradingview.com/symbols/AMEX-SOXS/); [YCharts SOXS AUM](https://ycharts.com/companies/SOXS/total_assets_under_management). A 2026 extract shows SOXS NAV at $33.59 after a 36.18% fall over the prior month — [stockanalysis SOXS](https://stockanalysis.com/etf/soxs/)
- **Name change:** "effective February 27, 2026, the fund replaced the term Shares in its name with ETF" (e.g., "Direxion Daily Semiconductor Bear 3X ETF"). The OCC memos for the 2026 SOXS reverse splits use the new "…ETF" names — [stockanalysis SOXS](https://stockanalysis.com/etf/soxs/); [OCC memo 59294](https://infomemo.theocc.com/infomemos?number=59294)
- **Expense ratio (one line):** SOXL net expense ratio 0.75% including acquired-fund fees and expenses, 0.71% excluding them — [Direxion page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs); [etfdb](https://etfdb.com/etf/SOXL/)
- **Korean retail as a holder base:** SOXL ranked first among leveraged ETFs held by Korean investors, at $5.93B as of Sept 21, 2026 (KSD/SEIBro data) — [Seoul Economic Daily, Sept 24, 2026](https://en.sedaily.com/finance/2026/09/24/leveraged-etf-executives-flock-to-korea-as-local-buying)

### Inferences
- **Which stocks move SOXL:**
  - A one-day SOXL return is about 3 × Σ(wᵢ·rᵢ) over index weights. With late-Sept 2026 proxy weights:
    - NVDA +10% → index ≈ +0.94% → SOXL ≈ +2.8%
    - MU +10% → SOXL ≈ +2.7%
    - AMD +10% → SOXL ≈ +2.5%
  - NVDA, MU, AMD and AVGO together are about 34% of the index, so their co-movement drives about a third of SOXL's daily variance budget before correlation effects.
  - Weights above the 8%/4% caps (NVDA 9.43%, INTC 5.09%) reflect price drift since the last capping. They are reset at each quarterly rebalance (3rd Fridays; Dec 18, 2026 next), which makes rebalance days mechanical trading events for the index trackers.
- **Do not proxy SOXL with the widely quoted SOX:**
  - Since 2024 SOX allows a 12%/10%/8% top-3 structure, while ICESEMI keeps 8% top-5 caps and a 10% aggregate ADR cap.
  - Their daily returns can therefore diverge on days driven by the largest names. Fair-value models should use ICESEMI/ICESEMIT.
- **TSMC reaches SOXL only through the TSM ADR:** the ADR's capped weight is about 4.7% (and ADRs are capped at 10% in aggregate). Taiwan-hours moves in TSMC therefore enter SOXL's fair value only through the ADR's US price.
- **Korean holders:** Korean holdings ($5.93B) equal roughly 25–50% of SOXL's AUM, depending on which AUM figure is right. Korean retail is therefore a structurally important marginal holder and flow source.
- **SOXL dominates the pair:** SOXL is about 7–22× the size of SOXS (from $12–24.3B vs $1.12–1.74B), so SOXL drives combined pair mechanics such as rebalancing.

### Gaps
- Official Sept 2026 AUM, shares outstanding and NAV for SOXL and SOXS could not be verified, because the Direxion page and file downloads were blocked. The AUM range above is wide and partly undated.
- SOXS's expense ratio was not found.
- Current (2025–2026) swap counterparties, swap notional and financing spreads were not verified. The latest list found is from the July 2023 N-PORT.
- The ICESEMI reconstitution month and exact rebalance-date rules come from secondary extracts that partly conflict. ICE's primary methodology PDF could not be read.
- The date of the ICE → "NYSE Semiconductor Index" rebrand was not found.
- September 2026 reconstitution adds and drops were not found. One open question is whether any newly US-listed semiconductor ADR was added; a July 2026 article mentions an "SK Hynix ADR" ([24/7 Wall St, Jul 14, 2026](https://247wallst.com/investing/2026/07/14/sk-hynix-adr-soars-19-as-leveraged-etfs-launch-lifting-micron-sandisk-western-digital/)), but its index eligibility was not verified.
- Weights for ASML, QCOM and other names outside the top 10 were not retrieved.

---

## 2. Intraday leverage drift: effective leverage L(1+r)/(1+L·r) within the day

### Takeaway
Each fund's index exposure is set at the prior close and stays fixed until the end-of-day rebalance. Effective leverage to the next index increment is therefore L(1+r)/(1+L·r), where r is the index return since the prior close. For SOXL (L = 3) it falls on up days (2.74× at +5%) and rises on down days (3.35× at −5%, 3.86× at −10%). For SOXS (L = −3) its magnitude rises on up days (−3.71× at +5%) and falls on down days (−2.48× at −5%).

Rule of thumb: whichever fund is losing on the day has |effective leverage| > 3, so it becomes more sensitive to further moves late in a big day. The winning fund becomes less sensitive.

### Cited Findings
- Direxion defines a "day" as close-to-close. Once an investor buys, their "level of exposure is set until … the Fund's next portfolio rebalance at the end of the day" — [Direxion: Understanding Leveraged ETFs](https://www.direxion.com/education/understanding-leveraged-exchange-traded-funds); [Direxion: Pursuing Daily Targets in Volatile Markets (PDF)](https://www.direxion.com/uploads/Direxion-Leveraged-ETFs-Pursuing-Daily-Targets-in-Volatile-Markets.pdf)
- Direxion states: "Intra-day, the total exposure of a Fund may be higher or lower than the stated daily investment objective depending on the movement of the target index away from its value at the end of the prior trading day." It adds that the funds "respond to gains by increasing exposure to the benchmark index, and respond to losses by decreasing exposure each day" — [Direxion education page](https://www.direxion.com/education/pursuing-daily-targets-in-volatile-markets); [Direxion brochure](https://www.direxion.com/uploads/Direxion-Understanding-Leveraged-ETFs-Brochure.pdf)
- **[older, 2009]** Cheng & Madhavan show that leveraged and inverse ETFs "always have to rebalance in the same direction as the benchmark", that their returns are path-dependent, and that they embed a path-dependent option on the index — [SSRN, Cheng & Madhavan (JOIM Q4 2009)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1539120)
- **(2026)** Bianchi & Goldberg: from Jan 2022 to Dec 2023 the S&P 500 rose while 2x and 3x daily S&P ETFs lost money. About two-thirds of the gap comes from compounding and volatility; the rest "is explained by the covariance between the ETFs' deviations from constant leverage and the index's return." In other words, real funds do not hold exactly constant leverage — [arXiv 2604.27287 (Apr 30, 2026)](https://arxiv.org/abs/2604.27287); [Journal of Asset Management](https://link.springer.com/article/10.1057/s41260-026-00473-z)

### Inferences
Worked numbers below are my calculations, ignoring fees and financing accruals.

**Effective leverage by index return since the prior close:**

| Index r since prior close | SOXL return | SOXL effective leverage | SOXS return | SOXS effective leverage |
|---|---|---|---|---|
| −20% | −60% | 6.00 | +60% | −1.50 |
| −10% | −30% | 3.86 | +30% | −2.08 |
| −5% | −15% | 3.35 | +15% | −2.48 |
| −3% | −9% | 3.20 | +9% | −2.67 |
| −2% | −6% | 3.13 | +6% | −2.77 |
| −1% | −3% | 3.06 | +3% | −2.88 |
| +1% | +3% | 2.94 | −3% | −3.12 |
| +2% | +6% | 2.89 | −6% | −3.26 |
| +3% | +9% | 2.84 | −9% | −3.40 |
| +5% | +15% | 2.74 | −15% | −3.71 |
| +10% | +30% | 2.54 | −30% | −4.71 |

**Late-day response to a further ±1% index move:**
- Index already +5%, then another +1%: SOXL +2.74%, SOXS −3.71% (versus ±3% at the start of the day).
- Index already −5%, then another −1%: SOXL −3.35%, SOXS +2.48%.
- At ±2% on the day: SOXL 2.89/3.13 and SOXS −3.26/−2.77 per unit of further index move.

**Theoretical limits:**
- SOXL's NAV goes to zero at r = −33.3%.
- SOXS's NAV goes to zero at r = +33.3%.
- Near those levels, the losing fund's effective leverage explodes (−20% gives SOXL 6×).

**Consequences for intraday modeling:**
- Fair value must be anchored to the prior close: FV_t ≈ NAV_{t−1} × (1 + L·r_t) − daily accruals. A constant 3× applied to the index change from any other intraday reference (the open, VWAP, 3:00 pm) will misprice. The error grows with |r|.
- SOXL's percentage move from an intraday reference is not the negative of SOXS's move. In a +5% rally, a further 1% move is worth 2.74% in SOXL but 3.71% in SOXS.
- The same geometry applies in pre-market, after-hours and overnight trading relative to the prior 4:00 pm NAV. There is no computed ICESEMI in those sessions (see Gaps), so fair value must come from proxies such as constituent extended-hours trades, Nasdaq-100 futures, or TSM/Asian semis.

### Gaps
- Direxion does not publish intraday exposure (swap notional) and does not state whether it ever makes intraday exposure adjustments on extreme days.
- Exact daily accruals (fees, swap financing spreads) for 2026 were not found, and the SOXS expense ratio is unverified.
- It was not verified whether ICE computes ICESEMI outside regular hours.

---

## 3. End-of-day rebalancing: size, timing/execution, and academic evidence on price effects

### Takeaway
The required end-of-day hedge change is L(L−1)·AUM₀·r: +6·AUM₀·r for SOXL and +12·AUM₀·r for SOXS. Both funds trade *with* the index: they buy index exposure on up days and sell on down days, so their flows add rather than offset.

At plausible 2026 AUMs (SOXL $12–24B, SOXS $1.0–1.74B), the combined notional is about:
- $0.8–1.7B for a ±1% index day
- $2.5–5.0B for ±3%
- $4.2–8.3B for ±5%

This is concentrated in NVDA, MU, AMD and AVGO. The rebalance is executed near the close by the fund (stock and swap trades) and by swap dealers hedging.

The academic record is mixed but consistent in direction:
- Rebalancing creates late-day momentum that partly reverses the next day (Cheng & Madhavan; Tuzun; Shum et al.; Barbon et al.; Baltussen et al.).
- Creations and redemptions can substantially offset it (Ivanov & Lenkey).
- 2026 commentary reports record LETF rebalancing volumes and more than $50B of semiconductor-focused LETF assets.

### Cited Findings
- **Execution:** Direxion "rebalances exposure daily by buying or selling swaps to ensure that each fund tracks as closely as possible to 300% … or 300% … of the inverse" of the index's daily performance — [Direxion FAQ](https://www.direxion.com/frequently-asked-questions). Exposure is set until "the Fund's next portfolio rebalance at the end of the day" — [Direxion education](https://www.direxion.com/education/understanding-leveraged-exchange-traded-funds)
- **Cheng & Madhavan (2009) [older]:** daily re-leveraging "can exacerbate volatility towards the close" and always runs in the benchmark's direction — [SSRN 1539120](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1539120). Their model, as cited secondarily: on a 1% index move LETF rebalancing could equal about 16.8% of market-on-close (MOC) volume, and on a 5% move about 50% — [Wikipedia: Inverse ETF](https://en.wikipedia.org/wiki/Inverse_exchange-traded_fund); [Trainor, "Do Leveraged ETFs Increase Volatility" (PDF)](https://pdfs.semanticscholar.org/ee11/37cd8b28d7d5abbe92aeb6f772c8c3edea33.pdf). These are 2009 market sizes and a secondary citation.
- **Tuzun (FEDS 2013-48) [older]:**
  - "A 1% increase in broad stock-market indexes induces LETFs to originate rebalancing flows equivalent to $1.04 billion worth of stock."
  - The positive-feedback rebalancing resembles 1987 portfolio insurance.
  - Implied price impact contributed to volatility in 2008–09 and H2 2011.
  - The flows are predictable and "may attract anticipatory trading."
  - Source: [Federal Reserve FEDS 2013-48](https://www.federalreserve.gov/pubs/feds/2013/201348/201348pap.pdf)
- **Shum, Hejazi, Haryanto & Rodier, Review of Finance 20(6):2379–2409, 2016 [older]:**
  - For 2006–2011, end-of-day volatility was "positively and statistically significantly correlated with the ratio of potential rebalancing trades to total trading volume."
  - Effects were "not all economically significant, but largest during the most volatile days."
  - The paper discusses predatory-trading implications.
  - Sources: [Oxford Academic](https://academic.oup.com/rof/article-abstract/20/6/2379/2418138); [SSRN 2161057](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2161057)
- **Ivanov & Lenkey (FEDS 2014-106; J. Financial Markets 2018) [older]:**
  - Capital flows "can lower ETF rebalancing demand and completely eliminate it in the limit."
  - Empirically (US equity LETFs, 2006–2014), flows "substantially reduce ETF rebalancing demand, even during periods of severe market stress."
  - After accounting for flows and risk factors, the effect on late-day returns and volatility is "economically insignificant."
  - Sources: [FEDS 2014-106](https://www.federalreserve.gov/econres/feds/are-concerns-about-leveraged-etfs-overblown.htm); [SSRN 2504012](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2504012); [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418117302604)
- **Barbon, Beckmeyer, Buraschi & Moerke (SSRN 3925725; SFI RP 22-40, 2021–22):**
  - LETF rebalancing and option delta-hedging "induce significant end-of-day momentum and mean-reversion in stock returns," and the effects dissipate within the next day.
  - LETF-driven effects "are decreasing significantly over time."
  - LETF flows are "perfectly predictable" because of the funds' strict mandate, so they "attract more liquidity provision and their effects on prices are shorter-lived."
  - Sources: [SSRN 3925725](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725); [SFI](https://www.sfi.ch/en/publications/n-22-40-liquidity-provision-to-leveraged-etfs-and-equity-options-rebalancing-flows-evidence-from-end-of-day-stock-prices)
- **Baltussen, Da, Lammers & Martens, "Hedging demand and market intraday momentum" (JFE 2021):**
  - Across 60+ futures from 1974 to 2020, the last-30-minute return is positively predicted by the return from the prior close to 30 minutes before the close, and this reverts over the next days.
  - The effect is linked to short-gamma hedging by option market makers and leveraged/inverse ETFs, and is stronger when hedging flows are larger.
  - A simple strategy earns annualized Sharpe ratios of 0.87–1.73 by asset class.
  - Sources: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21001598); [SSRN 3760365](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365)
- **Baltussen, Da & Soebhag, "End-of-Day Reversal" (2024–25 working paper):**
  - Individual US stocks show a cross-sectional *reversal* in the last 30 minutes, mainly from price pressure on intraday losers.
  - It is "distinct from market intraday momentum," is not explained by liquidity or gamma hedging, and is driven by attention-induced retail buying and short-seller risk management.
  - Sources: [SSRN 5039009](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009); [EFMA 2024 PDF](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/EndofDayReversal_withnames.pdf)
- **Jain, Mishra, Pagano & Rodriguez, "Of Seesaws and Swings" (SSRN 2022, updated July 2025; EFMA 2024):**
  - The interplay of LETF fund flows and index return autocorrelation (the "see-saw effect") moderates or amplifies rebalancing demand.
  - Disagreement between LETF investors and other traders can moderate volatility in stressful markets.
  - Some of the amplified volatility is informational, i.e., it supports price discovery.
  - Sources: [SSRN 5371016](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5371016); [EFMA 2024 PDF](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/LETF20231228EFMA.pdf)
- **Zhao, "Preying on Leveraged ETFs" (arXiv, draft Aug 4, 2026; preliminary):**
  - In Korea in 2026, speculators pre-positioned ahead of LETF closing rebalances, enlarged the funds' orders, and then liquidated into them.
  - Korean stocks tracked by LETFs reversed about 75% of their first-day response to pre-open US news by the next close.
  - Self-reinforcing rebalancing raised SK Hynix's annualized volatility from 100.0% to 136.7% over nine weeks and cost its LETF holders 17.6%.
  - Source: [arXiv 2608.03703](https://arxiv.org/abs/2608.03703)
- **2026 market-wide LETF rebalancing (Benzinga citing Bloomberg data, July 2026):**
  - Daily LETF rebalancing flows "surged fourfold since the start of 2026, hitting a record $50 billion" and made up a record 1.60% of S&P 500 futures volume.
  - Total LETF assets were $193B.
  - "More than $50 billion of leveraged ETF assets is now concentrated in semiconductor-focused products."
  - Source: [Benzinga, July 2026](https://www.benzinga.com/etfs/broad-u-s-equity-etfs/26/07/60264868/leveraged-etf-rebalancing-hits-50-billion-as-traders-warn-of-a-powerful-force-now-driving-us-market-volatility)
  - **[conflict]** A differently dated figure puts leveraged ETFs in chip stocks at "$21 billion" — [Memeburn (undated)](https://memeburn.com/leveraged-etfs-in-chip-stocks-hit-21-billion/). Total LETF AUM is reported variously as a record $198B — [Crypto Briefing](https://cryptobriefing.com/leveraged-etfs-record-198b-aum/) — or about $200B — [24/7 Wall St, Jul 10, 2026](https://247wallst.com/investing/2026/07/10/analyst-reveals-how-200-billion-in-leveraged-etfs-could-amplify-the-next-market-selloff/)
- **Market gamma:** a Bloomberg Odd Lots analyst (via 24/7 Wall St, Jul 10, 2026) argues that the roughly $200B leveraged cohort now "overwhelm[s] the long gamma from overwriting [covered-call] products," tilting net market gamma negative — [24/7 Wall St](https://247wallst.com/investing/2026/07/10/analyst-reveals-how-200-billion-in-leveraged-etfs-could-amplify-the-next-market-selloff/)

### Inferences
**Derivation.** Take AUM A₀ with exposure L·A₀. After an index move r:
- Exposure drifts to L·A₀(1+r).
- AUM becomes A₁ = A₀(1+L·r).
- Target exposure is L·A₁.
- Required trade = L·A₀(1+L·r) − L·A₀(1+r) = L(L−1)·A₀·r.

For SOXL, L(L−1) = 6. For SOXS, (−3)(−4) = +12. Both trades have the same sign as r.

**SOXS worked example** (A₀ = $1.74B, index +5%):
- Short exposure drifts from −$5.22B to −$5.48B.
- AUM falls to $1.48B.
- Target exposure is −3 × $1.48B = −$4.44B.
- The fund must *buy back* about $1.04B (= 12 × 1.74 × 0.05) of index exposure into the close.

**Size relative to end-of-day AUM** (formula L(L−1)r/(1+L·r)):

| Index day | SOXL | SOXS |
|---|---|---|
| +1% | +5.8% | +12.4% |
| −1% | −6.2% | −11.7% |
| +3% | +16.5% | +39.6% |
| −3% | −19.8% | −33.0% |
| +5% | +26.1% | +70.6% |
| −5% | −35.3% | −52.2% |

**Combined SOXL+SOXS rebalancing notional** (sign follows the index; AUM scenarios bracket the conflicting cited figures):

| Scenario | ±1% day | ±3% day | ±5% day |
|---|---|---|---|
| A: SOXL $12.0B, SOXS $1.0B (early-2026 levels) | $0.72 + 0.12 = **$0.84B** | $2.16 + 0.36 = **$2.52B** | $3.60 + 0.60 = **$4.20B** |
| B: SOXL $18.0B, SOXS $1.5B | **$1.26B** | **$3.78B** | **$6.30B** |
| C: SOXL $24.3B, SOXS $1.74B (YCharts/TradingView snippets) | $1.46 + 0.21 = **$1.67B** | **$5.00B** | $7.30 + 1.04 = **$8.34B** |

**Per-stock allocation in scenario C on a 5% day** (SOXX-proxy weights), before any netting:

| Stock | Notional |
|---|---|
| NVDA | ≈ $786M |
| MU | ≈ $743M |
| AMD | ≈ $686M |
| AVGO | ≈ $624M |
| INTC | ≈ $425M |
| MRVL | ≈ $389M |
| TSM | ≈ $388M |
| AMAT | ≈ $383M |
| LRCX | ≈ $356M |
| KLAC | ≈ $344M |

**What these gross figures overstate or leave out:**
- Same-day creations and redemptions offset or add, in line with Ivanov & Lenkey. Contrarian dip-buying in SOXL on down days, for example from Korean retail, reduces SOXL's required selling.
- Swap dealers may pre-hedge intraday or net against other client flows, so the imbalance seen at the close is likely smaller than the gross hedge change.
- Semiconductor single-stock LETFs and 2x sector LETFs rebalance in the same direction, so total semiconductor LETF closing demand exceeds SOXL+SOXS alone. Benzinga's more than $50B of semiconductor-focused LETF assets suggests it is several times larger.

**Timing and backtest implications:**
- The swap reference and NAV are the 4:00 pm close, so hedges concentrate in the closing auction (MOC/LOC) and the last 30–60 minutes. This matches the last-30-minute window in Baltussen et al.
- For backtests, the testable prediction is that SOXL/SOXS and their main constituents show same-direction drift into the close on large |r| days, scaled by (6·A_SOXL + 12·A_SOXS)·r relative to closing-auction volume, with partial next-day reversal.
- Zhao (2026) suggests that when this flow is large and predictable, pre-positioning can shift the effect earlier in the day.

### Gaps
- Direxion does not disclose its execution method (MOC vs. last-hour algorithms), the split between fund stock trades and dealer hedges, or which counterparties carry which share of the swaps in 2026.
- No SOXL/SOXS-specific academic estimate of close-price impact was found.
- No closing-auction imbalance data attributable to SOXL/SOXS was found.
- The rebalancing estimate depends on an AUM figure that could not be pinned down for Sept 2026.
- The Cheng & Madhavan MOC-share figures were seen only through secondary citations.

---

## 4. Price vs value: NAV, IIV/iNAV, premiums/discounts, creation/redemption arbitrage

### Takeaway
NAV is struck at 4:00 pm ET. Direxion's market-price returns use the bid/ask midpoint at 4:00 pm. Since August 19, 2022, leveraged/inverse ETFs can rely on Rule 6c-11, whose website disclosures cover daily holdings, prior-day NAV, premium/discount history and the 30-day median bid-ask spread.

Closing premiums/discounts appear small; undated snippets show +0.1% and −0.4%. The intraday indicative value (IIV) convention is the ".IV" suffix (SOXL.IV), historically published every 15 seconds. The SEC no longer requires an IIV under 6c-11, though exchange listing rules did at adoption.

Creation units were 25,000 shares in the 2022 SAI [older] and are handled by authorized participants (APs) with cash balancing amounts. Because exposure is fixed intraday and ICESEMI prints every second, market makers can price SOXL/SOXS precisely off the index. This is what keeps SOXL close to 3× the index move since the prior close.

### Cited Findings
- **Rule 6c-11 disclosures:** ETFs must post, on a free public website:
  - portfolio holdings before each day's open;
  - the prior day's NAV, market price and premium/discount;
  - the median bid-ask spread over the last rolling 30 days (using the national best bid and offer);
  - a disclosure and discussion if the premium or discount exceeded 2% for more than seven consecutive trading days.
  - Sources: [National Law Review, Rule 6c-11 compliance](https://natlawreview.com/article/program-compliance-exchange-traded-fund-rule-6c-11); [SEC Rule 6c-11 adopting release (2019)](https://www.sec.gov/files/rules/final/2019/33-10695.pdf)
- **Leveraged ETFs under 6c-11:** the Rule 18f-4 package changed Rule 6c-11 so leveraged/inverse ETFs can rely on it if they comply with Rule 18f-4. The SEC rescinded the sponsors' prior exemptive orders, with a compliance date of Aug 19, 2022 — [SEC 18f-4 adopting release](https://www.sec.gov/files/rules/final/2020/ic-34084.pdf); [SEC press release 2020-269](https://www.sec.gov/newsroom/press-releases/2020-269)
- **IIV:**
  - The intraday NAV (INAV/IIV/IOPV) is accessed "by adding '.IV' to an ETF's ticker," is "calculated at 15-second intervals," and is shown on sites such as Yahoo Finance and Thomson Reuters. The search identified SOXL.IV as SOXL's IIV ticker — [ETF Trends](https://www.etftrends.com/how-to-know-youre-getting-the-best-price-on-etf-trades/); [Direxion SOXL/SOXS fact sheet](https://www.direxion.com/uploads/SOXL-SOXS-Fact-Sheet.pdf) (appeared in results; contents not readable)
  - Rule 6c-11 does not require an IIV. At adoption, however, exchange rules still required IIV dissemination "at least every 15 seconds … until such time as the exchanges amend their rules" — [Chapman and Cutler](https://www.chapman.com/publication-SEC-Adopts-ETF-Rule); [Finance Research Letters, "Rethinking intraday indicative values"](https://www.sciencedirect.com/science/article/pii/S1544612320300520)
- **Closing price convention:** Direxion's "Market Price returns are based upon the midpoint of the bid/ask spread at 4:00 pm EST (when NAV is normally calculated)" — [Direxion page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs)
- **Premium/discount data:** Direxion hosts a premium/discount page for all its ETFs, and YCharts tracks the SOXL series. Undated snippets show premium/discount readings of +0.1% and −0.4% — [Direxion premium/discount](https://www.direxion.com/premium-discount); [YCharts SOXL premium/discount](https://ycharts.com/companies/SOXL/discount_or_premium_to_nav)
- **Creation/redemption [older, 2022 SAI]:**
  - One creation unit is 25,000 shares.
  - Units can be bought only by or through DTC participants that have signed an Authorized Participant Agreement.
  - Units are issued at the next-determined NAV.
  - APs pay a cash Balancing Amount plus a Transaction Fee.
  - The unit size may change.
  - Source: [Direxion Shares ETF Trust 485BPOS (2022)](https://www.sec.gov/Archives/edgar/data/1424958/000119312522215059/d384761d485bpos.htm)
- **Index feed for real-time valuation:** ICESEMI has been published every second since Jan 31, 2022 — [ICE notice](https://www.ice.com/publicdocs/equity_indices/notices/ICEBIO_ICESEMI_Methodology_Updates_20220128.pdf)

### Inferences
- **How arbitrage keeps SOXL near 3× the index move:**
  - Intraday fair value is almost deterministic: FV ≈ NAV_{t−1}·(1 ± 3·r_ICESEMI) − accruals.
  - Market makers hedge with constituent baskets, SOXX/SMH, index-correlated futures or swaps, and APs create or redeem at the 4:00 pm NAV.
  - Intraday deviations should therefore be bounded by hedging costs: tighter in regular hours and wider at the open, in fast markets, and in pre-market, after-hours and overnight sessions, where there is no live index and little or no AP activity.
- **Flows feed the next rebalance:** creations and redemptions change AUM and therefore the next day's rebalancing base. This links the price-vs-value mechanism to Section 3; for example, heavy dip-buying creations in SOXL shrink the required closing sale.
- **SOXS arbitrage:** SOXS exposure is entirely short swaps, so AP arbitrage runs through dealers' short hedges. Premiums/discounts may behave differently from SOXL in stressed rallies. This is unverified.

### Gaps
- No source was found for typical *intraday* premium/discount statistics for SOXL/SOXS, or for their current median bid-ask spreads.
- It was not verified whether SOXL.IV/SOXS.IV are still published in 2026, by which calculation agent, or at what frequency.
- Bloomberg/Refinitiv IIV tickers were not found.
- The current (2026) creation unit size and cut-off times were not verified.

---

## 5. Market-structure mechanics: tick size, round lots, LULD bands and halts, extended-hours and overnight trading

### Takeaway
As of Sept 27, 2026:
- **Tick size:** penny ticks still apply. The SEC's half-penny tick (amended Rule 612) was adopted in Sept 2024 and upheld by the D.C. Circuit in Oct 2025, but compliance was deferred first to Nov 2026 and then, in June 2026, to the first business day of November 2027.
- **Round lots:** since Nov 3, 2025, round lots are price-tiered. SOXL (about $150) and SOXS (about $30s) both remain at 100 shares.
- **LULD:** leveraged ETPs are excluded from the Tier 1 ETP list, so they are Tier 2. Their LULD percentage parameter is the Tier 2 value times the leverage ratio: 10% × 3 = 30% for a reference price above $3. Amendment 18 removed closing-period doubling for Tier 2 stocks above $3.
- **Halts:** no documented SOXL/SOXS LULD pauses were found.
- **Overnight:** trading currently runs on ATSs. Blue Ocean trades 8 pm–4 am ET, and it suspended SOXL from about Aug 31 to Sep 10, 2026 under the Reg ATS fair-access threshold. Exchange sessions are scheduled: Nasdaq 23/5, NYSE Arca 22-hour and 24X, targeted for Dec 6, 2026. LULD Amendment 27 (approved Aug 2026) adds temporary 20% static overnight bands, multiplied by leverage for leveraged ETPs.

### Cited Findings
- **Tick size rule:** adopted Sept 18, 2024. It sets a $0.005 increment for NMS stocks priced at or above $1 whose time-weighted average quoted spread is $0.015 or less during a three-month Evaluation Period, run twice a year — [SEC fact sheet 34-101070](https://www.sec.gov/files/34-101070-fact-sheet.pdf); [Sidley (Oct 2024)](https://www.sidley.com/en/insights/newsupdates/2024/10/sec-adopts-rules-modifying-minimum-pricing-increments-access-fee-caps-and-order-transparency). About 74.3% of stocks (on 2023 data) would have qualified for half-penny quoting — [Katten](https://katten.com/sec-revises-tick-size-access-fees-and-round-lot-definition-and-takes-steps-to-disseminate-odd-lot-and-other-better-priced-orders)
- **First delay (Oct 2025):** the SEC exempted compliance with Rules 600(b)(89)(i)(F), 610(c) and 612 until the first business day of November 2026 — [SEC press release 2025-130](https://www.sec.gov/newsroom/press-releases/2025-130-sec-issues-exemptive-order-regarding-compliance-certain-rules-under-regulation-nms); [Atkins statement, Oct 15, 2025](https://www.sec.gov/newsroom/speeches-statements/atkins-101525-statement-regarding-minimum-pricing-increments-access-fee-caps). In Oct 2025 the D.C. Circuit upheld the tick-size/fee-cap rule, "but its future remains uncertain" — [Sidley (Oct 2025)](https://www.sidley.com/en/insights/newsupdates/2025/10/dc-circuit-upholds-sec-tick-size-fee-cap-rule)
- **Second delay (June 2026):** the SEC extended relief for Rule 612 (and 610(c)) to the first business day of November 2027. It cited the cumulative 2026 workload, including Rule 605, expanded trading hours and other infrastructure changes — [Federal Register, June 15, 2026](https://www.federalregister.gov/documents/2026/06/15/2026-11997/order-granting-temporary-exemptive-relief-pursuant-to-section-36a1-of-the-securities-exchange-act-of); [SEC Release 34-105656](https://www.sec.gov/files/rules/exorders/2026/34-105656.pdf); [Atkins statement, June 11, 2026](https://www.sec.gov/newsroom/speeches-statements/atkins-statement-minimum-pricing-increments-access-fee-caps-061126). At the same time the SEC proposed rolling back core Regulation NMS provisions, including scrapping the trade-through rule (Rule 611) — [TradeInformer](https://tradeinformer.com/regulations/sec-extends-nms-relief-rule-611-repeal-2027); [Morrison Foerster (June 2026)](https://www.mofo.com/resources/insights/260612-sec-proposes-landmark-rollback-of-core-regulation)
- **Round lots:** since Nov 3, 2025, amended Rule 600(b)(93) sets round lots by the average closing price over the prior evaluation period:

  | Average closing price | Round lot |
  |---|---|
  | ≤ $250 | 100 shares |
  | $250.01–$1,000 | 40 shares |
  | $1,000.01–$10,000 | 10 shares |
  | > $10,000 | 1 share |

  Sizes are reassigned semiannually from a one-month evaluation period — [Schwab: Round Lots Regulatory Changes](https://www.schwab.com/learn/story/round-lots-regulatory-changes); [CTA Round Lot FAQ](https://www.ctaplan.com/publicdocs/ctaplan/CTA_Round_Lot_Changes_FAQ.pdf); [UTP Vendor Alert 2025-10](https://www.nasdaqtrader.com/TraderNews.aspx?id=UTP2025-10). Odd-lot information compliance was set for the first business day of May 2026 — [Katten](https://katten.com/sec-revises-tick-size-access-fees-and-round-lot-definition-and-takes-steps-to-disseminate-odd-lot-and-other-better-priced-orders)
- **LULD tiers:** Tier 1 is the S&P 500, the Russell 1000 and selected ETPs; base bands are 5% for Tier 1 and 10% for Tier 2 — [Nasdaq LULD FAQ](https://www.nasdaqtrader.com/content/MarketRegulation/LULD_FAQ.pdf); [etfdb](https://etfdb.com/core-strategies-channel/why-etfs-experience-limit-up-down-protections). "Leveraged ETPs were excluded from eligibility to be included as LULD Tier 1 ETPs," so they are Tier 2 regardless of volume — [Cboe LULD FAQ](https://www.cboe.com/document/tech-spec/document/technical-specifications/cboe-limit-updown-faq); [Cboe Tier 1 ETP list notice (Jul 2025)](https://www.cboe.com/notices/content/?id=55096)
- **LULD leveraged-ETP parameter:** the Tier 2 percentage parameters are 10% (reference price above $3), 20% ($0.75–$3.00), and the lesser of $0.15 or 75% (below $0.75). For a Tier 2 leveraged ETP, the parameter "is the applicable Percentage Parameter … multiplied by the leverage ratio of such product" — [SEC Release 34-101036 (2024, quoting plan text)](https://www.sec.gov/files/rules/other/2024/34-101036.pdf); [LULD Plan site](https://www.luldplan.com/)
- **Amendment 18 (effective about Feb 24, 2020) [older]:**
  - It eliminated doubling between 3:35 and 4:00 pm for Tier 2 stocks with a reference price above $3.00.
  - Tier 1 stocks and Tier 2 stocks at or below $3.00 keep the doubled closing-period parameters.
  - Doubling during the opening period (first 15 minutes) continues.
  - Sources: [Cboe LULD FAQ](https://www.cboe.com/document/tech-spec/document/technical-specifications/cboe-limit-updown-faq); [UTP Vendor Alert 2019-9](https://www.nasdaqtrader.com/TraderNews.aspx?id=UTP2019-09); [Oppenheimer LULD primer](https://oppenheimer.com/getmedia/b6be4644-8879-479a-beab-06e348619003/limit-up-limit-down.pdf)
- **LULD pause mechanics:** if a stock does not leave a Limit State within 15 seconds, the primary listing exchange declares a five-minute trading pause on all venues — [FINRA: Guardrails for Market Volatility](https://www.finra.org/investors/insights/guardrails-market-volatility)
- **LULD Amendment 27 (overnight):**
  - Approved by the SEC on Aug 5, 2026 (Release 34-106042; published 91 FR 51515, Aug 10, 2026).
  - It sets "temporary static bands 20% above and below two reference points" during "Overnight Protected Hours," without automatic trading pauses.
  - As extracted, the overnight percentage parameter for a leveraged ETP is 20% multiplied by its leverage ratio.
  - Sources: [Federal Register, Aug 10, 2026](https://www.federalregister.gov/documents/2026/08/10/2026-16201/joint-industry-plan-order-granting-approval-of-the-twenty-seventh-amendment-to-the-national-market); [SEC Release 34-106042](https://www.sec.gov/files/rules/sro/nms/2026/34-106042.pdf)
  - NYSE Arca filed changes to its clearly-erroneous rule 7.10-E (Federal Register, Sept 23, 2026; contents not retrieved) — [Justia/FR 2026-19398](https://regulations.justia.com/regulations/fedreg/2026/09/23/2026-19398.html)
- **Blue Ocean ATS:** trades US NMS stocks from 8:00 pm to 4:00 am ET, Sunday to Thursday — [Blue Ocean Technologies](https://www.blueocean-tech.io/). SOXL has a Blue Ocean (BOATS) symbol page on TradingView — [TradingView BOATS:SOXL](https://www.tradingview.com/symbols/BOATS-SOXL)
- **Blue Ocean suspension of SOXL (Aug–Sep 2026):**
  - Blue Ocean suspended 18 securities, most of them leveraged or inverse products including SOXL and KORU, starting with "Monday's 8 p.m. ET session" (report dated Sept 2, 2026).
  - The trigger was the SEC Fair Access Rule, under which an ATS that handles 5% or more of a security's volume in four of the preceding six months becomes subject to extra requirements.
  - Korean retail investors were left trading these ETFs "without access to real-time quotes during daytime hours" (Korean time).
  - "Beginning Thursday, September 10 at 8pm," Blue Ocean said it would no longer halt symbols for Rule 301(b)(5) fair-access reasons, and SOXL and KORU became available again.
  - Sources: [The Investor (Korea Herald)](https://www.theinvestor.co.kr/article/10860560); [Blue Ocean service status](https://blueocean-tech.io/blue-ocean-ats-service-status/)
  - **[older, Aug 2024]** Blue Ocean previously suspended overnight trading altogether (Robinhood notice) — [Robinhood on X](https://x.com/AskRobinhood/status/1820600734259519577?lang=en)
- **Broker 24/5 programs:**
  - Robinhood's 24 Hour Market covers 922 stocks and ETFs, from Sunday 8 pm to Friday 8 pm ET, executed through ATSs — [Robinhood support](https://robinhood.com/us/en/support/articles/24hour-market)
  - Schwab offers 1,100+ securities 24/5 on thinkorswim; the eligible list is in the "24 Hour Trading" public watchlist — [Schwab press release (2025)](https://pressroom.aboutschwab.com/press-releases/press-release/2025/Schwab-Makes-Expanded-24-Hour-Trading-Available-to-All-Clients/default.aspx)
  - SOXL/SOXS eligibility on either program was not confirmed.
- **Exchange overnight sessions (not yet live on Sept 27, 2026):**
  - The SEC approved Nasdaq's 23/5 proposal on April 10, 2026 — [Simpson Thacher memo](https://www.stblaw.com/docs/default-source/memos/firmmemo_04_29_26)
  - NYSE Arca received approval for 22-hour trading: 1:30 am–11:30 pm ET Monday to Thursday and 1:30 am–8:00 pm ET Friday — [Jones Day (Sept 2026)](https://www.jonesday.com/en/insights/2026/09/nyse-and-nasdaq-move-to-23hour-trading-day-overnight-session-is-an-evolution-but-not-yet-a-revolution); [NYSE Extended-Hours FAQ v4.0 (Aug 2026)](https://www.nyse.com/publicdocs/nyse/NYSE_Extended_Hours_Trading_FAQ.pdf)
  - The overnight sessions (9:00 pm–4:00 am ET, with an 8–9 pm pause and no opening auction) are planned from Dec 6, 2026 — [Jones Day](https://www.jonesday.com/en/insights/2026/09/nyse-and-nasdaq-move-to-23hour-trading-day-overnight-session-is-an-evolution-but-not-yet-a-revolution); [Massive (Polygon) blog](https://massive.com/blog/us-equities-move-to-23-5-trading)
  - 24X National Exchange's "24X Market Session" (9 pm–4 am ET) targets Dec 6, 2026, falling back to Jan 24, 2027 if the SIPs' extended-hours amendments are not ready. Only broker-dealers that are 24X members can trade it — [SEC exemptive order 34-106061 (2026)](https://www.sec.gov/files/rules/exorders/2026/34-106061.pdf); [24X overnight FAQ](https://equities.24exchange.com/overnight-trading-faqs); [PR Newswire, Apr 29, 2026](https://www.prnewswire.com/news-releases/24x-national-exchanges-response-letter-urges-sec-approval-of-temporary-exemption-to-launch-overnight-trading-302756559.html)
  - An SEC roundtable on preparations for 24-hour trading took place in Sept 2026 (Commissioner Peirce's remarks; URL suffix 091726) — [SEC](https://www.sec.gov/newsroom/speeches-statements/peirce-remarks-sec-roundtable-091726)
- **Documented halts:** searches found no documented LULD pause specific to SOXL or SOXS. NYSE publishes historical trading-halt data — [NYSE Trading Halt Data](https://www.nyse.com/trade-halt)

### Inferences
- **Tick size and round lots:**
  - SOXS, with a lower price and heavy volume, is more likely than SOXL (about $150) to be "tick-constrained" (TWAQS ≤ $0.015) and so eligible for half-penny quoting. Nothing changes before November 2027.
  - Both funds are well below $250, so round lots stay at 100 shares unless SOXL's price more than doubles.
- **LULD bands:**
  - With 30% bands (reference price = average price over the preceding 5 minutes), a SOXL/SOXS LULD pause needs roughly a 10% ICESEMI move within minutes. That makes such pauses rare and helps explain why none were found.
  - If opening-period doubling applies, bands are wider still in 9:30–9:45.
  - At the close (3:35–4:00) there is no doubling for these Tier 2 products above $3, so the late-day rebalancing window runs under the standard 30% bands.
- **Overnight trading:**
  - Overnight SOXL trading takes place without a computed index, on fragmented ATS liquidity. Korean daytime demand is concentrated there, so overnight SOXL prints partly reflect Korean retail flow and Asian semiconductor moves (TSMC, SK Hynix, Samsung).
  - The Aug 31–Sep 10, 2026 Blue Ocean suspension is a data-quality event for overnight backtests: expect missing or thin BOATS data for SOXL in that window.
  - After the Dec 2026 launch of exchange overnight sessions, the funds' "day" and NAV remain 4:00 pm–to–4:00 pm. Overnight trades will therefore price off a fixed prior-close NAV plus proxy information, and will fall under Amendment 27's 60% (20% × 3) static bands if the extracted parameter is correct.

### Gaps
- The primary LULD plan text could not be read. Unconfirmed: whether opening-period doubling applies to leveraged ETPs' already-multiplied 30% parameter, whether any cap applies, and the exact overnight leveraged-ETP parameter.
- No list of historical SOXL/SOXS LULD pauses was found; NYSE's historical halt files would need to be checked.
- Broker-level overnight eligibility of SOXL/SOXS was not confirmed for Robinhood, Schwab, Interactive Brokers or moomoo, and SOXS's status on Blue Ocean is unknown.
- The exact start date of the Blue Ocean suspension (reported as "Monday's 8 p.m. ET session", most likely Aug 31, 2026) and the full list of 18 securities were not retrieved.

---

## 6. Corporate actions: SOXL splits and SOXS reverse splits (for price-data adjustment)

### Takeaway
**SOXL:** one forward split found, 15-for-1, payable after the close on Mar 1, 2021 with an ex-date of Mar 2, 2021. No SOXL split was found in 2026. Direxion's June 10, 2026 announcement covered two 20-for-1 forward splits and seven reverse splits effective July 15, 2026, but SOXL was not identified among the forward splits, and its late-Sept 2026 price of about $150 is consistent with no split.

**SOXS:** frequent reverse splits. Three are confirmed:
- 1-for-10, after the close Apr 12, 2024 (split-adjusted trading Apr 15, 2024)
- 1-for-20, after the close Mar 4, 2026 (split-adjusted Mar 5, 2026; new CUSIP 25461H572)
- 1-for-10, ex-date Jul 15, 2026

Earlier ones (2021, 2022) are only partly verified. One aggregator counts 10 SOXS reverse splits in total. The cumulative factor since April 2024 alone is 2,000.

### Cited Findings
- **SOXL 15:1 [older, 2021]:**
  - Direxion announced on Jan 29, 2021 forward splits for SOXL (15-for-1), the Technology Bull 3X (10-for-1) and the S&P 500 High Beta Bull 3X (7-for-1), plus two reverse splits — [PR Newswire](https://www.prnewswire.com/news-releases/direxion-announces-forward-and-reverse-splits-of-five-etfs-301218362.html)
  - Payable Mar 1, 2021, with an ex-distribution date of Mar 2, 2021; OCC memo #48245 is dated Feb 3, 2021 — [OCC memo 48245](https://infomemo.theocc.com/infomemos?number=48245); [MIAX alert](https://www.miaxglobal.com/sites/default/files/alert-files/SOXL_Split_48245.pdf); [InvestorPlace (Mar 2021)](https://investorplace.com/2021/03/soxl-split-whats-going-on-today-with-the-semiconductor-etfs-15-for-1-stock-split/)
- **No SOXL split in 2026:** split-history pages extracted in Sept 2026 show SOXL's most recent split as the 15-1 on Mar 2, 2021 — [SplitHistory SOXL](https://www.splithistory.com/soxl/); [SymbolSurfing SOXL](https://symbolsurfing.com/soxl-stock-split-history)
- **June 10, 2026 announcement:** Direxion said it would execute forward share splits (twenty shares for each share held) for two ETFs and reverse splits for seven others, "after the close of the markets on July 14, 2026 (the 'Payable Date')," with split-adjusted trading from July 15, 2026 — [Direxion "to Split Nine ETFs"](https://www.direxion.com/press-release/direxion-to-split-nine-etfs); [FinanceWire, Jun 10, 2026](https://financewire.com/2026/06/10/direxion-to-split-nine-etfs/). **[conflict]** One search summary stated that SOXL took a 20-for-1 split on Jul 15, 2026, but it did not cite fund-specific text. Split-history pages and SOXL's price level contradict it.
- **SOXS 1-for-10, April 2024 [older]:**
  - Effective after the close Apr 12, 2024; split-adjusted trading on NYSE Arca from Apr 15, 2024.
  - Every ten shares became one, cutting shares outstanding by about 90%.
  - Sources: [Direxion release (Mar 15, 2024)](https://markets.financialcontent.com/bpas/article/newsdirect-2024-3-15-direxion-announces-reverse-split-of-soxs/); [MIAX corporate action alert, Apr 12, 2024](https://www.miaxglobal.com/alert/2024/04/12/miax-exchange-group-options-markets-corporate-action-alert-direxion-daily-0); [OCC memo 54368](https://infomemo.theocc.com/infomemos?number=54368); [Direxion 497 (2024)](https://www.sec.gov/Archives/edgar/data/1424958/000119312524069178/d809212d497.htm)
- **SOXS 1-for-20, March 2026:**
  - Direxion announced on Feb 4–5, 2026 reverse splits for JDST, SOXS, DUST, HIBS, MUD and TSLS, at 20-for-1 or 10-for-1 depending on the fund, effective after the close Mar 4, 2026, with CUSIP changes on Mar 5, 2026 — [Direxion release PDF (02.04.26)](https://www.direxion.com/uploads/6-ETFs-Reverse-Split-Press-Release-02.04.26_.pdf); [GlobeNewswire, Feb 5, 2026](https://www.globenewswire.com/news-release/2026/02/05/3232643/0/en/Direxion-Announces-Reverse-Split-of-JDST-SOXS-DUST-HIBS-MUD-TSLS.html)
  - OCC memo #58364 (Feb 13, 2026): each SOXS share converted "into the right to receive 0.05 (New)" shares, i.e., 1-for-20. The new CUSIP is 25461H572 — [MIAX copy of OCC 58364](https://www.miaxglobal.com/sites/default/files/alert-files/SOXS_Reverse_Split_58364.pdf); [BOX memo 207584](https://boxexchange.com/assets/BOXOnnMemo207584.pdf); [Dinari (LinkedIn)](https://www.linkedin.com/posts/dinari-global_a-1-for-20-reverse-soxs-stock-split-is-scheduled-activity-7434299079150534656-3nvu)
  - **[conflict]** One search extract described the March 2026 SOXS split as 1-for-10. The OCC terms (0.05 new shares) indicate 1-for-20; the 1-for-10 description likely mixes it up with July 2026.
- **SOXS 1-for-10, July 2026:** OCC memo #59294 for the "Direxion Daily Semiconductor Bear 3X ETF", reverse split effective Wednesday, July 15, 2026, converting each share into the right to receive 0.1 new shares — [OCC memo 59294](https://infomemo.theocc.com/infomemos?number=59294); [MIAX alert, Jul 14, 2026](https://www.miaxglobal.com/alert/2026/07/14/miax-exchange-group-options-markets-corporate-action-alert-direxion-daily-3)
- **Older SOXS reverse splits (partly verified):**
  - A DRIP & SOXS reverse split announcement exists (about 2022; ratio and date not retrieved) — [PR Newswire](https://www.prnewswire.com/news-releases/direxion-announces-reverse-splits-of-two-etfs-drip--soxs-301486023.html)
  - A secondary extract gives a 1-for-10 SOXS reverse split in January 2021 (unverified) — [Bybit Wiki SOXS split history](https://www.bybit.com/en/wiki/article/soxs-stock-split-history-5-splits-explained/)
  - ROIC says SOXS "has had 10 reverse stock splits in total," with July 2026 the 10th and the second of 2026 — [ROIC SOXS splits](https://www.roic.ai/quote/SOXS/stock-splits)
  - Direxion publishes a split Q&A document — [Direxion split Q&A](https://www.direxion.com/uploads/Direxion-Leveraged-ETFs-Forward-Reverse-Split-QA.pdf)

### Inferences
- **Adjustment factors:**
  - SOXS prices before Apr 15, 2024 must be multiplied by 2,000 (10 × 20 × 10) to compare with post–Jul 15, 2026 prices, and volumes and shares divided by 2,000, before also applying any earlier (2021/2022) factors.
  - SOXL prices before Mar 2, 2021 are divided by 15 and volumes multiplied by 15.
- **Identifier and options mapping:**
  - Each reverse split changes the CUSIP (for example, to 25461H572 in March 2026).
  - Options on SOXS get adjusted deliverables through OCC memos.
  - Holdings (N-PORT/13F), options open interest and short-interest time series need CUSIP/root mapping across split dates.
- **Recurrence:** SOXS reverse splits recur because an inverse 3× product loses value in a rising, volatile sector. The two 2026 reverse splits (factor 200 within five months) coincide with the 2026 semiconductor rally.

### Gaps
- The full, verified list of all SOXS reverse splits (dates, ratios, CUSIPs) was not obtained; ROIC's count of 10 is unverified.
- The post-July-2026 SOXS CUSIP was not retrieved.
- The identities of the two funds given 20-for-1 forward splits in July 2026 were not retrieved.

---

## 7. Catalysts that drive semiconductor intraday moves, and machine-readable calendars

### Takeaway
SOXL/SOXS intraday moves come from six main sources:
- **Constituent news.** Earnings from the heaviest weights (NVDA, MU, AMD, AVGO) matter most, followed by INTC, MRVL, TSM, AMAT, LRCX and KLAC.
- **TSMC monthly revenue,** released around the 10th of each month.
- **US macro releases** such as CPI, payrolls and FOMC decisions.
- **Unscheduled policy headlines** on export controls and tariffs.
- **Scheduled structural days:** quarterly index rebalances on the 3rd Friday of March, June, September and December, which coincide with quad witching (2026: Mar 20, Jun 18/19, Sep 18, Dec 18), and monthly options expiration.
- **Korean retail flows.**

Machine-readable calendars exist for most scheduled items: the FRED API, BLS iCal, the Alpha Vantage earnings CSV, TSMC's IR page and its Form 6-K filings on EDGAR.

### Cited Findings
- **TSMC monthly revenue:** released "around the 10th of each month". 2026 releases:

  | Revenue month | Release date |
  |---|---|
  | January | Feb 10 |
  | February | Mar 10 |
  | March | Apr 10 |
  | April | May 8 |
  | May | Jun 10 |
  | June | Jul 13 (delayed by a Jul 10 typhoon day-off) |
  | July | Aug 10 |

  TSMC posts these on its IR site and files them on SEC Form 6-K — [TSMC 2026 monthly revenue](https://investor.tsmc.com/english/monthly-revenue/2026); [TSMC financial calendar](https://investor.tsmc.com/english/financial-calendar); [TSM 6-K, Jul 13, 2026](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000447/tsm-revenue20260713.htm); [TSMC July 2026 revenue report](https://pr.tsmc.com/english/news/3329). Reported June 2026 sales drove a "revenue surge of 68%" — [Euronews, Jul 13, 2026](https://www.euronews.com/business/2026/07/13/tsmcs-june-sales-drive-revenue-surge-of-68-ahead-of-earnings-report)
- **Export-control headlines (examples):**
  - May 31, 2026: the US took a step to halt Nvidia AI chip shipments to Chinese firms outside China — [CNBC, May 31, 2026](https://www.cnbc.com/2026/05/31/us-takes-step-to-halt-nvidia-ai-chip-shipments-to-chinese-firms-outside-china.html)
  - **[older, Apr 2025]** New licensing requirements for Nvidia H20 and AMD MI308 exports to China led to a $5.5B Nvidia charge. Premarket moves: NVDA −5.2%, AMD −5.9%, MU −3.5%, AVGO −3.1% — [Benzinga (Apr 2025)](https://benzinga.com/25/04/44841356/chip-stocks-are-facing-selling-pressure-wednesday-heres-why)
- **Quad witching 2026:** Mar 20, Jun 19, Sep 18 and Dec 18 (third Fridays). June 19 is the Juneteenth market holiday, so the practical June expiration shifted to June 18 — [TradeStation (Jan 2026)](https://www.tradestation.com/insights/2026/01/23/quadruple-witching-dates-2026-stock-futures-trading/); [Option Alpha](https://optionalpha.com/learn/quadruple-witching). ICESEMI's quarterly rebalances fall on the same third Fridays (Section 1, from secondary extracts).
- **Macro calendars:**
  - FRED's `fred/release/dates` endpoint returns release dates as XML or JSON; FRED also runs an Economic Release Calendar — [FRED API docs](https://fred.stlouisfed.org/docs/api/fred/release_dates.html); [FRED release calendar](https://fred.stlouisfed.org/releases/calendar)
  - Other official machine-readable sources, per secondary listings: the BLS iCalendar feed, Census economic-indicator calendar, BEA release-date feed and Federal Reserve calendar — [Apify official US economic calendar](https://apify.com/redfoxxie/official-us-economic-release-calendar); [GitHub example using BLS/FRED feeds](https://github.com/jwplatta/tickrake/pull/94)
- **Earnings calendars:** Alpha Vantage `function=EARNINGS_CALENDAR` returns CSV with a 3-, 6- or 12-month horizon. Free-tier limits were documented as 5 requests per minute and 500 per day (may be outdated) — [Macroption guide](https://www.macroption.com/alpha-vantage-earnings-calendar/); [Alpha Vantage docs](https://www.alphavantage.co/documentation/)
- **Korean retail flow as a catalyst:**
  - SOXL was Korean investors' most-purchased security in June 2026 ($3.77B net).
  - Korean investors poured nearly $4B into SOXL in June–July, yet holdings rose only from $5.35B (end-May) to $5.81B (end-July).
  - SOXL's six-month buy-plus-sell settlement value was $56.4B, more than six times Micron's.
  - Source: [Seoul Economic Daily, Sept 24, 2026](https://en.sedaily.com/finance/2026/09/24/leveraged-etf-executives-flock-to-korea-as-local-buying)
  - Korean retail net-bought $431M of SOXL in early September 2026, then turned net sellers, unloading $677M — [Seoul Economic Daily, Sept 6, 2026](https://en.sedaily.ai/finance/2026/09/06/korean-retail-investors-dump-chip-stocks-pile-into-3x); [Seoul Economic Daily, Sept 13, 2026](https://en.sedaily.com/finance/2026/09/13/korean-retail-investors-turn-net-sellers-of-us-stocks)
  - Korean curbs on single-stock 2× products redirected Korean retail toward 3× ETFs such as SOXL — [Seoul Economic Daily, Jul 21, 2026](https://en.sedaily.com/finance/2026/07/21/leveraged-etf-rules-drive-korean-investors-to-soxl-tqqq); [Asia Business Daily, Aug 4, 2026](https://www.asiae.co.kr/en/article/2026080416131786841)
- **2026 volatility context:** SOXL turned $10,000 into $56,000, then "lost a fifth in one month" (article Aug 4, 2026) — [24/7 Wall St](https://247wallst.com/investing/etf/2026/08/04/this-3x-semiconductor-etf-turned-10000-into-56000-then-lost-a-fifth-in-one-month/). SOXX took in $5.4B in a single day in 2026 — [ETF.com](https://www.etf.com/sections/daily-etf-flows/semiconductor-etfs-roar-back-soxx-pulls-54-billion-single-day)

### Inferences
- **Event weights:** NVDA, MU, AMD and AVGO carry about 34% of index weight, so their earnings are the largest scheduled single-name catalysts for SOXL/SOXS.
- **Earnings timing:** most of these report outside regular hours (general market convention; not verified per company here). The price impact therefore lands as an overnight or pre-market gap relative to the prior 4:00 pm NAV, not as intraday drift.
- **TSMC timing:** TSMC's monthly figures come out during Asian hours, so they reach SOXL through the TSM ADR pre-market and US-listed peers.
- **Quarterly Fridays:** the 3rd-Friday quarterly dates combine index-rebalance trades, quad-witching hedge unwinds and the normal LETF close rebalance. They are natural candidates for a "structural close" flag in backtests.
- **Unscheduled headlines:** export-control and tariff headlines need a news feed or event scraping. The Federal Register is the machine-readable venue for Commerce Department/BIS rules; this is a suggestion and was not verified here.

### Gaps
- Official Q3/Q4 2026 earnings dates for constituents, the 2026 FOMC/BLS schedules and ICE's official 2026 rebalance calendar were not retrieved (primary pages blocked).
- No quantitative event study of SOXL/SOXS around TSMC monthly revenue, CPI or FOMC releases was found.
- Weights for ASML and QCOM in ICESEMI were not retrieved; ASML is an ADR subject to the ADR cap.

---

## 8. External data sources for tracking and backtesting (what, where, free vs paid)

### Takeaway
- **Fund-level data:** holdings (stocks plus swap notional), NAV, shares outstanding and premium/discount come free from Direxion's product page (daily holdings CSV) and the Rule 6c-11 disclosures. History comes from SEC EDGAR (N-PORT, N-CSR, 485BPOS/497) and from paid aggregators such as YCharts and Bloomberg.
- **Index and constituents:** index levels are free on Yahoo (^ICESEMI, ^ICESEMIT), NYSE and CNBC pages. Licensed intraday and constituent data come from ICE (paid). iShares SOXX daily holdings are a free proxy for index weights.
- **Options:** open interest and IV are available freemium from Market Chameleon, OptionCharts and FlashAlpha, with Cboe DataShop (paid) and OCC-reported OI underneath.
- **Short interest and short volume:** free from FINRA (twice-monthly short interest; daily off-exchange short-sale volume; Query API).
- **Flows:** ETF.com fund-flows tool (free), or computed from daily shares outstanding × NAV.
- **Korean holdings:** KSD SEIBro portal (free), with English-language press coverage.
- **Market structure:** NYSE halt history, the LULD plan site, SIP round-lot and LULD band data, and Blue Ocean's status page and BOATS prints.

### Cited Findings
- **Direxion (free):** each product page offers a "Daily Fund Holdings (csv)" download alongside the prospectus and fact sheet — [Direxion SOXL/SOXS page](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs); [example Direxion product page listing holdings CSV](https://www.direxion.com/product/daily-mu-bull-and-bear-leveraged-single-stock-etfs). Premium/discount history is on a separate page — [Direxion premium/discount](https://www.direxion.com/premium-discount). A SOXL/SOXS fact sheet lists index top-ten holdings — [Direxion fact sheet PDF](https://www.direxion.com/uploads/SOXL-SOXS-Fact-Sheet.pdf). Rule 6c-11 requires daily pre-open holdings, prior-day NAV, market price, premium/discount and the 30-day median spread on a free website — [National Law Review](https://natlawreview.com/article/program-compliance-exchange-traded-fund-rule-6c-11)
- **SEC EDGAR (free):** Direxion Shares ETF Trust (CIK 1424958) files:
  - NPORT-P reports with swap-level detail: counterparty, reference index, financing rate and notional — [NPORT-P, 07/31/2023](https://www.sec.gov/Archives/edgar/data/1424958/000114554923059576/direxionetfs_73123.htm)
  - N-CSR annual reports — [N-CSR FY2021](https://www.sec.gov/Archives/edgar/data/1424958/000110465922000321/tm213700d1_ncsr.htm)
  - 485BPOS/497 prospectus updates and supplements (creation units, splits) — [485BPOS (2022)](https://www.sec.gov/Archives/edgar/data/1424958/000119312522215059/d384761d485bpos.htm); [497 (Feb 2026)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526037667/d80567d497.htm)
- **Index levels:**
  - ^ICESEMI and ^ICESEMIT daily history on Yahoo Finance (free download) — [Yahoo ^ICESEMI](https://finance.yahoo.com/quote/%5EICESEMI/history/)
  - NYSE index quote pages for ICESEMI, ICESEMIT and ICESEMIN — [NYSE ICESEMI](https://www.nyse.com/quote/index/ICESEMI)
  - CNBC quote page for .ICESEMI — [CNBC](https://www.cnbc.com/quotes/.ICESEMI)
  - The index is published every second — [ICE notice](https://www.ice.com/publicdocs/equity_indices/notices/ICEBIO_ICESEMI_Methodology_Updates_20220128.pdf)
  - ICE also launched Semiconductor Index futures in 2022 — [ICE press release](https://ir.theice.com/press/news-details/2022/ICE-Launches-Biotechnology-Index-Futures-and-Semiconductor-Index-Futures-Contracts/default.aspx)
- **Index-weight proxy (free):** iShares SOXX product page, daily holdings and fact sheet — [iShares SOXX](https://www.ishares.com/us/products/239705/ishares-semiconductor-etf); [SOXX fact sheet](https://www.ishares.com/us/literature/fact-sheet/soxx-ishares-semiconductor-etf-fund-fact-sheet-en-us.pdf)
- **Options OI and IV:**
  - Market Chameleon: SOXL open-interest trends and daily OI history for about the last year — [Market Chameleon](https://marketchameleon.com/Overview/SOXL/OpenInterestTrends/)
  - OptionCharts: historical SOXL volume, OI, IV and max pain — [OptionCharts](https://optioncharts.io/options/SOXL/option-history)
  - FlashAlpha: dealer gamma exposure built from OCC-reported OI after the close — [FlashAlpha](https://flashalpha.com/stock/soxl)
  - Cboe DataShop (paid): Open-Close Volume Summary and option trade files — [Cboe DataShop](https://datashop.cboe.com/cboe-options-open-close-volume-summary)
  - Cboe delayed quote table (free) — [Cboe SOXL quotes](https://res.cboe.com/delayed_quotes/soxl/quote_table)
  - The average bid/ask spread across SOXL's options chain was reported at 15.59% — [Options Analysis Suite](https://www.optionsanalysissuite.com/etf/soxl/options-chain)
- **Short interest and short volume (FINRA, free):**
  - FINRA Rule 4560 requires member firms to report short positions twice a month, and FINRA publishes short interest for all exchange-listed and OTC equities — [FINRA short interest](https://www.finra.org/finra-data/browse-catalog/equity-short-interest); [FINRA reporting](https://www.finra.org/filing-reporting/regulatory-filing-systems/short-interest)
  - Daily Short Sale Volume Files aggregate short-sale volume reported to FINRA facilities (TRF/ADF/ORF, i.e., off-exchange). Older data comes as monthly files or via the Query API (CSV/JSON) — [FINRA daily short sale volume](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files); [FINRA Developer API](https://developer.finra.org/docs/api-explorer/query_api-equity-reg_sho_daily_short_sale_volume)
  - Third-party freemium option: Equibles (100 requests/day) — [Equibles](https://equibles.com/short-interest-api)
- **Fund flows:**
  - ETF.com fund-flows tool (free) and daily-flow articles — [ETF.com flows tool](https://www.etf.com/etfanalytics/etf-fund-flows-tool)
  - ETF Action commentary — [ETF Action](https://www.etfaction.com/leveraged-equity-etfs-draw-892m-as-traders-pile-into-soxl-and-broad-market-funds/)
  - ICI aggregate ETF net issuance — [ICI](https://www.ici.org/research/stats/combined_flows)
  - YCharts AUM series (paid upgrade needed for full data) — [YCharts SOXL AUM](https://ycharts.com/companies/SOXL/total_assets_under_management)
- **Shares-outstanding history (third-party, use with caution):** 243 data points since Jul 27, 2018. **[conflict]** Its reported 103.96M shares on Apr 1, 2025 looks inconsistent with SOXL's AUM at the time — [SharesOutstandingHistory](https://www.sharesoutstandinghistory.com/soxl/)
- **Korean holder data:** KSD's SEIBro portal publishes Korean investors' foreign-securities custody and settlement statistics by security. The press uses it for SOXL holdings, for example $5.93B on Sept 21, 2026 — [Seoul Economic Daily, Sept 24, 2026](https://en.sedaily.com/finance/2026/09/24/leveraged-etf-executives-flock-to-korea-as-local-buying); [Wikipedia: Korea Securities Depository](https://en.wikipedia.org/wiki/Korea_Securities_Depository). Korean holdings of US shares passed $200.01B on May 14, 2026, and the value of US stocks traded by Korean investors rose from $48.9B in January to $65.6B in June 2026 — [Seoulz](https://www.seoulz.com/korea-us-stock-investors/)
- **Halts, LULD, round lots and overnight venues:**
  - NYSE historical trading-halt data — [NYSE Trading Halt Data](https://www.nyse.com/trade-halt)
  - LULD Plan documents and annual reports — [luldplan.com](https://www.luldplan.com/); [LULD 2024 annual report](https://cdn.luldplan.com/reports/LULD-2024-Annual-Report.pdf)
  - SIP round-lot size changes are published by CTA and UTP — [CTA FAQ](https://www.ctaplan.com/publicdocs/ctaplan/CTA_Round_Lot_Changes_FAQ.pdf); [UTP alert](https://www.nasdaqtrader.com/TraderNews.aspx?id=UTP2025-10)
  - LULD band messages are carried on the CTA/UTP SIP feeds — [CTA LULD Amendment 18 notice](https://www.ctaplan.com/publicdocs/ctaplan/notifications/trader-update/CQS_CTS_LULD_Amendment_18_Notification_Update.pdf)
  - Blue Ocean publishes halts and suspensions on its service-status page, and BOATS prints are viewable on TradingView — [Blue Ocean status](https://blueocean-tech.io/blue-ocean-ats-service-status/); [TradingView BOATS:SOXL](https://www.tradingview.com/symbols/BOATS-SOXL)
- **Calendars:** see Section 7 — FRED API, BLS iCal, Alpha Vantage `EARNINGS_CALENDAR`, TSMC IR and 6-K filings.

### Inferences
**Suggested daily backtest panel** (all free except where noted):
- Direxion NAV, shares outstanding and holdings CSV, split into stock holdings and swap notional by counterparty. The file must be scraped daily; history is not guaranteed.
- ICESEMI and ICESEMIT closes from Yahoo or NYSE.
- SOXX weights, as the index-weight proxy.
- The fund's implied rebalancing need: 6·A_SOXL·r + 12·A_SOXS·r.
- Flows: Δshares × NAV.
- FINRA short interest (twice monthly) and daily off-exchange short volume.
- Options OI and IV (freemium, or Cboe DataShop paid).
- Korean net buying and holdings (KSD/SEIBro via press, weekly or monthly).
- Event flags: earnings, TSMC monthly revenue, CPI/NFP/FOMC, 3rd-Friday opex and quad witching, index rebalance days, export-control headlines.
- Corporate-action factors for SOXS/SOXL (Section 6).

**Intraday work:**
- 1-second ICESEMI (a licensed feed) or a constituent-based reconstruction plus SOXL/SOXS consolidated trades and quotes (TAQ-type data, paid) are needed to measure premiums/discounts, late-day drift and closing-auction pressure.
- ICESEMIT (total return) is the right benchmark for fund-return decomposition, because the swaps pay the index's total return.

### Gaps
- The exact Direxion CSV URL pattern, how far back the history goes, and the column schema were not verified (egress blocked).
- Whether Direxion or the exchanges provide historical IIV (SOXL.IV) data was not established.
- No free source of historical intraday ICESEMI levels was confirmed.
- The export format and API of SEIBro (Korean-language portal) were not verified.
- Current swap counterparty and notional detail (2025–2026 N-PORT) was not retrieved.
- Licensing terms and costs for ICE index data and Cboe/OCC options data were not researched.
