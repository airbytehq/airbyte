#!/usr/bin/env bash
set -euo pipefail

source "${BASH_SOURCE%/*}/lib/util.sh"

source "${BASH_SOURCE%/*}/lib/parse_args.sh"

exit_code=0
while read -r connector; do
  echo "---- PROCESSING METADATA FOR $connector ----"
  meta="${CONNECTORS_DIR}/${connector}/metadata.yaml"
  doc="$(connector_docs_path $connector)"
  # Don't exit immediately. We should run against all connectors.
  set +e
  if ! poetry run --directory $METADATA_SERVICE_PATH metadata_service validate "$meta" "$doc"; then
    exit_code=1
  fi
  # Reenable the "exit on error" option.
  set -e
done < <(get_connectors)

if test $exit_code -ne 0; then
  echo '------------'
  echo 'One or more connectors had invalid metadata.yaml. See previous logs for more information.'
  exit $exit_code
fi
