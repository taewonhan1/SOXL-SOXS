# Practical, regulatory and tax issues for a US retail trader switching SOXL↔SOXS intraday (status as of 2026-10-03)

*Method note (applies to all sections).* The network proxy blocked direct fetches from finra.org, irs.gov, direxion.com, federalregister.gov, ecfr.gov, investor.gov, law.cornell.edu, greentradertax.com, broker sites (Schwab, Fidelity, IBKR, Robinhood, Webull), luldplan.com, nyse.com, nasdaqtrader.com and most news sites. **sec.gov and EDGAR were reachable** (with a declared User-Agent). Every sec.gov/EDGAR link below was downloaded and read in this session. The session's web-search budget (200 calls, mostly used by earlier tasks) ran out partway through. Items marked *(search snippet)* rest only on search-engine extracts. Items marked *(prior notes)* reuse sourced findings from `research_notes/SOXL and SOXS intraday behavior/` (dated Sept 27, 2026). Items marked *(local computation)* are my calculations on this repo's Polygon/Massive data, with the file path given. Tax-statute items marked *[statute — not fetched]* cite the governing law, but the page could not be opened in this session.

---

## 1. Daily reset and volatility decay: why compounding hurts multi-day holds but barely matters intraday; issuer/regulator holding-period guidance; how far SOXL/SOXS drift from 3x/−3x

### Takeaway
SOXL and SOXS reset their exposure at every 4:00 pm close, so compounding ("volatility") decay builds up only across closes. In an open-to-close hold, SOXL moved a median 2.96× and SOXS −3.01× the index's open-to-close move (2021–2026). Over multiple days the funds drift far from ±3×. In 2024, for example, the index proxy rose 12.2% while SOXL fell 13.0% and SOXS fell 61.4%. Direxion sets no maximum holding period. It says the funds pursue their objective only for a single trading day and suit only investors who "actively monitor and manage their portfolios". Its own table shows that a flat index at 50% volatility costs SOXL −52.8% and SOXS −77.7% over a year.

### Cited Findings
**Issuer statements (current summary prospectuses dated Feb 27, 2026)**
- SOXL "seeks daily investment results, before fees and expenses, of 300% of the daily performance of the Index. The Fund does not seek to achieve its stated investment objective for a period of time different than a trading day." — [SOXL summary prospectus, Feb 27, 2026 (EDGAR 497K)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)
- SOXS seeks "300% of the inverse (or opposite) of the daily performance of the Index", with the same one-trading-day limitation — [SOXS summary prospectus, Feb 27, 2026 (EDGAR 497K)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- Multi-day warning, SOXL: "For periods longer than a single day, the Fund will lose money if the Index's performance is flat, and it is possible that the Fund will lose money even if the Index's performance increases over a period longer than a single day. An investor could lose the full principal value of his/her investment within a single day if the Index loses more than 33% in one day." — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)
- SOXS carries the mirror warning: it can lose even if the index *decreases* over multiple days, and holders lose everything "if the Index gains more than 33% in one day" — [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- Suitability language (both funds): designed "only by knowledgeable investors who understand the potential consequences of seeking daily leveraged (3X) investment results … and are willing to monitor their portfolios frequently. The Fund is not intended to be used by, and is not appropriate for, investors who do not intend to actively monitor and manage their portfolios." Neither document states a specific maximum holding period. — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- **"Intra-Day Investment Risk"** (both funds):
  - "The intra-day performance of Fund shares traded in the secondary market will be different from the performance of the Fund when measured from the close of the market on a given trading day until the close of the market on the subsequent trading day. An investor that purchases shares intra-day may experience performance that is greater than, or less than, the Fund's stated investment objective."
  - "In response to significant intraday market volatility … the Adviser may determine to trade a portion or all of the rebalance trade for the Fund prior to market close."
  - The shares "may experience significant premiums or discounts, or widened bid-ask spreads."
  - Sources: [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- **Direxion's hypothetical one-year table** (fund return before fees/financing, by one-year index return and annualized index volatility):

  | Index 1-yr return | SOXL @10% vol | @25% | @50% | @75% | SOXS @10% vol | @25% | @50% | @75% |
  |---|---|---|---|---|---|---|---|---|
  | −20% | −50.3% | −57.6% | −75.8% | −90.5% | +83.9% | +34.2% | −56.4% | −93.3% |
  | −10% | −29.3% | −39.6% | −65.6% | −86.5% | +29.2% | −5.7% | −69.4% | −95.3% |
  | 0% | −3.0% | −17.1% | −52.8% | −81.5% | −5.8% | −31.3% | −77.7% | −96.6% |
  | +10% | +29.2% | +10.3% | −37.1% | −75.4% | −29.2% | −48.4% | −83.2% | −97.4% |
  | +20% | +67.7% | +43.3% | −18.4% | −68.0% | −45.5% | −60.2% | −87.1% | −98.0% |

  Sources: [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- **Index volatility used by Direxion:** "The Index's annualized historical volatility rate for the period from April 13, 2021 (the inception date of the Index) to December 31, 2025 was 36.03%." The highest single calendar year was 44.38%, and annualized index performance over the period was 17.91%. — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)
- **Reported fund returns** (periods ended 12/31/2025):

  | Measure | SOXL | SOXS | NYSE Semiconductor Index |
  |---|---|---|---|
  | 1-year return | +55.05% | −85.48% | +41.22% |
  | 5-year annualized | +6.83% | −71.13% | n/a |
  | 10-year annualized | +38.43% | −74.30% | n/a |
  | Best quarter | +98.91% (Q2 2020) | +76.11% (Q2 2022) | n/a |
  | Worst quarter | −65.90% (Q2 2022) | −72.66% (Q2 2025) | n/a |

  Sources: [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)

**Quantified divergence (local computation).** The inputs are split-adjusted daily closes from Polygon/Massive for June 2021 to Sept 25, 2026. SOXX serves as the 1× proxy for the NYSE Semiconductor Index: it is price-only, so it excludes about 0.6% a year of dividends. SOXX is the index-weight proxy used in the prior notes — [iShares SOXX](https://www.ishares.com/us/products/239705/ishares-semiconductor-etf) *(prior notes)*. Data files: [SOXL.parquet](../../data/behavior/daily_adj/SOXL.parquet), [SOXS.parquet](../../data/behavior/daily_adj/SOXS.parquet), [SOXX.parquet](../../data/behavior/daily_adj/SOXX.parquet).
- **Daily close-to-close tracking is tight:** SOXL vs SOXX daily returns have correlation 0.9990 and beta 2.957, and the daily tracking difference has a standard deviation of about 33 bp. SOXS's beta is −2.992.
- **Calendar-period divergence (close-to-close):**

  | Period | SOXX (proxy) | 3× proxy | SOXL actual | −3× proxy | SOXS actual |
  |---|---|---|---|---|---|
  | 2021-12-30 → 2022-12-30 (vol 43%) | −36.0% | −108.1% | −85.9% | +108.1% | **+15.5%** |
  | 2022-12-30 → 2023-12-29 (vol 28%) | +65.6% | +196.7% | +224.7% | −196.7% | −85.3% |
  | 2023-12-29 → 2024-12-31 (vol 35%) | +12.2% | +36.6% | **−13.0%** | −36.6% | −61.4% |
  | 2024-12-31 → 2025-12-31 (vol 40%) | +39.8% | +119.3% | +53.9% | −119.3% | −86.1% |
  | 2025-12-31 → 2026-09-25 (vol 50%) | +90.2% | +270.5% | +260.3% | −270.5% | −94.8% |
  | 2021-08-25 (index switch) → 2026-09-25 | +272.1% | +816.2% | +238.2% | −816.2% | −99.975% |

- **Both funds fell while the index was flat:**
  - Apr 2 → May 2, 2025 (21 sessions): SOXX +0.29%, SOXL −18.27%, SOXS −39.95%.
  - May 11 → Aug 11, 2026 (63 sessions): SOXX +0.27%, SOXL −30.15%, SOXS −46.30%.
- **Rolling-window gap between fund return and ±3× proxy return** (median, with p90 in brackets):

  | Window | SOXL | SOXS |
  |---|---|---|
  | 5 days | 0.56% (1.73%) | 0.85% (3.05%) |
  | 21 days | 2.64% (6.93%) | 3.83% (13.60%) |
  | 63 days | 7.69% (20.40%) | 13.05% (39.48%) |
  | 252 days | 37.68% (65.16%) | 71.44% (217.91%) |

- **Intraday open→close tracking** (1,127 sessions with a SOXX open-to-close move above 0.3%):
  - SOXL/SOXX return ratio: median 2.960 (IQR 2.816–3.105), regression beta 2.969, median absolute deviation from 3×SOXX 19 bp (p90 56 bp).
  - SOXS: median ratio −3.012 (IQR −3.214 to −2.818), beta −3.013, median absolute deviation 25 bp (p90 75 bp).
- **Daily tracking shortfall vs ±3× proxy (mean, bp/day):**

  | Period | SOXL − 3×SOXX | SOXS + 3×SOXX |
  |---|---|---|
  | 2021 | −0.9 | −1.4 |
  | 2022 | −2.3 | −1.5 |
  | 2023 | −4.4 | +3.7 |
  | 2024 | −5.5 | +4.4 |
  | 2025 | −4.9 | +2.2 |
  | 2026 YTD | −7.0 | +3.8 |
  | May 1 – Sep 25, 2026 | −9.6 | — |

  These figures include fees, swap financing and the omitted SOXX dividends; see §3 for the 2026 swap spreads.

### Inferences
- **Why decay is a multi-day phenomenon.** A daily-reset fund with leverage L loses about (L²−L)·σ²/2 per day in log terms relative to L × the index's log return, where σ is daily index volatility. That is about −3σ² a day for SOXL and −6σ² for SOXS.
  - This formula reproduces Direxion's table exactly: flat index at 50% vol gives e^(−3·0.25) − 1 = −52.8% for SOXL and e^(−6·0.25) − 1 = −77.7% for SOXS. At 25% vol it gives −17.1% and −31.3%.
  - At ~40% annualized index volatility (~2.5% a day), multi-day holding costs roughly 0.19% a day for SOXL and 0.38% a day for SOXS. **SOXS decays about twice as fast as SOXL**, which matters if the switcher sometimes holds the bear side overnight.
- **Why it "barely" matters intraday.** The funds do not rebalance during the session, so there is no compounding within a day. What changes intraday is the *effective leverage of new money*.
  - With x = index move since the prior close, SOXL's leverage is 3(1+x)/(1+3x) and SOXS's is −3(1+x)/(1−3x).

    | x (index since prior close) | SOXL effective leverage | SOXS effective leverage |
    |---|---|---|
    | +1% | 2.94× | −3.12× |
    | +3% | 2.83× | −3.40× |
    | +5% | 2.74× | −3.71× |
    | −3% | 3.20× | −2.67× |
    | −5% | 3.35× | −2.48× |

  - Example: switching into SOXS after a +5% morning buys −3.71× exposure per dollar, not −3×. This matches the empirical open→close ratio IQR (2.82–3.11 for SOXL). It is the "greater than, or less than" effect in Direxion's Intra-Day Investment Risk paragraph.
- **What happens at the close.** Any position held through 4:00 pm is reset at the closing NAV. Holding for "several days" then exposes the switcher to the decay above, to overnight gaps and to the 33% one-day wipe-out scenario.
- **Fees and financing accrue daily in NAV.** A trader who is flat at each close bears only a small fraction of the 4–10 bp/day shortfall measured above; an overnight holder bears all of it.

### Gaps
- **SEC/FINRA holding-period guidance not retrieved.** The 2009 joint SEC/FINRA investor alert on leveraged and inverse ETFs could not be read: the sec.gov URL https://www.sec.gov/investor/pubs/leveragedetfs-alert.htm redirects to investor.gov, which was blocked. FINRA Regulatory Notice 09-31 on leveraged/inverse ETF suitability (https://www.finra.org/rules-guidance/notices/09-31) was also blocked. Their exact holding-period wording (commonly summarized as "typically unsuitable for retail investors who plan to hold them for longer than one trading session") is **unverified here**.
- No 2025–2026 SEC or FINRA statement setting a specific holding-period limit for leveraged ETFs was found.
- No ICESEMI index series was available locally. SOXX is a close but imperfect proxy: price-only, carries its own expense ratio, and tracks the NYSE Semiconductor Index per the prior notes, not re-verified here.

---

## 2. Corporate actions: SOXS reverse splits and SOXL splits (full history, including 2026), and their effect on price level, tick cost in bps, and charts/backtests

### Takeaway
SOXS has had **10 reverse splits** since 2011, for a cumulative factor of **960,000,000:1**. Two were in 2026: 1-for-20 effective Mar 5, 2026, and 1-for-10 effective Jul 15, 2026. SOXL has had **two forward splits**: 4-for-1 effective May 20, 2015, and 15-for-1 effective Mar 2, 2021. It has had none in 2026, although it closed as high as $300.77. Each SOXS reverse split lifts the price from ~$2–5 back to ~$34–50. That cuts the one-cent tick from ~23–52 bps to ~2.4–3 bps of price. It also leaves split-adjusted histories with absurd early prices (~$170,000 per SOXS share in mid-2021) and fractional historical volumes, and it changes the CUSIP.

### Cited Findings
**Primary-source split history (Direxion prospectus supplements on EDGAR).** "Effective" is the first split-adjusted trading day.

| # | Fund | Ratio | After close of | Split-adjusted trading from | Direxion supplement (EDGAR) |
|---|---|---|---|---|---|
| 1 | SOXS | 1-for-5 | Wed Feb 23, 2011 | Thu Feb 24, 2011 | [497, Jan 31, 2011](https://www.sec.gov/Archives/edgar/data/1424958/000089418911000294/drxnetf_497e.htm) |
| 2 | SOXS | 1-for-4 | Aug 19, 2013 | Aug 20, 2013 | [497, Jul 22, 2013](https://www.sec.gov/Archives/edgar/data/1424958/000089418913003866/drxnshrs-etftrst_497e.htm) |
| 3 | SOXS | 1-for-4 | May 19, 2015 | May 20, 2015 | [497, Apr 20, 2015](https://www.sec.gov/Archives/edgar/data/1424958/000119312515138276/d911085d497.htm) |
| — | **SOXL** | **4-for-1 (forward)** | May 19, 2015 | May 20, 2015 | [497, Apr 20, 2015](https://www.sec.gov/Archives/edgar/data/1424958/000119312515138280/d911082d497.htm) |
| 4 | SOXS | 1-for-5 | Apr 28, 2017 | May 1, 2017 | [497, Feb 28, 2017](https://www.sec.gov/Archives/edgar/data/1424958/000119312517062380/d341060d497.htm) |
| 5 | SOXS | 1-for-10 | Jun 27, 2019 | Jun 28, 2019 | [497, May 24, 2019](https://www.sec.gov/Archives/edgar/data/1424958/000119312519156999/d753383d497.htm) |
| 6 | SOXS | 1-for-12 | Aug 27, 2020 | Aug 28, 2020 | [497, Jul 27, 2020](https://www.sec.gov/Archives/edgar/data/1424958/000119312520199763/d49996d497.htm) |
| — | **SOXL** | **15-for-1 (forward)** | Mar 1, 2021 | Mar 2, 2021 | [497, Jan 29, 2021](https://www.sec.gov/Archives/edgar/data/1424958/000119312521022676/d59468d497.htm) |
| 7 | SOXS | 1-for-10 | Fri Mar 25, 2022 | Mon Mar 28, 2022 | [497, Feb 18, 2022](https://www.sec.gov/Archives/edgar/data/1424958/000119312522046674/d315590d497.htm) |
| 8 | SOXS | 1-for-10 | Fri Apr 12, 2024 | Mon Apr 15, 2024 | [497, Mar 15, 2024](https://www.sec.gov/Archives/edgar/data/1424958/000119312524069178/d809212d497.htm) |
| 9 | SOXS | **1-for-20** | Mar 4, 2026 | Mar 5, 2026 | [497, Feb 4, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526037667/d80567d497.htm) |
| 10 | SOXS | **1-for-10** | Jul 14, 2026 | Jul 15, 2026 | [497, Jun 10, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526265931/d101574d497.htm); re-issued [Jun 26, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526285638/d156414d497.htm) |

- **Earlier SOXS supplements, 2010–2018:** the EDGAR scan of 497 filings tagged to the SOXS series (S000027921) found no other split notice. The trust's 2012 financial highlights do mention a "1:5 reverse stock split" on Nov 10, 2011, but that footnote could not be tied to SOXS. — [EDGAR 497, Jul 3, 2012](https://www.sec.gov/Archives/edgar/data/1424958/000119312512293801/d375923d497.htm)
- **Aggregator cross-check:** an aggregator lists the same 10 SOXS reverse splits with matching dates and ratios — [ROIC SOXS splits](https://www.roic.ai/quote/SOXS/stock-splits) *(search snippet; page blocked)*
- **Vendor data cross-check:** the vendor's split records confirm the six SOXS splits since 2019 (execution dates 2019-06-28, 2020-08-28, 2022-03-28, 2024-04-15, 2026-03-05, 2026-07-15) and the two SOXL splits (2015-05-20, 2021-03-02) — [dq_splits.csv](../../analysis/backtests/output/dq_splits.csv) *(local)*
- **Unadjusted price jump at each recent SOXS split** (prior close → split-day open):

  | Split date | Prior close | Split-day open |
  |---|---|---|
  | Jun 28, 2019 | $5.14 | $50.19 |
  | Aug 28, 2020 | $3.63 | $43.14 |
  | Mar 28, 2022 | $3.49 | $35.85 |
  | Apr 15, 2024 | $3.52 | $33.82 |
  | Mar 5, 2026 | $1.93 | $39.59 |
  | Jul 15, 2026 | $4.28 | $41.23 |

  Source: [dq_splits.csv](../../analysis/backtests/output/dq_splits.csv) *(local)*
- **The July 2026 batch:** seven reverse splits, including SOXS at 1-for-10, plus two 20-for-1 forward splits (Direxion Daily MSCI South Korea Bull 3X ETF and Direxion Daily MU Bull 2X ETF). SOXL was not included. — [497, Jun 10, 2026 (reverse)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526265931/d101574d497.htm); [497, Jun 10, 2026 (forward)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526265925/d105555d497.htm)
- **SOXL's 2026 price range:** closes ranged from $40.62 to $300.77, and the last close was $151.45 on Sep 25, 2026. No 2026 split appears in the vendor split feed. — [SOXL.parquet](../../data/behavior/daily_adj/SOXL.parquet) *(local)*
- **Mechanics stated by Direxion (Feb 2026 supplement):**
  - "the per share net asset value ('NAV') and next day's opening market price will be approximately twenty, or ten-times higher."
  - "fractional shares cannot trade on the Exchange. Thus, a Fund will redeem for cash a shareholder's fractional shares at the Fund's split-adjusted NAV … a shareholder could recognize a gain or loss … Otherwise, the reverse splits will not result in a taxable transaction."
  - Source: [497, Feb 4, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526037667/d80567d497.htm)
- **CUSIP changes:**
  - March 2026: SOXS CUSIP 25460G112 → 25461H572 — [497, Feb 4, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526037667/d80567d497.htm)
  - July 2026: the supplement lists SOXS's "current" CUSIP as 25460G336 and the new one as 25461H291 — [497, Jun 10, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526265931/d101574d497.htm)
  - **[conflict]** The "current" CUSIP in the June 2026 supplement (25460G336) does not match the post-March CUSIP (25461H572) in the February supplement.
- **Stated policy:** "The Trust reserves the right to adjust the price levels of the Shares in the future to help maintain convenient trading ranges for investors. Any adjustments would be accomplished through stock splits or reverse stock splits, which would have no effect on the net assets of the Fund." — [Direxion prospectus, EDGAR 497, Mar 3, 2016](https://www.sec.gov/Archives/edgar/data/1424958/000119312516491338/d120125d497.htm)
- **Tick size relative to price** (prior notes, microstructure analysis):
  - One cent equalled 0.66 bps of SOXL's price and 3.08 bps of SOXS's on 2026-09-25 — [price_levels.csv](../../analysis/microstructure/output/price_levels.csv)
  - SOXS's relative tick jumped from ~55 bps to ~3 bps at the Mar 5, 2026 split and from ~21 bps to ~2–3 bps at the Jul 15, 2026 split — [microstructure notes](../SOXL%20and%20SOXS%20intraday%20behavior/microstructure_and_liquidity.md); [tick_constraint_summary.csv](../../analysis/microstructure/output/tick_constraint_summary.csv)
  - SOXS's effective spread was 15.06 bps in 2025 (price ~$12) versus 2.32 bps in the post-July-2026 regime, because the cents spread barely changes while the price does — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- **Half-penny tick rule postponed:** the SEC's half-penny increment for tick-constrained stocks (amended Rule 612, adopted Sep 18, 2024) has been deferred to "the first business day of November 2027", after an earlier deferral to November 2026. SOXS, which sits at one tick most of the time, would be a candidate once it takes effect. — [SEC Release 34-105656 (June 11, 2026)](https://www.sec.gov/files/rules/exorders/2026/34-105656.pdf)
- **Backtest and chart artifacts in split-adjusted data:**
  - SOXS's first stored bar (Jun 1, 2021) shows an adjusted close of $170,200 and an adjusted volume of about 482 shares — [SOXS.parquet](../../data/behavior/daily_adj/SOXS.parquet) *(local)*
  - After a reverse split, SOXS options carry adjusted roots, e.g. `O:SOXS1270115C00001000` — [prior notes, data_elements_and_backtesting.md](../SOXL%20and%20SOXS%20intraday%20behavior/data_elements_and_backtesting.md)

### Inferences
- **Cost of one 1-cent tick in bps before vs after each split** (arithmetic on the prices above):

  | Split | Before | After |
  |---|---|---|
  | Mar 2026 | 51.8 bps ($1.93) | 2.5 bps ($39.59) |
  | Jul 2026 | 23.4 bps ($4.28) | 2.4 bps ($41.23) |
  | Apr 2024 | 28.4 bps ($3.52) | 3.0 bps ($33.82) |

  SOXS is quoted at one tick most of the time, so its round-trip cost in bps is mostly a function of its price. That cost rises steadily as SOXS decays and collapses ~10–20× at each reverse split. A SOXL↔SOXS switcher's cost per switch therefore varies through the split cycle.
- **SOXL's tick cost moves the other way.** At $40 one cent is ~2.5 bps; at $300 it is ~0.33 bps. Above roughly $100 SOXL quotes multi-tick spreads (see §3), so its cost is set by competition rather than by the tick.
- **Splits are announced about 3–6 weeks ahead:**

  | Split | Supplement date | Effective date | Notice |
  |---|---|---|---|
  | SOXS 2024 | Mar 15, 2024 | Apr 15, 2024 | ~4 weeks |
  | SOXS Mar 2026 | Feb 4, 2026 | Mar 5, 2026 | ~4 weeks |
  | SOXS Jul 2026 | Jun 10, 2026 | Jul 15, 2026 | ~5 weeks |
  | SOXL 2021 | Jan 29, 2021 | Mar 2, 2021 | ~4.5 weeks |

  Historically, SOXS reverse-splits once its price has decayed to roughly $2–5. Given its −3× decay in a rising, volatile chip market (two reverse splits within five months of 2026), another reverse split is likely whenever SOXS falls back into that range. This is a pattern, not a stated policy.
- **Backtest practice:**
  - Model spreads and ticks on unadjusted prices.
  - Model returns on split-adjusted prices.
  - Multiply historical volumes by the cumulative split factor.
  - Map CUSIPs and options roots across split dates.
  - Expect a one-off fractional-share cash-out, which can be a small taxable event, if a position is held over a split.

### Gaps
- The June 2026 supplement's "current" CUSIP for SOXS (25460G336) conflicts with the March 2026 new CUSIP (25461H572). This was not resolved: the OCC and exchange notices were blocked.
- How brokers handle open GTC/stop orders over split dates (cancel vs adjust) was not researched; broker sites were blocked.
- Pre-2019 split dates are confirmed only by Direxion supplements, not by exchange or OCC notices.

---

## 3. Liquidity and costs in 2026: spreads, average daily volume, AUM, expense ratios, swap financing; the PHLX → NYSE (ICE) Semiconductor Index switch

### Takeaway
In mid/late 2026 SOXL is a ~$19.4B fund trading ~64M shares (~$8.7B) a day. SOXS is a ~$1.6B fund trading ~62M shares (~$2.8B) a day. Quoted RTH spreads average ~3–4 bps for both: SOXL ~5¢ with multi-tick quotes, SOXS pinned at 1¢. Spreads are about twice as wide in the first 30 minutes. Net expense ratios are 0.75% for SOXL (with a fee waiver through Sep 1, 2027) and 1.00% for SOXS. Both have tracked the NYSE Semiconductor Index (ICE Data Indices) since **Aug 25, 2021**, replacing the PHLX Semiconductor Sector Index. 2026 N-PORT data show SOXL paying large spreads over SOFR on $44.9B of swaps, which matters for overnight holders, not intraday ones.

### Cited Findings
**Expense ratios (prospectus fee tables, Feb 27, 2026)**

| Item | SOXL | SOXS |
|---|---|---|
| Management fee | 0.75% | 0.75% |
| 12b-1 fee | 0.00% | 0.00% |
| Other expenses | 0.12% | 0.12% |
| Acquired fund fees and expenses | 0.04% | 0.13% |
| Gross total | 0.91% | 1.00% |
| Expense cap / reimbursement | −0.16% | none |
| **Net total** | **0.75%** | **1.00%** |
| Reported portfolio turnover (excludes derivatives) | 250% | 0% |

- SOXL's waiver is an "Advisory Fee Waiver Agreement … through September 1, 2027" that "may be terminated or revised at any time with the consent of the Board of Trustees" — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)
- SOXS figures — [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)

**Index and index switch**
- "As of August 25, 2021, the Fund began to seek a daily leveraged investment objective … of 300% of the NYSE Semiconductor Index", replacing the PHLX Semiconductor Sector Index. SOXS changed to −300% of the same index on the same date. — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- The index began on Apr 13, 2021. It is "a rules-based, modified float-adjusted market capitalization-weighted index that tracks the performance of the thirty largest U.S. listed semiconductor companies" (ICE Uniform Sector Classification). It is "rebalanced quarterly and reconstituted annually" and had 30 constituents as of Dec 31, 2025. The licensor is ICE Data Indices, LLC. — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)
- Naming: the N-PORT swap descriptions call it the "ICE Semiconductor Index" — [SOXL N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404435/primary_doc.xml). ICE brands it "NYSE Semiconductor Index" (ticker ICESEMI) — *(prior notes)*.

**AUM and holdings (N-PORT for period ended Jul 31, 2026, filed Sep 28, 2026)**
- **SOXL:**
  - Total assets $22.43B, liabilities $2.99B, **net assets $19.44B**.
  - Holdings by category: equities ~$13.40B, short-term investments ~$10.79B, swap mark-to-market −$4.03B.
  - Nine total-return swaps on the ICE Semiconductor Index, total notional **$44.93B**: JPMorgan $9.56B, BofA $9.04B, Citibank $7.42B, Barclays $6.72B, BNP Paribas $3.67B, Goldman Sachs $3.59B, UBS $2.97B, Nomura $1.71B, Société Générale $0.26B.
  - Source: [SOXL N-PORT (EDGAR)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404435/primary_doc.xml)
- **SOXS:**
  - Total assets $1.80B, **net assets $1.61B**.
  - Eight short swaps, total notional −$4.84B; the largest counterparty is Goldman Sachs ($2.21B).
  - Source: [SOXS N-PORT (EDGAR)](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404519/primary_doc.xml)
- **Swap financing terms (both reset daily):**
  - SOXL *pays* "1 month Sofr + spread"; the reported `floatingRtSpread` values per counterparty are 4.18 to 10.65 (notional-weighted 8.67).
  - SOXS *receives* "1 month Sofr + spread", with values 3.80 to 7.65 (weighted 5.92).
  - Sources: [SOXL N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404435/primary_doc.xml); [SOXS N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404519/primary_doc.xml)
- **N-PORT NAV returns, May–July 2026:**

  | Month | SOXL | SOXS |
  |---|---|---|
  | May 2026 | +75.9% | −52.3% |
  | June 2026 | +19.5% | −48.5% |
  | July 2026 | −57.3% | +67.6% |

  These match the local closing-price monthly returns (SOXL +76.7%, +18.9%, −57.0%) — [N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404435/primary_doc.xml); [SOXL.parquet](../../data/behavior/daily_adj/SOXL.parquet) *(local)*
- **Superseded estimates:** aggregator AUM figures for SOXL ranged from $12B to $28B — [prior notes](../SOXL%20and%20SOXS%20intraday%20behavior/mechanics_and_external_data.md). The N-PORT figure above is the primary number.

**Volume (local computation, Polygon daily bars, through Sep 25, 2026)**

| Window | SOXL avg daily volume | SOXS avg daily volume |
|---|---|---|
| Last 63 sessions | 63.6M shares (~$8.69B) | 61.6M shares (~$2.82B) |
| 2026 YTD | 72.2M shares (~$7.93B) | 35.0M shares (~$2.43B) |
| Since Jul 15, 2026 split | 65.3M shares | 60.5M shares |

Sources: [SOXL.parquet](../../data/behavior/daily_adj/SOXL.parquet); [SOXS.parquet](../../data/behavior/daily_adj/SOXS.parquet). Dollar values use the daily VWAP; SOXS share counts are split-adjusted to the current basis.

**Spreads (prior notes; NBBO analysis of 7 sample days since Jul 15, 2026)**
- **SOXL quoted spread:** time-weighted mean 5.06¢ = 3.66 bps, at one tick only 4.9% of RTH time. It narrows from ~11.6¢ in the first five minutes to ~2.1¢ in the last five.
- **SOXS quoted spread:** mean 1.18¢ = 3.16 bps, at one tick 86.8% of RTH time.
- Source for both: [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv); [microstructure notes](../SOXL%20and%20SOXS%20intraday%20behavior/microstructure_and_liquidity.md)
- **Mean half-spread by time of day:**

  | Bucket | SOXL | SOXS |
  |---|---|---|
  | RTH average | 1.83 bps | 1.58 bps |
  | 09:30–10:00 | 3.04 bps | 2.22 bps |
  | 15:30–16:00 | 1.01 bps | 1.39 bps |

  Source: [quoted_spread_by_bucket.csv](../../analysis/microstructure/output/quoted_spread_by_bucket.csv)
- **Effective (dollar-weighted) spread:** SOXL 1.89 bps (61% of quoted), SOXS 2.32 bps (78% of quoted) — [effective_spread.csv](../../analysis/microstructure/output/effective_spread.csv)
- **Full sessions, Sep 21–25, 2026:** SOXL RTH quoted 2.16–3.93 bps; SOXS 2.87–3.32 bps — [microstructure notes](../SOXL%20and%20SOXS%20intraday%20behavior/microstructure_and_liquidity.md)
- **Stress days:** on 2026-06-05 and 06-09, SOXL's spread widened to 24–26¢ (11.6–13.7 bps), 4–5× the normal median — [microstructure notes](../SOXL%20and%20SOXS%20intraday%20behavior/microstructure_and_liquidity.md)

### Inferences
- **Cost per switch.** One SOXL→SOXS switch is a SOXL sale plus a SOXS purchase.
  - Crossing the quoted spread at the RTH average costs about 1.83 + 1.58 ≈ **3.4 bps per switch**, roughly 5 bps in the first half hour.
  - At typical effective-spread fills, the cost is ≈ (1.89 + 2.32)/2 ≈ **2.1 bps per switch**.
  - At 150 switches a year (3 a week), spread costs alone are roughly 3–5% of the traded capital per year. Opening trades roughly double this, and stress days multiply it by 4–5×. *(Arithmetic; ignores regulatory fees and commissions.)*
- **Expense ratios hardly matter intraday:** 0.75–1.00% a year is ~0.3–0.4 bp per day. They are relevant only to overnight holders.
- **Overnight financing may be large for SOXL holders.** If the N-PORT spread field is in percentage points (likely, but not stated), SOXL pays roughly SOFR + 8.7% on swap notional of about 2.3× NAV, while SOXS receives SOFR plus a spread.
  - This fits the observed widening of SOXL's daily shortfall to −9.6 bp/day since May 2026 (§1).
  - An overnight SOXL holder therefore pays a carry cost on the order of 20%+ a year, accrued daily. An intraday-only trader largely avoids it.
- **Order size is not a constraint.** Retail orders are negligible against $2.8–8.7B of daily volume. The binding costs are spread and tick, not market impact.

### Gaps
- The units of N-PORT `floatingRtSpread` are not stated. The 1-month SOFR level for July 2026 was not retrieved. The implied financing cost therefore needs confirmation, for example from the N-CSR swap schedule.
- Direxion's daily NAV, premium/discount and official AUM pages (direxion.com) were blocked.
- 2026 SEC Section 31 fee and FINRA TAF rates on sales were not retrieved; search budget exhausted.

---

## 4. Trading halts, LULD treatment of leveraged ETPs, stop-order slippage in fast markets, extended-hours and overnight (24-hour) trading in 2026

### Takeaway
Under the LULD Plan, SOXL and SOXS are Tier 2 leveraged ETPs. Their price bands are the Tier 2 percentage times 3, i.e. **30% for prices above $3**. If the price stays at a band limit for 15 seconds, a 5-minute trading pause follows. Pauses of the funds themselves are rare, but fast markets can trigger them. On Aug 24, 2015 there were 1,278 LULD halts, 83% of them in ETPs and mostly in the first 45 minutes, and post-halt reopening auctions were dominated by market orders, which is the order type a triggered stop becomes. **Exchange overnight sessions (9 pm–4 am ET) are scheduled to begin Dec 6, 2026.** The SEC approved temporary overnight bands on Aug 5, 2026: 20% × leverage, i.e. **60% for 3× ETPs**. Until then, overnight SOXL trading happens on ATSs; Blue Ocean suspended SOXL from about Aug 31 to Sep 10, 2026.

### Cited Findings
**LULD parameters and pauses**
- **Tier 2 bands:** the plan's Appendix A sets Tier 2 percentage parameters of "10% … Reference Price of more than $3.00; 20% … $0.75 and up to and including $3.00; and the lesser of $0.15 or 75% … less than $0.75". "The Percentage Parameter for a Tier 2 NMS Stock that is a leveraged ETP is the applicable Percentage Parameter … multiplied by the leverage ratio of such product." The SEC *disapproved* Amendment 23, which would have moved all ETPs except single-stock ETPs into Tier 1, so the existing structure stands. — [SEC Release 34-101036 (Sep 16, 2024)](https://www.sec.gov/files/rules/other/2024/34-101036.pdf)
- **Tier assignment:** "Leveraged ETPs were excluded from eligibility to be included as LULD Tier 1 ETPs" — [Cboe LULD FAQ](https://www.cboe.com/document/tech-spec/document/technical-specifications/cboe-limit-updown-faq) *(prior notes)*
- **Pause trigger:** if a stock does not leave a Limit State within 15 seconds, the primary listing exchange declares a five-minute trading pause on all venues — [FINRA: Guardrails for Market Volatility](https://www.finra.org/investors/insights/guardrails-market-volatility) *(prior notes)*
- **Opening and closing periods:** in the original plan, band percentages doubled from 9:30 to 9:45 and from 3:35 to 4:00. The SEC gave the example that a Tier 1 triple-leveraged ETP's band in 9:30–9:45 "would have been 30%, rather than the 10%" for a non-leveraged Tier 1 ETP. — [SEC staff Research Note, Equity Market Volatility on Aug 24, 2015 (Dec 2015)](https://www.sec.gov/marketstructure/research/equity_market_volatility.pdf)
- **Amendment 18** (effective about Feb 24, 2020) removed closing-period doubling for Tier 2 stocks priced above $3 — [prior notes; CTA LULD Amendment 18 notice](https://www.ctaplan.com/publicdocs/ctaplan/notifications/trader-update/CQS_CTS_LULD_Amendment_18_Notification_Update.pdf)
- **Fast-market evidence, Aug 24, 2015:**
  - "1,278 LULD halts were triggered in 471 securities. The halts were concentrated in ETPs (83%)… most of the halts (87%) triggered in the first 45 minutes."
  - In NYSE Arca reopening auctions with sell imbalances, "94% of the total imbalances resulted from market orders."
  - "Following LULD halts … 4,078 trades totaling $34.6 million … were executed at prices outside of the LULD bands that were disseminated after the halts."
  - Short sale restrictions were triggered in more than 2,000 securities.
  - Source: [SEC Research Note (Dec 2015)](https://www.sec.gov/marketstructure/research/equity_market_volatility.pdf)
- **Fund-level halt risk:** "an exchange or market may also halt the trading of the Fund's shares, limiting an investor's ability to buy or sell Fund shares on that exchange or market" — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)
- **Observed halts:** no documented SOXL/SOXS LULD pause was found — [prior notes](../SOXL%20and%20SOXS%20intraday%20behavior/mechanics_and_external_data.md)

**Overnight / 24-hour trading**
- **LULD Amendment 27 — overnight bands, approved Aug 5, 2026:**
  - It adds "Overnight Protections" for "Overnight Protected Hours" (9:00 pm ET Sunday–Thursday to 4:00 am ET the next day), as Phase 1 interim measures.
  - Bands sit 20% below the lower and 20% above the greater of two reference prices: (i) the listing market's closing price and (ii) the consolidated last round-lot sale as of 7:45 pm ET.
  - "The Overnight Percentage Parameter for a leveraged ETP will be 20%, multiplied by the ETP's leverage ratio." Minimum band thresholds ($1.00 if the closing price is under $1; $3.00 otherwise) are also multiplied by the leverage ratio.
  - Bands are disseminated before 9:00 pm. The 20% figure was chosen "to align with the 20% static band protections currently employed by ATSs."
  - "Overnight Protections are expected to commence on December 6, 2026."
  - Source: [SEC Release 34-106042 (Aug 5, 2026)](https://www.sec.gov/files/rules/sro/nms/2026/34-106042.pdf)
- **Exchange sessions:** Nasdaq's overnight session runs 9 pm–4 am ET, with a target launch of Sunday, Dec 6, 2026, subject to SIP readiness. As of early October 2026 no delay had been reported. — [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/nasdaq-plans-nearly-23-hour-210330984.html); [Jones Day (Sept 2026)](https://www.jonesday.com/en/insights/2026/09/nyse-and-nasdaq-move-to-23hour-trading-day-overnight-session-is-an-evolution-but-not-yet-a-revolution) *(search snippets)*
- NYSE Arca's 22-hour schedule (1:30 am–11:30 pm ET Mon–Thu) and 24X's Dec 6, 2026 target (with a fallback to Jan 24, 2027) — [Jones Day](https://www.jonesday.com/en/insights/2026/09/nyse-and-nasdaq-move-to-23hour-trading-day-overnight-session-is-an-evolution-but-not-yet-a-revolution); [SEC exemptive order 34-106061](https://www.sec.gov/files/rules/exorders/2026/34-106061.pdf) *(prior notes)*
- **Current ATS overnight trading:** Blue Ocean ATS trades 8 pm–4 am ET Sunday–Thursday.
  - Around Aug 31, 2026 it suspended 18 securities, mostly leveraged or inverse products including SOXL, under the Reg ATS fair-access threshold (5% of volume in 4 of the preceding 6 months).
  - It resumed them on Sep 10, 2026.
  - Sources: [The Investor (Korea Herald)](https://www.theinvestor.co.kr/article/10860560); [Blue Ocean service status](https://blueocean-tech.io/blue-ocean-ats-service-status/) *(prior notes)*
- **Broker overnight offerings:** Robinhood's 24 Hour Market covers about 922 stocks and ETFs, Sunday 8 pm to Friday 8 pm ET, via ATSs; Schwab offers 1,100+ securities 24/5 — [Robinhood support](https://robinhood.com/us/en/support/articles/24hour-market); [Schwab press release (2025)](https://pressroom.aboutschwab.com/press-releases/press-release/2025/Schwab-Makes-Expanded-24-Hour-Trading-Available-to-All-Clients/default.aspx) *(prior notes)*
- **The "day" stays 4 pm to 4 pm:** the funds' objective runs "from the close of the market on a given trading day until the close of the market on the subsequent trading day" — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)

### Inferences
- **What it takes to pause SOXL/SOXS.** The band is 30% around a ~5-minute average reference price, so a pause needs roughly a 10% index move within minutes, or about 20% in 9:30–9:45 if opening doubling still applies (60% band). The funds' own pauses are therefore rare. More likely disruptions are halts in large constituents such as NVDA, market-wide circuit breakers, or SIP/venue outages, during which SOXL/SOXS keep trading off stale or uncertain index inputs.
- **Stop orders.**
  - A triggered stop becomes a market order. For a 3× fund, a 1% index gap is a ~3% price gap, and the fill comes at the next available prices, often in the widest spreads of the day: the first 30 minutes, or 4–5× normal on stress days (§3).
  - Stops do not protect against overnight gaps; they trigger at the open.
  - A stop-limit protects the price but may not fill.
  - The 2015 evidence shows halts cluster in the first 45 minutes and that post-halt auctions are dominated by market orders.
- **Overnight bands give little protection for 3× ETPs.** At 60%, the planned overnight bands allow prints up to 60% away from reference. Overnight trading has no live index (no ICESEMI calculation) and fragmented liquidity, and the Blue Ocean suspension shows ATS availability can disappear for days.
- **Interim (until Dec 6, 2026):** ATS venues are the only overnight route and broker lists vary. After Dec 6, exchange sessions will exist, but closing NAV and rebalancing remain at 4 pm. Overnight prints will price off the prior NAV plus proxies such as futures and Asian semiconductors.

### Gaps
- It was not confirmed from the current plan text whether 9:30–9:45 doubling still applies to Tier 2 leveraged ETPs in 2026, giving a 60% band (luldplan.com blocked).
- No list of SOXL/SOXS-specific LULD pauses was found (NYSE halt history blocked).
- It was not confirmed whether SOXL/SOXS are eligible on Robinhood's, Schwab's, IBKR's or Webull's overnight lists, or how each broker treats stop orders in extended and overnight hours. Broker sites were blocked and the search budget was exhausted.
- No primary SEC/FINRA source specifically quantifying stop-order slippage was retrieved; the Dec 2015 SEC note does not mention stops (zero hits for "stop").

---

## 5. Pattern day trader (PDT) rule status in 2026, and the current rules for cash accounts

### Takeaway
**The PDT rule has been replaced.**
- FINRA filed SR-FINRA-2025-017 on Dec 29, 2025.
- The SEC approved it, as modified by Amendment No. 1, on **April 14, 2026** (Release 34-105226).
- FINRA Regulatory Notice 26-10 (Apr 20, 2026) set an **effective date of June 4, 2026**, with an **optional phase-in for firms until Oct 20, 2027**.

The rule removes the "pattern day trader" designation, the $25,000 minimum equity and "day-trading buying power". In their place, firms must determine each margin account's "intraday margin deficit". Robinhood and Webull switched on June 4, 2026 and Schwab stopped counting day trades on June 8, 2026, but other brokers may legally keep the old regime until Oct 2027. Cash accounts were never subject to PDT. They remain governed by Reg T payment rules on a T+1 settlement cycle (compliance date May 28, 2024).

### Cited Findings
**Timeline**
- FINRA filed on Dec 29, 2025. The notice was published at 91 FR 1580 on Jan 14, 2026, and comments closed Feb 4, 2026. The SEC extended its deadline to Apr 14, 2026, and FINRA responded to comments on Mar 18, 2026. Amendment No. 1 was filed Apr 2, 2026. The SEC granted accelerated approval on **April 14, 2026**. — [SEC Release 34-105226 (approval order)](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf); [SEC Release 34-104572 (notice of filing, Jan 9, 2026)](https://www.sec.gov/files/rules/sro/finra/2026/34-104572.pdf)
- Amendment No. 1: "FINRA would issue a Regulatory Notice announcing an effective date of 45 days from the publication of that Regulatory Notice … members that need more time … are permitted to phase-in implementation over a period of 18 months following the publication of the Regulatory Notice." The original filing had proposed a 12-month interim period. — [SEC 34-105226](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf)
- FINRA Regulatory Notice 26-10 (published Apr 20, 2026): "The effective date of the amendments is June 4, 2026, 45 days from publication of this Notice. Members that need more time … phase in their implementation over a period of 18 months, until October 20, 2027." — [FINRA RN 26-10](https://www.finra.org/rules-guidance/notices/26-10); [PDF](https://www.finra.org/sites/default/files/2026-04/Regulatory-Notice-26-10.pdf); [FINRA weekly update, Apr 15, 2026](https://www.finra.org/compliance-tools/weekly-archive/04152026) *(search snippets; finra.org blocked)*
- FINRA now publishes separate "Interpretations of Rule 4210 (valid through June 3, 2026)" and "(valid from June 4, 2026)" — [FINRA interps valid from June 4, 2026](https://www.finra.org/rules-guidance/guidance/interps-4210-202606) *(search snippet)*

**What was removed (old rule, as described by the SEC)**
- A pattern day trader was "any customer who executes four or more day trades within five business days". There was an exception if day trades were 6% or less of total trades in the period.
- PDTs needed $25,000 minimum equity, deposited before further day trading and "maintained … at all times".
- Day-trading buying power was prior-close equity minus the maintenance requirement, "multiplied by four for equity securities".
- An unmet call left the account cash-available-only for 90 days, and deposits had a 2-business-day withdrawal hold.
- Source: [SEC 34-105226](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf)

**What replaced it (new Rule 4210(d)(2) and definitions (a)(17)–(a)(19))**
- Each firm must determine the "intraday margin deficit" for each customer margin account "other than a good faith account or a portfolio margin account", for each day with an "IML-reducing transaction".
- The "intraday margin level" (IML) is the cash the customer could withdraw while still meeting maintenance margin, or the deposit needed to meet it.
- Firms may "use real-time monitoring to block trades that would create or increase customer intraday margin deficits", or they may compute deficits at the end of the day.
- Deficits must be "satisfied as promptly as possible, by deposits … or liquidations". If a deficit is not met within five business days, the firm takes a net-capital deduction for up to 10 business days. A customer who "makes a practice of failing to satisfy intraday margin deficits promptly" is frozen from new credit "until the deficit is satisfied (or 90 days elapse)".
- "The proposed rule change makes no change to the regular maintenance margin requirements."
- The $2,000 minimum equity requirement in Rule 4210(b) is cited as part of existing requirements; only the PDT references in paragraph (b) are deleted.
- FINRA's rationale: zero-commission trading removed a main reason for the old rule, and the new rule also addresses intraday risk from 0DTE options.
- Source: [SEC 34-105226](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf)

**Broker implementation** *(search snippets; broker sites blocked)*
- Robinhood: from June 4, 2026, "no more day trade restrictions or day trade calls for Robinhood margin account holders" — [Robinhood support: Day trading](https://robinhood.com/us/en/support/articles/day-trading/)
- Webull implemented on June 4, 2026 — [Webull blog](https://www.webull.com/blog/321-Understanding-the-PDT-Rule-What-It-Was-Why-It-Changed-and-What-It-Means-Now)
- Schwab: "As of June 8, Schwab no longer counts day trades in margin accounts" — [Schwab: Updates Day Trading and Margin Rules](https://www.schwab.com/learn/story/schwab-changes-rules-around-day-trading)
- Coverage of Robinhood, Webull and IBKR as beneficiaries — [Benzinga (Jun 4, 2026)](https://www.benzinga.com/trading-ideas/movers/26/06/53007723/robinhood-webull-interactive-brokers-set-to-gain-as-pdt-rule-dies-today)

**Cash accounts**
- FINRA's impact analysis notes its CAT-based count "include[s] cash accounts that are not affected by the PDT requirements" — [SEC 34-104572, n.51](https://www.sec.gov/files/rules/sro/finra/2026/34-104572.pdf)
- The new intraday-margin paragraph applies only to margin accounts, and excludes good-faith and portfolio-margin accounts — [SEC 34-105226](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf)
- T+1 settlement: "compliance date of May 28, 2024, for the amendments to Exchange Act Rule 15c6-1(a)" — [SEC Release 34-96930 (T+1 adopting release)](https://www.sec.gov/files/rules/final/2023/34-96930.pdf)

### Inferences
- **Margin-account switcher under the new regime.** Several SOXL↔SOXS round trips a week no longer trigger any designation or a $25,000 floor. Buying power is limited instead by maintenance requirements at each IML-reducing transaction. For 3× ETFs the requirement is 75% long, so maximum exposure is about 1.33× equity (§6).
  - A switch made as sell-then-buy does not raise exposure.
  - Buying the new fund *before* selling the old one temporarily doubles exposure and can create an intraday deficit. Real-time brokers would block such an order.
- **Check your broker's status.** Brokers may legally keep enforcing PDT until Oct 20, 2027.
- **Cash-account switcher.** This rests on standard Reg T cash-account mechanics, which were not fetched this session ([12 CFR 220.8](https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-220/section-220.8)).
  - Under T+1, sale proceeds settle the next business day.
  - Selling SOXL and immediately buying SOXS with the unsettled proceeds is allowed.
  - Selling that SOXS the *same day*, before the SOXL proceeds settle, is what brokers call a "good-faith violation".
  - Buying without settled funds and selling before paying is "free-riding", which carries a 90-day settled-cash restriction under Reg T.
  - In practice, a cash account can recycle a given dollar into one completed SOXL→SOXS→sell sequence per settlement cycle. The FINRA change does nothing for cash accounts.

### Gaps
- Regulatory Notice 26-10's full text could not be read (finra.org blocked). The June 4, 2026 and Oct 20, 2027 dates rest on FINRA-domain search snippets, and are consistent with the SEC order's 45-day/18-month mechanics.
- Implementation dates for Fidelity, E*TRADE/Morgan Stanley, IBKR, tastytrade and others were not confirmed.
- Reg T free-riding text and broker good-faith-violation policies (e.g., restrictions after a number of violations in 12 months) could not be fetched (ecfr.gov, federalreserve.gov and broker sites blocked).

---

## 6. Margin requirements for 3× leveraged ETFs (FINRA Rule 4210 multiples, broker house rules) and shorting SOXL vs buying SOXS

### Takeaway
FINRA Rule 4210 scales initial and maintenance margin on leveraged ETPs by their leverage: for 3× funds, **75% of market value for long positions and 90% for short positions**. Long requirements are capped at 100%; short requirements are not. Shorting SOXL instead of buying SOXS adds three costs: borrow fees (~2.2–2.6% a year in mid/late 2026), a locate, and exposure to the Reg SHO Rule 201 short-sale price test. A 10% drop in SOXL triggers that test, and SOXL's intraday low was at least 10% below the prior close on **23% of 2026 sessions**. Buying SOXS needs no borrow, is outside Rule 201, caps the loss at the investment and carries the 75% long requirement.

### Cited Findings
- **FINRA multiples:** "The initial and maintenance margin requirement for leveraged exchange trade products (ETPs) carried long or short in a customer's account is increased by an amount commensurate with its leverage, subject to a cap of 100% of the current market value on a long position (but without a cap on the margin on a short position)." Requirements by leverage:

  | ETP leverage | Long | Short |
  |---|---|---|
  | 1.5× | 37.5% | 45% |
  | 2× | 50% | 60% |
  | **3×** | **75%** | **90%** |
  | 4× | 100% | 120% |
  | 5× | 100% | 150% |

  Sources: [FINRA Interpretations of Rule 4210](https://www.finra.org/rules-guidance/guidance/interps-4210); [FINRA Regulatory Notice 09-53](https://www.finra.org/rules-guidance/notices/09-53); [FINRA notice PDF "Non-Traditional ETFs Increased Margin Requirements for Leveraged"](https://www.finra.org/sites/default/files/NoticeDocument/p119906.pdf) *(search snippets; finra.org blocked)*
- **Unchanged by the 2026 rewrite:** the intraday-margin change "makes no change to the regular maintenance margin requirements", so the leveraged-ETP multiples still apply — [SEC 34-105226](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf)
- **SOXL borrow fees and short interest** *(search snippets)*:
  - Borrow fee 2.17% a year as of Jun 17, 2026.
  - About 4,000,000 shares available at a 2.60% fee as of Sep 25, 2026. One source shows Interactive Brokers with 2,500,000 shares available (date unclear).
  - Short interest of 12,640,313 shares on May 29, 2026, or 0.18 days to cover.
  - Sources: [ChartExchange SOXL borrow fee](https://chartexchange.com/symbol/nyse-soxl/borrow-fee/); [Fintel SOXL](https://fintel.io/ss/us/soxl); [IBKR borrow fee documentation](https://www.ibkrguides.com/reportingreference/reportguide/borrowfeedetails.htm)
- **Rule 201 (short-sale price test):** trading centers must prevent "the execution or display of a short sale order of a covered security at a price that is less than or equal to the current national best bid if the price of that covered security decreases by 10% or more from the covered security's closing price … on the prior day". The restriction applies "for the remainder of the day and the following day". — [SEC Release 34-61595 (Rule 201 adopting release, 2010)](https://www.sec.gov/files/rules/final/2010/34-61595.pdf)
- **SEC on inverse ETFs as synthetic shorts:** the SEC acknowledged that short exposure obtained "through … inverse leveraged exchange traded funds" (a "synthetic short sale") is not restricted by Rule 201 and "may undermine our goals for adopting short sale price test restrictions" — [SEC 34-61595](https://www.sec.gov/files/rules/final/2010/34-61595.pdf)
- **How Rule 201 works in practice:** "When SSRs are triggered, short sale orders in that security generally are subject to a price test that requires the orders to be executed at prices greater than the national best bid" — [SEC Research Note (Dec 2015)](https://www.sec.gov/marketstructure/research/equity_market_volatility.pdf)
- **Rule 201 trigger frequency** (local computation): sessions on which the intraday low was at least 10% below the prior close.

  | Year | SOXL | SOXS |
  |---|---|---|
  | 2022 | 51/251 (20.3%) | 44 (17.5%) |
  | 2023 | 7/250 (2.8%) | 19 (7.6%) |
  | 2024 | 25/252 (9.9%) | 21 (8.3%) |
  | 2025 | 32/250 (12.8%) | 22 (8.8%) |
  | 2026 YTD | 43/184 (23.4%) | 39 (21.2%) |

  Source: [SOXL.parquet, SOXS.parquet](../../data/behavior/daily_adj/SOXL.parquet). This is approximate: it uses split-adjusted lows and closes, not the listing market's official close.

### Inferences
- **Practical buying power.** At 75%, a $10,000 margin account can hold about $13,300 of SOXL or SOXS. A $10,000 short SOXL position needs about $9,000 of equity at 90%. Shorting SOXL is therefore no more capital-efficient than buying SOXS, and it adds borrow, recall and Rule 201 risk.
  - Because Rule 201 bites on roughly 1 in 4 sessions in 2026, and stays on for the next day, the bear leg would become a passive (above-bid) short exactly in the fast down-moves a switcher wants to catch. SOXS has no such restriction.
- **Payoff differences are second-order intraday.** A short SOXL position's dollar exposure grows as SOXL rises (adverse convexity), while a long SOXS position shrinks as it loses. For small moves the two are equivalent.
- **Over multiple days the funds' decay changes the comparison.** A short SOXL position benefits from SOXL's decay, while a long SOXS position suffers SOXS's larger decay (§1). Short SOXL still carries unlimited loss and recall risk.
- **Borrow cost.** At ~2.6% a year, borrow is ~1 bp per day held. Whether it is charged on intraday-only shorts depends on the broker.
- **Broker house requirements** for leveraged ETFs are often stricter than FINRA's minimums. Check them for SOXL/SOXS in 2026; they were not verified here.

### Gaps
- Broker house margin for SOXL/SOXS (Schwab, Fidelity, IBKR, Robinhood, Webull) in 2026 was not verified: sites blocked and search budget exhausted.
- SOXS borrow availability and fee were not found.
- FINRA 4210 rule text (the leveraged-ETP paragraph) and Regulatory Notice 09-53's effective date were not read directly; the table above rests on FINRA-domain search snippets.

---

## 7. Tax: wash-sale rule (§1091) for repeated SOXL trades and for SOXL vs SOXS; short-term gains; trader tax status and the §475(f) mark-to-market election; Section 1256

### Takeaway
- **Gains and losses.** Every intraday round trip is a short-term capital gain or loss, taxed at ordinary-income rates (up to 37%) plus the 3.8% NIIT where it applies.
- **Repeated trades in the same fund.** Repeating SOXL trades (or SOXS trades) within 30 days creates wash sales. These defer losses rather than eliminating them, unless the replacement shares are bought in an IRA. The rule bites at year-end.
- **SOXL vs SOXS.** No IRS guidance treats SOXL and SOXS as "substantially identical". Their opposite economic exposure makes that reading unlikely, but holding both at once could raise straddle (§1092) issues.
- **§475(f) election.** A trader who qualifies for trader tax status can elect mark-to-market. The election removes wash-sale and $3,000-loss-limit constraints for trading securities. It must be made by the original due date of the prior year's return: April 15, 2026 for tax year 2026, so it is now too late for 2026 for an existing taxpayer.
- **No 60/40 treatment.** ETF shares are not Section 1256 contracts.

### Cited Findings
- **Wash-sale window:** the rule stops investors from "selling at a loss, buying the same (or 'substantially identical') investment back within a 61-day window and claiming the tax benefit". "There are no clear guidelines on what constitutes a substantially identical security." — [Fidelity: Tax Rules for ETF Losses](https://www.fidelity.com/learning-center/investment-products/etf/tax-rules-for-losses-etfs); [Fidelity: Wash-Sale Rules](https://www.fidelity.com/learning-center/personal-finance/wash-sales-rules-tax); [CNBC (Nov 15, 2024)](https://www.cnbc.com/2024/11/15/tax-loss-harvesting-etfs.html) *(search snippets)*
- **SOXL vs SOXS:** searches found **no IRS ruling or practitioner consensus document specific to SOXL vs SOXS**. Secondary sources note the two "track the same benchmark", with "the only fundamental difference being directional". — [Bybit Wiki: SOXS explained](https://www.bybit.com/en/wiki/article/soxs-etf-semiconductor-bear-3x-fund/); [Bogleheads thread "Wash Sale Substantially Identical?"](https://www.bogleheads.org/forum/viewtopic.php?t=443201) *(search snippets)*
- **Statutory rules** *[statute — not fetched; standard statutory content, verify]*:
  - **Wash sale, §1091:** a loss is disallowed if substantially identical stock is acquired within the period from 30 days before to 30 days after the sale. The disallowed loss is added to the basis of the replacement shares (§1091(d)), and their holding period includes that of the sold shares (§1223(3)). — [26 U.S.C. §1091](https://www.law.cornell.edu/uscode/text/26/1091); [IRS Publication 550](https://www.irs.gov/publications/p550)
  - **IRA replacement purchases:** a repurchase inside an IRA permanently disallows the loss with no basis step-up. — [Rev. Rul. 2008-5](https://www.irs.gov/pub/irs-irbs/irb08-03.pdf)
  - **Capital loss limit:** net capital losses deduct against ordinary income only up to $3,000 a year ($1,500 married filing separately), with the excess carried forward. — [26 U.S.C. §1211](https://www.law.cornell.edu/uscode/text/26/1211)
  - **NIIT:** 3.8% on net investment income above $200,000 (single) or $250,000 (MFJ) of modified AGI; these thresholds are not indexed. — [26 U.S.C. §1411](https://www.law.cornell.edu/uscode/text/26/1411)
  - **§475(f) for traders in securities:**
    - Gains and losses on securities held in the trading business are marked to market and treated as ordinary, and §1091 does not apply to them. — [26 U.S.C. §475](https://www.law.cornell.edu/uscode/text/26/475)
    - An existing taxpayer must file the election by the unextended due date of the return for the year *before* the election year, then file Form 3115 with the election-year return. — [Rev. Proc. 99-17](https://www.irs.gov/pub/irs-irbs/irb99-07.pdf)
  - **§1256:** "section 1256 contracts" are regulated futures, foreign currency contracts, nonequity options, dealer equity options and dealer securities futures contracts. Exchange-traded fund shares are not on the list, so SOXL/SOXS share trades do not get 60/40 treatment. — [26 U.S.C. §1256](https://www.law.cornell.edu/uscode/text/26/1256)
- **Fund-level §1256 does not pass through.** Direxion notes that some of the *fund's own* derivatives may be §1256 contracts ("Sixty percent of any net gain or loss …"). Investors receive ordinary or capital-gain distributions, not 60/40 treatment on their share trades. — [Direxion statutory prospectus/SAI, 485BPOS Feb 26, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526075941/d798177d485bpos.htm)
- **Distributions:** "The Fund will generally need to distribute net short-term capital gain … it could need to make larger and/or more frequent distributions than traditional ETFs. A shareholder that holds shares of the Fund when a Fund pays a distribution will receive the distribution which reflects net investment income and net capital gains the Fund earned prior to the shareholder's holding period." — [485BPOS, Feb 26, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526075941/d798177d485bpos.htm)
- **Straddle wash-sale regulations:** the regulations under §1092 "provide certain 'wash sale' rules, which apply to transactions where a position is sold at a loss and a new offsetting position is acquired within a prescribed period". Direxion describes this at the fund level. — [485BPOS, Feb 26, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526075941/d798177d485bpos.htm)
- **Corporate-action tax events:**
  - Reverse splits are not taxable except for the cash-out of fractional shares — [497, Feb 4, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526037667/d80567d497.htm)
  - Fund liquidation distributions "are taxable events" — [497, Mar 13, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526106262/d111775d497.htm)
- **Prospectus after-tax returns** "are calculated using the historically highest individual federal marginal income tax rates" — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)

### Inferences
- **Repeated SOXL (or SOXS) trades.** For a switcher, *SOXL→SOXL* (or SOXS→SOXS) re-entries within 30 days of a losing sale are wash sales, because these are identical securities. With several trades a week, almost every losing lot gets carried into a later lot.
  - Within a year the effect is mostly timing.
  - It becomes real at year-end: a December loss is pushed into the next year if the same fund is bought again by about Jan 30.
  - Buying replacement shares in an IRA destroys the loss.
  - Brokers' 1099-B wash-sale adjustments are generally limited to the same security (CUSIP) in the same account. Reconciling across accounts, a spouse's accounts and IRAs is the taxpayer's job. This last point is from Form 1099-B instructions, which were not fetched.
- **SOXL→SOXS flips.** Selling SOXL at a loss and buying SOXS (or the reverse) is, on the ordinary reading of "substantially identical", **not** a wash sale. The two funds move in opposite directions, so a loss on one is not offset by holding a near-equivalent position. There is no IRS confirmation, so conservative traders document their reasoning.
- **Holding both at once.** Holding SOXL and SOXS at the same time, for example legging into a switch, could create offsetting positions under the §1092 straddle rules. The consequences are loss deferral and holding-period effects. A strict sell-then-buy flipper avoids the overlap. Get professional advice.
- **Mark-to-market.**
  - Short-term gains are already taxed at ordinary rates, so a §475(f) election mainly helps with losses: ordinary losses with no $3,000 cap, no wash-sale tracking and simpler year-end accounting.
  - Its price is that gains and losses can never be long-term capital, and the election is sticky (revocation requires IRS consent).
  - Trader tax status is a facts-and-circumstances test from case law (substantial, regular and continuous trading aimed at short-term swings). "Several times a week" may or may not qualify.
- **Distributions.** A trader who is flat at every close is rarely a holder of record on a distribution date.

### Gaps
- irs.gov, law.cornell.edu and greentradertax.com were blocked and the search budget was exhausted. Statutory points are cited to the governing law but were **not re-verified this session**.
- The 2026 rate-bracket thresholds (Rev. Proc. 2025-32) were not verified.
- Green Trader Tax's trader-tax-status guidelines (holding-period, trade-count and days-per-week thresholds) were not retrieved.
- No IRS ruling, court case or Big-4 opinion addressing whether a 3× bull and a 3× bear fund on the same index are "substantially identical" was found.
- No 2025–2026 legislative change to §1091 or §475 was identified, but this could not be checked against current sources.

---

## 8. Fund-level risks: Direxion closure/liquidation risk, swaps and counterparties, prospectus warnings, and the 2026 regulatory environment for leveraged ETFs

### Takeaway
- **Closure risk is low but not zero.** SOXL ($19.4B) and SOXS ($1.6B) are among Direxion's largest funds. Between June 2025 and March 2026 Direxion announced closures of **15 small funds** for "inability to attract sufficient investment assets". SOXS's −85% in 2025 and its serial reverse splits show how quickly a bear fund shrinks.
- **Swap dependence.** Both funds get most of their exposure from total-return swaps with 8–9 bank counterparties. The prospectus warns that dealers may refuse to provide exposure in volatile markets.
- **New 3× funds are blocked; existing ones are grandfathered.** Rule 18f-4 effectively limits new leveraged funds to 2×, but exempts 3× funds that were operating on Oct 28, 2020, provided they do not change their index or increase leverage. In Dec 2025 SEC staff told Direxion it would not review 29 proposed 3× funds until they comply, and the press reported nine such letters to issuers in early 2026.
- **No rule targeting SOXL/SOXS.** No 2026 rule specifically targeting existing 3× index ETFs like SOXL and SOXS was found.

### Cited Findings
**Direxion fund closures, 2025–2026 (EDGAR supplements)**

| Announced | Funds closed | Closing date | Liquidation date | Source |
|---|---|---|---|---|
| Jun 27, 2025 | OOTO, CLDL (2 funds) | Jul 24, 2025 | Jul 30, 2025 | [497](https://www.sec.gov/Archives/edgar/data/1424958/000119312525151293/d949204d497.htm) |
| Oct 3, 2025 | WFH, EVAV, XXCH (3 funds) | Oct 23, 2025 | Oct 30, 2025 | [497](https://www.sec.gov/Archives/edgar/data/1424958/000119312525230306/d949346d497.htm) |
| Mar 13, 2026 | LMBO, REKT (2 funds) | Apr 10, 2026 | Apr 17, 2026 | [497](https://www.sec.gov/Archives/edgar/data/1424958/000119312526106267/d21665d497.htm) |
| Mar 13, 2026 | SHPD, LMTS, FRDD, FRDU, BOED, XOMZ, ELIS, BRKD (8 funds) | Apr 10, 2026 | Apr 17, 2026 | [497](https://www.sec.gov/Archives/edgar/data/1424958/000119312526106262/d111775d497.htm) |

- **Reason and mechanics:**
  - Rafferty told the Board each fund "could not conduct its business and operations in an economically efficient manner over the long term due to each Fund's inability to attract sufficient investment assets".
  - Between the closing and liquidation dates, "shareholders may only be able to sell their shares to certain broker-dealers and there is no assurance that there will be a market for a Fund's shares during this time period".
  - During that window the funds "should not be expected to provide investment exposure consistent with [their] investment objective".
  - Liquidation distributions "are taxable events".
  - Source: [497, Mar 13, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526106262/d111775d497.htm)

**Swaps, counterparties, rebalancing**
- **Prospectus counterparty warnings:**
  - "Because the Fund may enter into swap agreements with a limited number of counterparties, this increases the Fund's exposure to counterparty credit risk … there is a risk that no suitable counterparties will be willing to enter into, or continue to enter into, transactions with the Fund … The risk … may be heightened when there is significant volatility in the overall market or the reference asset."
  - The prospectus also lists Rebalancing Risk and Early Close/Trading Halt Risk.
  - Sources: [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- **Direxion's stated responses if instruments become thinly traded:** the fund may struggle to issue new creation units, its shares "could trade at a premium or discount … and/or the bid-ask spread … could widen", and the fund "may increase its transaction fee, utilize derivatives instruments that are less correlated to the Index, change its investme[nt objective]…" — [485BPOS, Feb 26, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526075941/d798177d485bpos.htm)
- **Counterparty concentration (Jul 31, 2026):**
  - SOXL has nine swap counterparties and $44.93B of notional, about 2.3× NAV. The largest exposures are JPMorgan ($9.56B), BofA ($9.04B), Citibank ($7.42B) and Barclays ($6.72B).
  - SOXS has eight counterparties and $4.84B of notional; Goldman Sachs alone is $2.21B.
  - Sources: [SOXL N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404435/primary_doc.xml); [SOXS N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404519/primary_doc.xml)
- **Prospectus loss warnings:** full loss of principal in a single day if the index moves more than 33% against the fund. Neither fund "is suitable for all investors". — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm); [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm)
- **Tax-status risk:** the funds' strategy may be limited by RIC qualification tests, and some investments' treatment "is unclear" — [SOXL 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078540/d50601d497k.htm)

**2026 regulatory environment**
- **Rule 18f-4 timeline:** adopted Oct 28, 2020, effective Feb 19, 2021, compliance date Aug 19, 2022 — [SEC Release IC-34084](https://www.sec.gov/files/rules/final/2020/ic-34084.pdf); [SEC press release 2020-269](https://www.sec.gov/newsroom/press-releases/2020-269)
- **The 200% limit:** the VaR limit "will effectively limit leveraged or inverse funds' targeted daily return to 200% of the return (or inverse of the return) of the fund's underlying index", with "an exception … for leveraged or inverse funds currently in operation that seek an investment return above 200%" — [SEC press release 2020-269](https://www.sec.gov/newsroom/press-releases/2020-269)
- **Exception text:** the exempt fund must "(i) As of October 28, 2020, … [be] in operation; has outstanding shares issued in one or more public offerings to investors; and discloses in its prospectus a leverage multiple or inverse multiple that exceeds 200% …; (ii) … not change the underlying market index or increase the level of leveraged or inverse market exposure …; and (iii) … disclose[] in its prospectus that it is not subject to the limit on fund leverage risk" — [SEC IC-34084](https://www.sec.gov/files/rules/final/2020/ic-34084.pdf)
- **Sales-practice rules never adopted:** "we are not adopting the proposed sales practices rules or the proposed exception from the VaR-based limit on leverage risk that was predicated on those rules" — [SEC IC-34084](https://www.sec.gov/files/rules/final/2020/ic-34084.pdf)
- **SEC staff letter to Direxion, Dec 2, 2025:**
  - "We write to express concern regarding the registration of exchange-traded funds that seek to provide more than 200% (2x) leveraged exposure to underlying indices or securities … We will not perform a substantive review of these filings … until the issues raised in this letter are addressed."
  - Each fund "must use the security or securities that it tracks … as the fund's designated reference portfolio".
  - The staff asked Direxion to "revise its objective and strategy to be consistent with rule 18f-4 … or withdraw its filings".
  - Appendix A lists 29 proposed 3× ETFs filed Oct 3 and Oct 10, 2025: AAPL, TSM, AMZN, GOOGL, META, MU, NFLX, NVDA, PLTR, TSLA, AMD, UNH, AVGO, BABA, BRKB, COIN, HOOD, INTC, MSFT, ORCL, Bitcoin, Energy, Ether, Gold Miners, Junior Gold Miners, MAG7+, Oil & Gas E&P, "Qs" and QQQE Bull 3X.
  - Source: [SEC staff letter (EDGAR UPLOAD, Dec 2, 2025)](https://www.sec.gov/Archives/edgar/data/1424958/000000000025011179/filename1.pdf)
- **Press coverage, early 2026:** the SEC sent nine warning letters to leveraged-ETF issuers, including Volatility Shares, ProShares, Direxion and GraniteShares, making clear "Rule 18f-4 does not permit funds to offer leverage above 200% once the correct 'designated reference portfolio' is applied" — [Advisor Perspectives (Mar 5, 2026)](https://www.advisorperspectives.com/articles/2026/03/05/sec-pushing-back-wave-high-leverage-etf-plans); [Barchart (Mar 4, 2026)](https://www.barchart.com/story/news/567339/the-sec-just-drew-a-line-in-the-sand-why-it-s-blocking-highly-leveraged-etfs); [etf.com "SEC Says No to 5x ETFs"](https://www.etf.com/sections/features/sec-says-no-5x-etfs) *(search snippets)*
- **[conflict: dates]** The Direxion letter on EDGAR is dated Dec 2, 2025, while the press described the letters in early March 2026. The press timing probably reflects when the letters became public; this was not verified. — [SEC staff letter](https://www.sec.gov/Archives/edgar/data/1424958/000000000025011179/filename1.pdf); [Advisor Perspectives](https://www.advisorperspectives.com/articles/2026/03/05/sec-pushing-back-wave-high-leverage-etf-plans)
- **[low reliability — unverified] Commodity-pool route:** a search summary says Volatility Shares later "secured the first clearance at the 3x tier" by structuring products as CFTC/NFA-supervised commodity pools outside the 1940 Act. The only result supporting this was a GitHub release page, which is not a credible source, and no news or SEC/CFTC source corroborated it. — [GitHub page (unreliable)](https://github.com/Ricosworks1/blockchain-payment-flow-analysis/releases/tag/comparative-analysis-sec-3x-leveraged-crypto-etf-approval-oct-2026); related coverage of the SEC pushback: [cryptorank (snippet)](https://cryptorank.io/news/feed/a4062-sec-pushes-back-on-3x-5x-etf-filings)
- **Single-stock product proliferation in Direxion's own filings (2025–2026):**
  - New single-stock tickers in Nov 2025: CONX, HODU, LINT, ORCU, ORCS — [497, Nov 14, 2025](https://www.sec.gov/Archives/edgar/data/1424958/000119312525282231/d201511d497.htm)
  - Feb 2026: ASMU, BABU, MRVU, SOFA — [497, Feb 6, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526040815/d63174d497.htm)
  - A "Direxion Daily SpaceX Bear 2X ETF" was renamed to ticker LOFD in July 2026 — [497, Jul 21, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526310566/d127224d497.htm)
  - Several 1× single-stock bear funds were reverse-split in 2026 — [497, Feb 26, 2026](https://www.sec.gov/Archives/edgar/data/1424958/000119312526076908/d100149d497.htm)
- **Market-structure items affecting 3× ETPs in 2026:**
  - LULD Amendment 23 (all ETPs except single-stock ETPs into Tier 1) was disapproved in Sep 2024 — [SEC 34-101036](https://www.sec.gov/files/rules/other/2024/34-101036.pdf)
  - The overnight LULD bands scale by leverage (approved Aug 5, 2026) — [SEC 34-106042](https://www.sec.gov/files/rules/sro/nms/2026/34-106042.pdf)
  - The half-penny tick is deferred to Nov 2027 — [SEC 34-105656](https://www.sec.gov/files/rules/exorders/2026/34-105656.pdf)
- **Name change:** effective Feb 27, 2026, Direxion replaced "Shares" with "ETF" in the fund names, e.g. "Direxion Daily Semiconductor Bear 3X ETF" — [SOXS 497K](https://www.sec.gov/Archives/edgar/data/1424958/000119312526078538/d48414d497k.htm). EDGAR's N-PORT series names still read "…3X Shares" — [SOXL N-PORT](https://www.sec.gov/Archives/edgar/data/1424958/000119312526404435/primary_doc.xml).

### Inferences
- **Regulatory risk to SOXL/SOXS is mainly about lost grandfathering.** Existing 3× funds keep operating under 18f-4's exception only if they keep the same index and leverage. A forced index change (for example, if ICE discontinued or materially changed the index) could put the 3× objective at risk. New 3× single-stock or sector products are blocked under the 1940 Act. This entrenches existing 3× index funds rather than threatening them.
- **Closure risk.**
  - SOXL is a flagship (~$19B) and very unlikely to close.
  - SOXS (~$1.6B) is far above the closed funds, which were tiny niche products, but its assets erode structurally in bull markets.
  - If a closure were announced, the historical pattern gives ~4 weeks' notice, a trading halt on the closing date, and a cash distribution that is a taxable sale.
- **Counterparty capacity.** Swap notional of ~$45B for SOXL, concentrated with a few dealers, means dealer appetite and financing spreads (§3) affect tracking and costs. In a volatility spike, Direxion may pull the rebalance earlier than the close (Intra-Day Investment Risk). Spreads and premiums or discounts can then widen exactly when an intraday switcher trades.
- **The 2021 index change and grandfathering.** SOXL/SOXS changed index on Aug 25, 2021. That was after the Oct 28, 2020 grandfather date but before the Aug 19, 2022 compliance date. How this squared with condition (ii) is not explained in the documents reviewed. The funds evidently continue to operate at 3×.

### Gaps
- It was not confirmed whether SOXL/SOXS's current prospectus contains the 18f-4 "not subject to the limit on fund leverage risk" disclosure; it was not found in the 497Ks or the Feb 26, 2026 485BPOS searched. How the Aug 2021 index change was treated under 18f-4(c)(5) was also not confirmed.
- The full set of nine SEC letters (early 2026) and any issuer responses were not retrieved; only Direxion's Dec 2, 2025 letter was found on EDGAR.
- No 2026 SEC or FINRA proposal specifically affecting existing 3× index ETFs (such as sales-practice or suitability rules for self-directed accounts) was found. finra.org was blocked and the search budget was exhausted, so this cannot be ruled out.
- No Direxion statement on SOXS's minimum viable asset size or on its counterparty limits was found.
