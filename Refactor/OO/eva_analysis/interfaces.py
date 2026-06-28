"""Abstract collaborator contracts (the stable seams of the program).

Reason to change: only when the *shape* of a collaboration changes — which
should be rare. Concrete implementations live in their own modules and depend
on these abstractions, never the other way round (Dependency Inversion).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Reporter(ABC):
    """A sink for human-readable progress messages."""

    @abstractmethod
    def report(self, message: str) -> None:
        """Emit a progress ``message``."""


class DurationConverter(ABC):
    """Converts a textual duration into a number of hours."""

    @abstractmethod
    def to_hours(self, duration: str) -> float:
        """Return ``duration`` expressed as a float number of hours."""


class CrewSizeCalculator(ABC):
    """Counts the members described by a crew text field."""

    @abstractmethod
    def size(self, crew: str) -> int | None:
        """Return the crew size, or ``None`` when the entry is empty."""


class DataSource(ABC):
    """A source that can produce a DataFrame of EVA records."""

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """Read and return the source data as a DataFrame."""


class DataSink(ABC):
    """A destination that can persist a DataFrame."""

    @abstractmethod
    def write(self, df: pd.DataFrame, destination: str) -> None:
        """Persist ``df`` to ``destination``."""


class DataTransformer(ABC):
    """A transformation from one DataFrame to another."""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a transformed copy of ``df``."""


class DurationSummariser(ABC):
    """An analysis that reduces EVA records to a per-subject summary."""

    @abstractmethod
    def summarise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a summary DataFrame derived from ``df``."""


class Plotter(ABC):
    """A renderer that turns a DataFrame into a saved figure."""

    @abstractmethod
    def plot(self, df: pd.DataFrame, destination: str) -> None:
        """Render ``df`` and save the figure to ``destination``."""
