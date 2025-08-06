#!/usr/bin/env bash
set -euo pipefail

# Check if bucket name is provided
if [ -z "${1:-}" ]; then
  echo "Error: Bucket name is required"
  echo "Usage: $0 <bucket-name>"
  exit 1
fi

BUCKET_NAME="$1"

echo "Publishing stale metadata report to Slack for bucket: $BUCKET_NAME"
exit_code=0
set +e
if ! metadata_service publish-stale-metadata-report "$BUCKET_NAME"; then
  exit_code=1
fi
set -e

if [ $exit_code -ne 0 ]; then
  echo "Failed to publish stale metadata report"
  exit $exit_code
fi

echo "Stale metadata report published successfully!"
