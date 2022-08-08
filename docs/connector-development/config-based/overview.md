# Config-based connectors overview

The goal of this document is to give enough technical specifics to understand how config-based connectors work.
When you're ready to start building a connector, you can start with [the tutorial](../../../config-based/tutorial/0-getting-started.md) or dive into the [reference documentation](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.html)

## Overview

Config-based connectors work by parsing a YAML configuration describing the Source, then running the configured connector using a Python backend.

The process then submits HTTP requests to the API endpoint, and extracts records out of the response.

See the [connector definition section](connector-definition.md) for more information on the YAML file describing the connector.

## Source

Config-based connectors are a declarative way to define HTTP API sources.

A source is defined by 2 components:

1. The source's `Stream`s, which define the data to read
2. A `ConnectionChecker`, which describes how to run the `check` operation to test the connection to the API source

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

A stream is defined by:

1. A name
2. Primary key (Optional): Used to uniquely identify records, enabling deduplication. Can be a string for single primary keys, a list of strings for composite primary keys, or a list of list of strings for composite primary keys consisting of nested fields.
3. [Schema](../cdk-python/schemas.md): Describes the data to sync
4. [Data retriever](overview.md#data-retriever): Describes how to retrieve the data from the API
5. [Cursor field](../cdk-python/incremental-stream.md) (Optional): Field to use used as stream cursor. Can either be a string, or a list of strings if the cursor is a nested field.
6. [Transformations](./record-selector.md#transformations) (Optional): A set of transformations to be applied on the records read from the source before emitting them to the destination
7. [Checkpoint interval](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing) (Optional): Defines the interval at which incremental syncs should be checkpointed.

More details on streams and sources can be found in the [basic concepts section](../cdk-python/basic-concepts.md).

## Data retriever

The data retriever defines how to read the data for a Stream, and acts as an orchestrator for the data retrieval flow.
There is currently only one implementation, the `SimpleRetriever`, which is defined by

1. Requester: Describes how to submit requests to the API source
2. Paginator: Describes how to navigate through the API's pages
3. Record selector: Describes how to select records from an HTTP response
4. Stream Slicer: Describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integrations they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

### Data flow

The retriever acts as a coordinator, moving the data between its components before emitting `AirbyteMessage`s that can be read by the platform.
The `SimpleRetriever`'s data flow can be described as follows:

1. Given the connection config and the current stream state, the `StreamSlicer` computes the stream slices to read.
2. Iterate over all the stream slices defined by the stream slicer.
3. For each stream slice,
    1. Submit a request as defined by the requester
    2. Select the records from the response
    3. Repeat for as long as the paginator points to a next page

More details on the record selector can be found in the [record selector section](record-selector.md)
More details on the stream slicers can be found in the [stream slicers section](stream-slicers.md)
More details on the paginator can be found in the [pagination section](pagination.md)

## Requester

The `Requester` defines how to prepare HTTP requests to send to the source API.
There currently is only one implementation, the `HttpRequester`, which is defined by

1. A base url: The root of the API source
2. A path: The specific endpoint to fetch data from for a resource
3. The HTTP method: the HTTP method to use (GET or POST)
4. A request options provider: Defines the request parameters (query parameters), headers, and request body to set on outgoing HTTP requests
5. An authenticator: Defines how to authenticate to the source
6. An error handler: Defines how to handle errors

More details on authentication can be found in the [authentication section](authentication.md).
More details on error handling can be found in the [error handling section](error-handling.md)

## Connection Checker

The `ConnectionChecker` defines how to test the connection to the integration.

The only implementation as of now is `CheckStream`, which tries to read a record from a specified list of streams and fails if no records could be read.