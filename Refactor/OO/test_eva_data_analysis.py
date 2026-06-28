"""Unit and integration tests for the ``eva_analysis`` package.

The suite is organised by collaborator. Pure-logic classes are tested in
isolation; the ``EvaAnalysisPipeline`` controller is tested with lightweight
test doubles (fakes/spies) so its orchestration can be verified without
touching the filesystem or matplotlib — a direct payoff of dependency
injection.
"""

import matplotlib

# Force a non-interactive backend before the module under test imports pyplot.
matplotlib.use("Agg")

import pandas as pd
import pytest

import eva_analysis as eva
from eva_analysis import plotting
import eva_data_analysis as entry


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
class TestReporters:
    def test_console_reporter_writes_to_stdout(self, capsys):
        eva.ConsoleReporter().report("hello")
        assert capsys.readouterr().out == "hello\n"

    def test_null_reporter_is_silent(self, capsys):
        eva.NullReporter().report("hello")
        assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- #
# Domain logic
# --------------------------------------------------------------------------- #
class TestTextDurationConverter:
    @pytest.mark.parametrize(
        "text, expected",
        [("0:00", 0.0), ("1:30", 1.5), ("2:00", 2.0), ("10:15", 10.25), ("0:36", 0.6)],
    )
    def test_to_hours(self, text, expected):
        assert eva.TextDurationConverter().to_hours(text) == pytest.approx(expected)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            eva.TextDurationConverter().to_hours("90 minutes")


class TestSemicolonCrewSizeCalculator:
    def setup_method(self):
        self.calc = eva.SemicolonCrewSizeCalculator()

    def test_single_member_trailing_semicolon(self):
        assert self.calc.size("Ed White;") == 1

    def test_multiple_members(self):
        assert self.calc.size("Bob;Alice;") == 2

    def test_blank_entry_returns_none(self):
        assert self.calc.size("   ") is None

    def test_empty_string_returns_none(self):
        assert self.calc.size("") is None


# --------------------------------------------------------------------------- #
# Transformations
# --------------------------------------------------------------------------- #
class TestEvaDataCleaner:
    def test_drops_rows_missing_duration_or_date_and_coerces_eva(self):
        df = pd.DataFrame(
            {
                "eva": ["1", "2", "3"],
                "duration": ["1:00", None, "2:00"],
                "date": [pd.Timestamp("2000-01-01"), pd.Timestamp("2000-02-01"), pd.NaT],
            }
        )
        out = eva.EvaDataCleaner().transform(df)
        assert list(out["eva"]) == [1.0]
        assert out["eva"].dtype == float

    def test_does_not_mutate_input(self):
        df = pd.DataFrame(
            {"eva": ["1"], "duration": ["1:00"], "date": [pd.Timestamp("2000-01-01")]}
        )
        eva.EvaDataCleaner().transform(df)
        assert df["eva"].tolist() == ["1"]


class TestCumulativeDurationTransformer:
    def test_sorts_and_accumulates(self):
        df = pd.DataFrame(
            {
                "duration": ["2:00", "1:30"],
                "date": [pd.Timestamp("2000-02-01"), pd.Timestamp("2000-01-01")],
            }
        )
        out = eva.CumulativeDurationTransformer(eva.TextDurationConverter()).transform(df)
        assert out["duration_hours"].tolist() == [1.5, 2.0]
        assert out["cumulative_time"].tolist() == [1.5, 3.5]

    def test_does_not_mutate_input(self):
        df = pd.DataFrame({"duration": ["1:00"], "date": [pd.Timestamp("2000-01-01")]})
        eva.CumulativeDurationTransformer(eva.TextDurationConverter()).transform(df)
        assert "cumulative_time" not in df.columns


class TestCrewSizeTransformer:
    def test_adds_crew_size_column(self):
        df = pd.DataFrame({"crew": ["Ed White;", "Bob;Alice;", "   "]})
        transformer = eva.CrewSizeTransformer(
            eva.SemicolonCrewSizeCalculator(), eva.NullReporter()
        )
        out = transformer.transform(df)
        assert out["crew_size"].tolist()[:2] == [1, 2]
        assert pd.isna(out["crew_size"].tolist()[2])


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #
class TestAstronautDurationSummariser:
    def test_sums_hours_per_individual_astronaut(self):
        df = pd.DataFrame({"crew": ["Alice;", "Bob;Alice;"], "duration": ["1:30", "2:00"]})
        summary = eva.AstronautDurationSummariser(
            eva.TextDurationConverter()
        ).summarise(df)
        # crew is a regular column now (the bug fix), not the index.
        assert "crew" in summary.columns
        indexed = summary.set_index("crew")
        assert indexed.loc["Alice", "duration_hours"] == pytest.approx(3.5)
        assert indexed.loc["Bob", "duration_hours"] == pytest.approx(2.0)
        assert "duration" not in summary.columns


# --------------------------------------------------------------------------- #
# I/O
# --------------------------------------------------------------------------- #
class TestJsonEvaDataSource:
    def test_reads_records_and_parses_dates(self, tmp_path):
        json_file = tmp_path / "eva.json"
        json_file.write_text(
            '[{"eva": "1", "crew": "Alice;", '
            '"date": "2000-01-01T00:00:00.000", "duration": "1:30"}]'
        )
        df = eva.JsonEvaDataSource(str(json_file), eva.NullReporter()).read()
        assert len(df) == 1
        assert df["date"].dtype.kind == "M"


class TestCsvDataSink:
    def test_writes_csv_without_index(self, tmp_path):
        out = tmp_path / "out.csv"
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        eva.CsvDataSink(eva.NullReporter()).write(df, str(out))
        reloaded = pd.read_csv(out)
        assert reloaded.columns.tolist() == ["a", "b"]
        assert reloaded["a"].tolist() == [1, 2]


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #
class TestCumulativeTimePlotter:
    def test_saves_figure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(plotting.plt, "show", lambda *a, **k: None)
        out = tmp_path / "graph.png"
        df = pd.DataFrame(
            {
                "date": [pd.Timestamp("2000-01-01"), pd.Timestamp("2000-02-01")],
                "cumulative_time": [1.5, 3.5],
            }
        )
        eva.CumulativeTimePlotter(eva.NullReporter()).plot(df, str(out))
        assert out.exists() and out.stat().st_size > 0


# --------------------------------------------------------------------------- #
# Configuration (CLI parsing now lives in CliConfigFactory)
# --------------------------------------------------------------------------- #
class TestCliConfigFactory:
    def _factory(self):
        return eva.CliConfigFactory(eva.NullReporter())

    def test_defaults_when_too_few_args(self):
        config = self._factory().from_args(["prog"])
        assert config.input_file == "data/eva-data.json"
        assert config.output_file == "results/eva-data.csv"

    def test_custom_args(self):
        config = self._factory().from_args(["prog", "in.json", "out.csv"])
        assert config.input_file == "in.json"
        assert config.output_file == "out.csv"
        assert config.graph_file == "results/cumulative_eva_graph.png"

    def test_reports_which_filenames_were_used(self):
        class _Spy(eva.Reporter):
            def __init__(self):
                self.messages = []

            def report(self, message):
                self.messages.append(message)

        spy = _Spy()
        eva.CliConfigFactory(spy).from_args(["prog"])
        assert spy.messages == ["Using default input and output filenames"]


# --------------------------------------------------------------------------- #
# Controller — orchestration verified with test doubles
# --------------------------------------------------------------------------- #
class _FakeSource(eva.DataSource):
    def __init__(self, data):
        self._data = data
        self.read_calls = 0

    def read(self):
        self.read_calls += 1
        return self._data


class _SpyTransformer(eva.DataTransformer):
    def __init__(self, output):
        self._output = output
        self.received = []

    def transform(self, df):
        self.received.append(df)
        return self._output


class _SpySink(eva.DataSink):
    def __init__(self):
        self.writes = []

    def write(self, df, destination):
        self.writes.append((df, destination))


class _SpySummariser(eva.DurationSummariser):
    def __init__(self, output):
        self._output = output
        self.received = []

    def summarise(self, df):
        self.received.append(df)
        return self._output


class _SpyPlotter(eva.Plotter):
    def __init__(self):
        self.calls = []

    def plot(self, df, destination):
        self.calls.append((df, destination))


class _SpyReporter(eva.Reporter):
    def __init__(self):
        self.messages = []

    def report(self, message):
        self.messages.append(message)


class TestEvaAnalysisPipeline:
    def _make(self):
        config = eva.PipelineConfig(
            input_file="in.json",
            output_file="out.csv",
            duration_by_astronaut_file="astro.csv",
            graph_file="graph.png",
        )
        d = {"raw": "RAW", "cleaned": "CLEANED", "summary": "SUMMARY", "cumulative": "CUMULATIVE"}
        source = _FakeSource(d["raw"])
        cleaner = _SpyTransformer(d["cleaned"])
        sink = _SpySink()
        summariser = _SpySummariser(d["summary"])
        cumulative = _SpyTransformer(d["cumulative"])
        plotter = _SpyPlotter()
        reporter = _SpyReporter()
        pipeline = eva.EvaAnalysisPipeline(
            config=config,
            source=source,
            sink=sink,
            cleaner=cleaner,
            cumulative_transformer=cumulative,
            summariser=summariser,
            plotter=plotter,
            reporter=reporter,
        )
        return pipeline, source, cleaner, sink, summariser, cumulative, plotter, reporter, d

    def test_run_wires_collaborators_together(self):
        (pipeline, source, cleaner, sink, summariser,
         cumulative, plotter, reporter, d) = self._make()

        pipeline.run()

        assert source.read_calls == 1
        assert cleaner.received == [d["raw"]]
        assert summariser.received == [d["cleaned"]]
        assert cumulative.received == [d["cleaned"]]
        assert (d["cleaned"], "out.csv") in sink.writes
        assert (d["summary"], "astro.csv") in sink.writes
        assert plotter.calls == [(d["cumulative"], "graph.png")]

    def test_run_emits_progress_through_reporter(self):
        pipeline, *_, reporter, _ = self._make()
        pipeline.run()
        # Logging is centralised through the injected reporter, not print.
        assert reporter.messages[0] == "--START--"
        assert reporter.messages[-1] == "--END--"


# --------------------------------------------------------------------------- #
# Composition root + end-to-end integration
# --------------------------------------------------------------------------- #
class TestBuildPipeline:
    def test_wires_concrete_types_and_shares_converter(self):
        config = eva.CliConfigFactory(eva.NullReporter()).from_args(["prog"])
        pipeline = entry.build_pipeline(config, eva.NullReporter())
        assert isinstance(pipeline, eva.EvaAnalysisPipeline)
        assert isinstance(pipeline._source, eva.JsonEvaDataSource)
        assert isinstance(pipeline._plotter, eva.CumulativeTimePlotter)
        assert (
            pipeline._summariser._duration_converter
            is pipeline._cumulative_transformer._duration_converter
        )


class TestEndToEnd:
    def _config(self, tmp_path, input_text):
        input_file = tmp_path / "eva.json"
        input_file.write_text(input_text)
        return eva.PipelineConfig(
            input_file=str(input_file),
            output_file=str(tmp_path / "eva.csv"),
            duration_by_astronaut_file=str(tmp_path / "astro.csv"),
            graph_file=str(tmp_path / "graph.png"),
        )

    def test_full_run_produces_expected_outputs(self, tmp_path, monkeypatch):
        monkeypatch.setattr(plotting.plt, "show", lambda *a, **k: None)
        config = self._config(
            tmp_path,
            "["
            '{"eva":"1","crew":"Alice;","date":"2000-01-01T00:00:00.000","duration":"1:30"},'
            '{"eva":"2","crew":"Bob;Alice;","date":"2000-02-01T00:00:00.000","duration":"2:00"},'
            '{"eva":"3","crew":"Carol;","duration":"0:30"},'  # missing date -> dropped
            '{"eva":"4","crew":"Dan;","date":"2000-03-01T00:00:00.000"}'  # missing duration -> dropped
            "]",
        )
        entry.build_pipeline(config, eva.NullReporter()).run()

        eva_csv = pd.read_csv(config.output_file)
        assert eva_csv["eva"].tolist() == [1.0, 2.0]

        # Bug fix: crew names are retained in the summary CSV.
        astro = pd.read_csv(config.duration_by_astronaut_file).set_index("crew")
        assert astro.loc["Alice", "duration_hours"] == pytest.approx(3.5)
        assert astro.loc["Bob", "duration_hours"] == pytest.approx(2.0)

        assert (tmp_path / "graph.png").stat().st_size > 0

    def test_summary_csv_retains_crew_names(self, tmp_path, monkeypatch):
        """Regression test for the previously-dropped crew names."""
        monkeypatch.setattr(plotting.plt, "show", lambda *a, **k: None)
        config = self._config(
            tmp_path,
            '[{"eva":"1","crew":"Alice;","date":"2000-01-01T00:00:00.000","duration":"1:30"}]',
        )
        entry.build_pipeline(config, eva.NullReporter()).run()

        astro = pd.read_csv(config.duration_by_astronaut_file)
        assert "crew" in astro.columns
        assert "Alice" in astro["crew"].tolist()
