"""__init__.py — marks this folder as a package and defines its PUBLIC surface.

WHY THIS FILE EXISTS
The presence of this file is what makes `eva_analysis` an importable package. By
re-exporting the key names here, callers can write `from eva_analysis import
run_analysis` instead of reaching into submodules (`from eva_analysis.pipeline
import run_analysis`). This file is the curated "front door": it states what the
package offers and hides where each piece happens to live.

Maintainability: ANALYSABILITY (one obvious entry point) and MODIFIABILITY
(internal files can be reorganised without breaking callers, as long as these
names still resolve).
"""

from __future__ import annotations

# Pull the public names up from their home modules into the package namespace.
# WHY group by source module: a reader can see at a glance what each part
# contributes — config, pipeline, plotting, readers, transforms, writers.
from .analysis import cumulative_time_in_space, total_duration_by_astronaut
from .config import AnalysisConfig
from .pipeline import run_analysis
from .plotting import build_cumulative_figure, save_figure
from .readers import DataFrameReader, JsonEvaReader
from .transforms import (
    add_crew_size,
    add_duration_hours,
    clean_eva_data,
    count_crew,
    parse_duration_to_hours,
)
from .writers import CsvDataFrameWriter, DataFrameWriter

# `__all__` lists the names considered public. HOW it is used: it defines what
# `from eva_analysis import *` would bring in, and signals intent to tools and
# readers. WHY maintain it: it is an explicit, reviewable contract of the
# package's API — anything not listed is "internal, may change".
__all__ = [
    "AnalysisConfig",
    "run_analysis",
    "DataFrameReader",
    "JsonEvaReader",
    "DataFrameWriter",
    "CsvDataFrameWriter",
    "clean_eva_data",
    "parse_duration_to_hours",
    "add_duration_hours",
    "count_crew",
    "add_crew_size",
    "total_duration_by_astronaut",
    "cumulative_time_in_space",
    "build_cumulative_figure",
    "save_figure",
]
