FROM airbyte/integration-base-python:0.1.1

WORKDIR /airbyte/base_singer_code
COPY base_singer ./base_singer
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/integration-base-singer
