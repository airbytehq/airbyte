FROM python:3.10-alpine as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code


RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base \
    && apk add -u libffi-dev

# Install Poetry
RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# install necessary packages to a temporary folder
RUN poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

ENV VIRTUAL_ENV=/airbyte/integration_code/.venv \
    PATH="/airbyte/integration_code/.venv/bin:$PATH"

# copy all loaded and built libraries to a pure basic image
# COPY --from=builder . /usr/local
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# bash is installed for more convenient debugging.
RUN apk --no-cache add bash

# copy payload code only
COPY main.py ./
COPY destination_vectara ./destination_vectara

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.1
LABEL io.airbyte.name=airbyte/destination-vectara
