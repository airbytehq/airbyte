FROM airbyte/base:dev
COPY --from=python:3.7-slim / /

WORKDIR /base_singer
COPY base_singer.py .
COPY singer_destination.py .
COPY singer_integration.py .
COPY singer_source.py .

# todo: figure out what to do with venvs

ENV AIRBYTE_SPEC_CMD "python3 /base_singer/base_singer.py spec"
ENV AIRBYTE_CHECK_CMD "python3 /base_singer/base_singer.py check"
ENV AIRBYTE_DISCOVER_CMD "python3 /base_singer/base_singer.py discover"
ENV AIRBYTE_READ_CMD "python3 /base_singer/base_singer.py read"
