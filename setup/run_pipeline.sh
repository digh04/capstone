#!/usr/bin/env bash
# End-to-end capstone pipeline: ingest -> analyze -> spreadsheets -> figures
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Use capstone_env Python if available
if command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.bash hook 2>/dev/null)" || true
    conda activate capstone_env 2>/dev/null || true
fi

PYTHON="${PYTHON:-python}"
if ! "$PYTHON" -c "import pandas" 2>/dev/null; then
    if [ -x "${HOME}/.conda/envs/capstone_env/bin/python" ]; then
        PYTHON="${HOME}/.conda/envs/capstone_env/bin/python"
    fi
fi

echo "Using Python: $("$PYTHON" --version)"
echo "Running pipeline..."
"$PYTHON" -m src.run_pipeline

echo ""
echo "To launch the web app:"
echo "  streamlit run webapp/app.py --server.port 2026"
