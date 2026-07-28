"""Load and validate capstone.csv."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.config_loader import load_config, resolve_path


def ingest(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config()
    raw_cols = config["columns"]["raw"]
    source_path = resolve_path(config, config["data"]["source"])

    if not source_path.exists():
        raise FileNotFoundError(f"Data file not found: {source_path}")

    df = pd.read_csv(source_path)
    expected = [raw_cols["year"], raw_cols["depression"], raw_cols["sun"]]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[expected].copy()
    df[raw_cols["year"]] = df[raw_cols["year"]].astype(int)
    df[raw_cols["depression"]] = df[raw_cols["depression"]].astype(float)
    df[raw_cols["sun"]] = df[raw_cols["sun"]].astype(float)

    if df.isnull().any().any():
        raise ValueError("Dataset contains missing values.")

    if df[raw_cols["year"]].duplicated().any():
        raise ValueError("Year values must be unique.")

    dep_min = config["validation"]["depression_min"]
    dep_max = config["validation"]["depression_max"]
    sun_min = config["validation"]["sun_min"]

    if ((df[raw_cols["depression"]] < dep_min) | (df[raw_cols["depression"]] > dep_max)).any():
        raise ValueError(f"Depression values must be between {dep_min} and {dep_max}.")

    if (df[raw_cols["sun"]] <= sun_min).any():
        raise ValueError(f"Sun values must be greater than {sun_min}.")

    return df.sort_values(raw_cols["year"]).reset_index(drop=True)


def main() -> None:
    df = ingest()
    print(f"Ingested {len(df)} rows from capstone.csv")
    print(df.to_string(index=False))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    main()
