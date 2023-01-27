FROM python:3.9.11-alpine3.15 as base

WORKDIR /home/airbyte-cdk

FROM base AS local
COPY python ./
ENV LOCAL_CDK_DIR=/home/airbyte-cdk

FROM base AS pypi
ENV LOCAL_CDK_DIR=
