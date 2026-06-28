"""Parsing helpers for EVA text fields.

This module has one responsibility: interpret structured text values from the
EVA dataset, especially the semicolon-separated crew field.
"""

from __future__ import annotations  # Keeps type annotations consistent.

import pandas as pd  # Used because one parser method adds a dataframe column.

from .columns import COLUMNS  # Shared schema names avoid duplicated string literals.


class CrewParser:
    """Parse the semicolon-separated crew field used in the EVA dataset."""

    @staticmethod  # Parsing one text value does not require instance state.
    def crew_members(crew: str) -> list[str]:
        """Return a clean list of astronaut names from one crew string."""
        return [  # A list comprehension makes the transformation explicit and compact.
            member.strip()  # Remove spaces around each astronaut name.
            for member in str(crew).split(";")  # Split the source field wherever semicolons appear.
            if member.strip()  # Ignore blank entries, including a trailing semicolon.
        ]

    def crew_size(self, crew: str) -> int | None:
        """Return crew size, or None when no crew members can be parsed."""
        members = self.crew_members(crew)  # Reuse the parsing logic rather than duplicating it.
        return len(members) if members else None  # None preserves the original idea that blank crew has no size.

    def add_crew_size_column(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of data with a crew_size column added."""
        result = data.copy()  # Avoid hidden mutation of caller-owned dataframes.
        result[COLUMNS.crew_size] = result[COLUMNS.crew].map(  # Apply crew_size to every row's crew field.
            self.crew_size  # Reuse the named method for clearer testing.
        )
        return result  # Return the enriched dataframe.
