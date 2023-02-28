FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

# upgrade pip and install libs
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base bash
COPY . ./
RUN pip install . --use-feature=in-tree-build
