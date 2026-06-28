"""Row/column-level DataFrame transformations.

Reason to change: how the EVA frame is cleaned or enriched before output. Each
transformer is substitutable for ``DataTransformer`` (Liskov) and returns a new
frame rather than mutating its input. Collaborators are typed by their
abstractions (Dependency Inversion).
"""

from __future__ import annotations

import pandas as pd

from .interfaces import (
    CrewSizeCalculator,
    DataTransformer,
    DurationConverter,
    Reporter,
)


class EvaDataCleaner(DataTransformer):
    """Coerces column types and drops rows that are unusable for analysis."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        df_copy["eva"] = df_copy["eva"].astype(float)
        df_copy.dropna(axis=0, subset=["duration", "date"], inplace=True)
        return df_copy


class CumulativeDurationTransformer(DataTransformer):
    """Sorts by date and adds ``duration_hours`` and ``cumulative_time``."""

    def __init__(self, duration_converter: DurationConverter) -> None:
        self._duration_converter = duration_converter

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        df_copy.sort_values("date", inplace=True)
        df_copy["duration_hours"] = df_copy["duration"].apply(
            self._duration_converter.to_hours
        )
        df_copy["cumulative_time"] = df_copy["duration_hours"].cumsum()
        return df_copy


class CrewSizeTransformer(DataTransformer):
    """Adds a ``crew_size`` column to the dataset.

    Mirrors the original module's crew-size helpers. It is a fully wired,
    substitutable transformer that can be added to the pipeline, but (like the
    original ``main``) it is left out of the default run to preserve identical
    output.
    """

    def __init__(
        self,
        crew_size_calculator: CrewSizeCalculator,
        reporter: Reporter,
    ) -> None:
        self._crew_size_calculator = crew_size_calculator
        self._reporter = reporter

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._reporter.report("Adding crew size variable (crew_size) to dataset")
        df_copy = df.copy()
        df_copy["crew_size"] = df_copy["crew"].apply(
            self._crew_size_calculator.size
        )
        return df_copy
