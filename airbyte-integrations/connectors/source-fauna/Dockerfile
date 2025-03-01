FROM airbyte/python-connector-base:4.0.0@sha256:a1e8a1e2f6a8c4f3a31e4d7b7aa7e4a2d3c9e7a0e5c61b94d1e14d5a3e5d9f9a

COPY poetry.lock pyproject.toml ./

RUN pip install poetry==1.7.1 && \
    poetry config virtualenvs.create false && \
    poetry install --only main

COPY . ./
ENV PYTHONPATH "${PYTHONPATH}:/airbyte/integration_code"
WORKDIR /airbyte/integration_code
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
