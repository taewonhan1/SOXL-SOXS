"""Step 6: supporting checks.

Outputs (analysis/microstructure/output/):
  nbbo_size_granularity_by_day.csv  share of 1-second NBBO snapshots whose bid/ask size is not a multiple of 100 shares
  trade_condition_census.csv        trade counts / volume by individual SIP condition code (sampled RTH windows, last 12 months)
  rth_gap_verification.csv          raw-trade check of the minute-bar gaps listed in rth_trade_gaps_2024_2026.csv
  luld_quote_flags.csv              sampled windows containing NBBO messages with quote condition 43 (LULD trading pause)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from ms_common import DATA, ET, OUT, TICKERS, et_to_utc_ns, fetch_trades, sample_days, unpack_conds  # noqa: E402

TICK = DATA / "tick"


def main():
    sd = sample_days()
    cat = dict(zip(sd.day, sd.category))
    # 1) NBBO size granularity
    rows = []
    for T in TICKERS:
        for day in sd.day:
            f = TICK / T / f"{day}_snap.parquet"
            if not f.exists():
                continue
            s = pd.read_parquet(f, columns=["bsz", "asz"]).dropna()
            s = s[(s.bsz > 0) & (s.asz > 0)]
            if not len(s):
                continue
            rows.append({"ticker": T, "day": day, "n_snapshots": len(s),
                         "share_bid_size_not_mult100": float((s.bsz % 100 != 0).mean()),
                         "share_ask_size_not_mult100": float((s.asz % 100 != 0).mean()),
                         "share_bid_size_mult40_not100": float(((s.bsz % 40 == 0) & (s.bsz % 100 != 0)).mean()),
                         "min_bid_size": float(s.bsz.min())})
    pd.DataFrame(rows).to_csv(OUT / "nbbo_size_granularity_by_day.csv", index=False)
    # 2) condition census (RTH rotating windows, last-12-month normal days)
    rows = []
    days12 = sd[(sd.day >= "2025-09-26") & (sd.category != "stress")].day
    for T in TICKERS:
        parts = []
        for day in days12:
            f = TICK / T / f"{day}_trades.parquet"
            w = TICK / T / f"{day}_wmeta.parquet"
            if not f.exists():
                continue
            t = pd.read_parquet(f, columns=["t", "size", "cond", "wid", "ex"])
            wm = pd.read_parquet(w)[["wid", "kind"]]
            t = t.merge(wm, on="wid")
            parts.append(t[t.kind == "rth"])
        if not parts:
            continue
        t = pd.concat(parts)
        n, v = len(t), t["size"].sum()
        codes = t["cond"].map(lambda c: unpack_conds(int(c)) or [0])
        ex = t.assign(code=codes).explode("code")
        g = ex.groupby("code").agg(n=("size", "size"), vol=("size", "sum")).reset_index()
        g["share_trades"] = g.n / n
        g["share_volume"] = g.vol / v
        g.insert(0, "ticker", T)
        g["n_trades_total"] = n
        rows.append(g)
    pd.concat(rows).to_csv(OUT / "trade_condition_census.csv", index=False)
    # 3) verify minute-bar gaps with raw trades (all gaps with >= 3 missing minutes)
    gaps = pd.read_csv(OUT / "rth_trade_gaps_2024_2026.csv")
    rows = []
    for r in gaps[gaps.missing_minutes >= 3].itertuples():
        a = r.last_bar_before if r.last_bar_before != "open" else "09:30"
        s = et_to_utc_ns(r.date, a) + 60 * 10**9
        e = et_to_utc_ns(r.date, r.next_bar)
        tr = fetch_trades(r.ticker, s, e)
        conds = sorted({c for v in tr["cond"] for c in unpack_conds(int(v))}) if len(tr) else []
        rows.append({"ticker": r.ticker, "date": r.date, "gap_start": a, "gap_end": r.next_bar, "missing_minutes": r.missing_minutes,
                     "raw_trades_in_gap": len(tr), "raw_volume_in_gap": float(tr["size"].sum()) if len(tr) else 0.0,
                     "max_seconds_between_trades": float(np.diff(np.r_[s, tr["t"].to_numpy(), e]).max() / 1e9),
                     "condition_codes_seen": " ".join(map(str, conds))})
    pd.DataFrame(rows).to_csv(OUT / "rth_gap_verification.csv", index=False)
    # 4) LULD quote flags in the sampled windows
    rows = []
    for T in TICKERS:
        for day in sd.day:
            f = TICK / T / f"{day}_qstats.parquet"
            if not f.exists():
                continue
            q = pd.read_parquet(f)
            x = q[q.n_luld_quotes > 0]
            for r in x.itertuples():
                rows.append({"ticker": T, "day": day, "category": cat[day], "kind": r.kind, "sub_start_min": r.sub_start,
                             "n_luld_quotes": r.n_luld_quotes, "n_msg": r.n_msg})
            rows.append({"ticker": T, "day": day, "category": cat[day], "kind": "ALL", "sub_start_min": -1,
                         "n_luld_quotes": int(q.n_luld_quotes.sum()), "n_msg": int(q.n_msg.sum()),
                         "n_nonregular_quotes": int(q.n_nonregular_quotes.sum())})
    pd.DataFrame(rows).to_csv(OUT / "luld_quote_flags.csv", index=False)
    print("done")


if __name__ == "__main__":
    main()
    import os
    os._exit(0)
