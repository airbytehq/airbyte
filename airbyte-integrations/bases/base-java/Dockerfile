ARG JDK_VERSION=17.0.4
ARG JDK_IMAGE=amazoncorretto:${JDK_VERSION}
FROM ${JDK_IMAGE}
RUN yum install -y tar && yum clean all
COPY --from=airbyte/integration-base:dev /airbyte /airbyte

WORKDIR /airbyte

COPY javabase.sh .

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD "/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD "/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD "/airbyte/javabase.sh --read"
ENV AIRBYTE_WRITE_CMD "/airbyte/javabase.sh --write"

ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"
ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/integration-base-java
