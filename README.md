# Capstone: Sunlight Exposure and Pediatric Depressive Symptoms

## Research question

**Does the amount of sunlight exposure impact how much the pediatric population reports depressive symptoms?**

This project loads `capstone.csv`, validates and analyzes the data, exports spreadsheet-style results, builds visualizations, and serves an interactive **Streamlit** web app.

Configuration, data, and environment files live in **`setup/`**. Source code, the web app, tests, and notebooks stay at the repository root.

## Data

| Column | Description |
|--------|-------------|
| `Year` | Observation year (2019, 2021, 2023) |
| `YouthDepression(%)` | Share of youth reporting depressive symptoms |
| `AverageSun(MJ/m^2/day)` | Average daily sunlight exposure |

**Important limitation:** The dataset contains only **3 annual observations**. All statistical results are **descriptive and exploratory** — they do not support causal or confirmatory inference.

## Environment setup

Use the conda environment **`capstone_env`** (spelling matters).

### Option A: Conda (recommended on OSC)

```bash
module load miniconda3/24.1.2-py310   # if on OSC
conda env create -f setup/environment-1.yml  # first time only
conda activate capstone_env
```

Or run the helper script (creates env and starts JupyterLab on port 2000):

```bash
bash setup/setup_env-1.sh
```

### Option B: Pip

```bash
pip install -r setup/requirements-1.txt
```

## Run the pipeline

From the repository root:

```bash
conda activate capstone_env
bash setup/run_pipeline.sh
```

This produces:

- `outputs/spreadsheets/` — six CSV tables (raw, cleaned, summary, correlation, regression, findings)
- `outputs/figures/` — pipeline charts and presentation figures
- `outputs/results/` — JSON metadata for reproducibility

## Launch the web app

```bash
conda activate capstone_env
streamlit run webapp/app.py --server.port 2026
```

Then open **http://localhost:2026** in your browser.

### Viewing on a remote cluster (OSC / SSH)

From your **local** machine:

```bash
ssh -L 2026:localhost:2026 YOUR_USERNAME@YOUR_CLUSTER
```

On the **remote** host (after activating the env and starting Streamlit):

```bash
streamlit run webapp/app.py --server.port 2026 --server.address localhost
```

Open **http://localhost:2026** locally — traffic is tunneled to the cluster.

## Run tests

```bash
conda activate capstone_env
pytest tests/ -v
```

Tests validate schema checks and golden statistics for the three known data points.

## Project structure

```
capstone/
├── README.md                 # This file
├── .gitignore
├── setup/
│   ├── capstone.csv          # Source data
│   ├── config.yaml           # Paths and column names
│   ├── run_pipeline.sh       # End-to-end pipeline entry point
│   ├── environment-1.yml     # Conda environment
│   ├── setup_env-1.sh        # OSC setup helper
│   └── requirements-1.txt    # Pip fallback
├── src/                      # Ingest, process, analyze, visualize, export
├── webapp/app.py             # Streamlit dashboard
├── notebooks/                # Exploratory notebook
├── outputs/                  # Generated artifacts (gitignored)
└── tests/                    # Pipeline verification tests
```

## Findings (exploratory)

After running the pipeline on `capstone.csv`:

1. **Youth depression varies more than sunlight.** Rates move from 33.0% (2019) to 42.6% (2021) to 35.0% (2023), while average sun stays near 14.1 MJ/m²/day.
2. **2021 shows the highest youth depression** without a proportional increase in sunlight.
3. **Descriptive correlation is moderately positive** (Pearson r ≈ 0.84), but with **n = 3** this is not statistically reliable and must not be interpreted as evidence of causation.
4. **Overall takeaway:** These three yearly points do **not** support a strong conclusion that sunlight drives pediatric depression rates. More years and finer-grained data would be needed.

See `outputs/figures/main_finding.png` after running the pipeline for the primary visualization.

## Spreadsheets reference

| File | Contents |
|------|----------|
| `01_raw_data.csv` | Validated source data |
| `02_cleaned_data.csv` | Standardized column names |
| `03_summary_statistics.csv` | Mean, SD, min, max |
| `04_correlation_results.csv` | Pearson and Spearman results |
| `05_regression_results.csv` | Descriptive linear trend |
| `06_findings_summary.csv` | Plain-English interpretation |

## License / course context

BSGP 7030 capstone project.
