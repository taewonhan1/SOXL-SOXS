#!/usr/bin/env python3
"""Study 2: opening burst continuation (REGISTRY.md, 16 variants, case Q for all)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = []
i = 0
for k in (2.0, 3.0):
    for hold in (1, 3):
        for filt in ("F0", "F1", "F2", "F3"):
            i += 1
            VARIANTS.append((f"S2-{i:02d}", k, hold, filt))


def main() -> None:
    run = Runner("study2_opening_burst")
    for vid, k, hold, filt in VARIANTS:
        run.log(f"{vid} k={k} hold={hold} filter={filt}")
        run.main_variant(vid, R.s2_intents, quote=True, k=k, hold=hold, filt=filt)
        run.robustness(vid, "delay", R.s2_intents, k=k, hold=hold, filt=filt, entry_delay=1)
        run.robustness(vid, "neighbour", R.s2_intents, k=k + 0.5, hold=hold, filt=filt)
        run.crosscheck(vid, R.s2_intents, k=k, hold=hold, filt=filt)
    run.finish(extra_pre_checks=True)


if __name__ == "__main__":
    main()
