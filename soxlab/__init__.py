"""soxlab - data, feature, backtest and tracking toolkit for SOXL / SOXS intraday work.

Modules
-------
config      paths, universe, session constants, cost assumptions
api         Massive (formerly Polygon.io) REST client with retry/backoff and bounded concurrency
data        download / cache / load 1-minute and daily bars, splits, trading calendar
calendar    trading-day calendar, half-day detection, event flags
quality     data-quality checks and report
features    look-ahead-safe feature engineering + data dictionary
costs       half-spread table, commissions, SEC / FINRA fees
backtest    next-bar-open execution engine, metrics, walk-forward, random baseline
strategies  behavior-probe signal generators
tracker     daily behavior tracker (one row per day per ticker)
"""

__version__ = "0.1.0"
