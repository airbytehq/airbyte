ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS server

EXPOSE 8000

RUN apt update && apt -y upgrade && apt install -y curl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

ENV APPLICATION airbyte-tests

WORKDIR /app

ADD bin/${APPLICATION}-0.35.4-alpha.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-0.35.4-alpha/bin/${APPLICATION}"]
