"""Plot-building and plot-saving code for EVA analysis.

This module has one responsibility: prepare and save graph output. It does not
read files, validate schemas or write CSV summaries.
"""

from __future__ import annotations  # Keeps annotations consistent.

import logging  # Provides configurable progress reporting.
from pathlib import Path  # Used for graph output paths.

import matplotlib.pyplot as plt  # Matplotlib is isolated here so plotting dependencies do not spread everywhere.
import pandas as pd  # DataFrame is the input/output structure for plot data.

from .columns import COLUMNS  # Shared column names avoid duplicated strings.
from .converters import DurationConverter  # Used to convert text durations into numeric hours.

LOGGER = logging.getLogger(__name__)  # Module-specific logger for plotting messages.


class CumulativeEvaDataBuilder:
    """Build the dataframe required for cumulative EVA plotting."""

    def __init__(self, duration_converter: DurationConverter):
        self.duration_converter = duration_converter  # Injecting this dependency avoids hard-coding conversion details.

    def build(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return sorted data with duration_hours and cumulative_time columns."""
        plot_data = data.sort_values(COLUMNS.date).reset_index(drop=True)  # Sort a copy for chronological plotting.
        plot_data = self.duration_converter.add_duration_hours(plot_data)  # Add numeric hours without mutating input.
        plot_data[COLUMNS.cumulative_time] = plot_data[COLUMNS.duration_hours].cumsum()  # Running total over time.
        return plot_data  # Return plot-ready data so it can be tested without creating a PNG.


class CumulativeEvaPlotter:
    """Save a cumulative EVA duration plot."""

    def __init__(self, cumulative_data_builder: CumulativeEvaDataBuilder):
        self.cumulative_data_builder = cumulative_data_builder  # Data preparation is separated from rendering.

    def save(self, data: pd.DataFrame, destination: Path) -> None:
        """Create and save the cumulative EVA duration graph."""
        LOGGER.info("Writing graph output: %s", destination)  # Log the output destination for traceability.
        destination.parent.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists.

        plot_data = self.cumulative_data_builder.build(data)  # Prepare data through a testable collaborator.
        figure, axis = plt.subplots()  # Use the object-oriented Matplotlib API for clearer figure management.
        axis.plot(  # Draw the cumulative duration line.
            plot_data[COLUMNS.date],  # x-axis: EVA date.
            plot_data[COLUMNS.cumulative_time],  # y-axis: running total of EVA hours.
            "ko-",  # Preserve the original black-circle line style.
        )
        axis.set_xlabel("Year")  # Label the x-axis for readability.
        axis.set_ylabel("Total time spent in space to date (hours)")  # Label the y-axis with units.
        figure.tight_layout()  # Reduce clipping around labels.
        figure.savefig(destination)  # Write the PNG or other image format inferred from filename.
        plt.close(figure)  # Free resources and avoid leaking state between tests or repeated runs.
