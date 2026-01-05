---
sidebar_label: cloud
title: airbyte.cloud
---

PyAirbyte classes and methods for interacting with the Airbyte Cloud API.

You can use this module to interact with Airbyte Cloud, OSS, and Enterprise.

## Examples

### Basic Sync Example:


### Example Read From Cloud Destination:

If your destination is supported, you can read records directly from the
`SyncResult` object. Currently this is supported in Snowflake and BigQuery only.


```python
import airbyte as ab
from airbyte import cloud

# Initialize an Airbyte Cloud workspace object
workspace = cloud.CloudWorkspace(
    workspace_id="123",
    api_key=ab.get_secret("AIRBYTE_CLOUD_API_KEY"),
)

# Run a sync job on Airbyte Cloud
connection = workspace.get_connection(connection_id="456")
sync_result = connection.run_sync()
print(sync_result.get_job_status())
```
```python
# Assuming we've already created a `connection` object...

# Get the latest job result and print the stream names
sync_result = connection.get_sync_result()
print(sync_result.stream_names)

# Get a dataset from the sync result
dataset: CachedDataset = sync_result.get_dataset("users")

# Get a SQLAlchemy table to use in SQL queries...
users_table = dataset.to_sql_table()
print(f"Table name: {users_table.name}")

# Or iterate over the dataset directly
for record in dataset:
    print(record)
```

## annotations

## TYPE\_CHECKING

## CloudClientConfig

## CloudConnection

## JobStatusEnum

## SyncResult

## CloudWorkspace

#### \_\_all\_\_

