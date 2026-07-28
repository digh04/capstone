"""Run the full capstone analysis pipeline end-to-end."""

from __future__ import annotations

import sys
from pathlib import Path

from src.analyze import analyze, write_analysis_outputs
from src.config_loader import load_config, resolve_path
from src.export_spreadsheets import export_spreadsheets
from src.ingest import ingest
from src.process import process
from src.visualize import visualize


def run_pipeline(config: dict | None = None) -> dict:
    config = config or load_config()

    for subdir in ("spreadsheets", "figures", "results"):
        resolve_path(config, config["paths"][subdir]).mkdir(parents=True, exist_ok=True)

    raw_df = ingest(config)
    cleaned_df = process(config, raw_df)
    results = analyze(config, cleaned_df)
    write_analysis_outputs(results, config)
    figure_paths = visualize(config, cleaned_df, results)
    spreadsheet_paths = export_spreadsheets(config)

    return {
        "raw_rows": len(raw_df),
        "cleaned_rows": len(cleaned_df),
        "figures": figure_paths,
        "spreadsheets": spreadsheet_paths,
        "metadata": results["metadata"],
    }


def main() -> None:
    summary = run_pipeline()
    print("Pipeline complete.")
    print(f"  Rows processed: {summary['cleaned_rows']}")
    print(f"  Pearson r: {summary['metadata']['pearson_r']:.4f}")
    print(f"  Figures: {len(summary['figures'])}")
    print(f"  Spreadsheets: {len(summary['spreadsheets'])}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    main()
