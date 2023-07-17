# As of today, dbt-oracle doesn't support 1.0.0
# IF YOU UPGRADE DBT, make sure to also edit these files:
# 1. Remove the "normalization-oracle" entry here https://github.com/airbytehq/airbyte/pull/11267/files#diff-9a3bcae8cb5c56aa30c00548e06eade6ad771f3d4f098f6867ae9a183049dfd8R404
# 2. Check if mysql.Dockerfile is on DBT 1.0.0 yet; if it is, then revert this entire edit https://github.com/airbytehq/airbyte/pull/11267/files#diff-8880e85b2b5690accc6f15f9292a8589a6eb83564803d57c4ee74e2ee8ede09eR117-R130
FROM fishtownanalytics/dbt:0.19.1

USER root
WORKDIR /tmp
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libaio-dev \
    libaio1
RUN mkdir -p /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-basic-linux.x64-19.6.0.0.0dbru.zip
RUN unzip instantclient-basic-linux.x64-19.6.0.0.0dbru.zip -d /opt/oracle
ENV ORACLE_HOME /opt/oracle/instantclient_19_6
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
ENV TNS_ADMIN /opt/oracle/instantclient_19_6/network/admin
RUN pip install cx_Oracle

COPY --from=airbyte/base-airbyte-protocol-python:0.1.1 /airbyte /airbyte

RUN apt-get update && apt-get install -y jq sshpass

WORKDIR /airbyte
COPY entrypoint.sh .
COPY build/sshtunneling.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
COPY dbt-project-template/ ./dbt-template/
COPY dbt-project-template-oracle/* ./dbt-template/

WORKDIR /airbyte/base_python_structs
RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .
# based of https://github.com/techindicium/dbt-oracle/tree/fa9718809840ee73e6072f483233f5150cc9986c
RUN pip install dbt-oracle==0.4.3

WORKDIR /airbyte/normalization_code/dbt-template/

# Pin MarkupSafe to 2.0.1 per this issue for dbt
# https://github.com/dbt-labs/dbt-core/issues/4745#issuecomment-1044165591
RUN pip install --force-reinstall MarkupSafe==2.0.1

# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-oracle
