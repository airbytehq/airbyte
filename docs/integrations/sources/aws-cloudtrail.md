# AWS CloudTrail

## Overview

The AWS CloudTrail source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Boto3 CloudTrail](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html).

### Output schema

This Source is capable of syncing the following core Streams:

- [Management Events](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html#CloudTrail.Client.lookup_events)

Insight events are not supported right now. Only Management events are available.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `integer`    |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

### Performance considerations

The rate of lookup requests for `events` stream is limited to two per second, per account, per region. This connector gracefully retries when encountering a throttling error. However if the errors continue repeatedly after multiple retries \(for example if you setup many instances of this connector using the same account and region\), the connector sync will fail.

## Getting started

### Requirements

- AWS Access key ID
- AWS Secret access key
- AWS region name

### Setup guide

Please, follow this [steps](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html) to get your AWS access key and secret.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.7   | 2024-04-15 | [37122](https://github.com/airbytehq/airbyte/pull/37122) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.6   | 2024-04-12 | [37122](https://github.com/airbytehq/airbyte/pull/37122) | schema descriptions                                                             |
| 0.1.5   | 2023-02-15 | [23083](https://github.com/airbytehq/airbyte/pull/23083) | Specified date formatting in specification                                      |
| 0.1.4   | 2022-04-11 | [11763](https://github.com/airbytehq/airbyte/pull/11763) | Upgrade to Python 3.9                                                           |
| 0.1.3   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications                               |
| 0.1.2   | 2021-08-04 | [5152](https://github.com/airbytehq/airbyte/pull/5152)   | Fix connector spec.json                                                         |
| 0.1.1   | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                 |
| 0.1.0   | 2021-06-23 | [4122](https://github.com/airbytehq/airbyte/pull/4122)   | Initial release supporting the LookupEvent API                                  |
