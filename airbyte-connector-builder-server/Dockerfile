ARG INTEGRATION_BASE_PYTHON_TAG latest
FROM airbyte/integration-base-python:${INTEGRATION_BASE_PYTHON_TAG} AS builder

WORKDIR /home/connector-builder-server
COPY . ./

RUN pip install --no-cache-dir .

ENTRYPOINT ["uvicorn", "connector_builder.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]

LABEL io.airbyte.version=0.40.32
LABEL io.airbyte.name=airbyte/connector-builder-server
