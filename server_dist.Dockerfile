# Build final image
FROM dataline/server/base:latest

EXPOSE 8000

WORKDIR /app/dataline-server

# TODO: add data mount instead
RUN mkdir data

RUN cp /code/dataline-server/build/distributions/*.tar dataline-server.tar \
    && rm -rf /code
RUN tar xf dataline-server.tar --strip-components=1

CMD bin/dataline-server
