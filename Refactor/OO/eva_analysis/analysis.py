"""Aggregation / analysis.

Reason to change: how EVA records are summarised into per-astronaut statistics.
Implements its own ``DurationSummariser`` contract rather than pretending to be
a row-wise ``DataTransformer`` (Interface Segregation).
"""

from __future__ import annotations

import pandas as pd

from .interfaces import DurationConverter, DurationSummariser


class AstronautDurationSummariser(DurationSummariser):
    """Summarises total EVA duration (in hours) per individual astronaut."""

    def __init__(self, duration_converter: DurationConverter) -> None:
        self._duration_converter = duration_converter

    def summarise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return total spacewalk hours per individual crew member.

        Args:
            df: The cleaned EVA dataframe.

        Returns:
            A dataframe with one row per crew member and columns
            ``crew`` and ``duration_hours``. ``crew`` is returned as a regular
            column (not the index) so it survives an index-free CSV export.
        """
        subset = df.loc[:, ["crew", "duration"]]
        # Split the crew into individuals, dropping the blank trailing split.
        subset.crew = subset.crew.str.split(";").apply(
            lambda names: [name for name in names if name.strip()]
        )
        subset = subset.explode("crew")
        subset["duration_hours"] = subset["duration"].apply(
            self._duration_converter.to_hours
        )
        subset = subset.drop("duration", axis=1)
        # reset_index keeps the crew names as a column rather than an index that
        # an index-free CSV write would silently discard.
        return subset.groupby("crew").sum().reset_index()
