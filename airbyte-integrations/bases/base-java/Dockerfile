ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim
COPY --from=airbyte/integration-base:dev /airbyte /airbyte

WORKDIR /airbyte

COPY javabase.sh .

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD "/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD "/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD "/airbyte/javabase.sh --read"
ENV AIRBYTE_WRITE_CMD "/airbyte/javabase.sh --write"

# Sentry DSN Key
ENV SENTRY_DSN "https://2a3a1622a2104b8f8d36db4915c956f8@o1114644.ingest.sentry.io/6145965"

ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"
ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base-java
