"""Pure EVA domain logic.

Reason to change: the rules for interpreting raw EVA fields (how a textual
duration maps to hours, how a crew string maps to a head count). These are
GRASP Information Experts with no I/O, pandas, or plotting dependencies. Each
implements an abstraction from ``interfaces`` so its consumers depend on the
contract, not this concrete class (Dependency Inversion).
"""

from __future__ import annotations

import re

from .interfaces import CrewSizeCalculator, DurationConverter


class TextDurationConverter(DurationConverter):
    """Converts a ``"HH:MM"`` text duration into hours."""

    def to_hours(self, duration: str) -> float:
        hours, minutes = duration.split(":")
        return int(hours) + int(minutes) / 60


class SemicolonCrewSizeCalculator(CrewSizeCalculator):
    """Counts crew members in a ``';'``-separated text field."""

    def size(self, crew: str) -> int | None:
        if crew.split() == []:
            return None
        return len(re.split(r";", crew)) - 1
