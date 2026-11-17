#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements-dashboard.txt
python3 -m streamlit run dashboard.py
