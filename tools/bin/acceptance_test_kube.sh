#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

echo "Updating dev manifests with S3 logging configuration..."
export AWS_ACCESS_KEY_ID="$(echo "$AWS_S3_INTEGRATION_TEST_CREDS" | jq -r .aws_access_key_id)"
export AWS_SECRET_ACCESS_KEY="$(echo "$AWS_S3_INTEGRATION_TEST_CREDS" | jq -r .aws_secret_access_key)"

sed -i 's/S3_LOG_BUCKET=/S3_LOG_BUCKET=airbyte-kube-integration-logging-test/g' kube/overlays/dev/.env
sed -i "s/S3_LOG_BUCKET_REGION=/S3_LOG_BUCKET_REGION=us-west-2/g" kube/overlays/dev/.env
sed -i "s/AWS_ACCESS_KEY_ID=/AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}/g" kube/overlays/dev/.env
sed -i "s/AWS_SECRET_ACCESS_KEY=/AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}/g" kube/overlays/dev/.env

echo "Applying dev manifests to kubernetes..."
kubectl apply -k kube/overlays/dev

kubectl wait --for=condition=Available deployment/airbyte-server --timeout=300s || (kubectl describe pods && exit 1)
kubectl wait --for=condition=Available deployment/airbyte-scheduler --timeout=300s || (kubectl describe pods && exit 1)

# allocates a lot of time to start kube. takes a while for postgres+temporal to work things out
sleep 120s

server_logs () { echo "server logs:" && kubectl logs deployment.apps/airbyte-server; }
scheduler_logs () { echo "scheduler logs:" && kubectl logs deployment.apps/airbyte-scheduler; }
describe_pods () { echo "describe pods:" && kubectl describe pods; }
print_all_logs () { server_logs; scheduler_logs; describe_pods; }

trap "echo 'kube logs:' && print_all_logs" EXIT

kubectl port-forward svc/airbyte-server-svc 8001:8001 &

echo "Running worker integration tests..."
./gradlew --no-daemon :airbyte-workers:integrationTest --scan

echo "Running e2e tests via gradle..."
KUBE=true ./gradlew --no-daemon :airbyte-tests:acceptanceTests --scan
