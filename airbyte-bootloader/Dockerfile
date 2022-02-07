ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim

ENV APPLICATION airbyte-bootloader

WORKDIR /app

ADD bin/${APPLICATION}-0.35.19-alpha.tar /app

ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-0.35.19-alpha/bin/${APPLICATION}"]
