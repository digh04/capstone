"""Generate figures for the capstone analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from src.analyze import analyze
from src.config_loader import load_config, resolve_path
from src.process import process


def visualize(
    config: dict | None = None,
    cleaned_df: pd.DataFrame | None = None,
    analysis_results: dict | None = None,
) -> dict[str, Path]:
    config = config or load_config()
    clean_cols = config["columns"]["clean"]
    figures_dir = resolve_path(config, config["paths"]["figures"])
    figures_dir.mkdir(parents=True, exist_ok=True)

    if cleaned_df is None:
        cleaned_df = process(config)
    if analysis_results is None:
        analysis_results = analyze(config, cleaned_df)

    years = cleaned_df[clean_cols["year"]]
    dep = cleaned_df[clean_cols["depression"]]
    sun = cleaned_df[clean_cols["sun"]]
    metadata = analysis_results["metadata"]

    # Primary figure: dual time series
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    fig.suptitle(
        "Youth Depression and Sunlight Exposure Over Time",
        fontsize=14,
        fontweight="bold",
    )

    axes[0].plot(years, dep, marker="o", color="#c0392b", linewidth=2, markersize=8)
    axes[0].set_ylabel("Youth Depression (%)")
    axes[0].set_title("Pediatric Depressive Symptoms")
    axes[0].grid(True, alpha=0.3)
    for x_val, y_val in zip(years, dep):
        axes[0].annotate(f"{y_val:.1f}%", (x_val, y_val), textcoords="offset points", xytext=(0, 8), ha="center")

    axes[1].plot(years, sun, marker="o", color="#f39c12", linewidth=2, markersize=8)
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Average Sun (MJ/m²/day)")
    axes[1].set_title("Sunlight Exposure")
    axes[1].grid(True, alpha=0.3)
    for x_val, y_val in zip(years, sun):
        axes[1].annotate(f"{y_val:.3f}", (x_val, y_val), textcoords="offset points", xytext=(0, 8), ha="center")

    plt.tight_layout()
    main_path = figures_dir / "main_finding.png"
    fig.savefig(main_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Individual time-series panels (presentation-friendly)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(years.astype(str), dep, color="#c0392b", alpha=0.85, edgecolor="white")
    ax.plot(years, dep, marker="o", color="#922b21", linewidth=2, markersize=8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Youth Depression (%)")
    ax.set_title("Youth Depressive Symptoms by Year")
    ax.grid(True, axis="y", alpha=0.3)
    for x_val, y_val in zip(years, dep):
        ax.annotate(f"{y_val:.1f}%", (x_val, y_val), textcoords="offset points", xytext=(0, 6), ha="center")
    plt.tight_layout()
    depression_path = figures_dir / "depression_by_year.png"
    fig.savefig(depression_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(years.astype(str), sun, color="#f39c12", alpha=0.85, edgecolor="white")
    ax.plot(years, sun, marker="o", color="#d68910", linewidth=2, markersize=8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Sun (MJ/m²/day)")
    ax.set_title("Average Sunlight Exposure by Year")
    ax.grid(True, axis="y", alpha=0.3)
    for x_val, y_val in zip(years, sun):
        ax.annotate(f"{y_val:.3f}", (x_val, y_val), textcoords="offset points", xytext=(0, 6), ha="center")
    plt.tight_layout()
    sunlight_path = figures_dir / "sunlight_by_year.png"
    fig.savefig(sunlight_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Secondary figure: scatter with regression line
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(sun, dep, s=100, color="#2980b9", edgecolors="white", linewidth=1.5, zorder=3)
    for x_val, y_val, year in zip(sun, dep, years):
        ax.annotate(str(year), (x_val, y_val), textcoords="offset points", xytext=(6, 4), fontsize=9)

    x_line = pd.Series([sun.min(), sun.max()])
    slope = metadata["slope"]
    intercept = metadata["intercept"]
    y_line = intercept + slope * x_line
    ax.plot(x_line, y_line, color="#e74c3c", linestyle="--", linewidth=2, label="Descriptive trend line")

    ax.set_xlabel("Average Sun (MJ/m²/day)")
    ax.set_ylabel("Youth Depression (%)")
    ax.set_title("Sunlight vs Youth Depression (Exploratory, n=3)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.text(
        0.05,
        0.95,
        f"Pearson r = {metadata['pearson_r']:.3f}\n(n=3; not inferential)",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.8},
    )

    plt.tight_layout()
    scatter_path = figures_dir / "scatter_regression.png"
    fig.savefig(scatter_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return {
        "main_finding": main_path,
        "depression_by_year": depression_path,
        "sunlight_by_year": sunlight_path,
        "scatter_regression": scatter_path,
    }


def main() -> None:
    paths = visualize()
    print("Figures written:")
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    main()
