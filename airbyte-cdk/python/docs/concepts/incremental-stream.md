# The Incremental Stream

If possible, developers should try to implement an incremental stream. An incremental stream takes advantage of the
Airbyte Specification's `AirbyteStateMessage` to read only new data. This is suitable for any API that offers filter/group
query parameters and/or has an ordered field in the response. Some common examples are resource-specific ids, timestamps, or
enumerated types. Although the implementation is slightly more complex (not that much as we will soon see) - the resulting
Stream only reads what is necessary, and is thus far more efficient.

Several new pieces are essential to understand how incrementality works with the CDK.

First is the `AirbyteStateMessage` and the `HttpStream`'s `cursor_field`. As mentioned, the `AirbyteStateMessage`
persists state between syncs, and allows a new sync to pick up from where the previous sync last finished.
The `cursor_field` refers to the actual element in the HTTP request used to determine order. The `cursor_field` informs the user which field is used to track cursors. This is useful information in general, but is especially important in scenarios where the user can select cursors as they can pass in the cursor value they'd like to use e.g: choose between `created_at` or `updated_at` fields in an API or DB table.
Setting this cursor field to any value informs the framework that this stream is incremental.
This field is also commonly used as a direct index into the api response to
create the `AirbyteStateMessage`.

Next is the `get_updated_state` function. This function helps the CDK figure out the latest state for every record processed
(as returned by the `parse_response`function mentioned above). This allows sync to resume from where the previous sync last stopped,
regardless of success or failure. This function typically compares the state object's and the latest record's cursor field, picking the latest one.

This can optionally be paired with the `stream_slices` function to granularly control exactly when state is saved. Conceptually, a Stream Slice is a subset of the records in a stream which represent the smallest unit of data which can be re-synced. Once a full slice is read, an `AirbyteStateMessage` will be output, causing state to be saved. If a connector fails while reading the Nth slice of a stream, then the next time it retries, it will begin reading at the beginning of the Nth slice again, rather than re-read slices `1...N-1`.
synced.

In the HTTP case, each Slice is equivalent to a HTTP request; the CDK will make one request
per element returned by the `stream_slices` function. A Slice object is not typed, and the developer
is free to include any information necessary to make the request. This function is called when the
`HTTPStream` is first created. Typically, the `stream_slices` function, via inspecting the state object,
generates a Slice for every request to be made.

As an example, suppose an API is able to dispense data hourly. If the last sync was exactly 24 hours ago,
we can either make an API call retrieving all data at once, or make 24 calls each retrieving an hour's
worth of data. In the latter case, the `stream_slices` function, sees that the previous state contains
yesterday's timestamp, and returns a list of 24 Slices, each with a different hourly timestamp to be
used when creating request. If the stream fails halfway through (at the 12th slice), then the next time it starts reading, it will read from the beginning of the 12th slice.

The current slice being read is passed into every other method in `HttpStream` e.g: `request_params`, `request_headers`, `path`, etc..
to be injected into a request.

In summary, the incremental stream requires:
* the `cursor_field` property
* the `get_updated_state` function
* Optionally, the `stream_slices` function
* updating the `request_params`, `path`, and other functions to incorporate slices