# Config-based connectors overview

The goal of this document is to give enough technical specifics to understand how config-based connectors work.
When you're ready to start building a connector, you can start with [the tutorial](../../../config-based/tutorial/0-getting-started.md) or dive into the [reference documentation](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.html)

## Overview

Config-based connectors work by parsing a YAML configuration describing the Source, then running the configured connector using a Python backend.

The process then submits HTTP requests to the API endpoint, and extracts records out of the response.

## Source

Config-based connectors are a declarative way to define HTTP API sources.

A source is defined by 2 components:

1. The source's `Stream`s, which define the data to read
2. A `ConnectionChecker`, which describes how to run the `check` operation to test the connection to the API source

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a RDMS source.

A stream is defined by:

1. Its name
2. A primary key: used to uniquely identify records, enabling deduplication
3. A schema: describes the data to sync
4. A data retriever: describes how to retrieve the data from the API
5. A cursor field: used to identify the stream's state from a record
6. A set of transformations to be applied on the records read from the source before emitting them to the destination
7. A checkpoint interval: defines when to checkpoint syncs.

More details on streams and sources can be found in the [basic concepts section](../cdk-python/basic-concepts.md).
More details on cursor fields, and checkpointing can be found in the [incremental-stream section](../cdk-python/incremental-stream.md)

## Data retriever

The data retriever defines how to read the data from an API source, and acts as an orchestrator for the data retrieval flow.
There is currently only one implementation, the `SimpleRetriever`, which is defined by

1. Requester: describes how to submit requests to the API source
2. Paginator[^1]: describes how to navigate through the API's pages
3. Record selector: describes how to select records from an HTTP response
4. Stream Slicer: describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integrations they are building against.

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

The `Requester` defines how to prepare HTTP requests to send to the source API [^2].
There currently is only one implementation, the `HttpRequester`, which is defined by

1. A base url: the root of the API source
2. A path: the specific endpoint to fetch data from for a resource
3. The HTTP method: the HTTP method to use (GET or POST)
4. A request options provider: defines the request parameters and headers to set on outgoing HTTP requests
5. An authenticator: defines how to authenticate to the source
6. An error handler: defines how to handle errors

More details on authentication can be found in the [authentication section](authentication.md).
More details on error handling can be found in the [error handling section](error-handling.md)

## Connection Checker

The `ConnectionChecker` defines how to test the connection to the integration.

The only implementation as of now is `CheckStream`, which tries to read a record from a specified list of streams and fails if no records could be read.

[^1] The paginator is conceptually more related to the requester than the data retriever, but is part of the `SimpleRetriever` because it inherits from `HttpStream` to increase code reusability.
[^2] As of today, the requester acts as a config object and is not directly responsible for preparing the HTTP requests. This is done in the `SimpleRetriever`'s parent class `HttpStream`.