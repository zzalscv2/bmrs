"""Cleaning logic for EVA dataframes.

This module has one responsibility: prepare raw but valid data for analysis. It
keeps cleaning separate from file input, output and plotting.
"""

from __future__ import annotations  # Supports modern type annotations.

from collections.abc import Sequence  # Allows flexible sequences of required non-null columns.

import pandas as pd  # Pandas provides dataframe operations such as dropna and to_datetime.
from pandas.api.types import is_datetime64_any_dtype  # Used to check whether date parsing is already complete.

from .columns import COLUMNS  # Shared column names prevent repeated literals.


class EvaDataCleaner:
    """Clean raw EVA data without mutating the caller's dataframe.

    Why copy data: Pandas operations can mutate dataframes. Copying protects the
    caller from hidden side effects, which improves analysability and testability.
    """

    def __init__(self, required_non_null_columns: Sequence[str] | None = None):
        self.required_non_null_columns = tuple(  # Store as tuple to make cleaner configuration stable.
            required_non_null_columns  # Use custom rules if the caller supplies them.
            or (COLUMNS.date, COLUMNS.duration, COLUMNS.crew)  # Default rules needed for this analysis.
        )

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned copy of the EVA dataframe."""
        cleaned = data.copy()  # Avoid modifying the dataframe owned by the caller.
        cleaned = cleaned.dropna(  # Remove rows that cannot support the required outputs.
            axis=0,  # axis=0 means rows are removed rather than columns.
            subset=list(self.required_non_null_columns),  # Only key analysis columns are checked for nulls.
        )
        cleaned[COLUMNS.eva] = cleaned[COLUMNS.eva].astype(float)  # Preserve original behaviour: EVA IDs become floats.

        if not is_datetime64_any_dtype(cleaned[COLUMNS.date]):  # Avoid reparsing if the reader already parsed dates.
            cleaned[COLUMNS.date] = pd.to_datetime(  # Convert date text into datetime values for sorting/plotting.
                cleaned[COLUMNS.date],  # Source date column.
                errors="coerce",  # Invalid dates become NaT rather than immediately crashing.
            )
            cleaned = cleaned.dropna(axis=0, subset=[COLUMNS.date])  # Remove rows whose dates could not be parsed.

        return cleaned.reset_index(drop=True)  # Return tidy row numbering after rows have been removed.
