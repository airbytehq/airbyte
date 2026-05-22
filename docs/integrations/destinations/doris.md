# Doris

destination-doris is a destination implemented based on [Apache Doris stream load](https://doris.apache.org/docs/dev/data-operate/import/import-way/stream-load-manual), supports batch rollback, and uses http/https put request

## Sync overview

### Output schema

Each stream will be output into its own table in Doris. Each table will contain 3 columns:

- `_airbyte_ab_id`: an uuid assigned by Airbyte to each event that is processed. The column type in Doris is `VARCHAR(40)`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Doris is `BIGINT`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Doris is `String`.

### Features

This section should contain a table with the following format:

| Feature                                | Supported?(Yes/No) | Notes                    |
| :------------------------------------- | :----------------- | :----------------------- |
| Full Refresh Sync                      | Yes                |                          |
| Incremental - Append Sync              | Yes                |                          |
| Incremental - Append + Deduped         | No                 | it will soon be realized |
| For databases, WAL/Logical replication | Yes                |                          |

### Performance considerations

Batch writes are performed. mini records may impact performance.
Importing multiple tables will generate multiple [Doris stream load](https://doris.apache.org/docs/dev/data-operate/import/import-way/stream-load-manual) transactions, which should be split as much as possible.

## Getting started

### Requirements

To use the Doris destination, you'll need:

- A Doris server version 0.14 or above
- Make sure your Doris fe http port can be accessed by Airbyte.
- Make sure your Doris database host can be accessed by Airbyte.
- Make sure your Doris user with read/write permissions on certain tables.

### Target Database and tables

You will need to choose a database that will be used to store synced data from Airbyte.
You need to prepare tables that will be used to store synced data from Airbyte, and ensure the order and matching of the column names in the table as much as possible.

### Setup the access parameters

- **Host**
- **HttpPort**
- **QueryPort**
- **Username**
- **Password**
- **Database**

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-11-14 | [17884](https://github.com/airbytehq/airbyte/pull/17884) | Initial Commit |

</details>