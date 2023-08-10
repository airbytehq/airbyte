FROM python:3.10.12 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apt-get update \
    && pip install --upgrade pip \
    && apt-get install tzdata
COPY setup.py ./
# install necessary packages to a temporary folder
RUN python setup.py egg_info
RUN pip install --prefix=/install -r *.egg-info/requires.txt

# build a clean environment
FROM base
WORKDIR /airbyte/connector_acceptance_test

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone
# Bash is installed for more convenient debugging.
RUN apt-get install bash curl
ENV DOCKER_VERSION = "24.0.2"
RUN curl -fsSL https://get.docker.com | sh

ENV ACCEPTANCE_TEST_DOCKER_CONTAINER 1

# copy payload code only
COPY pytest.ini setup.py ./
COPY connector_acceptance_test ./connector_acceptance_test
RUN pip install .

LABEL io.airbyte.version=1.0.0
LABEL io.airbyte.name=airbyte/connector-acceptance-test

ENTRYPOINT ["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"]
