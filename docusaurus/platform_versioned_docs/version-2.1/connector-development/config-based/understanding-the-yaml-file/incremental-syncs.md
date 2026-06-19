# Incremental Syncs

An incremental sync is a sync which pulls only the data that has changed since the previous sync (as opposed to all the data available in the data source).

Incremental syncs are usually implemented using a cursor value (like a timestamp) that delineates which data was pulled and which data is new. A very common cursor value is an `updated_at` timestamp. This cursor means that records whose `updated_at` value is less than or equal than that cursor value have been synced already, and that the next sync should only export records whose `updated_at` value is greater than the cursor value.

On a stream, `incremental_sync` defines the connector behavior to support cursor based replication.

When a stream is read incrementally, a state message will be output by the connector after reading all the records, which allows for checkpointing (link: https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing). On the next incremental sync, the prior state message will be used to determine the next set of records to read.

## DatetimeBasedCursor

The `DatetimeBasedCursor` is used to read records from the underlying data source (e.g: an API) according to a specified datetime range. This time range is partitioned into time windows according to the `step`. For example, if you have `start_time=2022-01-01T00:00:00`, `end_time=2022-01-05T12:00:00`, `step=P1D` and `cursor_granularity=PT1S`, the following partitions will be created:

| Start               | End                 |
| ------------------- | ------------------- |
| 2022-01-01T00:00:00 | 2022-01-01T23:59:59 |
| 2022-01-02T00:00:00 | 2022-01-02T23:59:59 |
| 2022-01-03T00:00:00 | 2022-01-03T23:59:59 |
| 2022-01-04T00:00:00 | 2022-01-04T23:59:59 |
| 2022-01-05T00:00:00 | 2022-01-05T12:00:00 |

During the sync, records are read from the API according to these time windows and the `cursor_field` indicates where the datetime value is stored on a record. This cursor is progressed as these partitions of records are successfully transmitted to the destination.

Upon a successful sync, the final stream state will be the datetime of the last record emitted. On the subsequent sync, the connector will fetch records whose cursor value begins on that datetime and onward.

Refer to the schema for both [`DatetimeBasedCursor`](reference.md#/definitions/DatetimeBasedCursor) and [`MinMaxDatetime`](reference.md#/definitions/MinMaxDatetime) in the YAML reference for more details.


Example:

```yaml
incremental_sync:
  type: DatetimeBasedCursor
  start_datetime: "2022-01-01T00:00:00"
  end_datetime: "2022-01-05T12:00:00"
  datetime_format: "%Y-%m-%dT%H:%M:%S"
  cursor_granularity: "PT1S"
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
If the `cursor_field` is `updated_at`, and the record is `{"id": 1234, "updated_at": "2021-02-02T00:00:00.000000+0000"}`, then the state after reading that record is `"updated_at": "2021-02-02T00:00:00.000000+0000"`. [^1]

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

### Nested Streams

Nested streams, subresources, or streams that depend on other streams can be implemented using a [`SubstreamPartitionRouter`](#SubstreamPartitionRouter)

The default state format is **per partition with fallback to global**, but there are options to enhance efficiency depending on your use case: **incremental_dependency** and **global_substream_cursor**. Here's when and how to use each option, with examples:

#### Per Partition with Fallback to Global (Default)
- **Description**: This is the default state format, where each partition has its own cursor. However, when the number of records in the parent sync exceeds two times the set limit, the cursor automatically falls back to a global state to manage efficiency and scalability.
- **Limitation**: The per partition state has a limit of 10,000 partitions. Once this limit is exceeded, the global cursor takes over, aggregating the state across partitions to avoid inefficiencies.
- **When to Use**: Use this as the default option for most cases. It provides the flexibility of managing partitions while preventing performance degradation when large numbers of records are involved.
- **Example State**:
  ```json
  {
      "states": [
          {"partition_key": "partition_1", "cursor_field": "2021-01-15"},
          {"partition_key": "partition_2", "cursor_field": "2021-02-14"}
      ],
      "state": {
          "cursor_field": "2021-02-15"
      },
      "use_global_cursor": false
  }
  ```
#### Incremental Dependency
- **Description**: This option allows the parent stream to be read incrementally, ensuring that only new data is synced.
- **Requirement**: The API must ensure that the parent record's cursor is updated whenever child records are added or updated. If this requirement is not met, child records added to older parent records will be lost.
- **When to Use**: Use this option if the parent stream is incremental and you want to read it with the state. The parent state is updated after processing all the child records for the parent record.
- **Example State**:
  ```json
  {
    "parent_state": {
      "parent_stream": { "timestamp": "2024-08-01T00:00:00" }
    },
    "states": [
      { "partition": "A", "timestamp": "2024-08-01T00:00:00" },
      { "partition": "B", "timestamp": "2024-08-01T01:00:00" }
    ]
  }
  ```

#### Global Substream Cursor
- **Description**: This option uses a single global cursor for all partitions, significantly reducing the state size. It enforces a minimal lookback window based on the previous sync's duration to avoid losing records added or updated during the sync. Since the global cursor is already part of the per partition with fallback to global approach, it should only be used cautiously for custom connectors with exceptionally large parent streams to avoid managing state per partition.
- **When to Use**: Use this option cautiously for custom connectors where the number of partitions in the parent stream is extremely high (e.g., millions of records per sync). The global cursor avoids the inefficiency of managing state per partition but sacrifices some granularity, which may not be suitable for every use case.
- **Operational Detail**: The global cursor is updated only at the end of the sync. If the sync fails, only the parent state is updated, provided that the incremental dependency is enabled. The global cursor ensures that records are captured through a lookback window, even if they were added during the sync.
- **Example State**:
  ```json
  [
    { "timestamp": "2024-08-01"}
  ]
  ```

### Summary
Summary
- **Per Partition with Fallback to Global (Default)**: Best for managing scalability and optimizing state size. Starts with per partition cursors, and automatically falls back to a global cursor if the number of records in the parent sync exceeds two times the partition limit.
- **Incremental Dependency**: Use for incremental parent streams with a dependent child cursor. Ensure the API updates the parent cursor when child records are added or updated.
- **Global Substream Cursor**: Use cautiously for custom connectors with very large parent streams. Avoids per partition state management but sacrifices some granularity.

Choose the option that best fits your data structure and sync requirements to optimize performance and data integrity.

## More readings

- [Incremental reads](../../cdk-python/incremental-stream.md)
- Many of the concepts discussed here are described in the [No-Code Connector Builder docs](../../connector-builder-ui/incremental-sync.md) as well, with more examples.
