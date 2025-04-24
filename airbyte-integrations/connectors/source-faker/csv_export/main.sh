#!/usr/bin/env bash

cd "$(dirname "$0")"
cd ".."

mkdir -p /tmp/csv

python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state secrets/state.json \
  | tee >(./csv_export/purchases.sh) >(./csv_export/products.sh) >(./csv_export/users.sh)
