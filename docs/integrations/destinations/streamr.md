# Streamr

## Features

| Feature                       | Support | Notes                                                                                        |
| :---------------------------- | :-----: | :------------------------------------------------------------------------------------------- |
| Full Refresh Sync             |   ❌    | Warning: this mode deletes all previously synced data in the configured bucket path.         |
| Incremental - Append Sync     |   ✅    |                                                                                              |
| Incremental - Deduped History |   ❌    | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces                    |   ❌    | Setting a specific bucket path is equivalent to having separate namespaces.                  |

The Airbyte S3 destination allows you to sync data to AWS S3 or Minio S3. Each stream is written to its own directory under the bucket.

## Troubleshooting

Check out common troubleshooting issues for the Streamr destination connector

## Configuration

| Parameter  |  Type  | Notes                      |
| :--------- | :----: | :------------------------- | --- |
| privateKey | string | You private key on Streamr |
| streamId   | string | Your full Stream ID        |     |

## Output Schema

All json data is output at StreamR

#### Data schema

Any json data schema will work

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject          |
| :------ | :--------- | :------------------------------------------------------- | :--------------- |
| 0.0.1   | 2021-11-20 | [GitHub](https://github.com/devmate-cloud/streamr-airbyte-connectors/releases/tag/v0.0.1) | Initial release. |