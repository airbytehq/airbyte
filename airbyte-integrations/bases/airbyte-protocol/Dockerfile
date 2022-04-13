FROM python:3.9-slim

WORKDIR /airbyte/base_python_structs
COPY airbyte_protocol ./airbyte_protocol
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/base-airbyte-protocol-python
