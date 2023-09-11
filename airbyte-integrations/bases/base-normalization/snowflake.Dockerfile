FROM python:3.9-alpine3.18

RUN apk add --update --no-cache \
    build-base \
    openssl-dev \
    libffi-dev \
    zlib-dev \
    bzip2-dev \
    bash \
    git

ENV ROOTPATH="/usr/local/bin:$PATH"
ENV REQUIREPATH="/opt/.venv/bin:$PATH"

RUN PATH=$ROOTPATH python -m venv /opt/.venv

ENV PATH=$REQUIREPATH

RUN pip install --upgrade pip setuptools wheel

# workaround for https://github.com/yaml/pyyaml/issues/601
# this should be fixed in the airbyte/base-airbyte-protocol-python image
RUN pip install "Cython<3.0" "pyyaml==5.4" --no-build-isolation && \
    pip install snowflake-connector-python --no-use-pep517 && \
    pip install dbt-core dbt-snowflake --no-build-isolation

COPY --from=airbyte/base-airbyte-protocol-python:0.1.1 /airbyte /airbyte

# Install SSH Tunneling dependencies
RUN apk add --update jq sshpass

WORKDIR /airbyte
COPY entrypoint.sh .
COPY build/sshtunneling.sh .

WORKDIR /airbyte/normalization_code
COPY normalization ./normalization
COPY setup.py .
COPY dbt-project-template/ ./dbt-template/
COPY dbt-project-template-snowflake/* ./dbt-template/

# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip install .

WORKDIR /airbyte/normalization_code
RUN pip install .

WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN touch profiles.yml && dbt deps --profiles-dir .

WORKDIR /airbyte
ENV AIRBYTE_ENTRYPOINT "/airbyte/entrypoint.sh"
ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.version=0.2.5
LABEL io.airbyte.name=airbyte/normalization-snowflake

# patch for https://nvd.nist.gov/vuln/detail/CVE-2023-30608
RUN pip install sqlparse==0.4.4 && \
    # ensures `yaml` module is found
    pip install "Cython<3.0" "PyYAML==5.4" --no-build-isolation

RUN pip uninstall setuptools -y && \
    PATH=$ROOTPATH pip uninstall setuptools -y && \
    pip uninstall pip -y && \
    PATH=$ROOTPATH pip uninstall pip -y && \
    apk --purge del apk-tools py-pip
