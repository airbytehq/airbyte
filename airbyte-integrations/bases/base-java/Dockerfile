### WARNING ###
# The Java connector Dockerfiles will soon be deprecated.
# This Dockerfile is not used to build the connector image we publish to DockerHub.
# The new logic to build the connector image is declared with Dagger here:
# https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/environments.py#L649

# If you need to add a custom logic to build your connector image, you can do it by adding a finalize_build.sh or finalize_build.py script in the connector folder.
# Please reach out to the Connectors Operations team if you have any question.
ARG JDK_VERSION=17.0.8
FROM amazoncorretto:${JDK_VERSION}
COPY --from=airbyte/integration-base:dev /airbyte /airbyte

RUN yum update -y && yum install -y tar openssl && yum clean all

WORKDIR /airbyte

# Add the Datadog Java APM agent
ADD https://dtdg.co/latest-java-tracer dd-java-agent.jar

COPY javabase.sh .
COPY run_with_normalization.sh .

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD "/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD "/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD "/airbyte/javabase.sh --read"
ENV AIRBYTE_WRITE_CMD "/airbyte/javabase.sh --write"

ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"
ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/integration-base-java
