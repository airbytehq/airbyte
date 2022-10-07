# bit.io

This page guides you through the process of setting up the bit.io destination connector.

The bit.io connector is a modified version of the Postgres connector.

## Prerequisites

To use the bit.io destination, you'll need:

* A bit.io account

You'll need the following information to configure the bit.io destination:

* **Username**
* **Connect Password** - Found on your database page on the `Connect` tab (this is NOT your bit.io login password)
* **Database** - The database name, including your username - eg, `adam/FCC`. 


## Supported sync modes

The bit.io destination connector supports the
following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | Yes |  |
| Namespaces | Yes |  |

## Schema map

#### Output Schema

Each stream will be mapped to a separate table in bit.io. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Postgres is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Postgres is `TIMESTAMP WITH TIME ZONE`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Postgres
  is `JSONB`.



## Changelog

| Version | Date       | Pull Request | Subject                                                                                             |
|:--------|:-----------| :--- |:----------------------------------------------------------------------------------------------------|
| 0.1.0  | 2022-08-20 | | Initial Version
