#!/usr/bin/env bash
set -euo pipefail

source "${BASH_SOURCE%/*}/lib/util.sh"

source "${BASH_SOURCE%/*}/lib/parse_args.sh"
connector=$(get_only_connector)

echo "---- PROCESSING METADATA FOR $connector ----"
meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
is_enterprise=$(yq -r '.data.ab_internal.isEnterprise // false' "$meta")
doc="$(connector_docs_path $connector $is_enterprise)"
poetry run --directory $METADATA_SERVICE_PATH metadata_service validate "$meta" "$doc"
