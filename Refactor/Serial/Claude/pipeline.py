"""pipeline.py — orchestration: sequence the steps using injected collaborators.

WHY THIS FILE EXISTS
`run_analysis` is the recipe: read → clean → enrich → write → summarise → write →
compute → plot → save. It depends ONLY on the reader/writer *abstractions* and on
the pure functions. It never names a file format and never builds an I/O object
itself — those arrive as parameters. So the identical orchestration runs against
JSON+CSV today and a different source/sink tomorrow with no edits here.

SOLID: Dependency Inversion (collaborators are injected), Single Responsibility
(this function only sequences; it does not read, parse, compute, or draw).
"""

from __future__ import annotations

# `logging` replaces the original's `print` calls. WHY: log output carries a
# severity and a logger name, can be filtered, silenced, or redirected to a file
# by the application — `print` can do none of that. (ANALYSABILITY)
import logging

# Imports are grouped and explicit so the dependency graph is readable at a
# glance: the pipeline pulls computation from analysis/transforms, presentation
# from plotting, and the TYPES (not the concretions) from readers/writers.
from .analysis import cumulative_time_in_space, total_duration_by_astronaut
from .config import AnalysisConfig
from .plotting import build_cumulative_figure, save_figure
from .readers import DataFrameReader   # the Protocol/type, not JsonEvaReader
from .transforms import add_crew_size, clean_eva_data
from .writers import DataFrameWriter   # the Protocol/type, not CsvDataFrameWriter

# A module-level logger named after this module (`__name__`). WHY this idiom:
# every message is automatically tagged with where it came from, and the
# application controls the actual output, not the library.
logger = logging.getLogger(__name__)


def run_analysis(
    config: AnalysisConfig,
    reader: DataFrameReader,
    writer: DataFrameWriter,
) -> None:
    """Run the full EVA analysis.

    Note the parameter TYPES: `DataFrameReader`/`DataFrameWriter` are the
    contracts. This function cannot tell — and must not care — whether it was
    handed a JSON reader and CSV writer or fakes in a test. That is dependency
    inversion in action, and it is what makes the pipeline testable with no disk.
    """
    logger.info("Reading source data")
    # Ask the injected reader for data. Which concrete reader this is was decided
    # elsewhere (cli.py). This line is format-agnostic.
    raw = reader.read()

    # Clean, then enrich — each returns a NEW frame, so reassigning `eva` simply
    # advances it through the pipeline without mutating anything shared.
    eva = clean_eva_data(raw)
    # Enrich with crew size. In the original, the crew-size code existed but was
    # NEVER CALLED (dead code). Wiring it in here makes the module's behaviour
    # match its capability. Deleting it instead would be equally valid — the
    # point is that good structure forced the choice into the open.
    eva = add_crew_size(eva)

    # Write the cleaned full table. The pipeline supplies WHAT and WHERE
    # (the frame and a path from config); the injected writer decides HOW (CSV).
    # The `%s` + argument form lets logging skip string-building if INFO is off.
    logger.info("Writing cleaned EVA table to %s", config.eva_csv_file)
    writer.write(eva, config.eva_csv_file)

    # Derive and write the per-astronaut summary, reusing the SAME writer
    # instance for a different destination (why `destination` is a per-call arg).
    logger.info("Summarising duration by astronaut")
    by_astronaut = total_duration_by_astronaut(eva)
    writer.write(by_astronaut, config.astronaut_csv_file)

    # Presentation, as three separated steps: compute the series (analysis),
    # build the figure (plotting), save the figure (plotting). Each could be
    # tested or reused on its own.
    logger.info("Plotting cumulative time in space to %s", config.graph_file)
    cumulative = cumulative_time_in_space(eva, date_column=config.date_column)
    figure = build_cumulative_figure(cumulative, date_column=config.date_column)
    save_figure(figure, config.graph_file)
