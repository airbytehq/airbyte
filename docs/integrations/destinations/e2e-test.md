# End-to-End Testing Destination

This destination is for testing of Airbyte connections. It can be set up as a source message logger, a `/dev/null`, or to mimic specific behaviors (e.g. exception during the sync). Please use it with discretion. This destination may log your data, and expose sensitive information.

## Features

| Feature                       | Supported | Notes |
| :---------------------------- | :-------- | :---- |
| Full Refresh Sync             | Yes       |       |
| Incremental Sync              | Yes       |       |
| Replicate Incremental Deletes | No        |       |
| SSL connection                | No        |       |
| SSH Tunnel Support            | No        |       |

## Mode

### Silent (`/dev/null`)

**This is the only mode allowed on Airbyte Cloud.**

This mode works as `/dev/null`. It does nothing about any data from the source connector. This is usually only useful for performance testing of the source connector.

### Logging

This mode logs the data from the source connector. It will log at most 1,000 data entries.

There are the different logging modes to choose from:

| Mode             | Notes                                                                                                                       | Parameters                                                                                                                                 |
| :--------------- | :-------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| First N entries  | Log the first N number of data entries for each data stream.                                                                | N: how many entries to log.                                                                                                                |
| Every N-th entry | Log every N-th entry for each data stream. When N=1, it will log every entry. When N=2, it will log every other entry. Etc. | N: the N-th entry to log. Max entry count: max number of entries to log.                                                                   |
| Random sampling  | Log a random percentage of the entries for each data stream.                                                                | Sampling ratio: a number in range of `[0, 1]`. Optional seed: default to system epoch time. Max entry count: max number of entries to log. |

### Throttling

This mode mimics a slow data sync. You can specify the time (in millisecond) of delay between each message from the source is processed.

### Failing

This mode throws an exception after receiving a configurable number of messages.

## CHANGELOG

The OSS and Cloud variants have the same version number starting from version `0.2.2`.

| Version | Date       | Pull Request                                             | Subject                                                   |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------- |
| 0.3.6   | 2024-05-09 | [38097](https://github.com/airbytehq/airbyte/pull/38097) | Support dedup                                             |
| 0.3.5   | 2024-04-29 | [37366](https://github.com/airbytehq/airbyte/pull/37366) | Support refreshes                                         |
| 0.3.4   | 2024-04-16 | [37366](https://github.com/airbytehq/airbyte/pull/37366) | Fix NPE                                                   |
| 0.3.3   | 2024-04-16 | [37366](https://github.com/airbytehq/airbyte/pull/37366) | Fix Log trace messages                                    |
| 0.3.2   | 2024-02-14 | [36812](https://github.com/airbytehq/airbyte/pull/36812) | Log trace messages                                        |
| 0.3.1   | 2024-02-14 | [35278](https://github.com/airbytehq/airbyte/pull/35278) | Adopt CDK 0.20.6                                          |
| 0.3.0   | 2023-05-08 | [25776](https://github.com/airbytehq/airbyte/pull/25776) | Standardize spec and change property field to non-keyword |
| 0.2.4   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors    |
| 0.2.3   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option              |
| 0.2.2   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745) | Integrate with Sentry.                                    |
| 0.2.1   | 2021-12-19 | [\#8824](https://github.com/airbytehq/airbyte/pull/8905) | Fix documentation URL.                                    |
| 0.2.0   | 2021-12-16 | [\#8824](https://github.com/airbytehq/airbyte/pull/8824) | Add multiple logging modes.                               |
| 0.1.0   | 2021-05-25 | [\#3290](https://github.com/airbytehq/airbyte/pull/3290) | Create initial version.                                   |
