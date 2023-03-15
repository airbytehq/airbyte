# Bytehouse


## Sync overview

### Output schema

#### Output Schema

Each stream will be output into its own table in ByteHouse. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in ByteHouse is `String`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in ByteHouse is `DateTime64`.
* `_airbyte_data`: a json blob representing with the event data. The column type in ByteHouse is `String`.

### Features

This section should contain a table with the following format:

| Feature | Supported?(Yes/No) | Notes |
| :--- |:-------------------| :--- |
| Full Refresh Sync | Yes                |  |
| Incremental Sync | Yes                |  |
| SSL connection | Yes                |  |

## Getting started

### Requirements

To use the ByteHouse destination, you'll need:

* ByteHouse 1.15.0 and above
* A user with permission to create tables, read & write rows to involved tables.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the ByteHouse Destination in Airbyte

You should now have all the requirements needed to configure ByteHouse as a destination in the UI. You'll need the following information to configure the ClickHouse destination:

* **Host**
* **Port**
* **Account**
* **Username**
* **Password**
* **Database**
* **Jdbc_url_params**
