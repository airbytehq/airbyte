# SingleStore

## Overview

[SingleStore](https://www.singlestore.com/) is a distributed SQL database that offers
high-throughput transactions (inserts and upserts), low-latency analytics and context from real-time
vector data

:::info
Airbyte SingleStore destination is implemented as Destination V2
with [Typing and Deduping](https://docs.airbyte.com/using-airbyte/core-concepts/typing-deduping) support. Legacy V1 is
not supported.
:::

## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
|:-------------------------------|:---------------------|:------|
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |
| Namespaces                     | Yes                  |       |

## Getting Started

#### Requirements

1. SingleStore instance
2. Allow connections from Airbyte to your SingleStore database \(if they exist in separate VPCs\) 
3. Create a dedicated Airbyte user with the minimum required permissions to CRUD tables and CREATE/EXECUTE functions

Here is an example of an SQL query to grant minimum required permissions for an Airbyte user:

```sql
CREATE USER airbyte IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, EXECUTE, CREATE ROUTINE, ALTER ROUTINE, CREATE DATABASE ON db.* TO 'airbyte'@'%';
```

4. Before setting up SingleStore destination in Airbyte, you need to set the 'local_infile' system variable to true. You
   can do this by running the query `SET GLOBAL local_infile = true`. This is required cause Airbyte
   uses `LOAD DATA LOCAL INFILE` to load data into raw table.

You'll need the following information to configure the SingleStore destination:

- **Host** - The host name of the server.
- **Port** - The port number the server is listening on. Defaults to the standard port
  number (3306).
- **Username**
- **Password**
- **Database** - The database name.
- **JDBC URL Params** (optional)

## Schema map

### Raw table

Each data stream will be associated with its own raw table within SingleStore. By default, these raw tables are created
within the default namespace specified by the `database` parameter. However, this default behavior can be overridden by
configuring the `raw_data_schema` parameter.

:::warning

It is advisable to use the same database for both the raw table and the final table in the SingleStore connector.
This recommendation stems from the fact that SingleStore does not support cross-database transactions.
Therefore, maintaining consistency within the same database ensures smoother data operations and transaction management.

:::

Raw table schema:

- `_airbyte_raw_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  SingleStore is `VARCHAR(256)`.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in SingleStore is `TIMESTAMP(6)`.
- `_airbyte_loaded_at`: a timestamp representing when the row was processed into final table. The
  column type in SingleStore is `TIMESTAMP(6)`.
- `_airbyte_data`: a json representing with the event data. The
  column type in SingleStore is `JSON`.

### Final table

After the data stream has been processed and stored in the raw table, the subsequent step involves parsing and
normalizing
the data to the final destination table. During this normalization process, the connector is equipped to handle data
casting errors efficiently.
Any encountered casting errors are tracked and recorded in the `_airbyte_meta` column, providing visibility into the
issues encountered during the normalization process.

Final table schema:
* `data columns`: normalized data columns from raw table _airbyte_data JSON column.
* `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source. The column type in SingleStore is TIMESTAMP(6).
* `_airbyte_meta`: column containing the warnings occurred during data normalization. 


### Final Table Data type mapping

| Airbyte Type               | SingleStore Type |
|:---------------------------|:-----------------|
| string                     | VARCHAR(21844)   |
| number                     | DECIMAL(38, 9)   |
| integer                    | BIGINT           |
| boolean                    | TINYINT(1)       |
| object                     | JSON             |
| array                      | JSON             |
| timestamp_without_timezone | TIMESTAMP(6)     |
| timestamp_with_timezone    | TIMESTAMP(6)     |
| time_without_timezone      | TIME(6)          |
| time_with_timezone         | TIME(6)          |
| date                       | DATE             |

### Naming limitations

SingleStore restricts all identifiers to 63 characters or less. If your stream includes column names
longer than 63 characters, they will be truncated to this length.

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                              |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------|
| 0.1.0   | 2024-05-23 | [38600](https://github.com/airbytehq/airbyte/pull/38600) | Implement SingleStore destination V2 |
