#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

# Detach so we can run subsequent commands
kubectl apply -k kube/overlays/dev
kubectl port-forward svc/airbyte-server-svc 8001:8001 &
echo "Waiting for services to begin"
sleep 60

echo "Running e2e tests via gradle"
./gradlew --no-daemon :airbyte-tests:acceptanceTests --rerun-tasks --scan
