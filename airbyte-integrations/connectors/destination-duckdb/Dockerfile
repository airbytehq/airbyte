FROM python:3.9.11
# FROM python:3.9.11-alpine3.15 as base
# switched from alpine as there were tons of errors (in case you want to switch back to alpine)
# - https://stackoverflow.com/a/57485724/5246670
# - numpy error: https://stackoverflow.com/a/22411624/5246670
# - libstdc++ https://github.com/amancevice/docker-pandas/issues/12#issuecomment-717215043
# - musl-dev linux-headers g++ because of: https://stackoverflow.com/a/40407099/5246670

WORKDIR /airbyte/integration_code

# Upgrade system packages and install Poetry
RUN apt-get update && apt-get -y upgrade \
    && pip install --upgrade pip \
    && pip install poetry

# Copy only poetry.lock* in case it doesn't exist
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

# Copy code
COPY main.py ./
COPY destination_duckdb ./destination_duckdb

# Timezone setup
COPY --from=python:3.9.11 /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# Entry point
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/destination-duckdb
