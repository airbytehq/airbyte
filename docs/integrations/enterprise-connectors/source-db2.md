---
dockerRepository: airbyte/source-db2
---
# Source Db2

## Features

| Feature                       | Supported | Notes |
| :---------------------------- |:----------|:------|
| Full Refresh Sync             | Yes       |       |
| Incremental Sync - Append     | Yes       |       |
| Replicate Incremental Deletes | No        |       |
| Change Data Capture (CDC)     | No        |       |
| SSL Support                   | No        |       |
| SSH Tunnel Connection         | No        |       |
| Namespaces                    | Yes       |       |

From the point of view of the Db2 database instance, the Enterprise Db2 source operates strictly in a read-only fashion.

## Getting Started

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect
to your Db2 instance is by testing the connection in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables

This step is optional but highly recommended to allow for better permission control and auditing.
Alternatively, you can use Airbyte with an existing user in your database.

## Data type mapping

Db2 data types are mapped to the following data types when synchronizing data.

| Oracle Type              | Airbyte Type               | Notes                                      |
|:-------------------------|:---------------------------|:-------------------------------------------|
| `SMALLINT`               | integer                    |                                            |
| `INT`                    | integer                    |                                            |
| `INTEGER`                | integer                    |                                            |
| `BIGINT`                 | integer                    |                                            |
| `DECIMAL`                | number/integer             | if scale is 0, use integer                 |
| `DEC`                    | number/integer             | if scale is 0, use integer                 |
| `NUMERIC`                | number/integer             | if scale is 0, use integer                 |
| `REAL`                   | number                     |                                            |
| `FLOAT`                  | number                     |                                            |
| `DOUBLE`                 | number                     |                                            |
| `DOUBLE PRECISION`       | number                     |                                            |
| `DECFLOAT`               | number                     | INF, -INF, and NaN values will map to null |
| `CHAR`                   | string                     |                                            |
| `CHARACTER`              | string                     |                                            |
| `VARCHAR`                | string                     |                                            |
| `CHARACTER VARYING`      | string                     |                                            |
| `CHAR VARYING`           | string                     |                                            |
| `CLOB`                   | string                     |                                            |
| `CHARACTER LARGE OBJECT` | string                     |                                            |
| `CHAR LARGE OBJECT`      | string                     |                                            |
| `BLOB`                   | binary                     |                                            |
| `BINARY LARGE OBJECT`    | binary                     |                                            |
| `BINARY`                 | binary                     |                                            |
| `VARBINARY`              | binary                     |                                            |
| `BINARY VARYING`         | binary                     |                                            |
| `DATE`                   | date                       |                                            |
| `TIME`                   | time without timezone      |                                            |
| `TIMESTAMP`              | timestamp without timezone |                                            |
| `BOOLEAN`                | boolean                    |                                            |
| `XML`                    | xml                        |                                            |


## Changelog

<details>
  <summary>Expand to review</summary>

The connector is still incubating, this section only exists to satisfy Airbyte's QA checks.

- 0.0.1

</details>
