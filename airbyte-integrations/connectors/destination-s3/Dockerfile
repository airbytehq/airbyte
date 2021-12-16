FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-s3
#ENV JAVA_TOOL_OPTIONS -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.1.16
LABEL io.airbyte.name=airbyte/destination-s3
