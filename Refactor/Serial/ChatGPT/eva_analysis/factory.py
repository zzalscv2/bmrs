"""Factory functions for assembling the default EVA analysis workflow.

This module has one responsibility: wire together concrete classes. Keeping
construction here prevents the workflow from knowing how to build its own
dependencies.
"""

from __future__ import annotations  # Keeps annotations consistent.

from .analysers import EvaSummaryAnalyser  # Concrete summary analyser.
from .cleaners import EvaDataCleaner  # Concrete data cleaner.
from .converters import DurationConverter  # Concrete duration converter shared by analysis and plotting.
from .parsers import CrewParser  # Concrete crew parser used by the analyser.
from .plotting import CumulativeEvaDataBuilder, CumulativeEvaPlotter  # Concrete plotting collaborators.
from .readers import JsonEvaDataReader  # Concrete JSON reader for the default input format.
from .validators import EvaSchemaValidator  # Concrete schema validator.
from .writers import CsvDataWriter  # Concrete CSV writer for default outputs.
from .workflow import EvaAnalysisWorkflow  # High-level workflow being assembled.


def build_workflow() -> EvaAnalysisWorkflow:
    """Create the default production workflow."""
    duration_converter = DurationConverter()  # Shared because both summary and plotting need duration conversion.
    crew_parser = CrewParser()  # Created separately so parsing remains independently replaceable.
    cumulative_data_builder = CumulativeEvaDataBuilder(duration_converter)  # Plot data builder reuses converter.

    return EvaAnalysisWorkflow(  # Inject all dependencies into the workflow constructor.
        reader=JsonEvaDataReader(),  # Default reader: JSON input.
        writer=CsvDataWriter(),  # Default writer: CSV output.
        validator=EvaSchemaValidator(),  # Default validator: required EVA columns and non-empty data.
        cleaner=EvaDataCleaner(),  # Default cleaner: remove unusable rows and normalise dates/EVA IDs.
        analyser=EvaSummaryAnalyser(duration_converter, crew_parser),  # Summary analyser with injected helpers.
        plotter=CumulativeEvaPlotter(cumulative_data_builder),  # Plotter with injected data builder.
    )
