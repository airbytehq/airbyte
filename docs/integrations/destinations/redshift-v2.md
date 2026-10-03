# Redshift V2

This page guides you through the process of setting up the Redshift V2 destination connector.

:::info
This is a new version of the Redshift destination built on the Dataflow CDK. It uses direct SQL INSERT statements without S3 staging.
:::

## Prerequisites

- An active Redshift cluster
- A database user with write permissions

### Configuration Options

- **Host**: The hostname of your Redshift cluster
- **Port**: The port number (default: 5439)
- **Database**: The database name
- **Username**: Database user with write permissions
- **Password**: Password for the database user
- **Schema**: The schema to write data to (default: public)

## Supported sync modes

The Redshift V2 destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append
- Incremental - Append + Deduped

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.1.0   | 2025-12-18 | [TBD](https://github.com/airbytehq/airbyte/pull/TBD)     | Initial release using Bulk CDK    |

</details>
