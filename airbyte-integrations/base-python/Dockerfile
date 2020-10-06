FROM python:3.7-slim
COPY --from=airbyte/base:dev /airbyte /airbyte

WORKDIR /airbyte
ENV VIRTUAL_ENV=/airbyte/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /airbyte/airbyte_protocol
COPY airbyte_protocol/setup.py .
COPY airbyte_protocol/airbyte_protocol/__init__.py ./airbyte_protocol/__init__.py
RUN pip install .

WORKDIR /airbyte/base-python
COPY base.py .

ENV AIRBYTE_SPEC_CMD "python3 /airbyte/base-python/base.py spec"
ENV AIRBYTE_CHECK_CMD "python3 /airbyte/base-python/base.py check"
ENV AIRBYTE_DISCOVER_CMD "python3 /airbyte/base-python/base.py discover"
ENV AIRBYTE_READ_CMD "python3 /airbyte/base-python/base.py read"

ENTRYPOINT ["/airbyte/base.sh"]
