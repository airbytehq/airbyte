# Destination Postgres

A migration of the Postgres destination to the Bulk CDK using the **Direct Load** pattern: no S3/GCS staging, the connector writes directly via JDBC. The work ran from October 2025 through January 2026; the connector lives at [`airbyte-integrations/connectors/destination-postgres/`](../../airbyte-integrations/connectors/destination-postgres). Current docker image: `3.0.13`.

> *Quick file reference: [Appendix §8.3 -- Destination Postgres](08-appendix-key-file-paths.md#83-destination-postgres).*

## Introduction

The legacy Postgres destination was a Java connector built on the old Java CDK with the same architectural problems as the legacy ClickHouse one ([§3](03-clickhouse.md)), plus an additional Postgres-specific cost: it ran every write through a staging step even though Postgres is a transactional database and can absorb writes directly. The Bulk-CDK migration shipped Direct Load -- batched JDBC inserts with optional dedup via temp-table upsert -- and reused the same connector ID (`25c5221d-dce2-4163-ade9-739ef790f503` in [`metadata.yaml`](../../airbyte-integrations/connectors/destination-postgres/metadata.yaml)) so existing users transitioned in place.

The migration shipped in roughly four phases:

1. **Acceptance harness.** [#67592](https://github.com/airbytehq/airbyte/pull/67592), [#67596](https://github.com/airbytehq/airbyte/pull/67596) set up the acceptance test framework before any real connector code shipped.
2. **Spec + value coercion.** [#68117](https://github.com/airbytehq/airbyte/pull/68117) defined the spec; [#68126](https://github.com/airbytehq/airbyte/pull/68126) implemented the Postgres value coercer; [#68123](https://github.com/airbytehq/airbyte/pull/68123) added the Postgres test-fixture init script.
3. **Raw-tables mode + RC.** [#68580](https://github.com/airbytehq/airbyte/pull/68580) implemented raw-tables-only mode (see [§4.3](#43-raw-tables-only-mode)); [#69846](https://github.com/airbytehq/airbyte/pull/69846) shipped the first RC.
4. **Hardening + refactor.** [#70326](https://github.com/airbytehq/airbyte/pull/70326), [#70337](https://github.com/airbytehq/airbyte/pull/70337), [#70347](https://github.com/airbytehq/airbyte/pull/70347), [#70348](https://github.com/airbytehq/airbyte/pull/70348), [#70364](https://github.com/airbytehq/airbyte/pull/70364), [#71146](https://github.com/airbytehq/airbyte/pull/71146), [#71163](https://github.com/airbytehq/airbyte/pull/71163), [#71183](https://github.com/airbytehq/airbyte/pull/71183) hardened the connector and refactored the schema utilities to match Snowflake's pattern.

## 4.1 Connector layout

Package root: [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres).

| Subpackage | Purpose | Key files |
|------------|---------|-----------|
| `spec/` | Spec + parsed config | `PostgresSpecification.kt`, `PostgresConfiguration.kt` |
| `config/` | Micronaut bean factories | -- |
| `client/` | JDBC client | `PostgresAirbyteClient.kt` |
| `sql/` | SQL generation | `PostgresDirectLoadSqlGenerator.kt` |
| `schema/` | Schema mapping + column management | `PostgresTableSchemaMapper.kt`, `PostgresColumnManager.kt`, `PostgresNamingUtils.kt` |
| `write/` | Write path | `PostgresWriter.kt`, `load/PostgresInsertBuffer.kt` |
| `check/` | Connection check (OSS / Cloud split) | `PostgresOssChecker.kt`, `PostgresCloudChecker.kt` |
| `dataflow/` | Aggregation hook | -- |

Top-level: `PostgresDestinationV2.kt` (Micronaut entry point; the "V2" is in the class name, not the directory).

## 4.2 The `PostgresColumnUtils` deletion and schema refactor ([PR #71183](https://github.com/airbytehq/airbyte/pull/71183))

The early Postgres connector concentrated all column-name and type-mapping logic in a single `PostgresColumnUtils.kt` static-helper file. As the connector matured, this single class accreted nearly every cross-cutting concern -- mapping, quoting, type inference, alteration planning -- and became hard to test in isolation.

[#71183](https://github.com/airbytehq/airbyte/pull/71183) **deleted `PostgresColumnUtils.kt`** entirely and replaced it with three injectable classes that mirror the Snowflake pattern:

| New class | Path | Responsibility |
|-----------|------|----------------|
| `PostgresTableSchemaMapper` | [`schema/PostgresTableSchemaMapper.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresTableSchemaMapper.kt) | Maps Airbyte stream schema → Postgres table schema. Mode-aware (raw vs full). |
| `PostgresColumnManager` | [`schema/PostgresColumnManager.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresColumnManager.kt) | Plans column add/drop/alter operations. |
| `PostgresNamingUtils` | [`schema/PostgresNamingUtils.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresNamingUtils.kt) | Identifier quoting and length-limit handling. |

This is the canonical example of "follow the existing pattern, even if the connector was first" -- when Snowflake migrated first and converged on this trio, Postgres followed even at the cost of a non-trivial refactor.

## 4.3 Raw-tables-only mode

Postgres supports two write modes:

| Mode | Spec field | What lands in the destination |
|------|------------|-------------------------------|
| **Full mode** | `legacyRawTablesOnly = false` (default) | Final typed table with one column per source field, plus Airbyte metadata columns |
| **Raw-tables-only mode** | `legacyRawTablesOnly = true` | A single `_airbyte_data jsonb` column per stream, plus Airbyte metadata columns -- no typing |

The flag is on [`PostgresSpecification.kt:41`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresSpecification.kt) (abstract; defaults at lines 155 and 305) and surfaced on [`PostgresConfiguration.kt:24, 53`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresConfiguration.kt). It is consulted everywhere a typed-vs-raw decision is made:

- [`write/PostgresWriter.kt:65-69`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/write/PostgresWriter.kt) -- which loader to construct
- [`write/load/PostgresInsertBuffer.kt:39`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/write/load/PostgresInsertBuffer.kt) -- raw-payload buffering
- [`schema/PostgresTableSchemaMapper.kt:43, 67, 105`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresTableSchemaMapper.kt) -- skip typed columns
- [`schema/PostgresColumnManager.kt:43, 56`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresColumnManager.kt) -- never alter user columns
- [`sql/PostgresDirectLoadSqlGenerator.kt:107-120`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/sql/PostgresDirectLoadSqlGenerator.kt) -- generate raw-mode `CREATE TABLE`
- [`client/PostgresAirbyteClient.kt:145, 188`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/client/PostgresAirbyteClient.kt) -- client-side dispatch

### 4.3.1 Dedup is forced to Append in raw mode ([PR #70364](https://github.com/airbytehq/airbyte/pull/70364))

In raw-tables-only mode, there is no typed column to dedup against. If a user configures a stream with `DestinationSyncMode.APPEND_DEDUP` and `legacyRawTablesOnly = true`, the writer **forces the import type to `Append`**. The dedup semantics are simply not achievable in raw mode; emitting an error would surprise users who toggled the flag without understanding the implication. The behavior is intentional but is the kind of "fine print" worth flagging in support tickets.

## 4.4 The check operation: OSS / Cloud split

Unlike Snowflake ([§5.1.2](05-other-destinations.md#512-the-snowflakechecker-recordformatter-fix)), Postgres splits its check into two implementations rather than using a single check class with an injected formatter:

| Class | Active in | Path |
|-------|-----------|------|
| `PostgresOssChecker` | OSS only (`@Requires(notEnv = [AIRBYTE_CLOUD_ENV])`) | [`check/PostgresOssChecker.kt:35`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/check/PostgresOssChecker.kt) |
| `PostgresCloudChecker` | Cloud (no env restriction) | [`check/PostgresCloudChecker.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/check/PostgresCloudChecker.kt) |

Each checker builds a small synthetic `ObjectType` test record by hand (see lines 41-51 of `PostgresOssChecker.kt`) rather than reusing a connector-side `RecordFormatter` -- the Postgres check is intentionally minimal (`test_key` + Airbyte metadata only) and doesn't need full schema processing. This is **a deliberate departure from the Snowflake pattern**: Snowflake needs the formatter because its check has to round-trip through the same value-coercion path as a real write; Postgres's check can stay simpler.

## 4.5 Schema evolution: CASCADE and `ALTER COLUMN TYPE` ([PR #71146](https://github.com/airbytehq/airbyte/pull/71146))

Postgres has two operations that look similar but need different CASCADE handling:

| Operation | CASCADE? | Why |
|-----------|----------|-----|
| `ALTER TABLE ... DROP COLUMN ...` | Yes -- `DROP COLUMN ... CASCADE` if `cascadeDropForColumnRemoval = true` ([`PostgresDirectLoadSqlGenerator.kt:34, 595`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/sql/PostgresDirectLoadSqlGenerator.kt)) | A dropped column may have dependent views / indexes; CASCADE silently drops them. User opts in via spec. |
| `ALTER TABLE ... ALTER COLUMN ... TYPE ...` | **No CASCADE** ([`PostgresDirectLoadSqlGenerator.kt:599-619`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/sql/PostgresDirectLoadSqlGenerator.kt)) | A type change should not silently drop dependent objects -- the user should know if a view they own references a column whose type just changed. |

Earlier code applied CASCADE to both. The fix narrowed CASCADE to `DROP COLUMN` only. The `ALTER COLUMN TYPE` path now also constructs a smart `USING` clause:

```kotlin
val usingClause = when {
    newType == "jsonb" -> "USING to_jsonb($quotedName)"
    oldType == "jsonb" && newType in setOf("varchar", "text", "character varying") -> "USING $quotedName #>> '{}'"
    else -> "USING $quotedName::$newType"
}
```

This handles two real cases that bit users:
- **Converting to `jsonb`** from a text column with valid JSON content -- the cast `text → jsonb` requires `to_jsonb` to wrap the value, not just `::jsonb`, which fails on numeric strings.
- **Converting from `jsonb` to `text`** -- a plain `::text` would render `"foo"` as `"\"foo\""` (with quotes); `#>> '{}'` extracts the raw text.

User-facing CASCADE option: [`PostgresSpecification.kt:157, 307`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresSpecification.kt). Error guidance for CASCADE failures: [`PostgresAirbyteClient.kt:455-465`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/client/PostgresAirbyteClient.kt).

## 4.6 Past Issues

### 4.6.1 Index recreation on non-existent columns ([PRs #70326](https://github.com/airbytehq/airbyte/pull/70326), [#70337](https://github.com/airbytehq/airbyte/pull/70337), [#70347](https://github.com/airbytehq/airbyte/pull/70347))

#### How we got there

In raw-tables-only mode ([§4.3](#43-raw-tables-only-mode)), there are no typed columns. The early index-creation code was running unconditionally and tried to create a primary-key index on `_airbyte_raw_id` and the dedup columns -- but the dedup columns don't exist in raw mode, so the `CREATE INDEX` statement failed with `column "..." does not exist` on first run, and again on every re-run because the index-recreation path was triggered by schema-change detection.

#### What we did to fix it

1. **[#70326](https://github.com/airbytehq/airbyte/pull/70326)** -- gated index creation on `legacyRawTablesOnly == false` at the immediate call site.
2. **[#70337](https://github.com/airbytehq/airbyte/pull/70337)** -- moved the raw-tables check **out** of the call sites and **into** the index-creation method itself, so adding a future caller wouldn't accidentally re-introduce the bug.
3. **[#70347](https://github.com/airbytehq/airbyte/pull/70347)** -- fixed the index-recreation path (the schema-change branch had been overlooked; same fix as #70337 but on the recreate-after-alter path).

#### Lessons

- **Defensive checks belong inside the method, not at every call site.** The same bug showed up in two places because the gate was at the caller; moving it inside the callee made the second occurrence impossible.
- **Raw-tables-only mode needs to be tested as a first-class mode, not a flag-flipped variant.** Most acceptance tests ran in full mode; the bug shipped because no test exercised raw mode + schema change.

### 4.6.2 The schema-utility monolith ([PR #71183](https://github.com/airbytehq/airbyte/pull/71183) -- design tax, not an incident)

Not a customer-visible incident but worth recording as a pattern lesson. The original `PostgresColumnUtils.kt` worked correctly but accumulated every Postgres-specific bit of schema knowledge in one file. Each new feature (CASCADE drop, smart `USING` clause, raw-mode gating) added another method to the monolith. By PR #70347 it was clear that the file was the bottleneck on every schema change.

The fix was to delete it and split the concerns into the three classes documented in [§4.2](#42-the-postgrescolumnutils-deletion-and-schema-refactor-pr-71183). The lesson is to **converge on the same shape as a sibling connector when one exists** -- Snowflake had the trio first, Postgres should have mirrored it from the start rather than building a parallel-but-different abstraction.

## 4.7 Potential Improvements

### 4.7.1 Cloud-pre-check the OSS/Cloud split

**Current:** [§4.4](#44-the-check-operation-oss--cloud-split) splits checks via `@Requires(notEnv = [AIRBYTE_CLOUD_ENV])`. At runtime, exactly one of `PostgresOssChecker` and `PostgresCloudChecker` exists in the Micronaut context, and the other is filtered out by environment. This works but is invisible at PR-review time -- it's easy to add a method to one and forget the other.

**With a shared base class:** Extract a `PostgresChecker` interface (or `AbstractPostgresChecker` base) that both implementations conform to. The Cloud-only behavior lives in `PostgresCloudChecker.checkCloudSpecifics()`; OSS overrides it as a no-op. This makes the divergence reviewable in one place and gives a single API surface for users of either flavor.

### 4.7.2 Move the index-creation gate further down

**Current:** [§4.6.1](#461-index-recreation-on-non-existent-columns-prs-70326-70337-70347)'s fix moved the raw-mode gate into the index-creation method. That's good, but the same gate is repeated in `PostgresAirbyteClient`, `PostgresTableSchemaMapper`, and `PostgresColumnManager`.

**With a typed write-mode object:** Encode the mode as a `WriteMode` sealed class (`Full(...)`, `RawOnly(...)`) and dispatch on it at the writer-construction boundary, not at the every-method boundary. The downstream classes don't take a flag, they take the mode-specific arguments. This is the same direction as the Snowflake refactor that pushed the formatter out of the checker.

### 4.7.3 Push the `USING`-clause matrix to the CDK

**Current:** [§4.5](#45-schema-evolution-cascade-and-alter-column-type-pr-71146)'s smart `USING` clause lives in `PostgresDirectLoadSqlGenerator`. The same problem -- "produce a safe CAST when changing a column type" -- exists in MSSQL and would exist in Redshift.

**With a CDK abstraction:** Add `TypeConversionSql` to the Bulk CDK's `load-db` toolkit, parameterized by source and target dialect. Each connector contributes its own conversion table; the generator picks the matching entry. The cost is the abstraction itself; the benefit is that the next connector inherits the same hard-won corner cases.

Pragmatic note: §4.7.1 and §4.7.2 are clean-up rather than capability work. §4.7.3 only pays off once we have a third or fourth connector hitting the same problem -- premature today, worth revisiting at Redshift.

---

[Back to Index](../../KNOWLEDGE-TRANSFER.md)
