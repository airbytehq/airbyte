FROM docker.io/airbyte/python-connector-base:3.0.0

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]