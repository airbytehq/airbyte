FROM golang:1.14

ENV GO111MODULE=on
RUN go get -u github.com/danielgtaylor/restish@v0.7.0

ENTRYPOINT ["restish"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/cli
