ARG JDK_VERSION=14.0.2
FROM openjdk:${JDK_VERSION}-slim

ENV APPLICATION airbyte-bootloader

WORKDIR /app

ADD bin/${APPLICATION}-0.33.12-alpha.tar /app

ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-0.33.12-alpha/bin/${APPLICATION}"]
