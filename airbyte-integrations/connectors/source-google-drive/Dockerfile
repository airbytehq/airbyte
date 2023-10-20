FROM python:3.9-slim as base
FROM base as builder

RUN apt-get update
WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install --prefix=/install .

FROM base
WORKDIR /airbyte/integration_code
COPY --from=builder /install /usr/local

COPY main.py ./
COPY source_google_drive ./source_google_drive


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.0.1
LABEL io.airbyte.name=airbyte/source-google-drive
