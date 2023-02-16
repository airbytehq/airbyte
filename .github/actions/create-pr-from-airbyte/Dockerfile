FROM golang:alpine

RUN apk add --update \
    bash \
    git 

ARG version=2d2d046925862b8afa639ce98b5cff0bd57aa1db
RUN go install github.com/lolabyte/gitxmod/cmd/gitxmod@${version}

COPY entrypoint /entrypoint

ENTRYPOINT [ "/entrypoint"]
