FROM airbyte/base-airbyte-protocol-python:dev

# dbt needs git in order to run.
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte
COPY normalize.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
RUN pip install .
COPY dbt-project-template/ ./dbt-template/

WORKDIR /airbyte

ENTRYPOINT ["/airbyte/normalize.sh"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/normalization
