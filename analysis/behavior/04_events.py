"""Detect catalyst dates from price/volume reactions (official schedules were not reachable:
federalreserve.gov, bls.gov and fred.stlouisfed.org are blocked by the session's egress policy).

Methods (all labelled 'detected' in the output):
  * Earnings (NVDA, AVGO, AMD, MU; all report after the US close - assumption):
      after-hours (16:00-20:00 ET) volume from 1-hour bars / median after-hours volume of the prior
      20 sessions. Greedy selection of the highest ratio, excluding +/-45 calendar days around each
      pick, while ratio >= 4. The catalyst day for SOXL is the NEXT regular session.
      NVDA picks are cross-checked against 10-Q acceptance timestamps from /vX/reference/financials.
  * FOMC decision days: QQQ volume in 14:00-14:02 ET / mean per-minute volume 13:30-13:59.
      Greedy selection, +/-30 day exclusion, ratio >= 4.
  * Likely-CPI days: QQQ pre-market volume 08:30-08:32 ET / mean per-minute volume 08:00-08:29,
      restricted to day-of-month 10-15 (CPI is typically released in the second week of the month),
      at most one per month (the highest ratio), ratio >= 4. PPI / retail-sales days can be
      misclassified - see caveats.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import DATA, END, OUT, api_get, load_minute, save_csv, sessions, TZ


def greedy(score: pd.Series, excl_days: int, thresh: float) -> list[str]:
    s = score.dropna().sort_values(ascending=False)
    picked = []
    for d, v in s.items():
        if v < thresh:
            break
        dt = pd.Timestamp(d)
        if all(abs((dt - pd.Timestamp(p)).days) > excl_days for p in picked):
            picked.append(d)
    return sorted(picked)


def ah_ratio_hour(t: str, days: list, h0: int, h1: int) -> pd.Series:
    h = pd.read_parquet(DATA / "hour" / f"{t}.parquet")
    ts = pd.to_datetime(h.t, unit="ms", utc=True).dt.tz_convert(TZ)
    h["date"] = ts.dt.strftime("%Y-%m-%d")
    h["hour"] = ts.dt.hour
    ah = h[(h.hour >= h0) & (h.hour < h1)].groupby("date").v.sum().reindex(days)
    return ah / ah.shift(1).rolling(20, min_periods=10).median()


def earnings(sess: pd.DataFrame) -> pd.DataFrame:
    """After-hours volume spike in BOTH windows: score = min(AH 16-20h ratio, AH 17-20h ratio), each vs the
    median of the prior 20 sessions. Requiring the 17-20h window (conference-call hours) removes
    closing/rebalance prints reported just after 16:00; requiring 16-20h removes low-base noise.
    Greedy picks with +/-60-day exclusion (reports are ~3 months apart), score >= 4."""
    rows = []
    days = list(sess.index)
    names = ["NVDA", "AVGO", "AMD", "MU"]
    ra = pd.DataFrame({t: ah_ratio_hour(t, days, 16, 20) for t in names})
    rb = pd.DataFrame({t: ah_ratio_hour(t, days, 17, 20) for t in names})
    for t in names:
        others = rb[[x for x in names if x != t]].median(axis=1)
        score = np.minimum(ra[t], rb[t])
        score = score[score.index >= "2021-12-01"]
        for d in greedy(score, 60, 4.0):
            i = days.index(d)
            nxt = days[i + 1] if i + 1 < len(days) else None
            rows.append({"ticker": t, "report_date": d, "weekday": pd.Timestamp(d).day_name(),
                         "ah_ratio_16_20": float(ra.loc[d, t]), "ah_ratio_17_20": float(rb.loc[d, t]),
                         "peer_median_ratio_17_20": float(others[d]), "score": float(score[d]),
                         "catalyst_day": nxt})
    ev = pd.DataFrame(rows)
    # context only: days between report date and nearest NVDA 10-Q/10-K SEC acceptance timestamp
    acc = []
    for tf in ("quarterly", "annual"):
        fin = api_get(f"/vX/reference/financials?ticker=NVDA&limit=100&timeframe={tf}&sort=filing_date&order=desc")
        for r in fin.get("results", []):
            a_ = r.get("acceptance_datetime")
            if a_:
                acc.append(pd.Timestamp(a_).tz_convert(TZ).normalize())
    acc = sorted(set(acc))
    off = []
    for t, d in zip(ev.ticker, ev.report_date):
        if t != "NVDA" or not acc:
            off.append(np.nan)
            continue
        dd = pd.Timestamp(d).tz_localize(TZ)
        after = [(x - dd).days for x in acc if (x - dd).days >= 0]
        off.append(min(after) if after else np.nan)
    ev["nvda_days_to_next_10q_10k_acceptance"] = off
    # Correction rule (second source): if an NVDA pick has no same-day SEC acceptance but an acceptance
    # date follows within 35 days AND that acceptance date itself scores >= 4, use the acceptance date.
    sc_n = np.minimum(ra["NVDA"], rb["NVDA"])
    ev["corrected_from"] = ""
    for i in ev.index[(ev.ticker == "NVDA")]:
        o = ev.at[i, "nvda_days_to_next_10q_10k_acceptance"]
        if np.isfinite(o) and 0 < o <= 35:
            cand = (pd.Timestamp(ev.at[i, "report_date"]) + pd.Timedelta(days=int(o))).strftime("%Y-%m-%d")
            if cand in sc_n.index and sc_n[cand] >= 4:
                j = days.index(cand)
                ev.at[i, "corrected_from"] = ev.at[i, "report_date"]
                ev.at[i, "report_date"] = cand
                ev.at[i, "weekday"] = pd.Timestamp(cand).day_name()
                ev.at[i, "score"] = float(sc_n[cand])
                ev.at[i, "catalyst_day"] = days[j + 1] if j + 1 < len(days) else None
                ev.at[i, "nvda_days_to_next_10q_10k_acceptance"] = 0
    return ev


def macro(sess: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    q = load_minute("QQQ")
    days = list(sess.index)
    q = q[q.date.isin(days)]

    def vol_between(a, b):
        return q[(q["mod"] >= a) & (q["mod"] < b)].groupby("date").v.sum().reindex(days).fillna(0)

    # FOMC: 14:00-14:05 volume spike AND 14:30-14:45 (press-conference) burst, both vs 13:30-13:55
    base = vol_between(13 * 60 + 30, 13 * 60 + 55) / 25
    r14 = (vol_between(14 * 60, 14 * 60 + 5) / 5) / base
    pc = (vol_between(14 * 60 + 30, 14 * 60 + 45) / 15) / base
    score = np.sqrt(r14.clip(lower=0) * pc.clip(lower=0))
    ok = (r14 >= 2) & (pc >= 2) & (~sess.is_half.reindex(score.index).astype(bool)) & (score.index >= "2021-12-01")
    fomc = greedy(score[ok], 30, 2.0)
    F = pd.DataFrame({"date": fomc})
    F["ratio_1400_1405"] = r14.reindex(fomc).values
    F["ratio_1430_1445"] = pc.reindex(fomc).values
    F["score"] = score.reindex(fomc).values
    F["confidence"] = np.where(F.score >= 4, "high", "lower")
    F["weekday"] = pd.to_datetime(F.date).dt.day_name()
    F.attrs["median_ratio_all_days"] = float(r14.median())

    # likely CPI
    spike = vol_between(8 * 60 + 30, 8 * 60 + 33) / 3
    pre = vol_between(8 * 60, 8 * 60 + 30) / 30
    c_ratio = (spike / pre).replace([np.inf], np.nan)
    c = pd.DataFrame({"ratio": c_ratio})
    c["dom"] = pd.to_datetime(c.index).day
    c["ym"] = pd.to_datetime(c.index).strftime("%Y-%m")
    c = c[(c.dom >= 10) & (c.dom <= 15) & (c.index >= "2021-12-01")]
    picks = c.sort_values("ratio", ascending=False).groupby("ym").head(1)
    picks = picks[picks.ratio >= 4.0].sort_index()
    C = pd.DataFrame({"date": picks.index, "ratio_0830": picks.ratio.values})
    C["weekday"] = pd.to_datetime(C.date).dt.day_name()
    # all top-decile 08:30 reaction days (any macro release)
    return F, C, c_ratio


def main():
    sess = sessions()
    ev = earnings(sess)
    F, C, c_ratio = macro(sess)
    save_csv(ev, "events_earnings_detected.csv", index=False)
    save_csv(F, "events_fomc_detected.csv", index=False)
    save_csv(C, "events_cpi_likely_detected.csv", index=False)
    rows = []
    for _, r in ev.iterrows():
        if r.catalyst_day and r.catalyst_day <= END:
            rows.append({"date": r.catalyst_day, "type": f"{r.ticker}_earnings_next_day", "method": "detected: after-hours volume spike on report day"})
    for d, cf in zip(F.date, F.confidence):
        if cf == "high":
            rows.append({"date": d, "type": "FOMC_high_conf", "method": "detected, score>=4"})
        rows.append({"date": d, "type": "FOMC", "method": "detected: QQQ 14:00 + 14:30 ET volume bursts"})
    for d in C.date:
        rows.append({"date": d, "type": "CPI_window_0830", "method": "detected: QQQ 08:30 ET pre-market volume spike, day 10-15, max 1/month"})
    E = pd.DataFrame(rows).sort_values("date")
    E = E[(E.date >= "2022-01-01") & (E.date <= END)]
    save_csv(E, "events_all_detected.csv", index=False)
    print(ev.to_string())
    print(F.to_string())
    print("median 14:00 ratio all days", F.attrs.get("median_ratio_all_days"))
    print(C.to_string())
    print(E.type.value_counts())


if __name__ == "__main__":
    main()
