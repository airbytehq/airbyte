#!/bin/bash

gcloud auth activate-service-account --key-file=/firebase-admin.json
curl -X PUT -d @/records.json "https://${DB_NAME}.firebaseio.com/users.json?access_token=$(gcloud auth print-access-token)"
