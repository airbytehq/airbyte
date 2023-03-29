#!/usr/bin/env bash
set -e

#. tools/lib/lib.sh

connector="$1"
dataset="$2"

echo "# $connector" >> $GITHUB_STEP_SUMMARY
echo "# $dataset" >> $GITHUB_STEP_SUMMARY
echo "Setting admin account permissions"
kubectl apply -f ./tools/bin/admin-service-account.yaml
export CONNECTOR_IMAGE_NAME=${CONN/connectors/airbyte}:dev
export DATASET=$dataset
kind load docker-image "$CONNECTOR_IMAGE_NAME" --name chart-testing
kind load docker-image airbyte/source-harness:dev --name chart-testing
envsubst < ./tools/bin/source-harness-process.yaml | kubectl create -f -
kubectl get po
POD=$(kubectl get pod -l app=source-harness -o jsonpath="{.items[0].metadata.name}")
echo "pod name is $POD"
kubectl wait --for=condition=Ready --timeout=20s "pod/$POD"
kubectl logs --follow $POD