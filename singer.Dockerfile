FROM python:3.7.8-alpine3.11

ENV SINGER_ROOT /lib/singer
RUN mkdir -p $SINGER_ROOT

COPY . /code/
WORKDIR /code

# postgres taps need postgres binaries & build-base (gcc)
RUN pwd && apk update && apk add postgresql-dev=12.2-r0 build-base=0.5-r1 \
    && . tools/singer/install_connector.sh "tap-postgres" "tap-postgres" "0.1.0" \
    && . tools/singer/install_connector.sh "target-postgres" "singer-target-postgres" "0.2.4"

CMD ["/bin/bash"]

# intended to be built & run with the following:
# docker build -f singer.Dockerfile -t dataline/singer-libs .
# docker run -d --network=host dataline/singer-libs /
# TODO figure out how to run singer commands from local tests inside the singer container
