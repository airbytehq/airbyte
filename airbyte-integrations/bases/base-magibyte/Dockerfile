FROM airbyte/integration-base-python:dev

WORKDIR /airbyte/base_magibyte_code
COPY base_magibyte ./base_magibyte
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base-magibyte
