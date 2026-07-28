"""Export spreadsheet-style CSV files for the web app and README."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.analyze import analyze
from src.config_loader import load_config, resolve_path
from src.ingest import ingest
from src.process import process


def export_spreadsheets(config: dict | None = None) -> dict[str, Path]:
    config = config or load_config()
    spreadsheets_dir = resolve_path(config, config["paths"]["spreadsheets"])
    spreadsheets_dir.mkdir(parents=True, exist_ok=True)

    raw_df = ingest(config)
    cleaned_df = process(config, raw_df)
    results = analyze(config, cleaned_df)

    outputs = {
        "01_raw_data.csv": raw_df,
        "02_cleaned_data.csv": cleaned_df,
        "03_summary_statistics.csv": results["summary_df"],
        "04_correlation_results.csv": results["correlation_df"],
        "05_regression_results.csv": results["regression_df"],
        "06_findings_summary.csv": results["findings_df"],
    }

    written: dict[str, Path] = {}
    for filename, dataframe in outputs.items():
        path = spreadsheets_dir / filename
        dataframe.to_csv(path, index=False)
        written[filename] = path

    return written


def main() -> None:
    paths = export_spreadsheets()
    print("Spreadsheets written:")
    for filename, path in paths.items():
        print(f"  {filename}: {path}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    main()
