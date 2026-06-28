import matplotlib.pyplot as plt
import pandas as pd
import sys
import re


def main(input_file, output_file, duration_by_astronaut_output_file, graph_file):
    print("--START--")

    # Read the data from JSON file
    eva_data = read_json_to_dataframe(input_file)

    # Convert and export data to CSV file
    write_dataframe_to_csv(eva_data, output_file)

    # Calculate summary table for total EVA per astronaut
    duration_by_astronaut_df = summary_duration_by_astronaut(eva_data)
    # Save summary duration data by each astronaut to CSV file
    write_dataframe_to_csv(duration_by_astronaut_df, duration_by_astronaut_output_file)

    # ------------------------------------------------------------------ #
    # FIX (Bug 2 - consumer side): the cumulative time-series plot is the
    # ONLY output that genuinely needs a 'date'. We therefore drop the
    # date-less rows HERE, locally, instead of globally in
    # read_json_to_dataframe(). This keeps those rows available to the
    # per-astronaut summary above (see read_json_to_dataframe for the
    # full explanation and the 44-row evidence).
    #
    # We also build a separate frame (eva_for_plot) rather than mutating
    # eva_data in place with sort_values(inplace=True). The original code
    # sorted eva_data in place AFTER the CSV/summary were produced, which
    # was harmless here but is a side effect waiting to bite a future
    # caller that reuses eva_data. A local copy is safer.
    # ------------------------------------------------------------------ #
    eva_for_plot = eva_data.dropna(subset=['date']).sort_values('date')

    # Plot cumulative time spent in space over years
    plot_cumulative_time_in_space(eva_for_plot, graph_file)

    print("--END--")


def read_json_to_dataframe(input_file):
    """
    Read the data from a JSON file into a Pandas dataframe.
    Clean the data by removing any rows where the 'duration' value is missing.

    Args:
        input_file (file or str): The file object or path to the JSON file.

    Returns:
         eva_df (pd.DataFrame): The cleaned data as a dataframe structure
    """
    print(f'Reading JSON file {input_file}')

    # ------------------------------------------------------------------ #
    # FIX (Bug 4 - latent encoding bug):
    # WHAT  : encoding was hard-coded to 'ascii'.
    # WHERE : the encoding= argument of pd.read_json below.
    # WHY   : the dataset is full of UTF-8-derived content (accented names
    #         such as "Jean-Louc Chretien" and many "\u00c2\u00xx" mojibake
    #         escapes). The shipped file happens to store all of it as \u
    #         escapes, so the raw bytes are pure ASCII (verified: 0 bytes
    #         > 127) and 'ascii' does not raise *today*. But the moment the
    #         source is regenerated with real UTF-8 bytes, read_json(...,
    #         encoding='ascii') raises UnicodeDecodeError. 'utf-8' reads the
    #         current file identically and is robust to that change.
    # ------------------------------------------------------------------ #
    eva_df = pd.read_json(input_file, convert_dates=['date'], encoding='utf-8')
    eva_df['eva'] = eva_df['eva'].astype(float)

    # ------------------------------------------------------------------ #
    # FIX (Bug 2 - over-aggressive cleaning):
    # WHAT  : the original dropped rows missing 'duration' OR 'date'
    #         (subset=['duration', 'date']).
    # WHERE : the dropna() call below.
    # WHY   : two reasons.
    #         (a) Correctness: 44 records have a valid 'duration' but no
    #             'date' (verified by counting duration.notna() & date.isna()).
    #             The per-astronaut summary does not use 'date' at all, yet
    #             those 44 spacewalks were being discarded before it ran,
    #             silently undercounting astronaut totals.
    #         (b) Contract: this function's own docstring promises only to
    #             remove rows "where the 'duration' value is missing" - it
    #             never mentions 'date'. The old code dropped more than it
    #             documented. We now drop on 'duration' alone, matching the
    #             docstring, and let the plotting path (in main) drop the
    #             date-less rows itself, since the time-series is the only
    #             consumer that needs a date.
    # ------------------------------------------------------------------ #
    eva_df.dropna(axis=0, subset=['duration'], inplace=True)
    return eva_df


def write_dataframe_to_csv(df, output_file):
    """
    Write the dataframe to a CSV file.

    Args:
        df (pd.DataFrame): The input dataframe.
        output_file (file or str): The file object or path to the output CSV file.

    Returns:
        None
    """
    print(f'Saving to CSV file {output_file}')
    # Save dataframe to CSV file for later analysis.
    #
    # NOTE (relates to Bug 1): index=False is intentionally kept here and is
    # CORRECT for every frame now passed in. The main export has a plain
    # RangeIndex (nothing meaningful to save), and the per-astronaut summary
    # now carries 'crew' as a real COLUMN rather than the index (we call
    # reset_index() inside summary_duration_by_astronaut). The Bug 1 fix
    # lives at that call site, not here, so this shared writer stays generic.
    df.to_csv(output_file, index=False, encoding='utf-8')


def plot_cumulative_time_in_space(df, graph_file):
    """
    Plot the cumulative time spent in space over years.

    Convert the duration column from strings to number of hours
    Calculate cumulative sum of durations
    Generate a plot of cumulative time spent in space over years and
    save it to the specified location

    Args:
        df (pd.DataFrame): The input dataframe. Must already be filtered to
            rows with a non-null 'date' and sorted by 'date' (done in main).

    Returns:
        None
    """
    print(f'Plotting cumulative spacewalk duration and saving to {graph_file}')
    df = add_duration_hours(df)
    df['cumulative_time'] = df['duration_hours'].cumsum()
    plt.plot(df['date'], df['cumulative_time'], 'ko-')

    # FIX (cosmetic): the x-axis plots full calendar dates, not years, so the
    # label 'Year' was misleading. Renamed to 'Date' to match the data drawn.
    plt.xlabel('Date')
    plt.ylabel('Total time spent in space to date (hours)')
    plt.tight_layout()
    plt.savefig(graph_file)
    plt.show()


def text_to_duration(duration):
    """
    Convert a text format duration "HH:MM" to duration in hours

    Args:
        duration (str): The text format duration

    Returns:
        duration_hours (float): The duration in hours
    """
    # No bug here - verified against hand calcs: "0:36"->0.6, "2:07"->2.1167,
    # "7:12"->7.2. Left unchanged.
    hours, minutes = duration.split(":")
    duration_hours = int(hours) + int(minutes)/60
    return duration_hours


def add_duration_hours(df):
    """
    Add duration in hours (duration_hours) variable to the dataset

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        df_copy (pd.DataFrame): A copy of df with the new duration_hours variable added
    """
    df_copy = df.copy()
    df_copy["duration_hours"] = df_copy["duration"].apply(
        text_to_duration
    )
    return df_copy


def calculate_crew_size(crew):
    """
    Calculate the size of the crew for a single crew entry

    Args:
        crew (str): The text entry in the crew column containing a list of crew member names

    Returns:
        (int): The crew size, or None if the entry contains no names
    """
    # ------------------------------------------------------------------ #
    # FIX (Bug 3 - crew miscount):
    # WHAT  : the original returned len(re.split(r';', crew)) - 1.
    # WHERE : the return expression below.
    # WHY   : splitting on ';' yields an empty trailing element for the
    #         normal "Name;" format (the "- 1" was there to cancel that one
    #         trailing blank). But several entries contain a DOUBLE
    #         separator, e.g. Apollo 17's "Harrison Schmidt;Eugene Cernan;;".
    #         That splits into 4 parts -> 4 - 1 = 3, reporting a 3-person
    #         crew for what is really 2 people. The robust approach is to
    #         split and then keep only non-blank, non-whitespace names and
    #         count those. This is exactly the parsing that
    #         summary_duration_by_astronaut already uses, so the two
    #         functions now agree instead of disagreeing.
    #
    #         Verified after fix: "Harrison Schmidt;Eugene Cernan;;" -> 2,
    #         "Ed White;" -> 1, "Neil Armstrong;Buzz Aldrin;" -> 2.
    #
    # (Note: calculate_crew_size / add_crew_size_column are not wired into
    #  main(), so this was dormant dead-code logic - but it was still wrong,
    #  and is now correct should the pipeline ever start using crew_size.)
    # ------------------------------------------------------------------ #
    members = [name for name in crew.split(';') if name.strip()]
    if not members:
        return None
    return len(members)

def add_crew_size_column(df):
    """
    Add crew_size column to the dataset containing the value of the crew size

    Args:
        df (pd.DataFrame): The input data frame.

    Returns:
        df_copy (pd.DataFrame): A copy of the dataframe df with the new crew_size variable added
    """
    print('Adding crew size variable (crew_size) to dataset')
    df_copy = df.copy()
    df_copy["crew_size"] = df_copy["crew"].apply(
        calculate_crew_size
    )
    return df_copy


def summary_duration_by_astronaut(df):
    """
    Summarise the duration data by each astronaut.

    Args:
        df (pd.DataFrame): Input dataframe to be summarised

    Returns:
        sum_by_astro (pd.DataFrame): Data frame with one row per astronaut and
            columns ['crew', 'duration_hours'].
    """
    # FIX (minor - SettingWithCopyWarning): take an explicit .copy() of the
    # sliced columns. The original assigned back into subset.crew on a slice
    # of df, which pandas flags with a SettingWithCopyWarning (it "works" but
    # relies on undefined copy/view behaviour). Copying makes the intent
    # explicit and silences the warning.
    subset = df.loc[:, ['crew', 'duration']].copy()  # only relevant columns

    # Split the crew string into individuals, dropping blank fields produced
    # by the trailing (and occasional double) ';' - same robust rule used in
    # calculate_crew_size after the Bug 3 fix.
    subset['crew'] = subset['crew'].str.split(';').apply(
        lambda names: [name for name in names if name.strip()]
    )
    subset = subset.explode('crew')          # one row per crew member
    subset = add_duration_hours(subset)      # need duration_hours for the sum
    subset = subset.drop('duration', axis=1)  # drop the original string column
    subset = subset.groupby('crew').sum()

    # ------------------------------------------------------------------ #
    # FIX (Bug 1 - astronaut names were being lost in the saved CSV):
    # WHAT  : groupby('crew').sum() returns a frame whose ROW INDEX is the
    #         crew name; 'crew' is NOT a column at this point.
    # WHERE : the reset_index() added below (and its interaction with
    #         write_dataframe_to_csv's index=False).
    # WHY   : the shared writer saves with index=False, which silently drops
    #         the index. Without this fix, duration_by_astronaut.csv came out
    #         as a single unlabelled 'duration_hours' column - the numbers
    #         were right (e.g. Buzz Aldrin = 8.1167 h, matching a hand calc
    #         of his 5 EVAs) but you couldn't tell whose total was whose.
    #         reset_index() promotes 'crew' back to a real column so it
    #         survives the index=False write.
    # ------------------------------------------------------------------ #
    subset = subset.reset_index()
    return subset


if __name__ == "__main__":

    if len(sys.argv) < 3:
        input_file = 'data/eva-data.json'
        output_file = 'results/eva-data.csv'
        print(f'Using default input and output filenames')
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print('Using custom input and output filenames')

    graph_file = 'results/cumulative_eva_graph.png'
    duration_by_astronaut_output_file = 'results/duration_by_astronaut.csv'

    main(input_file, output_file, duration_by_astronaut_output_file, graph_file)
