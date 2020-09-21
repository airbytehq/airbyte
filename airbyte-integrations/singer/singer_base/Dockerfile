FROM openjdk:14.0.2-slim AS singer_base
COPY --from=python:3.7-slim / /

ENV APPLICATION singer-base

WORKDIR /singer

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

ENTRYPOINT ["bin/${APPLICATION}"]
