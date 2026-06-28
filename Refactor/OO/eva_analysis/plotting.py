"""Concrete plotting.

Reason to change: how figures are rendered. This is the only module that
depends on matplotlib, so a switch to another charting library is contained
entirely here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from .interfaces import Plotter, Reporter


class CumulativeTimePlotter(Plotter):
    """Plots cumulative time spent in space over the years."""

    def __init__(self, reporter: Reporter) -> None:
        self._reporter = reporter

    def plot(self, df: pd.DataFrame, destination: str) -> None:
        self._reporter.report(
            f"Plotting cumulative spacewalk duration and saving to {destination}"
        )
        plt.plot(df["date"], df["cumulative_time"], "ko-")
        plt.xlabel("Year")
        plt.ylabel("Total time spent in space to date (hours)")
        plt.tight_layout()
        plt.savefig(destination)
        plt.show()
