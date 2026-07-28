"""Descriptive statistics, correlation, and simple regression."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

from src.config_loader import load_config, resolve_path
from src.process import process

EXPLORATORY_NOTE = "Exploratory only; n=3 is insufficient for reliable inference."


def analyze(config: dict | None = None, cleaned_df: pd.DataFrame | None = None) -> dict:
    config = config or load_config()
    clean_cols = config["columns"]["clean"]

    if cleaned_df is None:
        cleaned_df = process(config)

    dep = cleaned_df[clean_cols["depression"]]
    sun = cleaned_df[clean_cols["sun"]]
    n = len(cleaned_df)

    summary_rows = []
    for variable, series in [
        (clean_cols["depression"], dep),
        (clean_cols["sun"], sun),
    ]:
        summary_rows.append(
            {
                "variable": variable,
                "n": n,
                "mean": float(series.mean()),
                "std": float(series.std(ddof=1)) if n > 1 else 0.0,
                "min": float(series.min()),
                "max": float(series.max()),
            }
        )
    summary_df = pd.DataFrame(summary_rows)

    pearson_r, pearson_p = stats.pearsonr(sun, dep)
    spearman_rho, spearman_p = stats.spearmanr(sun, dep)
    slope, intercept, r_value, p_value, std_err = stats.linregress(sun, dep)

    correlation_df = pd.DataFrame(
        [
            {
                "method": "Pearson r",
                "statistic": float(pearson_r),
                "p_value": float(pearson_p),
                "note": EXPLORATORY_NOTE,
            },
            {
                "method": "Spearman rho",
                "statistic": float(spearman_rho),
                "p_value": float(spearman_p),
                "note": EXPLORATORY_NOTE,
            },
        ]
    )

    regression_df = pd.DataFrame(
        [
            {
                "term": "intercept",
                "estimate": float(intercept),
                "interpretation": "Predicted youth depression (%) when sun exposure is zero (not meaningful extrapolation).",
            },
            {
                "term": "slope",
                "estimate": float(slope),
                "interpretation": "Change in youth depression (%) per 1 MJ/m^2/day increase in sunlight (descriptive trend only).",
            },
            {
                "term": "r_squared",
                "estimate": float(r_value**2),
                "interpretation": "Share of depression variance linearly associated with sun in this 3-point sample.",
            },
            {
                "term": "p_value",
                "estimate": float(p_value),
                "interpretation": EXPLORATORY_NOTE,
            },
        ]
    )

    dep_range = float(dep.max() - dep.min())
    sun_range = float(sun.max() - sun.min())
    dep_peak_year = int(cleaned_df.loc[dep.idxmax(), clean_cols["year"]])

    if abs(pearson_r) >= 0.5:
        direction = "positive" if pearson_r > 0 else "negative"
        association = f"A {direction} linear association is visible descriptively (r={pearson_r:.3f})."
    else:
        association = f"No strong linear association is visible (r={pearson_r:.3f})."

    findings_df = pd.DataFrame(
        [
            {
                "finding": "Sample size",
                "evidence": f"{n} annual observations ({', '.join(map(str, cleaned_df[clean_cols['year']].tolist()))}).",
                "limitation": "Too few points for causal or confirmatory inference.",
                "confidence": "High (fact)",
            },
            {
                "finding": "Depression variability",
                "evidence": f"Youth depression ranges from {dep.min():.1f}% to {dep.max():.1f}% (span {dep_range:.1f} pp); peak in {dep_peak_year}.",
                "limitation": "Single aggregate rate per year; not individual-level data.",
                "confidence": "High (descriptive)",
            },
            {
                "finding": "Sunlight variability",
                "evidence": f"Average sun ranges from {sun.min():.4f} to {sun.max():.4f} MJ/m^2/day (span {sun_range:.4f}).",
                "limitation": "Regional average exposure, not personal exposure.",
                "confidence": "High (descriptive)",
            },
            {
                "finding": "Sun-depression association",
                "evidence": association,
                "limitation": EXPLORATORY_NOTE,
                "confidence": "Low (exploratory)",
            },
            {
                "finding": "Overall takeaway",
                "evidence": "Depression changed more across years than average sunlight; 2021 shows the highest youth depression without a proportional sunlight shift.",
                "limitation": "Cannot conclude that sunlight causes changes in pediatric depression from this dataset alone.",
                "confidence": "Moderate (interpretive)",
            },
        ]
    )

    results = {
        "summary_df": summary_df,
        "correlation_df": correlation_df,
        "regression_df": regression_df,
        "findings_df": findings_df,
        "metadata": {
            "n_observations": n,
            "pearson_r": float(pearson_r),
            "spearman_rho": float(spearman_rho),
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_value**2),
        },
    }
    return results


def write_analysis_outputs(results: dict, config: dict | None = None) -> None:
    config = config or load_config()
    results_dir = resolve_path(config, config["paths"]["results"])
    results_dir.mkdir(parents=True, exist_ok=True)

    with (results_dir / "analysis_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(results["metadata"], handle, indent=2)


def main() -> None:
    results = analyze()
    write_analysis_outputs(results)
    print("Analysis complete.")
    print(results["summary_df"].to_string(index=False))
    print()
    print(results["correlation_df"].to_string(index=False))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    main()
