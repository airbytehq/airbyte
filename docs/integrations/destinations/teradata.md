# Teradata

This page guides you through the process of setting up the Teradata destination connector.

## Prerequisites

To use the Teradata destination, you'll need:

* A Teradata database version 17.00 or above

You'll need the following information to configure the Teradata destination:

* **Host** - The host name of the Teradata database server.
* **Username**
* **Password**
* **Default Schema Name** - Specify the schema (or several schemas separated by commas) to be set in the search-path. These schemas will be used to resolve unqualified object names used in statements executed over this connection.
* **JDBC URL Params** (optional)

[Refer to this guide for more details](https://downloads.teradata.com/doc/connectivity/jdbc/reference/current/jdbcug_chapter_2.html#BGBHDDGB)

## Sync overview

### Output schema

Each stream will be output into its own table in Teradata. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Teradata is `VARCHAR(256)`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Teradata is `TIMESTAMP(6)`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Teradata is `JSON`.


### Features

The Teradata destination connector supports the
following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):


| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | Yes |  |
| Namespaces | Yes |  |

### Performance considerations

## Getting started

### Requirements

You need a Teradata user with the following permissions:

* can create tables and write rows.
* can create schemas e.g:

You can create such a user by running:

```
CREATE USER airbyte_user  as perm=10e6, PASSWORD=<password>;
GRANT ALL on dbc to airbyte_user;

```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.
### Setup guide

#### Set up the Teradata Destination connector

1. Log into your Airbyte Open Source account.
2. Click **Destinations** and then click **+ New destination**.
3. On the Set up the destination page, select **Teradata** from the **Destination type** dropdown.
4. Enter the **Name** for the Teradata connector.
5. For **Host**, enter the host domain of the Teradata instance
6. For **Default Schema**, enter the Default Schema name. The default value is public.
7. For **User** and **Password**, enter the database username and password.
8. To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://downloads.teradata.com/doc/connectivity/jdbc/reference/current/jdbcug_chapter_2.html#BGBHDDGB) as key-value pairs separated by the symbol & in the **JDBC URL Params** field.

   Example: key1=value1&key2=value2&key3=value3

   These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Teradata database.