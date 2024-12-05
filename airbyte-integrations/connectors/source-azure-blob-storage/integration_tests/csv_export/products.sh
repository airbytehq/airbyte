#!/usr/bin/env bash

cd "$(dirname "$0")"

FILE="/tmp/csv/products.csv"

rm -rf $FILE
echo "id,make,year,model,price,created_at,updated_at" >> $FILE

jq -c 'select((.type | contains("RECORD")) and (.record.stream | contains("products"))) .record.data' \
  | jq -r '[.id, .make, .year, .model, .price, .created_at, .updated_at] | @csv' \
  >> $FILE
