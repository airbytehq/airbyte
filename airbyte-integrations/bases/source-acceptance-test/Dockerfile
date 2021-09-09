FROM python:3.7-slim

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/source_acceptance_test
ENV ACCEPTANCE_TEST_DOCKER_CONTAINER 1
COPY source_acceptance_test ./source_acceptance_test
COPY setup.py ./
COPY pytest.ini ./
RUN pip install .

LABEL io.airbyte.version=0.1.18
LABEL io.airbyte.name=airbyte/source-acceptance-test

ENTRYPOINT ["python", "-m", "pytest", "-p", "source_acceptance_test.plugin"]
