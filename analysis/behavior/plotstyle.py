"""Matplotlib style: reference palette (light surface), thin marks, hairline grid."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
# categorical slots in fixed order; colour follows the entity
COL = {"SOXL": "#2a78d6", "SOXS": "#eb6834", "SOXX": "#1baf7a", "QQQ": "#4a3aa7",
       "NVDA": "#008300", "SMH": "#eda100", "TQQQ": "#e87ba4", "SQQQ": "#e34948"}
THEORY = "#52514e"


def setup():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.titlesize": 11, "axes.labelsize": 9, "xtick.color": MUTED, "ytick.color": MUTED,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.6, "grid.linestyle": "-", "axes.spines.top": False,
        "axes.spines.right": False, "lines.linewidth": 2.0, "legend.frameon": False,
        "legend.fontsize": 8, "font.family": "DejaVu Sans", "figure.dpi": 110,
    })


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
