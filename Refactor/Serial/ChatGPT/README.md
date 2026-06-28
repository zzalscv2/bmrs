# Annotated SOLID/ISO 25010 EVA analysis refactor

This is a multi-file refactor of `eva_data_analysis.py`.

Run it from the project root with:

```bash
python run_eva_analysis.py
```

or:

```bash
python -m eva_analysis.cli
```

Optional arguments:

```bash
python run_eva_analysis.py data/eva-data.json results/eva-data.csv \
  --astronaut-summary-file results/duration_by_astronaut.csv \
  --graph-file results/cumulative_eva_graph.png
```

The code is deliberately annotated with detailed comments explaining both what each line does and why it supports maintainability, SRP, dependency inversion, testability or clearer analysis.
