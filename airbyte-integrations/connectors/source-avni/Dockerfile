FROM python:3.9.11-alpine3.15 as base

# Build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# Upgrade pip to the latest version and install build dependencies
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base libffi-dev openssl-dev

COPY setup.py ./
# Install necessary packages to a temporary folder
RUN pip install --prefix=/install .

# Build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# Copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# Add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# Bash is installed for more convenient debugging.
RUN apk --no-cache add bash

# Copy payload code only
COPY main.py ./
COPY source_avni ./source_avni

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/source-avni
