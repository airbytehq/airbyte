FROM rust:1.70-bookworm AS builder

COPY . /code
WORKDIR /code
RUN cargo build --release

FROM debian:12

COPY --from=builder /code/target/release/field33-airbyte-connector /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/field33-airbyte-connector"]

LABEL io.airbyte.version=0.0.1
LABEL io.airbyte.name=airbyte/destination-field33
