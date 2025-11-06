# ClickHouse

The ClickHouse destination connector syncs data from Airbyte sources to [ClickHouse](https://clickhouse.com/), a high-performance columnar database designed for online analytical processing (OLAP). This connector writes data directly to ClickHouse tables with proper typing, enabling fast analytical queries on your replicated data.

This is a complete rewrite of the ClickHouse destination connector built on Airbyte's Bulk CDK framework, replacing the legacy v1 connector.

## Improvements over v1

Version 2.0.0 represents a complete architectural redesign of the ClickHouse destination connector with significant improvements:

- **All sync modes supported**: Full Refresh (Overwrite and Append) and Incremental (Append and Append + Deduped) sync modes are now fully supported.
- **Direct Load with typed columns**: Data is written directly to typed columns matching your source schema, rather than storing everything as JSON in raw tables. This improves query performance and reduces storage requirements.
- **Improved performance**: The new architecture uses ClickHouse's native binary protocol and batch inserts for significantly faster data loading.
- **Active maintenance**: Built on Airbyte's modern CDK framework with ongoing development and support from the Airbyte team.

## Features

All sync modes are supported.

| Feature                        | Supported?\(Yes/No\) | Notes                          |
| :----------------------------- |:---------------------|:-------------------------------|
| Full Refresh Sync              | Yes                  |                                |
| Incremental - Append Sync      | Yes                  |                                |
| Incremental - Append + Deduped | Yes                  | Leverages `ReplacingMergeTree` |
| Namespaces                     | Yes                  |                                |

### Deduplication

For optimal deduplication in Incremental - Append + Deduped sync mode, use a cursor column with one of these types:

- Integer types (Int64, etc.)
- Date
- Timestamp (DateTime64)

If you use a different cursor column type (such as String), the connector will fall back to using the `_airbyte_extracted_at` timestamp for deduplication ordering. This fallback may not accurately reflect your source data's natural ordering, and you'll see a warning in the sync logs.

### Output Schema

Each stream is written to its own table in ClickHouse. Tables are created in either the configured default database (typically `default`) or in a database corresponding to the namespace specified for the stream.

Airbyte data types are converted to ClickHouse types as follows:

- **Decimal** types → `Decimal(38, 9)` (38 digit precision with 9 decimal places)
- **Timestamp** types → `DateTime64(3)` (millisecond precision)
- **Object** types → `JSON` (if JSON is enabled in the connector configuration); otherwise → `String`
- **Integer** types → `Int64`
- **Boolean** types → `Bool`
- **String** types → `String`
- **Union** types → `String`
- **Array** types → `String`

:::note
Arrays and Unions are converted to String for compatibility. If you need to query these as structured data, you can use ClickHouse's JSON functions to parse the string values.
:::

### Requirements

To use the ClickHouse destination connector, you need:

- A ClickHouse instance (ClickHouse Cloud or self-hosted)
- ClickHouse server version 21.8.10.19 or later
- Network access from Airbyte to your ClickHouse instance
- A ClickHouse user with appropriate permissions (see below)

### Setup Guide

#### 1. Configure Network Access

Ensure your ClickHouse database is accessible from Airbyte:

- **ClickHouse Cloud**: Whitelist Airbyte's IP addresses in your ClickHouse Cloud settings
- **Self-hosted ClickHouse**: Configure your firewall to allow connections from Airbyte
- **VPC/Private Network**: If your ClickHouse instance is in a VPC, you may need to set up VPC peering or use SSH tunneling (see SSH Tunnel section below)

#### 2. Create a Dedicated User with Permissions

Create a dedicated ClickHouse user for Airbyte with the following permissions:

- Create and manage databases
- Create, alter, drop, and truncate tables
- Insert and select data

To create a user with the required permissions, run the following SQL commands in your ClickHouse instance:

```sql
-- Create the user (replace 'your_password' with a secure password)
CREATE USER airbyte_user IDENTIFIED BY 'your_password';

-- Grant permissions on the default database
GRANT CREATE ON * TO airbyte_user;
GRANT CREATE ON {database}.* TO airbyte_user;
GRANT ALTER ON {database}.* TO airbyte_user;
GRANT TRUNCATE ON {database}.* TO airbyte_user;
GRANT INSERT ON {database}.* TO airbyte_user;
GRANT SELECT ON {database}.* TO airbyte_user;
GRANT CREATE DATABASE ON {database}.* TO airbyte_user;
GRANT CREATE TABLE ON {database}.* TO airbyte_user;
GRANT DROP TABLE ON {database}.* TO airbyte_user;
```

Replace `{database}` with the database name you configure in the connector settings (typically `default`).

**For connections using custom namespaces**: If you configure custom namespaces in your Airbyte connections, grant permissions for each namespace:

```sql
GRANT CREATE ON {namespace}.* TO airbyte_user;
GRANT ALTER ON {namespace}.* TO airbyte_user;
GRANT TRUNCATE ON {namespace}.* TO airbyte_user;
GRANT INSERT ON {namespace}.* TO airbyte_user;
GRANT SELECT ON {namespace}.* TO airbyte_user;
GRANT CREATE DATABASE ON {namespace}.* TO airbyte_user;
GRANT CREATE TABLE ON {namespace}.* TO airbyte_user;
GRANT DROP TABLE ON {namespace}.* TO airbyte_user;
```

Replace `{namespace}` with each custom namespace you plan to use.

:::tip
While you can use an existing ClickHouse user, we strongly recommend creating a dedicated user for Airbyte. This improves security and makes it easier to audit Airbyte's database operations.
:::

#### 3. Configure the Connector

In Airbyte, configure the ClickHouse destination with the following information:

- **Hostname**: Your ClickHouse server hostname (without protocol prefix like `http://` or `https://`)
- **Port**: HTTP port for ClickHouse (default: 8443 for HTTPS, 8123 for HTTP)
- **Protocol**: Connection protocol (HTTPS recommended for production)
- **Database**: Target database name (default: `default`)
- **Username**: The ClickHouse user you created (for example, `airbyte_user`)
- **Password**: The password for the ClickHouse user
- **Enable JSON**: Whether to use ClickHouse's JSON type for object fields (recommended if your ClickHouse version supports it)

#### 4. SSH Tunnel (Optional)

:::warning
SSH tunneling support is currently in **Beta**. If you encounter issues with SSH tunneling, please contact Airbyte support.
:::

If your ClickHouse instance is not directly accessible from Airbyte, you can use SSH tunneling to establish a secure connection. Configure the SSH tunnel settings in the connector configuration with your SSH host, port, username, and authentication method (password or private key).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                               | Subject                                                                        |
|:-----------|:-----------|:-----------------------------------------------------------|:-------------------------------------------------------------------------------|
| 2.1.11     | 2025-11-05 | [69200](https://github.com/airbytehq/airbyte/pull/69200/)  | Add support for observability metrics                                          |
| 2.1.10     | 2025-11-03 | [69154](https://github.com/airbytehq/airbyte/pull/69154)   | Fix decimal validation                                                         |
| 2.1.9      | 2025-10-30 | [69100](https://github.com/airbytehq/airbyte/pull/69100)   | Upgrade to CDK 0.1.61 to fix state index bug                                   |
| 2.1.8      | 2025-10-28 | [68186](https://github.com/airbytehq/airbyte/pull/68186)   | Upgrade to CDK 0.1.59                                                          |
| 2.1.7      | 2025-10-21 | [67153](https://github.com/airbytehq/airbyte/pull/67153)   | Implement new proto schema implementation                                      |
| 2.1.6      | 2025-10-16 | [68144](https://github.com/airbytehq/airbyte/pull/68144)   | Implement TableOperationsSuite component tests.                                |
| 2.1.5      | 2025-10-09 | [67598](https://github.com/airbytehq/airbyte/pull/67598)   | Improve handling of heavily interleaved streams.                               |
| 2.1.4      | 2025-09-29 | [66743](https://github.com/airbytehq/airbyte/pull/66743)   | Activate speed mode.                                                           |
| 2.1.3      | 2025-09-29 | [66743](https://github.com/airbytehq/airbyte/pull/66743)   | Promoting release candidate 2.1.3-rc.1 to a main version.                      |
| 2.1.3-rc.1 | 2025-09-25 | [66699](https://github.com/airbytehq/airbyte/pull/66699)   | Prepare for speed mode. Fix interleaved stream state handling.                 |
| 2.1.2      | 2025-09-09 | [66143](https://github.com/airbytehq/airbyte/pull/66143)   | Improve schema propagation.                                                    |
| 2.1.1      | 2025-09-09 | [66134](https://github.com/airbytehq/airbyte/pull/66134)   | Update the type we are setting for the number type to `Decimal(38, 9)`.        |
| 2.1.0      | 2025-09-03 | [65929](https://github.com/airbytehq/airbyte/pull/65929)   | Promoting release candidate 2.1.0-rc.2 to a main version.                      |
| 2.1.0-rc.2 | 2025-08-29 | [\#65626](https://github.com/airbytehq/airbyte/pull/65626) | Pick up CDK fix for rare array OOB exception.                                  |
| 2.1.0-rc.1 | 2025-08-21 | [\#65144](https://github.com/airbytehq/airbyte/pull/65144) | Migrate to dataflow model.                                                     |
| 2.0.13     | 2025-08-20 | [\#65125](https://github.com/airbytehq/airbyte/pull/65125) | Update docs permissioning advice.                                              |
| 2.0.12     | 2025-08-20 | [\#65120](https://github.com/airbytehq/airbyte/pull/65120) | Check should properly surface protocol related config errors.                  |
| 2.0.11     | 2025-07-23 | [\#65117](https://github.com/airbytehq/airbyte/pull/65117) | Fix a bug related to the column duplicates name.                               |
| 2.0.10     | 2025-07-23 | [\#64104](https://github.com/airbytehq/airbyte/pull/64104) | Add an option to configure the batch size (both bytes and number of records).  |
| 2.0.9      | 2025-07-23 | [\#63738](https://github.com/airbytehq/airbyte/pull/63738) | Set clickhouse as an airbyte connector.                                        |
| 2.0.8      | 2025-07-23 | [\#63760](https://github.com/airbytehq/airbyte/pull/63760) | Throw an error if an invalid target table exist before the first sync.         |
| 2.0.7      | 2025-07-23 | [\#63751](https://github.com/airbytehq/airbyte/pull/63751) | Only copy intersection columns when there is a dedup change.                   |
| 2.0.6      | 2025-07-22 | [\#63724](https://github.com/airbytehq/airbyte/pull/63724) | Apply clickhouse column name transformation for columns.                       |
| 2.0.5      | 2025-07-22 | [\#63721](https://github.com/airbytehq/airbyte/pull/63721) | Fix schema change with PKs.                                                    |
| 2.0.4      | 2025-07-21 | [\#62948](https://github.com/airbytehq/airbyte/pull/62948) | SSH support BETA.                                                              |
| 2.0.3      | 2025-07-11 | [\#62946](https://github.com/airbytehq/airbyte/pull/62946) | Publish metadata changes.                                                      |
| 2.0.2      | 2025-07-10 | [\#62928](https://github.com/airbytehq/airbyte/pull/62928) | Makes json optional in spec to work around UI issue.                           |
| 2.0.1      | 2025-07-10 | [\#62906](https://github.com/airbytehq/airbyte/pull/62906) | Adds bespoke validation for legacy hostnames that contain a protocol.          |
| 2.0.0      | 2025-07-10 | [\#62887](https://github.com/airbytehq/airbyte/pull/62887) | Cut 2.0.0 release. Replace existing connector.                                 |
| 0.1.11     | 2025-07-09 | [\#62883](https://github.com/airbytehq/airbyte/pull/62883) | Only set JSON properties on client if enabled to support older CH deployments. |
| 0.1.10     | 2025-07-08 | [\#62861](https://github.com/airbytehq/airbyte/pull/62861) | Set user agent header for internal CH telemetry.                               |
| 0.1.9      | 2025-07-03 | [\#62509](https://github.com/airbytehq/airbyte/pull/62509) | Simplify union stringification behavior.                                       |
| 0.1.8      | 2025-06-30 | [\#62100](https://github.com/airbytehq/airbyte/pull/62100) | Add JSON support.                                                              |
| 0.1.7      | 2025-06-24 | [\#62047](https://github.com/airbytehq/airbyte/pull/62047) | Remove the use of the internal namespace.                                      |
| 0.1.6      | 2025-06-24 | [\#62047](https://github.com/airbytehq/airbyte/pull/62047) | Hide protocol option when running on cloud.                                    |
| 0.1.5      | 2025-06-24 | [\#62043](https://github.com/airbytehq/airbyte/pull/62043) | Expose database protocol config option.                                        |
| 0.1.4      | 2025-06-24 | [\#62040](https://github.com/airbytehq/airbyte/pull/62040) | Checker inserts into configured DB.                                            |
| 0.1.3      | 2025-06-24 | [\#62038](https://github.com/airbytehq/airbyte/pull/62038) | Allow the client to connect to the resolved DB.                                |
| 0.1.2      | 2025-06-23 | [\#62028](https://github.com/airbytehq/airbyte/pull/62028) | Enable the registry in OSS and cloud.                                          |
| 0.1.1      | 2025-06-23 | [\#62022](https://github.com/airbytehq/airbyte/pull/62022) | Publish first beta version and pin the CDK version.                            |
| 0.1.0      | 2025-06-23 | [\#62024](https://github.com/airbytehq/airbyte/pull/62024) | Release first beta version.                                                    |

</details>
