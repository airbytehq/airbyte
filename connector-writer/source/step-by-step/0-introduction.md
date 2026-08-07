# Step-by-Step Guide: Building a Source Connector

**Summary:** Complete guide to building a Bulk CDK source connector from scratch. Follow the numbered guides in sequence to build incrementally with clear milestones and quick feedback loops. After Guide 1, `--spec` works. After Guide 2, `--check` and `--discover` work. After Guide 3, full refresh reads work. After Guide 4, incremental sync works.

---

## Prerequisites

- Familiarity with Kotlin and your target database
- Understanding of [architecture.md](../architecture.md) (CDK architecture overview)
- Understanding of [implementation-reference.md](../implementation-reference.md) (component reference)
- Database credentials or Testcontainers setup
- Completed [preflight-checklist.md](../preflight-checklist.md) for your database

---

## Development Flow

### Path 1: Fast Path (Working Connector)

**Goal:** Get a working connector with full refresh and incremental sync

**Steps:**
1. **1-getting-started.md** (Setup Phases 1-2)
   - Project scaffolding and build setup
   - Spec operation implementation
   - **Milestone:** `./source-{db} spec` works

2. **2-schema-discovery.md** (Discovery Phases 1-3)
   - Database connectivity
   - Metadata querier implementation
   - Check and Discover operations
   - **Milestone:** `./source-{db} check` and `./source-{db} discover` work

3. **3-full-refresh.md** (Read Phases 1-2)
   - Source operations (type mapping)
   - Partition factory (basic)
   - Full refresh read
   - **Milestone:** `./source-{db} read` works for full refresh

4. **4-incremental.md** (Incremental Phases 1-2)
   - Cursor-based state management
   - Incremental partition
   - **Milestone:** Incremental sync works with cursor columns

**Result:** Working connector suitable for production use cases without CDC

---

### Path 2: CDC Path (Change Data Capture)

**Goal:** Full-featured connector with CDC support

**Steps:**
1-4. Complete Fast Path (above)

5. **5-cdc.md** (CDC Phases 1-3)
   - Debezium integration
   - CDC state management
   - CDC meta-fields
   - **Milestone:** CDC sync works

**Result:** Full-featured connector with all sync modes

---

### Path 3: Debug Path (Troubleshooting)

**Goal:** Fix issues quickly

**When:** Encountering errors during development

**Steps:**
1. Check **6-troubleshooting.md** for common errors
   - DI configuration issues
   - Type mapping problems
   - State serialization errors

2. Return to phase guide with solution

**Result:** Unblocked and back to development

---

## Milestone Summary

| Guide | What Works | Tests | Prerequisites |
|-------|------------|-------|---------------|
| **1-getting-started.md** | `spec` | SpecTest | None |
| **2-schema-discovery.md** | `check`, `discover` | CheckTest, DiscoverTest | Guide 1 |
| **3-full-refresh.md** | `read` (full refresh) | ReadTest | Guide 2 |
| **4-incremental.md** | `read` (incremental) | IncrementalTest | Guide 3 |
| **5-cdc.md** | `read` (CDC) | CdcTest | Guide 4 |
| **6-troubleshooting.md** | Debug help | - | Any |

---

## What You'll Build

### After Guide 1 (Getting Started)
- Project compiles and builds
- Docker image builds
- `spec` operation returns connector capabilities

### After Guide 2 (Schema Discovery)
- Database connection established
- Schema discovery (tables, columns, primary keys)
- `check` operation validates configuration
- `discover` operation returns available streams

### After Guide 3 (Full Refresh)
- Type mapping (database types → Airbyte types)
- Query generation
- Full table reads
- `read` operation works for full refresh sync mode

### After Guide 4 (Incremental)
- Cursor-based state tracking
- Incremental reads (WHERE cursor > last_value)
- State checkpointing
- Resume from saved state

### After Guide 5 (CDC)
- Debezium integration
- Binlog/WAL position tracking
- CDC meta-fields (_ab_cdc_*)
- Delete detection

---

## Key Concepts Per Guide

### Guide 1: Getting Started
- CDK version pinning
- Micronaut DI basics
- Specification and configuration classes
- JSON schema generation

### Guide 2: Schema Discovery
- JdbcMetadataQuerier pattern
- MetadataQuerier.Factory interface
- Check operation (connection validation)
- Discover operation (catalog generation)

### Guide 3: Full Refresh
- FieldTypeMapper (database types → Airbyte types)
- SelectQueryGenerator (SQL generation)
- JdbcPartitionFactory (partition creation)
- DefaultJdbcStreamState

### Guide 4: Incremental
- Cursor-based state management
- State serialization/deserialization
- Incremental partition types
- Checkpoint emission

### Guide 5: CDC
- Debezium connector configuration
- CDC position extraction
- CDC state serialization
- Meta-field decoration

### Guide 6: Troubleshooting
- Common DI errors
- Type mapping issues
- State serialization problems
- Quick reference fixes

---

## Architecture Recap

Before starting, understand these key patterns:

**Component Roles:**
- **ConfigurationSpecification:** JSON schema for UI form
- **Configuration:** Runtime config object
- **MetadataQuerier:** Schema discovery (tables, columns, PKs)
- **SourceOperations:** Type mapping + query generation
- **PartitionFactory:** Creates partitions based on sync mode/state
- **Partition:** Reads data for a specific range/state

**Data Flow:**
```
Platform → CLI args → AirbyteSourceRunner
                          → spec()  → SPEC message
                          → check() → CONNECTION_STATUS
                          → discover() → CATALOG
                          → read()  → RECORD + STATE messages
```

**Four Operations:**
| Operation | Input | Output | Purpose |
|-----------|-------|--------|---------|
| `spec` | None | ConnectorSpecification | Describe capabilities |
| `check` | Config JSON | ConnectionStatus | Validate connection |
| `discover` | Config JSON | AirbyteCatalog | List available streams |
| `read` | Config + Catalog + State | Records + States | Extract data |

---

## File Structure Overview

```
source-{db}/
├── src/main/kotlin/io/airbyte/integrations/source/{db}/
│   ├── {DB}Source.kt                              # Entry point
│   ├── {DB}SourceConfigurationSpecification.kt    # Config JSON schema
│   ├── {DB}SourceConfiguration.kt                 # Runtime config + factory
│   ├── {DB}SourceMetadataQuerier.kt              # Schema discovery
│   ├── {DB}SourceOperations.kt                   # Type mapping + queries
│   ├── {DB}SourceJdbcPartitionFactory.kt         # Partition creation
│   ├── {DB}SourceJdbcPartition.kt                # Partition implementations
│   ├── {DB}SourceJdbcStreamStateValue.kt         # State serialization
│   └── (CDC files if implementing CDC)
├── src/main/resources/
│   └── application.yml                            # CDK configuration
├── src/test/kotlin/...                           # Unit tests
├── build.gradle                                   # Build configuration
└── metadata.yaml                                  # Connector metadata
```

---

## Getting Help

**During development:**
- Check 6-troubleshooting.md first
- Review architecture.md for architecture questions
- Review implementation-reference.md for API details
- Look at source-mysql for reference implementation

**Common pitfalls:**
- Missing `@Singleton` or `@Primary` annotations (causes DI errors)
- Incorrect type mapping (causes data corruption)
- State not serializable (causes resume failures)
- Missing application.yml settings (causes startup failures)

---

## Next Steps

**Start with:** [1-getting-started.md](./1-getting-started.md)

**References:**
- [Architecture Overview](../architecture.md)
- [Implementation Reference](../implementation-reference.md)
- [Coding Standards](../coding-standards.md)
- [Preflight Checklist](../preflight-checklist.md)
