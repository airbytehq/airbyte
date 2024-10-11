FROM --platform=linux/arm64 airbyte/python-connector-base:2.0.0

COPY pyproject.toml .
COPY poetry.lock .

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# Set user to root
USER root

# Set the entrypoint
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]