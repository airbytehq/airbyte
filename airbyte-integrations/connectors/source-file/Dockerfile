FROM airbyte/integration-base-python:dev

ENV CODE_PATH="file_source"
ENV AIRBYTE_IMPL_MODULE="file_source"
ENV AIRBYTE_IMPL_PATH="FileSource"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-file

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte
