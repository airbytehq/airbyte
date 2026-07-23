# Preflight Checklist: Database Knowledge

**Summary:** Essential database knowledge required before implementing a destination connector. Complete this checklist to ensure you have the information needed for the 4 core components (SQL Generator, Database Client, Insert Buffer, Column Utilities).

**Time to complete:** 2-4 hours of research for unfamiliar database

---

## 1. Connection & Client Setup

**For SQL Generator + Database Client**

### Driver & Connection
- [ ] **Driver available?** JDBC, native client library, HTTP API?
- [ ] **Connection string format?** `jdbc:db://host:port/database` or custom URI?
- [ ] **Connection pooling?** HikariCP, built-in, or manual management?

**Quick validation:**
```kotlin
// Can you write this code?
val connection = /* create connection */
connection.execute("SELECT 1")
connection.close()
```

### Authentication
- [ ] **Auth methods supported?** Username/password, API key, OAuth, certificates?
- [ ] **How to configure?** Connection string params? Separate auth object?
- [ ] **Role/privileges required?** RBAC model? Default roles?

**Quick validation:**
```bash
# Can you connect with test credentials?
{database-cli} -h localhost -u testuser -p testpass -d testdb -c "SELECT 1"
```

### Test Environment
- [ ] **Testcontainers available?** Docker image exists? Version to use?
- [ ] **Or local setup?** Installation instructions? Port configuration?
- [ ] **Cleanup strategy?** Can drop/recreate test databases?

---

## 2. Namespace Management

**For SQL Generator: `createNamespace()`, `namespaceExists()`**

### Namespace Concept
- [ ] **Has namespaces?** Schema, database, catalog, or none?
- [ ] **Qualification?** `schema.table` or `database.table` or just `table`?
- [ ] **Implicit creation?** Created on first use or requires explicit CREATE?

### SQL Operations
- [ ] **Create syntax?** `CREATE SCHEMA`, `CREATE DATABASE`, or N/A?
- [ ] **Check existence?** Query `information_schema`, system catalog, or API?
- [ ] **Drop syntax?** `DROP SCHEMA CASCADE`? Restrictions?

**Quick validation:**
```sql
-- Can you write these queries?
CREATE SCHEMA test_schema;
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'test_schema';
DROP SCHEMA test_schema CASCADE;
```

---

## 3. Table Management

**For SQL Generator: `createTable()`, `dropTable()`, `tableExists()`, `countTable()`**

### Table Operations
- [ ] **Create syntax?** Column definitions, constraints, indexes?
- [ ] **Check existence?** Query system catalog? Try and catch error?
- [ ] **Drop syntax?** `DROP TABLE IF EXISTS`?
- [ ] **Count rows?** `SELECT COUNT(*)`? Performance considerations?
- [ ] **Introspect schema?** `DESCRIBE`, `information_schema.columns`, client API?

**Quick validation:**
```sql
-- Can you write these queries?
CREATE TABLE test_table (id BIGINT, name VARCHAR);
SELECT table_name FROM information_schema.tables WHERE table_name = 'test_table';
SELECT COUNT(*) FROM test_table;
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'test_table';
DROP TABLE IF EXISTS test_table;
```

### Atomic Operations
- [ ] **Rename/swap tables?** `ALTER TABLE RENAME`? `SWAP WITH`? `EXCHANGE TABLES`?
- [ ] **Atomic swap available?** Or need DROP + RENAME pattern?

**Quick validation:**
```sql
-- Can you atomically swap tables?
CREATE TABLE old_table (id INT);
CREATE TABLE new_table (id INT);
ALTER TABLE old_table SWAP WITH new_table;  -- Or your DB's syntax
```

---

## 4. Type System

**For Column Utilities: `toDialectType()`**

### Type Mapping Required
- [ ] **String type?** VARCHAR, TEXT, STRING, CLOB? Max length?
- [ ] **Integer type?** INT, BIGINT, INTEGER, NUMBER? Range?
- [ ] **Decimal type?** DECIMAL(p,s), NUMERIC, FLOAT, DOUBLE? Precision?
- [ ] **Boolean type?** BOOLEAN, TINYINT(1), BIT?
- [ ] **Date type?** DATE format? Storage (days, string, etc.)?
- [ ] **Time type?** TIME, supports timezone? Format?
- [ ] **Timestamp type?** TIMESTAMP, TIMESTAMPTZ, DATETIME? Timezone handling?
- [ ] **JSON type?** JSON, JSONB, VARIANT, or TEXT fallback?
- [ ] **Array type?** Native arrays or JSON encoding?
- [ ] **Binary type?** BLOB, BYTEA, BINARY, or Base64?

**Quick validation:**
```sql
-- Can you create table with all these types?
CREATE TABLE type_test (
    str_col VARCHAR,
    int_col BIGINT,
    dec_col DECIMAL(38,9),
    bool_col BOOLEAN,
    date_col DATE,
    time_col TIME WITH TIME ZONE,
    ts_col TIMESTAMP WITH TIME ZONE,
    json_col JSONB,
    arr_col JSONB,  -- or native array type
    bin_col BYTEA
);
```

### Nullable Handling
- [ ] **Default nullable?** Or default NOT NULL?
- [ ] **Syntax?** `NULL`/`NOT NULL` suffix? `Nullable()` wrapper?

**Quick validation:**
```sql
CREATE TABLE nullable_test (
    nullable_col VARCHAR,
    not_null_col VARCHAR NOT NULL
);
```

### Airbyte Metadata Columns
- [ ] **UUID storage?** Native UUID type or VARCHAR(36)?
- [ ] **Timestamp storage?** Millisecond precision? Timezone?
- [ ] **JSON storage?** JSONB, JSON, VARIANT, or TEXT?
- [ ] **Integer storage?** For generation_id?

**Required types:**
```sql
CREATE TABLE airbyte_test (
    _airbyte_raw_id VARCHAR NOT NULL,        -- UUID as string
    _airbyte_extracted_at TIMESTAMP NOT NULL, -- Extraction time
    _airbyte_meta JSONB NOT NULL,             -- Metadata
    _airbyte_generation_id BIGINT             -- Generation tracking
);
```

---

## 5. Batch Insert Strategy

**For Insert Buffer: `accumulate()`, `flush()`**

### Bulk Insert Methods
- [ ] **Multi-row INSERT?** `INSERT INTO t VALUES (...), (...)`? Row limit?
- [ ] **COPY/LOAD command?** `COPY FROM`, `LOAD DATA`, bulk API?
- [ ] **Staging support?** File upload, external stages, cloud storage?
- [ ] **Binary format?** Native binary protocol for faster inserts?

### Performance Considerations
- [ ] **Optimal batch size?** 100 rows? 1000? 10000?
- [ ] **Compression support?** GZIP, LZ4, Snappy?
- [ ] **Transaction size limits?** Max statement size? Max transaction duration?

**Quick validation:**
```sql
-- Can you insert multiple rows at once?
INSERT INTO test_table (id, name) VALUES
    (1, 'Alice'),
    (2, 'Bob'),
    (3, 'Charlie');

-- Or does your DB prefer COPY/bulk API?
COPY test_table FROM '/path/to/data.csv' WITH (FORMAT CSV);
```

**Decision needed:**
- Simple multi-row INSERT (easy, decent performance)
- CSV staging + COPY (faster for large datasets)
- Binary protocol (fastest, more complex)
- Native bulk API (database-specific)

---

## 6. Deduplication & Upsert

**For SQL Generator: `upsertTable()`**

### Upsert Mechanism
- [ ] **MERGE statement?** Full support with DELETE, UPDATE, INSERT clauses?
- [ ] **INSERT ON CONFLICT?** PostgreSQL-style upsert?
- [ ] **REPLACE INTO?** MySQL-style replace?
- [ ] **None?** Need temp table + window function + DELETE + INSERT approach?

**Quick validation:**
```sql
-- Test 1: Can you upsert with MERGE?
MERGE INTO target USING source ON target.pk = source.pk
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;

-- Test 2: Or INSERT ON CONFLICT?
INSERT INTO target VALUES (...)
ON CONFLICT (pk) DO UPDATE SET ...;

-- Test 3: Or manual approach?
DELETE FROM target WHERE pk IN (SELECT pk FROM source);
INSERT INTO target SELECT * FROM source;
```

### Window Functions
- [ ] **ROW_NUMBER() OVER?** For deduplication?
- [ ] **PARTITION BY?** For grouping by primary key?
- [ ] **ORDER BY in window?** For selecting latest record?

**Quick validation:**
```sql
-- Can you deduplicate with window function?
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY pk
        ORDER BY updated_at DESC
    ) AS rn
    FROM table
) WHERE rn = 1;
```

---

## 7. Schema Evolution

**For SQL Generator: `alterTable()`, Client: `discoverSchema()`, `computeSchema()`**

### ALTER TABLE Support
- [ ] **ADD COLUMN?** Syntax? Can add multiple at once?
- [ ] **DROP COLUMN?** Syntax? Restrictions?
- [ ] **MODIFY/ALTER COLUMN TYPE?** Direct type change? Requires USING clause?
- [ ] **RENAME COLUMN?** Supported?
- [ ] **ALTER CONSTRAINT?** ADD/DROP NOT NULL?

**Quick validation:**
```sql
CREATE TABLE schema_test (id INT);

-- Add column
ALTER TABLE schema_test ADD COLUMN name VARCHAR;

-- Drop column
ALTER TABLE schema_test DROP COLUMN name;

-- Change type
ALTER TABLE schema_test ALTER COLUMN id TYPE BIGINT;

-- Change nullable
ALTER TABLE schema_test ALTER COLUMN id DROP NOT NULL;
```

### Schema Introspection
- [ ] **System catalog?** `information_schema.columns`? `DESCRIBE TABLE`? Client API?
- [ ] **Returns?** Column name, type, nullable, default, precision?

**Quick validation:**
```sql
-- Can you introspect schema?
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'schema_test';
```

### Type Changes
- [ ] **Safe widening?** INT → BIGINT? VARCHAR(50) → VARCHAR(100)?
- [ ] **Unsafe narrowing?** Requires temp column approach? Or table recreation?
- [ ] **Incompatible changes?** VARCHAR → INT? How to handle?

---

## 8. Identifier Rules

**For SQL Generator: All methods**

### Case Sensitivity
- [ ] **Default case?** Lowercase, uppercase, or preserve?
- [ ] **Quoted behavior?** Preserves case? Case-sensitive comparison?
- [ ] **Quoting syntax?** Double quotes, backticks, square brackets?

**Quick validation:**
```sql
-- What happens here?
CREATE TABLE MyTable (MyColumn INT);
SELECT * FROM mytable;  -- Does this work?
SELECT * FROM "MyTable";  -- Does this preserve case?
```

### Reserved Keywords
- [ ] **How to use reserved words?** Must quote? Error if unquoted?
- [ ] **Common reserved keywords?** SELECT, ORDER, USER, TABLE, etc.?

**Quick validation:**
```sql
-- Can you use reserved keywords with quoting?
CREATE TABLE "order" ("user" VARCHAR);
```

### Special Characters
- [ ] **Allowed in identifiers?** Underscores? Hyphens? Unicode?
- [ ] **Max identifier length?** 63 chars (Postgres)? 255 (Snowflake)?

---

## 9. Error Handling

**For Database Client: Error classification**

### Error Codes
- [ ] **SQL State codes?** (e.g., 23505 = unique violation)
- [ ] **Error code system?** Numeric codes? String codes?
- [ ] **Exception hierarchy?** SQLException? Database-specific exceptions?

**Quick validation:**
```kotlin
// Can you classify errors?
try {
    connection.execute("INSERT INTO t VALUES (1, 1)")  // Duplicate PK
    connection.execute("INSERT INTO t VALUES (1, 2)")  // Duplicate PK
} catch (e: SQLException) {
    println("SQL State: ${e.sqlState}")  // 23505?
    println("Error code: ${e.errorCode}")
    println("Message: ${e.message}")
}
```

### Permission Errors
- [ ] **How to detect?** Error message keywords? SQL State?
- [ ] **Common patterns?** "permission denied", "insufficient privileges"?

---

## 10. Testing Setup

**For all phases**

### Test Environment
- [ ] **Testcontainers image?** `{database}:latest`? Specific version?
- [ ] **Or local install?** Installation steps? Default config?
- [ ] **Port?** Default port number? Configurable?

### Test Operations
- [ ] **Insert test data?** Prepared statements? Bulk API?
- [ ] **Read data back?** ResultSet iteration? Native API?
- [ ] **Type conversion?** AirbyteValue → DB types in tests?

---

## Quick Database Survey

**Answer these to assess readiness:**

| Question | Your Answer | Needed For |
|----------|-------------|------------|
| JDBC driver or native client? | | Phase 1 |
| Connection string format? | | Phase 1 |
| CREATE SCHEMA or CREATE DATABASE? | | Phase 2 |
| CREATE TABLE syntax? | | Phase 3 |
| String type (VARCHAR/TEXT/STRING)? | | Phase 3 |
| Integer type (INT/BIGINT/NUMBER)? | | Phase 3 |
| JSON type (JSONB/JSON/VARIANT)? | | Phase 3 |
| Timestamp type with timezone? | | Phase 3 |
| Has MERGE or INSERT ON CONFLICT? | | Phase 9 |
| Has window functions (ROW_NUMBER)? | | Phase 9 |
| Has ALTER TABLE ADD/DROP COLUMN? | | Phase 8 |
| System catalog for introspection? | | Phase 8 |
| Atomic table swap/exchange? | | Phase 6 |
| Optimal batch size for inserts? | | Phase 5 |

---

## Research Template

**Use this to document your findings:**

```markdown
# {Database} Connector Preflight Research

## 1. Connection & Client
- **Driver:** [JDBC / Native / HTTP API]
- **Maven coordinates:** `group:artifact:version`
- **Connection string:** `protocol://host:port/database?options`
- **Auth method:** [username/password / API key / other]
- **Connection pooling:** [HikariCP / built-in / manual]

## 2. Namespaces
- **Concept:** [Schema / Database / None]
- **Create:** `CREATE SCHEMA name` or `CREATE DATABASE name`
- **Check exists:** `SELECT ... FROM information_schema.schemata`
- **Drop:** `DROP SCHEMA name CASCADE`

## 3. Tables
- **Create:** `CREATE TABLE schema.table (cols...)`
- **Check exists:** `SELECT ... FROM information_schema.tables`
- **Drop:** `DROP TABLE IF EXISTS schema.table`
- **Describe:** `DESCRIBE TABLE` or `SELECT ... FROM information_schema.columns`
- **Swap:** `ALTER TABLE ... SWAP WITH ...` or recreation needed

## 4. Type Mapping
| Airbyte Type | Database Type | Notes |
|--------------|---------------|-------|
| String | VARCHAR / TEXT | Length limit? |
| Integer | BIGINT | Range? |
| Number | DECIMAL(38,9) | Precision? |
| Boolean | BOOLEAN | Or TINYINT? |
| Date | DATE | Format? |
| Timestamp+TZ | TIMESTAMPTZ | Precision? |
| JSON | JSONB | Or JSON / TEXT? |
| Array | JSONB | Or native array? |

## 5. Bulk Insert
- **Best method:** [Multi-row INSERT / COPY / Staging / Bulk API]
- **Batch size:** [1000 / 10000 / custom]
- **Compression:** [GZIP / LZ4 / None]
- **Example:** `COPY table FROM file WITH (...)`

## 6. Upsert
- **Method:** [MERGE / INSERT ON CONFLICT / REPLACE / Manual DELETE+INSERT]
- **Syntax:** `MERGE INTO ... USING ... ON ... WHEN MATCHED ...`
- **Window functions:** [ROW_NUMBER OVER supported? YES/NO]

## 7. Schema Evolution
- **ADD COLUMN:** `ALTER TABLE t ADD COLUMN c type`
- **DROP COLUMN:** `ALTER TABLE t DROP COLUMN c`
- **CHANGE TYPE:** `ALTER TABLE t ALTER COLUMN c TYPE newtype` or temp column approach
- **Discover schema:** `SELECT ... FROM information_schema.columns`

## 8. Identifiers
- **Case:** [Lowercase / Uppercase / Preserve]
- **Quoting:** [" / ` / [] ]
- **Reserved keywords:** [List common ones]
- **Max length:** [63 / 255 / other]

## 9. Errors
- **SQL State codes:** [23505 = unique violation, etc.]
- **Exception type:** [SQLException / DatabaseException / custom]
- **Permission errors:** [Pattern in error message]

## 10. Testing
- **Testcontainers:** `{database}Container("{db}:latest")`
- **Or local:** [Installation command]
- **Default port:** [5432 / 3306 / etc.]
```

---

## Validation Questions

**Before starting Phase 1, can you answer YES to all?**

### Critical (Must Have)
- [ ] I can establish a connection programmatically
- [ ] I know how to execute a simple query
- [ ] I know the CREATE TABLE syntax
- [ ] I know how to map basic types (String, Integer, Boolean, Timestamp)
- [ ] I can insert records programmatically
- [ ] I can read records back for verification
- [ ] I have a test environment (Testcontainers or local)

### Important (Needed for Full Features)
- [ ] I know how to create/drop namespaces (schemas/databases)
- [ ] I know how to check if table/namespace exists
- [ ] I know the system catalog for schema introspection
- [ ] I know how to handle JSON/JSONB data
- [ ] I know at least one bulk insert method
- [ ] I know how to swap/rename tables atomically (or workaround)

### Nice to Have (Can Research During Implementation)
- [ ] I know the optimal batch size for bulk inserts
- [ ] I know how to handle all edge case types (arrays, binary, etc.)
- [ ] I know database-specific optimization tricks
- [ ] I know all error codes for better error messages

---

## Red Flags (May Need Alternative Approach)

**If you answer YES to any, plan workarounds:**

- [ ] **No MERGE or INSERT ON CONFLICT?** → Use temp table + window function + DELETE + INSERT
- [ ] **No ALTER TABLE?** → Use table recreation for schema changes
- [ ] **No window functions?** → Dedupe via application logic (slower)
- [ ] **No atomic swap?** → Use temp table + DROP + RENAME (brief inconsistency window)
- [ ] **No JSON type?** → Use TEXT with JSON string encoding
- [ ] **No schemas/namespaces?** → Use table name prefixes

---

## Time Estimates by Familiarity

| Database Familiarity | Research Time | Total Implementation |
|---------------------|---------------|---------------------|
| **Expert** (daily use) | 30 min | 3-4 days |
| **Familiar** (used before) | 2-3 hours | 4-5 days |
| **New** (never used) | 4-8 hours | 5-7 days |
| **Exotic** (limited docs) | 8-16 hours | 7-10 days |

**Recommendation:** Spend the research time upfront. It pays off during implementation.

---

## Helpful Resources

### Documentation to Review
- [ ] Database SQL reference (CREATE, ALTER, DROP, INSERT)
- [ ] JDBC driver documentation (if applicable)
- [ ] Native client SDK documentation
- [ ] Type system reference
- [ ] System catalog documentation (information_schema or equivalent)
- [ ] Transaction and isolation level documentation

### Code References
- [ ] Existing connector for similar database (Postgres → MySQL, Snowflake → Databricks)
- [ ] Database driver examples and sample code
- [ ] Testcontainers examples

### Testing
- [ ] Set up local database instance or Testcontainers
- [ ] Connect via CLI and test all operations manually
- [ ] Write a simple JDBC/client test program

---

## Next Steps After Completing Checklist

**If you can answer all Critical questions:**
→ **Proceed to Phase 0 (Scaffolding)** in step-by-step-guide.md

**If you're missing Important knowledge:**
→ **Research those areas first** - they're needed by Phase 6-9

**If you're missing Nice to Have knowledge:**
→ **Start implementation anyway** - research these as needed during development

**If you hit Red Flags:**
→ **Review implementation-reference.md** for alternative approaches
→ **Consider asking in Airbyte community** if workarounds exist

---

## Checklist Summary

**Complete these research tasks (2-4 hours):**

1. ✅ Set up test environment (Testcontainers or local)
2. ✅ Test connection via CLI and code
3. ✅ Write CREATE/DROP operations for namespace and table
4. ✅ Map all Airbyte types to database types
5. ✅ Test bulk insert (multi-row or COPY or API)
6. ✅ Test upsert mechanism (MERGE or INSERT ON CONFLICT or workaround)
7. ✅ Test schema introspection (system catalog queries)
8. ✅ Test ALTER TABLE operations
9. ✅ Document identifier rules (case, quoting, keywords)
10. ✅ Document error codes and exception types

**Output:** Research document with all findings

**Then:** Proceed to step-by-step-guide.md Phase 0

**Estimated effort to implement:** 3-7 days depending on database familiarity
