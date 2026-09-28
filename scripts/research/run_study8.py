#!/usr/bin/env python3
"""Study 8 (exploratory, REGISTRY.md): short SOXL as the bearish leg for the four near-miss rules."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

RULES = [("S3-01", R.s3_intents, False, dict(design="A")),
         ("S3-13", R.s3_intents, False, dict(design="A", trail=1.0)),
         ("S4-02", R.s4_trades, True, dict(k=1.0, check="H")),
         ("S4-04", R.s4_trades, True, dict(k=1.5, check="H"))]


def main() -> None:
    run = Runner("study8_execution")
    for i, (rid, fn, is_tr, prm) in enumerate(RULES):
        vid = f"S8-{i + 1:02d}"
        run.log(f"{vid}: {rid} with short-SOXL bearish leg")
        run.main_variant(vid, fn, is_trades=is_tr, mode="switch_short", **prm)
    run.finish()


if __name__ == "__main__":
    main()
