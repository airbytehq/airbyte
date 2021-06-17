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
    && apt-get clean

