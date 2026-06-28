"""Concrete data sources.

Reason to change: how/where raw EVA data is read (file formats, encodings).
"""

from __future__ import annotations

import pandas as pd

from .interfaces import DataSource, Reporter


class JsonEvaDataSource(DataSource):
    """Reads raw EVA records from a JSON file."""

    def __init__(self, input_file: str, reporter: Reporter) -> None:
        self._input_file = input_file
        self._reporter = reporter

    def read(self) -> pd.DataFrame:
        self._reporter.report(f"Reading JSON file {self._input_file}")
        return pd.read_json(
            self._input_file, convert_dates=["date"], encoding="ascii"
        )
