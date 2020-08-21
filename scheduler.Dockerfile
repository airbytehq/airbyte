FROM dataline/java-base:dev

EXPOSE 8000

WORKDIR /app/dataline-scheduler

# TODO: add data mount instead
RUN mkdir data

RUN cp /code/dataline-scheduler/build/distributions/*.tar dataline-scheduler.tar \
    && rm -rf /code
RUN tar xf dataline-scheduler.tar --strip-components=1

# add docker-compose-wait tool
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait wait
RUN chmod +x wait

# wait for postgres to become available before starting server
CMD ./wait && bin/dataline-scheduler
