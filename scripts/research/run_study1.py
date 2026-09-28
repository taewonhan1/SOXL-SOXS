#!/usr/bin/env python3
"""Study 1: late-day fade (REGISTRY.md, 12 variants)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = []
i = 0
for thr in (0.01, 0.02):
    for ex in ("E1", "E2", "E3"):
        for gate in (True, False):
            i += 1
            VARIANTS.append((f"S1-{i:02d}", thr, ex, gate))


def main() -> None:
    run = Runner("study1_late_day_fade")
    for vid, thr, ex, gate in VARIANTS:
        run.log(f"{vid} thr={thr} exit={ex} gate={gate}")
        run.main_variant(vid, R.s1_intents, thr=thr, gate=gate, exit_=ex, exec_mode="switch")
        run.robustness(vid, "delay", R.s1_intents, thr=thr, gate=gate, exit_=ex, exec_mode="switch", entry_delay=1)
        run.robustness(vid, "neighbour", R.s1_intents, thr=0.015, gate=gate, exit_=ex, exec_mode="switch")
        run.crosscheck(vid, R.s1_intents, thr=thr, gate=gate, exit_=ex, exec_mode="ls")
    run.finish(extra_pre_checks=True)


if __name__ == "__main__":
    main()
