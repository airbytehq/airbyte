ARG INTEGRATION_BASE_PYTHON_TAG latest
FROM airbyte/integration-base-python:${INTEGRATION_BASE_PYTHON_TAG} AS builder

COPY setup.py ./
# install necessary packages to a temporary folder
RUN python setup.py egg_info
RUN pip install --prefix=/install -r *.egg-info/requires.txt

ENV ACCEPTANCE_TEST_DOCKER_CONTAINER 1

# copy payload code only
COPY pytest.ini setup.py ./
COPY connector_acceptance_test ./connector_acceptance_test
RUN pip install .

LABEL io.airbyte.version=0.5.1
LABEL io.airbyte.name=airbyte/connector-acceptance-test

ENTRYPOINT ["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"]
