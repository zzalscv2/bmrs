"""Small interfaces used to decouple the workflow from concrete classes.

This module supports the Dependency Inversion Principle. The high-level workflow
can depend on these protocols rather than directly depending on pd.read_json,
DataFrame.to_csv or Matplotlib plotting code.
"""

from __future__ import annotations  # Enables postponed evaluation of annotations.

from pathlib import Path  # Used in protocol method signatures for file locations.
from typing import Protocol  # Defines structural interfaces without inheritance-heavy design.

import pandas as pd  # DataFrame appears in the public method signatures of these protocols.


class DataReader(Protocol):
    """Minimal interface for loading tabular data.

    Why small: the Interface Segregation Principle says clients should not depend
    on methods they do not use. The workflow only needs read(), so the interface
    only exposes read().
    """

    def read(self, source: Path) -> pd.DataFrame:
        """Return a dataframe loaded from source."""


class DataWriter(Protocol):
    """Minimal interface for saving tabular data.

    A CSV writer, database writer or Parquet writer could satisfy this protocol
    without changing the workflow.
    """

    def write(self, data: pd.DataFrame, destination: Path) -> None:
        """Persist data to destination."""


class DataValidator(Protocol):
    """Minimal interface for checking dataframe validity."""

    def validate(self, data: pd.DataFrame) -> None:
        """Raise an exception if data is not valid for this analysis."""
