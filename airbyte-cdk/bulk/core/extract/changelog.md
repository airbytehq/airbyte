# Bulk CDK Extract

The Extract CDK provides functionality for source connectors including schema discovery, partitioned data reading, state management, CDC support via Debezium, and JDBC toolkits.

## Changelog

<details>
  <summary>Expand to review</summary>

### 1.2.3 — 2026-10-21

[#89633](https://github.com/airbytehq/airbyte/pull/89633) — Fix the Docker Scout critical/high findings on the extract classpath. `extract-jdbc` moves BouncyCastle to `1.86` (`bcpkix`, `bcprov`; `bctls` `1.86.2`) in place of the `1.77`/`1.78.1` mix (CVE-2024-29857, CVE-2025-14813, CVE-2026-8763, CVE-2026-13506). `extract-cdc` adds published `api` constraints on the Debezium transitive chain: Kafka `4.1.2` (CVE-2026-33557, CVE-2026-35554), Jetty `12.0.40`, `org.lz4:lz4-java` `1.8.1` (CVE-2025-12183), `at.yawk.lz4:lz4-java` `1.12.0` (CVE-2026-106451 in the `1.10.1` that Kafka `4.1.2` depends on) and plexus-utils `3.6.2` (CVE-2025-67030); connectors pick them up by bumping `cdkVersion`, with no build change of their own. `bulk-cdk-core-base` is re-pinned to `1.0.8` (sshd-mina `2.20.0`, mina-core `2.0.31`, bcprov `1.86`).

### 1.2.2 — 2026-10-21

[#86422](https://github.com/airbytehq/airbyte/pull/86422) — Treat an empty `{}` stream state as a cold start in `DefaultJdbcPartitionFactory` so retried full-refresh streams are re-read instead of being silently skipped.

### 1.2.1 — 2026-10-20

[#89583](https://github.com/airbytehq/airbyte/pull/89583) — Declare the Debezium `3.4.3.Final` artifacts in `extract-cdc` with explicit versions instead of importing the Debezium BOM, whose Testcontainers 2.0.2 constraint made the test fixtures unpublishable (extract 1.2.0 was only partially published). The CDK no longer sets versions for connectors' Debezium artifacts, and the BOM's JUnit 6 and Jackson 2.19 constraints no longer reach connector classpaths.

#### Follow-up for connectors

##### Debezium connector artifact: explicit version

Declare the connector's Debezium artifact with the version the CDK's `extract-cdc` toolkit uses, for example `implementation 'io.debezium:debezium-connector-mysql:3.4.3.Final'`, and change it whenever that toolkit's Debezium version changes.

### 1.2.0 — 2026-10-20

**Do not use: only `bulk-cdk-core-extract` was published, without its toolkits. Use 1.2.1.**

[#89012](https://github.com/airbytehq/airbyte/pull/89012) — Upgrade Debezium to `3.4.3.Final` in `extract-cdc`. Fixes source-mysql CDC syncs failing with `Incumbent CDC state is invalid ... "other" is null` once a failover, upgrade or restore adds a server UUID that the saved offset does not have (DBZ-9682, [#75558](https://github.com/airbytehq/airbyte/issues/75558)). The Debezium engine now gets 5 minutes to shut down and to start its task (`record.processing.shutdown.timeout.ms`, `internal.task.management.timeout.ms`), replacing `debezium.embedded.shutdown.pause.before.interrupt.ms`, which Debezium no longer reads.

#### Follow-up for connectors

##### Snapshot modes: `schema_only`, `schema_only_recovery` removed

Use `no_data` and `recovery` instead.

##### source-postgres: `flush.lsn.source` → `lsn.flush.mode`

Replace `flush.lsn.source=true` with `lsn.flush.mode=connector` and `flush.lsn.source=false` with `lsn.flush.mode=manual`; the deprecated property is still mapped the same way. The JDBC driver's keep-alive no longer advances the replication slot, so while the captured tables are idle only `heartbeat.action.query` moves it.

##### source-postgres: PostgreSQL 13

Debezium no longer supports PostgreSQL 13 (DBZ-9376); document PostgreSQL 14 as the minimum version for CDC.

##### source-mssql: Debezium version pins

Drop the `3.4.3.Final` version on `debezium-embedded` in `build.gradle`, which the CDK provides; keep it on `debezium-connector-sqlserver`.

### 1.1.22 — 2026-10-16

[#89040](https://github.com/airbytehq/airbyte/pull/89040) — Repo-wide reformat with ktfmt 0.65 (trailing commas on one-per-line parameter and argument lists, blank lines between declarations) and removal of SpotBugs suppressions that 4.10.5 on the K2 compiler no longer needs; no behaviour change.

### 1.1.21 — 2026-10-16

[#89039](https://github.com/airbytehq/airbyte/pull/89039) — Compile against the published bulk-cdk-core-base 1.0.6 (Kotlin 2.4 toolchain) instead of 1.0.3; no code change.

### 1.1.20 — 2026-10-16

[#89031](https://github.com/airbytehq/airbyte/pull/89031) — Kotlin compiler 2.4.21 with K2, KSP 2.3.10, kotlinx-coroutines 1.11.0 and mockk 1.14.11 (lifting the strictly-1.13.13 pin); KSP is now declared per source set (`kspTestFixtures`, `kspIntegrationTest`) because KSP2 no longer applies to every compilation; released alongside base 1.0.6 and load 1.1.6; no runtime behaviour change in extract.

### 1.1.19 — 2026-10-16

[#88992](https://github.com/airbytehq/airbyte/pull/88992) — Bump Micronaut to 4.10.31, Jackson to 2.21.7 (Kotlin runtime 2.1.21), JUnit to 5.14 and SpotBugs to 4.10.5; Dagger and `javax.inject` are removed in favour of `jakarta.inject` only. Released alongside base 1.0.5 and load 1.1.5; no extract behaviour change.

### 1.1.18 — 2026-10-16

[#88151](https://github.com/airbytehq/airbyte/pull/88151) — CDC: record writes that happen while the Debezium engine is shutting down are queued and performed by `CdcPartitionReader.run()` once the engine thread has ended, so the record count in the final checkpoint includes them. Previously, with Debezium's `AsyncEmbeddedEngine` (source-mssql), a shutdown-path write could still be in flight when the state message was emitted, so the source reported fewer records than it had sent and the platform waited for the checkpoints to flush. A shutdown-path write that fails now fails the read with its cause instead of being lost.

### 1.1.17 — 2026-10-15

[#89002](https://github.com/airbytehq/airbyte/pull/89002) — Test and testFixtures dependencies are declared explicitly (Kotlin Gradle plugin 2.0.10+ no longer propagates `implementation` dependencies into testFixtures, nor `testFixturesImplementation` into tests), `junit-platform-launcher` is on every test runtime classpath, and K2-lint cleanups that also compile on Kotlin 1.9 (`JdbcAccessor` array getter, redundant casts/safe calls). No behaviour change.

### 1.1.16 — 2026-10-12

[#88497](https://github.com/airbytehq/airbyte/pull/88497) — `SourceConfigurationFactory.make()` rethrows a `ConnectorErrorException` (for example the `ConfigErrorException` a connector throws to reject its configuration, such as `Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel.`) unchanged instead of wrapping it in the generic `Failed to build ConnectorConfiguration.` error, so the connector's message reaches the user in CHECK. Every other exception is still wrapped. This matches the existing behaviour of `DestinationConfigurationFactory`.

[#88497](https://github.com/airbytehq/airbyte/pull/88497) — New `CloudHostCheck` object in the extract-jdbc toolkit (`io.airbyte.cdk.check`). On Airbyte Cloud (`FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT`) it throws a `ConfigErrorException` for a loopback or unspecified host (`localhost`, `127.x.x.x`, `::1`, `0.0.0.0`) configured without an SSH tunnel (`Airbyte Cloud cannot reach a database on your own machine. Use a hostname reachable from the internet, or configure an SSH tunnel.`) and for a host that carries a scheme, a path, credentials or a port (`Enter only the hostname in Host; put the port in the Port field.`). Outside Airbyte Cloud it is a no-op. Connectors call it from `MetadataQuerier.Factory.session()` before the JDBC connection opens, so the message is not hidden behind the network error. `CloudHostCheck.validateHostSyntax()` runs the second half alone with a caller-supplied message, for a connector without an SSH tunnel option or a `Port` field (source-snowflake, whose Host is the account domain).

### 1.1.15 — 2026-10-08

[#88175](https://github.com/airbytehq/airbyte/pull/88175) — Restore null-safe JDBC `DateAccessor`/`TimestampAccessor` getters and revert `OffsetDateTimeFieldType` to `ObjectGetter`, removing the Postgres-specific `infinity`/`-infinity` checks from the shared accessors (source-postgres handles them in its own field types). MySQL zero dates read with `zeroDateTimeBehavior=convertToNull` now become null without a WARN stack trace or a `RETRIEVAL_FAILURE_TOTAL` change.

### 1.1.14 — 2026-10-07

[#88342](https://github.com/airbytehq/airbyte/pull/88342) — Accept `{"type": "array"}` fields without `items` in READ-time catalog validation (mapped to an array of JSONB) instead of failing with a NullPointerException.

### 1.1.13 — 2026-10-05

[#86976](https://github.com/airbytehq/airbyte/pull/86976) — Protobuf record consumer: set the stream namespace only when present instead of failing with a NullPointerException, restore the default data slots before every record so sparse payloads do not inherit the previous record's values, and clear the record meta before every record so field changes do not leak into the following records.

### 1.1.12 — 2026-09-17

[#86412](https://github.com/airbytehq/airbyte/pull/86412) — Return null instead of NPE when JDBC getTimestamp/getDate return null for a non-null string value (MySQL zero dates with zeroDateTimeBehavior=convertToNull).

### 1.1.11 — 2026-09-02

[#85313](https://github.com/airbytehq/airbyte/pull/85313) — Tolerate empty STREAM-typed input state in global (CDC) mode instead of failing.

### 1.1.10 — 2026-08-08

[#80949](https://github.com/airbytehq/airbyte/pull/80949) — Field decoration for full refresh CDC streams with no primary key.

### 1.1.9 — 2026-07-28

[#83201](https://github.com/airbytehq/airbyte/pull/83201) — Bump Testcontainers to 1.21.4 for Docker API v1.44 negotiation.

### 1.1.8 — 2026-05-28

[78475](https://github.com/airbytehq/airbyte/pull/78475) — Fix a resource leak entered in partitions creator factory resource acquisition in the previous version.

### 1.1.7 — 2026-05-11

[78022](https://github.com/airbytehq/airbyte/pull/78022) — Put Partitions Creator factory under concurrency control to prevent a case of uncontrolled db queries going over the limit.

### 1.1.6 — 2026-04-24

[76961](https://github.com/airbytehq/airbyte/pull/76961) — `JdbcSourceConfiguration.namespaces` is optional: an empty set means discover across all accessible schemas/catalogs.

### 1.1.5 — 2026-04-22

[76898](https://github.com/airbytehq/airbyte/pull/76898) — Catalog validation failure messages now include an actionable remediation sentence.

### 1.1.4 — 2026-04-20

[76481](https://github.com/airbytehq/airbyte/pull/76481) — Bump bulk-cdk-core-base to 1.0.3 to pick up AIRBYTE_EDITION feature flag fix.

### 1.1.3 — 2026-04-16

[76326](https://github.com/airbytehq/airbyte/pull/76326) — Catalog validation failures are captured as stream-level sync failures.

### 1.1.2 — 2026-03-31

[74124](https://github.com/airbytehq/airbyte/pull/74124) — Change the default implementation of JDBC incremental partition to non splittable.

### 1.1.1 — 2026-04-02

[76054](https://github.com/airbytehq/airbyte/pull/76054) — Clarified CDC termination condition. Ensure `querySingleValue` returns one result or throws.

### 1.1.0 — 2026-03-30

[75636](https://github.com/airbytehq/airbyte/pull/75636) — CDC positions are partially ordered, an optional CDC startup hook was added, and source fields are now represented by `EmittedField`.

#### Breaking changes

##### CDC positions: `Comparable` → `PartiallyOrdered`

Implement `PartiallyOrdered<T>` on the connector's CDC position type instead of `Comparable<T>`.

##### Source fields: `Field` → `EmittedField`

Rename connector usages of `Field` to `EmittedField`, including imports, type annotations, and generic arguments.

### 1.0.2 — 2026-02-24

[74007](https://github.com/airbytehq/airbyte/pull/74007) — Fix infinite loop when cursor-based incremental sync encounters an empty table with prior state by caching NULL cursor upper bound values (toolkit).

### 1.0.1 — 2026-02-24

Bump bulk-cdk-core-base to 1.0.1 to pick up CVE fixes (CVE-2021-47621, CVE-2022-36944).

### 1.0.0 — 2026-02-02

[72376](https://github.com/airbytehq/airbyte/pull/72376) — Initial independent release of bulk-cdk-core-extract. Separate versioning for extract package begins.

</details>

---

## Historical Entries (Unified Bulk CDK)

The entries below are from the unified bulk CDK before the split into separate base, extract, and load packages (versions 0.1.0 through 0.2.6). All three packages inherit this shared history.

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | CDK Component | Subject                                                                                                                                                                                                                                                                                                                                                         |
|---------|------------|----------------------------------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.6   | 2025-02-02 |                                                          | Load          | Cleanup load-iceberg-parquet toolkit: remove unused methods from IcebergUtil, inline generation ID validation into IcebergTableWriterFactory, add unit tests for toolkit classes.                                                                                                                                                                               |
| 0.2.5   | 2025-02-02 |                                                          | Load          | Fix legacy-task-loader base dependency: `implementation` -> `api` for transitive resolution. into IcebergTableWriterFactory, add unit tests for toolkit classes.                                                                                                                                                                                                |
| 0.2.4   | 2025-01-29 |                                                          | Load, Extract | Load and Extract now declare base CDK as an `api` dependency with explicit version (1.0.0), enabling transitive dependency resolution for connectors. Moved micronautVersion to gradle.properties.                                                                                                                                                              |
| 0.2.3   | 2025-01-29 | [72437](https://github.com/airbytehq/airbyte/pull/72437) | Load          | Exposes JsonConverterConfig and LifecycleParallelismConfig.                                                                                                                                                                                                                                                                                                     |
| 0.2.2   | 2025-01-16 | [71803](https://github.com/airbytehq/airbyte/pull/71803) | Extract       | Added validation in `CdcPartitionReader.checkpoint()` to fail if a watchdog timeout occurs during synthetic snapshot. Updated `ValidDebeziumWarmStartState` to require non-null schema history.                                                                                                                                                                  |
| 0.2.1   |            |                                                          | Load          | Revert schema parsing change in `legacy-task-loader` that failed streams when handling empty schemas. Schemas without a `type` field now default to object type again.                                                                                                                                                                                          |
| 0.2.0   |            |                                                          | Load          | Fully separate `legacy-task-loader` toolkit from `core-load`. Drastically simplify `core-load` by removing legacy abstractions.                                                                                                                                                                                                                                 |
| 0.1.108 |            |                                                          | Load          | DataCoercionSuite tests null character in strings                                                                                                                                                                                                                                                                                                               |
| 0.1.107 |            |                                                          | Base          | Add utility to start ssh tunnel + return endpoint                                                                                                                                                                                                                                                                                                               |
| 0.1.106 |            |                                                          | Load          | Add `DEFAULT_AIRBYTE_INTERNAL_NAMESPACE` constant to `core-load` table package. Add README documentation to `legacy-task-loader` and `legacy-task-load-db` toolkits                                                                                                                                                                                             |
| 0.1.105 |            |                                                          | Load          | Schema regression tests use .json extension                                                                                                                                                                                                                                                                                                                     |
| 0.1.104 |            |                                                          | Load          | Add `legacy-task-loader` toolkit containing CDK 0.1.74 code for connectors not yet migrated to the modern tableSchema API. Add `useLegacyTaskLoader` option to `airbyteBulkConnector` plugin to automatically include the toolkit and exclude core-load. Rename `load-db` toolkit to `legacy-task-load-db`. Revert `load-db` to pre components era (cdk 0.1.52) |
| 0.1.103 |            |                                                          | Load          | Add table identifier regression test                                                                                                                                                                                                                                                                                                                            |
| 0.1.102 |            |                                                          | Load          | Add schema regression test                                                                                                                                                                                                                                                                                                                                      |
| 0.1.101 |            |                                                          | Load          | Introduce scope and oauth server uri attributes in iceberg polaris spec                                                                                                                                                                                                                                                                                         |
| 0.1.100 |            |                                                          | Load          | Allow override of socket count in dest connectors                                                                                                                                                                                                                                                                                                               |
| 0.1.99  |            |                                                          | Load          | Enforce maximum parallelism for final aggregate flushes                                                                                                                                                                                                                                                                                                         |
| 0.1.98  |            |                                                          | Extract       | Fix a bug causing query limit pull a negative number of rows                                                                                                                                                                                                                                                                                                    |
| 0.1.97  |            |                                                          | Load          | Slightly refactor schema mapper suite                                                                                                                                                                                                                                                                                                                           |
| 0.1.96  |            |                                                          | Extract       | Allow setting an upper limit for the number of rows pulled in a single query for a sequential partition read                                                                                                                                                                                                                                                    |
| 0.1.95  |            |                                                          | Load          | Add schema mapper test suite                                                                                                                                                                                                                                                                                                                                    |
| 0.1.94  |            |                                                          | Extract       | Fix trigger table handling of empty change tables                                                                                                                                                                                                                                                                                                               |
| 0.1.93  |            |                                                          | Load          | Add KDoc documentation to core destination interfaces: Aggregate, AggregateFactory and RecordDTO                                                                                                                                                                                                                                                                |
| 0.1.92  |            |                                                          | Load          | Datacoercion suite calls ValueCoercer.map                                                                                                                                                                                                                                                                                                                       |
| 0.1.91  |            |                                                          | Load          | Upsert records test uses proper target schema                                                                                                                                                                                                                                                                                                                   |
| 0.1.90  |            |                                                          | Load          | Components tests: data coercion tests cover all data types                                                                                                                                                                                                                                                                                                      |
| 0.1.89  |            |                                                          | Load          | Components tests: data coercion tests for int+number                                                                                                                                                                                                                                                                                                            |
| 0.1.88  |            |                                                          | Load          | Add CDC_CURSOR_COLUMN_NAME constant                                                                                                                                                                                                                                                                                                                             |
| 0.1.87  |            |                                                          | Load          | Properly call NamespaceMapper before calculating final table names                                                                                                                                                                                                                                                                                              |
| 0.1.86  |            |                                                          | Load          | Adds toFinalSchema "escape hatch" for final table schema munging. Refactored Component test fixtures to require explicit StreamTableSchema creation using TableSchemaFactory                                                                                                                                                                                    |
| 0.1.85  |            |                                                          | Extract       | Fix CDC partition reader race condition when draining records after debezium shutdown                                                                                                                                                                                                                                                                           |
| 0.1.84  |            |                                                          | Load          | Move most DB packages into core. Refactor table schema interface into TableSchemaMapper                                                                                                                                                                                                                                                                         |
| 0.1.83  |            |                                                          | Load          | More tests to help guide dependency injection dependency implementations                                                                                                                                                                                                                                                                                        |
| 0.1.82  |            |                                                          | Load          | Components tests: more schema evolution testcases                                                                                                                                                                                                                                                                                                               |
| 0.1.81  |            |                                                          | Load          | Components tests: more coverage on upsert                                                                                                                                                                                                                                                                                                                       |
| 0.1.80  |            |                                                          | Extract       | Fix default partition_id value for `CheckpointOnlyPartitionReader`                                                                                                                                                                                                                                                                                              |
| 0.1.79  |            |                                                          | Extract       | Support multiple ts precision patterns for ts decoding. Expose `columnMetadataFromResultSet` function in `JdbcMetadataQuerier`                                                                                                                                                                                                                                  |
| 0.1.78  |            |                                                          | Load          | Add basic schema evolution test cases                                                                                                                                                                                                                                                                                                                           |
| 0.1.77  |            |                                                          | Extract       | Fix duplicate metadata key in JdbcMetadataQuerier                                                                                                                                                                                                                                                                                                               |
| 0.1.76  |            |                                                          | Load          | Remove a println from our code generating bad logs                                                                                                                                                                                                                                                                                                              |
| 0.1.75  |            |                                                          | Extract       | Improve handling of debezium engine shutdown                                                                                                                                                                                                                                                                                                                    |
| 0.1.74  |            |                                                          | Load          | Split up ensureSchemaMatches into smaller functions                                                                                                                                                                                                                                                                                                             |
| 0.1.73  |            |                                                          | Load          | More changes to `IcebergTableSynchronizer` to get BigLake working                                                                                                                                                                                                                                                                                               |
| 0.1.72  |            |                                                          | Extract       | Fix case sensitivity for table filtering                                                                                                                                                                                                                                                                                                                        |
| 0.1.71  |            |                                                          | Load          | Remove noisy logs                                                                                                                                                                                                                                                                                                                                               |
| 0.1.70  |            |                                                          | Load          | Make getOperation in icebergUtil public                                                                                                                                                                                                                                                                                                                         |
| 0.1.69  |            |                                                          | Load          | Update the IcebergTableSynchronizer to allow for individual update operations commit in preparation for BigLake                                                                                                                                                                                                                                                  |
| 0.1.68  |            |                                                          | Load          | Refactor additional state statistic tracking                                                                                                                                                                                                                                                                                                                    |
| 0.1.67  |            |                                                          | Load          | Fix expectations in basic integration tests related to additional stats                                                                                                                                                                                                                                                                                         |

</details>
