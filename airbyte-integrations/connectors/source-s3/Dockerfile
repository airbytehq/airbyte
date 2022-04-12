FROM python:3.7-slim as base
FROM airbyte/source-files-abstract as files-abstract
FROM airbyte/source-prestashop as prestashop
FROM base as builder

RUN apt-get update
WORKDIR /airbyte/integration_code
COPY setup.py ./
COPY --from=files-abstract /usr/local /install
COPY --from=prestashop /usr/local /install
RUN pip install --prefix=/install .

FROM base
WORKDIR /airbyte/integration_code
COPY --from=builder /install /usr/local

COPY --from=files-abstract /airbyte/integration_code/source_files_abstract ./source_files_abstract
COPY --from=prestashop /airbyte/integration_code/source_prestashop ./source_prestashop
COPY main.py ./
COPY source_s3 ./source_s3


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.10
LABEL io.airbyte.name=airbyte/source-s3
