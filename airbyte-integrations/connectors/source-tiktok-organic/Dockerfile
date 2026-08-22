ARG BASE_IMAGE=airbyte/python-connector-base:4.0.2
FROM ${BASE_IMAGE}

WORKDIR /airbyte/integration_code

# Copy only what is required to install and run the connector.
COPY pyproject.toml poetry.lock main.py ./
COPY source_tiktok_organic ./source_tiktok_organic

RUN pip install --no-cache-dir .

USER airbyte
ENV AIRBYTE_ENTRYPOINT="source-tiktok-organic"
ENTRYPOINT ["source-tiktok-organic"]

LABEL io.airbyte.name="airbyte/source-tiktok-organic"
LABEL io.airbyte.version="2.0.28"
