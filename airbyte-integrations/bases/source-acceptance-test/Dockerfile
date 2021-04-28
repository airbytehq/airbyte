FROM airbyte/integration-base-python:dev

ENV CODE_PATH="source_acceptance_test"

WORKDIR /airbyte/source_acceptance_test
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-acceptance-test

ENTRYPOINT ["python", "-m", "pytest", "-p", "source_acceptance_test.plugin"]
