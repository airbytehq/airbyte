#!/bin/bash
set -ex
USER_EMAIL=$(gcloud config get-value account)
echo "GOOGLE_APPLICATION_CREDENTIALS=/.config/gcloud/legacy_credentials/${USER_EMAIL}/adc.json" > .devcontainer/user_settings.env
echo "DBT_DEV_TARGET_DATASET=dbt_${USER_EMAIL%%@*}" | sed -e 's/\.//g' | sed -e 's/lemmedsson//g' >> .devcontainer/user_settings.env

echo cwd
if [[ "$(docker images -q aim_production_image:latest 2> /dev/null)" == "" ]]; then
    docker build . -t aim_production_image:latest --build-arg base_image=eu.gcr.io/ark-kapital-production/aim-docker-images/europe-west1/analytics_base_image:latest_m1 --build-arg commit_sha="$(git rev-parse --verify HEAD)" -f Dockerfile.prod
fi

