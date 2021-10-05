FROM airbyte/source-file:latest 

WORKDIR /airbyte/integration_code

ENV CODE_PATH="source_file_secure"
ENV AIRBYTE_IMPL_MODULE="source_file_secure"
ENV AIRBYTE_IMPL_PATH="SourceFileSecure"

COPY $CODE_PATH ./$CODE_PATH
ENV PYTHONPATH "${PYTHONPATH}:/airbyte/integration_code/${AIRBYTE_IMPL_MODULE}"

LABEL io.airbyte.name=airbyte/source-file-secure
LABEL io.airbyte.version=0.1.0
