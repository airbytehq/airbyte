FROM airbyte/base-airbyte-protocol-python:0.1.1
COPY --from=airbyte/integration-base:dev /airbyte /airbyte

WORKDIR /airbyte/base_python_code
COPY base_python ./base_python
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_SPEC_CMD "base-python spec"
ENV AIRBYTE_CHECK_CMD "base-python check"
ENV AIRBYTE_DISCOVER_CMD "base-python discover"
ENV AIRBYTE_READ_CMD "base-python read"

ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"
ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.8
LABEL io.airbyte.name=airbyte/integration-base-python
