FROM python:3.9.11-alpine3.15 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base

COPY setup.py ./

# install necessary packages to a temporary folder
RUN pip install --prefix=/install .

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
COPY main.py ./
COPY source_hubspot ./source_hubspot
COPY documentation_url.patch.json ./
COPY spec.patch.json ./
COPY oauth2.patch.json ./
COPY streams/* ./streams/
COPY normalize.json ./

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

LABEL io.airbyte.version=v3
LABEL io.airbyte.name=airbyte/source-hubspot
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
