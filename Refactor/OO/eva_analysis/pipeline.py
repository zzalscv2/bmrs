"""The orchestration controller.

Reason to change: the sequence of steps in the analysis. This module depends
*only* on the abstract contracts and the config value object — it imports no
concrete source, sink, transformer, summariser, plotter, or reporter
(Dependency Inversion). That is what lets the whole pipeline be exercised in
tests with simple test doubles.
"""

from __future__ import annotations

from .config import PipelineConfig
from .interfaces import (
    DataSink,
    DataSource,
    DataTransformer,
    DurationSummariser,
    Plotter,
    Reporter,
)


class EvaAnalysisPipeline:
    """Coordinates the end-to-end EVA analysis from injected collaborators."""

    def __init__(
        self,
        config: PipelineConfig,
        source: DataSource,
        sink: DataSink,
        cleaner: DataTransformer,
        cumulative_transformer: DataTransformer,
        summariser: DurationSummariser,
        plotter: Plotter,
        reporter: Reporter,
    ) -> None:
        self._config = config
        self._source = source
        self._sink = sink
        self._cleaner = cleaner
        self._cumulative_transformer = cumulative_transformer
        self._summariser = summariser
        self._plotter = plotter
        self._reporter = reporter

    def run(self) -> None:
        self._reporter.report("--START--")

        eva_data = self._cleaner.transform(self._source.read())
        self._sink.write(eva_data, self._config.output_file)

        duration_by_astronaut = self._summariser.summarise(eva_data)
        self._sink.write(
            duration_by_astronaut, self._config.duration_by_astronaut_file
        )

        cumulative = self._cumulative_transformer.transform(eva_data)
        self._plotter.plot(cumulative, self._config.graph_file)

        self._reporter.report("--END--")
