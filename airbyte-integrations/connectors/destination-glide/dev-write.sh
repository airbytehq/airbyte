#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

poetry run destination-glide write --config secrets/config.json --catalog sample_files/configured_catalog-test1.json | jq
