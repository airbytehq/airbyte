# Incremental Syncs

An incremental sync is a sync which pulls only the data that has changed since the previous sync (as opposed to all the data available in the data source).

Incremental syncs are usually implemented using a cursor value (like a timestamp) that delineates which data was pulled and which data is new. A very common cursor value is an `updated_at` timestamp. This cursor means that records whose `updated_at` value is less than or equal than that cursor value have been synced already, and that the next sync should only export records whose `updated_at` value is greater than the cursor value.

On a stream, `incremental_sync` defines the connector behavior to support cursor based replication.

When a stream is read incrementally, a state message will be output by the connector after reading all the records, which allows for checkpointing (link: https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing). On the next incremental sync, the prior state message will be used to determine the next set of records to read.

## DatetimeBasedCursor

The `DatetimeBasedCursor` is used to read records from the underlying data source (e.g: an API)  according to a specified datetime range. This time range is partitioned into time windows according to the `step`. For example, if you have `start_time=2022-01-01T00:00:00`, `end_time=2022-01-05T00:00:00` and `step=P1D`, the following partitions will be created:

| Start               | End                 |
|---------------------|---------------------|
| 2022-01-01T00:00:00 | 2022-01-01T23:59:59 |
| 2022-01-02T00:00:00 | 2022-01-02T23:59:59 |
| 2022-01-03T00:00:00 | 2022-01-03T23:59:59 |
| 2022-01-04T00:00:00 | 2022-01-04T23:59:59 |
| 2022-01-05T00:00:00 | 2022-01-05T00:00:00 |

During the sync, records are read from the API according to these time windows and the `cursor_field` indicates where the datetime value is stored on a record. This cursor is progressed as these partitions of records are successfully transmitted to the destination.

Upon a successful sync, the final stream state will be the datetime of the last record emitted. On the subsequent sync, the connector will fetch records whose cursor value begins on that datetime and onward.

Schema:

```yaml
  DatetimeBasedCursor:
    description: Cursor to provide incremental capabilities over datetime
    type: object
    required:
      - type
      - cursor_field
      - end_datetime
      - datetime_format
      - cursor_granularity
      - start_datetime
      - step
    properties:
      type:
        type: string
        enum: [DatetimeBasedCursor]
      cursor_field:
        description: The location of the value on a record that will be used as a bookmark during sync
        type: string
      datetime_format:
        description: The format of the datetime
        type: string
      cursor_granularity:
        description: Smallest increment the datetime_format has (ISO 8601 duration) that is used to ensure the start of a slice does not overlap with the end of the previous one
        type: string
      end_datetime:
        description: The datetime that determines the last record that should be synced
        anyOf:
          - type: string
          - "$ref": "#/definitions/MinMaxDatetime"
      start_datetime:
        description: The datetime that determines the earliest record that should be synced
        anyOf:
          - type: string
          - "$ref": "#/definitions/MinMaxDatetime"
      step:
        description: The size of the time window (ISO8601 duration)
        type: string
      end_time_option:
        description: Request option for end time
        "$ref": "#/definitions/RequestOption"
      lookback_window:
        description: How many days before start_datetime to read data for (ISO8601 duration)
        type: string
      start_time_option:
        description: Request option for start time
        "$ref": "#/definitions/RequestOption"
      partition_field_end:
        description: Partition start time field
        type: string
      partition_field_start:
        description: Partition end time field
        type: string
      $parameters:
        type: object
        additionalProperties: true
  MinMaxDatetime:
    description: Compares the provided date against optional minimum or maximum times. The max_datetime serves as the ceiling and will be returned when datetime exceeds it. The min_datetime serves as the floor
    type: object
    required:
      - type
      - datetime
    properties:
      type:
        type: string
        enum: [MinMaxDatetime]
      datetime:
        type: string
      datetime_format:
        type: string
        default: ""
      max_datetime:
        type: string
      min_datetime:
        type: string
      $parameters:
        type: object
        additionalProperties: true
```

Example:

```yaml
incremental_sync:
  type: DatetimeBasedCursor
  start_datetime: "2022-01-01T00:00:00.000000+0000"
  end_datetime: "2022-01-05T00:00:00.000000+0000"
  datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
  cursor_granularity: "PT0.000001S"
  step: "P1D"
```

will result in the datetime partition windows in the example mentioned earlier.

### Lookback Windows

The `DatetimeBasedCursor` also supports an optional lookback window, specifying how many days before the start_datetime to read data for.

```yaml
incremental_sync:
  type: DatetimeBasedCursor
  start_datetime: "2022-02-01T00:00:00.000000+0000"
  end_datetime: "2022-03-01T00:00:00.000000+0000"
  datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
  cursor_granularity: "PT0.000001S"
  lookback_window: "P31D"
  step: "P1D"
```

will read data from `2022-01-01` to `2022-03-01`.

The stream partitions will be of the form `{"start_date": "2021-02-01T00:00:00.000000+0000", "end_date": "2021-02-02T23:59:59.999999+0000"}`
The stream partitions' field names can be customized through the `partition_field_start` and `partition_field_end` parameters.

The `datetime_format` can be used to specify the format of the start and end time. It is [RFC3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6) by default.

The Stream's state will be derived by reading the record's `cursor_field`.
If the `cursor_field` is `updated_at`, and the record is `{"id": 1234, "created": "2021-02-02T00:00:00.000000+0000"}`, then the state after reading that record is `"updated_at": "2021-02-02T00:00:00.000000+0000"`. [^1]

Note that all durations are expressed as [ISO 8601 durations](https://en.wikipedia.org/wiki/ISO_8601#Durations).

### Filtering according to Cursor Field

If an API supports filtering data based on the cursor field, the `start_time_option` and `end_time_option` parameters can be used to configure this filtering.
For instance, if the API supports filtering using the request parameters `created[gte]` and `created[lte]`, then the component can specify the request parameters as

```yaml
incremental_sync:
  type: DatetimeBasedCursor
  <...>
  start_time_option:
    type: RequestOption
    field_name: "created[gte]"
    inject_into: "request_parameter"
  end_time_option:
    type: RequestOption
    field_name: "created[lte]"
    inject_into: "request_parameter"
```

## More readings

- [Incremental reads](../../cdk-python/incremental-stream.md)
