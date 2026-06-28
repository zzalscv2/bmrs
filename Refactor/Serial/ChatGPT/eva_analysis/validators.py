"""Validation rules for EVA dataframes.

This module has one responsibility: reject data that cannot be analysed safely.
It does not change values; transformation belongs in cleaners or converters.
"""

from __future__ import annotations  # Keeps type-hint behaviour consistent.

from collections.abc import Sequence  # Used for an immutable-friendly list of required columns.

import pandas as pd  # DataFrame is the object being validated.

from .columns import REQUIRED_INPUT_COLUMNS  # Centralised definition of mandatory schema fields.
from .exceptions import InvalidEvaDataError  # Domain-specific error for clear failure reporting.


class EvaSchemaValidator:
    """Validate dataframe structure before analysis begins.

    SRP: this class changes when schema requirements change. It should not change
    because file formats, plotting style or summary calculations change.
    """

    def __init__(self, required_columns: Sequence[str] = REQUIRED_INPUT_COLUMNS):
        self.required_columns = tuple(required_columns)  # Store as tuple to avoid accidental external mutation.

    def validate(self, data: pd.DataFrame) -> None:
        """Raise InvalidEvaDataError if required structure is missing."""
        missing_columns = [  # Build a precise list rather than failing on the first missing column.
            column  # The current required column being checked.
            for column in self.required_columns  # Iterate over the configured schema requirements.
            if column not in data.columns  # A column is missing if it is not in the dataframe header.
        ]
        if missing_columns:  # Any missing columns mean later analysis would be unreliable.
            raise InvalidEvaDataError(  # Raise a domain error rather than letting Pandas fail later.
                "Input data is missing required column(s): " + ", ".join(missing_columns)
            )

        if data.empty:  # An empty dataframe is structurally valid but useless for this analysis.
            raise InvalidEvaDataError("Input data contains no rows.")  # Provide a clear user-facing reason.
