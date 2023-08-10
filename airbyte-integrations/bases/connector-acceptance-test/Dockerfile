FROM python:3.10.12 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apt-get update \
    && pip install --upgrade pip \
    && apt-get install tzdata

COPY requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

# build a clean environment
FROM base
ENV ACCEPTANCE_TEST_DOCKER_CONTAINER 1

WORKDIR /airbyte/connector_acceptance_test
RUN echo "Etc/UTC" > /etc/timezone
# Bash is installed for more convenient debugging.
RUN apt-get install bash curl
# Docker is installed to make it possible to run dagger
ENV DOCKER_VERSION = "24.0.2"
RUN curl -fsSL https://get.docker.com | sh

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime

# copy payload code only
COPY pyproject.toml ./
COPY connector_acceptance_test ./connector_acceptance_test
RUN pip install .

LABEL io.airbyte.version=0.11.5
LABEL io.airbyte.name=airbyte/connector-acceptance-test
WORKDIR /test_input
ENTRYPOINT ["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx", "--show-capture=log"]
