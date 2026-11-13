# Preflight Checklist: Database Knowledge for Source Connectors

**Summary:** Essential database knowledge required before implementing a JVM source connector. Complete this checklist to ensure you have the information needed for the core components (Source Operations, Metadata Querier, State Management, CDC Configuration).

**Time to complete:** 2-4 hours of research for unfamiliar database

---

## 1. Connection & Client Setup

**For Source Configuration + JDBC Operations**

### Driver & Connection
- [ ] **JDBC driver available?** Standard JDBC, native client, or HTTP API?
- [ ] **Connection string format?** `jdbc:db://host:port/database` or custom URI?
- [ ] **Connection pooling?** HikariCP compatible? Connection limits?

**Quick validation:**
```kotlin
// Can you write this code?
val connection = DriverManager.getConnection(
    "jdbc:database://localhost:5432/testdb",
    "user", "password"
)
connection.createStatement().executeQuery("SELECT 1")
connection.close()
```

### Authentication
- [ ] **Auth methods supported?** Username/password, API key, OAuth, certificates?
- [ ] **SSL/TLS options?** Preferred, required, verify CA, verify identity?
- [ ] **SSH tunneling?** Supported for secure connectivity?

**Quick validation:**
```bash
# Can you connect with test credentials?
{database-cli} -h localhost -u testuser -p testpass -d testdb -c "SELECT 1"
```

### Test Environment
- [ ] **Testcontainers available?** Docker image exists? Version to use?
- [ ] **Or local setup?** Installation instructions? Port configuration?
- [ ] **Sample data?** Can create test schemas with various data types?

---

## 2. Schema Discovery

**For Metadata Querier: `discoverTables()`, `discoverColumns()`**

### Catalog/Schema Structure
- [ ] **Has catalogs?** Database → Schema → Table hierarchy?
- [ ] **Namespace concept?** Schema-qualified tables? Database-qualified?
- [ ] **Default schema?** `public`, `dbo`, or user-specific?

### System Catalog Queries
- [ ] **List tables?** `information_schema.tables`? System catalog?
- [ ] **List columns?** `information_schema.columns`? `DESCRIBE TABLE`?
- [ ] **Get primary keys?** `information_schema.table_constraints`? System views?
- [ ] **Get foreign keys?** Needed for relationship discovery?

**Quick validation:**
```sql
-- Can you discover schema?
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE';

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'my_table';

SELECT column_name
FROM information_schema.key_column_usage
WHERE table_name = 'my_table' AND constraint_name LIKE '%pkey%';
```

---

## 3. Type System

**For Source Operations: `getAirbyteType()`, `setJsonField()`**

### Type Mapping Required
- [ ] **String types?** VARCHAR, TEXT, CHAR, CLOB? Length metadata?
- [ ] **Integer types?** TINYINT, SMALLINT, INT, BIGINT? Signed/unsigned?
- [ ] **Decimal types?** DECIMAL(p,s), NUMERIC, FLOAT, DOUBLE? Precision/scale?
- [ ] **Boolean type?** BOOLEAN, BIT, TINYINT(1)?
- [ ] **Date type?** DATE format? Range limitations?
- [ ] **Time type?** TIME, with/without timezone?
- [ ] **Timestamp type?** TIMESTAMP, DATETIME? Timezone handling?
- [ ] **JSON type?** JSON, JSONB, or TEXT fallback?
- [ ] **Array type?** Native arrays or serialized?
- [ ] **Binary type?** BLOB, BYTEA, VARBINARY?
- [ ] **Special types?** UUID, ENUM, geometric, network addresses?

**Quick validation:**
```sql
-- Can you create and query all these types?
CREATE TABLE type_test (
    str_col VARCHAR(255),
    int_col BIGINT,
    dec_col DECIMAL(38,9),
    bool_col BOOLEAN,
    date_col DATE,
    time_col TIME,
    ts_col TIMESTAMP WITH TIME ZONE,
    json_col JSONB,
    bin_col BYTEA
);

INSERT INTO type_test VALUES (...);
SELECT * FROM type_test;
```

### JDBC ResultSet Handling
- [ ] **getObject() behavior?** Returns native types or wrapper objects?
- [ ] **getString() for all?** Can convert all types to strings?
- [ ] **Null handling?** `wasNull()` method reliable?
- [ ] **Large objects?** Streaming for BLOB/CLOB?

**Quick validation:**
```kotlin
// Can you extract values correctly?
val rs = stmt.executeQuery("SELECT * FROM type_test")
while (rs.next()) {
    val strVal = rs.getString("str_col")
    val intVal = rs.getLong("int_col")
    val decVal = rs.getBigDecimal("dec_col")
    val boolVal = rs.getBoolean("bool_col")
    val dateVal = rs.getDate("date_col")
    val tsVal = rs.getTimestamp("ts_col")
    // How to handle JSON? Binary?
}
```

---

## 4. Incremental Sync Support

**For State Management: Cursor-based incremental**

### Cursor Column Requirements
- [ ] **Sortable columns?** Timestamp, integer ID, or other sortable types?
- [ ] **Index support?** Can add indexes on cursor columns?
- [ ] **Null handling?** How to handle NULL cursor values?
- [ ] **Timezone consistency?** Server vs client timezone handling?

### Query Patterns
- [ ] **Range queries efficient?** `WHERE cursor > :last_value`?
- [ ] **Order by cursor?** `ORDER BY cursor ASC` performant?
- [ ] **Limit support?** `LIMIT :batch_size` or `FETCH FIRST`?

**Quick validation:**
```sql
-- Can you do efficient incremental reads?
SELECT * FROM my_table
WHERE updated_at > '2024-01-01 00:00:00'
ORDER BY updated_at ASC
LIMIT 10000;

-- Check query plan
EXPLAIN SELECT * FROM my_table WHERE updated_at > '2024-01-01';
```

---

## 5. Change Data Capture (CDC)

**For CDC Module: Debezium integration (if supported)**

### CDC Capability
- [ ] **Has replication protocol?** Logical replication, binlog, transaction log?
- [ ] **Debezium connector exists?** Check Debezium connectors list
- [ ] **Required privileges?** REPLICATION, SELECT, or specific grants?
- [ ] **Server configuration?** WAL level, binlog format settings?

### CDC Prerequisites
- [ ] **Replication slot/publication?** Postgres-style or MySQL binlog?
- [ ] **Position tracking?** LSN (Postgres), binlog file+position (MySQL)?
- [ ] **Snapshot capability?** Initial full read before streaming changes?

**Quick validation (Postgres):**
```sql
-- Check replication settings
SHOW wal_level;  -- Should be 'logical'
SELECT * FROM pg_replication_slots;

-- Create publication (for logical replication)
CREATE PUBLICATION my_publication FOR ALL TABLES;
```

**Quick validation (MySQL):**
```sql
-- Check binlog settings
SHOW VARIABLES LIKE 'log_bin';  -- Should be ON
SHOW VARIABLES LIKE 'binlog_format';  -- Should be ROW

-- Check privileges
SHOW GRANTS FOR CURRENT_USER;  -- Need REPLICATION SLAVE, REPLICATION CLIENT
```

### CDC State Tracking
- [ ] **Position format?** LSN, GTID, binlog coordinates?
- [ ] **Resumable?** Can restart from saved position?
- [ ] **Gap handling?** What happens if position is no longer available?

---

## 6. Full Refresh Support

**For Partition Factory: Full table reads**

### Table Scan Patterns
- [ ] **Full scan efficient?** Table size considerations?
- [ ] **Chunked reads?** Can split by primary key ranges?
- [ ] **Row identifiers?** CTID (Postgres), internal row ID, or PK only?

### Postgres-Specific (CTID)
- [ ] **CTID available?** Hidden column for physical row location?
- [ ] **CTID stable?** Only during single transaction?
- [ ] **Range queries?** `WHERE ctid > '(page,offset)'`?

**Quick validation (Postgres):**
```sql
-- Can you use CTID for chunked reads?
SELECT ctid, * FROM my_table WHERE ctid > '(0,0)' LIMIT 1000;
```

### MySQL-Specific
- [ ] **Primary key based?** Split by PK ranges?
- [ ] **LIMIT OFFSET?** Or keyset pagination?

---

## 7. Connection & Resource Management

**For Source Configuration + Operations**

### Connection Limits
- [ ] **Max connections?** Database limit? Pool sizing?
- [ ] **Timeout settings?** Query timeout, connection timeout?
- [ ] **Keep-alive?** Long-running query support?

### Transaction Handling
- [ ] **Read consistency?** Repeatable read for consistent snapshots?
- [ ] **Cursor stability?** Server-side cursors for large result sets?
- [ ] **Streaming results?** Avoid loading entire table into memory?

**Quick validation:**
```kotlin
// Can you stream large results?
val stmt = connection.createStatement()
stmt.fetchSize = 1000  // Stream results
val rs = stmt.executeQuery("SELECT * FROM large_table")
```

---

## 8. Error Handling

**For Exception Handler**

### Error Codes
- [ ] **SQL State codes?** (e.g., 23505 = unique violation)
- [ ] **Database-specific codes?** Vendor error codes?
- [ ] **Exception types?** SQLException subclasses?

**Quick validation:**
```kotlin
try {
    connection.execute("SELECT * FROM nonexistent_table")
} catch (e: SQLException) {
    println("SQL State: ${e.sqlState}")
    println("Error code: ${e.errorCode}")
    println("Message: ${e.message}")
}
```

### Retryable vs Config Errors
- [ ] **Network errors?** Connection timeout, reset?
- [ ] **Permission errors?** Access denied patterns?
- [ ] **Transient errors?** Deadlock, lock timeout?

---

## 9. Performance Considerations

**For Production readiness**

### Query Optimization
- [ ] **Index usage?** Queries use indexes for cursor columns?
- [ ] **Parallel reads?** Can split across multiple connections?
- [ ] **Memory usage?** Streaming vs buffered results?

### Large Table Handling
- [ ] **Row estimation?** `pg_class.reltuples`, `information_schema`?
- [ ] **Chunk sizing?** Adaptive based on table size?
- [ ] **Progress tracking?** Percentage complete estimation?

---

## 10. Testing Setup

**For all phases**

### Test Environment
- [ ] **Testcontainers image?** `{database}Container("{db}:latest")`?
- [ ] **Or local install?** Installation steps? Default config?
- [ ] **CDC-enabled image?** Pre-configured for replication?

### Test Operations
- [ ] **Create test tables?** Various types, sizes?
- [ ] **Insert test data?** Bulk insert for performance tests?
- [ ] **Verify reads?** Compare source data to extracted data?

---

## Quick Database Survey

**Answer these to assess readiness:**

| Question | Your Answer | Needed For |
|----------|-------------|------------|
| JDBC driver coordinates? | | Configuration |
| Connection string format? | | Configuration |
| Schema discovery queries? | | Metadata Querier |
| Type mapping for all types? | | Source Operations |
| Cursor column patterns? | | Incremental Sync |
| CDC/replication available? | | CDC Module |
| Debezium connector exists? | | CDC Module |
| CTID or chunking strategy? | | Full Refresh |
| Error code patterns? | | Exception Handler |

---

## Research Template

**Use this to document your findings:**

```markdown
# {Database} Source Connector Preflight Research

## 1. Connection & Client
- **JDBC Driver:** [Maven coordinates]
- **Connection string:** `jdbc:{db}://host:port/database`
- **Auth methods:** [username/password / SSL / SSH tunnel]
- **Connection pooling:** [HikariCP compatible: YES/NO]

## 2. Schema Discovery
- **List tables:** `SELECT ... FROM information_schema.tables`
- **List columns:** `SELECT ... FROM information_schema.columns`
- **Get primary keys:** `SELECT ... FROM information_schema.key_column_usage`
- **Namespace model:** [catalog.schema.table / schema.table / table]

## 3. Type Mapping
| Database Type | Airbyte Type | Notes |
|---------------|--------------|-------|
| VARCHAR | StringType | Max length? |
| BIGINT | IntegerType | |
| DECIMAL(p,s) | NumberType | |
| BOOLEAN | BooleanType | Or BIT? |
| DATE | DateType | |
| TIMESTAMP | TimestampType | With/without TZ? |
| JSON/JSONB | ObjectType | |
| ARRAY | ArrayType | Native or JSON? |

## 4. Incremental Sync
- **Cursor types:** [TIMESTAMP / BIGINT ID / other]
- **Efficient range query:** `SELECT * FROM t WHERE cursor > ? ORDER BY cursor LIMIT ?`
- **Null cursor handling:** [COALESCE / filter out / include]

## 5. CDC Support
- **Replication type:** [Logical replication / Binlog / None]
- **Debezium connector:** [YES: version / NO]
- **Required settings:** [wal_level=logical / log_bin=ON / etc.]
- **Position format:** [LSN / GTID / binlog file:pos]
- **Required privileges:** [REPLICATION / SELECT / etc.]

## 6. Full Refresh
- **Chunking strategy:** [CTID / PK ranges / LIMIT OFFSET]
- **Row identifier:** [CTID / internal ID / PK only]
- **Streaming results:** [fetchSize setting / native cursor]

## 7. Error Patterns
- **Permission denied:** [SQL State / error message pattern]
- **Connection errors:** [SQL State / error message pattern]
- **Transient errors:** [SQL State / error message pattern]

## 8. Testing
- **Testcontainers:** `{Database}Container("{image}:latest")`
- **Default port:** [5432 / 3306 / etc.]
- **CDC-enabled image:** [Image name or configuration steps]
```

---

## Validation Questions

**Before starting implementation, can you answer YES to all?**

### Critical (Must Have)
- [ ] I can establish a JDBC connection
- [ ] I can query the schema catalog for tables and columns
- [ ] I can map database types to Airbyte types
- [ ] I can read data from tables via ResultSet
- [ ] I have a test environment (Testcontainers or local)

### Important (Needed for Full Features)
- [ ] I know how to do efficient incremental reads (cursor-based)
- [ ] I know if CDC is available and how to configure it
- [ ] I know how to stream large result sets
- [ ] I know the error code patterns for classification

### Nice to Have (Can Research During Implementation)
- [ ] I know optimal batch sizes for large tables
- [ ] I know how to estimate table row counts
- [ ] I know database-specific optimization tricks

---

## Red Flags (May Need Alternative Approach)

**If you answer YES to any, plan workarounds:**

- [ ] **No JDBC driver?** -> May need native client or HTTP API approach
- [ ] **No cursor-friendly columns?** -> May need composite cursors or full refresh only
- [ ] **No CDC support?** -> Cursor-based incremental only (no deletes detected)
- [ ] **No streaming results?** -> Memory management for large tables
- [ ] **Limited type support?** -> Custom type handlers needed

---

## CDC-Specific Checklist

**If implementing CDC support:**

### Debezium Integration
- [ ] Debezium connector exists for this database
- [ ] Know the Debezium connector class name
- [ ] Know the position/offset format
- [ ] Know required server configuration
- [ ] Know required privileges

### State Management
- [ ] Know how to serialize CDC position
- [ ] Know how to validate saved position is still valid
- [ ] Know how to handle position gaps (e.g., WAL segments deleted)

### Snapshot + Streaming
- [ ] Know how to do initial snapshot
- [ ] Know how to transition from snapshot to streaming
- [ ] Know how to handle schema changes during streaming

---

## Next Steps After Completing Checklist

**If you can answer all Critical questions:**
-> **Proceed to implementation** using dataflow-cdk.md

**If you're missing Important knowledge:**
-> **Research those areas first** - they're needed for production quality

**If you hit Red Flags:**
-> **Review implementation-reference.md** for alternative approaches
-> **Consider asking in Airbyte community** if workarounds exist

---

## Checklist Summary

**Complete these research tasks (2-4 hours):**

1. Set up test environment (Testcontainers or local)
2. Test JDBC connection and basic queries
3. Write schema discovery queries (tables, columns, PKs)
4. Map all database types to Airbyte types
5. Test incremental read patterns (cursor-based WHERE/ORDER BY)
6. Investigate CDC support and configuration
7. Test streaming large result sets
8. Document error code patterns

**Output:** Research document with all findings

**Then:** Proceed to implementation using dataflow-cdk.md and implementation-reference.md
