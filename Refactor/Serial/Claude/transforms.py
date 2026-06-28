"""transforms.py — pure data transformations (data in, data out).

WHY THIS FILE EXISTS
Every function here takes a value and returns a value, with no file access, no
printing, and no shared global state. That single property buys three of the
maintainability qualities at once:
    * REUSABILITY  — callable from a notebook, a test, or another pipeline.
    * TESTABILITY  — a test is "call it, assert on the result"; no files/mocks.
    * ANALYSABILITY — one named job per function.

Behaviour is faithful to the original script. TWO correctness bugs are preserved
ON PURPOSE (the duration parser and the crew counter) to make the course's point
that a structural refactor improves *shape*, not *truth*. They are flagged below.
"""

from __future__ import annotations

import re  # regular-expression module, used by count_crew to split on ";"

import pandas as pd


def clean_eva_data(
    df: pd.DataFrame,
    *,
    required_columns: tuple[str, ...] = ("duration", "date"),
) -> pd.DataFrame:
    """Coerce the EVA id to a number and drop rows missing required fields.

    `required_columns` is a tuple with a default, made keyword-only, so the
    cleaning rule is configurable but callers usually need not think about it.
    A tuple (not a list) is used because the default is immutable — a classic
    guard against the "mutable default argument" trap.
    """
    # `.copy()` FIRST. WHY: every function here returns a NEW frame and never
    # edits the caller's. Without the copy, the later column assignment could
    # mutate the input in place and surprise whoever passed it in. Purity =
    # predictability.
    cleaned = df.copy()
    # Coerce the "eva" id column to float. HOW: `.astype(float)` converts the
    # whole column. WHY float not int: some rows have no EVA number, which pandas
    # represents as NaN — and NaN is a float, so the column cannot be a pure int.
    cleaned["eva"] = cleaned["eva"].astype(float)
    # Drop incomplete rows. HOW: `dropna(axis=0, subset=...)` removes any ROW
    # (axis=0) that has a missing value in ANY of the named columns. `list(...)`
    # converts our tuple because that is what the pandas argument expects.
    # WHY: a record with no duration or no date cannot be summed or plotted.
    # Note there is NO `inplace=True` here — unlike the original — which is what
    # makes the "return a copy, leave the input alone" guarantee hold.
    cleaned = cleaned.dropna(axis=0, subset=list(required_columns))
    return cleaned


def parse_duration_to_hours(duration: str) -> float:
    """Convert an "HH:MM" duration string into fractional hours.

    PRESERVED DEFECT (deliberate): this assumes the text is exactly "HH:MM".
    A value with seconds ("1:23:45"), an empty string, or a missing value will
    raise. As an isolated pure function the fragility is now a one-line test —
    which is the right place to specify and drive out a fix.
    """
    # Split the text on the colon into two pieces. HOW: `"2:07".split(":")`
    # gives the list `["2", "07"]`, which is unpacked into `hours` and
    # `minutes`. WHY this is fragile: if there are not EXACTLY two pieces (e.g.
    # "1:23:45" → three), the unpacking raises ValueError. That is the bug,
    # surfaced but intentionally left.
    hours, minutes = duration.split(":")
    # Convert each piece to an int and combine: whole hours plus minutes/60.
    # WHY `/ 60`: 7 minutes is 7/60 of an hour ≈ 0.1167. Integer division would
    # discard the fraction, so plain `/` (float division) is used on purpose.
    return int(hours) + int(minutes) / 60


def add_duration_hours(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a numeric `duration_hours` column added."""
    out = df.copy()  # copy-first, same purity contract as above
    # `.apply(fn)` runs `fn` once per value in the "duration" column and
    # collects the results into the new column.
    # WHY apply a named function (not a lambda): the parsing logic lives in ONE
    # tested place (`parse_duration_to_hours`); this line just maps it over the
    # column. Reuse, not duplication.
    out["duration_hours"] = out["duration"].apply(parse_duration_to_hours)
    return out


def count_crew(crew: str) -> int | None:
    """Count crew members in one ";"-delimited crew entry.

    Returns None for a blank entry. PRESERVED DEFECT (deliberate): an entry with
    a trailing empty field, e.g. "Harrison Schmidt;Eugene Cernan;;", is counted
    as 3 when the answer is 2. `total_duration_by_astronaut` splits crew a
    different way and does NOT share this bug — an inconsistency the refactor
    exposes but does not silently rewrite.
    """
    # `crew.split()` with no argument splits on ANY run of whitespace and drops
    # empties, so a string of only spaces becomes the empty list `[]`.
    # WHY: this is the original's way of detecting "no crew named here" → None.
    if crew.split() == []:
        return None
    # `re.split(r";", crew)` splits on every semicolon. For "Ed White;" that is
    # `["Ed White", ""]` (length 2), so subtracting 1 gives 1 — correct, because
    # the data always has a TRAILING ";" producing one empty tail element.
    # WHY it breaks on ";;": "...Cernan;;" yields an EXTRA empty element, so the
    # `- 1` no longer fully cancels the trailing blanks → an over-count. Bug kept.
    return len(re.split(r";", crew)) - 1


def add_crew_size(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a `crew_size` column added."""
    out = df.copy()
    # Map the (faithfully buggy) counter over the crew column. Same apply +
    # named-function pattern as add_duration_hours.
    out["crew_size"] = out["crew"].apply(count_crew)
    return out
