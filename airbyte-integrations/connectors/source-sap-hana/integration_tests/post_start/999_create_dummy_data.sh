#!/bin/bash

set -euo pipefail

#found in /run_hana.sh, hxe_optimize.sh
#durinng the 'initial' phase there is key for SYSTEM available
declare -r tenant_store_key=us_key_tenantdb

# import dump
function main() {
    case "$_HOOK_START_TYPE" in
        initial)
             /usr/sap/HXE/HDB90/exe/hdbsql -n localhost -i 90 -u SYSTEM -p Password1! -d HXE -B UTF8 "CREATE SCHEMA SBO_TEST" 2>&1
             /usr/sap/HXE/HDB90/exe/hdbsql -n localhost -i 90 -u SYSTEM -p Password1! -d HXE -B UTF8 "CREATE column table SBO_TEST.TEST as (SELECT * FROM tables)" 2>&1
            ;;
    esac
}

main

# /usr/sap/HXE/HDB90/exe/hdbsql -n localhost -i 90 -u SYSTEM -p Password1! -d HXE -B UTF8 "select distinct schema_name from tables"