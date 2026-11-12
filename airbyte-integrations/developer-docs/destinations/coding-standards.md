# Dataflow CDK Coding Standards

**Summary:** Best practices for implementing Airbyte destination connectors. Covers Kotlin style, Micronaut DI patterns, async/coroutines, SQL generation, error handling, and common pitfalls. Follow these standards for maintainable, production-ready code.

---

## Code Organization

### Package Structure

```
destination-{db}/src/main/kotlin/io/airbyte/integrations/destination/{db}/
├── {DB}Destination.kt                    # Entry point (main())
├── {DB}BeanFactory.kt                    # Micronaut DI setup
├── check/{DB}Checker.kt                  # Connection validation
├── client/
│   ├── {DB}AirbyteClient.kt             # Database operations
│   └── {DB}SqlGenerator.kt              # SQL generation
├── config/
│   ├── {DB}NameGenerators.kt            # Table/column naming
│   └── {DB}DirectLoadDatabaseInitialStatusGatherer.kt
├── dataflow/
│   ├── {DB}Aggregate.kt                 # Record accumulation
│   └── {DB}AggregateFactory.kt          # Create aggregates
├── spec/
│   ├── {DB}Specification.kt             # Config schema
│   └── {DB}Configuration.kt             # Runtime config
└── write/
    ├── {DB}Writer.kt                    # Orchestration
    └── load/{DB}InsertBuffer.kt         # Batch writes
```

### File Naming

**Pattern:** `{DatabaseName}{ComponentType}.kt`

**Examples:**
- `SnowflakeAirbyteClient.kt`
- `ClickhouseSqlGenerator.kt`
- `PostgresInsertBuffer.kt`

**Avoid:** Generic names like `Client.kt`, `Generator.kt`

---

## Kotlin Style

### Naming Conventions

```kotlin
// Classes: PascalCase with prefix
class SnowflakeAirbyteClient
class ClickhouseInsertBuffer

// Functions: camelCase, verb-based
fun createTable(...): String
fun toSnowflakeCompatibleName(): String
suspend fun flush()

// Variables: camelCase, descriptive
val snowflakeClient: SnowflakeAirbyteClient
private val columnNameMapping: ColumnNameMapping

// Constants: SCREAMING_SNAKE_CASE
internal const val DATA_SOURCE_CONNECTION_TIMEOUT_MS = 30000L
internal const val CSV_FIELD_SEPARATOR = ','
const val DEFAULT_FLUSH_LIMIT = 1000

// Companion object constants
companion object {
    const val DATETIME_WITH_PRECISION = "DateTime64(3)"
    const val PROTOCOL = "http"
}
```

### Data Classes vs Regular Classes

```kotlin
// ✅ Data classes: Immutable config/value objects
data class SnowflakeConfiguration(
    val host: String,
    val database: String,
    val schema: String,
) : DestinationConfiguration()

// ✅ Regular classes: Stateful components
@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SqlGenerator,
) : TableOperationsClient {
    // Methods with side effects
}
```

### Extension Functions

```kotlin
// ✅ SQL logging
fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

// ✅ Name compatibility
fun String.toSnowflakeCompatibleName(): String {
    return this.uppercase().replace(Regex("[^A-Z0-9_]"), "_")
}

// ✅ Type utilities
fun String.sqlNullable(): String = "Nullable($this)"
fun ColumnType.typeDecl() = typeDecl(this.type, this.nullable)

// ✅ Quoting
fun String.quote() = "\"$this\""  // Snowflake
```

---

## Dependency Injection (Micronaut)

### Always Use Constructor Injection

```kotlin
// ✅ DO: Constructor injection
@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val columnUtils: SnowflakeColumnUtils,
) : TableOperationsClient

// ❌ DON'T: Field injection
@Singleton
class BadExample {
    @Inject lateinit var dataSource: DataSource  // Avoid!
}
```

### BeanFactory Pattern

```kotlin
@Factory
class SnowflakeBeanFactory {

    @Singleton
    fun snowflakeConfiguration(
        configFactory: SnowflakeConfigurationFactory,
        specFactory: SnowflakeMigratingConfigurationSpecificationSupplier,
    ): SnowflakeConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun snowflakeDataSource(
        config: SnowflakeConfiguration,
    ): HikariDataSource {
        return HikariDataSource().apply {
            jdbcUrl = buildConnectionString(config)
            username = config.username
            // ... complex setup
        }
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyDataSource(): DataSource {
        return object : DataSource {
            override fun getConnection(): Connection? = null
        }
    }
}
```

### Conditional Beans

```kotlin
// ✅ Operation-specific beans
@Singleton
@Requires(property = Operation.PROPERTY, value = "spec")
fun specDataSource(): DataSource {
    // Only for --spec operation
}

@Singleton
@Requires(property = Operation.PROPERTY, notEquals = "spec")
fun realDataSource(config: MyConfiguration): HikariDataSource {
    // For --check and --write operations
}
```

### lateinit var Usage

```kotlin
// ✅ For lifecycle-initialized state
@Singleton
class SnowflakeWriter(...) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val status = initialStatuses[stream]!!  // Guaranteed after setup()
        // ...
    }
}

// ✅ For optional state
class InsertBuffer {
    private var csvWriter: CsvWriter? = null
    private var csvFilePath: Path? = null
}

// ❌ Don't use with nullables or primitives
private lateinit var config: Config?  // Compile error!
private lateinit var count: Int       // Compile error!
```

---

## Async & Coroutines

### suspend fun Usage

```kotlin
// ✅ Mark I/O operations as suspend
override suspend fun countTable(tableName: TableName): Long? { ... }
override suspend fun createNamespace(namespace: String) { ... }
override suspend fun flush() { ... }

// ✅ Propagate suspend through call chain
override suspend fun flush() {
    buffer.flush()  // Also suspend
}

// ❌ DON'T block in suspend functions
suspend fun bad() {
    Thread.sleep(1000)  // Blocks thread!
    future.get()        // Blocks thread!
}

// ✅ DO use suspend functions
suspend fun good() {
    delay(1000)         // Suspends without blocking
    future.await()      // Suspends without blocking
}
```

### runBlocking Usage

```kotlin
// ✅ Use only at non-suspend boundaries
@Singleton
class SnowflakeChecker(...) : DestinationCheckerV2 {
    override fun check() {  // Can't be suspend (interface constraint)
        runBlocking {
            try {
                client.createNamespace(namespace)
                client.createTable(...)
            } finally {
                client.dropTable(tableName)
            }
        }
    }
}

// ❌ DON'T use inside suspend functions
suspend fun bad() {
    runBlocking {  // Creates new scope - wrong!
        client.execute(query)
    }
}
```

### Convert Java Futures

```kotlin
import kotlinx.coroutines.future.await

// ✅ Use .await() for CompletableFuture
internal suspend fun execute(query: String): CommandResponse {
    return client.execute(query).await()
}

suspend fun flush() {
    val result = clickhouseClient
        .insert(tableName, data)
        .await()  // Not .get()!
}
```

### Error Handling in Async

```kotlin
// ✅ try-finally for cleanup
suspend fun flush() {
    csvFilePath?.let { filePath ->
        try {
            csvWriter?.flush()
            csvWriter?.close()
            client.putInStage(tableName, filePath.pathString)
            client.copyFromStage(tableName, filePath.fileName.toString())
        } catch (e: Exception) {
            logger.error(e) { "Unable to flush accumulated data." }
            throw e
        } finally {
            // Always cleanup
            filePath.deleteIfExists()
            csvWriter = null
            csvFilePath = null
            recordCount = 0
        }
    }
}
```

---

## SQL Generation Patterns

### Separation of Concerns

```kotlin
// ✅ SqlGenerator: Pure SQL strings, no execution
@Singleton
class SnowflakeDirectLoadSqlGenerator(
    private val columnUtils: SnowflakeColumnUtils,
    private val config: SnowflakeConfiguration,
) {
    fun createTable(...): String { ... }
    fun upsertTable(...): String { ... }
    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}"
    }
}

// ✅ Client: Execution only, delegates SQL generation
@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
) : TableOperationsClient {
    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    private suspend fun execute(sql: String) {
        dataSource.connection.use { conn ->
            conn.createStatement().executeQuery(sql)
        }
    }
}
```

### Always Log SQL

```kotlin
private val log = KotlinLogging.logger {}

// ✅ Extension function pattern
fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

// Usage
fun createTable(...): String {
    return """
        CREATE TABLE ${fullyQualifiedName(tableName)} (
            ${columnDeclarations}
        )
    """.trimIndent().andLog()
}
```

### Quoting and Escaping

```kotlin
// Snowflake: double quotes
internal const val QUOTE = "\""
fun String.quote() = "$QUOTE$this$QUOTE"
"${columnName.quote()}"  // "column_name"

// ClickHouse: backticks
"`${tableName.namespace}`.`${tableName.name}`"

// Escape special characters
fun escapeJsonIdentifier(identifier: String): String {
    return identifier.replace(QUOTE, "$QUOTE$QUOTE")
}
```

### Multi-line SQL

```kotlin
// ✅ Use trimIndent()
fun createTable(...): String {
    return """
        CREATE TABLE `${tableName.namespace}`.`${tableName.name}` (
          $COLUMN_NAME_AB_RAW_ID String NOT NULL,
          $COLUMN_NAME_AB_EXTRACTED_AT DateTime64(3) NOT NULL,
          ${columnDeclarations}
        )
        ENGINE = ${engine}
        ORDER BY (${orderByColumns})
    """.trimIndent().andLog()
}

// ✅ Use StringBuilder for complex statements
fun alterTable(changeset: ColumnChangeset, tableName: TableName): String {
    val builder = StringBuilder()
        .append("ALTER TABLE `${tableName.namespace}`.`${tableName.name}`")
        .appendLine()

    changeset.columnsToAdd.forEach { (columnName, columnType) ->
        builder.append(" ADD COLUMN `$columnName` ${columnType.typeDecl()},")
    }

    changeset.columnsToChange.forEach { (columnName, typeChange) ->
        builder.append(" MODIFY COLUMN `$columnName` ${typeChange.newType.typeDecl()},")
    }

    return builder.dropLast(1).toString().andLog()  // Remove trailing comma
}
```

---

## Error Handling

### Exception Types

```kotlin
// ✅ ConfigErrorException: User-fixable
throw ConfigErrorException(
    "Permission denied: Cannot CREATE tables in schema '$schema'. " +
    "Grant CREATE privileges to your role.",
    cause
)

throw ConfigErrorException(
    "Table '$tableName' exists but lacks Airbyte internal columns. " +
    "Delete the table or use a different table prefix."
)

// ✅ TransientErrorException: Retryable
throw TransientErrorException(
    "Network timeout connecting to database. Will retry automatically.",
    cause
)

// ✅ SystemErrorException: Internal errors
throw SystemErrorException(
    "Cannot execute hybrid refresh - unsupported sync mode"
)
```

### Wrap Database Exceptions

```kotlin
private fun handleSnowflakePermissionError(e: SnowflakeSQLException): Nothing {
    val errorMessage = e.message?.lowercase() ?: ""

    when {
        errorMessage.contains("current role has no privileges") -> {
            throw ConfigErrorException(
                "Permission denied. Grant privileges: " +
                "GRANT CREATE, DROP, ALTER ON SCHEMA ${schema} TO ROLE ${role};",
                e
            )
        }
        errorMessage.contains("insufficient privileges") -> {
            throw ConfigErrorException(
                "Insufficient privileges. Contact your database administrator.",
                e
            )
        }
        else -> throw e  // System error
    }
}

// Usage
override suspend fun createNamespace(namespace: String) {
    try {
        execute(sqlGenerator.createNamespace(namespace))
    } catch (e: SnowflakeSQLException) {
        handleSnowflakePermissionError(e)
    }
}
```

### Return Null for Expected Missing Data

```kotlin
// ✅ Return null when table doesn't exist (expected)
override suspend fun countTable(tableName: TableName): Long? =
    try {
        dataSource.connection.use { connection ->
            val statement = connection.createStatement()
            statement.use {
                val resultSet = it.executeQuery(sqlGenerator.countTable(tableName))
                if (resultSet.next()) resultSet.getLong("count") else 0L
            }
        }
    } catch (e: SQLException) {
        log.debug(e) {
            "Table ${tableName.toPrettyString()} does not exist. Returning null."
        }
        null  // Expected - not an error
    }
```

### Actionable Error Messages

```kotlin
// ✅ DO: Specific and actionable
throw ConfigErrorException(
    "Permission denied: Cannot CREATE tables in schema 'public'.\n\n" +
    "Required permission:\n" +
    "  GRANT CREATE ON SCHEMA public TO ROLE your_role;\n\n" +
    "Alternatively:\n" +
    "  1. Use a different schema where you have permissions\n" +
    "  2. Contact your database administrator\n\n" +
    "Current user: ${config.username}\n" +
    "Current role: ${config.role}",
    e
)

// ❌ DON'T: Vague
throw ConfigErrorException("Access denied", e)
throw ConfigErrorException(e.message, e)  // Raw database message
```

---

## Logging Patterns

### Log Levels

```kotlin
private val log = KotlinLogging.logger {}

// info: Normal operations
log.info { "Beginning insert into ${tableName.toPrettyString()}..." }
log.info { "Finished insert of $recordCount row(s)..." }

// warn: Unexpected but recoverable
log.warn { "CSV file path is not set: nothing to upload to staging." }

// error: Errors that will fail the operation
log.error(e) { "Unable to flush accumulated data." }

// debug: Detailed diagnostics
log.debug(e) { "Table does not exist. Returning null..." }
```

### Structured Logging

```kotlin
// ✅ Use lambda syntax for lazy evaluation
log.info { "Expensive computation: ${computeExpensiveValue()}" }
// Only called if INFO enabled

// ❌ DON'T: Eager evaluation
log.info("Expensive computation: ${computeExpensiveValue()}")
// Always called, even if INFO disabled

// ✅ Include context
log.info {
    "overwriteTable: source=${source.toPrettyString()}, " +
    "target=${target.toPrettyString()}, targetExists=$targetExists"
}

log.error(e) {
    "Failed to execute query on table ${tableName.toPrettyString()}. " +
    "Operation: $operation, SQL State: ${e.sqlState}"
}
```

---

## Resource Management

### JDBC Resources

```kotlin
// ✅ Use .use {} for automatic closing
override suspend fun countTable(tableName: TableName): Long? =
    dataSource.connection.use { connection ->
        val statement = connection.createStatement()
        statement.use {
            val resultSet = it.executeQuery(sqlGenerator.countTable(tableName))
            if (resultSet.next()) resultSet.getLong("count") else 0L
        }
    }

// ❌ DON'T: Manual close
val connection = dataSource.connection
try {
    // use connection
} finally {
    connection.close()  // Might not be called if exception in try
}
```

### File Cleanup

```kotlin
// ✅ Use deleteOnExit() for temp files
val tempFile = File.createTempFile("prefix", ".tmp")
tempFile.deleteOnExit()
tempFile.writeText(data)

// ✅ Use deleteIfExists() in finally
suspend fun flush() {
    csvFilePath?.let { filePath ->
        try {
            csvWriter?.flush()
            csvWriter?.close()
            client.putInStage(tableName, filePath.pathString)
        } finally {
            filePath.deleteIfExists()
            csvWriter = null
            csvFilePath = null
        }
    }
}
```

---

## Common Gotchas

### 1. Thread Safety

```kotlin
// ❌ Mutable state in singleton without synchronization
@Singleton
class Bad {
    private var counter = 0  // Race condition!
    fun increment() { counter++ }
}

// ✅ Use lateinit only for lifecycle initialization (set once)
@Singleton
class Good {
    private lateinit var initialStatuses: Map<...>  // Set once in setup()
}
```

### 2. Micronaut Pitfalls

```kotlin
// ❌ Forgetting @Singleton
class MyService {  // Won't be managed by DI!
}

// ❌ Operation beans without @Requires
@Singleton
fun specDataSource(): DataSource {
    // Created for ALL operations!
}

// ✅ Use @Requires
@Singleton
@Requires(property = Operation.PROPERTY, value = "spec")
fun specDataSource(): DataSource {
    // Only for spec operation
}
```

### 3. SQL Injection & Batching

```kotlin
// ❌ Not batching inserts
records.forEach { insertRecord(it) }  // One at a time!

// ✅ Use buffering
class InsertBuffer(flushLimit: Int = 1000) {
    private val buffer = mutableListOf<Record>()

    fun accumulate(record: Record) {
        buffer.add(record)
        if (buffer.size >= flushLimit) {
            runBlocking { flush() }
        }
    }

    suspend fun flush() {
        writeBatchToDatabase(buffer)
        buffer.clear()
    }
}
```

### 4. Resource Leaks

```kotlin
// ❌ Not closing resources
val connection = dataSource.connection
// use connection
// Forgot to close!

// ✅ Use .use {}
dataSource.connection.use { connection ->
    // Automatically closed even if exception
}
```

### 5. Async Pitfalls

```kotlin
// ❌ Blocking in suspend functions
suspend fun bad() {
    Thread.sleep(1000)  // Blocks!
    future.get()        // Blocks!
}

// ✅ Use suspend functions
suspend fun good() {
    delay(1000)     // Suspends
    future.await()  // Suspends
}

// ❌ Not propagating suspend
class Bad {
    fun flush() {  // Not suspend
        runBlocking { client.execute() }  // Creates new scope!
    }
}

// ✅ Keep suspend throughout
class Good {
    suspend fun flush() {  // Propagate suspend
        client.execute()
    }
}
```

### 6. CDK-Specific Gotchas

```kotlin
// ❌ Not using TableCatalog for column mapping
val mappedColumn = columnName.toUpperCase()  // Manual!

// ✅ Use TableCatalog
val mappedColumn = columnNameMapping[columnName]!!

// ❌ Creating tables in Writer.setup()
override suspend fun setup() {
    client.createTable(...)  // StreamLoader does this!
}

// ✅ Only create namespaces in setup()
override suspend fun setup() {
    namespaces.forEach { client.createNamespace(it) }
}

// ❌ Finalizing in InsertBuffer.flush()
suspend fun flush() {
    writeToDatabase()
    client.upsertTable(temp, final)  // DON'T - StreamLoader does this!
}

// ✅ Just write records
suspend fun flush() {
    writeToDatabase()  // That's it!
}
```

### 7. Null Safety

```kotlin
// ❌ Unnecessary !! operator
val value = map[key]!!  // Throws if missing

// ✅ Handle null explicitly
val value = map[key] ?: throw IllegalStateException("Key not found: $key")
val value = map[key]?.let { process(it) }  // Safe call

// ❌ lateinit with wrong types
private lateinit var config: Config?  // Compile error!
private lateinit var count: Int       // Compile error!

// ✅ Use nullable var or non-nullable
private var config: Config? = null
private var count: Int = 0
```

---

## Testing Patterns

### Test Structure

```kotlin
internal class SnowflakeDirectLoadSqlGeneratorTest {
    private lateinit var sqlGenerator: SnowflakeDirectLoadSqlGenerator
    private val uuidGenerator: UUIDGenerator = mockk()

    @BeforeEach
    fun setUp() {
        sqlGenerator = SnowflakeDirectLoadSqlGenerator(
            columnUtils,
            uuidGenerator,
            config,
            nameUtils,
        )
    }

    @Test
    fun testGenerateCountTableQuery() {
        val sql = sqlGenerator.countTable(tableName)

        assertTrue(sql.contains("SELECT COUNT(*)"))
        assertTrue(sql.contains(tableName.name))
    }
}
```

### Test Naming

```kotlin
// ✅ Descriptive test names
@Test
fun testGenerateCountTableQuery() { ... }

@Test
fun testGenerateCreateTableStatement() { ... }

// ✅ Backtick format for readability
@Test
fun `test extractPks with single primary key`() { ... }

@Test
fun `test extractPks with multiple primary keys`() { ... }
```

### Test Cleanup

```kotlin
// ✅ Use try-finally
override fun check() {
    runBlocking {
        try {
            client.createNamespace(namespace)
            client.createTable(table, ...)
            val count = client.countTable(table)
            require(count == 1L)
        } finally {
            client.dropTable(table)
        }
    }
}
```

---

## Style Summary

**Naming:**
- Classes: PascalCase with prefix (`SnowflakeAirbyteClient`)
- Functions: camelCase, verbs (`createTable`, `flush`)
- Variables: camelCase, descriptive (`columnNameMapping`)
- Constants: SCREAMING_SNAKE_CASE (`DEFAULT_FLUSH_LIMIT`)

**DI:**
- Always constructor injection
- Use `@Factory` for complex setup
- Use `@Requires` for conditional beans
- Use `lateinit var` only for lifecycle state

**Async:**
- Mark I/O as `suspend`
- Use `.use {}` for resources
- Use `.await()` for futures
- Propagate `suspend` through call chain

**SQL:**
- Separate generation from execution
- Always log SQL (`.andLog()`)
- Use `.trimIndent()` for multi-line
- Quote all identifiers

**Error:**
- `ConfigErrorException` for user errors
- `TransientErrorException` for retryable
- `SystemErrorException` for internal
- Return `null` for expected missing data

**Logging:**
- Use lambda syntax (lazy evaluation)
- Include context (table names, operations)
- Appropriate levels (info/warn/error/debug)

**Resources:**
- `.use {}` for JDBC/closeable
- `deleteOnExit()` and `finally` for files
- Clean up in `finally` blocks

---

## Quick Reference: Most Common Mistakes

1. ❌ Forgetting `@Singleton` on service classes
2. ❌ Not logging generated SQL
3. ❌ Blocking in suspend functions (`Thread.sleep`, `.get()`)
4. ❌ Not using `.use {}` for resource cleanup
5. ❌ Missing `.trimIndent()` on SQL strings
6. ❌ Using `!!` without proving non-null
7. ❌ Not batching database operations
8. ❌ Creating tables in `Writer.setup()` (StreamLoader does this)
9. ❌ Finalizing in `InsertBuffer.flush()` (StreamLoader does this)
10. ❌ Not using `TableCatalog` for column mapping
