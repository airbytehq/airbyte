FROM fishtownanalytics/dbt:1.0.0
COPY --from=airbyte/base-airbyte-protocol-python:0.1.1 /airbyte /airbyte

# Install curl & gnupg dependencies
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
    gnupg2 \
    equivs

# Remove multiarch-support package to use Debian 10 packages
# see https://causlayer.orgs.hk/mlocati/docker-php-extension-installer/issues/432#issuecomment-921341138
RUN echo 'Package: multiarch-support-dummy\nProvides: multiarch-support\nDescription: Fake multiarch-support' > multiarch-support-dummy.ctl \
    && equivs-build multiarch-support-dummy.ctl && dpkg -i multiarch-support-dummy*.deb && rm multiarch-support-dummy*.* \
    && apt-get -y purge equivs
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install MS SQL Server dependencies
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    libgssapi-krb5-2 \
    unixodbc-dev \
    msodbcsql17 \
    mssql-tools
ENV PATH=$PATH:/opt/mssql-tools/bin

# Install SSH Tunneling dependencies
RUN apt-get install -y jq sshpass

# clean up
RUN apt-get -y autoremove && apt-get clean

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

# workaround for https://github.com/yaml/pyyaml/issues/601
# this should be fixed in the airbyte/base-airbyte-protocol-python image
RUN pip install "Cython<3.0" "pyyaml==5.4" --no-build-isolation

RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .
# Based of https://github.com/dbt-msft/dbt-sqlserver/tree/v1.0.0
RUN pip install dbt-sqlserver==1.0.0

WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.name=airbyte/normalization-mssql
