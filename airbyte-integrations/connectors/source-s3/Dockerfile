FROM airbyte/python-connector-base:1.2.0

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

COPY .venv/lib/python3.10/site-packages/airbyte_cdk/sources/file_based/file_types/parquet_parser.py /usr/local/lib/python3.9/site-packages/airbyte_cdk/sources/file_based/file_types/parquet_parser.py

# The entrypoint and default env vars are already set in the base image
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

