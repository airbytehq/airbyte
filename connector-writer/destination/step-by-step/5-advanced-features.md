# Advanced Features: Production-Ready Connector

**Summary:** Add enterprise features to your connector: schema evolution, dedupe mode with primary keys, CDC support for deletions, and performance optimization. After completing this guide, your connector will be production-ready.

---

## Prerequisites

**Complete:** [4-write-operations.md](./4-write-operations.md) - Your connector must have working append and overwrite modes.

---

## What You'll Build

After completing this guide, you'll have a production-ready connector with:

- **Schema evolution:** Automatic column add/drop/modify when source schema changes
- **Dedupe mode:** MERGE with primary key for incremental syncs
- **CDC support:** Handle hard/soft deletes from change data capture sources
- **Performance optimization:** Efficient batch writes for large datasets
- **Production readiness:** Suitable for enterprise use

---

## Advanced Phase 1: Schema Evolution

**Goal:** Automatically adapt to schema changes

**Checkpoint:** Can add, drop, and modify columns

**📋 Schema Evolution Scenarios:**
1. **Add column**: Source adds new field → add column to destination
2. **Drop column**: Source removes field → drop column from destination (optional)
3. **Change type**: Source changes field type → alter column (with casting)
4. **Change nullability**: Source changes nullable → alter column constraints

### Advanced Step 1: Implement discoverSchema()

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun discoverSchema(tableName: TableName): TableSchema {
    val columns = getColumnsFromDb(tableName)
    return TableSchema(columns)
}

private fun getColumnsFromDb(tableName: TableName): Map<String, ColumnType> {
    val columns = mutableMapOf<String, ColumnType>()

    dataSource.connection.use { connection ->
        // Postgres/MySQL: Query information_schema.columns
        val sql = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = '${tableName.namespace}'
              AND table_name = '${tableName.name}'
        """

        connection.createStatement().use { statement ->
            val rs = statement.executeQuery(sql)

            while (rs.next()) {
                val columnName = rs.getString("column_name")

                // Skip Airbyte metadata columns
                if (columnName in AIRBYTE_META_COLUMNS) continue

                val dataType = rs.getString("data_type")
                    .takeWhile { it != '(' }  // Strip precision (e.g., VARCHAR(255) → VARCHAR)
                val nullable = rs.getString("is_nullable") == "YES"

                columns[columnName] = ColumnType(dataType, nullable)
            }
        }
    }

    return columns
}

private val AIRBYTE_META_COLUMNS = setOf(
    "_airbyte_raw_id",
    "_airbyte_extracted_at",
    "_airbyte_meta",
    "_airbyte_generation_id"
)
```

**Database-specific approaches:**
- **Snowflake**: `DESCRIBE TABLE` or `SHOW COLUMNS`
- **Postgres/MySQL**: `information_schema.columns`
- **ClickHouse**: `system.columns` or client API `getTableSchema()`
- **BigQuery**: `INFORMATION_SCHEMA.COLUMNS`

### Advanced Step 2: Implement computeSchema()

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override fun computeSchema(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping
): TableSchema {
    val columns = stream.schema.asColumns()
        .filter { (name, _) -> name !in AIRBYTE_META_COLUMNS }
        .mapKeys { (name, _) -> columnNameMapping[name]!! }
        .mapValues { (_, field) ->
            val dbType = columnUtils.toDialectType(field.type)
                .takeWhile { it != '(' }  // Strip precision
            ColumnType(dbType, field.nullable)
        }

    return TableSchema(columns)
}
```

**What this does:**
- Converts Airbyte schema → database schema
- Applies column name mapping (Phase 6 generators)
- Uses ColumnUtils.toDialectType() from Phase 4

### Advanced Step 3: Implement alterTable() - ADD COLUMN

**File:** Update `client/{DB}SqlGenerator.kt`

```kotlin
fun alterTable(
    tableName: TableName,
    columnsToAdd: Map<String, ColumnType>,
    columnsToDrop: Map<String, ColumnType>,
    columnsToChange: Map<String, ColumnTypeChange>,
): Set<String> {
    val statements = mutableSetOf<String>()

    // ADD COLUMN (simplest - implement first)
    columnsToAdd.forEach { (name, type) ->
        val nullableClause = if (type.nullable) "" else " NOT NULL"
        statements.add(
            "ALTER TABLE ${fullyQualifiedName(tableName)} ADD COLUMN \"$name\" ${type.type}$nullableClause".andLog()
        )
    }

    // DROP COLUMN (implement second)
    columnsToDrop.forEach { (name, _) ->
        statements.add(
            "ALTER TABLE ${fullyQualifiedName(tableName)} DROP COLUMN \"$name\"".andLog()
        )
    }

    // MODIFY COLUMN (implement last - most complex)
    columnsToChange.forEach { (name, typeChange) ->
        // See Step 12.4 for implementation
    }

    return statements
}
```

### Advanced Step 4: Implement alterTable() - MODIFY COLUMN

**Add to alterTable():**

```kotlin
columnsToChange.forEach { (name, typeChange) ->
    when {
        // Safe: NOT NULL → NULL (widen constraint)
        !typeChange.originalType.nullable && typeChange.newType.nullable -> {
            // Postgres/MySQL
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} ALTER COLUMN \"$name\" DROP NOT NULL".andLog()
            )

            // Or Snowflake
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} MODIFY COLUMN \"$name\" DROP NOT NULL".andLog()
            )
        }

        // Unsafe: Type change - use temp column approach
        typeChange.originalType.type != typeChange.newType.type -> {
            val tempColumn = "${name}_${UUID.randomUUID().toString().replace("-", "").take(8)}"
            val backupColumn = "${name}_backup"

            // 1. Add temp column with new type
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} ADD COLUMN \"$tempColumn\" ${typeChange.newType.type}".andLog()
            )

            // 2. Cast and copy data
            statements.add(
                "UPDATE ${fullyQualifiedName(tableName)} SET \"$tempColumn\" = CAST(\"$name\" AS ${typeChange.newType.type})".andLog()
            )

            // 3. Rename original to backup
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} RENAME COLUMN \"$name\" TO \"$backupColumn\"".andLog()
            )

            // 4. Rename temp to original
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} RENAME COLUMN \"$tempColumn\" TO \"$name\"".andLog()
            )

            // 5. Drop backup
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} DROP COLUMN \"$backupColumn\"".andLog()
            )
        }

        // Unsafe: NULL → NOT NULL (skip - may fail with existing NULLs)
        typeChange.originalType.nullable && !typeChange.newType.nullable -> {
            log.info { "Skipping change from nullable to non-nullable for column $name (may have NULL values)" }
        }

        // No change needed
        else -> {
            log.debug { "No schema change needed for column $name" }
        }
    }
}
```

**Alternative: Table Recreation (ClickHouse pattern):**

For databases where ALTER is expensive or impossible (e.g., changing primary key):

```kotlin
fun recreateTable(
    stream: DestinationStream,
    oldTableName: TableName,
    newTableName: TableName,
    columnMapping: ColumnNameMapping
): List<String> {
    return listOf(
        // 1. Create new table with new schema
        createTable(stream, newTableName, columnMapping, replace = false),

        // 2. Copy data (with type casting)
        copyTable(columnMapping, oldTableName, newTableName),

        // 3. Drop old table
        dropTable(oldTableName),

        // 4. Rename new table to old name
        "ALTER TABLE ${fullyQualifiedName(newTableName)} RENAME TO ${oldTableName.name.quote()}".andLog()
    )
}
```

### Advanced Step 5: Implement applyChangeset()

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun applyChangeset(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    tableName: TableName,
    expectedColumns: TableColumns,
    columnChangeset: ColumnChangeset,
) {
    if (columnChangeset.isNoop()) return

    log.info { "Summary of table alterations for ${tableName}:" }
    log.info { "  Added columns: ${columnChangeset.columnsToAdd.keys}" }
    log.info { "  Dropped columns: ${columnChangeset.columnsToDrop.keys}" }
    log.info { "  Modified columns: ${columnChangeset.columnsToChange.keys}" }

    val statements = sqlGenerator.alterTable(
        tableName,
        columnChangeset.columnsToAdd,
        columnChangeset.columnsToDrop,
        columnChangeset.columnsToChange,
    )

    statements.forEach { execute(it) }
}
```

### Advanced Step 6: Implement ensureSchemaMatches()

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun ensureSchemaMatches(
    stream: DestinationStream,
    tableName: TableName,
    columnNameMapping: ColumnNameMapping
) {
    val actualSchema = discoverSchema(tableName)
    val expectedSchema = computeSchema(stream, columnNameMapping)
    val changeset = actualSchema.diff(expectedSchema)

    if (!changeset.isNoop()) {
        log.info { "Schema mismatch detected for ${tableName}, applying changes" }
        applyChangeset(stream, columnNameMapping, tableName, expectedSchema.columns, changeset)
    } else {
        log.debug { "Schema matches for ${tableName}, no changes needed" }
    }
}
```

**When is this called?**
- StreamLoader.start() calls ensureSchemaMatches() before writing
- If source schema changed since last sync, applies schema changes
- Automatic - no user intervention needed

### Advanced Step 7: Validate Schema Evolution

**Validate:**
```bash
$ ./gradlew :destination-{db}:componentTest  # 12 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass
```

✅ **Checkpoint:** Schema evolution works + all previous phases still work

---

---

## Advanced Phase 2: Dedupe Mode

**Goal:** Support primary key deduplication

**Checkpoint:** Can deduplicate by primary key with "last write wins"

**📋 Dedupe Strategy:**
1. Write all records to temp table
2. Deduplicate in temp table (ROW_NUMBER() by primary key, ordered by cursor DESC)
3. Upsert from temp to final:
   - Match on primary key
   - Update if cursor is newer
   - Insert if no match

**Sync modes:**
- **Append** (Phase 8): Just insert
- **Overwrite** (Phase 10): Swap tables
- **Dedupe** (Phase 13): Upsert with primary key

### Advanced Step 1: Implement upsertTable() in SQL Generator

**Option A: MERGE Statement (Snowflake, SQL Server, BigQuery)**

**File:** Update `client/{DB}SqlGenerator.kt`

```kotlin
fun upsertTable(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    source: TableName,
    target: TableName
): String {
    val importType = stream.importType as Dedupe
    val pkColumns = importType.primaryKey.map { columnNameMapping[it]!! }
    val allColumns = columnNameMapping.values.toList()

    // Cursor column (for "last write wins" logic)
    val cursorColumn = if (importType.cursor.isNotEmpty()) {
        columnNameMapping[importType.cursor.first()]!!
    } else {
        "_airbyte_extracted_at"  // Fallback to extraction timestamp
    }

    // Deduplication CTE (keep latest record per primary key)
    val dedupCte = if (pkColumns.isNotEmpty()) {
        """
        WITH deduped AS (
          SELECT *, ROW_NUMBER() OVER (
            PARTITION BY ${pkColumns.joinToString(", ") { "\"$it\"" }}
            ORDER BY "$cursorColumn" DESC, "_airbyte_extracted_at" DESC
          ) AS rn
          FROM ${fullyQualifiedName(source)}
        )
        SELECT * FROM deduped WHERE rn = 1
        """
    } else {
        // No primary key - just dedupe by all columns (inefficient but safe)
        "SELECT * FROM ${fullyQualifiedName(source)}"
    }

    // Primary key match condition (handles NULLs)
    val pkMatch = pkColumns.joinToString(" AND ") { col ->
        """(target."$col" = source."$col" OR (target."$col" IS NULL AND source."$col" IS NULL))"""
    }

    // Cursor comparison (for UPDATE condition)
    val cursorComparison = """
        (
          target."$cursorColumn" < source."$cursorColumn"
          OR (target."$cursorColumn" = source."$cursorColumn" AND target."_airbyte_extracted_at" < source."_airbyte_extracted_at")
          OR (target."$cursorColumn" IS NULL AND source."$cursorColumn" IS NOT NULL)
        )
    """.trimIndent()

    // Column assignments for UPDATE
    val columnAssignments = allColumns.joinToString(",\n    ") { col ->
        "\"$col\" = source.\"$col\""
    }

    // Column list for INSERT
    val columnList = allColumns.joinToString(", ") { "\"$it\"" }
    val sourceColumnList = allColumns.joinToString(", ") { "source.\"$it\"" }

    return """
        MERGE INTO ${fullyQualifiedName(target)} AS target
        USING (
          $dedupCte
        ) AS source
        ON $pkMatch
        WHEN MATCHED AND $cursorComparison THEN UPDATE SET
          $columnAssignments
        WHEN NOT MATCHED THEN INSERT (
          $columnList
        ) VALUES (
          $sourceColumnList
        )
    """.trimIndent().andLog()
}
```

**Option B: INSERT ... ON CONFLICT (Postgres, SQLite)**

```kotlin
fun upsertTable(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    source: TableName,
    target: TableName
): List<String> {
    val importType = stream.importType as Dedupe
    val pkColumns = importType.primaryKey.map { columnNameMapping[it]!! }
    val allColumns = columnNameMapping.values.toList()
    val cursorColumn = if (importType.cursor.isNotEmpty()) {
        columnNameMapping[importType.cursor.first()]!!
    } else {
        "_airbyte_extracted_at"
    }

    val columnList = allColumns.joinToString(", ") { "\"$it\"" }
    val updateAssignments = allColumns
        .filter { it !in pkColumns }  // Don't update PK columns
        .joinToString(", ") { "\"$it\" = EXCLUDED.\"$it\"" }

    // 1. Dedupe in temp table first
    val dedupSql = """
        CREATE TEMP TABLE deduped AS
        SELECT * FROM (
          SELECT *, ROW_NUMBER() OVER (
            PARTITION BY ${pkColumns.joinToString(", ") { "\"$it\"" }}
            ORDER BY "$cursorColumn" DESC, "_airbyte_extracted_at" DESC
          ) AS rn
          FROM ${fullyQualifiedName(source)}
        ) WHERE rn = 1
    """.trimIndent().andLog()

    // 2. Upsert with cursor check
    val upsertSql = """
        INSERT INTO ${fullyQualifiedName(target)} ($columnList)
        SELECT $columnList FROM deduped
        ON CONFLICT (${pkColumns.joinToString(", ") { "\"$it\"" }})
        DO UPDATE SET $updateAssignments
        WHERE ${fullyQualifiedName(target)}."$cursorColumn" < EXCLUDED."$cursorColumn"
           OR (${fullyQualifiedName(target)}."$cursorColumn" = EXCLUDED."$cursorColumn"
               AND ${fullyQualifiedName(target)}."_airbyte_extracted_at" < EXCLUDED."_airbyte_extracted_at")
    """.trimIndent().andLog()

    // 3. Cleanup
    val cleanupSql = "DROP TABLE deduped".andLog()

    return listOf(dedupSql, upsertSql, cleanupSql)
}
```

**Option C: Separate DELETE + INSERT (fallback)**

```kotlin
fun upsertTable(...): List<String> {
    val pkColumns = (stream.importType as Dedupe).primaryKey.map { columnNameMapping[it]!! }
    val allColumns = columnNameMapping.values.toList()

    // 1. Dedupe (same as above)
    val dedupSql = "..."

    // 2. Delete existing records with matching PKs
    val deleteSql = """
        DELETE FROM ${fullyQualifiedName(target)}
        WHERE (${pkColumns.joinToString(", ") { "\"$it\"" }})
        IN (SELECT ${pkColumns.joinToString(", ") { "\"$it\"" }} FROM deduped)
    """.trimIndent().andLog()

    // 3. Insert all from deduped
    val insertSql = """
        INSERT INTO ${fullyQualifiedName(target)}
        SELECT ${allColumns.joinToString(", ") { "\"$it\"" }} FROM deduped
    """.trimIndent().andLog()

    // 4. Cleanup
    val cleanupSql = "DROP TABLE deduped".andLog()

    return listOf(dedupSql, deleteSql, insertSql, cleanupSql)
}
```

### Advanced Step 2: Implement upsertTable() in Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun upsertTable(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    sourceTableName: TableName,
    targetTableName: TableName
) {
    val sql = sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)

    // Single statement (MERGE)
    if (sql is String) {
        execute(sql)
    } else {
        // Multiple statements (INSERT ON CONFLICT, DELETE+INSERT)
        sql.forEach { execute(it) }
    }
}
```

### Advanced Step 3: Update Writer for Dedupe Mode

**File:** Update `write/{DB}Writer.kt`

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    val initialStatus = if (::initialStatuses.isInitialized) {
        initialStatuses[stream] ?: DirectLoadInitialStatus(null, null)
    } else {
        DirectLoadInitialStatus(null, null)
    }

    val tableNameInfo = names[stream]
    val (realTableName, tempTableName, columnNameMapping) = if (tableNameInfo != null) {
        Triple(
            tableNameInfo.tableNames.finalTableName!!,
            tempTableNameGenerator.generate(tableNameInfo.tableNames.finalTableName!!),
            tableNameInfo.columnNameMapping
        )
    } else {
        val tableName = TableName(
            namespace = stream.mappedDescriptor.namespace ?: "test",
            name = stream.mappedDescriptor.name
        )
        Triple(tableName, tempTableNameGenerator.generate(tableName), ColumnNameMapping(emptyMap()))
    }

    // Choose StreamLoader based on sync mode and import type
    return when (stream.minimumGenerationId) {
        0L -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupStreamLoader(
                stream, initialStatus, realTableName, tempTableName,
                columnNameMapping, client, client, streamStateStore
            )
            else -> DirectLoadTableAppendStreamLoader(
                stream, initialStatus, realTableName, tempTableName,
                columnNameMapping, client, client, streamStateStore
            )
        }
        stream.generationId -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupTruncateStreamLoader(
                stream, initialStatus, realTableName, tempTableName,
                columnNameMapping, client, client, streamStateStore, tempTableNameGenerator
            )
            else -> DirectLoadTableAppendTruncateStreamLoader(
                stream, initialStatus, realTableName, tempTableName,
                columnNameMapping, client, client, streamStateStore
            )
        }
        else -> throw SystemErrorException("Hybrid refresh not supported")
    }
}
```

**What changed:**
- Added `when (stream.importType)` check inside generation ID check
- Four StreamLoader types now supported:
  - DirectLoadTableAppendStreamLoader (incremental append)
  - DirectLoadTableAppendTruncateStreamLoader (full refresh overwrite)
  - DirectLoadTableDedupStreamLoader (incremental dedupe)
  - DirectLoadTableDedupTruncateStreamLoader (full refresh dedupe)

### Advanced Step 4: Enable Tests

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `upsert tables`() {
    super.`upsert tables`()
}
```

### Advanced Step 5: Validate

**Validate:**
```bash
$ ./gradlew :destination-{db}:testComponentUpsertTables  # 1 test should pass
$ ./gradlew :destination-{db}:componentTest  # 13 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass
```

✅ **Checkpoint:** Dedupe mode works + all previous phases still work

---

---

## Advanced Phase 3: CDC Support (Optional)

**Goal:** Handle source deletions

**Checkpoint:** Can process CDC deletion events

**📋 CDC (Change Data Capture):**
- Tracks INSERT, UPDATE, DELETE operations from source
- Deletion marked with `_ab_cdc_deleted_at` timestamp
- Two modes:
  - **Hard delete**: Remove record from destination
  - **Soft delete**: Keep record with deletion timestamp

### Advanced Step 1: Add CDC Configuration

**File:** Update `spec/{DB}Specification.kt`

```kotlin
@get:JsonProperty("cdc_deletion_mode")
@get:JsonPropertyDescription(
    """Whether to execute CDC deletions as hard deletes (propagate source deletions)
    or soft deletes (leave tombstone record). Defaults to hard deletes."""
)
val cdcDeletionMode: CdcDeletionMode? = null

enum class CdcDeletionMode(@get:JsonValue val value: String) {
    @JsonProperty("hard_delete") HARD_DELETE("Hard delete"),
    @JsonProperty("soft_delete") SOFT_DELETE("Soft delete"),
}
```

**File:** Update `spec/{DB}Configuration.kt`

```kotlin
data class {DB}Configuration(
    // ... existing fields
    val cdcDeletionMode: CdcDeletionMode,
)

// In ConfigurationFactory
override fun makeWithoutExceptionHandling(pojo: {DB}Specification): {DB}Configuration {
    return {DB}Configuration(
        // ... existing fields
        cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
    )
}
```

### Advanced Step 2: Add CDC Logic to upsertTable()

**File:** Update `client/{DB}SqlGenerator.kt`

```kotlin
fun upsertTable(...): String {
    val importType = stream.importType as Dedupe
    val pkColumns = importType.primaryKey.map { columnNameMapping[it]!! }
    val allColumns = columnNameMapping.values.toList()

    val hasCdc = stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)
    val isHardDelete = config.cdcDeletionMode == CdcDeletionMode.HARD_DELETE

    val cursorColumn = if (importType.cursor.isNotEmpty()) {
        columnNameMapping[importType.cursor.first()]!!
    } else {
        "_airbyte_extracted_at"
    }

    // Deduplication CTE (same as before)
    val dedupCte = """..."""

    val pkMatch = """..."""
    val cursorComparison = """..."""

    // CDC DELETE clause (must come BEFORE UPDATE)
    val cdcDeleteClause = if (hasCdc && isHardDelete) {
        """
        WHEN MATCHED AND source."_ab_cdc_deleted_at" IS NOT NULL
             AND $cursorComparison THEN DELETE
        """
    } else {
        ""
    }

    // Skip INSERT for deleted records (hard delete mode)
    val cdcSkipInsertClause = if (hasCdc && isHardDelete) {
        "AND source.\"_ab_cdc_deleted_at\" IS NULL"
    } else {
        ""
    }

    val columnAssignments = allColumns.joinToString(",\n    ") { "\"$it\" = source.\"$it\"" }
    val columnList = allColumns.joinToString(", ") { "\"$it\"" }
    val sourceColumnList = allColumns.joinToString(", ") { "source.\"$it\"" }

    return """
        MERGE INTO ${fullyQualifiedName(target)} AS target
        USING (
          $dedupCte
        ) AS source
        ON $pkMatch
        $cdcDeleteClause
        WHEN MATCHED AND $cursorComparison THEN UPDATE SET $columnAssignments
        WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT ($columnList) VALUES ($sourceColumnList)
    """.trimIndent().andLog()
}

private val CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at"
```

**Key Points:**
- DELETE clause must come **before** UPDATE (SQL execution order)
- Must check cursor (only delete if deletion is newer than existing record)
- Skip INSERT for deleted records (don't re-insert deleted rows)
- Soft delete: No special clauses (just upsert the deletion record with timestamp)

### Advanced Step 3: Test CDC

CDC tests are typically included in integration tests automatically if you have CDC streams configured. No separate test enablement needed - the framework tests CDC if the stream has `_ab_cdc_deleted_at` column.

### Advanced Step 4: Validate

**Validate:**
```bash
$ ./gradlew :destination-{db}:componentTest  # 13 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass (CDC tested automatically if applicable)
```

✅ **Checkpoint:** Full CDC support + all previous phases still work

---

---

## Advanced Phase 4: Optimization & Polish

**Goal:** Production-ready performance


---

## Next Steps

**Next:** Your connector is now production-ready! Continue to [6-testing.md](./6-testing.md) to run BasicFunctionalityIntegrationTest and validate all features.
