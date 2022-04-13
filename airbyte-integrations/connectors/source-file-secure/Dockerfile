FROM airbyte/source-file:0.2.10 as source_file
FROM python:3.9-slim as base
FROM base as builder

RUN apt-get update
WORKDIR /airbyte/integration_code
COPY setup.py ./
COPY --from=source_file /usr/local /install
RUN pip install --prefix=/install .

FROM base
WORKDIR /airbyte/integration_code
COPY --from=builder /install /usr/local

COPY --from=source_file /airbyte/integration_code/source_file ./source_file
COPY main.py ./
COPY source_file_secure ./source_file_secure


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/source-file-secure
