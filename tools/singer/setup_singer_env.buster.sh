#!/bin/bash
# Currently this assumes debian (buster)

set -e

. tools/lib/lib.sh

assert_root
SINGER_ROOT=$1
[ -z "$SINGER_ROOT" ] && error "singer_root is required"

apt-get clean
apt-get update
apt-get -y install libpq-dev=11.7-0+deb10u1 \
  python3.7=3.7.3-2+deb10u2 \
  python3-venv=3.7.3-1 \
  python3-pip=18.1-5

./tools/singer/install_all_connectors.sh "$SINGER_ROOT"
