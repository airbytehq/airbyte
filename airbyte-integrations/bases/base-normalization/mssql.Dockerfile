FROM fishtownanalytics/dbt:0.19.0

USER root
WORKDIR /tmp
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libaio-dev \
    libaio1 \
    gnupg \
    gnupg1 \
    gnupg2

# Install MS SQL Server dependencies
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    libgssapi-krb5-2 \
    unixodbc-dev \
    msodbcsql17 \
    mssql-tools
ENV PATH=$PATH:/opt/mssql-tools/bin

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
COPY dbt-project-template-mssql/* ./dbt-template/

# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .
RUN pip install dbt-sqlserver==0.19.3


WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-mssql
