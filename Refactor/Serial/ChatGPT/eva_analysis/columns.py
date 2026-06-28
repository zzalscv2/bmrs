"""Column-name definitions for the EVA analysis package.

This module has one responsibility: define the dataframe schema names used by
other modules. Keeping these names here avoids repeated string literals such as
"duration" or "crew" across the codebase.
"""

from __future__ import annotations  # Allows modern type hints to work consistently across supported Python versions.

from dataclasses import dataclass  # Used to define a small immutable schema object with less boilerplate.
from typing import Final  # Marks module constants as values that should not be reassigned.


@dataclass(frozen=True)  # frozen=True prevents accidental runtime changes to shared column names.
class EvaColumns:
    """Names of columns used throughout the EVA analysis pipeline.

    Why this exists: if the input dataset changes a column name, the change can
    start here rather than being hunted down across many functions. That improves
    ISO/IEC 25010 modifiability and analysability.
    """

    eva: str = "eva"  # Source column containing the EVA identifier/number.
    date: str = "date"  # Source column containing the EVA date; used for chronological plotting.
    crew: str = "crew"  # Source column containing semicolon-separated astronaut names.
    duration: str = "duration"  # Source column containing text durations in HH:MM form.
    duration_hours: str = "duration_hours"  # Derived numeric column used for calculations.
    cumulative_time: str = "cumulative_time"  # Derived running total used by the graph.
    astronaut: str = "astronaut"  # Derived column used after exploding crew into individual rows.
    crew_size: str = "crew_size"  # Derived column for number of crew members on an EVA.


COLUMNS: Final = EvaColumns()  # Single shared schema object imported by the rest of the package.

REQUIRED_INPUT_COLUMNS: Final[tuple[str, ...]] = (  # Required fields are centralised for validation.
    COLUMNS.eva,  # The EVA identifier must exist because it is part of the core dataset.
    COLUMNS.date,  # Dates must exist because chronological analysis depends on them.
    COLUMNS.crew,  # Crew must exist because astronaut-level summaries depend on it.
    COLUMNS.duration,  # Duration must exist because all time-based outputs depend on it.
)
