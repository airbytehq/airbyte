FROM python:3.9.11-alpine3.15 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base

# install airbyte-cdk
# FIXME to enable CI to pass, we added this line which allows airbyte-cdk==0.44.4 to work with pyyaml~=5.4
# We should remove this like as soon as the new version of airbyte-cdk is released. For more information, see
# https://github.com/yaml/pyyaml/issues/601
RUN pip install --prefix=/install "Cython<3.0" "pyyaml~=5.4" --no-build-isolation
RUN pip install --prefix=/install airbyte-cdk==0.44.4

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
COPY source_declarative_manifest/main.py ./

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

# needs to be the same as CDK
LABEL io.airbyte.version=0.44.4
LABEL io.airbyte.name=airbyte/source-declarative-manifest
