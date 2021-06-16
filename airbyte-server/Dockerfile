FROM openjdk:14.0.2-slim AS server

EXPOSE 8000

ENV WAIT_VERSION=2.7.2
ENV APPLICATION airbyte-server

WORKDIR /
# data is mapped to a volume. Check CONFIG_ROOT in .env file and docker-compoes file
COPY build/resources/main/config data/config

WORKDIR /app

# Install wait
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/${WAIT_VERSION}/wait wait
RUN chmod +x wait

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN mkdir latest_seeds
COPY build/resources/main/config latest_seeds

RUN tar xf ${APPLICATION}.tar --strip-components=1

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "./wait && bin/${APPLICATION}"]
