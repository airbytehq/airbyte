# Understanding the YAML file

The low-code framework involves editing a boilerplate [YAML file](../low-code-cdk-overview.md#configuring-the-yaml-file). This section deep dives into the components of the YAML file.

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

A stream's schema will can defined as a [JSONSchema](https://json-schema.org/) file in `<source_connector_name>/schemas/<stream_name>.json`.
More information on how to define a stream's schema can be found [here](../cdk-python/schemas.md)

The schema of a stream object is:

```yaml
Stream:
  type: object
  additionalProperties: false
  required:
    - name
    - schema_loader
    - retriever
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    name:
      type: string
    primary_key:
      "$ref": "#/definitions/PrimaryKey"
    schema_loader:
      "$ref": "#/definitions/SchemaLoader"
    retriever:
      "$ref": "#/definitions/Retriever"
    stream_cursor_field:
      type: object
      oneOf:
        - type: string
        - type: array
          items:
            type: string
    transformations:
      type: array
      items:
        "$ref": "#/definitions/RecordTransformation"
    checkpoint_interval:
      type: integer
```

More details on streams and sources can be found in the [basic concepts section](../cdk-python/basic-concepts.md).

### Data retriever

The data retriever defines how to read the data for a Stream and acts as an orchestrator for the data retrieval flow.

It is described by:

1. [Requester](#configuring-the-requester): Describes how to submit requests to the API source
2. [Paginator](#configuring-the-paginator): Describes how to navigate through the API's pages
3. [Record selector](#configuring-the-paginator): Describes how to extract records from a HTTP response
4. [Stream Slicer](./advanced-topics.md#stream-slicers): Describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integration they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

The schema of a retriever object is:

```yaml
Retriever:
  type:
  oneOf:
    - "$ref": "#/definitions/SimpleRetriever"
SimpleRetriever:
  type: object
  additionalProperties: false
  required:
    - name
    - primary_key
    - requester
    - record_selector
    - stream_slicer
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
  type: object
  oneOf:
    - string
    - type: array
      items:
        type: string
    - type: array
      items:
        type: array
        items:
          type: string
```

## More readings