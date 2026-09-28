"""Shared runner utilities for the study scripts (see analysis/strategies/REGISTRY.md)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from soxlab.research import common as C  # noqa: E402
from soxlab.research import engine as E  # noqa: E402

CROSS = ["SOXX", "SMH", "NVDA", "QQQ", "TQQQ"]
MAIN_PERIODS = ("pre", "dev", "val")          # holdout stays masked until a variant passes 1-5


class Runner:
    def __init__(self, key: str, stop_slippage: bool = False, quote_periods=("dev", "val", "hold")):
        self.key = key
        self.stop_slippage = stop_slippage        # adds case S (case B + 1 cent per stop-order fill)
        self.quote_periods = quote_periods
        self.out = C.RESEARCH_DIR / key
        self.out.mkdir(parents=True, exist_ok=True)
        self.t0 = time.time()
        self.ctx = C.Context()
        self.cms = {"A": C.cost_model(0.0), "B": C.cost_model(C.COMMISSION_B)}
        self.summ, self.cross, self.robust = [], [], []

    def log(self, msg: str) -> None:
        print(f"[{self.key} {time.time() - self.t0:6.0f}s] {msg}", flush=True)

    # ------------------------------------------------------------------ core
    def trades(self, fn, sig: str = "SOXL", mode: str = "switch", is_trades: bool = False,
               sim_kwargs: dict | None = None, day_mask=None, legs=None, max_per_day: int | None = None,
               quote: bool = False, **params):
        """Trades for one rule. ``legs`` (e.g. ("A", "B")) runs an equal-size scale-out: each leg is simulated
        from the same intents, positions are limited jointly (``max_per_day`` signals a day, one position at
        a time) and the legs are merged into one trade per signal."""
        emode = mode if sig == "SOXL" else "ls"
        if legs is None and max_per_day is None:
            obj = fn(self.ctx, sig=sig, **params)
            if isinstance(obj, tuple):          # (intents, close-based exit arrays)
                obj, kw = obj
                sim_kwargs = {**(sim_kwargs or {}), **kw}
            if day_mask is not None:            # day-level gate (Study 5): keep only days where the mask is True
                obj = obj[np.asarray(day_mask, bool)[obj["d"].to_numpy().astype(int)]]
            tr = obj if is_trades else E.simulate(self.ctx[sig], obj, **(sim_kwargs or {}))
            ex, sk = E.execute(tr, self.ctx, mode=emode, sig=sig)
            return self._price(E.add_costs(ex, self.cms), quote), sk
        sims = []
        for lg in (legs or [None]):
            obj = fn(self.ctx, sig=sig, **({"leg": lg} if lg else {}), **params)
            it, kw = obj if isinstance(obj, tuple) else (obj, {})
            sims.append(E.simulate(self.ctx[sig], it, one_position=False, **{**(sim_kwargs or {}), **kw}))
        exs, sk0 = [], None
        for tr in E.filter_positions(sims, max_per_day):
            ex, sk = E.execute(tr, self.ctx, mode=emode, sig=sig)
            exs.append(self._price(E.add_costs(ex, self.cms), quote))
            sk0 = sk if sk0 is None else sk0
        return (E.merge_legs(exs, legs) if len(exs) > 1 else exs[0]), sk0

    def _price(self, ex: pd.DataFrame, quote: bool) -> pd.DataFrame:
        if self.stop_slippage:
            ex = E.add_stop_slippage(ex)
        if quote:
            ex = E.add_quote_fills(ex, self.cms["B"], periods=self.quote_periods)
        return ex

    def main_variant(self, vid: str, fn, quote: bool = False, is_trades: bool = False,
                     sim_kwargs: dict | None = None, mode: str = "switch", day_mask=None,
                     **params) -> pd.DataFrame:
        ex, sk = self.trades(fn, is_trades=is_trades, sim_kwargs=sim_kwargs, mode=mode, day_mask=day_mask,
                             quote=quote, **params)
        E.save_trades(ex, self.key, vid)
        if len(sk):
            E.save_trades(sk, self.key, f"{vid}_skipped_bearish")
        s = E.summarize(ex, self.ctx, vid, sk, periods=MAIN_PERIODS)
        self.summ.append(s)
        return ex

    def robustness(self, vid: str, kind: str, fn, is_trades: bool = False, sim_kwargs: dict | None = None,
                   **params) -> None:
        ex, sk = self.trades(fn, is_trades=is_trades, sim_kwargs=sim_kwargs, **params)
        s = E.summarize(ex, self.ctx, vid, sk, periods=MAIN_PERIODS)
        s["test"] = kind
        self.robust.append(s)

    def crosscheck(self, vid: str, fn, tickers=CROSS, is_trades: bool = False, sim_kwargs: dict | None = None,
                   **params) -> None:
        for T in tickers:
            ex, _ = self.trades(fn, sig=T, mode="ls", is_trades=is_trades, sim_kwargs=sim_kwargs, **params)
            s = E.summarize(ex, self.ctx, vid, None, periods=MAIN_PERIODS)
            s["ticker"] = T
            self.cross.append(s[s["side"] == "all"])

    # ------------------------------------------------------------------ verdicts
    def finish(self, extra_pre_checks: bool = False, neighbour_label: str = "neighbour") -> pd.DataFrame:
        summ = pd.concat(self.summ, ignore_index=True)
        rob = pd.concat(self.robust, ignore_index=True) if self.robust else pd.DataFrame()
        cross = pd.concat(self.cross, ignore_index=True) if self.cross else pd.DataFrame()
        summ.to_csv(self.out / "summary.csv", index=False, float_format="%.4f")
        if len(rob):
            rob.to_csv(self.out / "robustness.csv", index=False, float_format="%.4f")
        if len(cross):
            cross.to_csv(self.out / "crosscheck.csv", index=False, float_format="%.4f")
        rows = []
        for vid in summ["variant"].unique():
            v = E.pick(summ, vid, "val")
            vq = E.pick(summ, vid, "val", case="Q")
            r = {"variant": vid, "val_n": v.get("n_trades"), "val_trades_per_day": v.get("trades_per_day"),
                 "val_mean_gross": v.get("mean_gross_bps"), "val_mean_net_B": v.get("mean_net_bps"),
                 "val_t_net_B": v.get("t_net"), "val_quarters_pos": v.get("quarters_positive"),
                 "val_days_traded": v.get("n_days_traded"),
                 "val_mean_net_Q": vq.get("mean_net_bps") if len(vq) else np.nan,
                 "dev_mean_net_B": E.pick(summ, vid, "dev").get("mean_net_bps"),
                 "dev_t_net_B": E.pick(summ, vid, "dev").get("t_net"),
                 "pre_mean_net_B": E.pick(summ, vid, "pre").get("mean_net_bps"),
                 "pre_t_net_B": E.pick(summ, vid, "pre").get("t_net")}
            vs = E.pick(summ, vid, "val", case="S")
            if len(vs):
                r["val_mean_net_S"] = vs.get("mean_net_bps")
            r["p_val_one_sided"] = C.one_sided_p(r["val_t_net_B"], int(r["val_days_traded"] or 0))
            r["c1_net_ge5"] = bool(np.nan_to_num(r["val_mean_net_B"], nan=-1e9) >= 5)
            r["c1_q_pos"] = (bool(r["val_mean_net_Q"] > 0) if np.isfinite(r["val_mean_net_Q"]) else None)
            r["c2_t_and_quarters"] = bool(np.nan_to_num(r["val_t_net_B"], nan=-9) >= 2 and
                                          np.nan_to_num(r["val_quarters_pos"], nan=0) >= 0.6)
            if len(rob):
                dly = rob[(rob["variant"] == vid) & (rob["test"] == "delay") & (rob["period"] == "val") &
                          (rob["side"] == "all") & (rob["case"] == "B")]
                nb = rob[(rob["variant"] == vid) & (rob["test"] == neighbour_label) & (rob["period"] == "val") &
                         (rob["side"] == "all") & (rob["case"] == "B")]
                g0 = r["val_mean_gross"]
                gd = dly["mean_gross_bps"].iloc[0] if len(dly) else np.nan
                r["delay_gross_ratio"] = gd / g0 if (np.isfinite(g0) and g0 > 0) else np.nan
                r["neighbour_net_B"] = nb["mean_net_bps"].iloc[0] if len(nb) else np.nan
                r["c4_robust"] = bool(np.nan_to_num(r["delay_gross_ratio"], nan=-1) >= 0.5 and
                                      np.nan_to_num(r["neighbour_net_B"], nan=-1) > 0)
            if len(cross):
                sgn = np.sign(r["val_mean_gross"])
                ok = []
                for T in ("SOXX", "SMH"):
                    cc = cross[(cross["variant"] == vid) & (cross["ticker"] == T) & (cross["period"] == "val") &
                               (cross["case"] == "B")]
                    g = cc["mean_gross_bps"].iloc[0] if len(cc) else np.nan
                    r[f"x_{T}_val_gross"] = g
                    ok.append(np.isfinite(g) and np.sign(g) == sgn and sgn != 0)
                r["c5_cross_same_sign"] = bool(all(ok))
                for T in CROSS:
                    for per in ("pre", "dev", "val"):
                        cc = cross[(cross["variant"] == vid) & (cross["ticker"] == T) & (cross["period"] == per) &
                                   (cross["case"] == "B")]
                        r[f"x_{T}_{per}_gross"] = cc["mean_gross_bps"].iloc[0] if len(cc) else np.nan
            if extra_pre_checks:
                pre_ok = bool(np.nan_to_num(r["pre_mean_net_B"], nan=-1) > 0)
                sign_ok = True
                for per in ("pre", "dev"):
                    sg = np.sign(E.pick(summ, vid, per).get("mean_gross_bps", np.nan))
                    for T in ("SOXX", "SMH"):
                        g = r.get(f"x_{T}_{per}_gross", np.nan)
                        sign_ok &= bool(np.isfinite(g) and np.sign(g) == sg and sg != 0)
                r["x_pre_net_pos"] = pre_ok
                r["x_pre_dev_cross_sign"] = sign_ok
            rows.append(r)
        ver = pd.DataFrame(rows)
        ver.to_csv(self.out / "verdicts.csv", index=False, float_format="%.4f")
        self.log(f"done: {len(ver)} variants -> {self.out}")
        return ver
