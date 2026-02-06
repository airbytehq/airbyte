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

### What You Get

The skill provides access to the following reference documents:

| Document | Purpose |
|----------|---------|
| `source/architecture.md` | CDK architecture overview, core abstractions, data flow |
| `source/coding-standards.md` | Code organization, naming, JDBC patterns, error handling |
| `source/implementation-reference.md` | Component API reference, type mappings, query patterns |
| `source/preflight-checklist.md` | Database research checklist before implementation |
| `source/step-by-step/0-introduction.md` | Development flow overview and milestones |
| `source/step-by-step/1-getting-started.md` | Project scaffolding and spec operation |
| `source/step-by-step/2-schema-discovery.md` | Check and discover operations |
| `source/step-by-step/3-full-refresh.md` | Full refresh read operation |
| `source/step-by-step/4-incremental.md` | Cursor-based incremental sync |
| `source/step-by-step/5-cdc.md` | CDC with Debezium integration |
| `source/step-by-step/6-troubleshooting.md` | Common issues and solutions |

### Development Path

**Path 1: Fast Path (No CDC)**
1. Read `architecture.md` for framework understanding
2. Complete `preflight-checklist.md` for your target database
3. Follow guides 1-4 sequentially
4. Result: Working connector with full refresh + incremental

**Path 2: Full CDC Path**
1. Complete Fast Path (guides 1-4)
2. Follow guide 5 for CDC implementation
3. Result: Full-featured connector with all sync modes

### Milestones

| After Guide | What Works |
|-------------|------------|
| 1 - Getting Started | `spec` operation returns config schema |
| 2 - Schema Discovery | `check` validates connection, `discover` returns catalog |
| 3 - Full Refresh | `read` works for full refresh sync mode |
| 4 - Incremental | `read` works for cursor-based incremental sync |
| 5 - CDC | `read` works for CDC sync mode |

## Implementation Process

When invoked, follow this process:

1. **Read the architecture document** to understand the Bulk CDK framework
2. **Complete the preflight checklist** for the target database (JDBC driver, type system, CDC support, etc.)
3. **Follow the step-by-step guides** in order, verifying each milestone before proceeding
4. **Reference coding-standards.md** for conventions and best practices
5. **Use implementation-reference.md** as a lookup guide during development
6. **Consult troubleshooting.md** when encountering errors

## Key Architecture Concepts

- **Bulk CDK**: Kotlin-based framework using Micronaut DI that orchestrates source connector operations
- **JDBC Toolkit**: Stock implementations for relational database sources (partitions, query generation, sampling)
- **CDC Toolkit**: Debezium-based change data capture (position tracking, state management)
- **Toolkit-First Approach**: Extend and customize only what's specific to your database dialect
- **Partition Model**: Data extraction is organized into partitions (units of work) that support resumability

## Existing Reference Connectors

- `source-mysql` - Full JDBC + CDC connector (Kotlin, Bulk CDK)
- `source-mssql` - Full JDBC + CDC connector (Kotlin, Bulk CDK)
- `source-mongodb` - Non-JDBC connector (Kotlin, Bulk CDK, extract core only)
- `source-snowflake` - JDBC connector without CDC (Java, Bulk CDK)
