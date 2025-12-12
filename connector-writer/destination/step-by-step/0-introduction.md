# Step-by-Step Guide: Building a Destination Connector

**Summary:** Complete guide to building a Dataflow CDK destination connector from scratch. Follow the numbered guides in sequence to build incrementally with clear milestones and quick feedback loops.

---

## Prerequisites

- Familiarity with Kotlin and your target database
- Understanding of [dataflow-cdk.md](../dataflow-cdk.md) (architecture overview)
- Understanding of [implementation-reference.md](../implementation-reference.md) (component reference)
- Database credentials or Testcontainers setup

---

## Development Flow

### Path 1: Fast Path (Working Connector)

**Goal:** Get a working connector with basic sync modes as quickly as possible

**Timeline:** 2-3 days

**Steps:**
1. **1-getting-started.md** (Setup Phases 1-2, ~4 hours)
   - Project scaffolding and build setup
   - Spec operation implementation
   - **Milestone:** `./destination-{db} --spec` works

2. **2-database-setup.md** (Database Phases 1-2, ~6 hours)
   - Database connectivity and all table operations
   - Check operation implementation
   - **Milestone:** `./destination-{db} --check --config config.json` works

3. **3-write-infrastructure.md** (Infrastructure Phases 1-2, ~4 hours)
   - Name generators and DI setup
   - Write operation infrastructure
   - Understanding test contexts
   - **Milestone:** DI configured, ready for business logic

4. **4-write-operations.md** (Write Phases 1-4, ~8 hours)
   - InsertBuffer, Aggregate, Writer implementation
   - Append mode (direct writes)
   - Generation ID support
   - Overwrite mode (atomic swap)
   - Copy operation
   - **Milestone:** `./destination-{db} --write` works with append + overwrite modes

**Result:** Working connector suitable for PoC and simple use cases

---

### Path 2: Production Path (Full-Featured Connector)

**Goal:** Production-ready connector with all enterprise features

**Timeline:** 5-7 days

**Steps:**
1-4. Complete Fast Path (above)

5. **5-advanced-features.md** (Advanced Phases 1-4, ~12 hours)
   - Schema evolution (automatic column add/drop/modify)
   - Dedupe mode (MERGE with primary key)
   - CDC support (hard/soft deletes)
   - Optimization and polish
   - **Milestone:** Full-featured, production-ready connector

6. **6-testing.md** (Testing Phase 1, ~2 hours)
   - Run BasicFunctionalityIntegrationTest
   - Validate all sync modes
   - Test schema evolution and CDC
   - **Milestone:** All tests passing

**Result:** Production-ready connector with all features

---

### Path 3: Debug Path (Troubleshooting)

**Goal:** Fix issues quickly

**When:** Encountering errors during development

**Steps:**
1. Check **7-troubleshooting.md** for common errors
   - Test context confusion
   - Dependency injection errors
   - Quick fixes and patterns

2. Return to phase guide with solution

**Result:** Unblocked and back to development

---

## Milestone Summary

| Guide | Phases | What Works | Lines | Time | Prerequisites |
|-------|--------|------------|-------|------|---------------|
| **1-getting-started.md** | Setup 1-2 | --spec | ~626 | 4h | None |
| **2-database-setup.md** | Database 1-2 | --check | ~1180 | 6h | Guide 1 |
| **3-write-infrastructure.md** | Infrastructure 1-2 | DI ready | ~600 | 4h | Guide 2 |
| **4-write-operations.md** | Write 1-4 | --write (append, overwrite) | ~780 | 8h | Guide 3 |
| **5-advanced-features.md** | Advanced 1-4 | All features | ~900 | 12h | Guide 4 |
| **6-testing.md** | Testing 1 | All tests pass | ~730 | 2h | Guide 5 |
| **7-troubleshooting.md** | Reference | Debug help | ~280 | As needed | Any |

---

## What You'll Build

### After Guide 1 (Getting Started)
- ✅ Project compiles and builds
- ✅ Docker image builds
- ✅ `--spec` operation returns connector capabilities

### After Guide 2 (Database Setup)
- ✅ Database connection established
- ✅ Namespace (schema/database) creation
- ✅ Table creation, drop, count operations
- ✅ `--check` operation validates configuration

### After Guide 3 (Write Infrastructure)
- ✅ Name generators (table, column, temp table)
- ✅ TableCatalog DI setup
- ✅ Write operation entry point
- ✅ Understanding of test contexts (critical!)

### After Guide 4 (Write Operations)
- ✅ InsertBuffer with efficient batch writes
- ✅ Aggregate and AggregateFactory
- ✅ Writer orchestration
- ✅ Append mode (direct insert)
- ✅ Overwrite mode (temp table + atomic swap)
- ✅ Generation ID tracking
- ✅ `--write` operation works for basic syncs

### After Guide 5 (Advanced Features)
- ✅ Schema evolution (automatic schema changes)
- ✅ Dedupe mode (MERGE with PK)
- ✅ CDC support (hard/soft deletes)
- ✅ Performance optimization
- ✅ Production-ready connector

### After Guide 6 (Testing)
- ✅ All integration tests passing
- ✅ All sync modes validated
- ✅ Schema evolution tested
- ✅ Ready for deployment

---

## Key Concepts Per Guide

### Guide 1: Getting Started
- CDK version pinning
- Micronaut DI basics
- Specification and configuration classes
- JSON schema generation

### Guide 2: Database Setup
- SqlGenerator pattern (SQL generation separate from execution)
- TableOperationsClient interface
- Testcontainers for local testing
- Component vs integration tests

### Guide 3: Write Infrastructure
- Name generators and column mapping
- StreamStateStore pattern
- Test contexts (component vs integration vs basic functionality)
- Common DI errors and fixes

### Guide 4: Write Operations
- InsertBuffer pattern (database-specific)
- StreamLoader variants (4 types)
- Writer.createStreamLoader() decision logic
- Temp table + atomic swap strategy

### Guide 5: Advanced Features
- Schema evolution (discover → compute → compare → apply)
- MERGE/UPSERT implementation
- Window functions for deduplication
- CDC handling (hard vs soft delete)

### Guide 6: Testing
- BasicFunctionalityIntegrationTest structure
- Testing all sync modes
- Validating schema evolution
- End-to-end validation

### Guide 7: Troubleshooting
- Test context confusion
- Micronaut DI errors
- Quick reference fixes

---

## Architecture Recap

Before starting, understand these key patterns:

**Component Roles:**
- **SqlGenerator:** Generates SQL (pure functions, testable)
- **Client:** Executes SQL (I/O, error handling)
- **InsertBuffer:** Efficient batch writes (database-specific)
- **StreamLoader:** Orchestrates table lifecycle (CDK-provided, you select)
- **Writer:** High-level orchestration (you implement, minimal logic)

**Data Flow:**
```
Platform → stdin → Lifecycle → Writer.setup()
                              → createStreamLoader()
                              → AggregateFactory.create()
                              → InsertBuffer
                              → Database
                              → StreamLoader.close()
                              → STATE → stdout → Platform
```

**Testing Strategy:**
- **Component tests:** Test individual operations (create table, insert, etc.)
- **Integration tests:** Test write initialization and lifecycle
- **Basic functionality tests:** End-to-end validation of all features

---

## Getting Help

**During development:**
- Check 7-troubleshooting.md first
- Review dataflow-cdk.md for architecture questions
- Review implementation-reference.md for API details
- Look at destination-snowflake or destination-clickhouse for examples

**Common pitfalls:**
- Not reading test contexts section (causes confusion in Infrastructure Phase 2)
- Missing DI registration (causes "No bean found" errors)
- Skipping CDK version pinning (causes build issues)
- Not understanding StreamLoader variants (causes wrong finalization)

---

## Next Steps

**Start with:** [1-getting-started.md](./1-getting-started.md)

**References:**
- [Architecture Overview](../dataflow-cdk.md)
- [Implementation Reference](../implementation-reference.md)
- [Coding Standards](../coding-standards.md)
- [Preflight Checklist](../preflight-checklist.md)
