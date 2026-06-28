"""Concrete data sinks.

Reason to change: how/where results are persisted (file formats, encodings).
"""

from __future__ import annotations

import pandas as pd

from .interfaces import DataSink, Reporter


class CsvDataSink(DataSink):
    """Writes a DataFrame to a CSV file."""

    def __init__(self, reporter: Reporter) -> None:
        self._reporter = reporter

    def write(self, df: pd.DataFrame, destination: str) -> None:
        self._reporter.report(f"Saving to CSV file {destination}")
        df.to_csv(destination, index=False, encoding="utf-8")
