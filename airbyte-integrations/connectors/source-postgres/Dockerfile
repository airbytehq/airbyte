FROM airbyte/integration-base-java:dev AS build
#RUN ls /
WORKDIR /airbyte
RUN python3 --version
ENV APPLICATION source-postgres

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar
RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY --from=build /airbyte /airbyte
#COPY --from=build /ndpi /ndpid
#RUN /nDPI/example/ndpiReader --help
#RUN ls /airbyte
LABEL io.airbyte.version=1.0.16
LABEL io.airbyte.name=airbyte/source-postgres
