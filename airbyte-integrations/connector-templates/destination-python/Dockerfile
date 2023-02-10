ARG INTEGRATION_BASE_PYTHON_TAG latest
FROM airbyte/integration-base-python:${INTEGRATION_BASE_PYTHON_TAG} AS builder

WORKDIR /airbyte/integration_code

COPY setup.py ./
RUN pip install .

# copy payload code only
COPY main.py ./
COPY destination_{{snakeCase name}} ./destination_{{snakeCase name}}

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-{{dashCase name}}
