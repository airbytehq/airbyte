ARG JDK_IMAGE=airbyte/airbyte-base-java-image:1.0
FROM ${JDK_IMAGE}

ARG VERSION=0.40.32

ENV APPLICATION airbyte-bootloader
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app


ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]
