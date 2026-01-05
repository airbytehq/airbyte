---
sidebar_label: sync_results
title: airbyte.cloud.sync_results
---

Sync results for Airbyte Cloud workspaces.

## Examples

### Run a sync job and wait for completion

To get started, we&#x27;ll need a `.CloudConnection` object. You can obtain this object by calling
`.CloudWorkspace.get_connection()`.

```python
from airbyte import cloud

# Initialize an Airbyte Cloud workspace object
workspace = cloud.CloudWorkspace(
    workspace_id="123",
    api_key=ab.get_secret("AIRBYTE_CLOUD_API_KEY"),
)

# Get a connection object
connection = workspace.get_connection(connection_id="456")
```

Once we have a `.CloudConnection` object, we can simply call `run_sync()`
to start a sync job and wait for it to complete.

```python
# Run a sync job
sync_result: SyncResult = connection.run_sync()
```

### Run a sync job and return immediately

By default, `run_sync()` will wait for the job to complete and raise an
exception if the job fails. You can instead return immediately by setting
`wait=False`.

```python
# Start the sync job and return immediately
sync_result: SyncResult = connection.run_sync(wait=False)

while not sync_result.is_job_complete():
    print("Job is still running...")
    time.sleep(5)

print(f"Job is complete! Status: {sync_result.get_job_status()}")
```

### Examining the sync result

You can examine the sync result to get more information about the job:

```python
sync_result: SyncResult = connection.run_sync()

# Print the job details
print(
    f'''
    Job ID: {sync_result.job_id}
    Job URL: {sync_result.job_url}
    Start Time: {sync_result.start_time}
    Records Synced: {sync_result.records_synced}
    Bytes Synced: {sync_result.bytes_synced}
    Job Status: {sync_result.get_job_status()}
    List of Stream Names: {', '.join(sync_result.stream_names)}
    '''
)
```

### Reading data from Airbyte Cloud sync result

**This feature is currently only available for specific SQL-based destinations.** This includes
SQL-based destinations such as Snowflake and BigQuery. The list of supported destinations may be
determined by inspecting the constant `.CloudWorkspace.get_connection()`0.

If your destination is supported, you can read records directly from the SyncResult object.

`.CloudWorkspace.get_connection()`1

------

## annotations

## time

## Iterator

## Mapping

## asdict

## dataclass

## TYPE\_CHECKING

## Any

## final

## ab\_datetime\_parse

## api\_util

## FAILED\_STATUSES

## FINAL\_STATUSES

## CachedDataset

## destination\_to\_cache

## AirbyteConnectionSyncError

## AirbyteConnectionSyncTimeoutError

#### DEFAULT\_SYNC\_TIMEOUT\_SECONDS

The default timeout for waiting for a sync job to complete, in seconds.

## SyncAttempt Objects

```python
@dataclass
class SyncAttempt()
```

Represents a single attempt of a sync job.

**This class is not meant to be instantiated directly.** Instead, obtain a `SyncAttempt` by
calling `.SyncResult.get_attempts()`.

#### workspace

#### connection

#### job\_id

#### attempt\_number

#### \_attempt\_data

#### attempt\_id

```python
@property
def attempt_id() -> int
```

Return the attempt ID.

#### status

```python
@property
def status() -> str
```

Return the attempt status.

#### bytes\_synced

```python
@property
def bytes_synced() -> int
```

Return the number of bytes synced in this attempt.

#### records\_synced

```python
@property
def records_synced() -> int
```

Return the number of records synced in this attempt.

#### created\_at

```python
@property
def created_at() -> datetime
```

Return the creation time of the attempt.

#### \_get\_attempt\_data

```python
def _get_attempt_data() -> dict[str, Any]
```

Get attempt data from the provided attempt data.

#### get\_full\_log\_text

```python
def get_full_log_text() -> str
```

Return the complete log text for this attempt.

**Returns**:

  String containing all log text for this attempt, with lines separated by newlines.

## SyncResult Objects

```python
@dataclass
class SyncResult()
```

The result of a sync operation.

**This class is not meant to be instantiated directly.** Instead, obtain a `SyncResult` by
interacting with the `.CloudWorkspace` and `.CloudConnection` objects.

#### workspace

#### connection

#### job\_id

#### table\_name\_prefix

#### table\_name\_suffix

#### \_latest\_job\_info

#### \_connection\_response

#### \_cache

#### \_job\_with\_attempts\_info

#### job\_url

```python
@property
def job_url() -> str
```

Return the URL of the sync job.

Note: This currently returns the connection&#x27;s job history URL, as there is no direct URL
to a specific job in the Airbyte Cloud web app.

TODO: Implement a direct job logs URL on top of the event-id of the specific attempt number.
E.g. {self.connection.job_history_url}?eventId={event-guid}&amp;openLogs=true

#### \_get\_connection\_info

```python
def _get_connection_info(*, force_refresh: bool = False) -> ConnectionResponse
```

Return connection info for the sync job.

#### \_get\_destination\_configuration

```python
def _get_destination_configuration(*,
                                   force_refresh: bool = False
                                   ) -> dict[str, Any]
```

Return the destination configuration for the sync job.

#### is\_job\_complete

```python
def is_job_complete() -> bool
```

Check if the sync job is complete.

#### get\_job\_status

```python
def get_job_status() -> JobStatusEnum
```

Check if the sync job is still running.

#### \_fetch\_latest\_job\_info

```python
def _fetch_latest_job_info() -> JobResponse
```

Return the job info for the sync job.

#### bytes\_synced

```python
@property
def bytes_synced() -> int
```

Return the number of records processed.

#### records\_synced

```python
@property
def records_synced() -> int
```

Return the number of records processed.

#### start\_time

```python
@property
def start_time() -> datetime
```

Return the start time of the sync job in UTC.

#### \_fetch\_job\_with\_attempts

```python
def _fetch_job_with_attempts() -> dict[str, Any]
```

Fetch job info with attempts from Config API using lazy loading pattern.

#### get\_attempts

```python
def get_attempts() -> list[SyncAttempt]
```

Return a list of attempts for this sync job.

#### raise\_failure\_status

```python
def raise_failure_status(*, refresh_status: bool = False) -> None
```

Raise an exception if the sync job failed.

By default, this method will use the latest status available. If you want to refresh the
status before checking for failure, set `refresh_status=True`. If the job has failed, this
method will raise a `AirbyteConnectionSyncError`.

Otherwise, do nothing.

#### wait\_for\_completion

```python
def wait_for_completion(*,
                        wait_timeout: int = DEFAULT_SYNC_TIMEOUT_SECONDS,
                        raise_timeout: bool = True,
                        raise_failure: bool = False) -> JobStatusEnum
```

Wait for a job to finish running.

#### get\_sql\_cache

```python
def get_sql_cache() -> CacheBase
```

Return a SQL Cache object for working with the data in a SQL-based destination&#x27;s.

#### get\_sql\_engine

```python
def get_sql_engine() -> sqlalchemy.engine.Engine
```

Return a SQL Engine for querying a SQL-based destination.

#### get\_sql\_table\_name

```python
def get_sql_table_name(stream_name: str) -> str
```

Return the SQL table name of the named stream.

#### get\_sql\_table

```python
def get_sql_table(stream_name: str) -> sqlalchemy.Table
```

Return a SQLAlchemy table object for the named stream.

#### get\_dataset

```python
def get_dataset(stream_name: str) -> CachedDataset
```

Retrieve an `airbyte.datasets.CachedDataset` object for a given stream name.

This can be used to read and analyze the data in a SQL-based destination.

TODO: In a future iteration, we can consider providing stream configuration information
      (catalog information) to the `CachedDataset` object via the &quot;Get stream properties&quot;
      API: https://reference.airbyte.com/reference/getstreamproperties

#### get\_sql\_database\_name

```python
def get_sql_database_name() -> str
```

Return the SQL database name.

#### get\_sql\_schema\_name

```python
def get_sql_schema_name() -> str
```

Return the SQL schema name.

#### stream\_names

```python
@property
def stream_names() -> list[str]
```

Return the set of stream names.

#### streams

```python
@final
@property
def streams() -> _SyncResultStreams
```

Return a mapping of stream names to `airbyte.CachedDataset` objects.

This is a convenience wrapper around the `stream_names`
property and `get_dataset()` method.

## \_SyncResultStreams Objects

```python
class _SyncResultStreams(Mapping[str, CachedDataset])
```

A mapping of stream names to cached datasets.

#### \_\_init\_\_

```python
def __init__(parent: SyncResult) -> None
```

#### \_\_getitem\_\_

```python
def __getitem__(key: str) -> CachedDataset
```

#### \_\_iter\_\_

```python
def __iter__() -> Iterator[str]
```

#### \_\_len\_\_

```python
def __len__() -> int
```

#### \_\_all\_\_

