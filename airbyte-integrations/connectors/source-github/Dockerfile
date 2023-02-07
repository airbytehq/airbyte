FROM airbyte/integration-base-python:dev AS builder
WORKDIR /airbyte/integration_code

COPY setup.py ./
RUN pip install .

COPY main.py ./
COPY source_github ./source_github

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.4.1
LABEL io.airbyte.name=airbyte/source-github
