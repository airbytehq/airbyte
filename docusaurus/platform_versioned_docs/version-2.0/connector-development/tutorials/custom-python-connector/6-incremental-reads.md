# Incremental reads

In this section, we'll add support to read data incrementally. While this is optional, you should
implement it whenever possible because reading in incremental mode allows users to save time and
money by only reading new data.

We'll first need to implement three new methods on the base stream class

The `cursor_field` property indicates that records produced by the stream have a cursor that can be
used to identify it in the timeline.

```python
    @property
    def cursor_field(self) -> Optional[str]:
        return self._cursor_field
```

The `get_updated_state` method is used to update the stream's state. We'll set its value to the
maximum between the current state's value and the value extracted from the record.
```python
# import the following library
import datetime
```

```python
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        state_value = max(current_stream_state.get(self.cursor_field, 0), datetime.datetime.strptime(latest_record.get(self._cursor_field, ""), _INCOMING_DATETIME_FORMAT).timestamp())
        return {self._cursor_field: state_value}
```

Note that we're converting the datetimes to unix epoch. We could've also chosen to persist it as an
ISO date. You can use any format that works best for you. Integers are easy to work with so that's
what we'll do for this tutorial.

Then we'll implement the `stream_slices` method, which will be used to partition the stream into
time windows. While this isn't mandatory since we could omit the `end_modified_at` parameter from
our requests and try to read all new records at once, it is preferable to partition the stream
because it enables checkpointing.

This might mean the connector will make more requests than necessary during the initial sync, and
this is most visible when working with a sandbox or an account that does not have many records. The
upside are worth the tradeoff because the additional cost is negligible for accounts that have many
records, and the time cost will be entirely mitigated in a follow up section when we fetch
partitions concurrently.

```python

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_ts = stream_state.get(self._cursor_field, _START_DATE) if stream_state else _START_DATE
        now_ts = datetime.datetime.now().timestamp()
        if start_ts >= now_ts:
            yield from []
            return
        for start, end in self.chunk_dates(start_ts, now_ts):
            yield {"start_date": start, "end_date": end}

    def chunk_dates(self, start_date_ts: int, end_date_ts: int) -> Iterable[Tuple[int, int]]:
        step = int(_SLICE_RANGE * 24 * 60 * 60)
        after_ts = start_date_ts
        while after_ts < end_date_ts:
            before_ts = min(end_date_ts, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1
```

Note that we're introducing the concept of a start date. You might have to fiddle to find the
earliest start date that can be queried. You can also choose to make the start date configurable by
the end user. This will make your life simpler, at the cost of pushing the complexity to the
end-user.

We'll now update the query params. In addition the passing the page size and the include field,
we'll pass in the `start_modified_at` and `end_modified_at` which can be extracted from the
`stream_slice` parameter.

```python
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return urlparse(next_page_token["next_url"]).query
        else:
            return {
                "per_page": _PAGE_SIZE, "include": "response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats",
                "start_modified_at": datetime.datetime.strftime(datetime.datetime.fromtimestamp(stream_slice["start_date"]), _OUTGOING_DATETIME_FORMAT),
                "end_modified_at": datetime.datetime.strftime(datetime.datetime.fromtimestamp(stream_slice["end_date"]), _OUTGOING_DATETIME_FORMAT)
                    }
```

And add the following constants to the source.py file

```python
_START_DATE = datetime.datetime(2020,1,1, 0,0,0).timestamp()
_SLICE_RANGE = 365
_OUTGOING_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_INCOMING_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
```

Notice the outgoing and incoming date formats are different!

Now, update the stream constructor so it accepts a cursor_field parameter.

```python
class SurveyMonkeyBaseStream(HttpStream, ABC):
    def __init__(self, name: str, path: str, primary_key: Union[str, List[str]], data_field: Optional[str], cursor_field: Optional[str],
**kwargs: Any) -> None:
        self._name = name
        self._path = path
        self._primary_key = primary_key
        self._data_field = data_field
        self._cursor_field = cursor_field
        super().__init__(**kwargs)
```

And update the stream's creation:

```python
return [SurveyMonkeyBaseStream(name="surveys", path="/v3/surveys", primary_key="id", data_field="data", cursor_field="date_modified", authenticator=auth)]
```

Finally, modify the configured catalog to run the stream in incremental mode:

```json
{
  "streams": [
    {
      "stream": {
        "name": "surveys",
        "json_schema": {},
        "supported_sync_modes": ["full_refresh", "incremental"]
      },
      "sync_mode": "incremental",
      "destination_sync_mode": "overwrite"
    }
  ]
}
```

Run another read operation. The state messages should include the cursor:

```json
{
  "type": "STATE",
  "state": {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": { "name": "surveys", "namespace": null },
      "stream_state": { "date_modified": 1623348420.0 }
    },
    "sourceStats": { "recordCount": 0.0 }
  }
}
```

And update the sample state to a timestamp earlier than the first record. There should be fewer
records

```json
[
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "surveys"
      },
      "stream_state": {
        "date_modified": 1711753326
      }
    }
  }
]
```

Run another read command, passing the `--state` flag:

```bash
poetry run source-survey-monkey-demo read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state integration_tests/sample_state.json
```

Only more recent records should be read.

In the [next section](7-reading-from-a-subresource.md), we'll implement the survey responses stream,
which depends on the surveys stream.
