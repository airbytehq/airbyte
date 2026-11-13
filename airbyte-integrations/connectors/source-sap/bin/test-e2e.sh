#!/usr/bin/env bash
# Run the e2e suite against a SAP system.
#
# Every ODP/BICS variable must be ABSENT rather than empty to skip cleanly --
# the fixtures skip on absence only, so exporting an empty value runs the test
# and fails it.
set -euo pipefail
cd "$(dirname "$0")/.."

: "${ERPL_EXTENSION_DIR:=$PWD/.erpl}"
if [ ! -d "${ERPL_EXTENSION_DIR}" ]; then
    echo "fetching the ERPL extensions into ${ERPL_EXTENSION_DIR}"
    ./bin/fetch-extensions.sh "${ERPL_EXTENSION_DIR}"
fi

export ERPL_EXTENSION_DIR
export LD_LIBRARY_PATH="${ERPL_EXTENSION_DIR}/v1.5.5/linux_amd64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

export ERPL_SAP_ASHOST="${ERPL_SAP_ASHOST:-localhost}"
export ERPL_SAP_SYSNR="${ERPL_SAP_SYSNR:-00}"
export ERPL_SAP_CLIENT="${ERPL_SAP_CLIENT:-001}"
export ERPL_SAP_USER="${ERPL_SAP_USER:-DEVELOPER}"
export ERPL_SAP_PASSWORD="${ERPL_SAP_PASSWORD:-ABAPtr2023#00}"
export ERPL_SAP_LANG="${ERPL_SAP_LANG:-EN}"
export ERPL_SAP_BASE_URL="${ERPL_SAP_BASE_URL:-http://localhost:50000}"

# The standard connector tests read secrets/config.json, so keep it in step.
./bin/write-secrets.sh

exec poetry run pytest e2e -m "requires_creds or not requires_creds" "$@"
