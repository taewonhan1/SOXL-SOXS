#!/usr/bin/env python3
"""Study 12: bull/bear-flag-like continuation (REGISTRY.md, 6 variants)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = []  # (id, params, neighbour params)
for i, (ent, ex) in enumerate([(ent, ex) for ent in ("stop", "close") for ex in ("XM", "X2R", "XSO")], start=1):
    prm = dict(entry=ent, exit_=ex)
    VARIANTS.append((f"S12-{i:02d}", prm, dict(prm, imp_k=2.0)))


def leg_kwargs(prm: dict) -> dict:
    """One position at a time, at most 3 signals a day; XSO runs as two paired legs."""
    return dict(legs=("A", "B") if prm["exit_"] == "XSO" else None, max_per_day=3)


def main() -> None:
    run = Runner("study12_flags", stop_slippage=True, quote_periods=("val",))
    for vid, prm, nb in VARIANTS:
        run.log(f"{vid} {prm}")
        kw = leg_kwargs(prm)
        run.main_variant(vid, R.s12_flag_intents, quote=True, **kw, **prm)
        run.robustness(vid, "delay", R.s12_flag_intents, entry_delay=1, **kw, **prm)
        run.robustness(vid, "neighbour", R.s12_flag_intents, **kw, **nb)
        run.crosscheck(vid, R.s12_flag_intents, **kw, **prm)
    run.finish()


if __name__ == "__main__":
    main()
