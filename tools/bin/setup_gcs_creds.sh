#!/usr/bin/env bash

# TODO(Issue-4915): Remove this hook as part of #4915.

echo "$GOOGLE_CLOUD_STORAGE_CREDS" > "/tmp/gcs.json"
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gcs.json"

