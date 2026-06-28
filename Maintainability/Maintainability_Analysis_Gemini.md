# Maintainability Analysis

This report outlines the structural maintainability analysis of `eva_data_analysis.py` based on the **ISO/IEC 25010:2023** system and software quality models.

## Identified Violations and Threats

| Line | Characteristic | ISO 25010 Definition | Implication | Impact | Solution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **8** | **Analysability** | Capability of a product to be effectively and efficiently assessed regarding the impact of an intended change to one or more of its parts, to diagnose it for deficiencies or causes of failures, or to identify parts to be modified. | Using `print("--START--")` (and elsewhere) instead of a standard logging framework makes it difficult to diagnose failures, track execution context, or redirect outputs for system monitoring. | Medium | Replace `print()` statements with Python's standard `logging` module, utilizing appropriate log levels (INFO, DEBUG, ERROR). |
| **67** | **Testability** | capability of a product to enable an objective and feasible test to be designed and performed to determine whether a requirement is met | The synchronous, blocking `plt.show()` call pauses script execution. This prevents automated headless unit/integration tests from running without manual intervention. | High | Remove `plt.show()` or place it behind a conditional flag (e.g., `if interactive:`), allowing tests to complete unattended. |
| **81** | **Analysability** | Capability of a product to be effectively and efficiently assessed regarding the impact of an intended change... to diagnose it for deficiencies or causes of failures... | The `duration.split(":")` assignment in `text_to_duration` assumes perfect formatting. Malformed data will cause an unhandled `ValueError`, obfuscating the exact cause and location of the data deficiency. | High | Wrap the string manipulation in a `try...except` block, log the specific parsing error, and handle or skip malformed rows gracefully. |
| **115** | **Analysability** | Capability of a product to be effectively and efficiently assessed regarding the impact of an intended change to one or more of its parts... or to identify parts to be modified. | `add_crew_size_column(df)` is never called within the script execution pipeline (dead code). This increases cognitive load and complicates the assessment of which parts actually need to be modified. | Low | Remove the unused function from the codebase or integrate it into the `main()` data transformation workflow if the business logic requires it. |
| **155** | **Modifiability** | Capability of a product to be effectively and efficiently modified without introducing defects or degrading existing product quality. | Manual `sys.argv` positional checks (`if len(sys.argv) < 3:`) are brittle. Adding or removing arguments in the future is likely to introduce parameter-parsing defects. | Medium | Refactor the command-line interface to use Python's built-in `argparse` module, which handles edge cases and typing automatically. |
| **162** | **Reusability** | Capability of a product to be used as assets in more than one system, or in building other assets | Paths for `graph_file` and `duration_by_astronaut_output_file` are strictly hardcoded. The script cannot be reused in an environment with a different directory structure without modifying the source code. | Medium | Parameterize all input and output file paths via `argparse`, providing these hardcoded strings strictly as default fallback values. |

***

*Analysis generated automatically referencing ISO/IEC 25010:2023.*
