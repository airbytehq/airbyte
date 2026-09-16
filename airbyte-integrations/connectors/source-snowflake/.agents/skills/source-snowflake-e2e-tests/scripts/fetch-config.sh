#!/usr/bin/env bash
set -euo pipefail

SNOWFLAKE_CONFIG_FILE="${SNOWFLAKE_CONFIG_FILE:?SNOWFLAKE_CONFIG_FILE must be set}"
GSM_PROJECT="${GSM_PROJECT:-dataline-integration-testing}"
SNOWFLAKE_SECRET_NAME="${SNOWFLAKE_SECRET_NAME:-SECRET_SOURCE-SNOWFLAKE_KEY_PAIR__CREDS}"

if [[ -f "$SNOWFLAKE_CONFIG_FILE" ]]; then
  exit 0
fi

umask 077
mkdir -p "$(dirname "$SNOWFLAKE_CONFIG_FILE")"
temporary_file="${SNOWFLAKE_CONFIG_FILE}.tmp.$$"
trap 'rm -f "$temporary_file"' EXIT
gcloud secrets versions access latest \
  --secret="$SNOWFLAKE_SECRET_NAME" \
  --project="$GSM_PROJECT" > "$temporary_file"
mv "$temporary_file" "$SNOWFLAKE_CONFIG_FILE"
touch "$SNOWFLAKE_CONFIG_FILE.fetched"
chmod 600 "$SNOWFLAKE_CONFIG_FILE.fetched"
trap - EXIT
