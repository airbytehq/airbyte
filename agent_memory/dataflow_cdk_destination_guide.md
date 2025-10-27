# Airbyte Dataflow CDK Destination Implementation Guide

**Purpose:** Reference guide for Claude Code when implementing new Airbyte dataflow CDK destinations.

**Version:** 1.0
**Last Updated:** 2025-10-23
**Reference Implementation:** Snowflake Destination

---

## Overview

The Airbyte Dataflow CDK provides a modern, reactive framework for building destination connectors using:

- **Kotlin** with coroutines for async operations
- **Micronaut** for compile-time dependency injection
- **Kotlin Flow** for reactive data pipelines with backpressure
- **HikariCP** for production-grade connection pooling

### CDK Location

```
/airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/
├── command/          # Lifecycle orchestration (DestinationLifecycle)
├── dataflow/         # Pipeline stages (Parse, Aggregate, Flush, State)
├── check/            # Connection validation (DestinationCheckerV2)
├── config/           # Bean factories (InputBeanFactory, DispatcherBeanFactory)
├── write/            # Writer interfaces (DestinationWriter)
└── spec/             # Specification interfaces (ConfigurationSpecification)
```

---

## Architecture Fundamentals

### The 4-Stage Data Flow Pipeline

```
Source → Parse → Aggregate → Flush → State → Destination

┌─────────────┐
│   Source    │  Raw records from source connector
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Parse    │  ParseStage: Transform raw → RecordDTO
└──────┬──────┘  Uses RecordMunger for schema mapping
       │
       ▼
┌─────────────┐
│  Aggregate  │  AggregateStage: Batch records for bulk loading
└──────┬──────┘  Emits when size/time threshold hit
       │
       ▼
┌─────────────┐
│    Flush    │  FlushStage: Calls aggregate.flush() to write
└──────┬──────┘  Actual database write happens here
       │
       ▼
┌─────────────┐
│    State    │  StateStage: Updates state stores
└──────┬──────┘  Tracks committed records for checkpointing
       │
       ▼
┌─────────────┐
│ Destination │
└─────────────┘
```

### Lifecycle Flow

```
1. INITIALIZATION
   └─ DestinationLifecycle.run()
      └─ DestinationWriter.setup()
         └─ Create schemas, tables, initial setup

2. STREAM PREPARATION
   └─ DestinationWriter.createStreamLoader(stream)
      └─ Return appropriate StreamLoader (append/truncate/dedupe)

3. DATA PIPELINE (parallel processing)
   └─ For each input flow: Parse → Aggregate → Flush → State
   └─ Coroutine dispatchers control concurrency per stage

4. FINALIZATION
   └─ Stream loaders finalized
   └─ DestinationWriter.teardown()
```

### Key CDK Classes

| Class | Location | Purpose |
|-------|----------|---------|
| `DestinationLifecycle` | `command/` | Central orchestrator, manages lifecycle |
| `DataFlowPipeline` | `dataflow/` | Implements 4-stage reactive pipeline |
| `ParseStage` | `dataflow/` | Transform records with RecordMunger |
| `AggregateStage` | `dataflow/` | Batch records using AggregateStore |
| `FlushStage` | `dataflow/` | Call aggregate.flush() |
| `StateStage` | `dataflow/` | Update state stores |
| `DestinationWriter` | `write/` | Main interface for destinations |
| `DestinationCheckerV2` | `check/` | Validate connection/permissions |
| `InputBeanFactory` | `config/` | Create input flows, aggregates |
| `DispatcherBeanFactory` | `config/` | Create coroutine dispatchers |

---

## Core Interfaces

### DestinationWriter (Main Entry Point)

```kotlin
interface DestinationWriter {
    suspend fun setup() {}  // Create schemas, initial setup
    fun createStreamLoader(stream: DestinationStream): StreamLoader
    suspend fun teardown(destinationFailure: DestinationFailure? = null) {}
}
```

### Aggregate (Batching Logic)

```kotlin
interface Aggregate {
    fun accept(record: RecordDTO)  // Accumulate records
    suspend fun flush()             // Write batch to destination
}

interface AggregateFactory {
    fun create(key: StoreKey): Aggregate
}
```

### DestinationCheckerV2 (Connection Validation)

```kotlin
interface DestinationCheckerV2 {
    fun check()      // Validate connection, throw on failure
    fun cleanup() {} // Always cleanup test artifacts
}
```

---

## The Snowflake Approach (Recommended Pattern)

**Reference Implementation:** `/airbyte-integrations/connectors/destination-snowflake/`

### Why Snowflake Pattern?

| Aspect | Snowflake Pattern | Why Better |
|--------|------------------|------------|
| **Checker** | `DestinationCheckerV2` | Full DI, no config passing |
| **Connection Pool** | HikariCP | Production-grade, health checks, leak detection |
| **Auth** | Polymorphic sealed classes | Type-safe, extensible |
| **Metadata** | `@Cacheable` on queries | Reduces repeated lookups |
| **Conditional Beans** | `@Requires(property)` | Different beans per operation |
| **Client** | Wrapper abstraction | High-level ops, error handling |
| **Type System** | Dedicated mapper/coercer | Separation of concerns |

### Key Files to Study

- `SnowflakeBeanFactory.kt` - DI patterns, conditional beans
- `SnowflakeChecker.kt` - End-to-end validation pattern
- `SnowflakeWriter.kt` - Stream loader selection logic
- `SnowflakeAggregateFactory.kt` - Caching pattern with `@Cacheable`
- `SnowflakeAirbyteClient.kt` - Client wrapper over JDBC
- `SnowflakeSpecification.kt` - Polymorphic config example

---

## Required Components for New Destination

### 1. Specification & Configuration

#### Files Needed
```
spec/
├── {Name}Specification.kt          # User-facing JSON Schema
├── {Name}Configuration.kt          # Internal data class
├── {Name}ConfigurationFactory.kt   # Transforms Spec → Config
└── {Name}SpecificationExtension.kt # Sync modes, UI groups (optional)
```

#### Specification Example
```kotlin
@Singleton
class MyDestinationSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription("Database hostname")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 0}""")
    val host: String = ""

    @get:JsonSchemaTitle("Password")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 3, "airbyte_secret": true}""")
    val password: String = ""
}
```

**Key Annotations:**
- `@JsonSchemaTitle` - Display name
- `@JsonPropertyDescription` - Help text
- `@JsonSchemaInject` - Additional properties: `order`, `default`, `airbyte_secret`, `group`, `airbyte_hidden`

#### Configuration Example
```kotlin
data class MyDestinationConfiguration(
    val host: String,
    val port: Int,
    val username: String,
    val password: String,
) : DestinationConfiguration() {
    // Derived properties
    val jdbcUrl = "jdbc:mydb://$host:$port"
}
```

#### Factory Example
```kotlin
@Singleton
class MyDestinationConfigurationFactory :
    DestinationConfigurationFactory<MyDestinationSpecification, MyDestinationConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MyDestinationSpecification
    ): MyDestinationConfiguration {
        return MyDestinationConfiguration(
            host = pojo.host,
            port = pojo.port,
            username = pojo.username,
            password = pojo.password,
        )
    }
}
```

### 2. Bean Factory (DI Container)

```kotlin
@Factory
class MyDestinationBeanFactory {

    // Load configuration
    @Singleton
    fun configuration(
        configFactory: MyDestinationConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier,
    ): MyDestinationConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    // Dummy datasource for spec operation (no config available)
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyDataSource(): DataSource {
        return object : DataSource {
            override fun getConnection(): Connection? = null
            override fun getLogWriter(): PrintWriter = PrintWriter(System.out)
            override fun setLogWriter(out: PrintWriter) {}
            override fun setLoginTimeout(seconds: Int) {}
            override fun getLoginTimeout(): Int = 0
            override fun getParentLogger(): Logger = Logger.getGlobal()
            override fun <T : Any> unwrap(iface: Class<T>): T? = null
            override fun isWrapperFor(iface: Class<*>): Boolean = false
        }
    }

    // Real connection pool for check/write operations
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun dataSource(config: MyDestinationConfiguration): HikariDataSource {
        val hikariConfig = HikariConfig().apply {
            connectionTimeout = 30000L        // 30 seconds
            maximumPoolSize = 10
            minimumIdle = 0
            idleTimeout = 600000L            // 10 minutes
            initializationFailTimeout = -1
            leakDetectionThreshold = 40000L  // 40 seconds
            maxLifetime = 610000L            // Slightly more than idle

            jdbcUrl = config.jdbcUrl
            driverClassName = MyDriver::class.qualifiedName
            username = config.username
            password = config.password

            // Driver-specific properties
            addDataSourceProperty("database", config.database)
            addDataSourceProperty("schema", config.schema)
        }
        return HikariDataSource(hikariConfig)
    }

    // Temp table name generator
    @Singleton
    fun tempTableNameGenerator(config: MyDestinationConfiguration): TempTableNameGenerator =
        DefaultTempTableNameGenerator(internalNamespace = config.internalSchema)

    // Batch configuration
    @Singleton
    fun aggregatePublishingConfig(
        dataChannelMedium: DataChannelMedium
    ): AggregatePublishingConfig {
        return if (dataChannelMedium == DataChannelMedium.STDIO) {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
            )
        } else {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
                maxBufferedAggregates = 6,
            )
        }
    }

    // Check operation (only for check)
    @Primary
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "check")
    fun checkOperation(
        destinationChecker: DestinationCheckerV2,
        outputConsumer: OutputConsumer,
    ) = CheckOperationV2(destinationChecker, outputConsumer)
}
```

### 3. Checker (V2 Pattern)

**Pattern:** End-to-end validation (create schema → create table → insert → verify → cleanup)

```kotlin
@Singleton
class MyDestinationChecker(
    private val client: MyDestinationAirbyteClient,
    private val config: MyDestinationConfiguration,
    private val columnUtils: MyDestinationColumnUtils,
) : DestinationCheckerV2 {

    override fun check() {
        val data = mapOf(
            Meta.AirbyteMetaFields.RAW_ID.fieldName to
                AirbyteValue.from(UUID.randomUUID().toString()),
            Meta.AirbyteMetaFields.EXTRACTED_AT.fieldName to
                AirbyteValue.from(OffsetDateTime.now()),
            Meta.AirbyteMetaFields.META.fieldName to
                AirbyteValue.from(emptyMap<String, String>()),
            Meta.AirbyteMetaFields.GENERATION_ID.fieldName to
                AirbyteValue.from(0),
            "test_key" to AirbyteValue.from("test-value")
        )

        // Unique table name with UUID
        val tableName = "_airbyte_connection_test_${
            UUID.randomUUID().toString().replace("-", "")
        }"
        val qualifiedTableName = TableName(
            namespace = config.schema,
            name = tableName
        )

        val destinationStream = DestinationStream(
            unmappedNamespace = config.schema,
            unmappedName = tableName,
            importType = Append,
            schema = ObjectType(
                linkedMapOf("test_key" to FieldType(StringType, nullable = false))
            ),
            generationId = 0L,
            minimumGenerationId = 0L,
            syncId = 0L,
            namespaceMapper = NamespaceMapper()
        )

        runBlocking {
            try {
                // 1. Create schema
                client.createNamespace(config.schema)

                // 2. Create table
                client.createTable(
                    stream = destinationStream,
                    tableName = qualifiedTableName,
                    columnNameMapping = ColumnNameMapping(emptyMap()),
                    replace = true,
                )

                // 3. Get table metadata
                val columns = client.describeTable(qualifiedTableName)

                // 4. Create insert buffer
                val insertBuffer = MyDestinationInsertBuffer(
                    tableName = qualifiedTableName,
                    columns = columns,
                    client = client,
                    config = config,
                    columnUtils = columnUtils,
                )

                // 5. Insert and verify
                insertBuffer.accumulate(data)
                insertBuffer.flush()

                val count = client.countTable(qualifiedTableName)
                require(count == 1L) {
                    "Failed to insert expected rows. Actual: $count"
                }

            } finally {
                // ALWAYS cleanup
                client.dropTable(qualifiedTableName)
            }
        }
    }
}
```

**What the checker validates:**
- ✅ Connection established
- ✅ Authentication valid
- ✅ CREATE SCHEMA permission
- ✅ CREATE TABLE permission
- ✅ INSERT permission
- ✅ SELECT permission (count query)
- ✅ DROP TABLE permission
- ✅ Full write path works (buffer flush)

### 4. Client Wrapper

**Pattern:** Abstract over raw driver, provide high-level operations

```kotlin
@Singleton
class MyDestinationAirbyteClient(
    private val dataSource: DataSource,
    private val config: MyDestinationConfiguration,
    private val sqlGenerator: MyDestinationSqlGenerator,
) {
    suspend fun createNamespace(namespace: String) {
        withConnection { conn ->
            conn.createStatement().use { stmt ->
                stmt.execute(sqlGenerator.createSchema(namespace))
            }
        }
    }

    suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        withConnection { conn ->
            val sql = sqlGenerator.createTable(stream, tableName, replace)
            conn.createStatement().use { stmt ->
                stmt.execute(sql)
            }
        }
    }

    suspend fun describeTable(tableName: TableName): List<ColumnMetadata> {
        return withConnection { conn ->
            val sql = sqlGenerator.describeTable(tableName)
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery(sql)
                buildList {
                    while (rs.next()) {
                        add(ColumnMetadata(
                            name = rs.getString("COLUMN_NAME"),
                            type = rs.getString("DATA_TYPE"),
                            nullable = rs.getBoolean("IS_NULLABLE")
                        ))
                    }
                }
            }
        }
    }

    suspend fun countTable(tableName: TableName): Long {
        return withConnection { conn ->
            val sql = "SELECT COUNT(*) FROM ${tableName.qualified()}"
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery(sql)
                if (rs.next()) rs.getLong(1) else 0L
            }
        }
    }

    suspend fun dropTable(tableName: TableName) {
        withConnection { conn ->
            val sql = sqlGenerator.dropTable(tableName)
            conn.createStatement().use { stmt ->
                stmt.execute(sql)
            }
        }
    }

    private suspend fun <T> withConnection(block: (Connection) -> T): T {
        return withContext(Dispatchers.IO) {
            dataSource.connection.use { conn ->
                block(conn)
            }
        }
    }
}
```

### 5. Writer

```kotlin
@Singleton
class MyDestinationWriter(
    private val client: MyDestinationAirbyteClient,
    private val config: MyDestinationConfiguration,
    private val catalog: DestinationCatalog,
) : DestinationWriter {

    override suspend fun setup() {
        // Create all schemas
        val namespaces = catalog.streams
            .map { it.descriptor.namespace }
            .distinct()

        namespaces.forEach { namespace ->
            client.createNamespace(namespace)
        }

        // Create internal schema
        if (config.internalSchema.isNotBlank()) {
            client.createNamespace(config.internalSchema)
        }
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return when {
            stream.importType is Dedupe -> {
                if (stream.generationId == stream.minimumGenerationId) {
                    DirectLoadTableDedupStreamLoader(stream, /* ... */)
                } else {
                    DirectLoadTableDedupTruncateStreamLoader(stream, /* ... */)
                }
            }
            else -> {
                if (stream.generationId == stream.minimumGenerationId) {
                    DirectLoadTableAppendStreamLoader(stream, /* ... */)
                } else {
                    DirectLoadTableAppendTruncateStreamLoader(stream, /* ... */)
                }
            }
        }
    }

    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        // Cleanup if needed
    }
}
```

### 6. Aggregate & AggregateFactory

```kotlin
class MyDestinationAggregate(
    private val tableName: TableName,
    private val columns: List<ColumnMetadata>,
    private val client: MyDestinationAirbyteClient,
    private val config: MyDestinationConfiguration,
) : Aggregate {

    private val buffer = MyDestinationInsertBuffer(
        tableName = tableName,
        columns = columns,
        client = client,
        config = config,
    )

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.data)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}

@Singleton
@CacheConfig("table-columns")
class MyDestinationAggregateFactory(
    private val client: MyDestinationAirbyteClient,
    private val config: MyDestinationConfiguration,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    // Cache expensive metadata lookups
    @Cacheable
    suspend fun getTableColumns(tableName: TableName): List<ColumnMetadata> {
        return client.describeTable(tableName)
    }

    override fun create(key: StoreKey): Aggregate {
        val executionConfig = streamStateStore.get(key)
        val tableName = executionConfig.tableName

        val columns = runBlocking {
            getTableColumns(tableName)
        }

        return MyDestinationAggregate(
            tableName = tableName,
            columns = columns,
            client = client,
            config = config,
        )
    }
}
```

### 7. Supporting Classes

#### SqlGenerator
```kotlin
@Singleton
class MyDestinationSqlGenerator {
    fun createSchema(schema: String): String =
        "CREATE SCHEMA IF NOT EXISTS $schema"

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        replace: Boolean
    ): String {
        // Generate CREATE TABLE statement
        val columns = stream.schema.properties.map { (name, field) ->
            "$name ${mapType(field.type)}"
        }.joinToString(", ")

        val dropClause = if (replace) "DROP TABLE IF EXISTS ${tableName.qualified()}; " else ""
        return "$dropClause CREATE TABLE ${tableName.qualified()} ($columns)"
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${tableName.qualified()}"
}
```

#### ColumnNameMapper
```kotlin
@Singleton
class MyDestinationColumnNameMapper : ColumnNameMapper {
    override fun mapFieldName(fieldName: String): String {
        return fieldName
            .replace("[^a-zA-Z0-9_]".toRegex(), "_")
            .uppercase()
    }
}
```

#### ValueCoercer
```kotlin
@Singleton
class MyDestinationValueCoercer {
    fun coerce(value: AirbyteValue, targetType: String): Any? {
        return when (value) {
            is StringValue -> value.value
            is IntegerValue -> value.value
            is NumberValue -> value.value
            is BooleanValue -> value.value
            is NullValue -> null
            // ... handle other types
            else -> value.toString()
        }
    }
}
```

---

## File Structure

```
destination-{name}/
├── build.gradle.kts
├── metadata.yaml
└── src/
    ├── main/
    │   ├── kotlin/io/airbyte/integrations/destination/{name}/
    │   │   ├── spec/
    │   │   │   ├── {Name}Specification.kt
    │   │   │   ├── {Name}Configuration.kt
    │   │   │   ├── {Name}ConfigurationFactory.kt
    │   │   │   └── {Name}SpecificationExtension.kt
    │   │   ├── check/
    │   │   │   └── {Name}Checker.kt
    │   │   ├── client/
    │   │   │   └── {Name}AirbyteClient.kt
    │   │   ├── write/
    │   │   │   ├── {Name}Writer.kt
    │   │   │   ├── {Name}Aggregate.kt
    │   │   │   ├── {Name}AggregateFactory.kt
    │   │   │   └── load/
    │   │   │       └── {Name}InsertBuffer.kt
    │   │   ├── sql/
    │   │   │   └── {Name}SqlGenerator.kt
    │   │   ├── db/
    │   │   │   ├── {Name}ColumnNameMapper.kt
    │   │   │   ├── {Name}ValueCoercer.kt
    │   │   │   └── {Name}ColumnUtils.kt
    │   │   └── {Name}BeanFactory.kt
    │   └── resources/
    │       └── application.yml
    └── test/
        └── kotlin/io/airbyte/integrations/destination/{name}/
            ├── check/
            ├── spec/
            └── ...
```

---

## Common Patterns

### Pattern 1: Polymorphic Authentication

```kotlin
// Specification
sealed class CredentialsSpecification(val authType: Type) {
    enum class Type { KEY_PAIR, USERNAME_PASSWORD }
}

class KeyPairAuthSpec(val privateKey: String) : CredentialsSpecification(Type.KEY_PAIR)
class UsernamePasswordAuthSpec(val password: String) : CredentialsSpecification(Type.USERNAME_PASSWORD)

// Configuration
sealed interface AuthTypeConfiguration
data class KeyPairAuthConfig(val privateKey: String) : AuthTypeConfiguration
data class UsernamePasswordAuthConfig(val password: String) : AuthTypeConfiguration

// Factory - Transform
val authTypeConfig = when (pojo.credentials) {
    is KeyPairAuthSpec -> KeyPairAuthConfig(pojo.credentials.privateKey)
    is UsernamePasswordAuthSpec -> UsernamePasswordAuthConfig(pojo.credentials.password)
    null -> UsernamePasswordAuthConfig("")
}

// Bean Factory - Use
when (config.authType) {
    is KeyPairAuthConfig -> { /* setup key-based */ }
    is UsernamePasswordAuthConfig -> { username = config.username; password = config.authType.password }
}
```

### Pattern 2: Metadata Caching

```kotlin
@Singleton
@CacheConfig("table-columns")
class AggregateFactory(...) {

    @Cacheable  // Caches per sync
    suspend fun getTableColumns(tableName: TableName): List<ColumnMetadata> {
        return client.describeTable(tableName)
    }
}
```

### Pattern 3: Conditional Bean Creation

```kotlin
// Dummy bean for spec
@Singleton
@Requires(property = Operation.PROPERTY, value = "spec")
fun emptyDataSource(): DataSource = DummyDataSource()

// Real bean for check/write
@Singleton
@Requires(property = Operation.PROPERTY, notEquals = "spec")
fun dataSource(config: Config): HikariDataSource = createRealDataSource(config)
```

---

## Best Practices

### DO ✅

**Configuration:**
- Use sealed classes for polymorphic config
- Mark secrets with `"airbyte_secret": true`
- Provide sensible defaults
- Add helpful descriptions with docs links

**Connection Management:**
- Use HikariCP for connection pooling
- Set proper timeouts (30s connection, 10min idle)
- Enable leak detection
- Create dummy datasource for spec operation

**Checker:**
- Test complete write path (end-to-end)
- Use UUID for unique table names
- Cleanup in finally block (always)
- Verify data was actually written

**SQL Generation:**
- Separate SQL generation into dedicated class
- Quote identifiers properly
- Handle reserved keywords
- Use IF EXISTS/IF NOT EXISTS

**Performance:**
- Use `@Cacheable` for expensive metadata queries
- Batch operations
- Configure appropriate buffer sizes

### DON'T ❌

**Configuration:**
- Don't perform I/O in specification classes
- Don't use mutable properties
- Don't expose dangerous options without warnings

**Connection Management:**
- Don't create raw connections (use pooling)
- Don't leave connections open
- Don't use overly large pool sizes

**Checker:**
- Don't just test connectivity (test full write path)
- Don't reuse table names (causes conflicts)
- Don't skip cleanup
- Don't assume operations succeeded without verification

**SQL Generation:**
- Don't mix SQL logic with business logic
- Don't concatenate user input without escaping
- Don't ignore destination-specific syntax

---

## Implementation Steps

1. **Configuration Setup**
   - Create Specification, Configuration, Factory
   - Define all user-facing fields with proper annotations

2. **Bean Factory**
   - Setup DI container
   - HikariCP connection pool
   - Conditional beans (spec vs check/write)

3. **Checker**
   - Implement DestinationCheckerV2
   - End-to-end validation
   - Proper cleanup

4. **Client Wrapper**
   - Abstract database operations
   - High-level methods
   - Error handling

5. **Supporting Classes**
   - SqlGenerator
   - ColumnNameMapper
   - ValueCoercer
   - ColumnUtils

6. **Writer**
   - Implement DestinationWriter
   - StreamLoader selection logic

7. **Aggregate & Factory**
   - Implement batching logic
   - Cache metadata

8. **Test**
   - Unit tests
   - Integration tests
   - Acceptance tests

---

## Micronaut Annotations Reference

| Annotation | Usage | Example |
|------------|-------|---------|
| `@Singleton` | Single instance | All main components |
| `@Factory` | Bean factory class | `MyBeanFactory` |
| `@Named("name")` | Named bean | Multiple dispatchers |
| `@Requires(property)` | Conditional creation | Spec vs check/write |
| `@Primary` | Preferred bean | Default check operation |
| `@Cacheable` | Cache method results | Table metadata |
| `@CacheConfig("name")` | Cache configuration | Cache name |

---

## Reference Files (Snowflake)

**Must study these files when implementing:**

1. `SnowflakeBeanFactory.kt` - Complete DI setup pattern
2. `SnowflakeChecker.kt` - End-to-end checker pattern
3. `SnowflakeWriter.kt` - Stream loader selection
4. `SnowflakeAggregateFactory.kt` - Caching with @Cacheable
5. `SnowflakeAirbyteClient.kt` - Client wrapper pattern
6. `SnowflakeSpecification.kt` - Polymorphic config

**Location:** `/airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/`

---

## Quick Reference: Operations

| Operation | Triggered By | Config Available? | Purpose |
|-----------|-------------|-------------------|---------|
| **spec** | `--spec` | ❌ No | Return JSON Schema |
| **check** | `--check` | ✅ Yes | Validate connection |
| **write** | `--write` | ✅ Yes | Perform data sync |

---

## Key Insight: Why Two Classes for Configuration?

```
Specification (User-facing)
├── Has Jackson annotations for JSON Schema
├── Generates UI in Airbyte
├── Can be complex/nested
└── User sees this

         ↓ (ConfigurationFactory transforms)

Configuration (Internal)
├── Simple data class
├── Optimized for code use
├── Can have derived properties
└── Code uses this
```

**Benefit:** Can change internal representation without breaking user-facing API.

---

## Remember When Implementing

1. **Always use Snowflake as reference** - It's the most complete, modern implementation
2. **Use DestinationCheckerV2** - Not V1 (DestinationChecker<C>)
3. **HikariCP for connections** - Not raw connections
4. **End-to-end checker** - Create → Insert → Verify → Cleanup
5. **Cache metadata** - Use @Cacheable for expensive queries
6. **Conditional beans** - Different beans for spec/check/write
7. **Cleanup always** - Use finally blocks
8. **UUID for test tables** - Prevent name collisions

---

**Last Updated:** 2025-10-23
