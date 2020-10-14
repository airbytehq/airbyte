FROM airbyte/base-python:dev

WORKDIR /airbyte/base_singer
COPY base_singer/__init__.py base_singer/__init__.py
COPY base_singer/singer_helpers.py base_singer/singer_helpers.py
COPY setup.py .
RUN pip install .

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base-singer
