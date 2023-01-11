# Stream Slicers

`StreamSlicer`s define how to partition a stream into a subset of records.

It can be thought of as an iterator over the stream's data, where a `StreamSlice` is the retriever's unit of work.

When a stream is read incrementally, a state message will be output by the connector after reading every slice, which allows for [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).

At the beginning of a `read` operation, the `StreamSlicer` will compute the slices to sync given the connection config and the stream's current state,
As the `Retriever` reads data from the `Source`, the `StreamSlicer` keeps track of the `Stream`'s state, which will be emitted after reading each stream slice.

More information about stream slicing can be found in the [stream-slices section](../../cdk-python/stream-slices.md).

Schema:

```yaml
  StreamSlicer:
    type: object
    anyOf:
      - "$ref": "#/definitions/DatetimeStreamSlicer"
      - "$ref": "#/definitions/ListStreamSlicer"
      - "$ref": "#/definitions/CartesianProductStreamSlicer"
      - "$ref": "#/definitions/SubstreamSlicer"
      - "$ref": "#/definitions/SingleSlice"
```

### Single slice

The single slice only produces one slice for the whole stream.

Schema:

```yaml
  SingleSlice:
    type: object
    additionalProperties: true
```

### DatetimeStreamSlicer

The `DatetimeStreamSlicer` iterates over a datetime range by partitioning it into time windows.
This is done by slicing the stream on the records' cursor value, defined by the Stream's `cursor_field`.

Given a start time, an end time, and a step function, it will partition the interval [start, end] into small windows of the size described by the step.
For instance,

Schema:

```yaml
  DatetimeStreamSlicer:
    type: object
    required:
      - start_datetime
      - end_datetime
      - step
      - cursor_field
      - datetime_format
      - cursor_granularity
    additional_properties: false
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      start_datetime:
        "$ref": "#/definitions/MinMaxDatetime"
      end_datetime:
        "$ref": "#/definitions/MinMaxDatetime"
      step:
        type: string
      cursor_field:
        type: string
      datetime_format:
        type: string
      cursor_granularity:
        type: string
      start_time_option:
        "$ref": "#/definitions/RequestOption"
      end_time_option:
        "$ref": "#/definitions/RequestOption"
      stream_state_field_start:
        type: string
      stream_state_field_end:
        type: string
      lookback_window:
        type: string
  MinMaxDatetime:
    type: object
    required:
      - datetime
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      datetime:
        type: string
      datetime_format:
        type: string
      min_datetime:
        type: string
      max_datetime:
        type: string
```

Example:

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z",
  cursor_granularity: "PT0.000001S"
  step: "P1D"
```

will create one slice per day for the interval `2021-02-01` - `2021-03-01`. The first slice will start from the `start_datetime` and end at `start_datetime + step - cursor_granularity` like this: `{"start_time": "2021-02-01T00:00:00.000000+0000", "end_time": "2021-02-01T23:59:59.999999+0000"}`. `cursor_granularity` allows the DatetimeStreamSlicer to create non overlapping slices so that the `end_time` of a slice is just before the `start_time` of the next one. 

The `DatetimeStreamSlicer` also supports an optional lookback window, specifying how many days before the start_datetime to read data for.

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z",
  cursor_granularity: "PT0.000001S"
  lookback_window: "P31D"
  step: "P1D"
```

will read data from `2021-01-01` to `2021-03-01`.

The stream slices will be of the form `{"start_date": "2021-02-01T00:00:00.000000+0000", "end_date": "2021-02-02T23:59:59.999999+0000"}`
The stream slices' field names can be customized through the `stream_state_field_start` and `stream_state_field_end` parameters.

The `datetime_format` can be used to specify the format of the start and end time. It is [RFC3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6) by default.

The Stream's state will be derived by reading the record's `cursor_field`.
If the `cursor_field` is `created`, and the record is `{"id": 1234, "created": "2021-02-02T00:00:00.000000+0000"}`, then the state after reading that record is `"created": "2021-02-02T00:00:00.000000+0000"`. [^1]

Note that all durations are expressed as [ISO 8601 durations](https://en.wikipedia.org/wiki/ISO_8601#Durations).

#### Cursor update

When reading data from the source, the cursor value will be updated to the max datetime between

- The last record's cursor field
- The start of the stream slice
- The current cursor value. This ensures that the cursor will be updated even if a stream slice does not contain any data

#### Stream slicer on dates

If an API supports filtering data based on the cursor field, the `start_time_option` and `end_time_option` parameters can be used to configure this filtering.
For instance, if the API supports filtering using the request parameters `created[gte]` and `created[lte]`, then the stream slicer can specify the request parameters as

```yaml
stream_slicer:
  type: "DatetimeStreamSlicer"
  <...>
  start_time_option:
    field_name: "created[gte]"
    inject_into: "request_parameter"
  end_time_option:
    field_name: "created[lte]"
    inject_into: "request_parameter"
```

### List stream slicer

`ListStreamSlicer` iterates over values from a given list.
It is defined by

- The slice values, which are the valid values for the cursor field
- The cursor field on a record
- request_option: optional request option to set on outgoing request parameters

Schema:

```yaml
  ListStreamSlicer:
    type: object
    required:
      - slice_values
      - cursor_field
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      slice_values:
        type: array
        items:
          type: string
      cursor_field:
        type: string
      request_option:
        "$ref": "#/definitions/RequestOption"
```

As an example, this stream slicer will iterate over the 2 repositories ("airbyte" and "airbyte-secret") and will set a request_parameter on outgoing HTTP requests.

```yaml
stream_slicer:
  type: "ListStreamSlicer"
  slice_values:
    - "airbyte"
    - "airbyte-secret"
  cursor_field: "repository"
  request_option:
    field_name: "repository"
    inject_into: "request_parameter"
```

### Cartesian Product stream slicer

`CartesianProductStreamSlicer` iterates over the cartesian product of its underlying stream slicers.

Schema:

```yaml
  CartesianProductStreamSlicer:
    type: object
    required:
      - stream_slicers
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      stream_slicers:
        type: array
        items:
          "$ref": "#/definitions/StreamSlicer"
```

Given 2 stream slicers with the following slices:
A: `[{"start_date": "2021-01-01", "end_date": "2021-01-01"}, {"start_date": "2021-01-02", "end_date": "2021-01-02"}]`
B: `[{"s": "hello"}, {"s": "world"}]`
the resulting stream slices are

```
[
    {"start_date": "2021-01-01", "end_date": "2021-01-01", "s": "hello"},
    {"start_date": "2021-01-01", "end_date": "2021-01-01", "s": "world"},
    {"start_date": "2021-01-02", "end_date": "2021-01-02", "s": "hello"},
    {"start_date": "2021-02-01", "end_date": "2021-02-01", "s": "world"},
]
```

## SubstreamSlicer

Substreams are streams that depend on the records on another stream

We might for instance want to read all the commits for a given repository (parent stream).

Substreams are implemented by defining their stream slicer as a`SubstreamSlicer`.

`SubstreamSlicer` iterates over the parent's stream slices.
We might for instance want to read all the commits for a given repository (parent resource).

- what the parent stream is
- what is the key of the records in the parent stream
- what is the field defining the stream slice representing the parent record
- how to specify that information on an outgoing HTTP request

Schema:

```yaml
  SubstreamSlicer:
    type: object
    required:
      - parent_stream_configs
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      parent_stream_configs:
        type: array
        items:
          "$ref": "#/definitions/ParentStreamConfig"
  ParentStreamConfig:
    type: object
    required:
      - stream
      - parent_key
      - stream_slice_field
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      stream:
        "$ref": "#/definitions/Stream"
      parent_key:
        type: string
      stream_slice_field:
        type: string
      request_option:
        "$ref": "#/definitions/RequestOption"
```

Example:

```yaml
stream_slicer:
  type: "SubstreamSlicer"
  parent_streams_configs:
    - stream: "*ref(repositories_stream)"
      parent_key: "id"
      stream_slice_field: "repository"
      request_option:
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
  stream_slicer:
    type: "SubstreamSlicer"
parent_streams_configs:
  - stream: "*ref(repositories_stream)"
    parent_key: "id"
    stream_slice_field: "repository"
```

## Nested streams

Nested streams, subresources, or streams that depend on other streams can be implemented using a [`SubstreamSlicer`](#SubstreamSlicer)

## More readings

- [Incremental streams](../../cdk-python/incremental-stream.md)
- [Stream slices](../../cdk-python/stream-slices.md)

[^1] This is a slight oversimplification. See [update cursor section](#cursor-update) for more details on how the cursor is updated.
