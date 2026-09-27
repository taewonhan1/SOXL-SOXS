#!/usr/bin/env python3
"""Pin down how far back options aggregates go on this key (options calls are paced to <= 5/min).

For several as-of dates, list near-the-money SOXL / SOXS calls expiring 2-5 weeks later (reference data
supports ``as_of``), then request their daily aggregates for the two weeks after the as-of date. If
bars come back, options history reaches that date. Rows are appended to endpoint_inventory.csv.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soxlab import api, config  # noqa: E402
from soxlab import data as sdata  # noqa: E402

ASOF = ["2023-06-01", "2024-06-03", "2024-09-03", "2024-10-01", "2025-01-02"]
PACE = 13.0


def paced_get(path, params):
    time.sleep(PACE)
    r = api.get(path, params, raise_for_status=False, retries=7)
    return r.status, (r.json() if isinstance(r.json(), dict) else {})


def main() -> None:
    rows = []
    for T in config.TRADED:
        du = sdata.load_daily(T, False)
        for a in ASOF:
            px = float(du.loc[:a, "c"].iloc[-1])
            a_ts = pd.Timestamp(a)
            st, js = paced_get("/v3/reference/options/contracts", {
                "underlying_ticker": T, "as_of": a, "contract_type": "call",
                "expiration_date.gte": (a_ts + pd.Timedelta(days=14)).strftime("%Y-%m-%d"),
                "expiration_date.lte": (a_ts + pd.Timedelta(days=35)).strftime("%Y-%m-%d"),
                "strike_price.gte": round(px * 0.9, 2), "strike_price.lte": round(px * 1.1, 2), "limit": 100})
            cs = js.get("results") or []
            cs.sort(key=lambda c: abs(c["strike_price"] - px))
            pick = cs[0]["ticker"] if cs else None
            n_bars, first = None, None
            if pick:
                end = (a_ts + pd.Timedelta(days=14)).strftime("%Y-%m-%d")
                st2, js2 = paced_get(f"/v2/aggs/ticker/{pick}/range/1/day/{a}/{end}", {"sort": "asc", "limit": 50})
                res = js2.get("results") or []
                n_bars = len(res)
                first = pd.Timestamp(res[0]["t"], unit="ms", tz="UTC").tz_convert(config.TZ).strftime("%Y-%m-%d") if res else None
            else:
                st2 = None
            rows.append({"family": "options", "probe": f"opt_history_asof_{a}", "ticker": pick or T,
                         "endpoint": "/v3/reference/options/contracts (as_of) + /v2/aggs/ticker/{contract}/range/1/day",
                         "params": f"as_of={a}; underlying close {px:.2f}; near-the-money call 2-5 weeks out",
                         "http_status": st2 if st2 else st, "api_status": "", "n_results": n_bars,
                         "first_record_time_et": first, "fields": "", "message": "" if cs else "no contracts listed",
                         "note": f"contracts listed as of {a}: {len(cs)}"})
            print(rows[-1])
    inv = config.OUTPUT_DIR / "endpoint_inventory.csv"
    df = pd.read_csv(inv)
    df = df[~df["probe"].str.startswith("opt_history_asof_")]
    add = pd.DataFrame(rows)
    add.insert(0, "probed_at_utc", pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S"))
    pd.concat([df, add], ignore_index=True).to_csv(inv, index=False)
    print(f"appended {len(add)} rows to {inv}")


if __name__ == "__main__":
    main()
