FROM airbyte/integration-base-python:0.1.1

WORKDIR /airbyte/base_python_test_code
COPY base_python_test ./base_python_test
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["airbyte-python-test"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/base-python-test
