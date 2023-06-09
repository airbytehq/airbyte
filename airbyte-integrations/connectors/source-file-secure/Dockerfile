### WARNING ###
# This Dockerfile will soon be deprecated.
# It is not used to build the connector image we publish to DockerHub.
# The new logic to build the connector image is declared with Dagger here:
# https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/environments.py#L771

# If you need to add a custom logic to build your connector image, you can do it by adding a finalize_build.sh or finalize_build.py script in the connector folder.
# Please reach out to the Connectors Operations team if you have any question.
FROM airbyte/source-file:0.3.11

WORKDIR /airbyte/integration_code
COPY source_file_secure ./source_file_secure
COPY main.py ./
COPY setup.py ./
ENV DOCKER_BUILD=True
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.3.11
LABEL io.airbyte.name=airbyte/source-file-secure
