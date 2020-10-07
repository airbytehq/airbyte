FROM openjdk:14.0.2-slim
COPY --from=airbyte/base:dev /airbyte /airbyte

WORKDIR /airbyte

COPY javabase.sh .

# airbyte base commands
ENV AIRBYTE_SPEC_CMD "./javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD "./javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD "./javabase.sh --discover"
ENV AIRBYTE_READ_CMD "./javabase.sh --read"
ENV AIRBYTE_READ_CMD "./javabase.sh --write"

ENTRYPOINT ["/airbyte/base.sh"]
