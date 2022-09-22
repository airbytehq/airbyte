FROM amazonlinux:2022.0.20220831.1

WORKDIR /airbyte

COPY base.sh .

ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"
ENTRYPOINT ["/airbyte/base.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base
