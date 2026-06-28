"""Value conversion helpers for EVA data.

This module has one responsibility: convert domain values from one representation
to another. At present, it converts HH:MM duration text into decimal hours.
"""

from __future__ import annotations  # Keeps annotations consistent.

import pandas as pd  # Used because one method adds a converted column to a dataframe.

from .columns import COLUMNS  # Shared schema names avoid duplicated strings.
from .exceptions import DurationParseError  # Specific error type for invalid duration text.


class DurationConverter:
    """Convert EVA duration values from HH:MM text to decimal hours."""

    @staticmethod  # No instance state is needed to convert one value.
    def text_to_hours(duration: str) -> float:
        """Convert a duration such as '02:30' into 2.5 hours."""
        try:  # Parsing is isolated so format errors can be converted into a clearer domain exception.
            hours_text, minutes_text = str(duration).strip().split(  # Split into hour and minute parts.
                ":",  # HH:MM uses a colon separator.
                maxsplit=1,  # Only one split is expected; extra colons should not be silently accepted.
            )
            hours = int(hours_text)  # Convert the hour part into an integer for arithmetic.
            minutes = int(minutes_text)  # Convert the minute part into an integer for validation and arithmetic.
        except ValueError as exc:  # int() and split() both raise ValueError for malformed input.
            raise DurationParseError(  # Raise a domain-specific error with the original value included.
                f"Duration must use HH:MM format; received {duration!r}."
            ) from exc

        if hours < 0 or not 0 <= minutes < 60:  # Reject negative hours and impossible minute values.
            raise DurationParseError(  # Provide a precise reason rather than returning misleading results.
                f"Duration has invalid hour/minute values: {duration!r}."
            )

        return hours + minutes / 60  # Convert minutes to a fraction of an hour and add to whole hours.

    def add_duration_hours(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of data with a numeric duration_hours column added."""
        result = data.copy()  # Copy to avoid mutating caller-owned dataframes.
        result[COLUMNS.duration_hours] = result[COLUMNS.duration].map(  # Apply conversion to each duration value.
            self.text_to_hours  # Mapping a named method is easier to test and analyse than an inline lambda.
        )
        return result  # Return the enriched dataframe for downstream analysis.
