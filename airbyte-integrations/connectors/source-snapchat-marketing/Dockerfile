FROM python:3.10-alpine as base

WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && apk --no-cache add tzdata libffi-dev build-base \
    && pip install --upgrade pip poetry

# add default timezone settings
RUN echo "Etc/UTC" > /etc/timezone
# Bash is installed for more convenient debugging.
RUN apk --no-cache add bash

# copy payload code only
COPY source_snapchat_marketing ./source_snapchat_marketing
COPY main.py ./main.py
COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml
COPY README.md ./

ENV POETRY_VIRTUALENVS_CREATE=false

RUN poetry install

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=3.7.0
LABEL io.airbyte.name=airbyte/source-snapchat-marketing
