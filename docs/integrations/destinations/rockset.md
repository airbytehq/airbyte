# Rockset

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your Rockset connector to version `0.1.4` or newer

## Features

| Feature                       | Support |
| :---------------------------- | :-----: |
| Full Refresh Sync             |   ✅    |
| Incremental - Append Sync     |   ✅    |
| Incremental - Deduped History |   ❌    |
| Namespaces                    |   ❌    |

## Troubleshooting

## Configuration

| Parameter  |  Type  | Notes                                                            |
| :--------- | :----: | :--------------------------------------------------------------- |
| api_key    | string | rockset api key                                                  |
| api_server | string | api URL to rockset, specifying http protocol                     |
| workspace  | string | workspace under which rockset collections will be added/modified |

## Getting Started \(Airbyte Open-Source / Airbyte Cloud\)

#### Requirements

1. Rockset api key with appropriate read and write credentials

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------- |
| 0.1.4   | 2022-06-17 | [15395](https://github.com/airbytehq/airbyte/pull/15395) | Updated Destination Rockset to handle per-stream state |
| 0.1.3   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.2   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                 |
| 0.1.1   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option           |
| 0.1.0   | 2021-11-15 | [8006](https://github.com/airbytehq/airbyte/pull/8006)   | Initial release                                        |
