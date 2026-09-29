# Understanding the YAML file

The low-code framework involves editing a boilerplate [YAML file](../low-code-cdk-overview.md#configuring-the-yaml-file). This section deep dives into the components of the YAML file.

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

By default, the schema of a stream's data is defined as a [JSONSchema](https://json-schema.org/) file in `<source_connector_name>/schemas/<stream_name>.json`.

Alternately, the stream's data schema can be stored in YAML format inline in the YAML file, by including the optional `schema_loader` key. If the data schema is provided inline, any schema on disk for that stream will be ignored.

More information on how to define a stream's schema can be found [here](https://github.com/airbytehq/airbyte-python-cdk/blob/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml)

The stream object is represented in the YAML file as:

```yaml
DeclarativeStream:
  description: A stream whose behavior is described by a set of declarative low code components
  type: object
  additionalProperties: true
  required:
    - type
    - retriever
  properties:
    type:
      type: string
      enum: [DeclarativeStream]
    retriever:
      "$ref": "#/definitions/Retriever"
    schema_loader:
      definition: The schema loader used to retrieve the schema for the current stream
      anyOf:
        - "$ref": "#/definitions/InlineSchemaLoader"
        - "$ref": "#/definitions/JsonFileSchemaLoader"
    stream_cursor_field:
      definition: The field of the records being read that will be used during checkpointing
      anyOf:
        - type: string
        - type: array
          items:
            - type: string
    transformations:
      definition: A list of transformations to be applied to each output record in the
      type: array
      items:
        anyOf:
          - "$ref": "#/definitions/AddFields"
          - "$ref": "#/definitions/CustomTransformation"
          - "$ref": "#/definitions/RemoveFields"
    $parameters:
      type: object
      additional_properties: true
```

More details on streams and sources can be found in the [basic concepts section](../../cdk-python/basic-concepts.md).

### Configuring a stream for incremental syncs

If you want to allow your stream to be configured so that only data that has changed since the prior sync is replicated to a destination, you can specify a `DatetimeBasedCursor` on your `Streams`'s `incremental_sync` field.

Given a start time, an end time, and a step function, it will partition the interval [start, end] into small windows of the size described by the step.

More information on `incremental_sync` configurations and the `DatetimeBasedCursor` component can be found in the [incremental syncs](./incremental-syncs.md) section.

## Data retriever

The data retriever defines how to read the data for a Stream and acts as an orchestrator for the data retrieval flow.

It is described by:

1. [Requester](./requester.md): Describes how to submit requests to the API source
2. [Paginator](./pagination.md): Describes how to navigate through the API's pages
3. [Record selector](./record-selector.md): Describes how to extract records from a HTTP response
4. [Partition router](./partition-router.md): Describes how to retrieve data across multiple resource locations

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integration they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

The schema of a retriever object is:

```yaml
retriever:
  description: Retrieves records by synchronously sending requests to fetch records. The retriever acts as an orchestrator between the requester, the record selector, the paginator, and the partition router.
  type: object
  required:
    - requester
    - record_selector
    - requester
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    requester:
      "$ref": "#/definitions/Requester"
    record_selector:
      "$ref": "#/definitions/HttpSelector"
    paginator:
      "$ref": "#/definitions/Paginator"
    stream_slicer:
      "$ref": "#/definitions/StreamSlicer"
PrimaryKey:
  type: string
```

### Routing to Data that is Partitioned in Multiple Locations

Some sources might require specifying additional parameters that are needed to retrieve data. Using the `PartitionRouter` component, you can specify a static or dynamic set of elements which will be iterated upon and made available for use when a connector dispatches requests to get data from a source.

More information on how to configure the `partition_router` field on a Retriever to retrieve data from multiple location can be found in the [iteration](./partition-router.md) section.

### Combining Incremental Syncs and Iterable Locations

A stream can be configured to support incrementally syncing data that is spread across multiple partitions by defining `incremental_sync` on the `Stream` and `partition_router` on the `Retriever`.

During a sync where both are configured, the Cartesian product of these parameters will be calculated and the connector will repeat requests to the source using the different combinations of parameters to get all of the data.

For example, if we had a `DatetimeBasedCursor` requesting data over a 3-day range partitioned by day and a `ListPartitionRouter` with the following locations `A`, `B`, and `C`. This would result in the following combinations that will be used to request data.

| Partition | Date Range                                |
| --------- | ----------------------------------------- |
| A         | 2022-01-01T00:00:00 - 2022-01-01T23:59:59 |
| B         | 2022-01-01T00:00:00 - 2022-01-01T23:59:59 |
| C         | 2022-01-01T00:00:00 - 2022-01-01T23:59:59 |
| A         | 2022-01-02T00:00:00 - 2022-01-02T23:59:59 |
| B         | 2022-01-02T00:00:00 - 2022-01-02T23:59:59 |
| C         | 2022-01-02T00:00:00 - 2022-01-02T23:59:59 |
| A         | 2022-01-03T00:00:00 - 2022-01-03T23:59:59 |
| B         | 2022-01-03T00:00:00 - 2022-01-03T23:59:59 |
| C         | 2022-01-03T00:00:00 - 2022-01-03T23:59:59 |

## More readings

- [Requester](./requester.md)
- [Incremental Syncs](./incremental-syncs.md)
- [Partition Router](./partition-router.md)
