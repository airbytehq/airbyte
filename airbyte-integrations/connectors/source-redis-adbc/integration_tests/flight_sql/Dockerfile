# Compatible reference server only; this is not a production Redis gateway.
FROM golang:1.26.10-bookworm@sha256:23ce71337b726608afb1bc00986e630a05034a87a87ea1fc2cd1ae5cf33387eb
RUN go install github.com/apache/arrow-go/v18/arrow/flight/flightsql/example/cmd/sqlite_flightsql_server@v18.8.0
ENTRYPOINT ["/go/bin/sqlite_flightsql_server", "-host", "0.0.0.0", "-port", "31337"]
