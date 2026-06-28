"""readers.py — read source data into a dataframe, behind an abstraction.

WHY THIS FILE EXISTS
The pipeline must not care whether data arrives from JSON, a CSV, or a database.
We express the *capability* ("can produce a dataframe") as a tiny contract and
provide one concrete implementation for JSON. A new source is a new class; the
pipeline never changes.

SOLID: Dependency Inversion (callers depend on the contract), Open/Closed (add
readers without editing existing ones), Interface Segregation (one-method
contract), Liskov (any reader substitutes for any other).
"""

from __future__ import annotations

# `Protocol` defines a contract by SHAPE, not by inheritance: any class that has
# a matching `read()` method qualifies as a DataFrameReader, even if it never
# names or subclasses this Protocol.
# WHY structural typing: it decouples implementations from the contract — a
# third party's reader class works with our pipeline without importing our code.
# `runtime_checkable` additionally permits isinstance(x, DataFrameReader) checks
# at runtime (otherwise Protocols are a static-analysis-only concept).
from typing import Protocol, runtime_checkable

import pandas as pd  # the dataframe library; every reader returns a DataFrame


@runtime_checkable
class DataFrameReader(Protocol):
    """The contract: 'something that can produce a dataframe of EVA records'."""

    # One method, declared but not implemented. The `...` (the Ellipsis object)
    # is a legal, do-nothing placeholder body — a Protocol describes *what* a
    # method looks like, not *how* it works.
    # WHY exactly one method: Interface Segregation. Code that holds a reader is
    # never forced to depend on anything beyond `read()`.
    def read(self) -> pd.DataFrame:
        ...


class JsonEvaReader:
    """Concrete reader: pulls raw EVA records from a JSON file.

    Note it does NOT inherit from DataFrameReader — thanks to structural typing
    it satisfies the contract simply by having a matching `read()`.

    It has ONE responsibility: I/O and parsing. It deliberately does not clean
    or enrich the data; those are pure functions in transforms.py. Keeping the
    jobs apart keeps this class small and lets the cleaning logic be tested
    without ever touching a file. (SRP)
    """

    # The `*` makes every parameter after it KEYWORD-ONLY: callers must write
    # `encoding="utf-8"`, not pass a bare positional value.
    # WHY: a call like `JsonEvaReader(path, "date", "utf-8")` is a riddle;
    # `JsonEvaReader(path, encoding="utf-8")` reads itself. It also means we can
    # reorder or add options later without breaking positional callers.
    def __init__(
        self,
        path: str,
        *,
        date_column: str = "date",
        encoding: str = "ascii",
    ) -> None:
        # A single leading underscore is the Python convention for "internal —
        # not part of the public surface". WHY: how this reader locates and
        # decodes its file is an implementation detail; callers use `read()`.
        self._path = path
        self._date_column = date_column
        self._encoding = encoding

    def read(self) -> pd.DataFrame:
        # The program's ONLY hard dependency on "JSON, via pandas" is isolated
        # in this one method, behind the contract above.
        # HOW: `pd.read_json` loads the file; `convert_dates=[...]` parses the
        # named column from strings into real timestamps as it reads (so sorting
        # and plotting by date work correctly downstream); `encoding` comes from
        # config rather than being fixed in the code.
        # WHY return raw, uncleaned rows: cleaning is a separate concern. This
        # method's single job is "get the bytes into a dataframe".
        return pd.read_json(
            self._path,
            convert_dates=[self._date_column],
            encoding=self._encoding,
        )
