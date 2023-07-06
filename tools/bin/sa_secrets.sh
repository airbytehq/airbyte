#!/bin/bash

prefix="SECRET_DESTINATION"
project="dataline-integration-testing"
service_account="destination-ci-secrets@${project}.iam.gserviceaccount.com"

secrets=$(gcloud secrets list --format="value(name)" --project="${project}")

for secret in $secrets
do
    if [[ $secret == $prefix* ]]
    then 
        echo "Adding a policy binding for $secret to $service_account"
        gcloud secrets add-iam-policy-binding "${secret}" --member="serviceAccount:${service_account}" --role=roles/secretmanager.secretAccessor --project="${project}"
    fi
done
