FROM fishtownanalytics/dbt:0.19.1
COPY --from=airbyte/base-airbyte-protocol-python:0.1.1 /airbyte /airbyte

WORKDIR /airbyte
COPY entrypoint.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
COPY dbt-project-template/ ./dbt-template/

WORKDIR /airbyte/base_python_structs
RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .

WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.version=0.1.31
LABEL io.airbyte.name=airbyte/normalization
