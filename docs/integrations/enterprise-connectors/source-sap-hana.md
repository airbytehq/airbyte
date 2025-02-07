# Source SAP HANA

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for 
Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team, 
provide enhanced capabilities and support for critical enterprise systems. 
To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

Airbyte’s incubating SAP HANA enterprise source connector currently offers Full Refresh and Incrementals syncs for streams. Support for Change Data Capture (CDC) is currently in-development and will be available soon.

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync - Append | Yes          |       |
| Incremental Sync - Append | Yes          |       |              
| Changa Data Capture (CDC) | No           |       |


## Prequisities

- Dedicated read-only Airbyte user with read-only access to tables needed for replication
- SAP HANA Host Name URL
  - In the SAP HANA Cloud Management Portal, this can be found under the **Connections** tab for you SAP HANA instance
  - The Host Name  is the first portion of the SQL Endpoint before the Port
  - ie:**01234abce-1234-56fg.us-01-hanacloud.ondemand.com**:123
  - The **Host** is also a combination of the **Instance ID** and **Landscape**
- Port Number
  - Inside of the SAP HANA Cloud Management Portal, this can be found under the **Connections** tab for you SAP HANA instance
  - The **Port** is listed explicitly in addition to being part of the **SQL Endpoint**
 
## Setup Guide

1. Enter your SAP HANA Host Name
2. Enter the Port number
3. Provide the login credentials for the SAP HANA account with access to the tables
4. Specify the schemas for tables that you would like to replicate
5. Select  either Full Refresh or Incremental for your desired Sync Type

## Data type mapping

SAP HANA data types are mapped to the following Airbyte data types when synchronizing data.

| SAP HANA Type  | Airbyte Type               | Notes |
| -------------- | -------------------------- | ----- |
| `BOOLEAN`      | BOOLEAN                    |       |
| `DOUBLE`       | NUMBER                     |       |
| `FLOAT`        | NUMBER                     |       |
| `REAL`         | NUMBER                     |       |
| `SMALLDECIMAL` | NUMBER                     |       |
| `DECIMAL`      | NUMBER                     |       |
| `DEC`          | NUMBER                     |       |
| `INTEGER`      | INTEGER                    |       |
| `TINYINT`      | INTEGER                    |       |
| `SMALLINT`     | INTEGER                    |       |
| `BIGINT`       | INTEGER                    |       |
| `CHAR`         | STRING                     |       |
| `VARCHAR`      | STRING                     |       |
| `ALPHANUM`     | STRING                     |       |
| `NCHAR`        | STRING                     |       |
| `NVARCHAR`     | STRING                     |       |
| `SHORTTEXT`    | STRING                     |       |
| `TIME`         | TIME_WITHOUT_TIMEZONE      |       |
| `DATE`         | DATE                       |       |
| `SECONDDATE`   | TIMESTAMP_WITHOUT_TIMEZONE |       |
| `TIMESTAMP`    | TIMESTAMP_WITHOUT_TIMEZONE |       |
| `BINARY`       | BINARY                     |       |
| `VARBINARY`    | BINARY                     |       |
| `REAL_VECTOR`  | BINARY                     |       |
| `BLOB`         | BINARY                     |       |
| `CLOB`         | STRING                     |       |
| `NCLOB`        | STRING                     |       |
| `TEXT`         | STRING                     |       |
| `BINTEXT`      | STRING                     |       |
| `ST_POINT`     | BINARY                     |       |
| `ST_GEOMETRY`  | BINARY                     |


