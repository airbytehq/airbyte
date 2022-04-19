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
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-oracle
