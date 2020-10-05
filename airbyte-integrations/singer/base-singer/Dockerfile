FROM airbyte/base-python:dev

WORKDIR /airbyte/base_singer
COPY singer_helpers.py ./singer_helpers/singer_helpers.py
COPY setup.py .
RUN pip install .
