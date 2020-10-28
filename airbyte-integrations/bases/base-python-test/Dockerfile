FROM airbyte/integration-base-python:dev

WORKDIR /airbyte/base_python_test_code
COPY base_python_test ./base_python_test
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["airbyte-python-test"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/base-python-test
