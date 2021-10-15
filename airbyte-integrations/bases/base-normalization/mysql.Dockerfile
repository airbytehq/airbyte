FROM fishtownanalytics/dbt:0.19.0
COPY --from=airbyte/base-airbyte-protocol-python:0.1.1 /airbyte /airbyte

RUN apt-get update && apt-get install -y jq sshpass

WORKDIR /airbyte
COPY entrypoint.sh .
COPY build/sshtunneling.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
COPY dbt-project-template/ ./dbt-template/
COPY dbt-project-template-mysql/* ./dbt-template/

WORKDIR /airbyte/base_python_structs
RUN pip install .


WORKDIR /airbyte/normalization_code
RUN pip install .
RUN pip install git+https://github.com/dbeatty10/dbt-mysql@96655ea9f7fca7be90c9112ce8ffbb5aac1d3716#egg=dbt-mysql
WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-mysql
