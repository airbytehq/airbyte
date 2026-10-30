# End-to-End Testing (/dev/null) Destination

The `/dev/null` destination is a testing destination. It accepts every record from the source and,
by default, discards it. Use it to benchmark a source connector, validate that a connection can
complete, or reproduce specific destination behaviors (slow processing or a failure after N
messages) without writing data anywhere.

:::danger
In **Logging** mode this destination writes source records into the sync logs. Anyone with access
to the Airbyte logs can read that data. Don't use Logging mode with production or sensitive data.
:::

## Prerequisites

None. The destination has no external dependencies and the connection check always succeeds if the
configuration is valid.

## Setup guide

1. In the Airbyte UI, go to **Destinations**, click **New destination**, and select
   **End-to-End Testing (/dev/null)**.
2. Enter a **Destination name**.
3. Under **Test Destination**, choose a mode (see [Modes](#modes)) and fill in its options.
4. Click **Set up destination**.

## Modes

The available modes depend on where Airbyte runs:

| Mode | Self-Managed | Airbyte Cloud |
| :--- | :---: | :---: |
| [Silent](#silent) | Yes | Yes |
| [Logging](#logging) | Yes | No |
| [Throttled](#throttled) | Yes | No |
| [Failing](#failing) | Yes | No |

### Silent

Silent mode is a true `/dev/null`: every record is accepted and discarded. State messages are still
acknowledged, so the source advances its cursor as it would with a real destination. Use it for
source performance testing or to confirm a sync completes end to end.

**This is the only mode available on Airbyte Cloud.**

### Logging

Logging mode discards records after writing a subset of them to the sync log at `INFO` level. Each
log line includes the stream, the record index, and the record's fields:

```text
Logging Destination(stream=public.users, recordIndex=0, logEntry=1/100): {...}
```

Each stream is logged independently, and the destination never logs more than **1,000 entries per
stream**, whichever logging type you choose.

| Logging type | Behavior | Options |
| :--- | :--- | :--- |
| **First N Entries** | Log the first N records of each stream. | **N**: number of records to log (default `100`, maximum `1000`). |
| **Every N-th Entry** | Log every N-th record of each stream. `N = 1` logs every record, `N = 2` every other record, and so on. | **N**: the interval. **Max Log Entries**: cap on the number of records logged (default `100`, maximum `1000`). |
| **Random Sampling** | Log each record with a given probability. | **Sampling Ratio**: a number between `0` and `1` (default `0.001`). **Random Number Generator Seed** (optional): fix the seed for reproducible sampling; defaults to the current time. **Max Log Entries**: cap on the number of records logged (default `100`, maximum `1000`). |

### Throttled

Throttled mode discards records but sleeps for a configurable number of milliseconds
(`millis_per_record`) before processing each one. Use it to simulate a slow destination
and observe how the source and the platform behave under back-pressure.

### Failing

Failing mode discards records until it has received the configured number of messages
(`num_messages`), then throws an exception, which fails the sync. Use it to test failure
handling, retries, and alerting.

## Sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

Every sync mode is accepted because no data is stored; deduplication and overwrite have no visible
effect. The destination also accepts file-based (file transfer) streams and discards the files.

## Namespace support

Namespaces have no effect on this destination. The stream namespace appears only in Logging mode
output as part of the stream identifier.

## Limitations

- No data is persisted. There is nothing to inspect after a sync other than the logs.
- Logging mode caps output at 1,000 entries per stream and may expose source data in logs.
- On Airbyte Cloud only Silent mode is offered.

## Changelog

<details>
  <summary>Expand to review</summary>

The self-managed and Cloud variants have the same version number starting from version `0.2.2`.

| Version     | Date       | Pull Request                                             | Subject                                                                                      |
|:------------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------|
| 0.9.8 | 2026-10-22 | [89655](https://github.com/airbytehq/airbyte/pull/89655) | Upgrade to Bulk CDK 1.1.9: fix critical CVEs in Apache MINA (mina-core 2.0.31), MINA SSHD 2.20.0 and BouncyCastle 1.86; netty 4.1.139 |
| 0.9.7 | 2026-10-16 | [89066](https://github.com/airbytehq/airbyte/pull/89066) | Bump Bulk CDK to base 1.0.6 / load 1.1.7 (Kotlin 2.4 / K2 toolchain, Micronaut 4.10.31, Jackson 2.21.7). |
| 0.9.6 | 2026-10-09 | [88426](https://github.com/airbytehq/airbyte/pull/88426) | Upgrade to Bulk CDK 1.1.1. |
| 0.9.5 | 2026-09-15 | [86330](https://github.com/airbytehq/airbyte/pull/86330) | Version bump to republish the Cloud-specific connector spec. |
| 0.9.4 | 2026-05-19 | [78228](https://github.com/airbytehq/airbyte/pull/78228) | Upgrade CDK to 1.0.13 |
| 0.9.3 | 2026-02-04 | [72856](https://github.com/airbytehq/airbyte/pull/72856) | Upgrade CDK to 0.2.8 |
| 0.9.2 | 2026-01-21 | [72291](https://github.com/airbytehq/airbyte/pull/72291) | Upgrade CDK to 0.2.0 |
| 0.9.1 | 2026-01-21 | [72226](https://github.com/airbytehq/airbyte/pull/72226) | No-op version bump to test release cycle |
| 0.9.0 | 2026-01-09 | [71264](https://github.com/airbytehq/airbyte/pull/71264) | Promoting release candidate 0.9.0-rc.2 to a main version. |
| 0.9.0-rc.2  | 2026-01-08 | [71242](https://github.com/airbytehq/airbyte/pull/71242) | Add missing configuration bean.                                                              |
| 0.9.0-rc.1  | 2026-01-08 | [71191](https://github.com/airbytehq/airbyte/pull/71191) | Migrate to modern dataflow CDK architecture.                                                 |
| 0.8.6       | 2025-11-05 | [69128](https://github.com/airbytehq/airbyte/pull/69128) | Upgrade to Bulk CDK 0.1.61.                                                                  |
| 0.8.5       | 2025-10-21 | [67153](https://github.com/airbytehq/airbyte/pull/67153) | Implement new proto schema implementation                                                    |
| 0.8.4       | 2025-09-24 | [66684](https://github.com/airbytehq/airbyte/pull/66684) | Pin to CDK artifact.                                                                         |
| 0.8.3       | 2025-09-08 | [65999](https://github.com/airbytehq/airbyte/pull/65999) | Testing publishing flow.                                                                     |
| 0.8.2       | 2025-08-12 | [64897](https://github.com/airbytehq/airbyte/pull/64897) | Testing publishing flow.                                                                     |
| 0.8.1       | 2025-07-30 | [64117](https://github.com/airbytehq/airbyte/pull/64117) | Re-release with latest CDK for socket related fixes.                                         |
| 0.8.0       | 2025-06-17 | [61585](https://github.com/airbytehq/airbyte/pull/61585) | Upgrade dev null to the new data channel based architecture.                                 |
| 0.7.27      | 2025-06-13 | [61587](https://github.com/airbytehq/airbyte/pull/61587) | Test publishing logic.                                                                       |
| 0.7.26      | 2025-05-27 | [60938](https://github.com/airbytehq/airbyte/pull/60938) | Revert to base 2.0.1, test default IPC Options                                               |
| 0.7.25      | 2025-05-15 | [60312](https://github.com/airbytehq/airbyte/pull/60312) | Migrate to base 2.0.2.                                                                       |
| 0.7.24      | 2025-05-15 | [60301](https://github.com/airbytehq/airbyte/pull/60301) | Add support for file-based syncs                                                             |
| 0.7.23      | 2025-05-09 | [59766](https://github.com/airbytehq/airbyte/pull/59766) | Test publishing in new flow.                                                                 |
| 0.7.22      | 2025-05-09 | [59759](https://github.com/airbytehq/airbyte/pull/59759) | Migrate to new flow.                                                                         |
| 0.7.21      | 2025-05-07 | [59710](https://github.com/airbytehq/airbyte/pull/59710) | CDK: bugfixes                                                                                |
| 0.7.20      | 2025-03-21 | [55906](https://github.com/airbytehq/airbyte/pull/55906) | CDK: Pass DestinationRecordRaw around instead of DestinationRecordAirbyteValue               |
| 0.7.19      | 2025-03-13 | [55737](https://github.com/airbytehq/airbyte/pull/55737) | CDK: Pass DestinationRecordRaw around instead of DestinationRecordAirbyteValue               |
| 0.7.18      | 2025-02-25 | [54179](https://github.com/airbytehq/airbyte/pull/54179) | Use new CDK interface; perf improvements, skip initial staging                               |
| 0.7.17      | 2025-01-24 | [51600](https://github.com/airbytehq/airbyte/pull/51600) | Internal refactor                                                                            |
| 0.7.16      | 2024-12-19 | [52076](https://github.com/airbytehq/airbyte/pull/52076) | Test improvements                                                                            |
| 0.7.15      | 2024-12-19 | [49931](https://github.com/airbytehq/airbyte/pull/49931) | Non-functional CDK changes                                                                   |
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
