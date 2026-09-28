#!/usr/bin/env python3
"""Event calendar for Study 5's G3 gate (REGISTRY.md), built only from data known before each session.

G3(a) earnings: NVDA/AMD/AVGO/MU after-hours (16:00-20:00) volume on day d-1 >= 5x its median over the prior
      60 sessions -> session d is the day after an earnings release.
G3(b) FOMC: scheduled statement days (list in REGISTRY.md).
G3(c) 08:30 macro release: QQQ 08:30 1-minute bar volume >= 5x its median over the prior 60 sessions.
Output: analysis/strategies/output/event_calendar.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from runlib import ROOT  # noqa: I001
from soxlab import data as sdata
from soxlab.research import common as C

FOMC = """2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16""".split()

KNOWN_RELEASES = {  # spot checks (release evening; next session is the event day)
    "NVDA": ["2024-02-21", "2024-05-22", "2024-08-28", "2024-11-20", "2025-02-26", "2025-05-28", "2025-08-27"],
    "AMD": ["2024-10-29", "2025-02-04"], "AVGO": ["2024-12-12", "2025-03-06"], "MU": ["2024-12-18", "2025-03-20"],
}


def prior_median(x: pd.Series, w: int = 60) -> pd.Series:
    return x.shift(1).rolling(w, min_periods=40).median()


def main() -> None:
    cal = C.Context().cal
    days = pd.DatetimeIndex(cal.index)
    out = pd.DataFrame(index=days)
    checks = []
    for tk in ("NVDA", "AMD", "AVGO", "MU"):
        b = sdata.load_minute_bars(tk, True, C.HIST_START, C.HIST_END)
        ah = b[(b["mod"] >= 16 * 60) & (b["mod"] < 20 * 60)].groupby("date")["v"].sum().reindex(days).fillna(0.0)
        release = ah >= 5 * prior_median(ah)
        out[f"earn_{tk}"] = release.shift(1, fill_value=False).to_numpy()   # next session after the release
        rel_days = set(release[release].index.strftime("%Y-%m-%d"))
        for dstr in KNOWN_RELEASES[tk]:
            checks.append({"ticker": tk, "known_release": dstr, "detected": dstr in rel_days})
        print(f"{tk}: {int(release.sum())} release evenings detected")
    out["fomc"] = days.isin(pd.DatetimeIndex(FOMC))
    q = sdata.load_minute_bars("QQQ", True, C.HIST_START, C.HIST_END)
    v830 = q[q["mod"] == 8 * 60 + 30].groupby("date")["v"].sum().reindex(days).fillna(0.0)
    out["macro_0830"] = (v830 >= 5 * prior_median(v830)).to_numpy()
    out["g3_any"] = out[["earn_NVDA", "earn_AMD", "earn_AVGO", "earn_MU", "fomc", "macro_0830"]].any(axis=1)
    out.index.name = "date"
    dst = C.RESEARCH_OUT / "event_calendar.csv"
    out.to_csv(dst)
    ck = pd.DataFrame(checks)
    ck.to_csv(C.RESEARCH_OUT / "event_calendar_checks.csv", index=False)
    print(ck.to_string(index=False))
    print(out.astype(int).groupby(out.index.year).sum().to_string())
    print(f"wrote {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
