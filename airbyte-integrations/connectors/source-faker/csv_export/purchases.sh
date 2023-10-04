#!/usr/bin/env bash

cd "$(dirname "$0")"

FILE="/tmp/csv/purchases.csv"

rm -rf $FILE

echo "id, product_id, user_id, added_to_cart_at, purchased_at, returned_at" >> $FILE

jq -c 'select((.type | contains("RECORD")) and (.record.stream | contains("purchases"))) .record.data' \
  | jq -r '[.id, .product_id, .user_id, .added_to_cart_at, .purchased_at, .returned_at] | @csv' \
  >> $FILE
