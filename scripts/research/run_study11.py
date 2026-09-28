#!/usr/bin/env python3
"""Study 11: Bone Zone-like pullback into the EMA9/EMA21 band (REGISTRY.md, 6 variants)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = []  # (id, params, neighbour params)
for i, (ent, ex) in enumerate([(ent, ex) for ent in ("close", "stop") for ex in ("XT", "XS", "XSO")], start=1):
    prm = dict(entry=ent, exit_=ex)
    VARIANTS.append((f"S11-{i:02d}", prm, dict(prm, imp_k=2.0)))


def leg_kwargs(prm: dict) -> dict:
    """One position at a time, at most 3 signals a day; XSO runs as two paired legs."""
    return dict(legs=("A", "B") if prm["exit_"] == "XSO" else None, max_per_day=3)


def main() -> None:
    run = Runner("study11_bone_zone", stop_slippage=True, quote_periods=("val",))
    for vid, prm, nb in VARIANTS:
        run.log(f"{vid} {prm}")
        kw = leg_kwargs(prm)
        run.main_variant(vid, R.s11_bz_intents, quote=True, **kw, **prm)
        run.robustness(vid, "delay", R.s11_bz_intents, entry_delay=1, **kw, **prm)
        run.robustness(vid, "neighbour", R.s11_bz_intents, **kw, **nb)
        run.crosscheck(vid, R.s11_bz_intents, **kw, **prm)
    run.finish()


if __name__ == "__main__":
    main()
