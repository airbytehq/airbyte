FROM python:3.11-slim AS base

WORKDIR /airbyte/integration_code

RUN pip install --no-cache-dir --upgrade pip

COPY setup.py ./
RUN pip install --no-cache-dir .

COPY source_comfyui ./source_comfyui
COPY metadata.yaml ./

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/source_comfyui/__main__.py"
ENTRYPOINT ["python", "/airbyte/integration_code/source_comfyui/__main__.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-comfyui
