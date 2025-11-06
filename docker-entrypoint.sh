#!/usr/bin/env sh
set -e

CRON_FILE="/etc/supercronic/letterboxd.cron"

if [ -f "${CRON_FILE}" ]; then
  echo "Starting supercronic with ${CRON_FILE}"
  /usr/local/bin/supercronic "${CRON_FILE}" &
else
  echo "Cron file ${CRON_FILE} not found; skipping supercronic startup." >&2
fi

exec "$@"
