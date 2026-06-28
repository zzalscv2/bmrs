# Maintainability Analysis by Claude: `eva_data_analysis.py`

**Reference standard:** ISO/IEC 25010:2023 maintainability characteristic and its sub‑characteristics, as defined in `ISO250102023.md` (Maintainability, Modularity, Reusability, Analysability, Modifiability, Testability).

**Method:** Each construct in `eva_data_analysis.py` was assessed against the six maintainability characteristics. Both confirmed **violations** (the code already breaches the characteristic) and **threats** (latent weaknesses that will breach it under foreseeable change) are recorded. Rows are ordered by line number. Line references match the script as supplied.

---

## Definitions used (from ISO250102023.md)

| Characteristic | Definition (paraphrased from the standard) |
|---|---|
| **Maintainability** | Capability of a product to be modified by intended maintainers with effectiveness and efficiency. |
| **Modularity** | Capability of a product to limit changes in one component from affecting other components (cohesive modules, minimal coupling). |
| **Reusability** | Capability of a product to be used as an asset in more than one system, or in building other assets. |
| **Analysability** | Capability of a product to be assessed for the impact of a change, diagnosed for defects/causes of failure, or have parts to be modified identified. |
| **Modifiability** | Capability of a product to be modified without introducing defects or degrading existing quality (a combination of changeability and stability). |
| **Testability** | Capability of a product to enable an objective and feasible test to be designed and performed to determine whether a requirement is met. |

---

## Violations and threats (ordered by line number)

| Line(s) | Type | Definition (short) | Occurrence — Violation / Threat | Implication | Impact | Solution |
|---|---|---|---|---|---|---|
| 7 | Modularity | Limit changes in one component from affecting others | `main()` orchestrates reading, CSV export, summarising, sorting and plotting in one function (low cohesion / multiple responsibilities). | A change to any single step sits in the same unit as every other step. | Edits ripple; high chance of unintended breakage; hard to reason about. | Compose a thin pipeline that calls focused single‑responsibility functions; keep `main()` to wiring only. |
| 8, 27, 41, 61, 82, 150, 183, 187 | Analysability | Diagnose deficiencies / assess change | Diagnostics emitted via `print()` rather than the `logging` module. | No severity levels, no routing, cannot be silenced or filtered. | Faults are hard to trace; noisy or missing context during diagnosis. | Replace prints with `logging` (levels, handlers, configurable verbosity). |
| 22 | Modifiability | Modify without introducing defects | `eva_data.sort_values('date', inplace=True)` mutates the shared frame in place **and** establishes a hidden ordering dependency required by the later cumulative plot. | The plot at line 84 silently assumes this sort already happened. | Removing/reordering this line breaks `cumulative_time` without an error. | Return a sorted copy; have the plotting function sort its own data, or document the contract explicitly. |
| 22, 43, 44, 46, 84, 119, 152, 169, 174 | Modifiability | Changeability + stability | Column names (`'date'`, `'duration'`, `'eva'`, `'crew'`, `'duration_hours'`, `'cumulative_time'`, `'crew_size'`) are hardcoded magic strings scattered throughout. | A schema/column rename must be found and edited in many places. | Easy to miss an occurrence; partial edits introduce defects. | Define column‑name constants (or a schema/config object) and reference them everywhere. |
| 43 | Reusability | Usable across more than one system | `pd.read_json(..., encoding='ascii')` hardcodes ASCII encoding. | Non‑ASCII astronaut names / international data cannot be read. | Data‑dependent crashes; unusable for other datasets. | Use `utf-8` and/or parameterise the encoding. |
| 44 | Analysability | Diagnose causes of failure | `eva_df['eva'].astype(float)` silently assumes the `'eva'` column exists and is convertible; no guard. | Failure surfaces as an opaque pandas/cast error far from the cause. | Difficult root‑cause analysis. | Validate the schema up front; wrap with a clear, contextual error. |
| 46 | Modifiability | Changeability + stability | `dropna(..., inplace=True)` mutates the input frame in place. | Hidden state change to a caller‑owned object. | Surprising side effects when the function is reused or reordered. | Assign the result (`df = df.dropna(...)`) and avoid `inplace`. |
| 66, 84 | Modularity / Testability | Cohesion; enable feasible test | `plot_cumulative_time_in_space()` mixes the cumulative‑sum **computation** (line 84) with **presentation**. | The calculation cannot be exercised without rendering a chart. | Core logic is untestable in isolation; presentation and analytics are coupled. | Extract the cumulative calculation into its own pure function; plot the result. |
| 85–89 | Modularity / Reusability | Minimal coupling; reuse as asset | Plotting drives global `pyplot` state (`plt.plot`, `plt.xlabel`, …) instead of an explicit `fig, ax`. | Global state couples calls together and leaks between invocations. | Not composable/reusable; figures interfere across runs. | Use `fig, ax = plt.subplots()` and draw on `ax`. |
| 90 | Testability | Enable objective, feasible test | `plt.show()` is a blocking GUI side effect inside a batch script, and no `plt.close()` is called. | Blocks headless/automated execution; figures accumulate in memory. | Cannot run unattended/in tests; resource leak. | Remove/guard `plt.show()`; close the figure after saving. |
| 103 | Testability / Analysability | Feasible test; diagnose failure | `hours, minutes = duration.split(":")` assumes a well‑formed `"HH:MM"` string with no validation. | Malformed/missing values raise `ValueError`/unpacking errors. | Brittle; crashes are hard to attribute to bad input. | Validate format (regex / try‑except) and return a clear error or `NaN`. |
| 125–138 | Analysability / Modifiability | Identify parts to modify; modify safely | `calculate_crew_size` uses `len(re.split(r';', crew)) - 1`, assuming a trailing `;`; `re` is unnecessary and the `crew.split() == []` check is convoluted. | Logic is hard to follow and silently wrong if the trailing‑`;` assumption breaks. | Incorrect crew counts with no error. | Simplify to `[c for c in crew.split(';') if c.strip()]` and count that; share with line 170. |
| 138, 170 | Modularity | Avoid duplicated/divergent logic | Crew‑string parsing is implemented **twice and differently** (trailing‑`;` count at 138 vs. blank‑filtering split at 170). | Two sources of truth for the same operation. | Divergent behaviour and double maintenance; bug‑prone. | Extract one shared crew‑parsing helper and call it from both sites. |
| 140 (and 125, 152) | Analysability / Modifiability | Identify parts; reduce clutter | `add_crew_size_column` (and its only caller of `calculate_crew_size`) is **never invoked** anywhere — dead code. | Maintainers must reason about code that does nothing. | Wasted effort, false impression of functionality. | Remove the dead code, or wire it into the pipeline if intended. |
| 158–167 | Analysability | Accurate basis for assessment | Docstring claims the function "saves resulting table to a CSV file" (it does not) and names the return `sum_by_astro` while the code returns `subset`. | Documentation contradicts behaviour. | Maintainers act on false assumptions. | Correct the docstring to match actual behaviour and variable names. |
| 170 | Modifiability / Analysability | Stability; diagnose failure | `subset.crew = …` assigns onto a `.loc` slice, risking `SettingWithCopyWarning`; over‑long inline comments reduce readability. | Pandas may operate on a view/copy unpredictably. | Subtle, environment‑dependent bugs and warnings. | Take an explicit `.copy()` and use `.assign()`/clear column ops. |
| 174 | Modifiability | Changeability + stability | `groupby('crew').sum()` implicitly relies on `duration_hours` being the only remaining numeric column (after the line‑173 drop). | Adding any numeric column changes the result silently. | Fragile aggregation; hidden coupling to upstream drops. | Aggregate the named column explicitly (e.g. `[['duration_hours']].sum()`). |
| 180 | Testability / Modifiability | Feasible test; safe extension | CLI handled by ad‑hoc `len(sys.argv) < 3` checks rather than `argparse`. | No validation, help text, or clean way to add arguments. | Hard to test/extend the entry point. | Use `argparse` with typed, documented options. |
| 181–182, 189–190 | Reusability / Modifiability | Reuse as asset; changeability | File paths are hardcoded magic strings, and `graph_file` / `duration_by_astronaut_output_file` are **always** hardcoded while input/output come from argv — inconsistent. | Relocating outputs requires editing source; interface is inconsistent. | Not portable/reusable across environments. | Parameterise all paths via args/config; apply the convention uniformly. |
| Throughout (e.g. 43, 44, 46, 103, 119) | Analysability | Diagnose causes of failure | No error handling around any I/O, parsing, or type conversion. | Failures surface as raw tracebacks with no domain context. | Slow, error‑prone diagnosis. | Add targeted `try/except` with meaningful, contextual messages. |
| Whole file | Testability | Enable objective, feasible test | No automated tests, no type hints, and logic entangled with side effects (global pyplot, prints, `inplace`). | Behaviour cannot be objectively verified; regressions go unnoticed. | Every change is high‑risk. | Add unit tests for the pure functions; add type hints; isolate side effects. |

---

## Summary

The dominant maintainability weaknesses are: (1) **Modularity** — `main()` and the plotting function carry multiple responsibilities and lean on global `pyplot` state; (2) **Modifiability** — pervasive magic strings for column names/paths plus `inplace` mutation and hidden ordering dependencies; (3) **Analysability** — `print`‑based diagnostics, absent error handling, dead code, and a docstring that contradicts the code; and (4) **Testability** — computation fused with presentation, a blocking `plt.show()`, and no tests.

The highest‑leverage fixes are to **separate computation from I/O/presentation**, **centralise column names and paths as configuration/constants**, **replace `print` with `logging` and add error handling**, and **remove dead/duplicated crew‑parsing logic** in favour of a single shared helper. These directly raise modularity, modifiability, analysability, and testability together.
