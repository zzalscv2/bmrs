"""plotting.py — turn a computed series into a figure (and, separately, save it).

WHY THIS FILE EXISTS
`build_cumulative_figure` BUILDS a figure and returns it; `save_figure` WRITES a
figure to disk. Splitting "make the picture" from "store the picture" means each
is independently testable and a caller can display, embed, or save the same
figure without duplicating drawing code.

The original combined four jobs in one function: it computed the cumulative sum,
drew, saved, AND called plt.show(). The computation now lives in analysis.py; the
blocking show() is removed so the pipeline can run unattended.

SOLID: Single Responsibility.
"""

from __future__ import annotations

# Importing matplotlib and choosing a backend BEFORE importing pyplot.
import matplotlib

# `matplotlib.use("Agg")` selects the non-interactive "Agg" backend, which draws
# to image files and never opens a window.
# WHY here, and why first: the backend must be selected before pyplot is imported,
# and "Agg" makes this safe to run headless (a server, a CI job) where there is
# no display. This is the structural replacement for the original's plt.show().
matplotlib.use("Agg")
# These two imports MUST follow the backend selection, hence the
# `# noqa: E402` which tells linters this import is deliberately not at the top.
import matplotlib.pyplot as plt  # noqa: E402  (pyplot: the figure/axes API)
from matplotlib.figure import Figure  # noqa: E402  (the return type, for hints)


def build_cumulative_figure(
    df,
    *,
    date_column: str = "date",
    cumulative_column: str = "cumulative_time",
) -> Figure:
    """Build (but do not save or show) a cumulative-time line figure.

    The x/y column names are parameters with defaults, so the same drawing code
    could plot a differently named series without edits. The return type is a
    `Figure` object — the function hands the picture back rather than writing it.
    """
    # `plt.subplots()` creates a Figure (the whole canvas) and one Axes (the plot
    # area inside it), returned as a pair. WHY use explicit fig/ax objects rather
    # than the original's module-level `plt.plot(...)`: the global pyplot state
    # is implicit and easy to cross-contaminate between plots; holding our own
    # objects is clearer and testable.
    fig, ax = plt.subplots()
    # Draw the line. HOW: `ax.plot(x, y, fmt)` where the format string "ko-"
    # means black ("k"), circle markers ("o"), joined by a solid line ("-").
    ax.plot(df[date_column], df[cumulative_column], "ko-")
    # Axis labels — set on the Axes object we own (not via global pyplot).
    ax.set_xlabel("Year")
    ax.set_ylabel("Total time spent in space to date (hours)")
    # `tight_layout()` adjusts spacing so labels are not clipped.
    fig.tight_layout()
    # Return the finished figure for the caller to do with as they wish.
    return fig


def save_figure(fig: Figure, destination: str) -> None:
    """Save a figure to `destination`. One line, one job."""
    # `fig.savefig(path)` writes the image; the format is inferred from the
    # file extension (e.g. .png). Returns None — the effect is the written file.
    fig.savefig(destination)
