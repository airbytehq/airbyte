FROM openjdk:14.0.2-slim

ENV APPLICATION airbyte-secrets-migration
WORKDIR /airbyte
COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar
RUN tar xf ${APPLICATION}.tar --strip-components=1

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/secrets-migration

CMD ["/airbyte/bin/airbyte-secrets-migration"]