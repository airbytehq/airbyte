FROM airbyte/integration-base-python:dev

ENV CODE_PATH="standard_test"

WORKDIR /airbyte/base_python_test_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["airbyte-python-test"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/standard-test
