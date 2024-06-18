#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

airbyte-ci connectors --name=destination-glide build

