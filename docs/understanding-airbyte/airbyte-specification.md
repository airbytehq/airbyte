# Airbyte Specification

## Key Takeaways

* The specification is Docker-based; this allows a developer to write a connector in any language they want. All they have to do is put that code in a Docker container that adheres to the interface and protocol described below.
  * We currently provide templates to make this even easier for those who prefer to work in python or java. These templates allow the developer to skip any Docker setup so that they can just implement code against well-defined interfaces in their language of choice.
* The specification is designed to work as a CLI. The Airbyte app is built on top of this CLI.
* The specification defines a standard interface for implementing data integrations: Sources and Destinations.
* The specification provides a structured stdout / stdin message passing standard for data transport.
* While this specification works with Airbyte, it is an independent standard.

#### Contents:

1. [General information about the specification](airbyte-specification.md#general)
2. [Connector primitives](airbyte-specification.md#primitives)
3. [Details of the protocol to pass information between connectors](airbyte-specification.md#the-airbyte-protocol)

This document is focused on the interfaces and primitives around connectors. You can better understand how that fits into the bigger picture by checking out the [High-level View](high-level-view.md).

## General

* All structs described in this article are defined using JsonSchema.
* Airbyte uses JSON representations of these structs for all inter-process communication.

### Definitions

* **Airbyte Worker** - This is a core piece of the Airbyte stack that is responsible for 1\) initializing a Source and a Destinations and 2\) passing data from Source to Destination.
  * Someone implementing a connector need not ever touch this code, but in this article we mention it to contextualize how data is flowing through Airbyte.
* **Connector** - A connector is code that allows Airbyte to interact with a specific underlying data source \(e.g. Postgres\). In Airbyte, an integration is either a Source or a Destination.
* **Source** - A connector that _pulls_ data from an underlying data source. \(e.g. A Postgres Source reads data from a Postgres database. A Stripe Source reads data from the Stripe API\)
* **Destination** - A connector that _pushes_ data to an underlying data source. \(e.g. A Postgres Destination writes data to a Postgres database\)
* **AirbyteSpecification** - the specification that describes how to implement connectors using a standard interface.
* **AirbyteProtocol** - the protocol used for inter-process communication.
* **Integration Commands** - the commands that an integration container implements \(e.g. `spec`, `check`, `discover`, `read`/`write`\). We describe these commands in more detail below.
* **Sync** - the act of moving data from a Source to a Destination.

## Primitives

### Source

A source is implemented as a Docker container. The container must adhere to the interface described below.

**How the container will be called:**

The first argument passed to the image must be the command \(e.g. `spec`, `check`, `discover`, `read`\). Additional arguments can be passed after the command. Note: The system running the container will handle mounting the appropriate paths so that the config files are available to the container. This code snippet does not include that logic.

```text
docker run --rm -i <source-image-name> spec
docker run --rm -i <source-image-name> check --config <config-file-path>
docker run --rm -i <source-image-name> discover --config <config-file-path>
docker run --rm -i <source-image-name> read --config <config-file-path> --catalog <catalog-file-path> [--state <state-file-path>] > message_stream.json
```

The `read` command will emit a stream records to stdout.

**Interface Pseudocode:**

```text
spec() -> ConnectorSpecification
check(Config) -> AirbyteConnectionStatus
discover(Config) -> AirbyteCatalog
read(Config, ConfiguredAirbyteCatalog, State) -> Stream<AirbyteMessage>
```

#### Spec

* Input:
  1. none.
* Output:
  1. `spec` - a [ConnectorSpecification](https://github.com/airbytehq/airbyte/blob/922bfd08a9182443599b78dbb273d70cb9f63d30/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L256-L306) wrapped in an `AirbyteMessage` of type `spec`.
* The objective of the spec command is to pull information about how to use a source. The `ConnectorSpecification` contains this information.
* The `connectionSpecification` of the `ConnectorSpecification` must be valid JsonSchema. It describes what inputs are needed in order for the source to interact with the underlying data source.
  * e.g. If using a Postgres source, the `ConnectorSpecification` would specify that a `hostname`, `port`, and `password` are required in order for the connector to function.
  * The UI reads the JsonSchema in this field in order to render the input fields for a user to fill in.
  * This JsonSchema is also used to validate that the provided inputs are valid. e.g. If `port` is one of the fields and the JsonSchema in the `connectorSpecification` specifies that this field should be a number, if a user inputs "airbyte", they will receive an error. Airbyte adheres to JsonSchema validation rules.

#### Check

* Input:
  1. `config` - A configuration JSON object that has been validated using the `ConnectorSpecification`.
* Output:
  1. `connectionStatus` - an [AirbyteConnectionStatus](https://github.com/airbytehq/airbyte/blob/922bfd08a9182443599b78dbb273d70cb9f63d30/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L99-L112) wrapped in an `AirbyteMessage` of type `connection_status`.
* The `check` command attempts to connect to the underlying data source in order to verify that the provided credentials are usable.
  * e.g. If given the credentials, it can connect to the Postgres database, it will return a success response. If it fails \(perhaps the password is incorrect\), it will return a failed response and \(when possible\) a helpful error message.

#### Discover

* Input:
  1. `config` - A configuration JSON object that has been validated using the `ConnectorSpecification`.
* Output:
  1. `catalog` - an [AirbyteCatalog](https://github.com/airbytehq/airbyte/blob/922bfd08a9182443599b78dbb273d70cb9f63d30/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L113-L123) wrapped in an `AirbyteMessage` of type `catalog`.
* This command detects the _structure_ of the data in the data source.
* An `AirbyteCatalog` describes the structure of data in a data source. It has a single field called `streams` that contains a list of `AirbyteStream`s. Each of these contain a `name` and `json_schema` field. The `json_schema` field accepts any valid JsonSchema and describes the structure of a stream. This data model is intentionally flexible. That can make it a little hard at first to mentally map onto your own data, so we provide some examples below:
  * If we are using a data source that is a traditional relational database, each table in that database would map to an `AirbyteStream`. Each column in the table would be a key in the `properties` field of the `json_schema` field.
    * e.g. If we have a table called `users` which had the columns `name` and `age` \(the age column is optional\) the `AirbyteCatalog` would look like this:

      ```text
        {
          "streams": [
            {
              "name": "users",
              "schema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "age": {
                    "type": "number"
                  }
                }
              }
            }
          ]
        }
      ```
  * If we are using a data source that wraps an API with multiple different resources \(e.g. `api/customers` and `api/products`\) each route would correspond to a stream. The JSON object returned by each route would be described in the `json_schema` field.
    * e.g. In the case where the API has two endpoints `api/customers` and `api/products` and each returns a list of JSON objects, the `AirbyteCatalog` might look like this. \(Note: using the JSON schema standard for defining a stream allows us to describe nested objects. We are not constrained to a classic "table/columns" structure\)

      ```text
        {
          "streams": [
            {
              "name": "customers",
              "schema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                  "name": {
                    "type": "string"
                  }
                }
              }
            },
            {
              "name": "products",
              "schema": {
                "type": "object",
                "required": ["name", "features"],
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "features": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "required": ["name", "productId"],
                      "properties": {
                        "name": { "type": "string" },
                        "productId": { "type": "number" }
                      }
                    }
                  }
                }
              }
            }
          ]
        }
      ```

**Note:** Stream and field names can be any UTF8 string. Destinations are responsible for cleaning these names to make them valid table and column names in their respective data stores.

#### Read

* Input:
  1. `config` - A configuration JSON object that has been validated using the `ConnectorSpecification`.
  2. `catalog` - A `ConfiguredAirbyteCatalog`. This `catalog` should be constructed from the `catalog` returned by the `discover` command. To convert an `AirbyteStream` to a `ConfiguredAirbyteStream` copy the `AirbyteStream` into the stream field of the `ConfiguredAirbyteStream`. Any additional configurations can be specified in the `ConfiguredAirbyteStream`. More details on how this is configured in the [catalog documentation](catalog.md). This catalog will be used in the `read` command to both select what data is transferred and how it is replicated.
  3. `state` - A JSON object. This object is only ever written or read by the source, so it is a JSON blob with whatever information is necessary to keep track of how much of the data source has already been read. This is important whenever we need to replicate data with Incremental sync modes such as [Incremental Append](connections/incremental-append.md) or [Incremental Deduped History](connections/incremental-deduped-history.md). Note that this is not currently based on the state of data existing on the destination side.
* Output:
  1. `message stream` - A stream of `AirbyteRecordMessage`s and `AirbyteStateMessage`s piped to stdout.
* This command reads data from the underlying data source and converts it into `AirbyteRecordMessage`.
* Outputting `AirbyteStateMessages` is optional. It can be used to track how much of the data source has been synced.
* The connector ideally will only pull the data described in the `catalog` argument. It is permissible for the connector, however, to ignore the `catalog` and pull data from any stream it can find. If it follows this second behavior, the extra data will be pruned in the worker. We prefer the former behavior because it reduces the amount of data that is transferred and allows control over not sending sensitive data. There are some sources for which this is simply not possible.

### Destination

A destination is implemented as a Docker container. The container must adhere to the following interface.

**How the container will be called:**

The first argument passed to the image must be the command \(e.g. `spec`, `check`, `write`\). Additional arguments can be passed after the command. Note: The system running the container will handle mounting the appropriate paths so that the config files are available to the container. This code snippet does not include that logic.

```text
docker run --rm -i <destination-image-name> spec
docker run --rm -i <destination-image-name> check --config <config-file-path>
cat <&0 | docker run --rm -i <destination-image-name> write --config <config-file-path> --catalog <catalog-file-path>
```

The `write` command will consume `AirbyteMessage`s from stdin.

**Interface Pseudocode:**

```text
spec() -> ConnectorSpecification
check(Config) -> AirbyteConnectionStatus
write(Config, AirbyteCatalog, Stream<AirbyteMessage>(stdin)) -> void
```

For the sake of brevity, we will not re-describe `spec` and `check`. They are exactly the same as those commands described for the Source.

#### Write

* Input:
  1. `config` - A configuration JSON object that has been validated using the `ConnectorSpecification`.
  2. `catalog` - An `AirbyteCatalog`. This `catalog` should be a subset of the `catalog` returned by the `discover` command. Any `AirbyteRecordMessages`s that the destination receives that do _not_ match the structure described in the `catalog` will fail.
  3. `message stream` - \(this stream is consumed on stdin--it is not passed as an arg\). It will receive a stream of JSON-serialized `AirbyteMesssage`.
* Output:
  1. `AirbyteMessage`s of type `AirbyteStateMessage`. The destination connector should only output state messages if they were previously received as input on stdin. Outputting a state message indicates that all records which came before it have been successfully written to the destination.
* The destination should read in the `AirbyteMessages` and write any that are of type `AirbyteRecordMessage` to the underlying data store.
* The destination should fail if any of the messages it receives do not match the structure described in the `catalog`.

## The Airbyte Protocol

* All messages passed to and from connectors must be wrapped in an `AirbyteMessage` envelope and serialized as JSON. The JsonSchema specification for these messages can be found [here](https://github.com/airbytehq/airbyte/blob/922bfd08a9182443599b78dbb273d70cb9f63d30/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L13-L45).
* Even if a record is wrapped in an `AirbyteMessage` it will only be processed if it appropriate for the given command. e.g. If a source `read` action includes AirbyteMessages in its stream of type Catalog for instance, these messages will be ignored as the `read` interface only expects `AirbyteRecordMessage`s and `AirbyteStateMessage`s. The appropriate `AirbyteMessage` types have been described in each command above.
* **ALL** actions are allowed to return `AirbyteLogMessage`s on stdout. For brevity, we have not mentioned these log messages in the description of each action, but they are always allowed. An `AirbyteLogMessage` wraps any useful logging that the connector wants to provide. These logs will be written to Airbyte's log files and output to the console.
* I/O:
  * Connectors receive arguments on the command line via JSON files. `e.g. --catalog catalog.json`
  * They read `AirbyteMessage`s from stdin. The destination `write` action is the only command that consumes `AirbyteMessage`s.
  * They emit `AirbyteMessage`s on stdout. All commands that output messages use this approach \(even `write` emits `AirbyteLogMessage`s\). e.g. `discover` outputs the `catalog` wrapped in an AirbyteMessage on stdout.
* Messages not wrapped in the `AirbyteMessage` will be ignored.
* Each message must be on its own line. Multiple messages _cannot_ be sent on the same line.
* Each message must but serialize to a JSON object that is exactly 1 line. The JSON objects cannot be serialized across multiple lines.

## Acknowledgements

We'd like to note that we were initially inspired by Singer.io's [specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification) and would like to acknowledge that some of their design choices helped us bootstrap our project. We've since made a lot of modernizations to our protocol and specification, but don't want to forget the tools that helped us get started.

