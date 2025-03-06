# Retrieving Records Spread Across Partitions

In some cases, the data you are replicating is spread across multiple partitions. You can specify a set of parameters to be iterated over and used while requesting all of your data. On each iteration, using the current element being iterated upon, the connector will perform a cycle of requesting data from your source.

`PartitionRouter`s gives you the ability to specify either a static or dynamic set of elements that will be iterated over one at a time. This in turn is used to route requests to a partition of your data according to the elements iterated over.

The most common use case for the `PartitionRouter` component is the retrieval of data from an API endpoint that requires extra request inputs to indicate which partition of data to fetch.

Schema:

```yaml
partition_router:
  default: []
  anyOf:
    - "$ref": "#/definitions/CustomPartitionRouter"
    - "$ref": "#/definitions/ListPartitionRouter"
    - "$ref": "#/definitions/SubstreamPartitionRouter"
    - type: array
      items:
        anyOf:
          - "$ref": "#/definitions/CustomPartitionRouter"
          - "$ref": "#/definitions/ListPartitionRouter"
          - "$ref": "#/definitions/SubstreamPartitionRouter"
```

Notice that you can specify one or more `PartitionRouter`s on a Retriever. When multiple are defined, the result will be Cartesian product of all partitions and a request cycle will be performed for each permutation.

## ListPartitionRouter

`ListPartitionRouter` iterates over values from a given list. It is defined by

- The partition values, which are the valid values for the cursor field
- The cursor field on a record
- request_option: optional request option to set on outgoing request parameters

Schema:

```yaml
ListPartitionRouter:
  description: Partition router that is used to retrieve records that have been partitioned according to a list of values
  type: object
  required:
    - type
    - cursor_field
    - slice_values
  properties:
    type:
      type: string
      enum: [ListPartitionRouter]
    cursor_field:
      type: string
    partition_values:
      anyOf:
        - type: string
        - type: array
          items:
            type: string
    request_option:
      "$ref": "#/definitions/RequestOption"
    $parameters:
      type: object
      additionalProperties: true
```

As an example, this partition router will iterate over the 2 repositories ("airbyte" and "airbyte-secret") and will set a request_parameter on outgoing HTTP requests.

```yaml
partition_router:
  type: ListPartitionRouter
  values:
    - "airbyte"
    - "airbyte-secret"
  cursor_field: "repository"
  request_option:
    type: RequestOption
    field_name: "repository"
    inject_into: "request_parameter"
```

## SubstreamPartitionRouter

Substreams are streams that depend on the records of another stream

We might for instance want to read all the commits for a given repository (parent stream).

Substreams are implemented by defining their partition router as a `SubstreamPartitionRouter`.

`SubstreamPartitionRouter` is used to route requests to fetch data that has been partitioned according to a parent stream's records . We might for instance want to read all the commits for a given repository (parent resource).

- what the parent stream is
- what is the key of the records in the parent stream
- what is the attribute on the parent record that is being used to partition the substream data
- how to specify that attribute on an outgoing HTTP request to retrieve that set of records

Schema:

```yaml
SubstreamPartitionRouter:
  description: Partition router that is used to retrieve records that have been partitioned according to records from the specified parent streams
  type: object
  required:
    - type
    - parent_stream_configs
  properties:
    type:
      type: string
      enum: [SubstreamPartitionRouter]
    parent_stream_configs:
      type: array
      items:
        "$ref": "#/definitions/ParentStreamConfig"
    $parameters:
      type: object
      additionalProperties: true
```

Example:

```yaml
partition_router:
  type: SubstreamPartitionRouter
  parent_stream_configs:
    - stream: "#/repositories_stream"
      parent_key: "id"
      partition_field: "repository"
      request_option:
        type: RequestOption
        field_name: "repository"
        inject_into: "request_parameter"
```

REST APIs often nest sub-resources in the URL path.
If the URL to fetch commits was "/repositories/:id/commits", then the `Requester`'s path would need to refer to the stream slice's value and no `request_option` would be set:

Example:

```yaml
retriever:
  <...>
  requester:
    <...>
    path: "/respositories/{{ stream_slice.repository }}/commits"
  partition_router:
    type: SubstreamPartitionRouter
    parent_streams_configs:
      - stream: "#/repositories_stream"
        parent_key: "id"
        partition_field: "repository"
        incremental_dependency: true
```

## Nested streams

Nested streams, subresources, or streams that depend on other streams can be implemented using a [`SubstreamPartitionRouter`](#SubstreamPartitionRouter)

## More readings

- [Incremental streams](../../cdk-python/incremental-stream.md)
- [Stream slices](../../cdk-python/stream-slices.md)

[^1] This is a slight oversimplification. See [update cursor section](#cursor-update) for more details on how the cursor is updated.
