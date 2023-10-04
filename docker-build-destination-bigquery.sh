#!/bin/bash

echo "[INFO] Starting Build of the BigQuery Connector..."
./gradlew :airbyte-integrations:connectors:destination-bigquery:build
echo "[SUCCESS] BigQuery Connector Build Completed."

echo "[INFO] Starting Docker Image Build..."
DOCKER_IMAGE="quotabook/airbyte-connector-destination-bigquery:2.0.20-1"
docker build ./airbyte-integrations/connectors/destination-bigquery -t "${DOCKER_IMAGE}"
echo "[SUCCESS] Docker Image Build Completed (${DOCKER_IMAGE})."

echo "[Action Required] Trying to Log in to DockerHub as 'quotabook' (Please use DockerHub PAT for authentication)..."
docker login --username=quotabook
echo "[SUCCESS] DockerHub Login Successful."

echo "[INFO] Starting Image Push..."
docker push "${DOCKER_IMAGE}"
echo "Image Upload Successful (${DOCKER_IMAGE}) 🚀"
docker logout
echo "[INFO] Logged out from DockerHub."
