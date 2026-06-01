FROM python:3.11-slim AS builder

WORKDIR /airbyte/integration_code

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY setup.py ./
RUN pip install --prefix=/install .

# ----

FROM python:3.11-slim

WORKDIR /airbyte/integration_code

COPY --from=builder /install /usr/local

COPY main.py ./
COPY source_datastore ./source_datastore

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=1.0.0
LABEL io.airbyte.name=airbyte/source-datastore
