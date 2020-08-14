#!/bin/bash

set -e

. tools/lib/lib.sh

assert_root

USAGE="./tools/singer/$(basename "$0") <singer_root>"

[ -z "$1" ] && echo "singer root not provided" && error "$USAGE"
export SINGER_ROOT=$1

pip3 install psycopg2-binary
./tools/singer/install_connector.sh tap-postgres tap-postgres 0.1.0
./tools/singer/install_connector.sh target-postgres singer-target-postgres 0.2.4
