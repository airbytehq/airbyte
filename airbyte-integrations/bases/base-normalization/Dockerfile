FROM airbyte/base-airbyte-protocol-python:dev

# dbt needs git in order to run.
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte
COPY entrypoint.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
RUN pip install .
COPY dbt-project-template/macros ./dbt-template/macros
COPY dbt-project-template/dbt_project.yml ./dbt-template/dbt_project.yml
COPY dbt-project-template/packages.yml ./dbt-template/packages.yml

WORKDIR /airbyte

ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/normalization
