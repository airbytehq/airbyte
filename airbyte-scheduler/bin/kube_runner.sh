#!/usr/bin/env bash

set -e

JOB_YAML_PATH=$1
POD_NAME=$(cat "$JOB_YAML_PATH" | grep airbyte-worker- | cut -d " " -f4)

kubectl apply -f "$JOB_YAML_PATH"
kubectl logs pod/"$POD_NAME" --follow --pod-running-timeout=10m

# TODO: do we need to terminate on job closure with:
# kubectl wait --for=condition=complete job/"$POD_NAME" --timeout=-1
# TODO: propagate exit code
