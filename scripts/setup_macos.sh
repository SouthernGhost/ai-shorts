#!/usr/bin/env bash
set -euo pipefail

# Create venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Check ffmpeg
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. On macOS: brew install ffmpeg"
fi

echo "Done. Activate with: source .venv/bin/activate"
