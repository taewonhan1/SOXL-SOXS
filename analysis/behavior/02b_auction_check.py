"""Check how opening/closing auction prints appear in trades vs minute bars (one session, 2026-09-25).
Largest prints around 09:30:00 and 16:00:00 ET from /v3/trades, compared with the 09:30 / 16:00 minute-bar
volume and the daily bar. Output: output/data_auction_print_check.csv"""
from __future__ import annotations

import pandas as pd

from common import BASE, TZ, api_get, load_minute, load_daily, save_csv

DAY = "2026-09-25"
WINDOWS = {"open": ("2026-09-25T13:29:59Z", "2026-09-25T13:30:02Z", 570),
           "close": ("2026-09-25T19:59:59Z", "2026-09-25T20:00:03Z", 960)}
rows = []
for t in ["SOXL", "SOXS", "SOXX"]:
    m = load_minute(t)
    m = m[m.date == DAY]
    d = load_daily(t, True).loc[DAY]
    for lab, (gte, lt, mod) in WINDOWS.items():
        url = f"{BASE}/v3/trades/{t}?timestamp.gte={gte}&timestamp.lt={lt}&limit=50000&sort=timestamp&order=asc"
        res = []
        while url:
            j = api_get(url)
            res += j.get("results", [])
            url = j.get("next_url")
        tr = pd.DataFrame(res)
        tr["ts"] = pd.to_datetime(tr.sip_timestamp, unit="ns", utc=True).dt.tz_convert(TZ)
        big = tr.sort_values("size", ascending=False).head(2)
        bar = m[m["mod"] == mod]
        for _, b in big.iterrows():
            rows.append({"ticker": t, "window": lab, "trade_time_ET": b.ts.strftime("%H:%M:%S.%f"), "price": b.price,
                         "size": b["size"], "exchange_id": b.exchange, "conditions": str(b.get("conditions")),
                         "minute_bar_start": f"{mod // 60:02d}:{mod % 60:02d}",
                         "minute_bar_volume": float(bar.v.iloc[0]) if len(bar) else None,
                         "minute_bar_open": float(bar.o.iloc[0]) if len(bar) else None,
                         "daily_bar_open": d.o, "daily_bar_close": d.c})
save_csv(pd.DataFrame(rows), "data_auction_print_check.csv", index=False)
print(pd.DataFrame(rows).to_string())
