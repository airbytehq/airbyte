# The Incremental Stream

An incremental Stream is a stream which reads data incrementally. That is, it only reads data that was generated or updated since the last time it ran, and is thus far more efficient than a stream which reads all the source data every time it runs. If possible, developers are encouraged to implement incremental streams to reduce sync times and resource usage. 
 
Several new pieces are essential to understand how incrementality works with the CDK: 

* `AirbyteStateMessage`
* cursor fields
* `Stream.get_updated_state`
as well as a few other optional concepts. 

### `AirbyteStateMessage`

The `AirbyteStateMessage`
persists state between syncs, and allows a new sync to pick up from where the previous sync last finished. See the [incremental sync guide](https://docs.airbyte.io/understanding-airbyte/connections/incremental-append) for more information. 

### Cursor fields
The `cursor_field` refers to the field in the stream's output records used to determine the "recency" or ordering of records. An example is a `created_at` or `updated_at` field in an API or DB table.

Cursor fields can be input by the user (e.g: a user can choose to use an auto-incrementing `id` column in a DB table) or they can be defined by the source e.g: where an API defines that `updated_at` is what determines the ordering of records. 

In the context of the CDK, setting the `Stream.cursor_field` property to any value informs the framework that this stream is incremental.

### `Stream.get_updated_state`
This function helps the CDK figure out the latest state for every record output by the connector
(as returned by the `Stream.read_records` method). This allows sync to resume from where the previous sync last stopped,
regardless of success or failure. This function typically compares the state object's and the latest record's cursor field, picking the latest one.

### `Stream.stream_slices`
The above methods can optionally be paired with the `stream_slices` function to granularly control exactly when state is saved. Conceptually, a Stream Slice is a subset of the records in a stream which represent the smallest unit of data which can be re-synced. Once a full slice is read, an `AirbyteStateMessage` will be output, causing state to be saved. If a connector fails while reading the Nth slice of a stream, then the next time it retries, it will begin reading at the beginning of the Nth slice again, rather than re-read slices `1...N-1`. 

A Slice object is not typed, and the developer is free to include any information necessary to make the request. This function is called when the `Stream` is about to be read. Typically, the `stream_slices` function, via inspecting the state object,
generates a Slice for every request to be made.

As an example, suppose an API is able to dispense data hourly. If the last sync was exactly 24 hours ago,
we can either make an API call retrieving all data at once, or make 24 calls each retrieving an hour's
worth of data. In the latter case, the `stream_slices` function, sees that the previous state contains
yesterday's timestamp, and returns a list of 24 Slices, each with a different hourly timestamp to be
used when creating request. If the stream fails halfway through (at the 12th slice), then the next time it starts reading, it will read from the beginning of the 12th slice.

For a more in-depth description of stream slicing, see the [Stream Slices guide](./stream_slices.md).

## Conclusion 
In summary, an incremental stream requires:
* the `cursor_field` property
* the `get_updated_state` function
* Optionally, the `stream_slices` function
