"""Output writers for EVA analysis results.

This module has one responsibility: persist dataframes. It knows about CSV output
but not about how the data was produced.
"""

from __future__ import annotations  # Keeps type hint behaviour consistent.

import logging  # Provides configurable runtime status messages.
from pathlib import Path  # Represents destinations in an OS-independent way.

import pandas as pd  # DataFrame is the data type being written.

LOGGER = logging.getLogger(__name__)  # Module logger identifies writer messages.


class CsvDataWriter:
    """Write dataframe output to CSV files.

    OCP: a new writer, such as ParquetDataWriter, can be added without editing
    the workflow as long as it has the same write(data, destination) behaviour.
    """

    def write(self, data: pd.DataFrame, destination: Path) -> None:
        """Save data to destination as UTF-8 CSV."""
        LOGGER.info("Writing CSV output: %s", destination)  # Exposes progress without coupling to print.
        destination.parent.mkdir(  # Ensure the results directory exists before writing.
            parents=True,  # Create missing parent directories recursively.
            exist_ok=True,  # Do not fail if the directory already exists.
        )
        data.to_csv(  # Delegate the actual CSV serialisation to Pandas.
            destination,  # File path supplied by the workflow configuration.
            index=False,  # Preserve original tutorial behaviour: no dataframe index column in the CSV.
            encoding="utf-8",  # UTF-8 is a safe default for output files.
        )
