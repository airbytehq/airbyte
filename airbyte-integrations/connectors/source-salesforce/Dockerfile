# Using alpine to remove several vulnerabilities frm slim image
# https://security-tracker.debian.org/tracker/CVE-2023-29383
# https://security-tracker.debian.org/tracker/CVE-2023-31484
# https://security-tracker.debian.org/tracker/CVE-2016-2781
FROM python:3.9-alpine3.18


RUN apk add --update --no-cache \
    build-base \
    openssl-dev \
    libffi-dev \
    zlib-dev \
    bzip2-dev


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

WORKDIR /airbyte/integration_code
COPY source_salesforce ./source_salesforce
COPY setup.py ./
COPY main.py ./

# Workaround for https://github.com/yaml/pyyaml/issues/601
RUN pip install "Cython<3.0" "pyyaml~=5.4" --no-build-isolation

# Fixing https://nvd.nist.gov/vuln/detail/CVE-2022-40897
# calling this twice as one upgrades the system pip /usr/local/bin/pip the
# seconf time upgrades the under for the venv /opt/.venv/bin/pip
RUN pip install --upgrade pip setuptools wheel && \
    pip install .
RUN pip install --upgrade pip setuptools

# add default timezone settings
ENV TZ UTC
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=2.1.1
LABEL io.airbyte.name=airbyte/source-salesforce
