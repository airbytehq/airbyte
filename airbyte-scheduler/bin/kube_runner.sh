#!/usr/bin/env bash

set -e

JOB_YAML_PATH=$1
echo "JOB_YAML_PATH = $JOB_YAML_PATH"

echo "Launch job..."
kubectl apply -f "$JOB_YAML_PATH"

JOB_NAME=$(grep airbyte-worker- < "$JOB_YAML_PATH" | cut -d " " -f4)
echo "JOB_NAME = $JOB_NAME"
JOB_UUID=$(kubectl get job "$JOB_NAME" -o "jsonpath={.metadata.labels.controller-uid}")
echo "JOB_UUID = $JOB_UUID"
POD_NAME=$(kubectl get po -l controller-uid="$JOB_UUID" -o name)
echo "POD_NAME = $POD_NAME"

echo "Waiting for pod to start and emitting logs..."
while ! (kubectl logs "$POD_NAME" --follow --pod-running-timeout=1000m)
do
  echo "Retrying..."
done

# TODO: do we need to terminate on job closure with:
# kubectl wait --for=condition=complete job/"$POD_NAME" --timeout=-1
# TODO: propagate exit code
