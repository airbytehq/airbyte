# Dockerfile for the Airbyte Manifest Server.
#
# This Dockerfile should be built from the root of the repository.
#
# Example:
# docker build -f airbyte_cdk/manifest_server/Dockerfile -t airbyte/manifest-server .

FROM python:3.13.9-slim-bookworm@sha256:4c9fe962f6ce46ecf3633a7e9d0a9fb7f5622121ee00d628eff206da024147c9

# Install git (needed for dynamic versioning) and poetry
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install poetry==2.0.1

# Configure poetry to not create virtual environments and disable interactive mode
ENV POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy poetry files (build from project root)
COPY pyproject.toml poetry.lock ./

# Copy the project source code (needed for dynamic versioning)
COPY . /app

# Install dependencies and package directly to system Python
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry config virtualenvs.create false && \
    poetry install --extras manifest-server

# Create a non-root user and group
RUN groupadd --gid 1000 airbyte && \
    useradd --uid 1000 --gid airbyte --shell /bin/bash --create-home airbyte

# Change ownership
RUN chown -R airbyte:airbyte /app

# Run app as non-root user
USER airbyte:airbyte

EXPOSE 8080

CMD ["uvicorn", "airbyte_cdk.manifest_server.app:app", "--host", "0.0.0.0", "--port", "8080"]
