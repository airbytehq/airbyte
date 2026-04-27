# Knowledge Transfer - Benoit Moriceau

> This document summarizes the work done by Benoit Moriceau (`benmoriceau`) across the Airbyte codebase, spanning from mid-2022 to early 2026. It covers platform infrastructure, the Bulk CDK, destination connector migrations, and CI/CD tooling.

---

## Table of Contents

1. [Overview](#overview)
2. [Bulk CDK (Connector Development Kit)](#bulk-cdk-connector-development-kit)
3. [Destination Connectors](#destination-connectors)
   - [ClickHouse v2](#clickhouse-v2)
   - [Destination Postgres (Direct Load)](#destination-postgres-direct-load)
   - [Destination Snowflake](#destination-snowflake)
   - [Destination Redshift](#destination-redshift)
   - [Destination MSSQL](#destination-mssql)
   - [Iceberg / S3 Data Lake](#iceberg--s3-data-lake)
4. [Platform Infrastructure (2022)](#platform-infrastructure-2022)
5. [CI/CD and Tooling](#cicd-and-tooling)
6. [Key Patterns and Conventions](#key-patterns-and-conventions)
7. [Open / In-Progress Work](#open--in-progress-work)

---

## Overview

Across 125+ merged PRs, the work spans two major eras:

- **2022**: Platform-level infrastructure (Temporal workflows, per-stream state, orchestrator decoupling, protocol changes)
- **2025-2026**: Destination connector development on the Bulk CDK (ClickHouse v2, Postgres direct load, Snowflake migration, Iceberg fixes, Redshift migration planning, CI/CD automation)

---

## Bulk CDK (Connector Development Kit)

The Bulk CDK is the next-generation framework for building destination connectors. Much of the work has been focused on extending and hardening it.

### Core CDK Contributions

| Area | Key PRs | Description |
|------|---------|-------------|
| **Finalization step** | [#64555](https://github.com/airbytehq/airbyte/pull/64555) | Added a finalization stage to the CDK data pipeline, allowing connectors to perform cleanup/post-processing after sync completion. |
| **Dataflow pipeline tests** | [#64887](https://github.com/airbytehq/airbyte/pull/64887) | Added tests to all stages of the dataflow pipeline to improve reliability and catch regressions. |
| **Resource config** | [#64885](https://github.com/airbytehq/airbyte/pull/64885) | Added resource configuration support for the CDK, enabling connectors to customize resource allocation. |
| **Connector check improvements** | [#64919](https://github.com/airbytehq/airbyte/pull/64919), [#64890](https://github.com/airbytehq/airbyte/pull/64890) | Limited connector check scope and fixed CDK check behavior. |
| **CDK version management** | [#64567](https://github.com/airbytehq/airbyte/pull/64567) | Updated how the CDK version is checked and managed across connectors. |
| **Temp table cleanup** | [#74715](https://github.com/airbytehq/airbyte/pull/74715) | Fixed duplicate records caused by temp tables not being dropped after successful upsert in `DedupTruncateStreamLoader`. |
| **Jinjava dependency** | [#72959](https://github.com/airbytehq/airbyte/pull/72959) | Bumped Jinjava dependency for template rendering. |
| **Agent file** | [#64903](https://github.com/airbytehq/airbyte/pull/64903) | Added an AI agent configuration file for the Bulk CDK. |

### Architecture Notes

- The Bulk CDK uses a **pipeline-based architecture** with distinct stages: input, transformation, batching, writing, and finalization.
- Connectors built on the Bulk CDK implement interfaces for schema mapping, SQL generation, client operations, and value coercion.
- The CDK supports both **raw tables mode** and **schema mode** (typed tables with Airbyte metadata columns).
- The `DedupTruncateStreamLoader` handles upserts using temporary tables to ensure atomicity.

---

## Destination Connectors

### ClickHouse v2

**Timeline**: June - September 2025  
**Status**: Released and published  
**Total PRs**: ~30 (merged)

This was a **ground-up rewrite** of the ClickHouse destination connector on the Bulk CDK.

| Phase | Key PRs | Details |
|-------|---------|---------|
| **Initial abstraction** | [#61354](https://github.com/airbytehq/airbyte/pull/61354) | Core abstraction layer for ClickHouse v2 on the Bulk CDK. |
| **Integration tests** | [#61384](https://github.com/airbytehq/airbyte/pull/61384) | Set up integration test infrastructure. |
| **Schema evolution** | [#61558](https://github.com/airbytehq/airbyte/pull/61558), [#66143](https://github.com/airbytehq/airbyte/pull/66143) | Added schema change support and improved schema change handling. |
| **Dedup support** | [#61696](https://github.com/airbytehq/airbyte/pull/61696) | Implemented deduplication sync mode. |
| **Truncate support** | [#61679](https://github.com/airbytehq/airbyte/pull/61679) | Implemented truncate refresh mode. |
| **JSON data type** | [#62100](https://github.com/airbytehq/airbyte/pull/62100) | Added JSON type support; ClickHouse uses `String` for JSON, no special handling needed. |
| **Acceptance tests** | [#61509](https://github.com/airbytehq/airbyte/pull/61509), [#61515](https://github.com/airbytehq/airbyte/pull/61515), [#61519](https://github.com/airbytehq/airbyte/pull/61519) | Progressively re-enabled and fixed acceptance tests. |
| **Spec defaults** | [#61510](https://github.com/airbytehq/airbyte/pull/61510), [#62047](https://github.com/airbytehq/airbyte/pull/62047) | Set default protocol in spec. |
| **Publish** | [#62022](https://github.com/airbytehq/airbyte/pull/62022), [#62028](https://github.com/airbytehq/airbyte/pull/62028) | Enabled publishing and metadata for the connector. |
| **Column mapping fix** | [#65117](https://github.com/airbytehq/airbyte/pull/65117) | Fixed column mapping issues. |
| **Decimal type** | [#66134](https://github.com/airbytehq/airbyte/pull/66134) | Changed decimal type handling. |
| **Temp table fix** | [#62447](https://github.com/airbytehq/airbyte/pull/62447) | Fixed temp table behavior. |
| **Batch size** | [#64104](https://github.com/airbytehq/airbyte/pull/64104) | Added option to configure batch size. |
| **PK table alter** | [#63721](https://github.com/airbytehq/airbyte/pull/63721) | Fixed table alter operations for primary keys. |
| **Compatible naming** | [#63724](https://github.com/airbytehq/airbyte/pull/63724) | Added compatible naming support. |
| **Error messages** | [#63760](https://github.com/airbytehq/airbyte/pull/63760) | Improved error messages for unexpected existing tables. |
| **Teardown** | [#64881](https://github.com/airbytehq/airbyte/pull/64881) | Added proper destination teardown. |

**Key ClickHouse-specific details**:
- ClickHouse uses `String` type for JSON columns (no native JSON type needed).
- Decimal type handling required special attention.
- Temp table management is critical for correctness in dedup mode.

---

### Destination Postgres (Direct Load)

**Timeline**: September 2025 - March 2026  
**Status**: Released (RC available, ongoing improvements)  
**Total PRs**: ~20 (merged)

A full migration of Destination Postgres to the Bulk CDK using the **Direct Load** pattern (no staging area; writes directly to the database).

| Phase | Key PRs | Details |
|-------|---------|---------|
| **Acceptance tests setup** | [#67592](https://github.com/airbytehq/airbyte/pull/67592), [#67596](https://github.com/airbytehq/airbyte/pull/67596) | Initial acceptance test framework for the new connector. |
| **Value coercer** | [#68126](https://github.com/airbytehq/airbyte/pull/68126) | Implemented value coercion for Postgres types. |
| **Init script** | [#68123](https://github.com/airbytehq/airbyte/pull/68123) | Added Postgres initialization script for tests. |
| **Full spec** | [#68117](https://github.com/airbytehq/airbyte/pull/68117) | Defined the full connector specification. |
| **Acceptance test fixes** | [#68142](https://github.com/airbytehq/airbyte/pull/68142), [#68151](https://github.com/airbytehq/airbyte/pull/68151), [#69086](https://github.com/airbytehq/airbyte/pull/69086) | Multiple rounds of fixing acceptance test failures. |
| **Raw table implementation** | [#68580](https://github.com/airbytehq/airbyte/pull/68580) | Implemented raw table mode. |
| **RC release** | [#69846](https://github.com/airbytehq/airbyte/pull/69846) | Created the first release candidate. |
| **Component tests** | [#70348](https://github.com/airbytehq/airbyte/pull/70348) | Added component tests for table operations. |
| **Index recreation fix** | [#70347](https://github.com/airbytehq/airbyte/pull/70347) | Fixed index recreation on non-existent columns in raw tables mode. |
| **CDK pattern refactor** | [#71183](https://github.com/airbytehq/airbyte/pull/71183) | Refactored schema utilities to follow the CDK pattern (deleted `PostgresColumnUtils.kt`, created modular `PostgresTableSchema*` classes). |
| **Code cleanup** | [#71163](https://github.com/airbytehq/airbyte/pull/71163) | Cleaned up destination Postgres code. |
| **Check operation fix** | [#71273](https://github.com/airbytehq/airbyte/pull/71273) | Fixed check operation in raw tables only mode (also affected Snowflake). |

**Key Postgres-specific details**:
- Uses Direct Load pattern (no S3/GCS staging, writes directly via JDBC).
- Schema utilities were refactored to follow the same pattern as Snowflake.
- Raw tables mode and schema mode both supported.

---

### Destination Snowflake

**Timeline**: September 2025 - March 2026  
**Status**: Migrated to Bulk CDK, actively maintained  
**Total PRs**: ~10 (merged)

The Snowflake connector was migrated to the Bulk CDK. Key work included:

| Area | Key PRs | Details |
|------|---------|---------|
| **Basic write fix** | [#66293](https://github.com/airbytehq/airbyte/pull/66293) | Fixed basic write operations. |
| **Config update** | [#66302](https://github.com/airbytehq/airbyte/pull/66302) | Properly updated the configuration. |
| **Schema ensure** | [#66354](https://github.com/airbytehq/airbyte/pull/66354) | Ensured schema creation/verification. |
| **Generation alias removal** | [#66507](https://github.com/airbytehq/airbyte/pull/66507) | Removed generation alias. |
| **Acceptance tests** | [#66189](https://github.com/airbytehq/airbyte/pull/66189) | Set up acceptance test suite. |
| **Check operation fix** | [#71273](https://github.com/airbytehq/airbyte/pull/71273) | Fixed check operation in raw tables mode — the check was unconditionally using `SnowflakeSchemaRecordFormatter`, which doesn't handle `_airbyte_loaded_at` required in raw mode. Refactored `SnowflakeChecker` to use constructor injection for the correct formatter. |
| **Version bump** | [#74824](https://github.com/airbytehq/airbyte/pull/74824) | Bumped version 4.0.38 to 4.0.39. |

---

### Destination Redshift

**Timeline**: April 2026  
**Status**: Planning phase (PR open)

| Area | Key PRs | Details |
|------|---------|---------|
| **Migration plan** | [#76077](https://github.com/airbytehq/airbyte/pull/76077) | Comprehensive migration plan from old Java CDK (0.46.0) to Bulk CDK (1.0.7) using Direct Load + S3 staging. Plan covers 11 phases: build system, config/spec with backward compatibility, schema mapping, SQL generation, client layer, S3 staging data loading, value coercion, writer orchestration, connection check, testing, and deployment. |

**Key notes**: The migration plan was built by analyzing Snowflake, Postgres, and ClickHouse migrations that were completed previously, making it a good reference for future migrations.

---

### Destination MSSQL

**Timeline**: June 2025  
**Status**: Merged

| Area | Key PRs | Details |
|------|---------|---------|
| **SSH tunneling** | [#62078](https://github.com/airbytehq/airbyte/pull/62078) | Added SSH tunnel support for MSSQL using existing CDK SSH configuration. The tunnel is created in the `DatasourceFactory` when needed. |

---

### Iceberg / S3 Data Lake

**Timeline**: March 2026  
**Status**: Merged

| Area | Key PRs | Details |
|------|---------|---------|
| **Schema evolution fix** | [#74723](https://github.com/airbytehq/airbyte/pull/74723) | Fixed `IllegalArgumentException` when schema evolution replaces a column that is also an identifier field. Deferred identifier field updates to after column replacement. |
| **PK type mapping** | [#74328](https://github.com/airbytehq/airbyte/pull/74328) | Changed primary key `NumberType` mapping from `DecimalType` to `StringType` to avoid precision issues. |
| **CDK bump** | [#74326](https://github.com/airbytehq/airbyte/pull/74326) | Bumped CDK for S3 Data Lake connector. |

---

## Platform Infrastructure (2022)

This earlier body of work focused on Airbyte's core platform, particularly around Temporal workflows, state management, and architecture decoupling.

### Per-Stream State

A major initiative to enable per-stream state tracking (vs. global state) for incremental syncs.

| Area | Key PRs | Details |
|------|---------|---------|
| **Namespace in protocol** | [#13356](https://github.com/airbytehq/airbyte/pull/13356) | Added namespace field to the state message protocol to make stream names schema-specific. |
| **State type updates** | [#14360](https://github.com/airbytehq/airbyte/pull/14360) | Updated the `state.state` type in the protocol. |
| **State aggregator** | [#14364](https://github.com/airbytehq/airbyte/pull/14364) | Implemented a state aggregator for managing per-stream state. |
| **Generic per-stream tests** | [#15267](https://github.com/airbytehq/airbyte/pull/15267) | Added generic tests for per-stream state behavior. |
| **Destination fixes** | [#15180](https://github.com/airbytehq/airbyte/pull/15180), [#15211](https://github.com/airbytehq/airbyte/pull/15211), [#15279](https://github.com/airbytehq/airbyte/pull/15279) | Fixed BigQuery, MongoDB, and other destinations to work with per-stream state. |
| **OSS release** | [#15008](https://github.com/airbytehq/airbyte/pull/15008) | Released per-stream state to the OSS project by enabling `USE_STREAM_CAPABLE_STREAM` by default. |

### Temporal Workflow Infrastructure

| Area | Key PRs | Details |
|------|---------|---------|
| **Temporal client extraction** | [#16778](https://github.com/airbytehq/airbyte/pull/16778) | Created `airbyte-commons-temporal` module, extracting the Temporal client from the worker for reuse by the cron service. |
| **Temporal cleaning cron** | [#16414](https://github.com/airbytehq/airbyte/pull/16414) | Added a Temporal cleaning cron job for workflow maintenance. |
| **Sync workflow tests** | [#16816](https://github.com/airbytehq/airbyte/pull/16816) | Added sync workflow replayer tests. |
| **Auto-fail versioning** | [#17562](https://github.com/airbytehq/airbyte/pull/17562) | Auto-fail all workflows on versioning issues. |

### Architecture Decoupling

| Area | Key PRs | Details |
|------|---------|---------|
| **Orchestrator decoupling** | [#17570](https://github.com/airbytehq/airbyte/pull/17570) | Removed dependency from orchestrator container to worker app by creating `airbyte-commons-worker` module. |
| **Connector worker extraction** | [#17977](https://github.com/airbytehq/airbyte/pull/17977) | Removed deprecated connector-worker dependencies. |
| **DB migration API extraction** | [#18459](https://github.com/airbytehq/airbyte/pull/18459) | Extracted database migration API into its own module. |

### Other Platform Fixes

| Area | Key PRs | Details |
|------|---------|---------|
| **Secret handling** | [#17354](https://github.com/airbytehq/airbyte/pull/17354), [#17484](https://github.com/airbytehq/airbyte/pull/17484), [#13241](https://github.com/airbytehq/airbyte/pull/13241) | Fixed secrets exposure in logs, fixed `JsonSecretProcessor` not handling `oneOf`, and improved secret hiding. |
| **Reset behavior** | [#17591](https://github.com/airbytehq/airbyte/pull/17591) | Made reset operations non-blocking (don't wait for reset to complete before returning). |
| **OpenAPI fix** | [#18445](https://github.com/airbytehq/airbyte/pull/18445) | Fixed tag in OpenAPI specification. |

---

## CI/CD and Tooling

| Area | Key PRs | Details |
|------|---------|---------|
| **CDK bump workflow** | [#58126](https://github.com/airbytehq/airbyte/pull/58126) | Created a GitHub Actions workflow to automate CDK version bumping: creates a commit with the new CDK version, publishes all modified connectors, updates changelogs, and merges the PR. |
| **Bulk CDK bump flow** | [#58648](https://github.com/airbytehq/airbyte/pull/58648) | Improved the Bulk CDK bump flow specifically. |
| **Version bump skip** | [#64913](https://github.com/airbytehq/airbyte/pull/64913) | Avoided requiring a version bump if only tests are updated. |
| **Skip missing connectors** | [#62482](https://github.com/airbytehq/airbyte/pull/62482) | CI now skips missing connectors gracefully. |
| **Empty action** | [#58604](https://github.com/airbytehq/airbyte/pull/58604), [#58118](https://github.com/airbytehq/airbyte/pull/58118) | Added empty GitHub Actions for workflow dispatching. |

---

## Key Patterns and Conventions

These are recurring patterns and conventions established during the work:

1. **Connector migration to Bulk CDK follows a standard progression**: spec/config -> schema mapping -> SQL generation -> client layer -> data loading -> value coercion -> writer orchestration -> check -> acceptance tests -> publish.
2. **Schema utilities follow a package pattern** (`*TableSchema*` classes) first established in Snowflake, then replicated in Postgres and ClickHouse.
3. **Raw tables mode vs. schema mode**: All connectors support both. Check operations must select the correct record formatter based on the mode.
4. **Temp table lifecycle**: Temp tables must be dropped after successful upserts (see [#74715](https://github.com/airbytehq/airbyte/pull/74715)) to prevent duplicate records.
5. **Acceptance tests are re-enabled incrementally**: Tests are first disabled, then re-enabled one-by-one as features are implemented.
6. **CDK version bumps** use an automated workflow to propagate changes across all dependent connectors.

---

## Open / In-Progress Work

These PRs are still open as of the document creation date:

| PR | Title | Status |
|----|-------|--------|
| [#76077](https://github.com/airbytehq/airbyte/pull/76077) | docs(destination-redshift): Bulk CDK migration plan | Open |
| [#75137](https://github.com/airbytehq/airbyte/pull/75137) | chore(destination-postgres): bump version 3.0.11 to 3.0.12 | Open |
| [#71103](https://github.com/airbytehq/airbyte/pull/71103) | feat(destination-postgres): Add NameMapper for acceptance tests | Open |
| [#70950](https://github.com/airbytehq/airbyte/pull/70950) | destination-postgres: map schema once at startup | Open |
| [#68181](https://github.com/airbytehq/airbyte/pull/68181) | Bmoric/postgres more acceptance fix | Open |
| [#66723](https://github.com/airbytehq/airbyte/pull/66723) | Test branch (Snowflake) | Open |
| [#65095](https://github.com/airbytehq/airbyte/pull/65095) | Bmoric/fix basic write (ClickHouse) | Open |
| [#62466](https://github.com/airbytehq/airbyte/pull/62466) | Update snowflake precision | Open |
