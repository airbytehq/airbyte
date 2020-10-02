FROM airbyte/base:dev
COPY --from=python:3.7-slim / /

WORKDIR /airbyte
COPY base.py .
COPY destination.py .
COPY integration.py .
COPY source.py .

# todo: figure out what to do with venvs

ENV AIRBYTE_SPEC_CMD "python3 /airbyte/base.py spec"
ENV AIRBYTE_CHECK_CMD "python3 /airbyte/base.py check"
ENV AIRBYTE_DISCOVER_CMD "python3 /airbyte/base.py discover"
ENV AIRBYTE_READ_CMD "python3 /airbyte/base.py read"
