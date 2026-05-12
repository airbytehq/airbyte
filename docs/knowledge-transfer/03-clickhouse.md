# Destination ClickHouse

The ClickHouse destination was rewritten from scratch on the Bulk CDK between June and September 2025. The connector directory is [`airbyte-integrations/connectors/destination-clickhouse/`](../../airbyte-integrations/connectors/destination-clickhouse) (the rewrite reused the original directory name -- there is **no `destination-clickhouse-v2`** directory). Current docker image: `2.1.23`.

> *Quick file reference: [Appendix §8.2 -- Destination ClickHouse](08-appendix-key-file-paths.md#82-destination-clickhouse).*

## Introduction

The legacy ClickHouse destination was a Java connector built on the old Java CDK. It worked but had three operational problems that compounded:

1. **Tightly coupled to staging.** It wrote to an S3 staging bucket first and then `COPY`-ed into ClickHouse, which made the data path slow and required extra credentials.
2. **No real schema evolution.** When the source catalog added a column, the destination didn't pick it up; users had to manually drop and recreate the table.
3. **Hard to extend.** Adding ClickHouse-specific features (custom engine choices, JSON-as-String, cluster-aware connections) meant overriding deep class hierarchies in the old CDK.

The rewrite kept the same connector definition ID (`ce0d828e-1dc4-496c-b122-2da42e637e48` in [`metadata.yaml`](../../airbyte-integrations/connectors/destination-clickhouse/metadata.yaml)) so existing users transitioned in place. The work shipped in roughly four phases:

1. **Abstraction + spec.** [#61354](https://github.com/airbytehq/airbyte/pull/61354) introduced the connector skeleton; [#61510](https://github.com/airbytehq/airbyte/pull/61510), [#62047](https://github.com/airbytehq/airbyte/pull/62047) finalized the spec.
2. **Schema, dedup, truncate.** [#61558](https://github.com/airbytehq/airbyte/pull/61558) and [#66143](https://github.com/airbytehq/airbyte/pull/66143) added schema-change support; [#61696](https://github.com/airbytehq/airbyte/pull/61696) added dedup; [#61679](https://github.com/airbytehq/airbyte/pull/61679) added truncate.
3. **Types.** [#62100](https://github.com/airbytehq/airbyte/pull/62100) added JSON support (as `String`); [#66134](https://github.com/airbytehq/airbyte/pull/66134) changed decimal handling.
4. **Hardening.** [#62447](https://github.com/airbytehq/airbyte/pull/62447) fixed temp-table behavior, [#63721](https://github.com/airbytehq/airbyte/pull/63721) fixed PK table alter, [#63760](https://github.com/airbytehq/airbyte/pull/63760) improved error messages, [#64104](https://github.com/airbytehq/airbyte/pull/64104) made batch size configurable, [#64881](https://github.com/airbytehq/airbyte/pull/64881) wired teardown, [#65117](https://github.com/airbytehq/airbyte/pull/65117) fixed column mapping.

## 3.1 Connector layout

Package root: [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse). The directory matches the Bulk-CDK connector skeleton one-to-one:

| Subpackage | Purpose | Key files |
|------------|---------|-----------|
| `spec/` | Connector spec + parsed config | `ClickhouseSpecification.kt`, `ClickhouseConfiguration.kt` |
| `config/` | Micronaut bean factories | `ClickhouseBeanFactory.kt`, `ClickhouseDirectLoadDatabaseInitialStatusGatherer.kt` |
| `client/` | JDBC + SQL generation | `ClickhouseAirbyteClient.kt`, `ClickhouseSqlGenerator.kt`, `ClickhouseSqlTypes.kt` |
| `schema/` | Schema/column mapping | `ClickhouseTableSchemaMapper.kt`, `ClickhouseNamingUtils.kt` |
| `write/` | Write path | `ClickHouseWriter.kt`, `load/BinaryRowInsertBuffer.kt`, `transform/ClickhouseCoercer.kt` |
| `check/` | Connection check | `ClickhouseChecker.kt` |
| `dataflow/` | Aggregation hook | `ClickhouseAggregate.kt` |
| `model/` | Domain types | `AlterationSummary.kt` |

Top-level: `ClickhouseDestination.kt` (Micronaut entry point).

## 3.2 The Writer

`ClickHouseWriter` -- [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/ClickHouseWriter.kt:23`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/ClickHouseWriter.kt) implements `DestinationWriter`. It does two things:

1. **`setup()`** (line 31) -- creates the destination namespace (database) for every stream in the catalog and gathers initial status (does the table exist already? what's its current schema?) via `ClickhouseDirectLoadDatabaseInitialStatusGatherer`.
2. **`createStreamLoader(stream)`** (line 39) -- picks one of two Bulk-CDK loaders:
   - `DirectLoadTableAppendStreamLoader` when `stream.minimumGenerationId == 0L` (incremental / append).
   - `DirectLoadTableAppendTruncateStreamLoader` when `stream.minimumGenerationId == stream.generationId` (full-refresh).
   - Anything else throws `SystemErrorException("Cannot execute a hybrid refresh ...")`.

Note that **`DirectLoadTableDedupTruncateStreamLoader` is not used** -- dedup is solved differently (see [§3.4](#34-dedup-via-replacingmergetree-not-temp-table-swap)).

## 3.3 SQL generation, table engine, naming

`ClickhouseSqlGenerator` -- [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt) produces every DDL/DML statement. Notable shapes:

| Statement | Method | Notes |
|-----------|--------|-------|
| `CREATE TABLE` | `createTable` | Always includes the four Airbyte metadata columns (`_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_meta`, `_airbyte_generation_id`) plus the user's columns. Engine depends on import type ([§3.4](#34-dedup-via-replacingmergetree-not-temp-table-swap)). |
| `DROP TABLE IF EXISTS` | `dropTable` (line 88) | Quotes namespace + name with backticks. |
| `EXCHANGE TABLES` | `exchangeTable` (line 91) | Atomic table swap, used to install a freshly-built table over the previous one on truncate. |
| `INSERT INTO ... FROM` | `copyTable` (line 99) | Intersection-only copy ([#63751](https://github.com/airbytehq/airbyte/pull/63751)): the column list is the intersection of source and destination columns so adding a column doesn't break the copy. |

Names go through `ClickhouseNamingUtils` to apply ClickHouse-compatible quoting (backtick on every identifier) and length limits ([#63724](https://github.com/airbytehq/airbyte/pull/63724)).

## 3.4 Dedup via `ReplacingMergeTree`, not temp-table swap

ClickHouse has a native engine for "keep only the latest version of each row" semantics -- `ReplacingMergeTree(<version_column>)` -- and the rewrite leans on it instead of the Bulk-CDK temp-table-swap pattern used by Snowflake / Postgres.

The choice happens at table-create time in `ClickhouseSqlGenerator.createTable` ([`ClickhouseSqlGenerator.kt:51-71`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt)):

```kotlin
val engine = when (tableSchema.importType) {
    is Dedupe -> {
        // pick the cursor column as the version column if it's a valid type;
        // otherwise fall back to _airbyte_extracted_at
        val cursor = tableSchema.getCursor().firstOrNull()
        val useCursorAsVersion = cursor != null && isValidVersionColumn(cursor, cursorType)
        val versionColumn = if (useCursorAsVersion) "`$cursor`" else COLUMN_NAME_AB_EXTRACTED_AT
        "ReplacingMergeTree($versionColumn)"
    }
    else -> "MergeTree()"
}
```

For `Dedupe` streams the `ORDER BY` clause is the primary key list; for everything else it is `_airbyte_raw_id`.

**Implication:** ClickHouse-side dedup is **eventual**. `ReplacingMergeTree` collapses duplicates during background merges and during `OPTIMIZE FINAL` -- a fresh `SELECT *` may still return duplicates until a merge runs. This is by design; the alternative was to run a full upsert with a temp table, which doesn't scale well in ClickHouse (no per-row updates without `ALTER ... UPDATE`).

## 3.5 JSON, decimals, and the type system

| Source type | Destination type | PR | Rationale |
|-------------|------------------|----|-----------|
| `object` / `array` | `String` | [#62100](https://github.com/airbytehq/airbyte/pull/62100) | ClickHouse has a native `JSON` type but it was unstable at the time of the rewrite; serializing to a JSON string keeps the data round-trippable. |
| `number` | `Decimal` (with precision/scale) | [#66134](https://github.com/airbytehq/airbyte/pull/66134) | Switched away from `Float64` because precision loss caused acceptance-test failures for monetary data. |
| `integer` | `Int64` | -- | Standard. |
| `string` | `String` | -- | Standard. |
| `boolean` | `Bool` | -- | Standard. |

The mapping lives in [`ClickhouseSqlTypes.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlTypes.kt) and the value-side conversion lives in [`ClickhouseCoercer`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/transform/ClickhouseCoercer.kt).

## 3.6 Past Issues

### 3.6.1 Temp table left behind on failure ([PR #62447](https://github.com/airbytehq/airbyte/pull/62447))

#### How we got there

Before [§2.6.1](02-bulk-cdk.md#261-temp-tables-leaking-across-failed-retries-pr-74715)'s framework-level fix, ClickHouse had its own connector-level version of the same bug. The truncate path created a temp table and used `EXCHANGE TABLES` to swap it into the real name; if the sync failed before the exchange, the temp table stayed around and the next attempt would either fail at `CREATE` (table exists) or overwrite stale data.

#### What we did to fix it

1. Added explicit `DROP TABLE IF EXISTS` for the temp table at the start of every sync.
2. Made the exchange-or-drop logic explicit in `ClickHouseWriter` and `ClickhouseAirbyteClient`.
3. Eventually folded into the broader CDK-level fix in [#74715](https://github.com/airbytehq/airbyte/pull/74715), which now applies the success/failure gate uniformly across every Bulk-CDK destination.

#### Lessons

- **Connector-level fixes are valuable but eventually want to live in the CDK.** The original ClickHouse fix worked but only protected ClickHouse; Postgres and Snowflake had the same shape of bug and needed their own fixes until the CDK-level one shipped.
- **The defensive `DROP IF EXISTS` at sync start is cheap and worth keeping** even after the CDK-level fix, because it also protects against orphan temp tables from older connector versions still in production.

### 3.6.2 Column mapping mismatches on schema change ([PR #65117](https://github.com/airbytehq/airbyte/pull/65117))

#### How we got there

ClickHouse identifier rules are stricter than Airbyte's (no dots, length limits) and the connector applies its own naming policy via `ClickhouseNamingUtils`. When the source catalog renamed a column, the destination was using the **source name** in some places (intersection check) and the **mapped name** in others (insert), so on schema change the intersection-copy would drop the renamed column silently.

#### What we did to fix it

1. Centralized the source-to-final-column-name mapping in `ColumnNameMapping` (from the Bulk CDK).
2. Made every SQL generator method take the `ColumnNameMapping` explicitly so source-vs-final names couldn't be confused at a call site.
3. Added schema-change tests covering rename + add-column + drop-column combinations ([#66143](https://github.com/airbytehq/airbyte/pull/66143)).

#### Lessons

- **Pass the mapping, don't reconstruct it.** Every place that produced a name was a place a future rename could go wrong.
- **Acceptance tests need to cover schema *change* explicitly, not just the initial schema** -- the original test suite mostly created a fresh table per test, which never exercised the rename path.

## 3.7 Potential Improvements

### 3.7.1 Native ClickHouse `JSON` type

**Current:** JSON/object/array columns are serialized to `String` ([§3.5](#35-json-decimals-and-the-type-system)). Users who want to query nested fields in ClickHouse have to parse the string client-side or use ClickHouse's `JSONExtract*` functions.

**With native JSON:** ClickHouse 24.x stabilized its native `JSON` type. Switching the destination column type to `JSON` would let users write `SELECT data.user.email FROM ...` directly. The migration is non-trivial because existing tables would need to be re-created (column type can't be altered from `String` to `JSON` in-place), so the rollout path is opt-in via the spec.

### 3.7.2 Cluster-aware DDL (`ON CLUSTER ...`)

**Current:** Every DDL statement targets the local node. In a replicated cluster, the user has to either set up `Distributed` tables manually or run the connector against the master node and rely on replication.

**With cluster-aware DDL:** Add an `On Cluster` field to the spec. When set, the generator appends `ON CLUSTER <name>` to `CREATE`, `DROP`, and `EXCHANGE` statements, so the destination works natively on replicated clusters.

### 3.7.3 Migrate to `DirectLoadTableDedupTruncateStreamLoader`

**Current:** Dedup is delegated to `ReplacingMergeTree` ([§3.4](#34-dedup-via-replacingmergetree-not-temp-table-swap)), which gives eventual semantics. Users who want strict dedup-on-write have to run `OPTIMIZE FINAL` manually.

**With temp-table dedup:** Wire `DirectLoadTableDedupTruncateStreamLoader` for dedup streams, like Snowflake does. The cost is more SQL traffic per batch; the benefit is post-sync queries see deduplicated data immediately.

Pragmatic note: I would not pursue any of these without a customer signal. `ReplacingMergeTree` + `String` JSON is the cheapest correct choice; the improvements above are pure capability extensions, not bug fixes.

---

[Back to Index](../../KNOWLEDGE-TRANSFER.md)
