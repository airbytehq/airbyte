# /dev/null Destination

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

## Changelog

<details>
  <summary>Expand to review</summary>

The OSS and Cloud variants have the same version number starting from version `0.2.2`.

| Version     | Date       | Pull Request                                             | Subject                                                                                      |
|:------------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------|
| 0.7.16 | 2025-01-10 | [51493](https://github.com/airbytehq/airbyte/pull/51493) | Use a non root base image |
| 0.7.15 | 2024-12-19 | [49899](https://github.com/airbytehq/airbyte/pull/49931) | Non-functional CDK changes                                                                                 |
| 0.7.14      | 2024-12-20 | [49974](https://github.com/airbytehq/airbyte/pull/49974) | Non-functional CDK changes                                                                   |
| 0.7.13      | 2024-12-18 | [49899](https://github.com/airbytehq/airbyte/pull/49899) | Use a base image: airbyte/java-connector-base:1.0.0                                          |
| 0.7.12      | 2024-12-04 | [48794](https://github.com/airbytehq/airbyte/pull/48794) | Promoting release candidate 0.7.12-rc.2 to a main version.                                   |
| 0.7.12-rc.2 | 2024-11-26 | [48693](https://github.com/airbytehq/airbyte/pull/48693) | Update for testing progressive rollout                                                       |
| 0.7.12-rc.1 | 2024-11-25 | [48693](https://github.com/airbytehq/airbyte/pull/48693) | Update for testing progressive rollout                                                       |
| 0.7.11      | 2024-11-18 | [48468](https://github.com/airbytehq/airbyte/pull/48468) | Implement File CDk                                                                           |
| 0.7.10      | 2024-11-08 | [48429](https://github.com/airbytehq/airbyte/pull/48429) | Bugfix: correctly handle state ID field                                                      |
| 0.7.9       | 2024-11-07 | [48417](https://github.com/airbytehq/airbyte/pull/48417) | Only pass through the state ID field, not all additional properties                          |
| 0.7.8       | 2024-11-07 | [48416](https://github.com/airbytehq/airbyte/pull/48416) | Bugfix: global state correclty sends additional properties                                   |
| 0.7.7       | 2024-10-17 | [46692](https://github.com/airbytehq/airbyte/pull/46692) | Internal code changes                                                                        |
| 0.7.6       | 2024-10-08 | [46683](https://github.com/airbytehq/airbyte/pull/46683) | Bugfix: pick up checkpoint safety check fix                                                  |
| 0.7.5       | 2024-10-08 | [46683](https://github.com/airbytehq/airbyte/pull/46683) | Bugfix: checkpoints in order, all checkpoints processed before shutdown                      |
| 0.7.4       | 2024-10-08 | [46650](https://github.com/airbytehq/airbyte/pull/46650) | Internal code changes                                                                        |
| 0.7.3       | 2024-10-01 | [46559](https://github.com/airbytehq/airbyte/pull/46559) | From load CDK: async improvements, stream incomplete, additionalProperties on state messages |
| 0.7.2       | 2024-10-01 | [45929](https://github.com/airbytehq/airbyte/pull/45929) | Internal code changes                                                                        |
| 0.7.1       | 2024-09-30 | [46276](https://github.com/airbytehq/airbyte/pull/46276) | Upgrade to latest bulk CDK                                                                   |
| 0.7.0       | 2024-09-20 | [45704](https://github.com/airbytehq/airbyte/pull/45704) |                                                                                              |
| 0.6.1       | 2024-09-20 | [45715](https://github.com/airbytehq/airbyte/pull/45715) | add destination to cloud registry                                                            |
| 0.6.0       | 2024-09-18 | [45651](https://github.com/airbytehq/airbyte/pull/45651) | merge destination-e2e(OSS) and destination-dev-null(cloud)                                   |
| 0.5.0       | 2024-09-18 | [45650](https://github.com/airbytehq/airbyte/pull/45650) | upgrade cdk                                                                                  |
| 0.4.1       | 2024-09-18 | [45649](https://github.com/airbytehq/airbyte/pull/45649) | convert test code to kotlin                                                                  |
| 0.4.0       | 2024-09-18 | [45648](https://github.com/airbytehq/airbyte/pull/45648) | convert production code to kotlin                                                            |
| 0.3.6       | 2024-05-09 | [38097](https://github.com/airbytehq/airbyte/pull/38097) | Support dedup                                                                                |
| 0.3.5       | 2024-04-29 | [37366](https://github.com/airbytehq/airbyte/pull/37366) | Support refreshes                                                                            |
| 0.3.4       | 2024-04-16 | [37366](https://github.com/airbytehq/airbyte/pull/37366) | Fix NPE                                                                                      |
| 0.3.3       | 2024-04-16 | [37366](https://github.com/airbytehq/airbyte/pull/37366) | Fix Log trace messages                                                                       |
| 0.3.2       | 2024-02-14 | [36812](https://github.com/airbytehq/airbyte/pull/36812) | Log trace messages                                                                           |
| 0.3.1       | 2024-02-14 | [35278](https://github.com/airbytehq/airbyte/pull/35278) | Adopt CDK 0.20.6                                                                             |
| 0.3.0       | 2023-05-08 | [25776](https://github.com/airbytehq/airbyte/pull/25776) | Standardize spec and change property field to non-keyword                                    |
| 0.2.4       | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors                                       |
| 0.2.3       | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                 |
| 0.2.2       | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745) | Integrate with Sentry.                                                                       |
| 0.2.1       | 2021-12-19 | [\#8824](https://github.com/airbytehq/airbyte/pull/8905) | Fix documentation URL.                                                                       |
| 0.2.0       | 2021-12-16 | [\#8824](https://github.com/airbytehq/airbyte/pull/8824) | Add multiple logging modes.                                                                  |
| 0.1.0       | 2021-05-25 | [\#3290](https://github.com/airbytehq/airbyte/pull/3290) | Create initial version.                                                                      |

</details>
