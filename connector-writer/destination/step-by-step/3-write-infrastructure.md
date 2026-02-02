# Write Infrastructure: DI Setup and Test Contexts

**Prerequisites:** Complete [2-database-setup.md](./2-database-setup.md) - Your connector's `--check` operation must be working.

## What You'll Build

After completing this guide, you'll have:
- TableSchemaMapper (unified schema transformation)
- Name generators (table, column, temp)
- TableCatalog DI setup
- Write operation entry point
- Understanding of test contexts (CRITICAL!)

---

## Infrastructure Phase 1: TableSchemaMapper

**Goal:** Define how Airbyte schemas transform to your database's conventions

**Checkpoint:** TableSchemaMapper implemented (validated later via TableSchemaEvolutionSuite)

**📋 What TableSchemaMapper Does:**

TableSchemaMapper defines schema transformations:
- **Table names:** Stream descriptor → database table name
- **Column names:** Airbyte column → database column (case, special chars)
- **Column types:** Airbyte types → database types (INTEGER → BIGINT, etc.)
- **Temp tables:** Generate staging table names

This interface is used by:
- `TableNameResolver` / `ColumnNameResolver` (CDK collision handling)
- `TableSchemaEvolutionClient` (schema evolution in Phase 5)

### Infrastructure Step 1: Create TableSchemaMapper

**File:** `schema/{DB}TableSchemaMapper.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.{db}.config.toDbCompatibleName
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import jakarta.inject.Singleton

@Singleton
class {DB}TableSchemaMapper(
    private val config: {DB}Configuration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = (desc.namespace ?: config.database).toDbCompatibleName()
        val name = desc.name.toDbCompatibleName()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return name.toDbCompatibleName()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val dbType = when (fieldType.type) {
            BooleanType -> {DB}SqlTypes.BOOLEAN
            DateType -> {DB}SqlTypes.DATE
            IntegerType -> {DB}SqlTypes.BIGINT
            NumberType -> {DB}SqlTypes.DECIMAL
            StringType -> {DB}SqlTypes.VARCHAR
            TimeTypeWithTimezone,
            TimeTypeWithoutTimezone -> {DB}SqlTypes.TIME
            TimestampTypeWithTimezone,
            TimestampTypeWithoutTimezone -> {DB}SqlTypes.TIMESTAMP
            is ArrayType,
            ArrayTypeWithoutSchema,
            is UnionType,
            is UnknownType -> {DB}SqlTypes.JSON
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is ObjectType -> {DB}SqlTypes.JSON
        }
        return ColumnType(dbType, fieldType.nullable)
    }
}
```

**Database-specific type mappings:**

| Airbyte Type | Postgres | MySQL | Snowflake | ClickHouse |
|--------------|----------|-------|-----------|------------|
| BooleanType | BOOLEAN | TINYINT(1) | BOOLEAN | Bool |
| IntegerType | BIGINT | BIGINT | NUMBER(38,0) | Int64 |
| NumberType | DECIMAL(38,9) | DECIMAL(38,9) | FLOAT | Decimal(38,9) |
| StringType | VARCHAR | VARCHAR(65535) | VARCHAR | String |
| TimestampTypeWithTimezone | TIMESTAMPTZ | TIMESTAMP | TIMESTAMP_TZ | DateTime64(3) |
| ObjectType | JSONB | JSON | VARIANT | String/JSON |

**Optional: Override toFinalSchema() for Dedupe Mode**

Some databases need to adjust column nullability for dedupe mode (e.g., ClickHouse's ReplacingMergeTree requires non-null PK/cursor columns):

```kotlin
override fun toFinalSchema(tableSchema: StreamTableSchema): StreamTableSchema {
    if (tableSchema.importType !is Dedupe) {
        return tableSchema  // No changes for append/overwrite
    }

    // Make PK and cursor columns non-nullable for dedupe
    val pks = tableSchema.getPrimaryKey().flatten()
    val cursor = tableSchema.getCursor().firstOrNull()
    val nonNullCols = buildSet {
        addAll(pks)
        cursor?.let { add(it) }
    }

    val finalSchema = tableSchema.columnSchema.finalSchema
        .mapValues { (name, type) ->
            if (name in nonNullCols) type.copy(nullable = false) else type
        }

    return tableSchema.copy(
        columnSchema = tableSchema.columnSchema.copy(finalSchema = finalSchema)
    )
}
```

Most databases don't need this override - the default implementation returns the schema unchanged.

### Infrastructure Step 2: Validate Compilation

```bash
$ ./gradlew :destination-{db}:compileKotlin
```

Expected: BUILD SUCCESSFUL (may have unresolved reference to `toDbCompatibleName` until Phase 2)

**Note:** TableSchemaMapper is validated via `TableSchemaEvolutionSuite` in [5-advanced-features.md](./5-advanced-features.md). No separate tests needed now.

✅ **Checkpoint:** TableSchemaMapper implemented

---

## Infrastructure Phase 2: Name Generators & TableCatalog DI

**Goal:** Create name generator beans required for TableCatalog instantiation

**Checkpoint:** Compilation succeeds without DI errors

**📋 Dependency Context:** TableCatalog (auto-instantiated by CDK) requires these @Singleton beans:
- FinalTableNameGenerator
- ColumnNameGenerator
- TempTableNameGenerator

Without these beans, you'll get **"Error instantiating TableCatalog"** or **"No bean of type [FinalTableNameGenerator]"** errors in write tests.

### Infrastructure Step 1: Create Name Generators

**Add to file:** `config/{DB}NameGenerators.kt` (same file as the helper function)

```kotlin
package io.airbyte.integrations.destination.{db}.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameGenerator
import io.airbyte.cdk.load.table.FinalTableNameGenerator
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import jakarta.inject.Singleton
import java.util.Locale
import java.util.UUID

@Singleton
class {DB}FinalTableNameGenerator(
    private val config: {DB}Configuration,
) : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val namespace = (streamDescriptor.namespace ?: config.database).toDbCompatibleName()
        val name = streamDescriptor.name.toDbCompatibleName()
        return TableName(namespace, name)
    }
}

@Singleton
class {DB}ColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toDbCompatibleName(),
            column.lowercase(Locale.getDefault()).toDbCompatibleName(),
        )
    }
}

/**
 * Transforms a string to be compatible with {DB} table and column names.
 */
fun String.toDbCompatibleName(): String {
    // 1. Replace non-alphanumeric characters with underscore
    var transformed = toAlphanumericAndUnderscore(this)

    // 2. Ensure identifier does not start with a digit
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // 3. Handle empty strings
    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}"
    }

    return transformed
}
```

**Notes:**
- `@Singleton` annotation is **REQUIRED** - without it, Micronaut cannot inject these beans
- `canonicalName` is used for collision detection (usually lowercase)
- `displayName` is what appears in queries
- Both generators use the same `toDbCompatibleName()` helper as `TableSchemaMapper`

### Infrastructure Step 2: Register TempTableNameGenerator in BeanFactory

**File:** Update `{DB}BeanFactory.kt`

Choose the pattern that fits your database:

**Pattern A: Simple (no separate internal schema)**
```kotlin
@Singleton
fun tempTableNameGenerator(): TempTableNameGenerator {
    return DefaultTempTableNameGenerator()
}
```

**Pattern B: With internal schema (Postgres, Snowflake)**
```kotlin
@Singleton
fun tempTableNameGenerator(config: {DB}Configuration): TempTableNameGenerator {
    return DefaultTempTableNameGenerator(
        internalNamespace = config.internalSchema
    )
}
```

**Which pattern to use:**
- **Pattern A:** Temp tables in same namespace as final tables (ClickHouse)
- **Pattern B:** Dedicated internal/staging schema for temp tables (Postgres, Snowflake)

**Why register as bean?**
- TempTableNameGenerator is an interface, not a class
- CDK provides implementation, but YOU must register it
- Used by Writer to create staging tables

### Infrastructure Step 3: Verify Compilation

**Validate:**
```bash
$ ./gradlew :destination-{db}:compileKotlin  # BUILD SUCCESSFUL
$ ./gradlew :destination-{db}:componentTest  # 5 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # testSpecOss, testSuccessConfigs should pass
```

**If you see DI errors:**
- Check all classes have `@Singleton` annotation
- Verify package name matches your connector structure
- Ensure classes implement correct interfaces:
  - `FinalTableNameGenerator` (from `io.airbyte.cdk.load.table`)
  - `ColumnNameGenerator` (from `io.airbyte.cdk.load.table`)

✅ **Checkpoint:** Name generators registered + all previous phases still work

---

---

⚠️ **IMPORTANT: Before starting Phase 3, read [Understanding Test Contexts](./7-troubleshooting.md#understanding-test-contexts) in the troubleshooting guide. This phase introduces integration tests which behave differently than the component tests you've been using.**

---

## Infrastructure Phase 3: Write Operation Infrastructure

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
import jakarta.inject.Singleton

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

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.table.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Singleton

@Singleton
class {DB}DirectLoadDatabaseInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    catalog: DestinationCatalog,
) : BaseDirectLoadInitialStatusGatherer(
    tableOperationsClient,
    catalog,
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

**Note:** The `@Singleton` annotation on the class is sufficient - no separate BeanFactory registration needed. Micronaut will auto-discover this bean.

### Infrastructure Step 3: Create ColumnNameMapper

**File:** `write/transform/{DB}ColumnNameMapper.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.table.TableCatalog
import jakarta.inject.Singleton

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

### Infrastructure Step 4: Register AggregatePublishingConfig in BeanFactory

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

### Infrastructure Step 5: Create WriteInitializationTest

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

### Infrastructure Step 6: Create Test Config File

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

### Infrastructure Step 7: Validate WriteInitializationTest

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
