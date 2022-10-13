# Stream Slicers

`StreamSlicer`s define how to partition a stream into a subset of records.

It can be thought of as an iterator over the stream's data, where a `StreamSlice` is the retriever's unit of work.

When a stream is read incrementally, a state message will be output by the connector after reading every slice, which allows for [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).

At the beginning of a `read` operation, the `StreamSlicer` will compute the slices to sync given the connection config and the stream's current state,
As the `Retriever` reads data from the `Source`, the `StreamSlicer` keeps track of the `Stream`'s state, which will be emitted after reading each stream slice.

More information of stream slicing can be found in the [stream-slices section](../cdk-python/stream-slices.md).

## Implementations

This section gives an overview of the stream slicers currently implemented.

### Datetime

The `DatetimeStreamSlicer` iterates over a datetime range by partitioning it into time windows.
This is done by slicing the stream on the records' cursor value, defined by the Stream's `cursor_field`.

Given a start time, an end time, and a step function, it will partition the interval [start, end] into small windows of the size described by the step.
For instance,

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  step: "1d"
```

will create one slice per day for the interval `2021-02-01` - `2021-03-01`.

The `DatetimeStreamSlicer` also supports an optional lookback window, specifying how many days before the start_datetime to read data for.

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  lookback_window: "31d"
  step: "1d"
```

will read data from `2021-01-01` to `2021-03-01`.

The stream slices will be of the form `{"start_date": "2021-02-01T00:00:00.000000+0000", "end_date": "2021-02-01T00:00:00.000000+0000"}`
The stream slices' field names can be customized through the `stream_state_field_start` and `stream_state_field_end` parameters.

The `datetime_format` can be used to specify the format of the start and end time. It is [RFC3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6) by default.

The Stream's state will be derived by reading the record's `cursor_field`.
If the `cursor_field` is `created`, and the record is `{"id": 1234, "created": "2021-02-02T00:00:00.000000+0000"}`, then the state after reading that record is `"created": "2021-02-02T00:00:00.000000+0000"`. [^1]

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

### Substream slicer

`SubstreamSlicer` iterates over the parent's stream slices.
This is useful for defining sub-resources.

We might for instance want to read all the commits for a given repository (parent resource).

For each stream, the slicer needs to know

- what the parent stream is
- what is the key of the records in the parent stream
- what is the field defining the stream slice representing the parent record
- how to specify that information on an outgoing HTTP request

Assuming the commits for a given repository can be read by specifying the repository as a request_parameter, this could be defined as

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

```yaml
retriever:
  <...>
  requester:
    <...>
    path: "/respositories/{{ stream_slice.repository }}/commits
  stream_slicer:
    type: "SubstreamSlicer"
    parent_streams_configs:
      - stream: "*ref(repositories_stream)"
        parent_key: "id"
        stream_slice_field: "repository"
```

[^1] This is a slight oversimplification. See [update cursor section](#cursor-update) for more details on how the cursor is updated.

## More readings

- [Incremental streams](../cdk-python/incremental-stream.md)
- [Stream slices](../cdk-python/stream-slices.md)