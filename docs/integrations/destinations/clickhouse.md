
# ClickHouse

## Features

| Feature                       | Supported?\(Yes/No\) | Notes |
|:------------------------------|:---------------------|:------|
| Full Refresh Sync             | Yes                  |       |
| Incremental - Append Sync     | Yes                  |       |
| Incremental - Deduped History | Yes                  |       |
| Namespaces                    | Yes                  |       |

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
* **Port**
* **Username**
* **Password**
* **Database**
* **Jdbc_url_params**

## Naming Conventions

From [ClickHouse SQL Identifiers syntax](https://clickhouse.com/docs/en/sql-reference/syntax/):

* SQL identifiers and key words must begin with a letter \(a-z, but also letters with diacritical marks and non-Latin letters\) or an underscore \(\_\).
* Subsequent characters in an identifier or key word can be letters, underscores, digits \(0-9\).
* Identifiers can be quoted or non-quoted. The latter is preferred.
* If you want to use identifiers the same as keywords or you want to use other symbols in identifiers, quote it using double quotes or backticks, for example, "id", `id`.
* If you want to write portable applications you are advised to always quote a particular name or never quote it.

Therefore, Airbyte ClickHouse destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names are containing special characters.

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                             |
|:--------|:-----------|:-----------------------------------------------------------|:--------------------------------------------------------------------|
| 0.2.4   | 2023-06-05 | [\#27036](https://github.com/airbytehq/airbyte/pull/27036) | Internal code change for future development (install normalization packages inside connector) |
| 0.2.3   | 2023-04-04 | [\#24604](https://github.com/airbytehq/airbyte/pull/24604) | Support for destination checkpointing                               |
| 0.2.2   | 2023-02-21 | [\#21509](https://github.com/airbytehq/airbyte/pull/21509) | Compatibility update with security patch for strict encrypt version |
| 0.2.1   | 2022-12-06 | [\#19573](https://github.com/airbytehq/airbyte/pull/19573) | Update dbt version to 1.3.1                                         |
| 0.2.0   | 2022-09-27 | [\#16970](https://github.com/airbytehq/airbyte/pull/16970) | Remove TCP port from spec parameters                                |
| 0.1.12  | 2022-09-08 | [\#16444](https://github.com/airbytehq/airbyte/pull/16444) | Added custom jdbc params field                                      |
| 0.1.10  | 2022-07-05 | [\#13639](https://github.com/airbytehq/airbyte/pull/13639) | Change JDBC ClickHouse version into 0.3.2-patch9                    |
| 0.1.8   | 2022-07-05 | [\#13516](https://github.com/airbytehq/airbyte/pull/13516) | Added JDBC default parameter socket timeout                         |
| 0.1.7   | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852) | Updated stacktrace format for any trace message errors              |
| 0.1.6   | 2022-05-17 | [\#12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                              |
| 0.1.5   | 2022-04-06 | [\#11729](https://github.com/airbytehq/airbyte/pull/11729) | Bump mina-sshd from 2.7.0 to 2.8.0                                  |
| 0.1.4   | 2022-02-25 | [\#10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling                                   |
| 0.1.3   | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                        |
| 0.1.1   | 2021-12-21 | [\#8982](https://github.com/airbytehq/airbyte/pull/8982)   | Set isSchemaRequired to false                                       |
| 0.1.0   | 2021-11-04 | [\#7620](https://github.com/airbytehq/airbyte/pull/7620)   | Add ClickHouse destination                                          |
