FROM openjdk:14.0.2-slim

# This env variable is used in install_connector.sh
ENV SINGER_ROOT /lib/singer
RUN mkdir -p $SINGER_ROOT

COPY . /code/
WORKDIR /code

# postgres taps need postgres binaries & build-base (gcc)
RUN apt-get update && apt-get --assume-yes install build-essential=12.6 \
                      libpq-dev=11.7-0+deb10u1 \
                      python3.7=3.7.3-2+deb10u2 \
                      python3-venv=3.7.3-1 \
                      python3-pip=18.1-5 \
    && pip3 install psycopg2-binary \


WORKDIR /code
COPY ./test_file.sh ./

CMD ["/bin/bash"]
