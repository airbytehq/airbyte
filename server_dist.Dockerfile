# Build final image
FROM dataline/server/base:latest

EXPOSE 8000

WORKDIR /app/dataline-server

# TODO: add data mount instead
RUN mkdir data

RUN cp /code/dataline-server/build/distributions/*.tar dataline-server.tar \
    && rm -rf /code
RUN tar xf dataline-server.tar --strip-components=1

# add docker-compose-wait tool
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait wait
RUN chmod +x wait

CMD bin/dataline-server
