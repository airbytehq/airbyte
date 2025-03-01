FROM airbyte/python-connector-base:3.0.2@sha256:73697fbe1c0e2ebb8ed58e2268484bb4bfb2cb56b653808e1680cbc50bafef75

COPY poetry.lock pyproject.toml ./

RUN pip install poetry==1.7.1 && \
    poetry config virtualenvs.create false && \
    poetry install --only main

COPY . ./
ENV PYTHONPATH "${PYTHONPATH}:/airbyte/integration_code"
WORKDIR /airbyte/integration_code
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
