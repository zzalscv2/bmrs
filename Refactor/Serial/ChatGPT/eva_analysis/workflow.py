"""Workflow orchestration for the EVA analysis use case.

This module has one responsibility: coordinate the sequence of collaborators. It
contains the application flow but not the details of reading, cleaning, writing,
analysis or plotting.
"""

from __future__ import annotations  # Keeps type-hint behaviour consistent.

import logging  # Used to report high-level workflow progress.

from .analysers import EvaSummaryAnalyser  # Collaborator that produces astronaut summaries.
from .cleaners import EvaDataCleaner  # Collaborator that prepares raw data for analysis.
from .config import EvaAnalysisConfig  # Typed paths/configuration for one run.
from .interfaces import DataReader, DataValidator, DataWriter  # Protocols support dependency inversion.
from .plotting import CumulativeEvaPlotter  # Collaborator that saves the graph.

LOGGER = logging.getLogger(__name__)  # Module logger identifies workflow messages.


class EvaAnalysisWorkflow:
    """Coordinate the complete EVA analysis workflow.

    DIP: the workflow receives dependencies through the constructor. It does not
    construct pd.read_json, CSV writing or plotting details itself.
    """

    def __init__(
        self,
        reader: DataReader,  # Abstraction for input, allowing JSON/CSV/database readers.
        writer: DataWriter,  # Abstraction for output, allowing CSV/Parquet/database writers.
        validator: DataValidator,  # Abstraction for validation rules.
        cleaner: EvaDataCleaner,  # Concrete cleaner because this is the domain cleaning policy.
        analyser: EvaSummaryAnalyser,  # Concrete analyser for this use case's summary output.
        plotter: CumulativeEvaPlotter,  # Concrete plotter for this use case's graph output.
    ):
        self.reader = reader  # Store reader dependency for use in run().
        self.writer = writer  # Store writer dependency for both CSV outputs.
        self.validator = validator  # Store validator dependency for raw/cleaned checks.
        self.cleaner = cleaner  # Store cleaner dependency for transformation stage.
        self.analyser = analyser  # Store analyser dependency for summary stage.
        self.plotter = plotter  # Store plotter dependency for graph stage.

    def run(self, config: EvaAnalysisConfig) -> None:
        """Execute the full analysis pipeline once."""
        LOGGER.info("Starting EVA analysis")  # High-level trace message for the start of the use case.

        raw_data = self.reader.read(config.input_file)  # Load raw records through the reader abstraction.
        self.validator.validate(raw_data)  # Check required structure before cleaning or analysis.
        clean_data = self.cleaner.clean(raw_data)  # Produce cleaned data without mutating raw_data.
        self.validator.validate(clean_data)  # Recheck structure after cleaning in case all rows were removed.

        self.writer.write(clean_data, config.cleaned_csv_file)  # Save cleaned data through writer abstraction.

        astronaut_summary = self.analyser.duration_by_astronaut(clean_data)  # Create grouped astronaut summary.
        self.writer.write(astronaut_summary, config.astronaut_summary_file)  # Save summary through same writer interface.

        self.plotter.save(clean_data, config.graph_file)  # Save cumulative duration graph.
        LOGGER.info("Finished EVA analysis")  # High-level trace message for successful completion.
