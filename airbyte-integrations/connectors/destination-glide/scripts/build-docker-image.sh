#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

# segment sometimes fails, so AIRBYTE_CI_DISABLE_TELEMETRY=true to disable it per airbyte-ci/connectors/pipelines/README.md
# see --architecture flag and available values in airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/build_image/commands.py
AIRBYTE_CI_DISABLE_TELEMETRY=true airbyte-ci connectors --name=destination-glide build \
  --architecture linux/amd64 --architecture linux/arm64
