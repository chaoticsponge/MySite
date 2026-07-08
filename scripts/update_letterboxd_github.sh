#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
LETTERBOXD_DIR="${PROJECT_ROOT}/letterboxd"

cd "${LETTERBOXD_DIR}"

echo "Updating Letterboxd diary..."
node ./bin/letterboxd.js diary kawaiisponge

echo "Rebuilding movie index..."
python3 moviejson.py

echo "Done."