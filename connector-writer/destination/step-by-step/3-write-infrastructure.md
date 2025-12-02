# Write Infrastructure: DI Setup and Test Contexts

**Prerequisites:** Complete [2-database-setup.md](./2-database-setup.md) - Your connector's `--check` operation must be working.

## What You'll Build

After completing this guide, you'll have:
- Name generators (table, column, temp)
- TableCatalog DI setup
- Write operation entry point
- Understanding of test contexts (CRITICAL!)

---

## Infrastructure Phase 1: Name Generators & TableCatalog DI

**Goal:** Create name generator beans required for TableCatalog instantiation

**Checkpoint:** Compilation succeeds without DI errors

**📋 Dependency Context:** TableCatalog (auto-instantiated by CDK) requires these three @Singleton beans:
- RawTableNameGenerator
- FinalTableNameGenerator
- ColumnNameGenerator

Without these beans, you'll get **"Error instantiating TableCatalog"** or **"No bean of type [FinalTableNameGenerator]"** errors in Phase 7 write tests.

### Infrastructure Step 1: Create RawTableNameGenerator

**File:** `config/{DB}NameGenerators.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}RawTableNameGenerator(
    private val config: {DB}Configuration,
) : RawTableNameGenerator {
    override fun getTableName(descriptor: DestinationStream.Descriptor): TableName {
        // Raw tables typically go to internal schema
        // Modern CDK uses final tables directly, so raw tables are rarely used
        val namespace = config.database  // Or config.internalSchema if you have one
        val name = "_airbyte_raw_${descriptor.namespace}_${descriptor.name}".toDbCompatible()
        return TableName(namespace, name)
    }
}
```

**Notes:**
- `@Singleton` annotation is **REQUIRED** - without it, Micronaut cannot inject this bean
- RawTableNameGenerator is legacy from two-stage sync (raw → final tables)
- Modern connectors typically use final tables only, but interface must be implemented
- Keep implementation simple (identity mapping is fine)

### Infrastructure Step 2: Create FinalTableNameGenerator

**Add to same file:** `config/{DB}NameGenerators.kt`

```kotlin
@Singleton
class {DB}FinalTableNameGenerator(
    private val config: {DB}Configuration,
) : FinalTableNameGenerator {
    override fun getTableName(descriptor: DestinationStream.Descriptor): TableName {
        val namespace = descriptor.namespace?.toDbCompatible()
            ?: config.database
        val name = descriptor.name.toDbCompatible()
        return TableName(namespace, name)
    }
}
```

**What this does:**
- Maps Airbyte stream descriptor → database table name
- Handles namespace mapping (if source has schemas/databases)
- Applies database-specific name transformation rules

**Example transforms:**
```kotlin
// Input: descriptor(namespace="public", name="users")
// Output: TableName("public", "users")

// Input: descriptor(namespace=null, name="customers")
// Output: TableName("my_database", "customers")  // Uses config.database as fallback
```

### Infrastructure Step 3: Create ColumnNameGenerator

**Add to same file:** `config/{DB}NameGenerators.kt`

```kotlin
@Singleton
class {DB}ColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        val dbName = column.toDbCompatible()
        return ColumnNameGenerator.ColumnName(
            canonicalName = dbName,
            displayName = dbName,
        )
    }
}
```

**What this does:**
- Maps Airbyte column names → database column names
- Applies database-specific transformations (case, special chars)

**Example transforms:**
```kotlin
// Snowflake: uppercase
"userId" → "USERID"

// Postgres/ClickHouse: lowercase
"userId" → "userid"

// MySQL: preserve case
"userId" → "userId"
```

### Infrastructure Step 4: Add Name Transformation Helper

**Add to same file:** `config/{DB}NameGenerators.kt`

```kotlin
// Helper function for database-specific name transformations
private fun String.toDbCompatible(): String {
    // Snowflake: uppercase
    return this.uppercase()

    // ClickHouse/Postgres: lowercase
    return this.lowercase()

    // MySQL: preserve case, but sanitize special chars
    return this.replace(Regex("[^a-zA-Z0-9_]"), "_")

    // Custom rules: Apply your database's naming conventions
    // - Max length limits
    // - Reserved word handling
    // - Character restrictions
}
```

**Database-specific examples:**

**Snowflake:**
```kotlin
private fun String.toDbCompatible() = this.uppercase()
```

**ClickHouse:**
```kotlin
private fun String.toDbCompatible() = this.lowercase()
```

**Postgres (strict):**
```kotlin
private fun String.toDbCompatible(): String {
    val sanitized = this
        .lowercase()
        .replace(Regex("[^a-z0-9_]"), "_")
        .take(63)  // Postgres identifier limit

    // Handle reserved words
    return if (sanitized in POSTGRES_RESERVED_WORDS) {
        "_$sanitized"
    } else {
        sanitized
    }
}

private val POSTGRES_RESERVED_WORDS = setOf("user", "table", "select", ...)
```

### Infrastructure Step 5: Register TempTableNameGenerator in BeanFactory

**File:** Update `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun tempTableNameGenerator(config: {DB}Configuration): TempTableNameGenerator {
    return DefaultTempTableNameGenerator(
        internalNamespace = config.database  // Or config.internalSchema if you have one
    )
}
```

**What this does:**
- Temp tables are used during overwrite/dedupe operations
- CDK provides `DefaultTempTableNameGenerator` implementation
- Just needs to know which namespace to use for temp tables

**Why register as bean?**
- TempTableNameGenerator is an interface, not a class
- CDK provides implementation, but YOU must register it
- Used by Writer to create staging tables

### Infrastructure Step 6: Verify Compilation

**Validate:**
```bash
$ ./gradlew :destination-{db}:compileKotlin  # BUILD SUCCESSFUL
$ ./gradlew :destination-{db}:componentTest  # 5 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # testSpecOss, testSuccessConfigs should pass
```

**If you see DI errors:**
- Check all three classes have `@Singleton` annotation
- Verify package name matches your connector structure
- Ensure classes implement correct interfaces:
  - `RawTableNameGenerator` (from `io.airbyte.cdk.load.orchestration.db`)
  - `FinalTableNameGenerator` (from `io.airbyte.cdk.load.orchestration.db`)
  - `ColumnNameGenerator` (from `io.airbyte.cdk.load.orchestration.db`)

✅ **Checkpoint:** Name generators registered + all previous phases still work

---

---

⚠️ **IMPORTANT: Before starting Phase 7, read [Understanding Test Contexts](./7-troubleshooting.md#understanding-test-contexts) in the troubleshooting guide. Phase 7 introduces integration tests which behave differently than the component tests you've been using.**

---

## Infrastructure Phase 2: Write Operation Infrastructure

**Goal:** Create write operation infrastructure beans (no business logic yet)

**Checkpoint:** Write operation initializes with real catalog (no DI errors)

**📋 Dependency Context:** This phase creates PURE INFRASTRUCTURE:
- WriteOperationV2 (enables --write command)
- DatabaseInitialStatusGatherer (checks existing tables before write)
- ColumnNameMapper (maps column names)

**NO business logic** (Writer/Aggregate/Buffer come in Phase 8)

**Key insight:** Separate infrastructure DI from business logic DI to catch errors incrementally.

### Infrastructure Step 1: Create WriteOperationV2

**File:** `cdk/WriteOperationV2.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.cdk

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Singleton

@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperationV2(
    private val d: DestinationLifecycle,
) : Operation {
    override fun execute() {
        d.run()
    }
}
```

⚠️ **REQUIRED:** This bean enables --write command

**What this does:**
- Declares a @Primary implementation of Operation for write mode
- Delegates to DestinationLifecycle (provided by CDK)
- DestinationLifecycle orchestrates the full write pipeline:
  - Setup (create namespaces, gather initial state)
  - Open (start data flow)
  - Process (accept records)
  - Close (flush buffers, finalize)

**Without this bean:**
```
IllegalStateException: A legal sync requires a declared @Singleton of a type that implements LoadStrategy
```

**Why @Primary?**
- CDK provides default implementations for spec/check operations
- WriteOperationV2 overrides default for write operation only
- @Primary tells Micronaut to prefer this bean over CDK defaults

**Why in `cdk/` package?**
- Pure framework integration (no database-specific code)
- Many connectors keep this file identical across databases
- Signals "this is infrastructure, not business logic"

### Infrastructure Step 2: Create DatabaseInitialStatusGatherer

**File:** `config/{DB}DirectLoadDatabaseInitialStatusGatherer.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.config

import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.orchestration.db.*
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}DirectLoadDatabaseInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    tempTableNameGenerator: TempTableNameGenerator,
) : BaseDirectLoadInitialStatusGatherer(
    tableOperationsClient,
    tempTableNameGenerator,
)
```

**What this does:**
- Extends CDK base class that checks which tables already exist
- Used by Writer.setup() to determine:
  - Does target table exist?
  - Does temp table exist (from previous failed sync)?
  - What generation ID is in the table?

**Base class provides:**
```kotlin
suspend fun gatherInitialStatus(catalog: TableCatalog): Map<DestinationStream, DirectLoadInitialStatus>
```

Returns status like:
```kotlin
DirectLoadInitialStatus(
    finalTableExists = true,
    tempTableExists = false,
    finalTableGenerationId = 42L,
)
```

⚠️ **MISSING IN V1 GUIDE:** This step existed as code but bean registration was missing!

### Infrastructure Step 3: Register DatabaseInitialStatusGatherer in BeanFactory

**File:** Update `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun initialStatusGatherer(
    client: TableOperationsClient,
    tempTableNameGenerator: TempTableNameGenerator,
): DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    return {DB}DirectLoadDatabaseInitialStatusGatherer(client, tempTableNameGenerator)
}
```

⚠️ **CRITICAL:** This bean registration was MISSING in V1 guide!

**Why this is needed:**
- Writer requires `DatabaseInitialStatusGatherer<DirectLoadInitialStatus>` injection
- Without this bean: `No bean of type [DatabaseInitialStatusGatherer] exists`
- Class exists but bean registration forgotten → DI error

**Why use factory method instead of class @Singleton?**
- DatabaseInitialStatusGatherer is generic: `DatabaseInitialStatusGatherer<DirectLoadInitialStatus>`
- Micronaut needs explicit return type for generic beans
- Factory method provides type safety

### Infrastructure Step 4: Create ColumnNameMapper

**File:** `write/transform/{DB}ColumnNameMapper.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.table.TableCatalog
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}ColumnNameMapper(
    private val names: TableCatalog,
) : ColumnNameMapper {
    override fun getMappedColumnName(
        stream: DestinationStream,
        columnName: String
    ): String? {
        return names[stream]?.columnNameMapping?.get(columnName)
    }
}
```

**What this does:**
- Used by record transformer to map Airbyte column names → database column names
- During transformation pipeline:
  ```kotlin
  // Input record: {"userId": 123, "email": "test@example.com"}
  // Snowflake output: {"USERID": 123, "EMAIL": "test@example.com"}
  // Postgres output: {"userid": 123, "email": "test@example.com"}
  ```

**How it works:**
- TableCatalog (provided by CDK) contains column name mappings
- Column names already generated by ColumnNameGenerator (Phase 6)
- ColumnNameMapper just looks up the mapping

**Why separate from ColumnNameGenerator?**
- ColumnNameGenerator: Creates mappings (Phase 6)
- ColumnNameMapper: Uses mappings during transform (Phase 7)
- Separation of concerns: generation vs. application

### Infrastructure Step 5: Register AggregatePublishingConfig in BeanFactory

**File:** Update `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun aggregatePublishingConfig(dataChannelMedium: DataChannelMedium): AggregatePublishingConfig {
    // Different settings for STDIO vs SOCKET mode
    return if (dataChannelMedium == DataChannelMedium.STDIO) {
        AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000_000L,
            maxEstBytesPerAgg = 350_000_000L,
            maxEstBytesAllAggregates = 350_000_000L * 5,
        )
    } else {
        // SOCKET mode (faster IPC)
        AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000_000L,
            maxEstBytesPerAgg = 350_000_000L,
            maxEstBytesAllAggregates = 350_000_000L * 5,
            maxBufferedAggregates = 6,
        )
    }
}
```

**What this configures:**
- `maxRecordsPerAgg`: Flush aggregate after this many records
- `maxEstBytesPerAgg`: Flush aggregate after this many bytes
- `maxEstBytesAllAggregates`: Total memory limit across all streams
- `maxBufferedAggregates`: Backpressure threshold (SOCKET mode only)

**Why this is required:**
- Controls memory usage and batching behavior
- CDK's data pipeline needs this configuration
- Without it: `No bean of type [AggregatePublishingConfig] exists`

**Default values:**
- Use Snowflake/ClickHouse values as template (shown above)
- Tune later based on performance requirements
- Start with defaults - they work for most databases

### Infrastructure Step 6: Create WriteInitializationTest

**File:** `src/test-integration/kotlin/.../write/{DB}WriteInitTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write

import io.airbyte.cdk.load.write.WriteInitializationTest
import io.airbyte.integrations.destination.{db}.spec.{DB}Specification
import java.nio.file.Path

/**
 * Validates write operation can initialize with real catalog.
 * Catches missing beans that ConnectorWiringSuite (with mock catalog) doesn't test.
 *
 * This test spawns a real write process (same as Docker) and validates:
 * - TableCatalog can be instantiated (requires name generators from Phase 6)
 * - Write operation can be created (requires WriteOperationV2 from Phase 7.1)
 * - All write infrastructure beans exist (DatabaseInitialStatusGatherer, ColumnNameMapper, etc.)
 *
 * Does NOT validate data writing - that's Phase 8 (ConnectorWiringSuite)
 */
class {DB}WriteInitTest : WriteInitializationTest<{DB}Specification>(
    configContents = Path.of("secrets/config.json").toFile().readText(),
    configSpecClass = {DB}Specification::class.java,
)
```

**That's it!** Just 10 lines - extend `WriteInitializationTest` and provide your config.

**What WriteInitializationTest provides (from CDK):**
- ✅ Test method: `writer can be instantiated with real catalog`
- ✅ Minimal catalog (one stream) - hardcoded in base class
- ✅ Spawns real write process (same as Docker)
- ✅ Validates DI initialization only (no data writing)
- ✅ Clear error messages pointing to missing beans

**Why this test matters:**
- **ConnectorWiringSuite** (Phase 8) uses MockDestinationCatalog → doesn't test TableCatalog DI
- **WriteInitializationTest** uses REAL catalog parsing → catches TableCatalog DI errors
- **Catches:** Missing name generators, missing WriteOperationV2, missing beans

**Test progression:**
```
Phase 6: Name generators exist
Phase 7: WriteInitTest validates they work with real catalog
Phase 8: ConnectorWiringSuite validates full write path with mock catalog
```

### Infrastructure Step 7: Create Test Config File

**File:** `secrets/config.json`

```bash
$ mkdir -p destination-{db}/secrets
```

**File:** `destination-{db}/secrets/config.json`

```json
{
  "hostname": "localhost",
  "port": 5432,
  "database": "test",
  "username": "test",
  "password": "test"
}
```

**For CI/local with Testcontainers:**
- WriteInitTest doesn't use Testcontainers (integration test, not component test)
- Provide real database credentials or use local database
- Alternatively: Update test to read from environment variables

**Note:** Add `secrets/` to `.gitignore` to avoid committing credentials

### Infrastructure Step 8: Validate WriteInitializationTest

**Validate:**
```bash
$ ./gradlew :destination-{db}:integrationTestWriterCanBeInstantiatedWithRealCatalog  # 1 test should pass
$ ./gradlew :destination-{db}:componentTest  # 5 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass
```

**If this FAILS with DI errors:**

**"Error instantiating TableCatalog"** or **"No bean of type [FinalTableNameGenerator]"**
→ Missing name generator from Phase 6
→ Check @Singleton annotation on all three generators

**"No bean of type [DatabaseInitialStatusGatherer]"**
→ Missing bean registration in BeanFactory (Step 7.3)
→ Add `initialStatusGatherer()` factory method

**"IllegalStateException: No LoadStrategy"** or **"A legal sync requires a declared @Singleton"**
→ Missing WriteOperationV2 (Step 7.1)
→ Create `cdk/WriteOperationV2.kt` with @Primary @Singleton

**"Failed to inject ColumnNameMapper"**
→ Missing @Singleton annotation on ColumnNameMapper
→ Check `write/transform/{DB}ColumnNameMapper.kt`

✅ **Checkpoint:** Write operation infrastructure exists + all previous phases still work

---

---


## Troubleshooting Reference

**If you encounter errors during Phases 6-7, refer to:**

### Understanding Test Contexts

Phase 7 introduces **integration tests** which behave differently than component tests:

- **Component tests** (Phases 2-5): Use MockDestinationCatalog, bypass name generators
- **Integration tests** (Phase 7+): Use real catalog parsing, require name generators

**Why this matters:**
- Component tests passing ≠ integration tests passing
- Integration tests catch missing name generators, bean registrations, and DI issues
- Docker runtime uses same context as integration tests

📖 **Full explanation:** [Understanding Test Contexts](./7-troubleshooting.md#understanding-test-contexts)

---

### Common DI Errors in Phase 7

**Quick fixes for the most common errors:**

| Error | Likely Cause | Fix Guide |
|-------|--------------|-----------|
| "No bean of type [FinalTableNameGenerator]" | Missing name generator classes | Phase 6, Step 6.1-6.3 |
| "No bean of type [DatabaseInitialStatusGatherer]" | Missing bean registration | Phase 7, Step 7.3 |
| "A legal sync requires a declared @Singleton" | Missing WriteOperationV2 | Phase 7, Step 7.1 |
| "Failed to inject value for parameter [dataChannelMedium]" | Missing application-connector.yml | Phase 0, Step 0.8 |

📖 **Detailed troubleshooting:** [Common DI Errors & Fixes](./7-troubleshooting.md#common-di-errors--fixes)


**Next:** Continue to [4-write-operations.md](./4-write-operations.md) to implement the core write business logic.
