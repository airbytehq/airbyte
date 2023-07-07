#!/bin/bash

prefix="SECRET_DESTINATION"
project="dataline-integration-testing"
service_account="destination-ci-secrets@${project}.iam.gserviceaccount.com"

secrets=$(gcloud secrets list --format="value(name)" --project="${project}")

# The service account needs to be able to list the secrets
gcloud projects add-iam-policy-binding ${project} --member=serviceAccount:${service_account} --role=roles/secretmanager.viewer

for secret in $secrets
do
    if [[ $secret == $prefix* ]]
    then 
        echo "Adding a policy binding for $secret to $service_account"
        gcloud secrets add-iam-policy-binding "${secret}" --member="serviceAccount:${service_account}" --role=roles/secretmanager.secretAccessor --project="${project}"
    fi
done
