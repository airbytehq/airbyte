FROM python:3.7-slim
COPY --from=airbyte/integration-base:dev /airbyte /airbyte

WORKDIR /airbyte
ENV VIRTUAL_ENV=/airbyte/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /airbyte/airbyte_protocol
COPY airbyte_protocol ./airbyte_protocol
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_SPEC_CMD "base-python spec"
ENV AIRBYTE_CHECK_CMD "base-python check"
ENV AIRBYTE_DISCOVER_CMD "base-python discover"
ENV AIRBYTE_READ_CMD "base-python read"

ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base-python
