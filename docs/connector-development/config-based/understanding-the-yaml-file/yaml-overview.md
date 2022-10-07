# Understanding the YAML file

The low-code framework involves editing a boilerplate [YAML file](../low-code-cdk-overview.md#configuring-the-yaml-file). This section deep dives into the components of the YAML file.

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source. A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

A stream is defined by:

1. A name
2. Primary key (Optional): Used to uniquely identify records, enabling deduplication. Can be a string for single primary keys, a list of strings for composite primary keys, or a list of list of strings for composite primary keys consisting of nested fields
3. [Schema](../../cdk-python/schemas.md): Describes the data to sync
4. [Data retriever](#data-retriever): Describes how to retrieve the data from the API
5. [Cursor field](../../cdk-python/incremental-stream.md) (Optional): Field to use as stream cursor. Can either be a string, or a list of strings if the cursor is a nested field.
6. [Transformations](#transformations) (Optional): A set of transformations to be applied on the records read from the source before emitting them to the destination
7. [Checkpoint interval](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing) (Optional): Defines the interval, in number of records, at which incremental syncs should be checkpointed

### Data retriever

The data retriever defines how to read the data for a Stream, and acts as an orchestrator for the data retrieval flow.
There is currently only one implementation, the `SimpleRetriever`, which is defined by

1. [Requester](requester.md): Describes how to submit requests to the API source
2. [Paginator](pagination.md): Describes how to navigate through the API's pages
3. [Record selector](record-selector.md): Describes how to extract records from a HTTP response
4. [Stream Slicer](stream-slicers.md): Describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integration they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

### Transformations

Fields can be added or removed from records by adding `Transformation`s to a stream's definition.

#### Adding fields

Fields can be added with the `AddFields` transformation.
This example adds a top-level field "field1" with a value "static_value"

```yaml
stream:
  <...>
  transformations:
      - type: AddFields
        fields:
          - path: [ "field1" ]
            value: "static_value"
```

This example adds a top-level field "start_date", whose value is evaluated from the stream slice:

```yaml
stream:
  <...>
  transformations:
      - type: AddFields
        fields:
          - path: [ "start_date" ]
            value: {{ stream_slice[ 'start_date' ] }}
```

Fields can also be added in a nested object by writing the fields' path as a list.

Given a record of the following shape:

```
{
  "id": 0,
  "data":
  {
    "field0": "some_data"
  }
}
```

this definition will add a field in the "data" nested object:

```yaml
stream:
  <...>
  transformations:
      - type: AddFields
        fields:
          - path: [ "data", "field1" ]
            value: "static_value"
```

resulting in the following record:

```
{
  "id": 0,
  "data":
  {
    "field0": "some_data",
    "field1": "static_value"
  }
}
```

#### Removing fields

Fields can be removed from records with the `RemoveFields` transformation.

Given a record of the following shape:

```
{
  "path": 
  {
    "to":
    {
      "field1": "data_to_remove",
      "field2": "data_to_keep"
    }
  },
  "path2": "data_to_remove",
  "path3": "data_to_keep"
}
```

this definition will remove the 2 instances of "data_to_remove" which are found in "path2" and "path.to.field1":

```yaml
the_stream:
  <...>
  transformations:
      - type: RemoveFields
        field_pointers:
          - [ "path", "to", "field1" ]
          - [ "path2" ]
```

resulting in the following record:

```
{
  "path": 
  {
    "to":
    {
      "field2": "data_to_keep"
    }
  },
  "path3": "data_to_keep"
}
```