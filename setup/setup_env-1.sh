#!/usr/bin/env bash
# OSC conda setup for BSGP 7030. Serves JupyterLab on port 2000.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load Miniconda
module load miniconda3/24.1.2-py310

# Create Conda environment (now includes pandas/scipy/seaborn/sklearn/ggplot2/caret)
conda env create -f environment-1.yml

# Activate the environment
conda activate capstone_env

# Optional: pip path (the conda env above already includes these libraries)
# pip install -r requirements-1.txt

# Register Python kernel
python -m ipykernel install --user --name capstone_env --display-name "Python (capstone_env)"

# Register R kernel
Rscript -e 'IRkernel::installspec(name="ir_capstone_env", displayname="R (capstone_env)")'

# Start JupyterLab
jupyter lab --no-browser --port=2000
