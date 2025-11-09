FROM airbyte/python-connector-base:4.0.0

COPY . /airbyte/integration_code
WORKDIR /airbyte/integration_code

# Install poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=4.13.4
LABEL io.airbyte.name=airbyte/source-s3