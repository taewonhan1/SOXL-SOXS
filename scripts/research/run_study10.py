#!/usr/bin/env python3
"""Study 10: Hitchhiker-like opening drive -> consolidation -> breakout (REGISTRY.md, 12 variants)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = []  # (id, params, neighbour params)
for i, (we, ent, ex) in enumerate([(we, ent, ex) for we in (29, 44, 59) for ent in ("stop", "close")
                                   for ex in ("X2R", "XSO")], start=1):
    prm = dict(window_end=we, entry=ent, exit_=ex)
    VARIANTS.append((f"S10-{i:02d}", prm, dict(prm, drive_k=2.5)))


def leg_kwargs(prm: dict) -> dict:
    """First setup of the day only; XSO runs as two paired legs."""
    return dict(legs=("A", "B") if prm["exit_"] == "XSO" else None, max_per_day=1)


def main() -> None:
    run = Runner("study10_hitchhiker", stop_slippage=True, quote_periods=("val",))
    for vid, prm, nb in VARIANTS:
        run.log(f"{vid} {prm}")
        kw = leg_kwargs(prm)
        run.main_variant(vid, R.s10_hh_intents, quote=True, **kw, **prm)
        run.robustness(vid, "delay", R.s10_hh_intents, entry_delay=1, **kw, **prm)
        run.robustness(vid, "neighbour", R.s10_hh_intents, **kw, **nb)
        run.crosscheck(vid, R.s10_hh_intents, **kw, **prm)
    run.finish()


if __name__ == "__main__":
    main()
