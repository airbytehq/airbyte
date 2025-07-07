# Resumable Full Refresh Streams

:::warning
This feature is currently in-development. CDK interfaces and classes relating to this feature may change without notice.
:::

A resumable full refresh stream is one that cannot offer incremental sync functionality because the API endpoint
does not offer a way to retrieve data relative to a specific point in time. Being able to only fetch records after
a specific timestamp (i.e. 2024-04-01) is an example of an API endpoint that supports incremental sync. An API that
only supports pagination using an arbitrary page number is a candidate for resumable full refresh.

## Synthetic cursors

Unlike Incremental stream cursors which rely on values such as a date (i.e. `2024-04-30`) to reliably partition the
data retrieved from an API after the provided point, Resumable Full Refresh streams define cursors according to
values like a page number or next record cursor. Some APIs don't provide guarantees that records in between
requests might have changed relative to others when using pagination parameters. We refer to the artificial page
values used to checkpoint state in between resumable full refresh sync attempts as synthetic cursors.

## Criteria for Resumable Full Refresh

:::warning
Resumable full refresh in the Python CDK does not currently support substreams. This work is currently in progress.
:::

Determining if a stream can implement checkpointing state using resumable full refresh is based on criteria of the
API endpoint being used to fetch data. This can be done either by reading the API documentation or making cURL
requests to API endpoint itself:

1. The API endpoint must support pagination. If records are only returned within a single page request, there is no suitable checkpoint value. The synthetic cursor should be based on value included in the request to fetch the next set of records.
2. When requesting a page of records, the same request should yield the same records in the response. Because RFR relies on getting records after the last checkpointed pagination cursor, it relies on the API to return roughly the same records on a subsequent attempt. An API that returns different set of records for a specific page each time a request is made would not be compatible with RFR.

An example of an endpoint compatible with resumable full refresh is the [Hubspot GET /contacts](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts) API endpoint.
This endpoint does not support getting records relative to a timestamp. However, it does allow for cursor-based
pagination using `vidOffset` and records are always returned on the same page and in the same order if a request
is retried.

## Implementing Resumable Full Refresh streams

### `StateMixin`

This class mixin adds property `state` with abstract setter and getter.
The `state` attribute helps the CDK figure out the current state of sync at any moment.
The setter typically deserializes state saved by CDK and initialize internal state of the stream.
The getter should serialize internal state of the stream.

```python
@property
def state(self) -> Mapping[str, Any]:
   return {self.cursor_field: str(self._cursor_value)}

@state.setter
def state(self, value: Mapping[str, Any]):
   self._cursor_value = value[self.cursor_field]
```

### `Stream.read_records()`

To implement resumable full refresh, the stream must override it's `Stream.read_records()` method. This implementation is responsible for:

1. Reading the stream's current state and assigning it to `next_page_token` which populates the pagination page parameter for the next request
2. Make the outbound API request to retrieve the next page of records.
3. Transform (if needed) and emit each response record.
4. Update the stream's state to the page of records to retrieve using the stream's `next_page_token()` method.

### State object format

In the `Stream.read_records()` implementation, the stream must structure the state object representing the next page
to request according to a certain format.

Stream state that invokes a subsequent request to retrieve more records should be formatted with a single `key:value` pair:

```json
{
  "page": 25
}
```

The empty object `{}` indicates that a resumable full refresh stream has no more records to sync.

### `AirbyteStateMessage`

The `AirbyteStateMessage` persists state between sync attempts after a prior attempt fails. Subsequent sync attempts
of a job can pick up from the last checkpoint of the previous one. For resumable full refresh syncs, state is passed
in between sync attempts, but deleted at the beginning of new sync jobs.

## Conclusion

In summary, a resumable full refresh stream requires:

- to be inherited from `StateMixin` and state methods implemented
- implementing `Stream.read_records()` to get the Stream's current state, request a single page of records, and update the Stream's state with the next page to fetch or `{}`.
