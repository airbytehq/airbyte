# SelectDB

destination-selectdb is a destination implemented based on [SelectDB copy into ](https://cn.selectdb.com/docs/%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97/%E6%95%B0%E6%8D%AE%E5%AF%BC%E5%85%A5#copy-into), supports batch rollback, and uses http/https put request

## Sync overview

### Output schema

Each stream will be output into its own table in SelectDB. Each table will contain 3 columns:

- `_airbyte_ab_id`: an uuid assigned by Airbyte to each event that is processed. The column type in Doris is `VARCHAR(40)`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Doris is `BIGINT`.
- `_airbyte_data`: a json blob representing with the event data. The column type in SelectDB is `String`.

### Features

This section should contain a table with the following format:

| Feature                                | Supported?(Yes/No) | Notes |
| :------------------------------------- | :----------------- | :---- |
| Full Refresh Sync                      | Yes                |       |
| Incremental - Append Sync              | Yes                |       |
| Incremental - Append + Deduped         | No                 |       |
| For databases, WAL/Logical replication | Yes                |       |

### Performance considerations

Batch writes are performed. mini records may impact performance.
Importing multiple tables will generate multiple transactions, which should be split as much as possible.

## Getting started

### Requirements

To use the SelectDB destination, you'll need:

- A SelectDB server and your
- Make sure your SelectDB http port and mysql query port can be accessed by Airbyte.
- Make sure your SelectDB host can be accessed by Airbyte. if use a public network to access SelectDB, please ensure that your airbyte public network IP is in the ip whitelist of your SelectDB.
- Make sure your SelectDB user with read/write permissions on certain tables.

### Target Database and tables

You will need to choose a database that will be used to store synced data from Airbyte.
You need to prepare database that will be used to store synced data from Airbyte, and ensure the order and matching of the column names in the table as much as possible.

### Setup the access parameters

- **loadURL**
- **jdbcURL**
- **clustername**
- **username**
- **password**
- **database**

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                              |
| :------ | :--------- | :--------------------------------------------------------- | :----------------------------------- |
| 0.1.0   | 2023-04-03 | [\#20881](https://github.com/airbytehq/airbyte/pull/20881) | Initial release SelectDB Destination |

</details>