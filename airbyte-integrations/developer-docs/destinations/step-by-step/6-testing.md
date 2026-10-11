# BasicFunctionalityIntegrationTest Implementation Guide

**Summary:** Comprehensive guide for implementing the full CDK integration test suite. This test validates edge cases, type handling, schema evolution, and CDC support. Required for production certification.

**When to use this:** After Phase 8 (working connector with ConnectorWiringSuite passing)

**Time estimate:** 4-8 hours for complete implementation

---

## What BasicFunctionalityIntegrationTest Validates

**Comprehensive test coverage (50+ scenarios):**

### Data Type Handling
- All Airbyte types (string, integer, number, boolean, date, time, timestamp)
- Nested objects and arrays
- Union types (multiple possible types for one field)
- Unknown types (unrecognized JSON schema types)
- Null values vs unset fields
- Large integers/decimals (precision handling)

### Sync Modes
- `testAppend()` - Incremental append without deduplication
- `testDedupe()` - Incremental append with primary key deduplication
- `testTruncate()` - Full refresh (replace all data)
- `testAppendSchemaEvolution()` - Schema changes during append

### Schema Evolution
- Add column
- Drop column
- Change column type (widening)
- Nullable to non-nullable changes

### CDC Support (if enabled)
- Hard delete (actually remove records)
- Soft delete (tombstone records)
- Delete non-existent records
- Insert + delete in same sync

### Edge Cases
- Empty syncs
- Very large datasets
- Concurrent streams
- State checkpointing
- Error recovery

---

## Prerequisites

Before starting, you must have:
- ✅ Phase 8 complete (ConnectorWiringSuite passing)
- ✅ Phase 13 complete (if testing dedupe mode)
- ✅ Working database connection (Testcontainers or real DB)
- ✅ All sync modes implemented

---

## Testing Phase 1: BasicFunctionalityIntegrationTest

### Testing Step 1: Implement Test Helper Classes

### Step 1.1: Create DestinationDataDumper

**Purpose:** Read data from database for test verification

**File:** `src/test-integration/kotlin/.../{DB}DataDumper.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.destination.DestinationDataDumper
import javax.sql.DataSource

class {DB}DataDumper(
    private val dataSource: DataSource,
) : DestinationDataDumper {

    override fun dumpRecords(stream: DestinationStream): List<OutputRecord> {
        val tableName = stream.descriptor.name  // Or use name generator
        val namespace = stream.descriptor.namespace ?: "test"

        val records = mutableListOf<OutputRecord>()

        dataSource.connection.use { connection ->
            val sql = "SELECT * FROM \"$namespace\".\"$tableName\""
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)
                val metadata = rs.metaData

                while (rs.next()) {
                    val data = mutableMapOf<String, AirbyteValue>()

                    for (i in 1..metadata.columnCount) {
                        val columnName = metadata.getColumnName(i)
                        val value = rs.getObject(i)

                        // Convert database value to AirbyteValue
                        data[columnName] = when {
                            value == null -> NullValue
                            value is String -> StringValue(value)
                            value is Int -> IntegerValue(value.toLong())
                            value is Long -> IntegerValue(value)
                            value is Boolean -> BooleanValue(value)
                            value is java.math.BigDecimal -> NumberValue(value)
                            value is java.sql.Timestamp -> TimestampWithTimezoneValue(value.toInstant().toString())
                            value is java.sql.Date -> DateValue(value.toLocalDate().toString())
                            // Add more type conversions as needed
                            else -> StringValue(value.toString())
                        }
                    }

                    // Extract Airbyte metadata columns
                    val extractedAt = (data["_airbyte_extracted_at"] as? TimestampWithTimezoneValue)?.value?.toLong() ?: 0L
                    val generationId = (data["_airbyte_generation_id"] as? IntegerValue)?.value?.toLong() ?: 0L
                    val meta = data["_airbyte_meta"]  // ObjectValue with errors/changes

                    records.add(
                        OutputRecord(
                            extractedAt = extractedAt,
                            generationId = generationId,
                            data = data.filterKeys { !it.startsWith("_airbyte") },
                            airbyteMeta = parseAirbyteMeta(meta)
                        )
                    )
                }
            }
        }

        return records
    }

    private fun parseAirbyteMeta(meta: AirbyteValue?): OutputRecord.Meta {
        // Parse _airbyte_meta JSON to OutputRecord.Meta
        // For now, simple implementation:
        return OutputRecord.Meta(syncId = 0)
    }
}
```

**What this does:**
- Queries database table for a stream
- Converts database types back to AirbyteValue
- Extracts Airbyte metadata columns
- Returns OutputRecord list for test assertions

### Step 1.2: Create DestinationCleaner

**Purpose:** Clean up test data between test runs

**File:** `src/test-integration/kotlin/.../{DB}Cleaner.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.load.test.util.destination.DestinationCleaner
import javax.sql.DataSource

class {DB}Cleaner(
    private val dataSource: DataSource,
    private val testNamespace: String = "test",
) : DestinationCleaner {

    override fun cleanup() {
        dataSource.connection.use { connection ->
            // Drop all test tables
            val sql = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = '$testNamespace'
            """

            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)
                val tablesToDrop = mutableListOf<String>()

                while (rs.next()) {
                    tablesToDrop.add(rs.getString("table_name"))
                }

                // Drop each table
                tablesToDrop.forEach { tableName ->
                    try {
                        statement.execute("DROP TABLE IF EXISTS \"$testNamespace\".\"$tableName\" CASCADE")
                    } catch (e: Exception) {
                        // Ignore errors during cleanup
                    }
                }
            }

            // Optionally drop test namespace
            try {
                connection.createStatement().use {
                    it.execute("DROP SCHEMA IF EXISTS \"$testNamespace\" CASCADE")
                }
            } catch (e: Exception) {
                // Ignore
            }
        }
    }
}
```

**What this does:**
- Finds all tables in test namespace
- Drops them to clean up between tests
- Runs once per test suite (not per test)

---

### Testing Step 2: Create BasicFunctionalityIntegrationTest Class

### Step 2.1: Understand Required Parameters

BasicFunctionalityIntegrationTest has **14 required constructor parameters** (15 for dataflow CDK):

| Parameter | Type | Purpose | Common Value |
|-----------|------|---------|--------------|
| `configContents` | String | Database config JSON | Load from secrets/config.json |
| `configSpecClass` | Class<T> | Specification class | `{DB}Specification::class.java` |
| `dataDumper` | DestinationDataDumper | Read data for verification | `{DB}DataDumper(dataSource)` |
| `destinationCleaner` | DestinationCleaner | Clean between tests | `{DB}Cleaner(dataSource)` |
| `isStreamSchemaRetroactive` | Boolean | Schema changes apply retroactively | `true` (usually) |
| `dedupBehavior` | DedupBehavior? | CDC deletion mode | `DedupBehavior(CdcDeletionMode.HARD_DELETE)` |
| `stringifySchemalessObjects` | Boolean | Convert objects without schema to strings | `false` |
| `schematizedObjectBehavior` | SchematizedNestedValueBehavior | How to handle nested objects | `PASS_THROUGH` or `STRINGIFY` |
| `schematizedArrayBehavior` | SchematizedNestedValueBehavior | How to handle nested arrays | `STRINGIFY` (usually) |
| `unionBehavior` | UnionBehavior | How to handle union types | `STRINGIFY` or `PROMOTE_TO_OBJECT` |
| `supportFileTransfer` | Boolean | Supports file uploads | `false` (for databases) |
| `commitDataIncrementally` | Boolean | Commit during sync vs at end | `true` |
| `allTypesBehavior` | AllTypesBehavior | Type handling configuration | `StronglyTyped(...)` |
| `unknownTypesBehavior` | UnknownTypesBehavior | Unknown type handling | `PASS_THROUGH` |
| `nullEqualsUnset` | Boolean | Null same as missing field | `true` |
| **`useDataFlowPipeline`** | **Boolean** | **Use dataflow CDK architecture** | **`true`** ⭐ **REQUIRED for dataflow CDK** |

### Step 2.2: Create Test Class

**File:** `src/test-integration/kotlin/.../{DB}BasicFunctionalityTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.load.test.util.destination.DestinationCleaner
import io.airbyte.cdk.load.test.util.destination.DestinationDataDumper
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.{db}.spec.{DB}Specification
import java.nio.file.Path
import javax.sql.DataSource
import org.junit.jupiter.api.BeforeAll

class {DB}BasicFunctionalityTest : BasicFunctionalityIntegrationTest(
    configContents = Path.of("secrets/config.json").toFile().readText(),
    configSpecClass = {DB}Specification::class.java,
    dataDumper = createDataDumper(),
    destinationCleaner = createCleaner(),

    // Schema behavior
    isStreamSchemaRetroactive = true,

    // CDC deletion mode
    dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),

    // Type handling
    stringifySchemalessObjects = false,
    schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
    unionBehavior = UnionBehavior.STRINGIFY,

    // Feature support
    supportFileTransfer = false,  // Database destinations don't transfer files
    commitDataIncrementally = true,

    // Type system behavior
    allTypesBehavior = AllTypesBehavior.StronglyTyped(
        integerCanBeLarge = false,  // true if your DB has unlimited integers
        numberCanBeLarge = false,   // true if your DB has unlimited precision
        nestedFloatLosesPrecision = false,
    ),
    unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    nullEqualsUnset = true,

    // Dataflow CDK architecture (REQUIRED for new CDK)
    useDataFlowPipeline = true,  // ⚠️ Must be true for dataflow CDK connectors
) {
    companion object {
        private lateinit var testDataSource: DataSource

        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            // Set up test database (Testcontainers or real DB)
            testDataSource = createTestDataSource()
        }

        private fun createDataDumper(): DestinationDataDumper {
            return {DB}DataDumper(testDataSource)
        }

        private fun createCleaner(): DestinationCleaner {
            return {DB}Cleaner(testDataSource)
        }

        private fun createTestDataSource(): DataSource {
            // Initialize Testcontainers or connection pool
            val container = {DB}Container("{db}:latest")
            container.start()

            return HikariDataSource().apply {
                jdbcUrl = container.jdbcUrl
                username = container.username
                password = container.password
            }
        }
    }

    // Test methods - uncomment as you implement features

    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Test
    override fun testTruncate() {
        super.testTruncate()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Test
    override fun testDedupe() {
        super.testDedupe()
    }
}
```

---

### Testing Step 3: Configure Test Parameters

### Quick Reference Table

| Parameter | Typical Value | Purpose |
|-----------|---------------|---------|
| configContents | `Path.of("secrets/config.json").toFile().readText()` | DB connection config |
| configSpecClass | `{DB}Specification::class.java` | Your spec class |
| dataDumper | `{DB}DataDumper(testDataSource)` | Read test data (from Step 1) |
| destinationCleaner | `{DB}Cleaner(testDataSource)` | Cleanup test data (from Step 1) |
| isStreamSchemaRetroactive | `true` | Schema changes apply to existing data |
| supportFileTransfer | `false` | Database destinations don't support files |
| commitDataIncrementally | `true` | Commit batches as written |
| nullEqualsUnset | `true` | Treat `{"x": null}` same as `{}` |
| stringifySchemalessObjects | `false` | Use native JSON if available |
| unknownTypesBehavior | `PASS_THROUGH` | Store unrecognized types as-is |
| unionBehavior | `STRINGIFY` | Convert union types to JSON string |
| schematizedObjectBehavior | `PASS_THROUGH` or `STRINGIFY` | See below |
| schematizedArrayBehavior | `STRINGIFY` | See below |

### Complex Parameters (Database-Specific)

#### dedupBehavior

**Purpose:** How to handle CDC deletions

**Options:**
```kotlin
// Hard delete - remove CDC-deleted records
DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE)

// Soft delete - keep tombstone records
DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE)

// No CDC support yet
null
```

#### allTypesBehavior

**Purpose:** Configure type precision limits

```kotlin
// Snowflake/BigQuery: Unlimited precision
AllTypesBehavior.StronglyTyped(
    integerCanBeLarge = true,
    numberCanBeLarge = true,
    nestedFloatLosesPrecision = false,
)

// MySQL/Postgres: Limited precision
AllTypesBehavior.StronglyTyped(
    integerCanBeLarge = false,  // BIGINT limits
    numberCanBeLarge = false,   // DECIMAL limits
    nestedFloatLosesPrecision = false,
)
```

#### schematizedObjectBehavior / schematizedArrayBehavior

**Purpose:** How to store nested objects and arrays

**Options:**
- `PASS_THROUGH`: Use native JSON/array types (Postgres JSONB, Snowflake VARIANT)
- `STRINGIFY`: Convert to JSON strings (fallback for databases without native types)

**Recommendations:**
- **Objects:** `PASS_THROUGH` if DB has native JSON, else `STRINGIFY`
- **Arrays:** `STRINGIFY` (most DBs don't have typed arrays, except Postgres)

#### useDataFlowPipeline ⚠️

**Value:** `true` - **REQUIRED for dataflow CDK connectors**

**Why critical:** Setting to `false` uses old CDK code paths that don't work with Aggregate/InsertBuffer pattern. Always use `true`.

---

## ⚠️ CRITICAL: All Tests Must Pass - No Exceptions

**NEVER rationalize test failures as:**
- ❌ "Cosmetic, not functional"
- ❌ "The connector IS working, tests just need adjustment"
- ❌ "Just test framework expectations vs database behavior"
- ❌ "State message comparison issues, not real problems"
- ❌ "Need database-specific adaptations (but haven't made them)"

**Test failures mean ONE of two things:**

### 1. Your Implementation is Wrong (90% of cases)
- State message format doesn't match expected
- Schema evolution doesn't work correctly
- Deduplication logic has bugs
- Type handling is incorrect

**Fix:** Debug and fix your implementation

### 2. Test Expectations Need Tuning (10% of cases)
- Database truly handles something differently (e.g., ClickHouse soft delete only)
- Type precision genuinely differs
- **BUT:** You must document WHY and get agreement this is acceptable

**Fix:** Update test parameters with clear rationale

**Key principle:** If tests fail, the connector is NOT working correctly for production use.

**Example rationalizations to REJECT:**

❌ "Many tests failing due to state message comparison - cosmetic"
→ State messages are HOW Airbyte tracks progress. Wrong state = broken checkpointing!

❌ "Schema evolution needs MongoDB-specific expectations"
→ Implement schema evolution correctly for MongoDB, then tests pass!

❌ "Dedupe tests need configuration"
→ Add the configuration! Don't skip tests!

❌ "Some tests need adaptations"
→ Make the adaptations! Document what's different and why!

**ALL tests must pass or be explicitly skipped with documented rationale approved by maintainers.**

### Common Rationalizations That Are WRONG

**Agent says:** "The 7 failures are specific edge cases - advanced scenarios, not core functionality"

**Reality:**
- Truncate/overwrite mode = **CORE SYNC MODE** used by thousands of syncs
- Generation ID tracking = **REQUIRED for refresh** to work correctly
- "Edge cases" = real user scenarios that WILL happen in production
- "Advanced scenarios" = standard Airbyte features your connector claims to support

**If you don't support a mode:**
- Don't claim to support it (remove from SpecificationExtension)
- Explicitly skip those tests with @Disabled annotation
- Document the limitation clearly

**If you claim to support it (in SpecificationExtension):**
- Tests MUST pass
- No "works for normal cases" excuses
- Users will try to use it and it will break

**Agent says:** "The connector works for normal use cases"

**Reality:**
- Tests define "working"
- "Normal use cases" is undefined - what's normal?
- Users will hit "edge cases" in production
- Failed tests = broken functionality that will cause support tickets

**The rule:** If supportedSyncModes includes OVERWRITE, then testTruncate() must pass.

---

### Specific Scenarios That Are NOT Optional

**Truncate/Overwrite Mode:**
- Used by: Full refresh syncs (very common!)
- Tests: testTruncate()
- **NOT optional** if you declared `DestinationSyncMode.OVERWRITE` in SpecificationExtension

**Generation ID Tracking:**
- Used by: All refresh operations
- Tests: Generation ID assertions in all tests
- **NOT optional** - required for sync modes to work correctly

**State Messages:**
- Used by: Checkpointing and resume
- Tests: State message format validation
- **NOT optional** - wrong state = broken incremental syncs

**Schema Evolution:**
- Used by: When source schema changes
- Tests: testAppendSchemaEvolution()
- **NOT optional** - users will add/remove columns

**Deduplication:**
- Used by: APPEND_DEDUP mode
- Tests: testDedupe()
- **NOT optional** if you declared `DestinationSyncMode.APPEND_DEDUP`

**None of these are "edge cases" - they're core Airbyte features!**

---

### Testing Step 4: Run Tests

### Test Individually

```bash
# Test append mode
$ ./gradlew :destination-{db}:integrationTest --tests "*BasicFunctionalityTest.testAppend"

# Test dedupe mode
$ ./gradlew :destination-{db}:integrationTest --tests "*BasicFunctionalityTest.testDedupe"

# Test schema evolution
$ ./gradlew :destination-{db}:integrationTest --tests "*BasicFunctionalityTest.testAppendSchemaEvolution"
```

### Run Full Suite

```bash
$ ./gradlew :destination-{db}:integrationTest --tests "*BasicFunctionalityTest"
```

**Expected:** All enabled tests pass

**Time:** 5-15 minutes (depending on database and data volume)

---

### Testing Step 5: Debug Common Failures

### Test: testAppend fails with "Record mismatch"

**Cause:** DataDumper not converting types correctly

**Fix:** Check type conversion in DataDumper:
- Timestamps: Ensure timezone handling matches
- Numbers: Check BigDecimal vs Double conversion
- Booleans: Check 1/0 vs true/false

### Test: testDedupe fails with "Expected 1 record, got 2"

**Cause:** Deduplication not working

**Fix:** Check upsertTable() implementation:
- MERGE statement correct?
- Primary key comparison working?
- Cursor field comparison correct?

### Test: testAppendSchemaEvolution fails with "Column not found"

**Cause:** Schema evolution (ALTER TABLE) not working

**Fix:** Check applyChangeset() implementation:
- ADD COLUMN syntax correct?
- DROP COLUMN supported?
- Type changes handled?

### Test: Data type tests fail

**Cause:** Type mapping issues

**Fix:** Check ColumnUtils.toDialectType():
- All Airbyte types mapped?
- Nullable handling correct?
- Precision/scale for decimals?

---

### Testing Step 6: Optional Test Customization

### Skip Tests Not Applicable

```kotlin
// If your DB doesn't support certain features:

// @Test
// override fun testDedupe() {
//     // Skip if no MERGE/UPSERT support yet
// }
```

### Add Database-Specific Tests

```kotlin
@Test
fun testDatabaseSpecificFeature() {
    // Your custom test
}
```

---

## Reference Implementations

### Snowflake
**File:** `destination-snowflake/src/test-integration/.../SnowflakeBasicFunctionalityTest.kt`

**Parameters:**
- `unionBehavior = UnionBehavior.PROMOTE_TO_OBJECT` (uses VARIANT type)
- `schematizedObjectBehavior = PASS_THROUGH` (native OBJECT type)
- `allTypesBehavior.integerCanBeLarge = true` (NUMBER unlimited)

### ClickHouse
**File:** `destination-clickhouse/src/test-integration/.../ClickhouseBasicFunctionalityTest.kt`

**Parameters:**
- `dedupBehavior = SOFT_DELETE` (ReplacingMergeTree doesn't support DELETE in MERGE)
- `schematizedArrayBehavior = STRINGIFY` (no native typed arrays)
- `allTypesBehavior.integerCanBeLarge = false` (Int64 has limits)

### MySQL
**File:** `destination-mysql/src/test-integration/.../MySQLBasicFunctionalityTest.kt`

**Parameters:**
- `unionBehavior = STRINGIFY`
- `schematizedObjectBehavior = STRINGIFY` (JSON type but limited)
- `commitDataIncrementally = true`

---

## Troubleshooting

### "No bean of type [DestinationDataDumper]"

**Cause:** DataDumper not created in companion object

**Fix:** Verify `createDataDumper()` returns {DB}DataDumper instance

### "Test hangs indefinitely"

**Cause:** Database not responding or deadlock

**Fix:**
- Check database is running (Testcontainers started?)
- Check for locks (previous test didn't cleanup?)
- Add timeout: `@Timeout(5, unit = TimeUnit.MINUTES)`

### "All tests fail with same error"

**Cause:** Setup/cleanup issue

**Fix:** Check DestinationCleaner.cleanup() actually drops tables

### "Data type test fails for one specific type"

**Cause:** Type conversion in DataDumper is wrong

**Fix:** Add logging to see what database returns:
```kotlin
val value = rs.getObject(i)
println("Column $columnName: value=$value, type=${value?.javaClass}")
```

---

## Success Criteria

BasicFunctionalityIntegrationTest is complete when:

**Minimum (Phase 8):**
- ✅ testAppend passes

**Full Feature Set (Phase 13):**
- ✅ testAppend passes
- ✅ testTruncate passes
- ✅ testAppendSchemaEvolution passes
- ✅ testDedupe passes

**Production Ready (Phase 15):**
- ✅ All tests pass
- ✅ All type tests pass
- ✅ CDC tests pass (if supported)
- ✅ No flaky tests
- ✅ Tests run in <15 minutes

---

## Time Estimates

| Task | Time |
|------|------|
| Implement DataDumper | 1-2 hours |
| Implement Cleaner | 30 min |
| Create test class with parameters | 30 min |
| Debug testAppend | 1-2 hours |
| Debug other tests | 2-4 hours |
| **Total** | **5-9 hours** |

**Tip:** Implement tests incrementally:
1. testAppend first (simplest)
2. testTruncate next
3. testAppendSchemaEvolution
4. testDedupe last (most complex)

---

## Summary

BasicFunctionalityIntegrationTest is the **gold standard** for connector validation but has significant complexity:

**Pros:**
- Comprehensive coverage (50+ scenarios)
- Validates edge cases
- Required for production certification
- Catches type handling bugs

**Cons:**
- 13 required parameters
- 5-9 hours to implement and debug
- Complex failure modes
- Slow test execution

**Strategy:**
- Phase 8: Get working connector with ConnectorWiringSuite (fast)
- Phase 15: Add BasicFunctionalityIntegrationTest (comprehensive)
- Balance: Quick iteration early, thorough validation later

The v2 guide gets you to working connector without this complexity, but this guide ensures production readiness!
