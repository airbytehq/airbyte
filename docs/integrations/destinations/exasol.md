# Exasol

Exasol is the in-memory database built for analytics.

## Sync overview

### Output schema

Exasol tables become Airbyte Streams and Exasol columns become Airbyte Fields. Each table will contain 3 columns:

* `_AIRBYTE_AB_ID`: a uuid assigned by Airbyte to each event that is processed. The column type in Exasol is `VARCHAR(64)`.
* `_AIRBYTE_DATA`: a json blob representing with the event data. The column type in Exasol is `VARCHAR(2000000)`.
* `_AIRBYTE_EMITTED_AT`: a timestamp representing when the event was pulled from the data source. The column type in Exasol is `TIMESTAMP`.


### Data type mapping

This section should contain a table mapping each of the connector's data types to Airbyte types. At the moment, Airbyte uses the same types used by [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html). `string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number` are the most commonly used data types.

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |


### Features

This section should contain a table with the following format:

| Feature | Supported? (Yes/No) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync |  |  |
| Incremental Sync |  |  |
| Replicate Incremental Deletes |  |  |
| For databases, WAL/Logical replication |  |  |
| SSL connection | Yes | TLS |
| SSH Tunnel Support | No |  |

### Performance considerations

## Getting started

### Requirements

To use the Exasol destination, you'll need Exasol database version 7.1 or above.

#### Network Access

Make sure your Exasol database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

As Airbyte namespaces allow to store data into different schemas, we have different scenarios each with specific required permissions:

| Login user | Destination user | Required permissions | Comment |
| :--- | :--- | :--- | :--- |
| DBA User | Any user | - |  |
| Regular user | Same user as login | Create, drop and write table, create session |  |
| Regular user | Any existing user | Create, drop and write ANY table, create session | Grants can be provided on a system level by DBA or by target user directly |
| Regular user | Not existing user | Create, drop and write ANY table, create user, create session | Grants should be provided on a system level by DBA |

We highly recommend creating an Airbyte-specific user for this purpose.

### Setup guide

For each of the above high-level requirements as appropriate, add or point to a follow-along guide. See existing source or destination guides for an example.

For each major cloud provider we support, also add a follow-along guide for setting up Airbyte to connect to that destination. See the Postgres destination guide for an example of what this should look like.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------|
| 0.1.0   | 2023-01-?? | [21200](https://github.com/airbytehq/airbyte/pull/21200) | Initial version of the Exasol destination |
