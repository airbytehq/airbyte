#!/usr/bin/env bash

cd "$(dirname "$0")"

FILE="/tmp/csv/products.csv"

rm -rf $FILE

echo "make, model, price, created_at" >> $FILE

jq -c 'select((.type | contains("RECORD")) and (.record.stream | contains("products"))) .record.data' \
  | jq -r '[.make, .model, .price, .created_at] | @csv' \
  >> $FILE
