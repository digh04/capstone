"""Tests for the capstone analysis pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analyze import analyze
from src.config_loader import PROJECT_ROOT, load_config
from src.export_spreadsheets import export_spreadsheets
from src.ingest import ingest
from src.process import process
from src.run_pipeline import run_pipeline


@pytest.fixture
def config():
    return load_config()


def test_ingest_row_count(config):
    df = ingest(config)
    assert len(df) == 3


def test_ingest_columns(config):
    raw_cols = config["columns"]["raw"]
    df = ingest(config)
    assert list(df.columns) == [raw_cols["year"], raw_cols["depression"], raw_cols["sun"]]


def test_process_renames_columns(config):
    clean_cols = config["columns"]["clean"]
    df = process(config)
    assert list(df.columns) == [clean_cols["year"], clean_cols["depression"], clean_cols["sun"]]


def test_summary_statistics_golden_values(config):
    results = analyze(config)
    summary = results["summary_df"].set_index("variable")

    dep = summary.loc["youth_depression_pct"]
    assert dep["n"] == 3
    assert dep["min"] == pytest.approx(33.0)
    assert dep["max"] == pytest.approx(42.6)
    assert dep["mean"] == pytest.approx(36.8666666667, rel=1e-4)

    sun = summary.loc["avg_sun_mj_m2_day"]
    assert sun["min"] == pytest.approx(13.9795, rel=1e-4)
    assert sun["max"] == pytest.approx(14.164, rel=1e-4)
    assert sun["mean"] == pytest.approx(14.0851666667, rel=1e-4)


def test_correlation_golden_values(config):
    results = analyze(config)
    meta = results["metadata"]
    assert meta["pearson_r"] == pytest.approx(0.841021, rel=1e-4)
    assert meta["spearman_rho"] == pytest.approx(1.0, rel=1e-4)
    assert meta["slope"] == pytest.approx(44.776752, rel=1e-4)
    assert meta["r_squared"] == pytest.approx(0.707317, rel=1e-4)


def test_pipeline_writes_outputs(config):
    test_config = config.copy()
    rel = "outputs/_test_pipeline"
    test_config["paths"] = {
        "output_dir": rel,
        "spreadsheets": f"{rel}/spreadsheets",
        "figures": f"{rel}/figures",
        "results": f"{rel}/results",
    }

    summary = run_pipeline(test_config)
    output_root = PROJECT_ROOT / rel
    assert summary["cleaned_rows"] == 3
    assert (output_root / "spreadsheets" / "01_raw_data.csv").exists()
    assert (output_root / "figures" / "main_finding.png").exists()


def test_spreadsheet_files_exist_after_export(config):
    paths = export_spreadsheets(config)
    assert len(paths) == 6
    for path in paths.values():
        assert path.exists()
        df = pd.read_csv(path)
        assert len(df) >= 1
