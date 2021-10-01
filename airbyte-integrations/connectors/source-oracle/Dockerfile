FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-oracle
ENV TZ UTC

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar
#ENV JAVA_TOOL_OPTIONS -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005
RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.3.5
LABEL io.airbyte.name=airbyte/source-oracle
