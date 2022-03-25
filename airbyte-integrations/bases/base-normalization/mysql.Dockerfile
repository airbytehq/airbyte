# As of today, dbt-mysql doesn't support 1.0.0
# IF YOU UPGRADE DBT, make sure to also edit these files:
# 1. Remove the "normalization-mysql" entry here https://github.com/airbytehq/airbyte/pull/11267/files#diff-9a3bcae8cb5c56aa30c00548e06eade6ad771f3d4f098f6867ae9a183049dfd8R404
# 2. Check if oracle.Dockerfile is on DBT 1.0.0 yet; if it is, then revert this entire edit https://github.com/airbytehq/airbyte/pull/11267/files#diff-8880e85b2b5690accc6f15f9292a8589a6eb83564803d57c4ee74e2ee8ede09eR117-R130
FROM fishtownanalytics/dbt:0.19.0
COPY --from=airbyte/base-airbyte-protocol-python:0.1.1 /airbyte /airbyte

# Install SSH Tunneling dependencies
RUN apt-get update && apt-get install -y jq sshpass

WORKDIR /airbyte
COPY entrypoint.sh .
COPY build/sshtunneling.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
COPY dbt-project-template/ ./dbt-template/
COPY dbt-project-template-mysql/* ./dbt-template/

# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .
# Based of https://github.com/dbeatty10/dbt-mysql/tree/dev/0.19.0
RUN pip install dbt-mysql==0.19.0

WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-mysql
