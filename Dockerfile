FROM ubuntu:20.04
 
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
        curl \
        zip \
        git \
        docker \
        python3 \
        default-jre \
        nodejs \
        postgresql \
        jq \
        cmake \
    && apt-get clean

RUN git clone https://github.com/airbytehq/airbyte.git

RUN cd airbyte