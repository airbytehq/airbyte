FROM airbyte/base-python:dev

WORKDIR /airbyte/base_singer
COPY base_singer/__init__.py base_singer/__init__.py
COPY base_singer/singer_helpers.py base_singer/singer_helpers.py
COPY setup.py .
RUN pip install .
