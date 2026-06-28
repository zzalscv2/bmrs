"""Concrete progress reporters.

Reason to change: how progress messages are surfaced (stdout, a logger, a GUI).
Isolating this here is what lets every other class stay silent and free of any
presentation concern — they depend only on the ``Reporter`` abstraction.
"""

from __future__ import annotations

from .interfaces import Reporter


class ConsoleReporter(Reporter):
    """Writes progress messages to standard output."""

    def report(self, message: str) -> None:
        print(message)


class NullReporter(Reporter):
    """Discards progress messages (useful in tests and library use)."""

    def report(self, message: str) -> None:
        pass
