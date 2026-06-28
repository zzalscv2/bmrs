"""Analysis operations for cleaned EVA data.

This module has one responsibility: create analytical outputs. It depends on
small converter/parser helpers rather than embedding all logic in one function.
"""

from __future__ import annotations  # Keeps type annotations consistent.

import pandas as pd  # Pandas provides grouping, exploding and sorting operations.

from .columns import COLUMNS  # Shared schema names avoid duplicated strings.
from .converters import DurationConverter  # Converts HH:MM text to numeric hours.
from .parsers import CrewParser  # Parses semicolon-separated crew fields.


class EvaSummaryAnalyser:
    """Create summary tables from cleaned EVA data."""

    def __init__(self, duration_converter: DurationConverter, crew_parser: CrewParser):
        self.duration_converter = duration_converter  # Injected dependency makes conversion replaceable/testable.
        self.crew_parser = crew_parser  # Injected dependency makes crew parsing replaceable/testable.

    def duration_by_astronaut(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return total EVA duration, in hours, grouped by astronaut."""
        subset = data.loc[:, [COLUMNS.crew, COLUMNS.duration]].copy()  # Work only with columns needed for this summary.
        subset[COLUMNS.astronaut] = subset[COLUMNS.crew].map(  # Convert each crew string into a list of names.
            self.crew_parser.crew_members  # Delegate parsing to the parser class to preserve SRP.
        )
        subset = subset.explode(COLUMNS.astronaut)  # Turn one row with many astronauts into many rows with one astronaut.
        subset = subset.dropna(axis=0, subset=[COLUMNS.astronaut])  # Remove rows where no astronaut was produced.
        subset = self.duration_converter.add_duration_hours(subset)  # Add numeric hours for aggregation.

        summary = (  # Build the summary in a readable Pandas method chain.
            subset.groupby(COLUMNS.astronaut, as_index=False)[COLUMNS.duration_hours]  # Group all rows for each astronaut.
            .sum()  # Add all EVA hours for each astronaut.
            .sort_values(COLUMNS.duration_hours, ascending=False)  # Put largest totals first for easier reading.
            .reset_index(drop=True)  # Produce clean row numbering after sorting.
        )
        return summary  # Return the table rather than writing it; output belongs to writer classes.
