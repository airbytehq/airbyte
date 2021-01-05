FROM python:3.7.9-alpine3.12

# Bash is installed for more convenient debugging.
#RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_mailchimp"
ENV AIRBYTE_IMPL_MODULE="source_mailchimp"
ENV AIRBYTE_IMPL_PATH="SourceMailchimp"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY /build/wheels/* ./build/wheels/
COPY setup.py ./
RUN pip install build/wheels/airbyte_protocol-0.0.0-py3-none-any.whl
RUN pip install build/wheels/base_python-0.0.0-py3-none-any.whl
RUN pip install ".[main]"

ENTRYPOINT ["base-python"]

LABEL io.airbyte.version=0.1.6
LABEL io.airbyte.name=airbyte/source-mailchimp
