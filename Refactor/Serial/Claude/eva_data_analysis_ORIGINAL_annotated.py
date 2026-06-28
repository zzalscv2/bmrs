# eva_data_analysis_ORIGINAL.py  [ANNOTATED — THE "BEFORE" EXHIBIT]
#
# This is the ORIGINAL script, unchanged, with line-by-line annotations. Where a
# line embodies a maintainability problem it is tagged:
#
#     SMELL (-> Step N): <what is wrong and why> ... fixed by walkthrough Step N
#
# so this file cross-references the refactoring walkthrough and the Assembly-Line
# activity. The code still runs; nothing functional has been altered.

# --- imports ---------------------------------------------------------------

import matplotlib.pyplot as plt
# WHAT: the plotting library, aliased to `plt` by convention.
# WHY:  imported at module top level, so this script cannot even be loaded
#       without matplotlib present — fine here, but note the whole module is
#       coupled to a GUI/plotting stack even for the parts that only move data.

import pandas as pd
# The dataframe library, aliased `pd` by convention. Used for all data handling.

import sys
# Standard library: gives access to sys.argv (the command-line arguments) below.

import re
# Standard library regular expressions. Used only by calculate_crew_size — which,
# as we will see, is never actually called (dead code, Step 6).


# --- orchestration ---------------------------------------------------------

def main(input_file, output_file, duration_by_astronaut_output_file, graph_file):
    # SMELL (-> Steps 2-5): this ONE function reads, writes, summarises, sorts and
    # plots. It has many reasons to change and is the hub everything couples to.
    # Parameters are positional with no types, so a caller must remember the order
    # of four file paths — easy to swap two by mistake.
    print("--START--")
    # SMELL (-> Step 7): progress is printed to stdout. There is no way to silence
    # or redirect it; `print` is a side channel, not configurable logging.

    eva_data = read_json_to_dataframe(input_file)
    # Calls the reader. Note `main` is glued to a function that hard-codes JSON;
    # there is no seam to substitute another source. (Inversion comes in Steps 4-5.)

    write_dataframe_to_csv(eva_data, output_file)
    # Writes the full table. Same helper is reused below for a different shape...

    duration_by_astronaut_df = summary_duration_by_astronaut(eva_data)
    # Computes the per-astronaut summary (returns a frame indexed by crew name).

    write_dataframe_to_csv(duration_by_astronaut_df, duration_by_astronaut_output_file)
    # SMELL (-> Step 3 result): the writer below always uses index=False. This
    # frame's astronaut names live in the INDEX, so they are silently dropped —
    # the summary file ends up with only a duration column. One rigid writer
    # forced onto two different data shapes produces a wrong file.

    eva_data.sort_values('date', inplace=True)
    # SMELL (-> Step 3): sorting (a data concern) sits in the orchestrator, and
    # `inplace=True` mutates the shared frame that earlier lines also used.

    plot_cumulative_time_in_space(eva_data, graph_file)
    print("--END--")


# --- reading + cleaning (two jobs in one) ----------------------------------

def read_json_to_dataframe(input_file):
    """Read the data from a JSON file into a Pandas dataframe and clean it."""
    # SMELL (-> Step 2): the name says "read", but this function reads AND coerces
    # a type AND drops rows AND prints. Four reasons to change in one place.
    print(f'Reading JSON file {input_file}')  # SMELL (-> Step 7): print side channel.

    eva_df = pd.read_json(input_file, convert_dates=['date'], encoding='ascii')
    # HOW: pandas parses the JSON, turning the 'date' strings into datetimes.
    # SMELL (-> Step 1): encoding='ascii' is a hard-coded, unstated assumption
    # about the input. It happens to work because the file stores non-ASCII as
    # \uXXXX escapes, but it is fragile and buried inside a function body.

    eva_df['eva'] = eva_df['eva'].astype(float)
    # HOW: converts the 'eva' id column from text to floating-point numbers.

    eva_df.dropna(axis=0, subset=['duration', 'date'], inplace=True)
    # HOW: drops any ROW (axis=0) where 'duration' or 'date' is missing.
    # SMELL (-> Step 2): `inplace=True` mutates in place; combined with the read,
    # the cleaning rule cannot be tested without also touching the filesystem.

    return eva_df


# --- writing ---------------------------------------------------------------

def write_dataframe_to_csv(df, output_file):
    """Write the dataframe to a CSV file."""
    print(f'Saving to CSV file {output_file}')  # SMELL (-> Step 7): print again.
    df.to_csv(output_file, index=False, encoding='utf-8')
    # HOW: writes the frame as CSV; index=False omits the row index.
    # SMELL (-> Step 4): the format choice (CSV) is welded in. Supporting another
    # output means editing this working function rather than adding a new one.
    # Note also: encoding here is 'utf-8' while the reader used 'ascii' — an
    # inconsistency that only stands out once both are visible settings.


# --- plotting (FOUR jobs in one) -------------------------------------------

def plot_cumulative_time_in_space(df, graph_file):
    """Plot the cumulative time spent in space over years."""
    print(f'Plotting cumulative spacewalk duration and saving to {graph_file}')

    df = add_duration_hours(df)
    # SMELL (-> Step 3): a function named "plot" secretly does ARITHMETIC. The
    # headline number (cumulative hours) is computed here, hidden inside drawing
    # code, so you cannot obtain or test the numbers without rendering a chart.
    df['cumulative_time'] = df['duration_hours'].cumsum()
    # HOW: `.cumsum()` produces a running total down the column.

    plt.plot(df['date'], df['cumulative_time'], 'ko-')
    # HOW: 'ko-' is a matplotlib format string: black ('k'), circle markers ('o'),
    # solid line ('-'). Drawing onto the global pyplot state (no explicit figure).
    plt.xlabel('Year')
    plt.ylabel('Total time spent in space to date (hours)')
    plt.tight_layout()

    plt.savefig(graph_file)
    # SMELL (-> Step 3): drawing AND saving in the same function — two jobs.
    plt.show()
    # SMELL (-> Steps 3 & 7): opens an interactive window and BLOCKS until a human
    # closes it. Fatal for an unattended/batch run; removed in the refactor.


# --- a pure helper (already reasonable) ------------------------------------

def text_to_duration(duration):
    """Convert a text format duration "HH:MM" to duration in hours."""
    hours, minutes = duration.split(":")
    # HOW: splits "HH:MM" on the colon into two strings and unpacks them.
    # SMELL (-> Step 9, correctness): assumes EXACTLY two parts. "1:23:45" unpacks
    # into three -> ValueError. Empty/missing values also raise. The refactor only
    # RENAMES this (parse_duration_to_hours) and isolates it; the fragility remains
    # to prove that structure is not correctness.
    duration_hours = int(hours) + int(minutes)/60
    # HOW: hours + minutes/60. Note int()/60 is float division in Python 3, so the
    # result is a float (e.g. "1:30" -> 1.5). The intermediate variable adds
    # nothing; Step 8 returns the expression directly for readability.
    return duration_hours


def add_duration_hours(df):
    """Add duration in hours (duration_hours) variable to the dataset."""
    df_copy = df.copy()
    # GOOD: copies before mutating, so the caller's frame is left intact. This is
    # the pattern the refactor applies consistently elsewhere.
    df_copy["duration_hours"] = df_copy["duration"].apply(
        text_to_duration
    )
    # HOW: `.apply(fn)` runs fn on every cell of the 'duration' column.
    return df_copy


# --- DEAD CODE: defined, documented, and never called ----------------------

def calculate_crew_size(crew):
    """Calculate the size of the crew for a single crew entry."""
    # SMELL (-> Step 6): this function is never called anywhere in the script.
    if crew.split() == []:
        # HOW: `crew.split()` with no args splits on whitespace; an all-blank
        # string yields [], i.e. "no real content" -> return None.
        return None
    else:
        return len(re.split(r';', crew))-1
        # HOW: splits on ';' and subtracts 1 for the trailing empty piece after
        # the final ';'. SMELL (-> Step 9, correctness): a DOUBLE ';;' (as in the
        # real "Harrison Schmidt;Eugene Cernan;;") leaves two trailing empties, so
        # this returns 3 for a 2-person crew. summary_duration_by_astronaut below
        # counts crew a DIFFERENT way and does not share the bug — an inconsistency.

def add_crew_size_column(df):
    """Add crew_size column to the dataset containing the value of the crew size."""
    # SMELL (-> Step 6): also never called. Dead code is a tax: a reader must study
    # it to confirm it is safe to ignore, and it is never exercised so it can rot.
    print('Adding crew size variable (crew_size) to dataset')
    df_copy = df.copy()
    df_copy["crew_size"] = df_copy["crew"].apply(
        calculate_crew_size
    )
    return df_copy


# --- the per-astronaut summary ---------------------------------------------

def summary_duration_by_astronaut(df):
    """Summarise the duration data by each astronaut."""
    # NOTE the docstring claims it "saves resulting table to a CSV file" — it does
    # NOT. SMELL (-> Step 8): documentation that lies is worse than none; a reader
    # trusts it and is misled.
    subset = df.loc[:,['crew', 'duration']]
    # HOW: `.loc[:, [cols]]` selects all rows, two columns. SMELL: this is a VIEW/
    # slice; the next line assigns back into `subset.crew`, which can trigger
    # pandas' SettingWithCopyWarning. The refactor adds an explicit `.copy()`.
    subset.crew = subset.crew.str.split(';').apply(lambda x: [i for i in x if i.strip()])
    # HOW (read inside-out): `.str.split(';')` turns "A;B;" into ["A","B",""];
    # the list comprehension `[i for i in x if i.strip()]` drops blank pieces
    # (handling the trailing ';' AND the double ';;' correctly — unlike
    # calculate_crew_size above). This is the GOOD crew-splitting approach.
    subset = subset.explode('crew')
    # HOW: `.explode` turns each list of names into one row per name, duplicating
    # the duration alongside each crew member.
    subset = add_duration_hours(subset)
    # Reuse the helper to add numeric hours.
    subset = subset.drop('duration', axis=1)
    # HOW: drop the original text duration column (axis=1 = a column); it cannot
    # be summed.
    subset = subset.groupby('crew').sum()
    # HOW: group rows by astronaut and sum the numeric columns -> total hours each.
    # SMELL (-> Step 3 result): the result is INDEXED by crew name. Because the
    # shared writer uses index=False, those names are dropped when saved.
    return subset


# --- script entry point ----------------------------------------------------

if __name__ == "__main__":
    # WHAT: this block runs only when the file is executed directly (not imported).
    # HOW: when imported, Python sets __name__ to the module name, so this is
    # skipped; when run as `python eva_data_analysis.py`, __name__ == "__main__".

    if len(sys.argv) < 3:
        # HOW: sys.argv is [program_name, arg1, arg2, ...]; fewer than 3 entries
        # means the user gave fewer than two arguments, so fall back to defaults.
        input_file = 'data/eva-data.json'
        output_file = 'results/eva-data.csv'
        # SMELL (-> Step 1): file paths hard-coded as literals here, mixed in with
        # control flow. Configuration is not separated from logic.
        print(f'Using default input and output filenames')
        # (Minor) this f-string has no {placeholder}; the `f` prefix is pointless.
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print('Using custom input and output filenames')

    graph_file = 'results/cumulative_eva_graph.png'
    duration_by_astronaut_output_file = 'results/duration_by_astronaut.csv'
    # SMELL (-> Step 1): two more hard-coded paths, and the argument parsing logic
    # is hand-rolled. The refactor moves all of this to a config object + argparse.

    main(input_file, output_file, duration_by_astronaut_output_file, graph_file)
    # Hands the four paths to main() in a fixed order — the positional coupling
    # the refactor removes by passing a single AnalysisConfig object.
