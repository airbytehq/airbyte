# Doris

destination-doris is a destination implemented based on [Doris stream load](https://doris.apache.org/docs/dev/data-operate/import/import-way/stream-load-manual), supports batch rollback, and uses http/https put request

## Sync overview

### Output schema

Each stream will be output into its own table in Doris, Each table columns depends on the stream's JsonSchema, therefore, the output schema written depends on the parsing of the column by the stream.
If the column names are the same, this process does not need to manually specify the comparison order, nor does it need to build '_airbyte_ab_id','_airbyte_emitted_at','_airbyte_data' columns in doris table to store the result data.

### Features

This section should contain a table with the following format:

| Feature | Supported?(Yes/No) | Notes |
| :--- |:-------------------| :--- |
| Full Refresh Sync | Yes                |  |
| Incremental Sync | Yes                |  |
| Replicate Incremental Deletes | No                 | it will soon be realized |
| For databases, WAL/Logical replication | Yes                |  |

### Performance considerations

Batch writes are performed. mini records may impact performance.  
Importing multiple tables will generate multiple [Doris stream load](https://doris.apache.org/docs/dev/data-operate/import/import-way/stream-load-manual) transactions, which should be split as much as possible.

## Getting started

### Requirements

To use the Doris destination, you'll need:
* A Doris server version 0.14 or above
* Make sure your Doris fe http port can be accessed by Airbyte.
* Make sure your Doris database host can be accessed by Airbyte.
* Make sure your Doris user with read/write permissions on certain tables.

### Target Database and tables
You will need to choose a database that will be used to store synced data from Airbyte.
You need to prepare tables that will be used to store synced data from Airbyte, and ensure the order and matching of the column names in the table as much as possible.

### Setup the access parameters
* **Host**
* **Port**
* **Username**
* **Password**
* **Database**
