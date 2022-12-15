# Incremental Streams

An incremental Stream is a stream which reads data incrementally. That is, it only reads data that was generated or updated since the last time it ran, and is thus far more efficient than a stream which reads all the source data every time it runs. If possible, developers are encouraged to implement incremental streams to reduce sync times and resource usage.

Several new pieces are essential to understand how incrementality works with the CDK:

* `AirbyteStateMessage`
* cursor fields
* `IncrementalMixin`
* `Stream.get_updated_state` (deprecated)

  as well as a few other optional concepts.

### `AirbyteStateMessage`

The `AirbyteStateMessage` persists state between syncs, and allows a new sync to pick up from where the previous sync last finished. See the [incremental sync guide](https://docs.airbyte.io/understanding-airbyte/connections/incremental-append) for more information.

### Cursor fields

The `cursor_field` refers to the field in the stream's output records used to determine the "recency" or ordering of records. An example is a `created_at` or `updated_at` field in an API or DB table.

Cursor fields can be input by the user \(e.g: a user can choose to use an auto-incrementing `id` column in a DB table\) or they can be defined by the source e.g: where an API defines that `updated_at` is what determines the ordering of records.

In the context of the CDK, setting the `Stream.cursor_field` property to any truthy value informs the framework that this stream is incremental.

### `IncrementalMixin`

This class mixin adds property `state` with abstract setter and getter.
The `state` attribute helps the CDK figure out the current state of sync at any moment (in contrast to deprecated `Stream.get_updated_state` method).
The setter typically deserialize state saved by CDK and initialize internal state of the stream.
The getter should serialize internal state of the stream. 

```python
@property
def state(self) -> Mapping[str, Any]:
   return {self.cursor_field: str(self._cursor_value)}

@state.setter
def state(self, value: Mapping[str, Any]):
   self._cursor_value = value[self.cursor_field]
```

The actual logic of updating state during reading is implemented somewhere else, usually as part of `read_records` method, right after the latest record returned that matches the new state.
Therefore, the state represents the latest checkpoint successfully achieved, and all next records should match the next state after that one.
```python
def read_records(self, ...):
   ...
   yield record
   yield record
   yield record
   self._cursor_value = max(record[self.cursor_field], self._cursor_value)
   yield record
   yield record
   yield record
   self._cursor_value = max(record[self.cursor_field], self._cursor_value)
```

### `Stream.get_updated_state`
(deprecated since 1.48.0, see `IncrementalMixin`)

This function helps the stream keep track of the latest state by inspecting every record output by the stream \(as returned by the `Stream.read_records` method\) and comparing it against the most recent state object. This allows sync to resume from where the previous sync last stopped, regardless of success or failure. This function typically compares the state object's and the latest record's cursor field, picking the latest one.

## Checkpointing state

There are two ways to checkpointing state \(i.e: controlling the timing of when state is saved\) while reading data from a connector:

1. Interval-based checkpointing
2. Stream Slices

### Interval based checkpointing

This is the simplest method for checkpointing. When the interval is set to a truthy value e.g: 100, then state is persisted after every 100 records output by the connector e.g: state is saved after reading 100 records, then 200, 300, etc..

While this is very simple, **it requires that records are output in ascending order with regards to the cursor field**. For example, if your stream outputs records in ascending order of the `updated_at` field, then this is a good fit for your usecase. But if the stream outputs records in a random order, then you cannot use this method because we can only be certain that we read records after a particular `updated_at` timestamp once all records have been fully read.

Interval based checkpointing can be implemented by setting the `Stream.state_checkpoint_interval` property e.g:

```text
class MyAmazingStream(Stream): 
  # Save the state every 100 records
  state_checkpoint_interval = 100
```

### `Stream.stream_slices`

Stream slices can be used to achieve finer grain control of when state is checkpointed.

Conceptually, a Stream Slice is a subset of the records in a stream which represent the smallest unit of data which can be re-synced. Once a full slice is read, an `AirbyteStateMessage` will be output, causing state to be saved. If a connector fails while reading the Nth slice of a stream, then the next time it retries, it will begin reading at the beginning of the Nth slice again, rather than re-read slices `1...N-1`.

A Slice object is not typed, and the developer is free to include any information necessary to make the request. This function is called when the `Stream` is about to be read. Typically, the `stream_slices` function, via inspecting the state object, generates a Slice for every request to be made.

As an example, suppose an API is able to dispense data hourly. If the last sync was exactly 24 hours ago, we can either make an API call retrieving all data at once, or make 24 calls each retrieving an hour's worth of data. In the latter case, the `stream_slices` function, sees that the previous state contains yesterday's timestamp, and returns a list of 24 Slices, each with a different hourly timestamp to be used when creating request. If the stream fails halfway through \(at the 12th slice\), then the next time it starts reading, it will read from the beginning of the 12th slice.

For a more in-depth description of stream slicing, see the [Stream Slices guide](https://github.com/airbytehq/airbyte/tree/8500fef4133d3d06e16e8b600d65ebf2c58afefd/docs/connector-development/cdk-python/stream-slices.md).

## Conclusion

In summary, an incremental stream requires:

* the `cursor_field` property
* to be inherited from `IncrementalMixin` and state methods implemented
* Optionally, the `stream_slices` function

