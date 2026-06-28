# Code Smell Analysis by Claude:  `eva_data_analysis.py`

**Analysed file:** `eva_data_analysis.py` (193 lines)
**Taxonomy reference:** `Smells.md`
**Method:** Each line/construct was inspected against the categories in the taxonomy. Definitions are quoted from `Smells.md`. Findings are ordered by line number. A single construct may appear more than once where it exhibits distinct smells.

---

## Smell Register (ordered by line number)

| Line(s) | Smell Type | Definition (from Smells.md) | Implication | Impact | Solution |
|--------|-----------|------------------------------|-------------|--------|----------|
| 7 | Long Parameter List | A function requiring many parameters to operate. | `main()` takes four positional file-path arguments; call sites must remember order and meaning. | Easy to transpose arguments (e.g. swap two output paths) with no error raised; poor readability. | Group related paths into a small config object / dataclass (e.g. `Paths(input, csv, summary, graph)`), or pass a config dict. |
| 7 | Data Clumps | Groups of variables that repeatedly appear together. | `input_file`, `output_file`, `duration_by_astronaut_output_file`, `graph_file` always travel together through `main`. | Duplicated knowledge of "the set of I/O paths"; any new path means editing the signature everywhere. | Introduce a single `Paths`/config object that bundles all I/O locations. |
| 7–27 | Divergent Change | A class changes for many unrelated reasons. (applied at function level) | `main` orchestrates reading, CSV export, summarising, sorting and plotting — several unrelated responsibilities in one place. | Changes to plotting, I/O format, or summary logic all force edits to `main`. | Keep `main` as a thin orchestrator; ensure each step is fully delegated and side-effect-free where possible. |
| 33 / 46 | Misleading Comment | Documentation contradicts or obscures the implementation. | Docstring (line 33) states only rows with missing `duration` are removed, but line 46 also drops rows missing `date`. | Developers under-estimate what data is discarded; silent data loss on the `date` column. | Update the docstring to state both `duration` and `date` are required, or make the cleaning rule a documented parameter. |
| 43 | Hard-coded Setting | Configuration values embedded directly within source code. | `encoding='ascii'` is fixed; any non-ASCII astronaut name (accents, diacritics) will fail to parse. | Environment-/data-specific read failures; reduced portability. | Default to `utf-8` and/or expose `encoding` as a parameter. |
| 44 | Hidden Side Effects | A function performs unexpected modifications beyond its stated purpose. | The `eva` column is silently coerced to `float`; this transformation is not mentioned in the docstring (which claims only "read + clean"). | Undocumented schema mutation surprises callers and complicates debugging. | Document the coercion, or move type-normalisation into a clearly named separate step. |
| 50–63 | Lazy Class / Middle Man | A class providing too little functionality to justify its existence. / A class delegates nearly all work to another class. | `write_dataframe_to_csv` adds only a `print` over `df.to_csv`; it is a thin pass-through wrapper. | Marginal indirection; debatable value. (Mild — acceptable if standardising logging.) | Keep only if it centralises logging/encoding policy; otherwise call `to_csv` directly. |
| 63 | Hard-coded Setting | Configuration values embedded directly within source code. | `encoding='utf-8'` fixed at write time (inconsistent with the `ascii` read on line 43). | Read/write encodings can silently disagree; reduced flexibility. | Parameterise encoding and keep read/write defaults consistent. |
| 66–90 | Long Method / Divergent Change | A method that has grown too large and performs multiple responsibilities. | `plot_cumulative_time_in_space` performs data transformation (add hours, cumulative sum) **and** rendering in one function. | Cannot reuse the cumulative-time calculation without triggering plotting; harder to test. | Split into `compute_cumulative_time(df)` (pure) and a thin `plot(df)` that only renders. |
| 84 | Magic Values | Numeric or string literals appear without explanation. | Column-name string literals (`'cumulative_time'`, `'duration_hours'`, `'date'`) are scattered as bare strings. | Typos surface only at runtime; renames require shotgun edits. | Define column names as module constants or an enum. |
| 84 | Hidden Side Effects | A function performs unexpected modifications beyond its stated purpose. | A new `cumulative_time` column is written into the dataframe; not stated in the docstring's purpose ("plot … and save"). | Caller's dataframe shape changes unexpectedly (mitigated here by the earlier copy on line 83, but undocumented). | Compute on an explicit local copy and document any returned/mutated structure. |
| 85 | Magic Values | Numeric or string literals appear without explanation. | `'ko-'` (black, circle marker, solid line) is an unexplained Matplotlib format string. | Intent of the style code is opaque to non-Matplotlib readers. | Use named keyword args (`color='black', marker='o', linestyle='-'`) or a named style constant. |
| 86 | Misleading Comment / Poor Naming | Documentation contradicts or obscures the implementation. / Variables, methods, or classes fail to communicate intent. | X-axis label is `'Year'`, but the plotted x-values are full `date` values, not years. | Chart mislabels the axis, misleading readers of the output. | Label the axis `'Date'`, or aggregate/format the x-values to actual years. |
| 85–90 | Static Dependencies / Global Mutable State | Static/global resources prevent isolated testing. / Shared mutable variables accessible throughout the program. | Uses the global `pyplot` state machine (`plt.plot/xlabel/savefig/show`) rather than explicit `fig, ax`. | Concurrent/repeated plots share hidden global state; very hard to unit-test in isolation. | Use the object-oriented API: `fig, ax = plt.subplots()` and operate on `ax`. |
| 90 | Hidden Side Effects / Non-deterministic Behaviour | A function performs unexpected modifications beyond its stated purpose. / Code produces different outputs under identical inputs. | `plt.show()` opens an interactive window; the docstring only promises to *save* the figure. | Blocks/raises in headless or CI environments; behaviour differs by environment. | Remove `plt.show()` from the save routine, or gate it behind an explicit `show=False` flag. |
| 104 | Magic Values | Numeric or string literals appear without explanation. | Literal `60` (minutes per hour) embedded in the conversion arithmetic. | Meaning relies on the reader inferring the unit conversion. | Replace with a named constant, e.g. `MINUTES_PER_HOUR = 60`. |
| 103–104 | Improper Exception Cleanup / Hidden Side Effects | Exceptions bypass resource cleanup. (here: unguarded parsing) | No validation: a malformed `duration` (missing `:`, non-numeric) raises an unhandled `ValueError`. | Single bad record aborts the whole pipeline. | Validate input / wrap in a guarded parse and skip or log bad rows. |
| 125–155 | Dead Code | Code that is never executed or no longer contributes functionality. | `calculate_crew_size` and `add_crew_size_column` are defined but never called from `main` or anywhere else. | Maintenance cost and confusion; readers assume crew-size is computed when it is not. | Remove if unused, or wire `add_crew_size_column` into the pipeline if intended. |
| 138 | Magic Values | Numeric or string literals appear without explanation. | The trailing `-1` corrects for an assumed trailing `;` in the crew string — an unexplained, fragile offset. | Breaks silently if the trailing-`;` convention ever changes; off-by-one risk. | Filter empty splits explicitly (as done on line 170) instead of subtracting a magic offset. |
| 138 | Speculative Generality | Abstractions created for anticipated future requirements that never occur. | `re.split(r';', crew)` uses the `re` engine for a plain single-character delimiter. | Needless dependency/complexity over a simple `crew.split(';')`. | Use `crew.split(';')`; this also makes `import re` (line 4) removable. |
| 138 & 170 | Repeated Knowledge / Duplicate Code | Business rules or algorithms implemented multiple times, even if written differently. / Identical or nearly identical code appears in multiple places. | Crew-string parsing (split on `;`, handle blanks) is implemented twice in **two different ways** (line 138 vs line 170). | Inconsistent results if only one copy is fixed; divergent edge-case handling. | Extract one shared `parse_crew(crew) -> list[str]` helper used by both. |
| 160 | Misleading Comment | Documentation contradicts or obscures the implementation. | Docstring claims the function "saves resulting table to a CSV file"; it does not save — it only returns a dataframe. | Reader expects a side-effecting save that never happens. | Correct the docstring to describe a pure summarise-and-return. |
| 167 | Misleading Comment / Poor Naming | Documentation contradicts or obscures the implementation. / Variables fail to communicate intent. | Docstring documents a return value named `sum_by_astro`, but the function actually returns `subset`. | Documentation drifts from code; readers search for a non-existent variable. | Align names: rename the local to `sum_by_astro` (also clearer intent) and update the docstring. |
| 169–174 | Magic Values / Primitive Obsession | Numeric or string literals appear without explanation. / Primitive types used instead of meaningful domain objects. | Bare column strings `'crew'`, `'duration'`, `'duration_hours'` repeated; raw string manipulation models a domain concept (crew membership). | Typo-prone, and the crew abstraction is only ever a delimited string. | Centralise column names as constants; model crew parsing in one helper. |
| 180 | Magic Values | Numeric or string literals appear without explanation. | `len(sys.argv) < 3` uses a bare `3` to mean "input + output supplied". | Intent unclear; brittle if argument handling changes. | Use a named constant or, better, an argument parser (`argparse`). |
| 181–182, 189–190 | Hard-coded File Path | Absolute or fixed file paths within source code. | Default input/output/graph/summary paths are fixed strings in the entry block. | Environment-specific failures; not relocatable without code edits. | Move defaults to config/CLI arguments (`argparse` with defaults). |
| 183 | Dead Code | Code that is never executed or no longer contributes functionality. | `f'Using default input and output filenames'` is an f-string with no interpolation fields. | Harmless but signals copy-paste; misleads readers into looking for a substitution. | Drop the `f` prefix (plain string). |
| 189–190 | Hard-coded Setting | Configuration values embedded directly within source code. | `graph_file` and `duration_by_astronaut_output_file` are **not** overridable even when custom `input_file`/`output_file` are supplied via argv. | Inconsistent configurability; users supplying custom paths still get hard-coded outputs. | Expose all four paths through the same argument-parsing mechanism. |

---

## Summary by Category

| Category | Count | Representative lines |
|----------|-------|----------------------|
| Configuration (Hard-coded Setting / File Path) | 6 | 43, 63, 181–182, 189–190 |
| Data (Magic Values / Primitive Obsession) | 7 | 84, 85, 104, 138, 169–174, 180 |
| Maintainability (Misleading Comment, Poor Naming, Dead Code, Divergent Change) | 8 | 33/46, 86, 125–155, 160, 167, 183 |
| Testing (Hidden Side Effects, Static Dependencies, Non-deterministic) | 5 | 44, 84, 85–90, 90 |
| Duplication (Repeated Knowledge / Duplicate Code) | 1 | 138 & 170 |
| Size (Long Method, Long Parameter List, Data Clumps) | 4 | 7, 7–27, 66–90 |
| Abstraction (Lazy Class, Speculative Generality) | 2 | 50–63, 138 |
| Resources (Improper Exception Cleanup) | 1 | 103–104 |

## Highest-Leverage Fixes

A handful of changes resolve clusters of related smells:

1. **Extract a single `parse_crew()` helper** — removes the duplicate/repeated-knowledge pair (lines 138 & 170), the `-1` magic offset, the speculative `re.split`, and lets you drop `import re`.
2. **Split `plot_cumulative_time_in_space` into a pure calculation + a thin renderer using the OO Matplotlib API**, and remove `plt.show()` — clears the Long Method, hidden side effect, non-deterministic, and static-dependency smells around lines 66–90 in one pass.
3. **Introduce a config/`argparse` layer for all four paths** — removes the Long Parameter List, Data Clumps, hard-coded paths, the inconsistent-config setting (189–190), and the `< 3` magic number.
4. **Reconcile docstrings with behaviour** (lines 33/46, 160, 167) — removes the misleading-comment cluster with no behavioural risk.
5. **Define column-name and unit constants** — clears the recurring magic-value/primitive-obsession findings (84, 85, 104, 169–174).

---

*Note (per `Smells.md`): code smells are maintainability indicators, not functional defects. Several findings above (e.g. the `write_dataframe_to_csv` wrapper) are mild and warrant developer judgement before refactoring.*
