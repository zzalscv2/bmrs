"""Runtime configuration for the EVA analysis application.

This module has one responsibility: define file paths used by a run of the
analysis. Keeping paths in a configuration object avoids scattering filenames
through workflow code.
"""

from __future__ import annotations  # Supports modern type annotations consistently.

from dataclasses import dataclass  # Provides a compact immutable configuration type.
from pathlib import Path  # Represents filesystem paths safely across operating systems.


@dataclass(frozen=True)  # frozen=True makes each run configuration stable once created.
class EvaAnalysisConfig:
    """File locations needed by the analysis workflow.

    Why this exists: the workflow should receive configuration rather than hard-
    code paths. That makes the code easier to reuse in tests, tutorials and other
    command-line runs.
    """

    input_file: Path = Path("data/eva-data.json")  # Default JSON input file used by the tutorial.
    cleaned_csv_file: Path = Path("results/eva-data.csv")  # Output path for cleaned tabular data.
    astronaut_summary_file: Path = Path("results/duration_by_astronaut.csv")  # Output path for summary table.
    graph_file: Path = Path("results/cumulative_eva_graph.png")  # Output path for generated plot image.
