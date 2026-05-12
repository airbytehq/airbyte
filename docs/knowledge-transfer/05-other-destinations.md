# Snowflake, Iceberg / S3 Data Lake, MSSQL, Redshift

This section gathers smaller-scoped contributions across four destinations: a Snowflake migration with a notable `check` refactor; Iceberg / S3 Data Lake correctness fixes; an MSSQL SSH-tunnel addition; and the Redshift migration plan.

> *Quick file reference: [Appendix §8.4 -- Other Destinations](08-appendix-key-file-paths.md#84-other-destinations).*

## 5.1 Destination Snowflake

Snowflake was migrated to the Bulk CDK in parallel with the ClickHouse rewrite. The work landed across roughly ten PRs between September 2025 and March 2026 ([#66189](https://github.com/airbytehq/airbyte/pull/66189), [#66293](https://github.com/airbytehq/airbyte/pull/66293), [#66302](https://github.com/airbytehq/airbyte/pull/66302), [#66354](https://github.com/airbytehq/airbyte/pull/66354), [#66507](https://github.com/airbytehq/airbyte/pull/66507), [#66513](https://github.com/airbytehq/airbyte/pull/66513), [#66518](https://github.com/airbytehq/airbyte/pull/66518), [#66528](https://github.com/airbytehq/airbyte/pull/66528), [#71273](https://github.com/airbytehq/airbyte/pull/71273), [#74824](https://github.com/airbytehq/airbyte/pull/74824)). The connector lives at [`airbyte-integrations/connectors/destination-snowflake/`](../../airbyte-integrations/connectors/destination-snowflake); current docker image: `4.0.41`.

### 5.1.1 Loader strategy

The Snowflake writer wires up two of the three Direct-Load loaders ([§2.4](02-bulk-cdk.md#24-direct-load-table-stream-loaders-pr-74715)) -- [`SnowflakeWriter.kt:16-18, 101, 113, 125`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/SnowflakeWriter.kt):

| `importType` × `minimumGenerationId` | Loader |
|--------------------------------------|--------|
| `Append` / `Dedupe` with `minimumGenerationId == 0` | `DirectLoadTableAppendStreamLoader` |
| `Append` with `minimumGenerationId == generationId` | `DirectLoadTableAppendTruncateStreamLoader` |
| `Dedupe` with `minimumGenerationId == generationId` | `DirectLoadTableDedupTruncateStreamLoader` |

This is the canonical pattern for Direct-Load destinations and the same shape Postgres ([§4](04-destination-postgres.md)) follows. ClickHouse ([§3.2](03-clickhouse.md#32-the-writer)) deviates because it dedup-via-engine instead of dedup-via-temp-table.

### 5.1.2 The `SnowflakeChecker` recordformatter fix ([PR #71273](https://github.com/airbytehq/airbyte/pull/71273))

Before this fix, `SnowflakeChecker` instantiated `SnowflakeRecordFormatter` directly inside `check()`, hard-coding the standard (non-raw-mode) formatter. In raw-tables-only mode (`legacyRawTablesOnly = true`), the standard formatter does not emit the `_airbyte_loaded_at` column -- a required column in raw mode -- so the check would fail with `column "_airbyte_loaded_at" does not exist` even though a real sync in raw mode would succeed.

The fix refactored `SnowflakeChecker` to **inject** the formatter via the constructor ([`SnowflakeChecker.kt:34-39`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/check/SnowflakeChecker.kt)):

```kotlin
@Singleton
class SnowflakeChecker(
    private val snowflakeAirbyteClient: SnowflakeAirbyteClient,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val columnManager: SnowflakeColumnManager,
    private val snowflakeRecordFormatter: SnowflakeRecordFormatter,
) : DestinationChecker { ... }
```

The mode-aware `SnowflakeRecordFormatter` bean is selected at Micronaut wire time based on `legacyRawTablesOnly`, so the check now uses the same formatter a real sync would use. This is the pattern Postgres ([§4.4](04-destination-postgres.md#44-the-check-operation-oss--cloud-split)) intentionally **does not** adopt -- Postgres splits OSS/Cloud as separate classes and keeps the check minimal rather than going through the full record-formatting pipeline.

The class name is `SnowflakeRecordFormatter` ([`write/load/SnowflakeRecordFormatter.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/load/SnowflakeRecordFormatter.kt)); the fix also affected the Postgres equivalent in the same PR.

## 5.2 Iceberg / S3 Data Lake

The active Iceberg destination is [`destination-s3-data-lake`](../../airbyte-integrations/connectors/destination-s3-data-lake) (the [`destination-iceberg`](../../airbyte-integrations/connectors/destination-iceberg) directory is essentially empty -- it contains only `metadata.yaml` and `icon.svg`; the real implementation moved). The connector is built on top of the [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet) toolkit, where most of the work covered here lives.

Three correctness fixes shipped in March 2026.

### 5.2.1 PK `NumberType` → `StringType` ([PR #74328](https://github.com/airbytehq/airbyte/pull/74328))

Iceberg has a concept of **identifier fields**: a set of columns that uniquely identify a row, used for equality deletes and merge-on-read. Iceberg disallows `float`, `double`, and `decimal` types as identifier fields. Airbyte's `NumberType` maps to Iceberg's `Types.DoubleType.get()` by default ([`AirbyteTypeToIcebergSchema.kt:70`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteTypeToIcebergSchema.kt)), which fails when a `NumberType` column is declared as a primary key.

The fix added a PK-specific override at [`AirbyteTypeToIcebergSchema.kt:111-114`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteTypeToIcebergSchema.kt):

```kotlin
val icebergType =
    if (isPrimaryKey && field.type is NumberType) {
        // Override PK NumberType fields to StringType so they can be used as
        // Iceberg identifier fields (float/double are disallowed as identifiers).
        Types.StringType.get()
    } else {
        icebergTypeConverter.convert(field.type, stringifyObjects = stringifyObjects)
    }
```

The runtime value-side counterpart is at [`AirbyteValueToIcebergRecord.kt:68`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteValueToIcebergRecord.kt), which stringifies the value before writing it to the Parquet file.

This is a deliberate type narrowing for the PK case only -- non-PK number columns continue to map to `DoubleType`. (The previously circulating claim that the fix mapped `NumberType` → `DecimalType` is inaccurate.)

### 5.2.2 Deferred identifier-field update on column replacement ([PR #74723](https://github.com/airbytehq/airbyte/pull/74723))

Schema evolution that replaces a column whose **name** is also in the table's identifier-fields list previously failed with `IllegalArgumentException: ... is not a valid identifier field`. The chain of events:

1. `IcebergTableSynchronizer.synchronize` ([`load-iceberg-parquet/IcebergTableSynchronizer.kt:110-274`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/IcebergTableSynchronizer.kt)) detected an identifier-field change AND a column replacement.
2. It called `updateSchema().setIdentifierFields(newPks)` **before** the column was replaced.
3. Iceberg checked the identifier-field set against the *current* schema (which still had the old column), found it didn't include `newPk`, and threw.

The fix deferred the `setIdentifierFields` call until **after** the column-replacement transaction committed (the call sites at lines 230, 253, 274 now run in the post-replace branch). Tests at [`IcebergTypesComparator.kt:71, 97-99`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/IcebergTypesComparator.kt) cover `identifierFieldsChanged` detection.

### 5.2.3 CDK bump ([PR #74326](https://github.com/airbytehq/airbyte/pull/74326))

Routine bump to pick up the fixes in §5.2.1 and §5.2.2 in the S3-Data-Lake connector. The connector's `dockerImageTag` is currently `0.3.48`.

## 5.3 Destination MSSQL: SSH tunnel ([PR #62078](https://github.com/airbytehq/airbyte/pull/62078))

The MSSQL destination lives at [`airbyte-integrations/connectors/destination-mssql/`](../../airbyte-integrations/connectors/destination-mssql); current image `2.2.16`. Note the package path is under `…/mssql/v2/…` -- the "v2" indicates the Bulk-CDK rewrite but is in the package, not the directory name.

The connector previously had no way to reach a database behind a bastion host. [#62078](https://github.com/airbytehq/airbyte/pull/62078) added SSH-tunnel support by reusing the CDK's existing SSH primitives. The tunnel is created in `DataSourceFactory` (note the camelcase S) at [`src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/DataSourceFactory.kt:20`](../../airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/DataSourceFactory.kt):

| Function | Line | Role |
|----------|------|------|
| `@Factory class DataSourceFactory` | 20 | Micronaut factory |
| `MSSQLConfiguration.toSQLServerDataSource()` (extension) | 37 | Build the JDBC datasource |
| SSH-tunnel branch | 44-57 | If `ssh is SshKeyAuthTunnelMethod \| SshPasswordAuthTunnelMethod`, create a local-forwarded session via `createTunnelSession` (line 51) and rewrite the JDBC URL to point at `localhost:<localPort>` |
| `MSSQLDataSourceFactory` | 99 | The Micronaut-registered factory bean |

Spec wiring: [`MSSQLSpecification.kt:20-21, 89-107`](../../airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/MSSQLSpecification.kt). Config wiring: [`MSSQLConfiguration.kt:13, 26, 74`](../../airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/MSSQLConfiguration.kt).

The implementation deliberately reused the CDK's existing SSH tunnel primitives rather than building a new one -- the only MSSQL-specific code is the URL rewrite, everything else is CDK.

## 5.4 Destination Redshift: migration plan

The Redshift connector has not yet been migrated to the Bulk CDK; the migration plan was written in early 2026 by analyzing the Snowflake, Postgres, and ClickHouse migrations already completed. The plan is documented as part of [`destination-redshift`](../../airbyte-integrations/connectors/destination-redshift)'s docs (not as a markdown file in the connector root) and breaks the work into eleven phases:

1. **Build system** -- Gradle migration, dependency cleanup.
2. **Config / spec** -- Convert `RedshiftDestinationConfig` to a `RedshiftSpecification` + `RedshiftConfiguration` pair, preserving JSON-shape compatibility with the legacy connector.
3. **Schema mapping** -- Create `RedshiftTableSchemaMapper` mirroring the Postgres / Snowflake trio.
4. **SQL generation** -- Implement a `RedshiftDirectLoadSqlGenerator`, modeling Redshift's `COPY` from S3 and avoiding Postgres-only DDL.
5. **Client layer** -- `RedshiftAirbyteClient` for JDBC + IAM-role assumption for S3 staging.
6. **S3 staging data loading** -- Reuse the `load-object-storage` toolkit for the staging step (the one place where Redshift cannot do Direct Load without staging).
7. **Value coercion** -- `RedshiftValueCoercer` composing with `AirbyteValueCoercer`.
8. **Writer orchestration** -- Wire up `DirectLoadTableAppendStreamLoader`, `DirectLoadTableAppendTruncateStreamLoader`, `DirectLoadTableDedupTruncateStreamLoader`.
9. **Connection check** -- Decide OSS/Cloud-split vs formatter-injection (lean toward OSS/Cloud split per [§4.4](04-destination-postgres.md#44-the-check-operation-oss--cloud-split)).
10. **Testing** -- Port the acceptance suite incrementally, tracked by a per-test checklist (see lesson from [§2.6.2](02-bulk-cdk.md#262-acceptance-test-re-enabling-churn-clickhouse--postgres-rewrites)).
11. **Deployment** -- RC release, parallel run against legacy connector, cutover.

The plan is structured as an explicit application of the patterns learned from the prior migrations rather than a clean-room design.

## 5.5 Past Issues

### 5.5.1 Raw-tables-mode check failure ([PR #71273](https://github.com/airbytehq/airbyte/pull/71273))

#### How we got there

When Snowflake first migrated, the check operation was written before `legacyRawTablesOnly` mode existed. When the raw-tables mode was added, the check was not updated -- it continued to use the standard `SnowflakeRecordFormatter`, which doesn't emit `_airbyte_loaded_at`. Users who configured raw-tables-only mode saw their initial `Test connection` fail even though a real sync would succeed.

The bug also existed in Postgres -- the same PR fixed both.

#### What we did to fix it

1. Refactored `SnowflakeChecker` to inject the formatter via the constructor ([§5.1.2](#512-the-snowflakechecker-recordformatter-fix-pr-71273)).
2. Added Micronaut wiring that selects the mode-appropriate formatter at startup.
3. For Postgres, used the OSS/Cloud split rather than formatter injection ([§4.4](04-destination-postgres.md#44-the-check-operation-oss--cloud-split)) because the Postgres check is much simpler and doesn't need full formatter behavior.

#### Lessons

- **The check operation has to exercise the same code paths a real sync does**, including mode-specific formatters. Anything less and the check becomes a misleading green light.
- **Multiple connectors with the same shape of bug.** When you find a bug in one connector, immediately check whether the same pattern exists in sibling connectors -- the cost of a parallel-fix PR is low and the cost of a parallel-bug-discovered-by-a-customer is high.

### 5.5.2 Iceberg identifier-field ordering ([PR #74723](https://github.com/airbytehq/airbyte/pull/74723))

Documented inline in [§5.2.2](#522-deferred-identifier-field-update-on-column-replacement-pr-74723). The general lesson: when a destination has an **invariant** (Iceberg: "every identifier field must exist in the current schema"), schema-evolution code has to commit changes in an order that respects the invariant at every intermediate state, not just the final state.

## 5.6 Potential Improvements

### 5.6.1 Converge Snowflake and Postgres `Checker` shapes

**Current:** Snowflake's check uses constructor-injected formatter ([§5.1.2](#512-the-snowflakechecker-recordformatter-fix-pr-71273)); Postgres splits OSS/Cloud as separate classes ([§4.4](04-destination-postgres.md#44-the-check-operation-oss--cloud-split)). Both work, but they're divergent for no strong reason -- it's an accident of who wrote them when.

**With convergence:** Pick one shape and apply it everywhere. The Snowflake shape is more general (supports any per-mode dispatch); the Postgres shape is simpler. Either is defensible -- the value is in picking one so reviewers know which pattern to expect.

### 5.6.2 Bring `destination-iceberg` and `destination-s3-data-lake` together

**Current:** `destination-iceberg` is an empty husk (metadata + icon) and `destination-s3-data-lake` is the real connector. The duplication confuses users who search the registry for "iceberg".

**With a rename or alias:** Either delete the `destination-iceberg` entry entirely, or repurpose it as a thin alias that delegates to `destination-s3-data-lake`. The alias path is more disruptive (existing users with `iceberg` configs); the delete is cleaner if we're confident no one references it.

### 5.6.3 Push the SSH-tunnel logic into a CDK toolkit

**Current:** MSSQL's SSH-tunnel code ([§5.3](#53-destination-mssql-ssh-tunnel-pr-62078)) reuses the CDK's SSH primitives but lives in MSSQL's `DataSourceFactory`. Postgres and Redshift will want the same.

**With a toolkit module:** Add an `ssh-tunnel` helper to the `load-db` toolkit that takes a JDBC URL + an `SshTunnelMethod` and returns a rewritten URL + a session to close in teardown. The next connector that needs SSH adds one line of wiring instead of reproducing the MSSQL code.

Pragmatic note: §5.6.1 and §5.6.2 are tidying; do them when you're already in the area. §5.6.3 pays off at the third user of SSH tunnels; given Redshift is in planning ([§5.4](#54-destination-redshift-migration-plan)) and will need SSH, that's probably the right moment.

---

[Back to Index](../../KNOWLEDGE-TRANSFER.md)
