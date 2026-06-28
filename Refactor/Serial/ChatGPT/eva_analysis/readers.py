"""Input readers for EVA analysis data.

This module has one responsibility: read external data into Pandas dataframes.
It deliberately does not validate, clean, analyse or plot the data.
"""

from __future__ import annotations  # Keeps annotation behaviour consistent.

import logging  # Used instead of print so callers can configure output verbosity.
from pathlib import Path  # Used for robust filesystem path handling.

import pandas as pd  # Pandas performs the actual JSON-to-dataframe conversion.

from .columns import COLUMNS  # Centralised schema names avoid duplicated string literals.

LOGGER = logging.getLogger(__name__)  # Module-specific logger helps trace where messages come from.


class JsonEvaDataReader:
    """Read EVA records from a JSON file.

    SRP: this class changes if JSON input handling changes. It should not change
    because plotting, validation or summary rules change.
    """

    def read(self, source: Path) -> pd.DataFrame:
        """Load a JSON file as a dataframe.

        The date column is parsed at read time because JSON reading is the first
        place where text values become typed tabular data.
        """
        if not source.exists():  # Fail early with a clear error before Pandas emits a longer traceback.
            raise FileNotFoundError(f"Input file does not exist: {source}")  # Gives the missing path directly.

        LOGGER.info("Reading JSON input: %s", source)  # Logging supports analysability without hard-coded print calls.
        return pd.read_json(  # Return the raw dataframe; cleaning is intentionally delegated elsewhere.
            source,  # Path supplied by configuration or command-line arguments.
            convert_dates=[COLUMNS.date],  # Parse the known date column for chronological calculations.
            encoding="ascii",  # Matches the original tutorial dataset assumption.
        )
