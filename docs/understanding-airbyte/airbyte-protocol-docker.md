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
* Connectors receive arguments on the command line via JSON files. `e.g. --catalog catalog.json`
* They read `AirbyteMessage`s from STDIN. The destination `write` action is the only command that consumes `AirbyteMessage`s.
* They emit `AirbyteMessage`s on STDOUT.
