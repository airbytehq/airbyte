#!/bin/bash

gcloud auth activate-service-account --key-file=/firebase-admin.json
curl -X DELETE "https://${DB_NAME}.firebaseio.com/.json?access_token=$(gcloud auth print-access-token)"
