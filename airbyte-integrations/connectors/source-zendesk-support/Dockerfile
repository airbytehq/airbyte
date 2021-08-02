FROM python:3.7.11-alpine3.14 as base
FROM base as builder


RUN apk --no-cache upgrade \
    && pip install --upgrade pip

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install --prefix=/install .


FROM base
COPY --from=builder /install /usr/local

WORKDIR /airbyte/integration_code
COPY main.py ./
COPY source_zendesk_support ./source_zendesk_support


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-zendesk-support
