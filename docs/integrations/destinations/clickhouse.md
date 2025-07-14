# ClickHouse

A fresh implementation of ClickHouse leveraging our new CDK. 

## Improvements over v1
* All sync modes supported
* Data will be typed and written to columns matching the defined schema (Direct Load)
* Performance improvements
* Actively maintained and developed by Airbyte

## Features

All sync modes are supported.

| Feature                        | Supported?\(Yes/No\) | Notes                          |
| :----------------------------- |:---------------------|:-------------------------------|
| Full Refresh Sync              | Yes                  |                                |
| Incremental - Append Sync      | Yes                  |                                |
| Incremental - Append + Deduped | Yes                  | Leverages `ReplacingMergeTree` |
| Namespaces                     | Yes                  |                                |

### Output Schema

Each stream will be output into its own table in ClickHouse in either the configured default database (`default`) or a database corresponding to the specified namespace on the stream.

Airbyte types will be converted to ClickHouse types as follows:

- Decimal types are NUMBER128(9) — 9 digit precision
- Timestamp are DateTime64(3) — millisecond precision
- Object types are JSON **if JSON is enabled in the actor config**; otherwise they are converted to String
- Integers are Int64
- Booleans are Bool
- Strings are String
- Unions will be converted to String
- Arrays will be converted to String

### Requirements

To use the ClickHouse destination, you'll need:

- A cloud ClickHouse instance
- A ClickHouse server version 21.8.10.19 or above

### Configure Network Access

Make sure your ClickHouse database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

### **Permissions**

You need a ClickHouse user with the following permissions:

- can create tables and write rows.
- can create databases
- can alter, drop and exchange tables

You can create such a user by running the following:

```
GRANT CREATE ON * TO airbyte_user;
GRANT DROP ON * TO airbyte_user;
GRANT CREATE ON {database}.* TO airbyte_user;
GRANT DROP ON {database}.* TO airbyte_user;
GRANT ALTER ON {database}.* TO airbyte_user;
GRANT TRUNCATE ON {database}.* TO airbyte_user;
GRANT INSERT ON {database}.* TO airbyte_user;
GRANT SELECT ON {database}.* TO airbyte_user;
GRANT CREATE DATABASE ON {database}.* TO airbyte_user;
GRANT CREATE TABLE ON {database}.* TO airbyte_user;
```

Where `{database}` is the database configured on your connector.

Then for each connection using this connector with a custom namespace, run:

```
GRANT CREATE ON {namespace}.* TO airbyte_user;
GRANT DROP ON {namespace}.* TO airbyte_user;
GRANT ALTER ON {namespace}.* TO airbyte_user;
GRANT TRUNCATE ON {namespace}.* TO airbyte_user;
GRANT INSERT ON {namespace}.* TO airbyte_user;
GRANT SELECT ON {namespace}.* TO airbyte_user;
GRANT CREATE DATABASE ON {namespace}.* TO airbyte_user;
GRANT CREATE TABLE ON {namespace}.* TO airbyte_user;
```

Where `{namespace}` is the custom namespace configured for that connection.


You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                        |
|:--------|:-----------|:-----------------------------------------------------------|:-------------------------------------------------------------------------------|
| 2.0.3   | 2025-07-11 | [\#62928](https://github.com/airbytehq/airbyte/pull/62928) | Publish metadata changes.                                                      |
| 2.0.2   | 2025-07-10 | [\#62928](https://github.com/airbytehq/airbyte/pull/62928) | Makes json optional in spec to work around UI issue.                           |
| 2.0.1   | 2025-07-10 | [\#62906](https://github.com/airbytehq/airbyte/pull/62906) | Adds bespoke validation for legacy hostnames that contain a protocol.          |
| 2.0.0   | 2025-07-10 | [\#62887](https://github.com/airbytehq/airbyte/pull/62887) | Cut 2.0.0 release. Replace existing connector.                                 |
| 0.1.11  | 2025-07-09 | [\#62883](https://github.com/airbytehq/airbyte/pull/62883) | Only set JSON properties on client if enabled to support older CH deployments. |
| 0.1.10  | 2025-07-08 | [\#62861](https://github.com/airbytehq/airbyte/pull/62861) | Set user agent header for internal CH telemetry.                               |
| 0.1.9   | 2025-07-03 | [\#62509](https://github.com/airbytehq/airbyte/pull/62509) | Simplify union stringification behavior.                                       |
| 0.1.8   | 2025-06-30 | [\#62100](https://github.com/airbytehq/airbyte/pull/62100) | Add JSON support.                                                              |
| 0.1.7   | 2025-06-24 | [\#62047](https://github.com/airbytehq/airbyte/pull/62047) | Remove the use of the internal namespace.                                      |
| 0.1.6   | 2025-06-24 | [\#62047](https://github.com/airbytehq/airbyte/pull/62047) | Hide protocol option when running on cloud.                                    |
| 0.1.5   | 2025-06-24 | [\#62043](https://github.com/airbytehq/airbyte/pull/62043) | Expose database protocol config option.                                        |
| 0.1.4   | 2025-06-24 | [\#62040](https://github.com/airbytehq/airbyte/pull/62040) | Checker inserts into configured DB.                                            |
| 0.1.3   | 2025-06-24 | [\#62038](https://github.com/airbytehq/airbyte/pull/62038) | Allow the client to connect to the resolved DB.                                |
| 0.1.2   | 2025-06-23 | [\#62028](https://github.com/airbytehq/airbyte/pull/62028) | Enable the registry in OSS and cloud.                                          |
| 0.1.1   | 2025-06-23 | [\#62022](https://github.com/airbytehq/airbyte/pull/62022) | Publish first beta version and pin the CDK version.                            |
| 0.1.0   | 2025-06-23 | [\#62024](https://github.com/airbytehq/airbyte/pull/62024) | Release first beta version.                                                    |
</details>
