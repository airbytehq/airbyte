---
name: db-connector-writer
description: Write database extract (source) connectors on the Airbyte Bulk CDK. Guides through architecture, scaffolding, schema discovery, full refresh, incremental sync, and CDC implementation.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task
argument-hint: <database-name>
---

# Database Connector Writer

This skill helps you build **database extract (source) connectors** on the Airbyte Bulk CDK framework. It provides comprehensive architecture documentation, step-by-step implementation guides, coding standards, and reference material.

## What This Skill Does

Given a target database (e.g., MongoDB, Oracle, CockroachDB), this skill guides you through building a production-ready Airbyte source connector that supports:

- **Full Refresh** sync mode (with resumability via primary key checkpointing)
- **Incremental** sync mode (cursor-based, two-phase: snapshot then incremental)
- **CDC** sync mode (Change Data Capture via Debezium, optional)

## How to Use

### Quick Start

```
/db-connector-writer <database-name>
```

Example: `/db-connector-writer oracle`

### Implementation Process

When invoked, follow this process:

1. **Start with `source/architecture.md`** - This is the primary document. Read it fully to understand:
   - The Bulk CDK framework architecture (entry point, data flow, core abstractions)
   - The JDBC and CDC toolkit stock implementations
   - What you need to implement vs what the CDK provides
   - The reference connector implementations section at the bottom (with exact file paths)

2. **Study a reference connector** - Before writing any code, read the actual source code of the closest reference connector:
   - **JDBC source (recommended start):** `source-mysql` on `master` branch (`airbyte-integrations/connectors/source-mysql/`)
   - **JDBC + CDC:** `source-mssql` on `master` branch (`airbyte-integrations/connectors/source-mssql/`)
   - **Advanced JDBC:** `source-postgres` on `source-postgres/bulk-cdk` branch (`airbyte-integrations/connectors/source-postgres/`)

3. **Complete `source/preflight-checklist.md`** for the target database (JDBC driver, type system, CDC support, etc.)

4. **Follow the step-by-step guides** in order, verifying each milestone:
   - `source/step-by-step/0-introduction.md` - Overview and development paths
   - `source/step-by-step/1-getting-started.md` - Scaffolding and spec operation
   - `source/step-by-step/2-schema-discovery.md` - Check and discover operations
   - `source/step-by-step/3-full-refresh.md` - Full refresh read
   - `source/step-by-step/4-incremental.md` - Cursor-based incremental
   - `source/step-by-step/5-cdc.md` - CDC with Debezium (optional)

5. **Reference documents** (use during development as needed):
   - `source/coding-standards.md` - Code organization, naming, JDBC patterns, error handling
   - `source/implementation-reference.md` - Component API reference, type mappings, query patterns
   - `source/step-by-step/6-troubleshooting.md` - Common issues and solutions

### Milestones

| After Guide | What Works |
|-------------|------------|
| 1 - Getting Started | `spec` operation returns config schema |
| 2 - Schema Discovery | `check` validates connection, `discover` returns catalog |
| 3 - Full Refresh | `read` works for full refresh sync mode |
| 4 - Incremental | `read` works for cursor-based incremental sync |
| 5 - CDC | `read` works for CDC sync mode |

## Key Architecture Concepts

- **Bulk CDK**: Kotlin-based framework using Micronaut DI that orchestrates source connector operations
- **JDBC Toolkit**: Stock implementations for relational database sources (partitions, query generation, sampling)
- **CDC Toolkit**: Debezium-based change data capture (position tracking, state management)
- **Toolkit-First Approach**: Extend and customize only what's specific to your database dialect
- **Partition Model**: Data extraction is organized into partitions (units of work) that support resumability

## Reference Connectors

| Connector | Branch | Toolkits | Use As Reference For |
|-----------|--------|----------|---------------------|
| `source-mysql` | `master` | extract-jdbc, extract-cdc | Standard JDBC + CDC, backtick quoting, LIMIT |
| `source-mssql` | `master` | extract-jdbc, extract-cdc | SQL Server dialect, TOP N, TABLESAMPLE, LSN CDC |
| `source-postgres` | `source-postgres/bulk-cdk` | extract-jdbc, extract-cdc | CTID partitioning, XMIN, rich types, pgoutput CDC |
| `source-mongodb` | `master` | none (core only) | Non-JDBC connector, custom PartitionsCreator/PartitionReader, native client |

## Document Index

| Document | Purpose |
|----------|---------|
| `source/architecture.md` | **Start here.** CDK architecture, core abstractions, data flow, reference connector file paths |
| `source/coding-standards.md` | Code organization, naming conventions, JDBC patterns, error handling, common gotchas |
| `source/implementation-reference.md` | Component API reference, type mappings, sync mode queries, CDC integration |
| `source/preflight-checklist.md` | Database research checklist (types, CDC, queries) to complete before implementation |
| `source/step-by-step/0-introduction.md` | Development flow overview, paths, and milestones |
| `source/step-by-step/1-getting-started.md` | Project scaffolding, build.gradle, spec operation |
| `source/step-by-step/2-schema-discovery.md` | MetadataQuerier, FieldTypeMapper, check + discover operations |
| `source/step-by-step/3-full-refresh.md` | SelectQueryGenerator, PartitionFactory, full refresh read |
| `source/step-by-step/4-incremental.md` | Cursor partitions, state management, incremental sync |
| `source/step-by-step/5-cdc.md` | Debezium integration, CDC position, meta-fields, state |
| `source/step-by-step/6-troubleshooting.md` | Common DI errors, type issues, state problems, quick fixes |
