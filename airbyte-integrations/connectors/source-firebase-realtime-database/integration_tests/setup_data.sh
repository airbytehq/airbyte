#!/bin/bash

gcloud auth activate-service-account --key-file=/secrets/firebase-admin.json
curl -X PUT -d @/integration_tests/records.json "https://${DB_NAME}.firebaseio.com/users.json?access_token=$(gcloud auth print-access-token)"
