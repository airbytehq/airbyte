# Databend

This page guides you through the process of setting up the [Databend](https://databend.rs/) destination connector.

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |


#### Output Schema

Each stream will be output into its own table in Databend. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Databend is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Databend is `TIMESTAMP`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Databend is `VARVHAR`.
## Getting Started (Airbyte Cloud)
Coming soon...

## Getting Started (Airbyte Open-Source)
You can follow the [Connecting to a Warehouse docs](https://docs.databend.com/using-databend-cloud/warehouses/connecting-a-warehouse) to get the user, password, host etc.

Or you can create such a user by running:

```
GRANT CREATE ON * TO airbyte_user;
```

Make sure the Databend user with the following permissions:

* can create tables and write rows.
* can create databases e.g:

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.


#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the Databend Destination in Airbyte

You should now have all the requirements needed to configure Databend as a destination in the UI. You'll need the following information to configure the Databend destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Database**


## Changelog

| Version | Date       | Pull Request                                             | Subject                                  |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------|
| 0.1.1   | 2022-01-09 | [21182](https://github.com/airbytehq/airbyte/pull/21182)   | Remove protocol option and enforce HTTPS |
| 0.1.0   | 2022-01-09 | [20909](https://github.com/airbytehq/airbyte/pull/20909)   | Destination Databend                     |

