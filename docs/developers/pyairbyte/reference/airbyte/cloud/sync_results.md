---
id: airbyte-cloud-sync_results
title: airbyte.cloud.sync_results
---

Module airbyte.cloud.sync_results
=================================
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

Classes
-------

`SyncAttempt(workspace: CloudWorkspace, connection: CloudConnection, job_id: int, attempt_number: int)`
:   Represents a single attempt of a sync job.
    
    **This class is not meant to be instantiated directly.** Instead, obtain a `SyncAttempt` by
    calling `.SyncResult.get_attempts()`.

    ### Instance variables

    `attempt_id: int`
    :   Return the attempt ID.

    `attempt_number: int`
    :

    `bytes_synced: int`
    :   Return the number of bytes synced in this attempt.

    `connection: CloudConnection`
    :

    `created_at: datetime`
    :   Return the creation time of the attempt.

    `job_id: int`
    :

    `records_synced: int`
    :   Return the number of records synced in this attempt.

    `status: str`
    :   Return the attempt status.

    `workspace: CloudWorkspace`
    :

    ### Methods

    `get_full_log_text(self) ‑> str`
    :   Return the complete log text for this attempt.
        
        Returns:
            String containing all log text for this attempt, with lines separated by newlines.

`SyncResult(workspace: CloudWorkspace, connection: CloudConnection, job_id: int, table_name_prefix: str = '', table_name_suffix: str = '')`
:   The result of a sync operation.
    
    **This class is not meant to be instantiated directly.** Instead, obtain a `SyncResult` by
    interacting with the `.CloudWorkspace` and `.CloudConnection` objects.

    ### Instance variables

    `bytes_synced: int`
    :   Return the number of records processed.

    `connection: CloudConnection`
    :

    `job_id: int`
    :

    `job_url: str`
    :   Return the URL of the sync job.
        
        Note: This currently returns the connection's job history URL, as there is no direct URL
        to a specific job in the Airbyte Cloud web app.
        
        TODO: Implement a direct job logs URL on top of the event-id of the specific attempt number.
              E.g. \{self.connection.job_history_url\}?eventId=\{event-guid\}&openLogs=true

    `records_synced: int`
    :   Return the number of records processed.

    `start_time: datetime`
    :   Return the start time of the sync job in UTC.

    `stream_names: list[str]`
    :   Return the set of stream names.

    `streams: _SyncResultStreams`
    :   Return a mapping of stream names to `airbyte.CachedDataset` objects.
        
        This is a convenience wrapper around the `stream_names`
        property and `get_dataset()` method.

    `table_name_prefix: str`
    :

    `table_name_suffix: str`
    :

    `workspace: CloudWorkspace`
    :

    ### Methods

    `get_attempts(self) ‑> list[airbyte.cloud.sync_results.SyncAttempt]`
    :   Return a list of attempts for this sync job.

    `get_dataset(self, stream_name: str) ‑> airbyte.datasets._sql.CachedDataset`
    :   Retrieve an `airbyte.datasets.CachedDataset` object for a given stream name.
        
        This can be used to read and analyze the data in a SQL-based destination.
        
        TODO: In a future iteration, we can consider providing stream configuration information
              (catalog information) to the `CachedDataset` object via the "Get stream properties"
              API: https://reference.airbyte.com/reference/getstreamproperties

    `get_job_status(self) ‑> JobStatusEnum`
    :   Check if the sync job is still running.

    `get_sql_cache(self) ‑> CacheBase`
    :   Return a SQL Cache object for working with the data in a SQL-based destination's.

    `get_sql_database_name(self) ‑> str`
    :   Return the SQL database name.

    `get_sql_engine(self) ‑> sqlalchemy.engine.Engine`
    :   Return a SQL Engine for querying a SQL-based destination.

    `get_sql_schema_name(self) ‑> str`
    :   Return the SQL schema name.

    `get_sql_table(self, stream_name: str) ‑> sqlalchemy.Table`
    :   Return a SQLAlchemy table object for the named stream.

    `get_sql_table_name(self, stream_name: str) ‑> str`
    :   Return the SQL table name of the named stream.

    `is_job_complete(self) ‑> bool`
    :   Check if the sync job is complete.

    `raise_failure_status(self, *, refresh_status: bool = False) ‑> None`
    :   Raise an exception if the sync job failed.
        
        By default, this method will use the latest status available. If you want to refresh the
        status before checking for failure, set `refresh_status=True`. If the job has failed, this
        method will raise a `AirbyteConnectionSyncError`.
        
        Otherwise, do nothing.

    `wait_for_completion(self, *, wait_timeout: int = 1800, raise_timeout: bool = True, raise_failure: bool = False) ‑> JobStatusEnum`
    :   Wait for a job to finish running.