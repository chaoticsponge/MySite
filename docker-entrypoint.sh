#!/usr/bin/env sh
set -e

CRON_FILE="/etc/supercronic/letterboxd.cron"
UPDATE_SCRIPT="/usr/local/bin/update_letterboxd.sh"

if [ -x "${UPDATE_SCRIPT}" ]; then
  echo "Running initial Letterboxd sync..."
  if ! "${UPDATE_SCRIPT}"; then
    echo "Initial Letterboxd sync failed; continuing to start services." >&2
  fi
else
  echo "Update script ${UPDATE_SCRIPT} not found or not executable; skipping initial sync." >&2
fi

if [ -f "${CRON_FILE}" ]; then
  echo "Starting supercronic with ${CRON_FILE}"
  /usr/local/bin/supercronic "${CRON_FILE}" &
else
  echo "Cron file ${CRON_FILE} not found; skipping supercronic startup." >&2
fi

exec "$@"
