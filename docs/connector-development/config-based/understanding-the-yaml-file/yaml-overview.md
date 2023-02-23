# Understanding the YAML file

The low-code framework involves editing a boilerplate [YAML file](../low-code-cdk-overview.md#configuring-the-yaml-file). This section deep dives into the components of the YAML file.

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

By default, the schema of a stream's data is defined as a [JSONSchema](https://json-schema.org/) file in `<source_connector_name>/schemas/<stream_name>.json`. 

Alternately, the stream's data schema can be stored in YAML format inline in the YAML file, by including the optional `schema_loader` key. If the data schema is provided inline, any schema on disk for that stream will be ignored.

More information on how to define a stream's schema can be found [here](../../../../airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml)

The stream object is represented in the YAML file as:

```yaml
  Stream:
    type: object
    additionalProperties: true
    required:
      - name
      - retriever
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      name:
        type: string
      primary_key:
        "$ref": "#/definitions/PrimaryKey"
      retriever:
        "$ref": "#/definitions/Retriever"
      stream_cursor_field:
        type: string
      transformations:
        "$ref": "#/definitions/RecordTransformation"
      checkpoint_interval:
        type: integer
      schema_loader:
        "$ref": "#/definitions/InlineSchemaLoader"
```

More details on streams and sources can be found in the [basic concepts section](../../cdk-python/basic-concepts.md).

### Data retriever

The data retriever defines how to read the data for a Stream and acts as an orchestrator for the data retrieval flow.

It is described by:

1. [Requester](./requester.md): Describes how to submit requests to the API source
2. [Paginator](./pagination.md): Describes how to navigate through the API's pages
3. [Record selector](./record-selector.md): Describes how to extract records from a HTTP response
4. [Stream slicer](./stream-slicers.md): Describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integration they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

The schema of a retriever object is:

```yaml
  Retriever:
    type: object
    anyOf:
      - "$ref": "#/definitions/SimpleRetriever"
  SimpleRetriever:
    type: object
    additionalProperties: true
    required:
      - name
      - requester
      - record_selector
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      name:
        type: string
      primary_key:
        "$ref": "#/definitions/PrimaryKey"
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

## Configuring the cursor field for incremental syncs

Incremental syncs are supported by using a `DatetimeStreamSlicer` to iterate over a datetime range.

Given a start time, an end time, and a step function, it will partition the interval [start, end] into small windows of the size described by the step.
Note that the `StreamSlicer`'s `cursor_field` must match the `Stream`'s `stream_cursor_field`.

More information on `DatetimeStreamSlicer` can be found in the [stream slicers](./stream-slicers.md#datetimestreamslicer) section.

## More readings

- [Requester](./requester.md)
- [Stream slicers](./stream-slicers.md)
