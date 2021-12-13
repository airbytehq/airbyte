FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV JAVA_TOOL_OPTIONS -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
ENV APPLICATION destination-bigquery

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.5.0
LABEL io.airbyte.name=airbyte/destination-bigquery
