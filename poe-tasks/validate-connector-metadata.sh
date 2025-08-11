#!/usr/bin/env bash
set -euo pipefail

source "${BASH_SOURCE%/*}/lib/util.sh"

source "${BASH_SOURCE%/*}/lib/parse_args.sh"
connector=$(get_only_connector)

echo "---- PROCESSING METADATA FOR $connector ----"
meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
doc="$(connector_docs_path $connector)"
poetry run --directory $METADATA_SERVICE_PATH metadata_service validate "$meta" "$doc"
