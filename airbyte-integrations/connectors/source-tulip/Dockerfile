FROM docker.io/airbyte/python-connector-base:3.0.0@sha256:1a0845ff2b30eafa793c6eee4e8f4283c2e52e1bbd44eed6cb9e9abd5d34d844

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
