"""
NASA EVA (Extra-Vehicular Activity) spacewalk analysis.

Pipeline:
  1. Read raw spacewalk records from eva-data.json
  2. Clean the data for analysis (parse dates, convert durations to hours,
     tidy the crew field, drop rows that cannot be analysed)
  3. Write the cleaned data to eva-data.csv
  4. Build a per-astronaut summary of total EVA time and save it to CSV
  5. Sort by date and compute cumulative EVA time
  6. Plot cumulative EVA time over the years to cumulative_eva_graph.png

Usage:
    python eva_analysis.py [input_json] [output_dir]
"""

import sys
import json
from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # non-interactive backend, safe for headless runs
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def duration_to_hours(duration):
    """Convert an 'H:MM' duration string into decimal hours.

    Returns None for missing or malformed values so they can be dropped.
    """
    if not isinstance(duration, str) or ":" not in duration:
        return None
    try:
        hours, minutes = duration.split(":")
        return int(hours) + int(minutes) / 60.0
    except (ValueError, TypeError):
        return None


def split_crew(crew):
    """Split a ';'-separated crew string into a clean list of names.

    Handles trailing and doubled semicolons (e.g. 'A;B;;') and stray spaces.
    """
    if not isinstance(crew, str):
        return []
    return [name.strip() for name in crew.split(";") if name.strip()]


# ----------------------------------------------------------------------
# Pipeline steps
# ----------------------------------------------------------------------
def read_data(json_path):
    """Read the raw EVA records from a JSON file into a DataFrame."""
    print(f"Reading data from {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    print(f"  {len(df)} raw records loaded")
    return df


def clean_data(df):
    """Clean the raw EVA data for analysis.

    - Parse the date column to real datetimes.
    - Convert 'H:MM' durations to decimal hours.
    - Tidy the crew field.
    - Drop rows missing a date or duration (cannot be placed on a timeline
      or contribute to time totals) and sort chronologically.
    """
    print("Cleaning data")
    df = df.copy()

    # Parse dates; unparseable / missing become NaT
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Convert duration to decimal hours
    df["duration_hours"] = df["duration"].apply(duration_to_hours)

    # Tidy crew into both a clean string and a list
    df["crew_list"] = df["crew"].apply(split_crew)
    df["crew"] = df["crew_list"].apply(lambda names: "; ".join(names))

    # Drop rows we cannot analyse (no date or no duration)
    before = len(df)
    df = df.dropna(subset=["date", "duration_hours"])
    print(f"  dropped {before - len(df)} rows missing date or duration")

    # Sort chronologically and reset the index
    df = df.sort_values("date").reset_index(drop=True)
    print(f"  {len(df)} clean records remain")
    return df


def write_cleaned_csv(df, out_path):
    """Write the cleaned data to a CSV file (list column excluded)."""
    columns = [
        "eva", "country", "crew", "vehicle",
        "date", "duration", "duration_hours", "purpose",
    ]
    columns = [c for c in columns if c in df.columns]
    df[columns].to_csv(out_path, index=False)
    print(f"Wrote cleaned CSV -> {out_path}")


def summarise_by_astronaut(df, out_path):
    """Build and save a per-astronaut total-EVA summary.

    Each spacewalk's duration is credited to every crew member on it.
    """
    print("Building per-astronaut summary")
    exploded = df.explode("crew_list").rename(columns={"crew_list": "astronaut"})
    exploded = exploded[exploded["astronaut"].notna() & (exploded["astronaut"] != "")]

    summary = (
        exploded.groupby("astronaut")
        .agg(
            number_of_evas=("eva", "size"),
            total_eva_hours=("duration_hours", "sum"),
        )
        .sort_values("total_eva_hours", ascending=False)
        .reset_index()
    )
    summary["total_eva_hours"] = summary["total_eva_hours"].round(2)
    summary.to_csv(out_path, index=False)
    print(f"  {len(summary)} astronauts summarised -> {out_path}")
    return summary


def plot_cumulative(df, out_path):
    """Plot cumulative EVA time against date and save to a PNG."""
    print("Plotting cumulative EVA time")
    df = df.sort_values("date").copy()
    df["cumulative_hours"] = df["duration_hours"].cumsum()

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["date"], df["cumulative_hours"],
            color="#1f4e79", linewidth=2)
    ax.fill_between(df["date"], df["cumulative_hours"],
                    color="#1f4e79", alpha=0.12)

    ax.set_title("Cumulative Time Spent on Spacewalks (EVAs) Over the Years",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Cumulative EVA time (hours)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.4)

    total = df["cumulative_hours"].iloc[-1]
    ax.annotate(f"{total:,.0f} total hours",
                xy=(df["date"].iloc[-1], total),
                xytext=(-10, -20), textcoords="offset points",
                ha="right", fontsize=10, color="#1f4e79")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Saved plot -> {out_path}")
    return df


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    input_json = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("eva-data.json")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_csv = output_dir / "eva-data.csv"
    summary_csv = output_dir / "eva-per-astronaut.csv"
    graph_png = output_dir / "cumulative_eva_graph.png"

    df_raw = read_data(input_json)
    df = clean_data(df_raw)
    write_cleaned_csv(df, cleaned_csv)
    summarise_by_astronaut(df, summary_csv)
    plot_cumulative(df, graph_png)

    print("\nDone.")


if __name__ == "__main__":
    main()
