"""Command-line interface for the EVA analysis package.

This module has one responsibility: convert command-line input into configuration
and run the application. It does not contain data-analysis logic.
"""

from __future__ import annotations  # Keeps annotation behaviour consistent.

import argparse  # Standard-library tool for command-line argument parsing.
import logging  # Standard-library logging used across the package.
from pathlib import Path  # Converts command-line path strings into path objects.

from .config import EvaAnalysisConfig  # Typed configuration returned by parse_args().
from .exceptions import EvaAnalysisError  # Parent error type for expected failures.
from .factory import build_workflow  # Assembles the default workflow dependencies.

LOGGER = logging.getLogger(__name__)  # Module logger for CLI-level error messages.


def parse_args() -> EvaAnalysisConfig:
    """Parse command-line arguments into a typed configuration object."""
    parser = argparse.ArgumentParser(  # Create a parser dedicated to the CLI boundary.
        description="Analyse NASA EVA data."  # Short help text shown with --help.
    )
    parser.add_argument(  # Optional positional input path preserves the original tutorial style.
        "input_file",  # Argument name.
        nargs="?",  # Makes the argument optional.
        default=EvaAnalysisConfig.input_file,  # Use the dataclass default when omitted.
    )
    parser.add_argument(  # Optional positional cleaned CSV output path.
        "cleaned_csv_file",  # Argument name.
        nargs="?",  # Makes the argument optional.
        default=EvaAnalysisConfig.cleaned_csv_file,  # Preserve the original default output location.
    )
    parser.add_argument(  # Named option for astronaut summary output.
        "--astronaut-summary-file",  # Long option name.
        default=EvaAnalysisConfig.astronaut_summary_file,  # Default summary output path.
    )
    parser.add_argument(  # Named option for graph output.
        "--graph-file",  # Long option name.
        default=EvaAnalysisConfig.graph_file,  # Default graph output path.
    )
    args = parser.parse_args()  # Read arguments from sys.argv.

    return EvaAnalysisConfig(  # Convert parsed strings/defaults into a typed config object.
        input_file=Path(args.input_file),  # Convert input path to Path for reader compatibility.
        cleaned_csv_file=Path(args.cleaned_csv_file),  # Convert cleaned CSV output path to Path.
        astronaut_summary_file=Path(args.astronaut_summary_file),  # Convert summary path to Path.
        graph_file=Path(args.graph_file),  # Convert graph path to Path.
    )


def configure_logging() -> None:
    """Configure simple command-line logging."""
    logging.basicConfig(  # Configure root logging once for the command-line program.
        level=logging.INFO,  # Show informative progress and error messages.
        format="%(levelname)s: %(message)s",  # Keep tutorial command-line output readable.
    )


def main() -> None:
    """Command-line entry point."""
    configure_logging()  # Ensure log messages are visible when the script is run directly.
    try:  # Catch expected application-level errors and convert them to a clean exit code.
        build_workflow().run(parse_args())  # Assemble dependencies, parse config and execute the workflow.
    except EvaAnalysisError as exc:  # Only catch known domain errors; unexpected bugs should still surface.
        LOGGER.error("EVA analysis failed: %s", exc)  # Report a concise user-facing failure message.
        raise SystemExit(1) from exc  # Exit with non-zero status so shells/CI know the run failed.


if __name__ == "__main__":  # Allows this module to be run with python -m eva_analysis.cli.
    main()  # Delegate to the explicit entry-point function.
