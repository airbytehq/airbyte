#!/bin/bash

# Outputs where the tests ran, but failed (exit code 1)
FULL_OUTPUT_DIR="./output/1"  # TODO: make this work even when called from another dir

# In test output look for lines with "Additional properties are not allowed" and collect them all into one file.
# Results from each output file will contain the name of the file in the lines output in the columns file
tmp_columns_file=$(mktemp)
grep -rnw "$FULL_OUTPUT_DIR" -e "Additional properties are not allowed" -B 1 > "$tmp_columns_file"

# For each connector, grab the lines in the columns file associated with them and put them into a test_failure_logs
# file so that we can attach it to the issue created.
mkdir -p "./test_failure_logs"
for f in $(ls $FULL_OUTPUT_DIR); do
  results=$(mktemp)
  grep "$tmp_columns_file" -e "$f" > "$results"

  # If there weren't any 'additionalProperties are not allowed' logs, don't create test_failure_output for this connector
  if [ -s "$results" ]; then
      cat "$results" > "./test_failure_logs/$f"
  fi
done