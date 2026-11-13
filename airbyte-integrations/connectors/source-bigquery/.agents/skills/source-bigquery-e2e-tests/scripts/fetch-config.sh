#!/usr/bin/env bash
set -euo pipefail
umask 077

: "${REPRO_OUT:?REPRO_OUT must be set}"
GSM_PROJECT="${GSM_PROJECT:-dataline-integration-testing}"
BIGQUERY_SECRET_NAME="${BIGQUERY_SECRET_NAME:-SECRET_SOURCE-BIGQUERY_CREDENTIALS__CREDS}"
BIGQUERY_CONFIG_FILE="${BIGQUERY_CONFIG_FILE:-$REPRO_OUT/.bigquery-config.json}"
SA_KEY_FILE="$REPRO_OUT/.bigquery-sa.json"

mkdir -p "$REPRO_OUT" "$(dirname "$BIGQUERY_CONFIG_FILE")"
chmod 700 "$REPRO_OUT"

if [[ ! -f "$BIGQUERY_CONFIG_FILE" ]]; then
  temporary_config="$(mktemp "${BIGQUERY_CONFIG_FILE}.tmp.XXXXXX")"
  trap 'rm -f "$temporary_config"' EXIT
  gcloud secrets versions access latest \
    --secret="$BIGQUERY_SECRET_NAME" \
    --project="$GSM_PROJECT" > "$temporary_config"
  chmod 600 "$temporary_config"
  mv "$temporary_config" "$BIGQUERY_CONFIG_FILE"
  touch "$BIGQUERY_CONFIG_FILE.fetched"
  chmod 600 "$BIGQUERY_CONFIG_FILE.fetched"
  trap - EXIT
fi
chmod 600 "$BIGQUERY_CONFIG_FILE"

if [[ ! -f "$SA_KEY_FILE" ]]; then
  echo "[fetch-config] secret keys:" >&2
  jq 'keys' "$BIGQUERY_CONFIG_FILE" >&2
  temporary_key="$(mktemp "$REPRO_OUT/.bigquery-sa.XXXXXX")"
  trap 'rm -f "$temporary_key"' EXIT
  jq -er '
    if has("credentials_json") then
      .credentials_json | if type == "string" then . else tojson end
    else
      tojson
    end
  ' "$BIGQUERY_CONFIG_FILE" > "$temporary_key"
  jq -e '
    type == "object" and
    .type == "service_account" and
    (.client_email | type == "string") and
    (.private_key | type == "string")
  ' "$temporary_key" >/dev/null
  chmod 600 "$temporary_key"
  mv "$temporary_key" "$SA_KEY_FILE"
  touch "$SA_KEY_FILE.fetched"
  chmod 600 "$SA_KEY_FILE.fetched"
  trap - EXIT
fi
chmod 600 "$SA_KEY_FILE"
