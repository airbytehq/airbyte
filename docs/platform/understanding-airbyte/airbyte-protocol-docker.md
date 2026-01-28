# Airbyte Protocol Docker Interface

## Summary

The [Airbyte Protocol](airbyte-protocol.md) describes a series of structs and interfaces for building data pipelines. That article describes those interfaces in language agnostic pseudocode. This article transcribes them into docker commands. Airbyte's implementation of the protocol is all done in docker. Thus, this reference is helpful for getting a more concrete look at how the Protocol is used. You can also use this article as a reference for interacting with Airbyte's implementation of the Protocol.

The examples in this document show the legacy STDIO-based interface. In Airbyte's high-performance socket mode, records flow over Unix domain sockets instead of STDIO. For details on data channel modes, see [Data channel modes](#data-channel-modes) and the [Airbyte Protocol](airbyte-protocol.md#data-channel-modes) documentation.

## Source

### Pseudocode

```text
spec() -> ConnectorSpecification
check(Config) -> AirbyteConnectionStatus
discover(Config) -> AirbyteCatalog
read(Config, ConfiguredAirbyteCatalog, State) -> Stream<AirbyteRecordMessage | AirbyteStateMessage>
```

### Docker

```shell
docker run --rm -i <source-image-name> spec
docker run --rm -i <source-image-name> check --config <config-file-path>
docker run --rm -i <source-image-name> discover --config <config-file-path>
docker run --rm -i <source-image-name> read --config <config-file-path> --catalog <catalog-file-path> [--state <state-file-path>] > message_stream.json
```

In STDIO mode, the `read` command emits a stream of records to STDOUT. In socket mode, records flow over Unix domain sockets while control messages use STDOUT.

## Destination

### Pseudocode

```text
spec() -> ConnectorSpecification
check(Config) -> AirbyteConnectionStatus
write(Config, AirbyteCatalog, Stream<AirbyteMessage>(stdin)) -> Stream<AirbyteStateMessage>
```

### Docker

```shell
docker run --rm -i <destination-image-name> spec
docker run --rm -i <destination-image-name> check --config <config-file-path>
cat <&0 | docker run --rm -i <destination-image-name> write --config <config-file-path> --catalog <catalog-file-path>
```

In STDIO mode, the `write` command consumes `AirbyteMessage`s from STDIN. In socket mode, the destination receives records over Unix domain sockets while control messages still use STDIN/STDOUT.

## Input and output

Connectors receive arguments on the command line via JSON files, for example `--catalog catalog.json`.

In STDIO mode, sources emit `AirbyteMessage`s on STDOUT and destinations consume them from STDIN. In socket mode, records and state messages flow over Unix domain sockets while control messages (logs, traces) still use STDIO.

## Data channel modes

Airbyte supports two data channel modes that determine how data flows between connectors during a sync.

### STDIO mode (legacy)

In this mode, all messages flow through standard input/output pipes with JSON serialization. The Docker examples in this document demonstrate STDIO mode operation.

Environment configuration:

- `DATA_CHANNEL_MEDIUM=STDIO` (default)
- `DATA_CHANNEL_FORMAT=JSONL` (default)

### Socket mode (fast)

Socket mode enables direct source-to-destination communication via Unix domain sockets, achieving 4-10x performance improvements through parallel data transfer and Protocol Buffers serialization. In this mode, records flow directly between source and destination over multiple sockets, while control messages (logs, traces) still use STDIO.

Environment configuration:

- `DATA_CHANNEL_MEDIUM=SOCKET`
- `DATA_CHANNEL_FORMAT=PROTOBUF`
- `DATA_CHANNEL_SOCKET_PATHS`: Comma-separated list of socket file paths

The Airbyte platform automatically selects the appropriate mode based on connector capabilities. For more details on data channel modes and architecture, see the [Airbyte Protocol](airbyte-protocol.md#data-channel-modes) and [Workloads & jobs](jobs.md#replication-architecture-modes) documentation.

## Additional Docker image requirements

### Environment variable: `AIRBYTE_ENTRYPOINT`

The Docker image must contain an environment variable called `AIRBYTE_ENTRYPOINT`. This must be the same as the `ENTRYPOINT` of the image.

**Important**: the `AIRBYTE_ENTRYPOINT` environment variable must use absolute paths to ensure proper execution. Note that the Airbyte platform may change the working directory at runtime. For instance, it can change to `/source` for sources and `/dest` for destinations. Using relative paths in the entrypoint can cause execution failures when the working directory is overridden.

**Example**:

- ✅ Correct: `ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"`
- ❌ Incorrect: `ENV AIRBYTE_ENTRYPOINT="./main.py"`

## Non-root user: `airbyte`

The Docker image should run under a user named `airbyte`.

## Specified `/airbyte` directory

The Docker image must have a directory called `/airbyte`, which the user `airbyte` owns and can write to.

This is the directory to which temporary files are mounted, including the `config.json` and `catalog.json` files.

## Only write file artifacts to directories permitted by the base image

The connector code must only write to directories permitted within the connector's base image.

For a list of permitted write directories, please consult the base image definitions in the [`airbytehq/airbyte` repo](https://github.com/airbytehq/airbyte), under the [`docker-images` directory](https://github.com/airbytehq/airbyte/tree/master/docker-images).

## Must be an `amd64` or multi-arch image

To run on Airbyte Platform, the image bust be valid for `amd64`. Since most developers contribute from ARM-based, Mac M-series laptops, consider creating a multi-arch image that covers both `arm64/amd64` so that the same image tags work on both ARM and AMD runtimes.
