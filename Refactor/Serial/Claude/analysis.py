"""analysis.py — derive results from cleaned data (still no I/O, no plotting).

WHY THIS FILE EXISTS
These functions compute the two headline results — total hours per astronaut,
and the cumulative-time series — and RETURN dataframes. They never draw, save or
print. Keeping computation separate from presentation means the numbers can be
asserted on in a test with no plotting backend, and the same numbers can feed a
different chart or report later.

SOLID: Single Responsibility — one result per function.
"""

from __future__ import annotations

import pandas as pd

# We reuse the duration parser from transforms rather than re-deriving hours.
# WHY a relative import (`.transforms`): it ties this module to its sibling
# inside the same package and makes the dependency explicit and one-directional
# (analysis depends on transforms, never the reverse).
from .transforms import add_duration_hours


def total_duration_by_astronaut(df: pd.DataFrame) -> pd.DataFrame:
    """Total spacewalk hours per individual astronaut.

    Returns a TIDY frame with `crew` as a real column (not the index). The
    original returned it as the index and then wrote with index=False, which
    silently DROPPED the names — the summary file held only durations. Returning
    a column is both better practice and what lets one index=False writer
    produce a correct file.
    """
    # Take only the two columns we need, and copy. HOW: `.loc[:, [cols]]` selects
    # all rows (`:`) and the listed columns. WHY copy: we are about to overwrite
    # the crew column, and we must not mutate the caller's frame.
    subset = df.loc[:, ["crew", "duration"]].copy()
    # Turn each crew STRING into a LIST of names, with blanks removed.
    # HOW, in three parts:
    #   .str.split(";")  → "A;B;" becomes ["A", "B", ""] for every row
    #   .apply(lambda names: [...])  → runs a small filter on each list
    #   [name for name in names if name.strip()] → keeps only non-blank names,
    #     discarding the empty tail element left by the trailing ";".
    # WHY this approach (vs count_crew): filtering blanks explicitly is robust to
    # the ";;" case that fools count_crew — hence the two disagree, by design.
    subset["crew"] = (
        subset["crew"]
        .str.split(";")
        .apply(lambda names: [name for name in names if name.strip()])
    )
    # `.explode("crew")` turns each list into MULTIPLE rows — one per name —
    # duplicating that row's duration onto each. So a two-person EVA becomes two
    # rows. WHY: we want a per-PERSON tally, so each person must be their own row.
    subset = subset.explode("crew")
    # Add the numeric hours column (reusing the shared parser).
    subset = add_duration_hours(subset)
    # Drop the now-redundant text duration; we keep only the numeric hours.
    # `axis=1` means "drop a COLUMN" (axis=0 would mean a row).
    subset = subset.drop("duration", axis=1)
    # Group all rows belonging to the same person and SUM their hours.
    # HOW: `groupby("crew").sum()` collapses each name to one total row.
    # WHY `as_index=False`: it keeps `crew` as an ordinary column instead of
    # making it the index — the whole point of the "tidy output" fix above.
    return subset.groupby("crew", as_index=False).sum()


def cumulative_time_in_space(
    df: pd.DataFrame,
    *,
    date_column: str = "date",
) -> pd.DataFrame:
    """Return the data sorted by date with a running cumulative-hours column.

    In the original, this sort + cumulative-sum was buried INSIDE the plotting
    function. Pulling it here makes the headline series a value you can test
    directly, separate from any chart.
    """
    # Sort chronologically so the running total accumulates in time order.
    # `sort_values` returns a NEW, sorted frame (we did not pass inplace=True),
    # preserving the no-mutation contract.
    ordered = df.sort_values(date_column)
    # Add the per-row numeric hours (shared parser again).
    ordered = add_duration_hours(ordered)
    # `.cumsum()` produces a running total: row N holds the sum of rows 0..N.
    # WHY: that is exactly "total time in space to DATE" — the y-axis of the plot.
    ordered["cumulative_time"] = ordered["duration_hours"].cumsum()
    return ordered
