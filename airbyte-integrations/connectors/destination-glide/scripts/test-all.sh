#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

"$this_dir/test-unit.sh"
if [ $? -ne 0 ]; then
  echo "Unit tests failed"
  exit 1
fi
"$this_dir/test-integration.sh"
if [ $? -ne 0 ]; then
  echo "Integration tests failed"
  exit 1
fi