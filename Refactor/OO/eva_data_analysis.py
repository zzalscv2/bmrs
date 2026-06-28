"""Composition root and command-line entry point.

Reason to change: which concrete implementations are wired together. This is the
*only* module that imports concretions; every other module depends on
abstractions. Run with:

    python eva_data_analysis.py [input.json output.csv]
"""

from __future__ import annotations

import sys

from eva_analysis import (
    AstronautDurationSummariser,
    CliConfigFactory,
    ConsoleReporter,
    CsvDataSink,
    CumulativeDurationTransformer,
    CumulativeTimePlotter,
    EvaAnalysisPipeline,
    EvaDataCleaner,
    JsonEvaDataSource,
    PipelineConfig,
    Reporter,
    TextDurationConverter,
)

def build_pipeline(config: PipelineConfig, reporter: Reporter) -> EvaAnalysisPipeline:
    """Wire up concrete collaborators into a ready-to-run pipeline."""
    duration_converter = TextDurationConverter()
    return EvaAnalysisPipeline(
        config=config,
        source=JsonEvaDataSource(config.input_file, reporter),
        sink=CsvDataSink(reporter),
        cleaner=EvaDataCleaner(),
        cumulative_transformer=CumulativeDurationTransformer(duration_converter),
        summariser=AstronautDurationSummariser(duration_converter),
        plotter=CumulativeTimePlotter(reporter),
        reporter=reporter,
    )


def main(argv: list[str]) -> None:
    reporter = ConsoleReporter()
    config = CliConfigFactory(reporter).from_args(argv)
    build_pipeline(config, reporter).run()


if __name__ == "__main__":
    main(sys.argv)
