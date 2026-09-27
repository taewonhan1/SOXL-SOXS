"""Convenience loaders shared by scripts: calendar, panels, official closes, pre-market, features."""
from __future__ import annotations

import time

import pandas as pd

from . import calendar as scal
from . import config
from . import data as sdata
from . import features as sfeat

PANEL_TICKERS = ["SOXL", "SOXS", "SOXX", "NVDA", "QQQ", "SMH"]


def load_context(start: str = config.HISTORY_START, end: str = config.HISTORY_END,
                 tickers=PANEL_TICKERS, feature_tickers=config.TRADED, verbose: bool = True) -> dict:
    t0 = time.time()
    cal = scal.load_calendar()
    cal = cal[(cal.index >= pd.Timestamp(start)) & (cal.index <= pd.Timestamp(end))]
    panels = {tk: sdata.build_panel(tk, cal, start, end) for tk in tickers}
    dates = panels[tickers[0]].dates
    official = {tk: sfeat.official_close(tk, dates) for tk in tickers}
    premarket = {tk: sfeat.premarket_summary(tk, dates) for tk in feature_tickers}
    feats = {tk: sfeat.compute_features(tk, panels, official, premarket, cal) for tk in feature_tickers}
    if verbose:
        print(f"context loaded: {len(dates)} days x {len(tickers)} tickers in {time.time() - t0:.0f}s")
    return {"cal": cal, "panels": panels, "official": official, "premarket": premarket, "features": feats}
