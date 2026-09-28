#!/usr/bin/env python3
"""Study 3: opening-range breakout (REGISTRY.md, 14 variants)."""
from runlib import Runner  # noqa: I001
from soxlab.research import rules as R

VARIANTS = [  # (id, params, neighbour params)
    ("S3-01", dict(design="A"), dict(design="A", or_len=20)),
    ("S3-02", dict(design="B"), dict(design="B", candle_len=10)),
    ("S3-03", dict(design="A", rvol_min=1.0), dict(design="A", rvol_min=1.25)),
    ("S3-04", dict(design="A", rvol_min=1.5), dict(design="A", rvol_min=1.75)),
    ("S3-05", dict(design="A", rvol_min=2.0), dict(design="A", rvol_min=2.25)),
    ("S3-06", dict(design="B", rvol_min=1.0), dict(design="B", rvol_min=1.25)),
    ("S3-07", dict(design="B", rvol_min=1.5), dict(design="B", rvol_min=1.75)),
    ("S3-08", dict(design="B", rvol_min=2.0), dict(design="B", rvol_min=2.25)),
    ("S3-09", dict(design="A", rvol_min=1.0, atr_stop=0.10), dict(design="A", rvol_min=1.0, atr_stop=0.15)),
    ("S3-10", dict(design="B", rvol_min=1.0, atr_stop=0.10), dict(design="B", rvol_min=1.0, atr_stop=0.15)),
    ("S3-11", dict(design="A", e1=True), dict(design="A", e1=True, band=(15, 85))),
    ("S3-12", dict(design="A", e2=True), dict(design="A", e2=True, e2_pct=50)),
    ("S3-13", dict(design="A", trail=1.0), dict(design="A", trail=1.5)),
    ("S3-14", dict(design="B", trail=1.0), dict(design="B", trail=1.5)),
]


def main() -> None:
    run = Runner("study3_opening_range_breakout")
    for vid, prm, nb in VARIANTS:
        run.log(f"{vid} {prm}")
        run.main_variant(vid, R.s3_intents, **prm)
        run.robustness(vid, "delay", R.s3_intents, entry_delay=1, **prm)
        run.robustness(vid, "neighbour", R.s3_intents, **nb)
        run.crosscheck(vid, R.s3_intents, **prm)
    run.finish()


if __name__ == "__main__":
    main()
