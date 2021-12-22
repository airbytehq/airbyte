
# ClickHouse

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | Yes |  |
| Namespaces | Yes |  |

#### Output Schema

Each stream will be output into its own table in ClickHouse. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in ClickHouse is `String`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in ClickHouse is `DateTime64`.
* `_airbyte_data`: a json blob representing with the event data. The column type in ClickHouse is `String`.

## Getting Started \(Airbyte Cloud\)

Airbyte Cloud only supports connecting to your ClickHouse instance with SSL or TLS encryption, which is supported by [ClickHouse JDBC driver](https://github.com/ClickHouse/clickhouse-jdbc).

## Getting Started \(Airbyte Open-Source\)

#### Requirements

To use the ClickHouse destination, you'll need:

* A ClickHouse server version 21.8.10.19 or above

#### Configure Network Access

Make sure your ClickHouse database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a ClickHouse user with the following permissions:

* can create tables and write rows.
* can create databases e.g:

You can create such a user by running:

```
GRANT CREATE ON * TO airbyte_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the ClickHouse Destination in Airbyte

You should now have all the requirements needed to configure ClickHouse as a destination in the UI. You'll need the following information to configure the ClickHouse destination:

* **Host**
* **Port** (JDBC HTTP port, not the native port)
* **Username**
* **Password**
* **Database**

## Naming Conventions

From [ClickHouse SQL Identifiers syntax](https://clickhouse.com/docs/en/sql-reference/syntax/):

* SQL identifiers and key words must begin with a letter \(a-z, but also letters with diacritical marks and non-Latin letters\) or an underscore \(\_\).
* Subsequent characters in an identifier or key word can be letters, underscores, digits \(0-9\).
* Identifiers can be quoted or non-quoted. The latter is preferred.
* If you want to use identifiers the same as keywords or you want to use other symbols in identifiers, quote it using double quotes or backticks, for example, "id", `id`.
* If you want to write portable applications you are advised to always quote a particular name or never quote it.

Therefore, Airbyte ClickHouse destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names are containing special characters.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.1 | 2021-12-21 | [\#8982](https://github.com/airbytehq/airbyte/pull/8982) | Set isSchemaRequired to false |
| 0.1.0 | 2021-11-04 | [\#7620](https://github.com/airbytehq/airbyte/pull/7620) | Add ClickHouse destination |

