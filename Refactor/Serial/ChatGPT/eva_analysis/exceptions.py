"""Custom exceptions for predictable EVA analysis failures.

This module has one responsibility: define domain-specific error types. Custom
exceptions make failures easier to identify, catch, test and report clearly.
"""

from __future__ import annotations  # Keeps type-hint behaviour consistent with the rest of the package.


class EvaAnalysisError(Exception):
    """Base exception for expected failures in this application.

    Why this exists: the command-line entry point can catch this one parent type
    and handle known analysis failures without hiding unexpected programming
    errors such as AttributeError or TypeError.
    """


class InvalidEvaDataError(EvaAnalysisError):
    """Raised when the input dataframe is structurally invalid.

    Example causes include missing columns or an empty dataset. This improves
    analysability because callers get a precise cause instead of a later Pandas
    KeyError from somewhere deeper in the program.
    """


class DurationParseError(EvaAnalysisError):
    """Raised when a duration cannot be converted from HH:MM to hours.

    This separates data-format problems from general value errors, which makes
    testing and command-line reporting clearer.
    """
