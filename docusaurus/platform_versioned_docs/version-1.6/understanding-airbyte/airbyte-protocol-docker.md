# Airbyte Protocol Docker Interface

## Summary

The [Airbyte Protocol](airbyte-protocol.md) describes a series of structs and interfaces for building data pipelines. The Protocol article describes those interfaces in language agnostic pseudocode, this article transcribes those into docker commands. Airbyte's implementation of the protocol is all done in docker. Thus, this reference is helpful for getting a more concrete look at how the Protocol is used. It can also be used as a reference for interacting with Airbyte's implementation of the Protocol.

## Source

### Pseudocode:

```
spec() -> ConnectorSpecification
check(Config) -> AirbyteConnectionStatus
discover(Config) -> AirbyteCatalog
read(Config, ConfiguredAirbyteCatalog, State) -> Stream<AirbyteRecordMessage | AirbyteStateMessage>
```

### Docker:

```shell
docker run --rm -i <source-image-name> spec
docker run --rm -i <source-image-name> check --config <config-file-path>
docker run --rm -i <source-image-name> discover --config <config-file-path>
docker run --rm -i <source-image-name> read --config <config-file-path> --catalog <catalog-file-path> [--state <state-file-path>] > message_stream.json
```

The `read` command will emit a stream records to STDOUT.

## Destination

### Pseudocode:

```
spec() -> ConnectorSpecification
check(Config) -> AirbyteConnectionStatus
write(Config, AirbyteCatalog, Stream<AirbyteMessage>(stdin)) -> Stream<AirbyteStateMessage>
```

### Docker:

```shell
docker run --rm -i <destination-image-name> spec
docker run --rm -i <destination-image-name> check --config <config-file-path>
cat <&0 | docker run --rm -i <destination-image-name> write --config <config-file-path> --catalog <catalog-file-path>
```

The `write` command will consume `AirbyteMessage`s from STDIN.

## I/O:

- Connectors receive arguments on the command line via JSON files. `e.g. --catalog catalog.json`
- They read `AirbyteMessage`s from STDIN. The destination `write` action is the only command that consumes `AirbyteMessage`s.
- They emit `AirbyteMessage`s on STDOUT.

## Additional Docker Image Requirements

### Environment variable: `AIRBYTE_ENTRYPOINT` 

The Docker image must contain an environment variable called `AIRBYTE_ENTRYPOINT`. This must be the same as the `ENTRYPOINT` of the image.

## Non-Root User: `airbyte`

The Docker image should run under a user named `airbyte`.

## Specified `/airbyte` directory

The Docker image must have a directory called `/airbyte`, which the user `airbyte` owns and can write to.

This is the directory to which temporary files will be mounted, including the `config.json` and `catalog.json` files.

## Only write file artifacts to directories permitted by the base image

The connector code must only write only to directories permitted within the connector's base image.

For a list of permitted write directories, please consult the base image definitions in the [`airbytehq/airbyte` repo](https://github.com/airbytehq/airbyte), under the [`docker-images` directory](https://github.com/airbytehq/airbyte/tree/master/docker-images).

## Must be an `amd64` or multi-arch image

To run on Airbyte Platform, the image bust be valid for `amd64`. Since most developers contribute from (ARM-based) Mac M-series laptops, we recommend creating a multi-arch image that covers both `arm64/amd64` so that the same image tags work on both ARM and AMD runtimes.
