ARG JDK_VERSION=17.0.4
FROM amazoncorretto:${JDK_VERSION}
COPY --from=airbyte/integration-base:dev /airbyte /airbyte
#RUN amazon-linux-extras install epel
RUN yum install -y tar openssl python3 net-tools && yum clean all
RUN yum install -y git gcc autoconf automake libtool gettext flex bison pkgconfig libpcap libpcap-devel
RUN git clone https://github.com/ntop/nDPI.git
#RUN cd nDPI
WORKDIR /nDPI
RUN ./autogen.sh
RUN make
RUN ls example
#RUN example/ndpiReader --help
WORKDIR /airbyte
COPY mon.py /
COPY javabase.sh .
#COPY ./libndpi4-4.0-1.6.aarch64.rpm .
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
