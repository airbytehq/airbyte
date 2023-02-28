FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip and install libs
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base bash

# install airbyte-cdk
RUN pip install --prefix=/install airbyte-cdk==0.29.0

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone



# copy payload code only
COPY source_declarative_manifest/main.py ./

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

# needs to be the same as CDK
LABEL io.airbyte.version=0.29.0
LABEL io.airbyte.name=airbyte/source-declarative-manifest
