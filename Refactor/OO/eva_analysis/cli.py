"""Command-line configuration assembly.

Reason to change: how configuration is obtained from the command line (argument
conventions, defaults). Separated from ``PipelineConfig`` so that the shape of
the configuration and the way it is parsed evolve independently (SRP).
"""

from __future__ import annotations

from .config import PipelineConfig
from .interfaces import Reporter


class CliConfigFactory:
    """Builds a :class:`PipelineConfig` from command-line arguments."""

    DEFAULT_INPUT = "data/eva-data.json"
    DEFAULT_OUTPUT = "results/eva-data.csv"
    DURATION_BY_ASTRONAUT_FILE = "results/duration_by_astronaut.csv"
    GRAPH_FILE = "results/cumulative_eva_graph.png"

    def __init__(self, reporter: Reporter) -> None:
        self._reporter = reporter

    def from_args(self, argv: list[str]) -> PipelineConfig:
        """Parse ``argv``, falling back to defaults when too few are supplied."""
        if len(argv) < 3:
            self._reporter.report("Using default input and output filenames")
            input_file = self.DEFAULT_INPUT
            output_file = self.DEFAULT_OUTPUT
        else:
            self._reporter.report("Using custom input and output filenames")
            input_file = argv[1]
            output_file = argv[2]

        return PipelineConfig(
            input_file=input_file,
            output_file=output_file,
            duration_by_astronaut_file=self.DURATION_BY_ASTRONAUT_FILE,
            graph_file=self.GRAPH_FILE,
        )
