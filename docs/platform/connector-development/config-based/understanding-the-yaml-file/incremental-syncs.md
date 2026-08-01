# Incremental Sync

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

## Incremental Support for Child Streams

Nested streams, subresources, or streams that depend on other streams can be implemented using a [`SubstreamPartitionRouter`](./partition-router.md#substreampartitionrouter).

The default state format is **per partition with fallback to global**, but there are options to enhance efficiency depending on your use case: **incremental_dependency** and **global_substream_cursor**. Here's when and how to use each option, with examples:

### Per Partition with Fallback to Global (Default)

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

### Incremental Dependency

`incremental_dependency: true` on a `SubstreamPartitionRouter` tells the parent stream to be read with state during warm syncs. On the first sync it iterates all parents, the same as it would without the flag. On subsequent syncs it persists the parent's cursor as `parent_state` inside the child stream's state, and the partition router uses that to iterate only parent partitions whose cursor has advanced since the last sync. For each parent the router visits, the child stream re-fetches its records.

The intent is to avoid re-iterating every parent on every sync when the parent set is large.

- **When to use**: the parent stream has its own `incremental_sync` block, the child stream has its own incremental cursor (see [When `incremental_dependency` has no effect](#when-incremental_dependency-has-no-effect) below), and the API satisfies [the parent-cursor-bump assumption](#the-parent-cursor-bump-assumption) below.
- **Example state**:

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

#### When `incremental_dependency` has no effect

`incremental_dependency: true` is a runtime optimization on the partition router rather than a declaration that the child stream is incremental. It only takes effect when the child stream itself defines an `incremental_sync` block. When the child has no cursor of its own, the CDK assigns it a `FinalStateCursor`, which never persists `parent_state`; in that case every sync re-reads the parent from `start_datetime` and the flag has no observable effect. The optimization becomes active once the child stream gains its own incremental cursor — typically one derived from a parent timestamp — or once the child uses a base stream class that supplies a per-partition cursor.

#### The parent-cursor-bump assumption

For `incremental_dependency: true` to be safe, the API needs to update the parent record's cursor field whenever a child resource is created, updated, or deleted. If a child mutation does not advance the parent's cursor, that child record is added to a parent the partition router will skip on subsequent warm syncs — so the new child is never observed, even though the sync itself completes successfully. When a particular child mutation does not bump the parent cursor, disable `incremental_dependency` on that child's `SubstreamPartitionRouter`. Without the flag, the partition router re-iterates the parent stream from `start_date` on every sync, so children added to parents whose cursor was never advanced are still observed.

API behavior here is per-resource and frequently varies within a single API, so this assumption typically benefits from empirical verification before shipping. A typical confirmation pass looks like:

1. Capture the parent record's cursor field (for example, `updated_at`).
2. Perform each kind of child mutation the connector exposes — including create, update, delete, and any side-effecting endpoints such as state transitions, votes, or watchers.
3. Re-fetch the parent and compare the cursor field. If it did not advance, that child operation is unsafe under `incremental_dependency: true`: children added to an unchanged parent are not re-iterated on warm syncs.

A few common false negatives are worth being aware of: no-op mutations (such as adding the same watcher twice), parent re-fetches that hit a cache, idempotent endpoints that return success without actually writing, and APIs that expose more than one timestamp where only one of them is the cursor. A positive write that produces a real state change tends to be the most reliable signal.

### Global Substream Cursor

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

- **Per Partition with Fallback to Global (Default)**: Best for managing scalability and optimizing state size. Starts with per partition cursors, and automatically falls back to a global cursor if the number of records in the parent sync exceeds two times the partition limit.
- **Incremental Dependency**: Use for incremental parent streams with a dependent child cursor. Ensure the API updates the parent cursor when child records are added or updated.
- **Global Substream Cursor**: Use cautiously for custom connectors with very large parent streams. Avoids per partition state management but sacrifices some granularity.

Choose the option that best fits your data structure and sync requirements to optimize performance and data integrity.

## Related

- *No-Code Connector Builder*: [Incremental Sync](/platform/connector-development/connector-builder-ui/incremental-sync)
- [Incremental reads](../../cdk-python/incremental-stream.md)
