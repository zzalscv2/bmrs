"""Configuration value object.

Reason to change: the set of paths the pipeline needs. This is now a pure,
immutable data holder with no behaviour — CLI parsing lives in ``cli`` so that
"what configuration is" and "how it is obtained" change independently (SRP).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Holds the file paths the pipeline reads from and writes to."""

    input_file: str
    output_file: str
    duration_by_astronaut_file: str
    graph_file: str
