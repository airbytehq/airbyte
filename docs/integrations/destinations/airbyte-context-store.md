# Airbyte Agents Context Store

The Airbyte Agents Context Store is a fully managed destination for Airbyte Agents. Airbyte
provisions and operates the underlying storage, so there is nothing for you to configure and no
storage location or credentials are exposed to, or accepted from, this connection.

Data is written as Apache Iceberg tables using the same write path as the
[S3 Data Lake](s3-data-lake.md) destination.

## Setup

The only setting is an acknowledgement that storage is managed by Airbyte. Everything else — bucket,
region, warehouse location, catalog and credentials — is supplied by Airbyte at runtime and is never
stored on the destination.

| Field                       | Description                                                                |
| :-------------------------- | :------------------------------------------------------------------------- |
| Airbyte-managed storage     | Acknowledge that Airbyte provisions and manages the storage for this store. |

## Sync modes

| Feature                        | Supported |
| :----------------------------- | :-------- |
| Full Refresh - Overwrite       | Yes       |
| Incremental - Append           | Yes       |
| Incremental - Append + Deduped | Yes       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                 |
| :------ | :--------- | :----------- | :---------------------- |
| 0.1.0   | 2026-08-22 | [84956](https://github.com/airbytehq/airbyte/pull/84956) | Initial release. |

</details>
