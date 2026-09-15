FROM amazoncorretto:21-al2023

RUN yum update -y --security && \
    yum install -y tar openssl findutils && \
    yum clean all

WORKDIR /airbyte

COPY base.sh /airbyte/base.sh
COPY javabase.sh /airbyte/javabase.sh
COPY destination-doris.tar destination-doris.tar

RUN tar xf destination-doris.tar --strip-components=1 && rm destination-doris.tar

ENV APPLICATION=destination-doris
ENV AIRBYTE_ENTRYPOINT="/airbyte/base.sh"
ENV AIRBYTE_SPEC_CMD="/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD="/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD="/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD="/airbyte/javabase.sh --read"
ENV AIRBYTE_WRITE_CMD="/airbyte/javabase.sh --write"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-doris

ENTRYPOINT ["/airbyte/base.sh"]
