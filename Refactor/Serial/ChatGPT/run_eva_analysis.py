"""Thin script entry point for running the EVA analysis package.

This file exists for convenience so users can run:

    python run_eva_analysis.py

The real command-line logic lives in eva_analysis/cli.py so this file has only
one responsibility: delegate execution to the package entry point.
"""

from eva_analysis.cli import main  # Import the package CLI entry point without duplicating its logic.


if __name__ == "__main__":  # Only run when this file is executed directly, not when imported.
    main()  # Delegate all behaviour to the CLI module.
