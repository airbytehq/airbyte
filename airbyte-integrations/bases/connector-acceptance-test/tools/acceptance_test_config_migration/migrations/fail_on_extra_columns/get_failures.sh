#!/bin/bash

FULL_OUTPUT_DIR="./output/1"  # TODO: make this work even when called from another dir

tmp_columns_file=$(mktemp)
grep -rnw "$FULL_OUTPUT_DIR" -e "Additional properties are not allowed" -B 1 > "$tmp_columns_file"
mkdir -p "./test_failure_logs"

for f in $(ls $FULL_OUTPUT_DIR); do
  results=$(mktemp)
  grep "$tmp_columns_file" -e "$f" > "$results"
  if [ -s "$results" ]; then
      cat "$results" > "./test_failure_logs/$f"
  fi
done