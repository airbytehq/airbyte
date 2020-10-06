FROM openjdk:14.0.2-slim
COPY --from=airbyte/base:dev /airbyte /airbyte

WORKDIR /airbyte
ENV APPLICATION base-java

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "./bin/base-java --spec"
ENV AIRBYTE_CHECK_CMD "./bin/base-java --check"
ENV AIRBYTE_DISCOVER_CMD "./bin/base-java --discover"
ENV AIRBYTE_READ_CMD "./bin/base-java --write"

ENTRYPOINT ["/airbyte/base.sh"]
