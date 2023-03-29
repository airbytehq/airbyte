# StarRocks

The destination-starrocks is a destination implemented based on [StarRocks stream load](https://docs.starrocks.io/en-us/latest/loading/StreamLoad), uses http put request

## Sync overview

### Output schema

Each stream will be output into its own table in StarRocks. Each table will contain 3 columns:

- `_airbyte_ab_id`: an uuid assigned by Airbyte to each event that is processed. The column type in StarRocks is `VARCHAR(40)`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in StarRocks is `BIGINT`.
- `_airbyte_data`: a json blob representing with the event data. The column type in StarRocks is `String`.

### Features

This section should contain a table with the following format:

| Feature                                | Supported?(Yes/No) | Notes |
| :------------------------------------- | :----------------- |:------|
| Full Refresh Sync                      | Yes                |       |
| Incremental - Append Sync              | Yes                |       |
| Incremental - Deduped History          | No                 |       |

### Performance considerations

Batch writes are performed. mini records may impact performance.

## Getting started

### Requirements

To use the StarRocks destination, you'll need:

- A StarRocks server version 2.0 or above
- Make sure your StarRocks fe http port can be accessed by Airbyte.
- Make sure your StarRocks database host can be accessed by Airbyte.
- Make sure your StarRocks user with read/write permissions on certain tables.

### Target Database and tables

You will need to choose a database that will be used to store synced data from Airbyte.
You need to prepare tables that will be used to store synced data from Airbyte, and ensure the order and matching of the column names in the table as much as possible.

### Setup the access parameters

- **FeHost**
- **HttpPort**
- **QueryPort**
- **Username**
- **Password**
- **Database**

