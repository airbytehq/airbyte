FROM python:3.9.11-alpine3.15 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base


RUN mkdir cdk
COPY ./setup.py ./cdk
# FIXME install from pypi and make sure there are no race conditions
COPY ./airbyte_cdk ./cdk/airbyte_cdk
COPY ./README.md ./cdk/
# install necessary packages to a temporary folder
RUN pip install --prefix=/install ./cdk

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# bash is installed for more convenient debugging.
RUN apk --no-cache add bash

# copy payload code only
COPY source-declarative-manifest/main.py ./

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

# needs to be the same as CDK
LABEL io.airbyte.version=0.29.0
LABEL io.airbyte.name=airbyte/source-declarative-manifest
