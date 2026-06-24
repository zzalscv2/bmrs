"""
NASA EVA data analysis.

Reads eva-data.json, cleans the records, exports cleaned CSV data,
builds a per-astronaut EVA duration summary, calculates cumulative EVA time
by date, saves a cumulative graph, and opens the graph for viewing.

Expected input file in the same directory as this script:
    eva-data.json

Outputs written to the same directory:
    eva-data.csv
    astronaut_eva_summary.csv
    cumulative_eva_by_date.csv
    cumulative_eva_graph.png
"""

from __future__ import annotations

import json
import platform
import subprocess
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


ROOT_DIRECTORY = Path(__file__).resolve().parent
INPUT_JSON_FILE = ROOT_DIRECTORY / "eva-data.json"
CLEANED_CSV_FILE = ROOT_DIRECTORY / "eva-data.csv"
ASTRONAUT_SUMMARY_CSV_FILE = ROOT_DIRECTORY / "astronaut_eva_summary.csv"
CUMULATIVE_EVA_CSV_FILE = ROOT_DIRECTORY / "cumulative_eva_by_date.csv"
CUMULATIVE_GRAPH_FILE = ROOT_DIRECTORY / "cumulative_eva_graph.png"


REQUIRED_COLUMNS = ["eva", "country", "crew", "vehicle", "date", "duration", "purpose"]


def read_eva_json(json_file_path: Path) -> list[dict[str, Any]]:
    """Read EVA records from a JSON file."""
    if not json_file_path.exists():
        raise FileNotFoundError(f"Could not find input file: {json_file_path}")

    with json_file_path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    if not isinstance(data, list):
        raise ValueError("The JSON file must contain a list of EVA records.")

    return data


def parse_duration_to_hours(duration_value: Any) -> float | None:
    """Convert a duration such as '7:24' into decimal hours."""
    if pd.isna(duration_value):
        return None

    duration_text = str(duration_value).strip()
    if not duration_text:
        return None

    try:
        hours_text, minutes_text = duration_text.split(":", maxsplit=1)
        hours = int(hours_text)
        minutes = int(minutes_text)
    except ValueError as error:
        raise ValueError(f"Invalid duration value: {duration_value!r}") from error

    if minutes < 0 or minutes >= 60:
        raise ValueError(f"Invalid minute value in duration: {duration_value!r}")

    return hours + minutes / 60


def clean_crew_names(crew_value: Any) -> str:
    """Clean the semicolon-separated crew field."""
    if pd.isna(crew_value):
        return ""

    crew_names = [name.strip() for name in str(crew_value).split(";") if name.strip()]
    return "; ".join(crew_names)


def clean_text(value: Any) -> str:
    """Normalise missing values and repeated whitespace in text fields."""
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def clean_eva_data(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Clean raw EVA records and return a date-sorted DataFrame."""
    dataframe = pd.DataFrame(records)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"The input data is missing columns: {missing_columns}")

    dataframe = dataframe[REQUIRED_COLUMNS].copy()

    for column in ["country", "vehicle", "purpose"]:
        dataframe[column] = dataframe[column].apply(clean_text)

    dataframe["crew"] = dataframe["crew"].apply(clean_crew_names)
    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")
    dataframe["duration_hours"] = dataframe["duration"].apply(parse_duration_to_hours)

    dataframe["eva"] = pd.to_numeric(dataframe["eva"], errors="coerce").astype("Int64")

    dataframe = dataframe.dropna(subset=["date", "duration_hours"])
    dataframe = dataframe.drop_duplicates()
    dataframe = dataframe.sort_values(by=["date", "eva"], ascending=True).reset_index(drop=True)

    dataframe["date"] = dataframe["date"].dt.date

    return dataframe


def create_astronaut_summary(cleaned_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create a per-astronaut summary of EVA count and total EVA time."""
    astronaut_dataframe = cleaned_dataframe.copy()
    astronaut_dataframe["astronaut"] = astronaut_dataframe["crew"].str.split("; ")
    astronaut_dataframe = astronaut_dataframe.explode("astronaut")
    astronaut_dataframe["astronaut"] = astronaut_dataframe["astronaut"].str.strip()
    astronaut_dataframe = astronaut_dataframe[astronaut_dataframe["astronaut"] != ""]

    summary_dataframe = (
        astronaut_dataframe.groupby("astronaut", as_index=False)
        .agg(
            eva_count=("eva", "count"),
            total_duration_hours=("duration_hours", "sum"),
        )
        .sort_values(by=["total_duration_hours", "eva_count", "astronaut"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    summary_dataframe["total_duration_hours"] = summary_dataframe["total_duration_hours"].round(2)
    return summary_dataframe


def create_cumulative_eva_by_date(cleaned_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calculate cumulative EVA time by date for plotting."""
    daily_dataframe = (
        cleaned_dataframe.groupby("date", as_index=False)["duration_hours"]
        .sum()
        .sort_values(by="date")
        .reset_index(drop=True)
    )

    daily_dataframe["cumulative_duration_hours"] = daily_dataframe["duration_hours"].cumsum()
    daily_dataframe["duration_hours"] = daily_dataframe["duration_hours"].round(2)
    daily_dataframe["cumulative_duration_hours"] = daily_dataframe["cumulative_duration_hours"].round(2)

    return daily_dataframe


def plot_cumulative_eva(cumulative_dataframe: pd.DataFrame, output_file_path: Path) -> None:
    """Plot cumulative EVA time over the years and save it as a PNG file."""
    plt.figure(figsize=(12, 7))
    plt.plot(
        pd.to_datetime(cumulative_dataframe["date"]),
        cumulative_dataframe["cumulative_duration_hours"],
        linewidth=2,
    )
    plt.title("Cumulative Time Spent on NASA EVAs")
    plt.xlabel("Year")
    plt.ylabel("Cumulative EVA Time (hours)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file_path, dpi=300)
    plt.close()


def open_file(file_path: Path) -> None:
    """Open a file using the default viewer on macOS, Windows, or Linux."""
    system_name = platform.system()

    try:
        if system_name == "Darwin":
            subprocess.run(["open", str(file_path)], check=False)
        elif system_name == "Windows":
            subprocess.run(["cmd", "/c", "start", "", str(file_path)], check=False, shell=False)
        else:
            subprocess.run(["xdg-open", str(file_path)], check=False)
    except OSError as error:
        print(f"Could not automatically open {file_path}: {error}")


def main() -> None:
    """Run the full EVA data analysis workflow."""
    records = read_eva_json(INPUT_JSON_FILE)

    cleaned_dataframe = clean_eva_data(records)
    cleaned_dataframe.to_csv(CLEANED_CSV_FILE, index=False)

    astronaut_summary_dataframe = create_astronaut_summary(cleaned_dataframe)
    astronaut_summary_dataframe.to_csv(ASTRONAUT_SUMMARY_CSV_FILE, index=False)

    cumulative_dataframe = create_cumulative_eva_by_date(cleaned_dataframe)
    cumulative_dataframe.to_csv(CUMULATIVE_EVA_CSV_FILE, index=False)

    plot_cumulative_eva(cumulative_dataframe, CUMULATIVE_GRAPH_FILE)
    open_file(CUMULATIVE_GRAPH_FILE)

    print(f"Cleaned CSV saved to: {CLEANED_CSV_FILE}")
    print(f"Astronaut summary CSV saved to: {ASTRONAUT_SUMMARY_CSV_FILE}")
    print(f"Cumulative EVA CSV saved to: {CUMULATIVE_EVA_CSV_FILE}")
    print(f"Cumulative EVA graph saved to: {CUMULATIVE_GRAPH_FILE}")


if __name__ == "__main__":
    main()
