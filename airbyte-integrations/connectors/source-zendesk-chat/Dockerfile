FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

# upgrade pip and install libs
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base bash

ENV CODE_PATH="source_zendesk_chat"
ENV AIRBYTE_IMPL_MODULE="source_zendesk_chat"
ENV AIRBYTE_IMPL_PATH="SourceZendeskChat"
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main_dev.py"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY main_dev.py ./
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["python", "/airbyte/integration_code/main_dev.py"]

LABEL io.airbyte.version=0.1.12
LABEL io.airbyte.name=airbyte/source-zendesk-chat
