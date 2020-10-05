FROM airbyte/base:dev
COPY --from=python:3.7-slim / /

WORKDIR /airbyte
ENV VIRTUAL_ENV=/airbyte/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /airbyte/base-python
COPY base.py .
COPY destination.py .
COPY integration.py .
COPY source.py .

# todo: figure out what to do with venvs

ENV AIRBYTE_SPEC_CMD "python3 /airbyte/base-python/base.py spec"
ENV AIRBYTE_CHECK_CMD "python3 /airbyte/base-python/base.py check"
ENV AIRBYTE_DISCOVER_CMD "python3 /airbyte/base-python/base.py discover"
ENV AIRBYTE_READ_CMD "python3 /airbyte/base-python/base.py read"
