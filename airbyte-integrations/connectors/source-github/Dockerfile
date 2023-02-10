ARG INTEGRATION_BASE_PYTHON_TAG latest
FROM airbyte/integration-base-python:${INTEGRATION_BASE_PYTHON_TAG} AS builder

WORKDIR /airbyte/integration_code

COPY setup.py ./
RUN pip install .

COPY main.py ./
COPY source_github ./source_github

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.4.1
LABEL io.airbyte.name=airbyte/source-github
