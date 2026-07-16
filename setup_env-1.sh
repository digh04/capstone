#!/usr/bin/env bash
# OSC conda setup for BSGP 7030. Serves JupyterLab on port 2000.

# Load Miniconda
module load miniconda3/24.1.2-py310

# Create Conda environment (now includes pandas/scipy/seaborn/sklearn/ggplot2/caret)
conda env create -f environment.yml

# Activate the environment
conda activate 7030_class_1

# Optional: pip path (the conda env above already includes these libraries)
# pip install -r requirements.txt

# Register Python kernel
python -m ipykernel install --user --name 7030_class_1 --display-name "Python (7030_class_1)"

# Register R kernel
Rscript -e 'IRkernel::installspec(name="ir_7030_class_1", displayname="R (7030_class_1)")'

# Start JupyterLab
jupyter lab --no-browser --port=2000
