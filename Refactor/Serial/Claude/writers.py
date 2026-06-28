"""writers.py — persist a dataframe to a destination, behind an abstraction.

WHY THIS FILE EXISTS
The mirror image of readers.py. The pipeline depends on the *capability* "can
write a dataframe somewhere", not on CSV specifically. A Parquet or Excel writer
would drop in as a new class with no change to the pipeline.

SOLID: Dependency Inversion, Open/Closed, Interface Segregation, Liskov.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class DataFrameWriter(Protocol):
    """The contract: 'something that can persist a dataframe to a destination'."""

    # Two parameters: the data, and where to put it. The destination is passed
    # IN (not stored on the writer) so a single writer instance can be reused
    # for several files — which is exactly what the pipeline does (it writes the
    # full table and the summary with the same writer).
    def write(self, df: pd.DataFrame, destination: str) -> None:
        ...


class CsvDataFrameWriter:
    """Concrete writer: writes a dataframe to a CSV file."""

    # `encoding` and `index` are captured once at construction as POLICY for
    # this writer ("always UTF-8, never write the index"), separate from the
    # per-call destination. WHY keyword-only (`*`): see the reader — it stops
    # silent positional mistakes.
    # `index=False` means the dataframe's row index is NOT written as a column.
    # WHY default False: for a normal table the index is just 0,1,2… and adds a
    # meaningless column. (The analysis functions deliberately return their key
    # as a real column so this default does not lose information — that is what
    # fixed the original's "lost astronaut names" bug.)
    def __init__(self, *, encoding: str = "utf-8", index: bool = False) -> None:
        self._encoding = encoding
        self._index = index

    def write(self, df: pd.DataFrame, destination: str) -> None:
        # The single concrete dependency on "CSV, via pandas" lives here.
        # HOW: `df.to_csv` serialises the frame; the stored policy supplies
        # `index` and `encoding`; the caller supplies `destination`.
        # Returns None — its effect is the side effect of a file being written.
        df.to_csv(destination, index=self._index, encoding=self._encoding)
