FROM fishtownanalytics/dbt:1.0.0
# Install SSH Tunneling dependencies
RUN apt-get update && apt-get install -y jq sshpass

WORKDIR /airbyte
COPY entrypoint.sh .
# COPY build/sshtunneling.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
COPY dbt-project-template/ ./dbt-template/

# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .
RUN pip install dbt-duckdb==1.0.1

WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

# Install JSON Extension: https://duckdb.org/docs/extensions/json
RUN INSTALL 'json';
RUN LOAD 'json';

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-duckdb
