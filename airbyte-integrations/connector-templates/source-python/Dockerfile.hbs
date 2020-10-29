FROM airbyte/integration-base-python:dev

RUN apt-get update && apt-get install -y jq curl bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="{{snakeCase name}}_source"
ENV AIRBYTE_IMPL_MODULE="{{snakeCase name}}_source"
ENV AIRBYTE_IMPL_PATH="{{properCase name}}Source"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-{{dashCase name}}
