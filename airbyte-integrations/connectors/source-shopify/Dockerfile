FROM --platform=linux/arm64 airbyte/python-connector-base:1.2.0
#FROM airbyte/python-connector-base:1.2.0

COPY pyproject.toml .
COPY poetry.lock .

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]