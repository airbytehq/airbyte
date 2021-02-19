FROM golang:1.14

ENV GO111MODULE=on
RUN go get -u github.com/danielgtaylor/restish@4aa30c3f866cf4a551c64ea3d4c6eefea72cf2bc

ENTRYPOINT ["restish"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/cli
