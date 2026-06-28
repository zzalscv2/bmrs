"""EVA data analysis package.

Public facade. Importing from ``eva_analysis`` gives access to every collaborator
and the pipeline, while each lives in its own single-responsibility module.
"""

from __future__ import annotations

from .analysis import AstronautDurationSummariser
from .cli import CliConfigFactory
from .config import PipelineConfig
from .domain import SemicolonCrewSizeCalculator, TextDurationConverter
from .interfaces import (
    CrewSizeCalculator,
    DataSink,
    DataSource,
    DataTransformer,
    DurationConverter,
    DurationSummariser,
    Plotter,
    Reporter,
)
from .pipeline import EvaAnalysisPipeline
from .plotting import CumulativeTimePlotter
from .reporting import ConsoleReporter, NullReporter
from .sinks import CsvDataSink
from .sources import JsonEvaDataSource
from .transformers import (
    CrewSizeTransformer,
    CumulativeDurationTransformer,
    EvaDataCleaner,
)

__all__ = [
    "AstronautDurationSummariser",
    "CliConfigFactory",
    "ConsoleReporter",
    "CrewSizeCalculator",
    "CrewSizeTransformer",
    "CsvDataSink",
    "CumulativeDurationTransformer",
    "CumulativeTimePlotter",
    "DataSink",
    "DataSource",
    "DataTransformer",
    "DurationConverter",
    "DurationSummariser",
    "EvaAnalysisPipeline",
    "EvaDataCleaner",
    "JsonEvaDataSource",
    "NullReporter",
    "PipelineConfig",
    "Plotter",
    "Reporter",
    "SemicolonCrewSizeCalculator",
    "TextDurationConverter",
]
