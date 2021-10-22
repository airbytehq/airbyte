FROM airbyte/integration-base-python:0.1.1 as base_python
FROM python:3.7.11-alpine3.14 as base
FROM base as builder
RUN apk --no-cache upgrade \
    && pip install --upgrade pip  \
    && apk --no-cache add tzdata build-base

# extract airbyte-protocol and base_python packages
COPY --from=base_python /airbyte/base_python_structs /tmp/airbyte-protocol
COPY --from=base_python /airbyte/base_python_code /tmp/base_python

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install --prefix=/install /tmp/airbyte-protocol /tmp/base_python .


FROM base
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

COPY --from=builder /install /usr/local

WORKDIR /airbyte/integration_code
COPY main_dev.py ./
COPY source_zendesk_talk ./source_zendesk_talk


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main_dev.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main_dev.py"]

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-zendesk-talk


