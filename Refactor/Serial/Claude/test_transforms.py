"""test_transforms.py — unit tests over the pure functions.

WHY THIS FILE EXISTS (and the course point it makes)
Once logic is split into pure functions, a test is just "call it, assert on the
result" — no temp files, no plotting backend, no mocks. The refactor made
correctness CHEAP TO CHECK. It did not make the code correct: two tests below
pin the bugs that good structure surfaced but did not fix.

Run:  python -m pytest -v
"""

from __future__ import annotations

import pandas as pd
# `pytest` is the test framework. WHY it: tests are plain functions named
# test_*, discovered automatically; failures are reported with rich diffs; and
# it provides helpers like `raises` and `xfail` used below.
import pytest

# Import the units under test by name. Tests import from the package exactly as
# any other caller would — exercising the real public surface.
from eva_analysis.transforms import (
    add_duration_hours,
    count_crew,
    parse_duration_to_hours,
)
from eva_analysis.analysis import total_duration_by_astronaut


# --- parse_duration_to_hours ------------------------------------------------

def test_parse_duration_simple():
    # The whole test: one call, one assert. "1:30" is one and a half hours.
    # If the function returns anything else, pytest shows expected vs actual.
    assert parse_duration_to_hours("1:30") == 1.5


def test_parse_duration_whole_hours():
    # A second example guards the zero-minutes path (minutes/60 == 0).
    assert parse_duration_to_hours("2:00") == 2.0


def test_parse_duration_is_fragile_on_seconds():
    # This test ASSERTS THE BUG, on purpose. `pytest.raises(ValueError)` passes
    # only if the code inside the block raises that error.
    # WHY write a test that the buggy behaviour satisfies: it documents and locks
    # the current limitation so it cannot regress silently, and marks the exact
    # spot where a future fix must change the expectation.
    with pytest.raises(ValueError):
        parse_duration_to_hours("1:23:45")


# --- add_duration_hours -----------------------------------------------------

def test_add_duration_hours_adds_numeric_column():
    # Build a tiny in-memory dataframe — no file needed, which is the payoff of
    # the function being pure.
    df = pd.DataFrame({"duration": ["0:30", "1:00"]})
    result = add_duration_hours(df)
    # Check the new column's values...
    assert list(result["duration_hours"]) == [0.5, 1.0]
    # ...that the original column is retained...
    assert "duration" in result.columns
    # ...and crucially that the INPUT was not mutated (purity guarantee).
    assert "duration_hours" not in df.columns


# --- count_crew -------------------------------------------------------------

def test_count_crew_single_member():
    # "Ed White;" → 1. Confirms the trailing-";" handling for the simple case.
    assert count_crew("Ed White;") == 1


def test_count_crew_two_members():
    assert count_crew("Neil Armstrong;Buzz Aldrin;") == 2


def test_count_crew_blank_returns_none():
    # A whitespace-only entry means "no crew here" → None (not 0).
    assert count_crew("   ") is None


# `@pytest.mark.xfail` marks a test as EXPECTED TO FAIL. HOW it reports: a failure
# shows as "xfail" (expected) and keeps the suite green; if it ever PASSES it
# shows as "xpass", flagging that the bug was fixed and the marker should go.
# WHY use it here: the ";;" miscount is a known, deliberately-unfixed defect; this
# keeps it visible and tracked without breaking the build.
@pytest.mark.xfail(reason="PRESERVED DEFECT: trailing ';;' is miscounted as an extra member")
def test_count_crew_double_semicolon_should_not_overcount():
    # The real data contains "Harrison Schmidt;Eugene Cernan;;" (Apollo 17).
    # The correct answer is 2; count_crew returns 3. The assertion below is the
    # DESIRED behaviour, so it currently fails — exactly what xfail expects.
    assert count_crew("Harrison Schmidt;Eugene Cernan;;") == 2


# --- total_duration_by_astronaut -------------------------------------------

def test_summary_returns_crew_as_column_not_index():
    # Two EVAs; "Anna" appears in both, so her total should be 1.0 + 0.5 = 1.5.
    df = pd.DataFrame(
        {"crew": ["Anna;Bob;", "Anna;"], "duration": ["1:00", "0:30"]}
    )
    result = total_duration_by_astronaut(df)
    # The regression guard for the "lost names" fix: crew must be a real COLUMN,
    # so an index=False writer keeps the names.
    assert "crew" in result.columns
    # Locate Anna's row and read her total. `.loc[mask, col]` selects by
    # condition; `.iloc[0]` takes the first matching value.
    anna = result.loc[result["crew"] == "Anna", "duration_hours"].iloc[0]
    assert anna == 1.5
