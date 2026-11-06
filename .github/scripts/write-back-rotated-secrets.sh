#!/usr/bin/env bash
# Write connector configs rotated during tests back to GSM.
#
# Tests persist rotated configs as `secrets/updated_configurations/<stem>|<emitted_at_ms>.json`.
# The newest file per stem becomes a new version of the GSM secret labelled `filename=<stem>`
# (`airbyte-ops secrets update`), or a new `SECRET_<CONNECTOR>__<STEM>` secret if none exists
# (`airbyte-ops secrets create`).
set -euo pipefail

: "${CONNECTOR:?CONNECTOR is required}"

if [[ -z "${GCP_GSM_WRITER_CREDENTIALS:-}" ]]; then
  echo "::warning::GCP_GSM_WRITER_CREDENTIALS is not set; rotated secrets were not written back."
  exit 0
fi

CONNECTOR_DIR="airbyte-integrations/connectors/${CONNECTOR}"
UPDATED_DIR="${CONNECTOR_DIR}/secrets/updated_configurations"
shopt -s nullglob
UPDATED_FILES=("${UPDATED_DIR}"/*.json)
if [[ ${#UPDATED_FILES[@]} -eq 0 ]]; then
  echo "No rotated secrets found under ${UPDATED_DIR}."
  exit 0
fi

# Map each GSM secret's `filename` label to its secret name.
declare -A SECRET_NAMES=() AMBIGUOUS=()
SECRET_HANDLES="$("$(uv tool dir)/airbyte-internal-ops/bin/python" - "$CONNECTOR" <<'PY'
import sys

from airbyte_ops_mcp.connector_secrets import extract_gcp_secret_name, fetch_secret_handles

for secret in fetch_secret_handles(connector_name=sys.argv[1]):
    print(f"{secret.labels.get('filename', 'config')}\t{extract_gcp_secret_name(secret.name)}")
PY
)"
while IFS=$'\t' read -r label name; do
  [[ -z "$label" ]] && continue
  [[ -n "${SECRET_NAMES[$label]:-}" ]] && AMBIGUOUS[$label]=1
  SECRET_NAMES[$label]="$name"
done <<<"$SECRET_HANDLES"

# Keep the newest update per stem.
declare -A LATEST=()
while IFS= read -r file; do
  base="$(basename "$file" .json)"
  LATEST["${base%%|*}"]="$file"
done < <(printf '%s\n' "${UPDATED_FILES[@]}" | sort -t'|' -k2,2n)

FAILED=0
for stem in "${!LATEST[@]}"; do
  file="${LATEST[$stem]}"
  original="${CONNECTOR_DIR}/secrets/${stem}.json"
  if [[ -f "$original" && "$(jq -S . "$original")" == "$(jq -S . "$file")" ]]; then
    echo "${stem}.json is unchanged; skipping."
    continue
  fi
  if [[ -n "${AMBIGUOUS[$stem]:-}" ]]; then
    echo "::warning::Several GSM secrets of ${CONNECTOR} use filename '${stem}'; ${stem}.json was not written back."
    continue
  fi

  secret_name="${SECRET_NAMES[$stem]:-SECRET_${CONNECTOR^^}__$(tr 'a-z-' 'A-Z_' <<<"$stem")}"
  if output="$(airbyte-ops secrets update "$CONNECTOR_DIR" --secret-name "$secret_name" --config-file "$file" 2>&1)"; then
    echo "$output"
    continue
  fi

  if grep -q "was not found" <<<"$output"; then
    create_args=(--secret-name "$secret_name" --config-file "$file")
    [[ "$stem" != "config" ]] && create_args+=(--filename "$stem")
    if output="$(airbyte-ops secrets create "$CONNECTOR_DIR" "${create_args[@]}" 2>&1)"; then
      echo "$output"
      continue
    fi
  elif grep -q "still need disabling" <<<"$output"; then
    # The new version was added and is latest; only disabling older versions failed.
    echo "::warning::$(tail -n 1 <<<"$output")"
    continue
  fi

  echo "$output"
  echo "::error::Failed to write back rotated ${stem}.json to GSM secret ${secret_name}."
  FAILED=1
done
exit "$FAILED"
