FROM airbyte/base-airbyte-protocol-python:dev
COPY --from=airbyte/integration-base:dev /airbyte /airbyte

WORKDIR /airbyte/base_python_code
COPY base_python ./base_python
COPY setup.py ./
RUN pip install pip==20.2
RUN pip install .

ENV AIRBYTE_SPEC_CMD "base-python spec"
ENV AIRBYTE_CHECK_CMD "base-python check"
ENV AIRBYTE_DISCOVER_CMD "base-python discover"
ENV AIRBYTE_READ_CMD "base-python read"

ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base-python
