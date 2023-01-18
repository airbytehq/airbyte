ARG JDK_IMAGE=airbyte/airbyte-base-java-image:1.0
FROM ${JDK_IMAGE} AS connector-builder-server-micronaut

ARG VERSION=dev

ENV APPLICATION airbyte-connector-builder-server-micronaut
ENV VERSION ${VERSION}

WORKDIR /tmp
# Install python3.9
RUN yum -y groupinstall "Development Tools"
RUN yum -y install openssl-devel bzip2-devel libffi-devel
RUN yum -y install wget
RUN wget https://www.python.org/ftp/python/3.9.11/Python-3.9.11.tgz
RUN tar xvf Python-3.9.11.tgz
WORKDIR /tmp/Python-3.9.11
RUN pwd
RUN ls
RUN ./configure --enable-optimizations
RUN make altinstall

WORKDIR /app

# This is automatically unzipped by Docker
ADD bin/${APPLICATION}-${VERSION}.tar /app
ADD . /app

RUN pip3.9 install .

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

LABEL io.airbyte.version=0.40.28
LABEL io.airbyte.name=airbyte/connector-builder-server-micronaut
