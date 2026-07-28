"""Clean and rename columns for analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.config_loader import load_config
from src.ingest import ingest


def process(config: dict | None = None, raw_df: pd.DataFrame | None = None) -> pd.DataFrame:
    config = config or load_config()
    raw_cols = config["columns"]["raw"]
    clean_cols = config["columns"]["clean"]

    if raw_df is None:
        raw_df = ingest(config)

    cleaned = raw_df.rename(
        columns={
            raw_cols["year"]: clean_cols["year"],
            raw_cols["depression"]: clean_cols["depression"],
            raw_cols["sun"]: clean_cols["sun"],
        }
    )
    return cleaned.sort_values(clean_cols["year"]).reset_index(drop=True)


def main() -> None:
    df = process()
    print(f"Processed {len(df)} rows")
    print(df.to_string(index=False))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    main()
