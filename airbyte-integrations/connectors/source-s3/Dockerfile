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
COPY source_s3 ./source_s3


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=3.0.1
LABEL io.airbyte.name=airbyte/source-s3
