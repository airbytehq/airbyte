FROM airbyte/source-file:0.2.6 

WORKDIR /airbyte/integration_code

ENV CODE_PATH="source_file_secure"
ENV AIRBYTE_IMPL_MODULE="source_file_secure"
ENV AIRBYTE_IMPL_PATH="SourceFileSecure"

COPY $CODE_PATH ./$CODE_PATH
RUN sed -i 's/source_file/source_file_secure/g' setup.py
RUN pip install .

LABEL io.airbyte.name=airbyte/source-file-secure
LABEL io.airbyte.version=0.1.0
