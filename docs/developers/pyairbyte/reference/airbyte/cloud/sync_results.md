---
id: airbyte-cloud-sync_results
title: airbyte.cloud.sync_results
---

Sync results for Airbyte Cloud workspaces.

## Examples

### Run a sync job and wait for completion

To get started, we'll need a `.CloudConnection` object. You can obtain this object by calling
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
determined by inspecting the constant `airbyte.cloud.constants.READABLE_DESTINATION_TYPES`.

If your destination is supported, you can read records directly from the SyncResult object.

```python
# Assuming we've already created a `connection` object...
sync_result = connection.get_sync_result()

# Print a list of available stream names
print(sync_result.stream_names)

# Get a dataset from the sync result
dataset: CachedDataset = sync_result.get_dataset("users")

# Get the SQLAlchemy table to use in SQL queries...
users_table = dataset.to_sql_table()
print(f"Table name: {users_table.name}")

# Or iterate over the dataset directly
for record in dataset:
    print(record)
```

------

### `SyncAttempt` {#airbyte.cloud.sync_results.SyncAttempt}

<ApiMember kind="class">

<ApiSignature>

```python
class SyncAttempt(
    workspace: CloudWorkspace,
    connection: CloudConnection,
    job_id: int,
    attempt_number: int,
)
```

</ApiSignature>

Represents a single attempt of a sync job.

**This class is not meant to be instantiated directly.** Instead, obtain a `SyncAttempt` by
calling `.SyncResult.get_attempts()`.

#### Attributes {#airbyte.cloud.sync_results.SyncAttempt--attributes}

- **`attempt_id`**&nbsp;(`int`) — Return the attempt ID.

- **`attempt_number`**&nbsp;(`int`)

- **`bytes_synced`**&nbsp;(`int`) — Return the number of bytes synced in this attempt.

- **`connection`**&nbsp;(`CloudConnection`)

- **`created_at`**&nbsp;(`datetime`) — Return the creation time of the attempt.

- **`job_id`**&nbsp;(`int`)

- **`records_synced`**&nbsp;(`int`) — Return the number of records synced in this attempt.

- **`status`**&nbsp;(`str`) — Return the attempt status.

- **`workspace`**&nbsp;(`CloudWorkspace`)

#### `get_full_log_text` {#airbyte.cloud.sync_results.SyncAttempt.get_full_log_text}

<ApiMember kind="method">

<ApiSignature>

```python
def get_full_log_text(self) -> str
```

</ApiSignature>

Return the complete log text for this attempt.

**Returns:**

String containing all log text for this attempt, with lines separated by newlines.

</ApiMember>

</ApiMember>

### `SyncResult` {#airbyte.cloud.sync_results.SyncResult}

<ApiMember kind="class">

<ApiSignature>

```python
class SyncResult(
    workspace: CloudWorkspace,
    connection: CloudConnection,
    job_id: int,
    table_name_prefix: str = '',
    table_name_suffix: str = '',
)
```

</ApiSignature>

The result of a sync operation.

**This class is not meant to be instantiated directly.** Instead, obtain a `SyncResult` by
interacting with the `.CloudWorkspace` and `.CloudConnection` objects.

#### Attributes {#airbyte.cloud.sync_results.SyncResult--attributes}

- **`bytes_synced`**&nbsp;(`int`) — Return the number of records processed.

- **`connection`**&nbsp;(`CloudConnection`)

- **`job_id`**&nbsp;(`int`)

- **`job_url`**&nbsp;(`str`) — Return the URL of the sync job.  Note: This currently returns the connection's job history URL, as there is no direct URL to a specific job in the Airbyte Cloud web app.  TODO: Implement a direct job logs URL on top of the event-id of the specific attempt number.       E.g. \{self.connection.job_history_url\}?eventId=\{event-guid\}&openLogs=true

- **`records_synced`**&nbsp;(`int`) — Return the number of records processed.

- **`start_time`**&nbsp;(`datetime`) — Return the start time of the sync job in UTC.

- **`stream_names`**&nbsp;(`list[str]`) — Return the set of stream names.

- **`streams`**&nbsp;(`_SyncResultStreams`) — Return a mapping of stream names to `airbyte.CachedDataset` objects.  This is a convenience wrapper around the `stream_names` property and `get_dataset()` method.

- **`table_name_prefix`**&nbsp;(`str`)

- **`table_name_suffix`**&nbsp;(`str`)

- **`workspace`**&nbsp;(`CloudWorkspace`)

#### `get_attempts` {#airbyte.cloud.sync_results.SyncResult.get_attempts}

<ApiMember kind="method">

<ApiSignature>

```python
def get_attempts(self) -> list[airbyte.cloud.sync_results.SyncAttempt]
```

</ApiSignature>

Return a list of attempts for this sync job.

</ApiMember>

#### `get_dataset` {#airbyte.cloud.sync_results.SyncResult.get_dataset}

<ApiMember kind="method">

<ApiSignature>

```python
def get_dataset(self, stream_name: str) -> airbyte.datasets._sql.CachedDataset
```

</ApiSignature>

Retrieve an `airbyte.datasets.CachedDataset` object for a given stream name.

This can be used to read and analyze the data in a SQL-based destination.

TODO: In a future iteration, we can consider providing stream configuration information
      (catalog information) to the `CachedDataset` object via the "Get stream properties"
      API: https://reference.airbyte.com/reference/getstreamproperties

</ApiMember>

#### `get_job_status` {#airbyte.cloud.sync_results.SyncResult.get_job_status}

<ApiMember kind="method">

<ApiSignature>

```python
def get_job_status(self) -> airbyte.cloud.models.JobStatusEnum
```

</ApiSignature>

Check if the sync job is still running.

</ApiMember>

#### `get_sql_cache` {#airbyte.cloud.sync_results.SyncResult.get_sql_cache}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_cache(self) -> CacheBase
```

</ApiSignature>

Return a SQL Cache object for working with the data in a SQL-based destination's.

</ApiMember>

#### `get_sql_database_name` {#airbyte.cloud.sync_results.SyncResult.get_sql_database_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_database_name(self) -> str
```

</ApiSignature>

Return the SQL database name.

</ApiMember>

#### `get_sql_engine` {#airbyte.cloud.sync_results.SyncResult.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> sqlalchemy.engine.Engine
```

</ApiSignature>

Return a SQL Engine for querying a SQL-based destination.

</ApiMember>

#### `get_sql_schema_name` {#airbyte.cloud.sync_results.SyncResult.get_sql_schema_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_schema_name(self) -> str
```

</ApiSignature>

Return the SQL schema name.

</ApiMember>

#### `get_sql_table` {#airbyte.cloud.sync_results.SyncResult.get_sql_table}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table(self, stream_name: str) -> sqlalchemy.Table
```

</ApiSignature>

Return a SQLAlchemy table object for the named stream.

</ApiMember>

#### `get_sql_table_name` {#airbyte.cloud.sync_results.SyncResult.get_sql_table_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table_name(self, stream_name: str) -> str
```

</ApiSignature>

Return the SQL table name of the named stream.

</ApiMember>

#### `is_job_complete` {#airbyte.cloud.sync_results.SyncResult.is_job_complete}

<ApiMember kind="method">

<ApiSignature>

```python
def is_job_complete(self) -> bool
```

</ApiSignature>

Check if the sync job is complete.

</ApiMember>

#### `raise_failure_status` {#airbyte.cloud.sync_results.SyncResult.raise_failure_status}

<ApiMember kind="method">

<ApiSignature>

```python
def raise_failure_status(self, *, refresh_status: bool = False) -> None
```

</ApiSignature>

Raise an exception if the sync job failed.

By default, this method will use the latest status available. If you want to refresh the
status before checking for failure, set `refresh_status=True`. If the job has failed, this
method will raise a `AirbyteConnectionSyncError`.

Otherwise, do nothing.

</ApiMember>

#### `wait_for_completion` {#airbyte.cloud.sync_results.SyncResult.wait_for_completion}

<ApiMember kind="method">

<ApiSignature>

```python
def wait_for_completion(
    self,
    *,
    wait_timeout: int = 1800,
    raise_timeout: bool = True,
    raise_failure: bool = False,
) -> airbyte.cloud.models.JobStatusEnum
```

</ApiSignature>

Wait for a job to finish running.

</ApiMember>

</ApiMember>