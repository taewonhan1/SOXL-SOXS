#!/usr/bin/env python3
"""Probe Massive REST endpoints for SOXL / SOXS and record HTTP status + earliest/latest dates.

Output
------
    analysis/backtests/output/endpoint_inventory.csv      one row per probe
    data/soxlab/reference/probe_raw/*.json                  truncated raw responses (gitignored)
    data/soxlab/reference/conditions_stocks.parquet         trade-condition table (for quirk docs)

Earliest date = first record of an ascending query starting at 2000-01-01 (limit=1); latest date =
first record of the matching descending query. Every value in the CSV comes from the live API.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soxlab import api, config  # noqa: E402

END = config.HISTORY_END
RAW = config.REF_DIR / "probe_raw"
ROWS: list[dict] = []
# Options / indices / futures entitlements on this key are rate-limited per minute (HTTP 429
# "exceeded the maximum requests per minute"); pace those families to <= ~5 calls/minute.
PACED = {"options", "indices", "futures"}
PACE_SECONDS = 13.0
_last_paced = [0.0]


def _ts_to_date(v) -> str | None:
    """Convert ms / ns epoch or ISO strings into an ET date string."""
    if v is None:
        return None
    if isinstance(v, str):
        try:
            return pd.Timestamp(v).tz_convert(config.TZ).strftime("%Y-%m-%d") if pd.Timestamp(v).tzinfo \
                else pd.Timestamp(v).strftime("%Y-%m-%d")
        except Exception:
            return v[:10]
    v = int(v)
    unit = "ns" if v > 1e17 else ("ms" if v > 1e11 else "s")
    return pd.Timestamp(v, unit=unit, tz="UTC").tz_convert(config.TZ).strftime("%Y-%m-%d %H:%M:%S")


def _first(js):
    r = js.get("results") if isinstance(js, dict) else None
    if isinstance(r, list):
        return r[0] if r else None
    if isinstance(r, dict):
        vals = r.get("values")
        if isinstance(vals, list):
            return vals[0] if vals else None
        return r
    return None


def _n(js):
    r = js.get("results") if isinstance(js, dict) else None
    if isinstance(r, list):
        return len(r)
    if isinstance(r, dict):
        vals = r.get("values")
        return len(vals) if isinstance(vals, list) else 1
    return js.get("resultsCount") if isinstance(js, dict) else None


def call(name: str, family: str, path: str, params: dict | None = None, ticker: str = "",
         time_key: str | None = None, note: str = "", save: bool = True):
    if family in PACED:
        wait = PACE_SECONDS - (time.time() - _last_paced[0])
        if wait > 0:
            time.sleep(wait)
        _last_paced[0] = time.time()
    resp = api.get(path, params or {}, raise_for_status=False, retries=7)
    js = resp.json() if isinstance(resp.json(), dict) else {"_raw": resp.json()}
    first = _first(js)
    when = None
    if time_key and isinstance(first, dict):
        when = _ts_to_date(first.get(time_key))
    if save:
        RAW.mkdir(parents=True, exist_ok=True)
        trunc = dict(js)
        if isinstance(trunc.get("results"), list):
            trunc["results"] = trunc["results"][:3]
        (RAW / f"{name}_{ticker or 'all'}.json".replace(":", "_").replace("/", "_")).write_text(
            json.dumps(trunc, indent=1, default=str)[:20000])
    row = {"family": family, "probe": name, "ticker": ticker, "endpoint": path,
           "params": json.dumps(params or {}), "http_status": resp.status,
           "api_status": js.get("status") if isinstance(js, dict) else None,
           "n_results": _n(js), "first_record_time_et": when,
           "fields": ",".join(sorted(first.keys()))[:400] if isinstance(first, dict) else "",
           "message": (js.get("message") or js.get("error") or "")[:200] if isinstance(js, dict) else "",
           "note": note}
    ROWS.append(row)
    print(f"{resp.status} {family:12s} {name:28s} {ticker:22s} n={row['n_results']} t={when} {row['message'][:60]}")
    return js, row


def earliest_latest(name, family, path, params, ticker, time_key, asc_params, desc_params, note=""):
    js_a, row_a = call(name + "_earliest", family, path, {**params, **asc_params}, ticker, time_key, note)
    js_d, row_d = call(name + "_latest", family, path, {**params, **desc_params}, ticker, time_key, note)
    return js_a, js_d


def probe_stock(T: str) -> None:
    for span in ("second", "minute", "hour", "day"):
        for adj in ("true", "false") if span == "minute" else ("true",):
            nm = f"aggs_{span}" + ("" if adj == "true" else "_unadj")
            lim = 50_000 if span == "hour" else 1  # 'limit' counts BASE aggregates (minutes) for hour bars
            earliest_latest(nm, "aggregates", f"/v2/aggs/ticker/{T}/range/1/{span}/2000-01-01/{END}",
                            {"adjusted": adj, "limit": lim}, T, "t", {"sort": "asc"}, {"sort": "desc"},
                            "t = bar start, UTC ms" + ("; limit=50000 base aggs" if span == "hour" else ""))
    call("aggs_prev", "aggregates", f"/v2/aggs/ticker/{T}/prev", {}, T, "t")
    call("open_close", "aggregates", f"/v1/open-close/{T}/{END}", {}, T, None,
         "daily open/close incl. preMarket/afterHours fields")
    call("summaries", "snapshot", "/v1/summaries", {"ticker.any_of": T}, T, None)
    # ticks
    earliest_latest("trades", "trades", f"/v3/trades/{T}", {"limit": 1, "sort": "timestamp"}, T,
                    "sip_timestamp", {"order": "asc", "timestamp.gte": "2000-01-01"}, {"order": "desc"})
    earliest_latest("quotes_nbbo", "quotes", f"/v3/quotes/{T}", {"limit": 1, "sort": "timestamp"}, T,
                    "sip_timestamp", {"order": "asc", "timestamp.gte": "2000-01-01"}, {"order": "desc"})
    call("last_trade", "trades", f"/v2/last/trade/{T}", {}, T, "t")
    call("last_nbbo", "quotes", f"/v2/last/nbbo/{T}", {}, T, "t")
    # snapshots
    js, _ = call("snapshot_v2_ticker", "snapshot", f"/v2/snapshot/locale/us/markets/stocks/tickers/{T}", {}, T,
                 None)
    upd = (js.get("ticker") or {}).get("updated") if isinstance(js, dict) else None
    if upd:
        ROWS[-1]["first_record_time_et"] = _ts_to_date(upd)
        ROWS[-1]["note"] = "ticker.updated shown in first_record_time_et"
    call("snapshot_v3_unified", "snapshot", "/v3/snapshot", {"ticker.any_of": T}, T, None)
    # technical indicators
    for ind, extra in (("sma", {"window": 20}), ("ema", {"window": 20}), ("rsi", {"window": 14}),
                       ("macd", {"short_window": 12, "long_window": 26, "signal_window": 9})):
        for tsp in ("minute", "day"):
            earliest_latest(f"ind_{ind}_{tsp}", "indicators", f"/v1/indicators/{ind}/{T}",
                            {"timespan": tsp, "series_type": "close", "adjusted": "true", "limit": 1, **extra},
                            T, "timestamp", {"order": "asc", "timestamp.gte": "2000-01-01"}, {"order": "desc"})
    # reference
    js, _ = call("ticker_details", "reference", f"/v3/reference/tickers/{T}", {}, T, None)
    for d in ("2019-01-02", "2022-01-03", "2024-01-02", "2026-09-25"):
        js, row = call(f"ticker_details_asof_{d}", "reference", f"/v3/reference/tickers/{T}", {"date": d}, T,
                       None)
        res = js.get("results") or {}
        row["note"] = (f"share_class_shares_outstanding={res.get('share_class_shares_outstanding')}; "
                       f"weighted_shares_outstanding={res.get('weighted_shares_outstanding')}")
    call("splits_v3", "reference", "/v3/reference/splits", {"ticker": T, "limit": 1000}, T, "execution_date")
    call("splits_stocks_v1", "reference", "/stocks/v1/splits", {"ticker": T, "limit": 1000}, T, "execution_date")
    call("dividends_v3", "reference", "/v3/reference/dividends", {"ticker": T, "limit": 1000}, T,
         "ex_dividend_date")
    call("dividends_stocks_v1", "reference", "/stocks/v1/dividends", {"ticker": T, "limit": 1000}, T,
         "ex_dividend_date")
    call("ticker_events", "reference", f"/vX/reference/tickers/{T}/events", {}, T, None)
    call("related_companies", "reference", f"/v1/related-companies/{T}", {}, T, None)
    earliest_latest("short_interest", "reference", "/stocks/v1/short-interest",
                    {"ticker": T, "limit": 1}, T, "settlement_date",
                    {"sort": "settlement_date.asc"}, {"sort": "settlement_date.desc"}, "sort=field.asc|desc syntax")
    earliest_latest("short_volume", "reference", "/stocks/v1/short-volume",
                    {"ticker": T, "limit": 1}, T, "date", {"sort": "date.asc"}, {"sort": "date.desc"},
                    "sort=field.asc|desc syntax")
    call("financials_vX", "reference", "/vX/reference/financials", {"ticker": T, "limit": 1}, T, None)
    # news
    earliest_latest("news", "news", "/v2/reference/news", {"ticker": T, "limit": 1, "sort": "published_utc"}, T,
                    "published_utc", {"order": "asc"}, {"order": "desc"})
    js, row = call("news_last_365d", "news", "/v2/reference/news",
                   {"ticker": T, "limit": 1000, "published_utc.gte": "2025-09-26", "order": "asc",
                    "sort": "published_utc"}, T, "published_utc", "count of articles 2025-09-26..2026-09-27 (1 page)")
    call("benzinga_news_v2", "news", "/benzinga/v2/news", {"tickers": T, "limit": 1}, T, "published")
    # ETF Global add-on
    for ep in ("constituents", "fund-flows", "profiles", "analytics", "taxonomies"):
        call(f"etf_global_{ep}", "etf_global", f"/etf-global/v1/{ep}", {"composite_ticker": T, "limit": 1}, T,
             "effective_date")
    # options
    probe_options(T)


def probe_options(T: str) -> None:
    js, row = call("opt_contracts_active", "options", "/v3/reference/options/contracts",
                   {"underlying_ticker": T, "limit": 1000, "expired": "false"}, T, "expiration_date",
                   "first page (limit 1000) of active contracts")
    active = js.get("results") or []
    js_e, _ = call("opt_contracts_expired_earliest", "options", "/v3/reference/options/contracts",
                   {"underlying_ticker": T, "limit": 5, "expired": "true", "order": "asc",
                    "sort": "expiration_date"}, T, "expiration_date")
    # snapshot chain (greeks, IV, open interest)
    js_s, row = call("opt_snapshot_chain", "options", f"/v3/snapshot/options/{T}", {"limit": 250}, T, None)
    chain = js_s.get("results") or []
    have = {k: sum(1 for c in chain if c.get(k) not in (None, {}, [])) for k in
            ("greeks", "implied_volatility", "open_interest", "last_quote", "last_trade", "day")}
    row["note"] = f"of {len(chain)} contracts on page 1, non-empty: {have}"
    # pick a liquid near-dated contract: the one with max day volume on the snapshot page
    pick = None
    if chain:
        chain_sorted = sorted(chain, key=lambda c: -((c.get("day") or {}).get("volume") or 0))
        pick = chain_sorted[0]["details"]["ticker"]
    elif active:
        pick = active[0]["ticker"]
    if pick:
        call("opt_contract_snapshot", "options", f"/v3/snapshot/options/{T}/{pick}", {}, pick, None)
        earliest_latest("opt_aggs_minute", "options", f"/v2/aggs/ticker/{pick}/range/1/minute/2000-01-01/{END}",
                        {"limit": 1}, pick, "t", {"sort": "asc"}, {"sort": "desc"})
        call("opt_aggs_day", "options", f"/v2/aggs/ticker/{pick}/range/1/day/2000-01-01/{END}",
             {"limit": 1, "sort": "asc"}, pick, "t")
        earliest_latest("opt_trades", "options", f"/v3/trades/{pick}", {"limit": 1, "sort": "timestamp"}, pick,
                        "sip_timestamp", {"order": "asc", "timestamp.gte": "2000-01-01"}, {"order": "desc"})
        earliest_latest("opt_quotes", "options", f"/v3/quotes/{pick}", {"limit": 1, "sort": "timestamp"}, pick,
                        "sip_timestamp", {"order": "asc", "timestamp.gte": "2000-01-01"}, {"order": "desc"})
    # history depth: long-dated contracts listed years earlier -> first bar shows the plan's history start
    for exp in ("2025-01-17", "2026-01-16"):
        js_l, _ = call(f"opt_contracts_exp_{exp}", "options", "/v3/reference/options/contracts",
                       {"underlying_ticker": T, "expiration_date": exp, "expired": "true", "contract_type": "call",
                        "limit": 250}, T, "expiration_date")
        cl = js_l.get("results") or []
        if cl:
            mid = cl[len(cl) // 2]["ticker"]
            call(f"opt_aggs_day_leaps_{exp}", "options", f"/v2/aggs/ticker/{mid}/range/1/day/2000-01-01/{END}",
                 {"limit": 1, "sort": "asc"}, mid, "t", "first daily bar of a long-dated contract")
    # oldest expired contract: does history exist for it?
    olds = js_e.get("results") or []
    if olds:
        old = olds[0]["ticker"]
        call("opt_aggs_day_oldest_contract", "options", f"/v2/aggs/ticker/{old}/range/1/day/2000-01-01/{END}",
             {"limit": 1, "sort": "asc"}, old, "t", "oldest listed expired contract in reference data")
        call("opt_trades_oldest_contract", "options", f"/v3/trades/{old}",
             {"limit": 1, "sort": "timestamp", "order": "asc", "timestamp.gte": "2000-01-01"}, old, "sip_timestamp")
        call("opt_quotes_oldest_contract", "options", f"/v3/quotes/{old}",
             {"limit": 1, "sort": "timestamp", "order": "asc", "timestamp.gte": "2000-01-01"}, old, "sip_timestamp")


def probe_indices() -> None:
    js, row = call("index_search_semiconductor", "indices", "/v3/reference/tickers",
                   {"market": "indices", "search": "semiconductor", "limit": 50}, "", None)
    row["note"] = "; ".join(f"{r.get('ticker')}={r.get('name')}" for r in (js.get("results") or []))[:600]
    for I in ("I:SOX", "I:NDX", "I:SPX"):
        for span in ("minute", "day"):
            earliest_latest(f"index_aggs_{span}", "indices", f"/v2/aggs/ticker/{I}/range/1/{span}/2000-01-01/{END}",
                            {"limit": 1}, I, "t", {"sort": "asc"}, {"sort": "desc"})
        call("index_sma_minute", "indices", f"/v1/indicators/sma/{I}",
             {"timespan": "minute", "window": 20, "series_type": "close", "limit": 1}, I, "timestamp")
    call("index_snapshot", "indices", "/v3/snapshot/indices", {"ticker.any_of": "I:SOX,I:NDX"}, "I:SOX,I:NDX", None)


def probe_futures() -> None:
    call("fut_exchanges", "futures", "/futures/v1/exchanges", {"limit": 10}, "", None)
    for pc in ("NQ", "ES"):
        call("fut_products", "futures", "/futures/v1/products", {"product_code": pc, "limit": 5}, pc, None)
        js, row = call("fut_contracts", "futures", "/futures/v1/contracts",
                       {"product_code": pc, "date": END, "limit": 100}, pc, None)
        res = [r for r in (js.get("results") or []) if r.get("ticker") and "-" not in r["ticker"]
               and r.get("last_trade_date", "") >= END]
        res.sort(key=lambda r: r["last_trade_date"])
        tks = [r["ticker"] for r in res]
        row["note"] = "outright contracts as of END (front first): " + ",".join(tks[:8]) + \
            "; contracts endpoint is point-in-time (one row per as-of date)"
        call("fut_schedules", "futures", "/futures/v1/schedules", {"product_code": pc, "limit": 1}, pc, None)
        call("fut_market_status", "futures", "/futures/v1/market-status", {"product_code": pc, "limit": 1}, pc,
             None)
        call("fut_snapshot", "futures", "/futures/v1/snapshot", {"product_code": pc, "limit": 5}, pc, None)
        tk = tks[0] if tks else f"{pc}Z6"
        earliest_latest("fut_aggs_1min", "futures", f"/futures/v1/aggs/{tk}", {"resolution": "1min", "limit": 1},
                        tk, "window_start", {"sort": "window_start.asc"}, {"sort": "window_start.desc"})
        for old in (f"{pc}Z5", f"{pc}Z4", f"{pc}Z3"):
            call("fut_aggs_1day_history", "futures", f"/futures/v1/aggs/{old}",
                 {"resolution": "1session", "limit": 1, "sort": "window_start.asc"}, old, "window_start",
                 "history depth check on an expired contract")
        call("fut_trades", "futures", f"/futures/v1/trades/{tk}", {"limit": 1}, tk, "timestamp")
        call("fut_quotes", "futures", f"/futures/v1/quotes/{tk}", {"limit": 1}, tk, "timestamp")


def probe_market() -> None:
    call("marketstatus_now", "market", "/v1/marketstatus/now", {}, "", None)
    js, row = call("marketstatus_upcoming", "market", "/v1/marketstatus/upcoming", {}, "", None)
    if isinstance(js, dict) and isinstance(js.get("_raw"), list):
        up = js["_raw"]
        row["n_results"] = len(up)
        row["note"] = "; ".join(f"{u.get('date')} {u.get('exchange')} {u.get('status')} {u.get('open', '')}-"
                                f"{u.get('close', '')}" for u in up if u.get("exchange") == "NYSE")[:600]
    js, row = call("conditions_stocks", "reference", "/v3/reference/conditions",
                   {"asset_class": "stocks", "limit": 1000}, "", None)
    conds = js.get("results") or []
    if conds:
        pd.json_normalize(conds).to_parquet(config.REF_DIR / "conditions_stocks.parquet", index=False)
    call("exchanges_stocks", "reference", "/v3/reference/exchanges", {"asset_class": "stocks"}, "", None)
    call("grouped_daily", "aggregates", f"/v2/aggs/grouped/locale/us/market/stocks/{END}", {"adjusted": "true"}, "",
         None, "all US stocks for one day", save=False)


def main() -> None:
    t0 = time.time()
    config.REF_DIR.mkdir(parents=True, exist_ok=True)
    for T in config.TRADED:
        probe_stock(T)
    probe_indices()
    probe_futures()
    probe_market()
    df = pd.DataFrame(ROWS)
    df.insert(0, "probed_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = config.OUTPUT_DIR / "endpoint_inventory.csv"
    df.to_csv(out, index=False)
    print(f"wrote {out} ({len(df)} probes) in {time.time() - t0:.0f}s")
    print(df.groupby(["family", "http_status"]).size())


if __name__ == "__main__":
    main()
