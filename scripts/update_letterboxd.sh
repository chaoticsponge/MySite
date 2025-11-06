#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/usr/local/apache2/htdocs"
LETTERBOXD_DIR="${PROJECT_ROOT}/letterboxd"

if [ ! -d "${LETTERBOXD_DIR}" ]; then
  echo "Letterboxd directory not found at ${LETTERBOXD_DIR}" >&2
  exit 1
fi

cd "${LETTERBOXD_DIR}"

echo "[supercronic] Updating Letterboxd diary..."
node ./bin/letterboxd.js diary kawaiisponge

echo "[supercronic] Rebuilding movie index..."
python3 moviejson.py

echo "[supercronic] Update complete."
