"""Download and cache all raw data used by the behavior study (idempotent).

- daily bars (split-adjusted and unadjusted) for MAIN + EXTRA tickers
- 1-minute bars (split-adjusted, 04:00-20:00 ET) for MAIN tickers, monthly parquet chunks
- 1-hour bars for NVDA/AVGO/AMD/MU (after-hours volume -> earnings-date detection)
- 1-second bars for SECOND_TICKERS on the last 10 sessions (lead-lag)
- splits and dividends reference data
Concurrency is capped at 4 simultaneous requests (API is shared with other analysts).
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from common import DATA, END, EXTRA, MAIN, SECOND_TICKERS, WARMUP_START, api_get, fetch_aggs

MAX_WORKERS = 4
SECOND_DAYS = ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18",
               "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25"]


def month_ranges(start: str, end: str):
    s = pd.Timestamp(start).replace(day=1)
    e = pd.Timestamp(end)
    while s <= e:
        m_end = min(s + pd.offsets.MonthEnd(0), e)
        yield s.strftime("%Y-%m-%d"), m_end.strftime("%Y-%m-%d"), s.strftime("%Y-%m")
        s = s + pd.offsets.MonthBegin(1)


def job_daily(t, adjusted):
    d = DATA / ("daily_adj" if adjusted else "daily_unadj")
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{t}.parquet"
    if f.exists():
        return f"skip {f.name}"
    df = fetch_aggs(t, 1, "day", "2021-06-01", END, adjusted)
    df.to_parquet(f)
    return f"daily {t} adj={adjusted} rows={len(df)}"


def job_minute(t, fr, to, tag):
    d = DATA / "minute" / t
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{tag}.parquet"
    if f.exists():
        return None
    df = fetch_aggs(t, 1, "minute", fr, to, True)
    df.to_parquet(f)
    return f"minute {t} {tag} rows={len(df)}"


def job_hour(t):
    d = DATA / "hour"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{t}.parquet"
    if f.exists():
        return f"skip {f.name}"
    df = fetch_aggs(t, 1, "hour", WARMUP_START, END, True)
    df.to_parquet(f)
    return f"hour {t} rows={len(df)}"


def job_second(t, day):
    d = DATA / "second" / t
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{day}.parquet"
    if f.exists():
        return None
    df = fetch_aggs(t, 1, "second", day, day, True)
    df.to_parquet(f)
    return f"second {t} {day} rows={len(df)}"


def reference():
    d = DATA / "ref"
    d.mkdir(parents=True, exist_ok=True)
    out = {}
    for t in MAIN + EXTRA:
        sp = api_get(f"/v3/reference/splits?ticker={t}&limit=1000").get("results", [])
        dv = api_get(f"/v3/reference/dividends?ticker={t}&limit=1000").get("results", [])
        out[t] = {"splits": sp, "dividends": dv}
    (d / "splits_dividends.json").write_text(json.dumps(out, indent=1))
    return "reference ok"


def main():
    jobs = []
    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        jobs.append(ex.submit(reference))
        for t in MAIN + EXTRA:
            jobs.append(ex.submit(job_daily, t, True))
            jobs.append(ex.submit(job_daily, t, False))
        for t in ["NVDA"] + EXTRA:
            jobs.append(ex.submit(job_hour, t))
        for t in MAIN:
            for fr, to, tag in month_ranges(WARMUP_START, END):
                jobs.append(ex.submit(job_minute, t, fr, to, tag))
        for t in SECOND_TICKERS:
            for day in SECOND_DAYS:
                jobs.append(ex.submit(job_second, t, day))
        n = 0
        for fut in as_completed(jobs):
            n += 1
            try:
                msg = fut.result()
            except Exception as e:  # keep going, report at end
                msg = f"ERROR {e}"
            if msg and (msg.startswith("ERROR") or n % 25 == 0 or not msg.startswith("minute")):
                print(f"[{n}/{len(jobs)}] {msg}", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    sys.exit(main())
