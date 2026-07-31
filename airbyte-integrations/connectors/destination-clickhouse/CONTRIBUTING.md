# Deduplication & Primary Keys in `destination-clickhouse`

This document describes how the ClickHouse destination implements deduplication and
how it declares primary-key-like constructs, and contrasts that with the other
Bulk-CDK destinations on the same CDK family (`cdkVersion=1.0.x`).

All references point to code in this repository at the time of writing
(`destination-clickhouse` is on `cdkVersion=1.0.13`, see
`gradle.properties:1`).

---

## 1. TL;DR

| Topic | ClickHouse | Postgres / MSSQL / Snowflake / BigQuery / Redshift |
| --- | --- | --- |
| Dedup mechanism | **Engine-level**, lazy: `ReplacingMergeTree(version)` collapses duplicates in the background | **Query-level**, eager: `MERGE` / writable CTE / multi-statement script driven by `ROW_NUMBER() OVER (PARTITION BY pk ORDER BY cursor DESC, _airbyte_extracted_at DESC)` |
| `upsertTable()` impl | Throws `NotImplementedError("We rely on Clickhouse's table engine for deduping")` (`ClickhouseAirbyteClient.kt:96`) | Real SQL that runs at upsert time |
| Dedup happens... | Asynchronously, on merge, may take time after insert | Synchronously, inside the upsert call |
| PK keyword used in `CREATE TABLE` | `ORDER BY (<pks>)` on a `ReplacingMergeTree` engine | None of them use `PRIMARY KEY`. They use either nothing, a side index, or `CLUSTER BY` |
| Extra structure declared at table-creation time | Engine choice (`MergeTree` vs `ReplacingMergeTree`) plus `ORDER BY` | Optional side index (Postgres/MSSQL) or clustering (BigQuery) |

---

## 2. How ClickHouse deduplicates

### 2.1 The two engines this connector emits

`ClickhouseSqlGenerator.createTable` (`ClickhouseSqlGenerator.kt:27`) chooses the
table engine based on the stream's import type:

```kotlin
// ClickhouseSqlGenerator.kt:51-71
val engine =
    when (tableSchema.importType) {
        is Dedupe -> {
            // ...resolve version column from cursor or fall back to _airbyte_extracted_at
            "ReplacingMergeTree($versionColumn)"
        }
        else -> "MergeTree()"
    }
```

- **Append / overwrite streams** -> `MergeTree()`
- **Dedup streams** -> `ReplacingMergeTree(<version>)`

The `<version>` argument is what ClickHouse uses to decide which row "wins"
among duplicates with the same sort key. The connector picks the version column
as follows (`ClickhouseSqlGenerator.kt:55-67`):

1. If the stream's cursor exists and is one of `Int64`, `Date32`, `DateTime64(3)`
   (see `ClickhouseSqlTypes.VALID_VERSION_COLUMN_TYPES`), the cursor itself is the
   version column.
2. Otherwise, `_airbyte_extracted_at` is used as the version column.

The validation lives in `isValidVersionColumn` (`ClickhouseSqlTypes.kt:29`):

```kotlin
fun isValidVersionColumn(name: String, type: String) =
    // CDC cursors cannot be used as a version column since they are null
    // during the initial CDC snapshot.
    name != CDC_CURSOR_COLUMN && VALID_VERSION_COLUMN_TYPES.contains(type)
```

CDC cursors are explicitly excluded because they are `NULL` during the initial
snapshot, which would break the version semantics.

### 2.2 The ORDER BY clause IS the dedup key

The `CREATE TABLE` statement (`ClickhouseSqlGenerator.kt:73-83`) ends with:

```kotlin
"""
CREATE $forceCreateTable TABLE `${tableName.namespace}`.`${tableName.name}` (
  ...
  $columnDeclarations
)
ENGINE = $engine
ORDER BY ($orderBy)
"""
```

where `$orderBy` is:

- `_airbyte_raw_id` for non-dedup streams
- the joined primary key columns for dedup streams
  (`ClickhouseSqlGenerator.kt:40-49`)

In ClickHouse, `ORDER BY` on a `*MergeTree` engine is both the sorting key and
the implicit primary key/sparse index. For `ReplacingMergeTree`, rows that share
the same `ORDER BY` tuple are considered duplicates, and the row with the
largest version wins on merge.

### 2.3 No upsert SQL is generated

`ClickhouseAirbyteClient.upsertTable` (`ClickhouseAirbyteClient.kt:90-97`)
deliberately does nothing:

```kotlin
override suspend fun upsertTable(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    sourceTableName: TableName,
    targetTableName: TableName
) {
    throw NotImplementedError("We rely on Clickhouse's table engine for deduping")
}
```

So the path that on Postgres or Snowflake would `MERGE` / `UPDATE` / `INSERT`
duplicate-resolved rows is simply not exercised on ClickHouse. Instead, the
connector inserts every row (including duplicates) into the final table, and
ClickHouse's `ReplacingMergeTree` collapses them later, on merge.

### 2.4 NOT NULL on PK + version, by construction

Because `ReplacingMergeTree` cannot handle `NULL` values in the sort key or
version column safely, `ClickhouseTableSchemaMapper.toFinalSchema`
(`ClickhouseTableSchemaMapper.kt:86-120`) forcibly strips nullability from:

- every primary key column
- the cursor column, **if** it is a valid version column

This is unique to ClickHouse: other destinations let PK columns stay nullable
because their dedup query can tolerate `NULL`s with `IS NULL` joins or
`NULLS LAST` ordering. (The MERGE generators for Snowflake/BigQuery have
explicit `OR (a IS NULL AND b IS NULL)` join branches; ClickHouse's engine
does not.)

### 2.5 Eventual-consistency caveat

`ReplacingMergeTree` is **eventually** deduplicated. A `SELECT *` immediately
after a sync can return both old and new copies until a background merge runs.
Users that need a deduplicated view must either:

- query with `SELECT ... FINAL`,
- force `OPTIMIZE TABLE ... FINAL`, or
- be aware that the deduplication is lazy.

This is a fundamental behavioural difference compared to every other
destination in the comparison: on Postgres / MSSQL / Snowflake / BigQuery /
Redshift, when `upsertTable()` returns successfully the final table is
immediately deduplicated.

---

## 3. How the other Bulk-CDK destinations deduplicate

All destinations listed below are on `cdkVersion` close to ClickHouse's
`1.0.13`:

| Destination | `cdkVersion` |
| --- | --- |
| destination-clickhouse | 1.0.13 |
| destination-bigquery | 1.0.13 |
| destination-redshift | 1.0.13 |
| destination-snowflake | 1.0.13 |
| destination-mssql | 1.0.11 |
| destination-postgres | 1.0.9 |

The five non-ClickHouse destinations share the same conceptual recipe:

1. Land raw rows into a staging/temp table (per the Bulk-CDK direct-load flow).
2. Run a **single deterministic dedup expression** based on `ROW_NUMBER()`
   partitioned by the primary key and ordered by `cursor DESC NULLS LAST,
   _airbyte_extracted_at DESC`.
3. Merge / update / insert that deduped row set into the final table.

The differences between them are syntactic, not conceptual.

### 3.1 Postgres - writable CTE

`PostgresDirectLoadSqlGenerator.upsertTable`
(`PostgresDirectLoadSqlGenerator.kt:257-325`) emits a single statement of the
form:

```sql
WITH deduped_source AS (
    SELECT ... FROM (
      SELECT *, ROW_NUMBER() OVER (
        PARTITION BY <pk>
        ORDER BY <cursor> DESC NULLS LAST, "_airbyte_extracted_at" DESC
      ) AS row_number
      FROM <source>
    ) WHERE row_number = 1
),
deleted AS ( DELETE FROM target USING deduped_source WHERE ... ),  -- CDC only
updates AS ( UPDATE target SET ... FROM deduped_source WHERE ... )
INSERT INTO target (...)
SELECT ... FROM deduped_source
WHERE NOT EXISTS (SELECT 1 FROM target WHERE <pk match>);
```

### 3.2 MSSQL - MERGE

`MSSQLBulkLoadHandler` builds a global temp table `##TempTable_<ts>_<rand>`,
dedupes inside it with a `ROW_NUMBER()` CTE that `DELETE`s rows where
`row_num > 1`, then runs (`MSSQLBulkLoadHandler.kt:262-273`):

```sql
MERGE INTO [schema].[main] AS Target
USING [##TempTable_...] AS Source ON Target.[pk] = Source.[pk]
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT (...) VALUES (...);
```

### 3.3 Snowflake - MERGE with inline CTE

`SnowflakeDirectLoadSqlGenerator.upsertTable`
(`SnowflakeDirectLoadSqlGenerator.kt:123-242`) emits:

```sql
MERGE INTO <target> AS target_table
USING (
  WITH records AS (SELECT ... FROM <source>),
       numbered_rows AS (
         SELECT *, ROW_NUMBER() OVER (
           PARTITION BY <pk>
           ORDER BY <cursor> DESC NULLS LAST, "_AIRBYTE_EXTRACTED_AT" DESC
         ) AS row_number FROM records
       )
  SELECT ... FROM numbered_rows WHERE row_number = 1
) AS new_record
ON ... 
WHEN MATCHED AND <cursor cmp> THEN UPDATE ...
WHEN NOT MATCHED THEN INSERT ...;
```

### 3.4 BigQuery - MERGE with inline CTE

Same shape as Snowflake's MERGE; see
`BigqueryDirectLoadSqlGenerator.kt:131-233`.

### 3.5 Redshift - multi-statement script

Redshift does not support writable CTEs, so
`RedshiftSqlGenerator.upsertTable`
(`RedshiftSqlGenerator.kt:174-265`) materializes a `TEMP TABLE` and then runs
`DELETE` (CDC only), `UPDATE`, and `INSERT ... WHERE NOT EXISTS`, all wrapped
in a `BEGIN TRANSACTION; ... COMMIT;` block.

### 3.6 Summary of the dedup mechanism

| Destination | Dedup mechanism | `upsertTable()` implementation |
| --- | --- | --- |
| ClickHouse | Engine: `ReplacingMergeTree(version)` collapses duplicates lazily | Stub, throws `NotImplementedError` |
| Postgres | Writable CTE: `WITH deduped AS (ROW_NUMBER...) UPDATE / INSERT WHERE NOT EXISTS` | Real SQL |
| MSSQL | Bulk-load to global temp -> `ROW_NUMBER()` CTE delete -> `MERGE` | Real SQL (in `MSSQLBulkLoadHandler`) |
| Snowflake | Single `MERGE` with `WITH ... ROW_NUMBER()` inline CTE | Real SQL |
| BigQuery | Single `MERGE` with `WITH ... ROW_NUMBER()` inline CTE | Real SQL |
| Redshift | `BEGIN; CREATE TEMP TABLE _airbyte_dedup_...; UPDATE; INSERT WHERE NOT EXISTS; COMMIT;` | Real SQL |

---

## 4. How the "primary key" is declared

This is where ClickHouse is most visibly different.

### 4.1 None of the destinations use the SQL `PRIMARY KEY` keyword

A simple but striking finding: **no destination in this comparison declares
`PRIMARY KEY` in its `CREATE TABLE` statement**. The "primary key" is purely
a logical concept used to construct the dedup query, indexed however the
underlying engine prefers.

### 4.2 Per-destination PK syntax

| Destination | Syntax used in `CREATE TABLE` for the PK | Where |
| --- | --- | --- |
| **ClickHouse** | `ENGINE = ReplacingMergeTree(<version>) ORDER BY (<pks>)` | `ClickhouseSqlGenerator.kt:68, 82` |
| **Postgres** | None in `CREATE TABLE`; a separate `CREATE INDEX IF NOT EXISTS idx_pk_<table> ON ... (<pks>)` is emitted (non-unique B-tree index) | `PostgresDirectLoadSqlGenerator.kt:176` |
| **MSSQL** | None in `CREATE TABLE`; a separate `CREATE INDEX ... ON [schema].[table] (<pks>)` (non-clustered, non-unique) is emitted | `MSSQLQueryBuilder.kt:119-130, 442-475` |
| **Snowflake** | Nothing. Pure column declarations. (Snowflake does not enforce PKs anyway.) | `SnowflakeDirectLoadSqlGenerator.kt:90-95` |
| **BigQuery** | `PARTITION BY DATE_TRUNC(_airbyte_extracted_at, DAY) CLUSTER BY <first 3 pks>, _airbyte_extracted_at` | `BigqueryDirectLoadSqlGenerator.kt:80-92` |
| **Redshift** | Nothing. No `PRIMARY KEY`, no `DISTKEY`, no `SORTKEY`. | `RedshiftSqlGenerator.kt:91-92` |

### 4.3 What `ORDER BY` actually means in ClickHouse

In a `MergeTree`-family engine, the `ORDER BY` tuple is the only thing that
matters; ClickHouse uses it as:

- the **sorting key** of the data parts on disk,
- the **sparse primary index** (`primary.idx`),
- the **deduplication key** for `ReplacingMergeTree`.

ClickHouse also has a standalone `PRIMARY KEY` clause that lets users decouple
the index from the sorting key, but this connector does not use it - `ORDER BY`
is the single source of truth.

This means, on ClickHouse:

- The PK is the physical sort order. Re-defining it requires rebuilding the
  table.
- Adding, dropping, or changing nullability of a PK column is a
  *deduplication-affecting* change, which is exactly what
  `ClickhouseAirbyteClient.applyChangeset`
  (`ClickhouseAirbyteClient.kt:133-163`) detects via nullability changes and
  handles by recreating the table:

  ```kotlin
  // ClickhouseAirbyteClient.kt:140-150
  // This is a bit hacky, and relies on the fact that we make all
  // non-pk/cursor columns nullable.
  // We assume that if any column changes its nullability,
  // or we want to drop a non-nullable column,
  // this indicates a change in the PK/cursor, and therefore we need to
  // reconfigure the table engine.
  ```

  When such a change is detected, `applyDeduplicationChanges`
  (`ClickhouseAirbyteClient.kt:165-190`) creates a temp table with the new
  schema, copies the old data over, `EXCHANGE TABLES`, and drops the old one.

  No other destination in this comparison needs this dance, because none of them
  encode the PK into the physical storage layout.

### 4.4 Constraint on PK shape

`ClickhouseSqlGenerator.flattenPks`
(`ClickhouseSqlGenerator.kt:176-187`) only accepts top-level PKs:

```kotlin
internal fun flattenPks(primaryKey: List<List<String>>): List<String> {
    return primaryKey.map { fieldPath ->
        if (fieldPath.size != 1) {
            throw UnsupportedOperationException(
                "Only top-level primary keys are supported, got $fieldPath",
            )
        }
        fieldPath.first()
    }
}
```

Nested-path primary keys are rejected, again because the PK must end up as
column references in the `ORDER BY` of the table engine.

---

## 5. Implications for users

| Scenario | ClickHouse behaviour | Other destinations |
| --- | --- | --- |
| Reading immediately after a sync | May see duplicates until background merge runs; use `SELECT ... FINAL` if needed | Final table is already deduplicated |
| Cursor/PK column with `NULL` values | Sync fails (PK + version forced `NOT NULL`); needs schema fix upstream | Tolerated via `NULLS LAST` / `IS NULL` checks in the MERGE / CTE |
| Nested PK | Rejected with `UnsupportedOperationException` | Generally supported |
| PK / cursor column changes | Triggers a full table rebuild via `EXCHANGE TABLES` | Usually just an `ALTER TABLE` |
| Performance shape | Insert-only hot path is fast; dedup cost is paid asynchronously by ClickHouse merges | Each sync pays the dedup cost synchronously via `MERGE` / CTE / multi-statement script |

---

## 6. Where to look in the code

| Concern | File | Symbol |
| --- | --- | --- |
| Engine + `ORDER BY` selection | [`ClickhouseSqlGenerator.kt`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt) | [`createTable`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt#L27), [`flattenPks`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt#L176) |
| Version column rules | [`ClickhouseSqlTypes.kt`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlTypes.kt) | [`VALID_VERSION_COLUMN_TYPES`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlTypes.kt#L19), [`isValidVersionColumn`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlTypes.kt#L29) |
| NOT NULL enforcement for PK / cursor | [`ClickhouseTableSchemaMapper.kt`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/schema/ClickhouseTableSchemaMapper.kt) | [`toFinalSchema`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/schema/ClickhouseTableSchemaMapper.kt#L86) |
| Skipping `upsertTable` | [`ClickhouseAirbyteClient.kt`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt) | [`upsertTable`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt#L90) |
| Schema-evolution PK/cursor rebuild | [`ClickhouseAirbyteClient.kt`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt) | [`applyChangeset`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt#L133), [`applyDeduplicationChanges`](src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt#L165) |
