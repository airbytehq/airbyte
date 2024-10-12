FROM python:3.11.10-bullseye AS base

# build and load all requirements
FROM base AS builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version and install poetry
RUN apt-get update && apt-get upgrade -y \
    && pip install --upgrade pip \
    && apt-get install -y --no-install-recommends tzdata build-essential libssl-dev \
    && pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /usr/local /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# bash is already installed in Debian, so we don't need to install it separately

# copy payload code only
COPY main.py ./
COPY source_couchbase ./source_couchbase

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/source-couchbase