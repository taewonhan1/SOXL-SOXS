"""Light NBBO sample from /v3/quotes, summarised per 5-minute window.

Sample design (all windows are 5 minutes, ET):
  A) 10 most recent full sessions before 2026-09-26 (2026-09-14 .. 2026-09-25):
       SOXL, SOXS : 09:35, 10:30, 12:30, 14:30, 15:45
       SOXX, SMH, NVDA, TQQQ, QQQ : 10:30, 14:30
  B) one session per month (the trading day closest to the 15th), 2022-01 .. 2026-09:
       SOXL, SOXS : 09:35, 10:30, 14:30
Raw windows are cached (bid, ask, sizes, sip_timestamp) in data/dynamics/quotes/.
Summary (time-weighted quoted spread etc.) -> output/nbbo_windows.csv
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from common import DATA, OUT, TZ, api_get_all, half_days, load_daily

QDIR = DATA / "quotes"
QDIR.mkdir(parents=True, exist_ok=True)
MAXW = 4


def trading_days():
    d = load_daily("QQQ", True)
    days = pd.to_datetime(d["t"], unit="ms", utc=True).dt.tz_convert(TZ).dt.date
    hd = half_days()
    return [x for x in days if x not in hd]


def fetch_window(ticker, day, hhmm, minutes=5):
    fn = QDIR / f"{ticker}_{day}_{hhmm.replace(':', '')}.parquet"
    if fn.exists():
        return pd.read_parquet(fn)
    start = pd.Timestamp(f"{day} {hhmm}", tz=TZ)
    end = start + pd.Timedelta(minutes=minutes)
    params = {"timestamp.gte": start.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
              "timestamp.lt": end.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
              "limit": 50000, "sort": "timestamp", "order": "asc"}
    res = api_get_all(f"/v3/quotes/{ticker}", params)
    df = pd.DataFrame(res)
    keep = [c for c in ["sip_timestamp", "bid_price", "ask_price", "bid_size", "ask_size"] if c in df.columns]
    df = df[keep] if len(df) else pd.DataFrame(columns=keep)
    df.to_parquet(fn)
    return df


def summarise(df, ticker, day, hhmm, minutes=5):
    start = pd.Timestamp(f"{day} {hhmm}", tz=TZ)
    end_ns = (start + pd.Timedelta(minutes=minutes)).value
    n_all = len(df)
    if n_all == 0:
        return dict(ticker=ticker, date=str(day), window=hhmm, n_quotes=0)
    ts = df["sip_timestamp"].to_numpy(dtype=np.int64)
    bid = df["bid_price"].to_numpy(float)
    ask = df["ask_price"].to_numpy(float)
    dur = np.diff(np.append(ts, end_ns)).astype(float)
    ok = (bid > 0) & (ask > 0) & (ask > bid)
    locked_crossed = ((bid > 0) & (ask > 0) & (ask <= bid))
    spr = ask - bid
    mid = (ask + bid) / 2
    w = np.where(ok, dur, 0.0)
    W = w.sum()
    tw_spread = (spr * w).sum() / W
    tw_mid = (mid * w).sum() / W
    tw_bps = ((spr / mid) * 1e4 * w).sum() / W
    ticks = np.round(spr / 0.01)
    share1 = (w * (ticks <= 1)).sum() / W
    bs = df["bid_size"].to_numpy(float) if "bid_size" in df else np.full(n_all, np.nan)
    as_ = df["ask_size"].to_numpy(float) if "ask_size" in df else np.full(n_all, np.nan)
    return dict(ticker=ticker, date=str(day), window=hhmm, n_quotes=n_all,
                frac_time_locked_crossed=(dur * locked_crossed).sum() / dur.sum(),
                tw_mid=tw_mid, tw_spread_usd=tw_spread, tw_spread_bps=tw_bps,
                median_spread_usd=float(np.median(spr[ok])), share_time_1tick=share1,
                tw_bid_size=(bs * w).sum() / W, tw_ask_size=(as_ * w).sum() / W)


def main():
    days = trading_days()
    recent = [d for d in days if str(d) <= "2026-09-25"][-10:]
    jobs = []
    for d in recent:
        for w in ["09:35", "10:30", "12:30", "14:30", "15:45"]:
            for t in ["SOXL", "SOXS"]:
                jobs.append((t, d, w, "recent"))
        for w in ["10:30", "14:30"]:
            for t in ["SOXX", "SMH", "NVDA", "TQQQ", "QQQ"]:
                jobs.append((t, d, w, "recent"))
    ser = pd.Series(pd.to_datetime([str(x) for x in days]), index=range(len(days)))
    for per in pd.period_range("2022-01", "2026-09", freq="M"):
        target = pd.Timestamp(per.year, per.month, 15)
        cand = ser[(ser.dt.year == per.year) & (ser.dt.month == per.month)]
        if not len(cand):
            continue
        d = days[(cand - target).abs().idxmin()]
        if d in recent:
            continue
        for w in ["09:35", "10:30", "14:30"]:
            for t in ["SOXL", "SOXS"]:
                jobs.append((t, d, w, "monthly"))
    print("jobs", len(jobs), flush=True)
    rows = []
    with ThreadPoolExecutor(MAXW) as ex:
        futs = {ex.submit(fetch_window, t, d, w): (t, d, w, s) for t, d, w, s in jobs}
        for i, f in enumerate(as_completed(futs)):
            t, d, w, s = futs[f]
            r = summarise(f.result(), t, d, w)
            r["sample"] = s
            rows.append(r)
            if i % 50 == 0:
                print(i, t, d, w, r.get("n_quotes"), flush=True)
    out = pd.DataFrame(rows).sort_values(["ticker", "date", "window"])
    out.to_csv(OUT / "nbbo_windows.csv", index=False, float_format="%.6g")
    print(out.groupby(["ticker", "sample"])[["tw_spread_usd", "tw_spread_bps", "share_time_1tick"]].median())


if __name__ == "__main__":
    main()
