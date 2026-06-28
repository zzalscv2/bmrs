"""config.py — run settings collected into one immutable object.

WHY THIS FILE EXISTS
Everything that varies between runs (file paths, encodings, column names) lives
here, so the rest of the code never hard-codes a literal. "Read a different
file" or "use a different encoding" becomes a *data* change, not a *code* change.

Maintainability: MODIFIABILITY (one place to change settings).
SOLID: Single Responsibility (configuration is its own concern).
"""

# `from __future__ import annotations` turns every type hint in this file into a
# plain string at runtime instead of evaluating it immediately.
# HOW: it is a parser directive, processed before the rest of the module.
# WHY: it lets us use modern hint syntax (like `str | None`) regardless of
# interpreter version, and avoids "name used in a hint before it is defined"
# errors. It has no runtime cost — the hints are never executed here.
from __future__ import annotations

# `dataclass` is a decorator that writes the repetitive parts of a data-holding
# class for us: __init__, __repr__ and __eq__.
# WHY: this class only carries values; hand-writing a constructor would be
# noise. Importing just what we use (not the whole module) keeps the namespace
# clean and the dependency explicit.
from dataclasses import dataclass


# The decorator is applied with `frozen=True`, which makes instances immutable:
# after construction, assigning to an attribute raises an error.
# WHY frozen: configuration must not drift mid-run. Freezing converts an
# accidental `config.input_file = ...` into an immediate, loud failure, and
# makes the object safe to share freely (it is hashable and cannot be mutated
# by one part of the program behind another's back).
@dataclass(frozen=True)
class AnalysisConfig:
    """All inputs the pipeline needs to run (see per-field comments)."""

    # These four fields have NO default value, so the caller is REQUIRED to
    # supply them. Each annotation (`: str`) both documents the expected type
    # and tells the dataclass to treat the name as a field.
    # WHY required: there is no safe universal default for "where is your data".
    # Forcing the caller to state it prevents silently reading or overwriting
    # the wrong file.
    input_file: str            # source JSON to read
    eva_csv_file: str          # destination for the cleaned full table
    astronaut_csv_file: str    # destination for the per-astronaut summary
    graph_file: str            # destination for the cumulative-time PNG

    # The next three fields DO have defaults (the `= ...`), making them
    # optional. In a dataclass, fields with defaults must come after fields
    # without them — which is why these sit at the bottom.
    # WHY defaults: they rarely change, so callers shouldn't be forced to pass
    # them, but they stay overridable for the cases that do.

    # Encoding used to READ the source file. The default "ascii" reproduces the
    # original script's behaviour exactly.
    # HOW it currently works: the bundled data file is pure ASCII on disk — its
    # accented characters are stored as ASCII escape sequences like \u00c2 — so
    # ascii decoding succeeds.
    # WHY it is still a smell: that is an unstated assumption. A source
    # re-exported with raw (non-escaped) UTF-8 bytes would fail to read. Because
    # the encoding is a *setting* now rather than a literal buried in a function,
    # correcting it is a one-line change: input_encoding="utf-8". (MODIFIABILITY)
    input_encoding: str = "ascii"

    # Encoding used to WRITE CSV output. "utf-8" is the safe, conventional
    # choice and the standard for text data interchange.
    output_encoding: str = "utf-8"

    # Name of the date column — the one parsed into timestamps on read and
    # sorted on before plotting. Parameterised rather than hard-coded so a
    # renamed column is handled by editing config, not the reader or analysis.
    date_column: str = "date"
