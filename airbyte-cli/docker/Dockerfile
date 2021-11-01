FROM golang:1.14

ENV GO111MODULE=on


# todo (cgardens) - replace this forked commit with an official version when a fix is released.
#RUN go get -u github.com/danielgtaylor/restish@v0.7.0
RUN go get -u github.com/cgardens/restish@e6f8ddda7fb5a3a989537272292c8321022cdb54

ENTRYPOINT ["restish"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/cli
