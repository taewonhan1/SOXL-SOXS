#!/usr/bin/env python3
"""Study 6: failed-break fade at key levels (REGISTRY.md, 4 variants)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = [("S6-01", "PM", "T1"), ("S6-02", "PM", "T2"), ("S6-03", "PD", "T1"), ("S6-04", "PD", "T2")]


def main() -> None:
    run = Runner("study6_failed_break_fade")
    for vid, lv, tg in VARIANTS:
        run.log(f"{vid} level={lv} target={tg}")
        run.main_variant(vid, R.s6_intents, level=lv, target=tg)
        run.robustness(vid, "delay", R.s6_intents, level=lv, target=tg, entry_delay=1)
        run.robustness(vid, "neighbour", R.s6_intents, level=lv, target=tg, fail_window=15)
        run.crosscheck(vid, R.s6_intents, level=lv, target=tg)
    run.finish()


if __name__ == "__main__":
    main()
