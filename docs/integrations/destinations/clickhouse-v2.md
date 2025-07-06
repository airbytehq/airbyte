# ClickHouse v2

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

The types we are using have the following properties:

- The decimal types have a precision of 9 digits, we are using the ClickHouse type NUMBER128(9)
- The Timestamp types have a millisecond precision, we are using the ClickHouse type DATETIME64(3)
- The object type is converted to JSON **if the JSON option is selected**; otherwise it will be a String
- The integers are Int64
- The booleans are Bool
- The strings are String
- The unions will be converted as a String
- The times will be converted to a String
- The arrays will be converted to a String


### Requirements

To use the ClickHouse destination, you'll need:

- A cloud ClickHouse instance
- A ClickHouse server version 21.8.10.19 or above

### Configure Network Access

Make sure your ClickHouse database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

### **Permissions**

You need a ClickHouse user with the following permissions:

- can create tables and write rows.
- can create databases e.g:

You can create such a user by running:

```
GRANT CREATE ON * TO airbyte_user;
GRANT CREATE ON {your configured default database} * TO airbyte_user;
GRANT DROP ON * TO airbyte_user;
GRANT TRUNCATE ON * TO airbyte_user;
GRANT INSERT ON * TO airbyte_user;
GRANT SELECT ON * TO airbyte_user;
GRANT CREATE DATABASE ON airbyte_internal.* TO airbyte_user;
GRANT CREATE TABLE ON airbyte_internal.* TO airbyte_user;
GRANT DROP ON airbyte_internal.* TO airbyte_user;
GRANT TRUNCATE ON airbyte_internal.* TO airbyte_user;
GRANT INSERT ON airbyte_internal.* TO airbyte_user;
GRANT SELECT ON airbyte_internal.* TO airbyte_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                             |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------|
| 0.1.8   | 2025-06-30 | [\#62100](https://github.com/airbytehq/airbyte/pull/62100) | Add JSON support.                                       |
| 0.1.7   | 2025-06-24 | [\#62047](https://github.com/airbytehq/airbyte/pull/62047) | Remove the use of the internal namespace.           |
| 0.1.6   | 2025-06-24 | [\#62047](https://github.com/airbytehq/airbyte/pull/62047) | Hide protocol option when running on cloud.         |
| 0.1.5   | 2025-06-24 | [\#62043](https://github.com/airbytehq/airbyte/pull/62043) | Expose database protocol config option.             |
| 0.1.4   | 2025-06-24 | [\#62040](https://github.com/airbytehq/airbyte/pull/62040) | Checker inserts into configured DB.                 |
| 0.1.3   | 2025-06-24 | [\#62038](https://github.com/airbytehq/airbyte/pull/62038) | Allow the client to connect to the resolved DB.     |
| 0.1.2   | 2025-06-23 | [\#62028](https://github.com/airbytehq/airbyte/pull/62028) | Enable the registry in OSS and cloud.               |
| 0.1.1   | 2025-06-23 | [\#62022](https://github.com/airbytehq/airbyte/pull/62022) | Publish first beta version and pin the CDK version. |
| 0.1.0   | 2025-06-23 | [\#62024](https://github.com/airbytehq/airbyte/pull/62024) | Release first beta version.                         |
</details>
