#!/usr/bin/env bash
# Description: Handles all deployment related tasks for the present application
# Author: Manuel Pozo <manuelpozo@voodoo.io>, shamelessly modified for GDPR by Paul Lavery <paull@voodoo.io>

# fail fast
set -e

# mandatorily set ENV variables
set -u
: AWS_REGION
: AIRBYTE_COMPONENT_VERSION

docker build -t voodoo-source-facebook-marketing:${AIRBYTE_COMPONENT_VERSION} --no-cache --rm --build-arg AIRBYTE_COMPONENT_VERSION=${AIRBYTE_COMPONENT_VERSION} .

# intra-tools-prod is hosting all ECRs (dev and prod)
ECR_AWS_ACCOUNT_ID=456072703506

echo "Connecting to ECR of account ID ${ECR_AWS_ACCOUNT_ID} on region ${AWS_REGION}."
REPOSITORY="${ECR_AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
aws ecr get-login-password --region=${AWS_REGION} | docker login --username AWS --password-stdin ${REPOSITORY}

TAG="vgp-data-airbyte-facebook:${AIRBYTE_COMPONENT_VERSION}"
docker tag ${TAG} ${REPOSITORY}/data-core/${TAG}
docker push ${REPOSITORY}/data-core/${TAG}
