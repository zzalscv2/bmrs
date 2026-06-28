"""cli.py — command-line entry point and COMPOSITION ROOT.

WHY THIS FILE EXISTS
This is the single place that chooses concrete collaborators (a JSON reader, a
CSV writer) and binds them to the pipeline. Concentrating those choices here is
what keeps every other module free of format decisions: the knowledge "this run
uses JSON in and CSV out" exists in exactly one spot.

Run:  python -m eva_analysis.cli [input_file] [eva_csv_file]
"""

from __future__ import annotations

import argparse  # standard library command-line argument parser
import logging
import sys        # gives access to sys.argv, the raw command-line arguments

from .config import AnalysisConfig
from .pipeline import run_analysis
# NOTE: here we import the CONCRETE classes (not the Protocols), because this is
# the layer whose job is to pick concretions. Everything below the composition
# root imported only the abstractions.
from .readers import JsonEvaReader
from .writers import CsvDataFrameWriter

logger = logging.getLogger(__name__)

# Default paths as module-level constants (UPPER_CASE by convention).
# WHY constants: the defaults appear in two places (the argparse help text and
# the config construction); naming them once prevents the two drifting apart.
DEFAULT_INPUT_FILE = "data/eva-data.json"
DEFAULT_EVA_CSV_FILE = "results/eva-data.csv"
DEFAULT_ASTRONAUT_CSV_FILE = "results/duration_by_astronaut.csv"
DEFAULT_GRAPH_FILE = "results/cumulative_eva_graph.png"


def build_config(argv: list[str] | None = None) -> AnalysisConfig:
    """Parse command-line arguments into an immutable AnalysisConfig.

    Separated from main() so the parsing logic can be tested on a list of fake
    arguments without actually running the analysis. `argv=None` lets argparse
    fall back to the real command line when called for real.
    """
    # Create the parser with a human-readable description (shown in --help).
    parser = argparse.ArgumentParser(description="Analyse NASA EVA (spacewalk) data.")
    # A POSITIONAL argument that is OPTIONAL. HOW: `nargs="?"` means "zero or one";
    # with a `default`, omitting it falls back to the default path. WHY: the
    # script is convenient to run bare (`python -m eva_analysis.cli`) yet still
    # accepts a custom path.
    parser.add_argument(
        "input_file",
        nargs="?",
        default=DEFAULT_INPUT_FILE,
        help=f"Source JSON file (default: {DEFAULT_INPUT_FILE}).",
    )
    parser.add_argument(
        "eva_csv_file",
        nargs="?",
        default=DEFAULT_EVA_CSV_FILE,
        help=f"Cleaned EVA CSV output (default: {DEFAULT_EVA_CSV_FILE}).",
    )
    # An OPTIONAL flag (note the leading `--`). This is where the original's
    # buried `encoding='ascii'` becomes a visible, documented choice.
    parser.add_argument(
        "--input-encoding",
        default="ascii",
        help=(
            "Encoding for the source file. The original hard-coded 'ascii', "
            "which works on the bundled file (non-ASCII chars are stored as "
            "ASCII escape sequences) but is a fragile assumption; 'utf-8' is "
            "the safe choice. Default kept as 'ascii' to preserve behaviour."
        ),
    )
    # Parse the provided list (or the real command line if argv is None).
    args = parser.parse_args(argv)

    # Build the immutable config from the parsed values. argparse turns
    # `--input-encoding` into the attribute `input_encoding` (dash → underscore).
    return AnalysisConfig(
        input_file=args.input_file,
        eva_csv_file=args.eva_csv_file,
        astronaut_csv_file=DEFAULT_ASTRONAUT_CSV_FILE,
        graph_file=DEFAULT_GRAPH_FILE,
        input_encoding=args.input_encoding,
    )


def main(argv: list[str] | None = None) -> None:
    """Build the concrete collaborators and run the pipeline — the wiring."""
    # Configure where log messages go and how they look. Done once, at the entry
    # point, because choosing the logging policy is the APPLICATION's job, not a
    # library's. INFO level shows the pipeline's progress messages.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = build_config(argv)

    # THE COMPOSITION ROOT: pick the concrete reader and writer, configured from
    # `config`. This is the only code that knows the formats. Swap these two
    # lines (e.g. for a ParquetWriter) and nothing else in the package changes.
    reader = JsonEvaReader(
        config.input_file,
        date_column=config.date_column,
        encoding=config.input_encoding,
    )
    writer = CsvDataFrameWriter(encoding=config.output_encoding)

    # Hand the abstractions to the pipeline and run.
    run_analysis(config, reader, writer)


# `if __name__ == "__main__":` is True only when this file is run directly
# (`python -m eva_analysis.cli`), and False when it is imported by another module
# or a test. WHY: it lets the file double as both an importable module and a
# runnable script without executing the pipeline on import. `sys.argv[1:]` passes
# the real arguments (dropping argv[0], the program name).
if __name__ == "__main__":
    main(sys.argv[1:])
