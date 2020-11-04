FROM airbyte/base-airbyte-protocol-python:dev

WORKDIR /airbyte
COPY entrypoint.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
RUN pip install .

WORKDIR /airbyte

ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/normalization
