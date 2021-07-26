FROM golang:1.14

ENV GO111MODULE=on
RUN go get -u github.com/danielgtaylor/restish@47de8a55eae6c0ab38e35119bef52ccf2837e3b3

ENTRYPOINT ["restish"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/cli
