# Database Setup: Connectivity, Operations, and Check

**Prerequisites:** Complete [1-getting-started.md](./1-getting-started.md) - Your connector's `--spec` operation must be working.

## What You'll Build

After completing this guide, your connector will have:
- Database connectivity
- Namespace operations
- Basic table operations (create, drop, count)
- `--check` operation working

---

## Phase 2: Database Connectivity

**Goal:** Establish database connection

**Checkpoint:** Can connect to database and execute simple query

### Step 2.1: Create BeanFactory with DataSource

**File:** `{DB}BeanFactory.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.Operation
import io.airbyte.integrations.destination.{db}.spec.*
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Singleton
import javax.sql.DataSource

@Factory
class {DB}BeanFactory {

    @Singleton
    fun configuration(
        configFactory: {DB}ConfigurationFactory,
        specFactory: MigratingConfigurationSpecificationSupplier<{DB}Specification>,
    ): {DB}Configuration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun dataSource(config: {DB}Configuration): DataSource {
        // For JDBC databases:
        return HikariDataSource().apply {
            jdbcUrl = "jdbc:{db}://${config.hostname}:${config.port}/${config.database}"
            username = config.username
            password = config.password
            maximumPoolSize = 10
            connectionTimeout = 30000
        }

        // For non-JDBC: Create your native client here
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyDataSource(): DataSource {
        return object : DataSource {
            override fun getConnection() = null
            override fun getConnection(username: String?, password: String?) = null
            override fun unwrap(iface: Class<*>?) = throw UnsupportedOperationException()
            override fun isWrapperFor(iface: Class<*>?) = false
            override fun getLogWriter() = null
            override fun setLogWriter(out: java.io.PrintWriter?) {}
            override fun setLoginTimeout(seconds: Int) {}
            override fun getLoginTimeout() = 0
            override fun getParentLogger() = throw UnsupportedOperationException()
        }
    }
}
```

### Step 2.2: Add Testcontainers Dependency

**File:** Update `build.gradle.kts`

```kotlin
dependencies {
    // Existing dependencies...

    // Testcontainers for automated testing (recommended)
    testImplementation("org.testcontainers:testcontainers:1.19.0")
    testImplementation("org.testcontainers:{db}:1.19.0")  // e.g., postgresql, mysql, etc.
    // Or for databases without specific module:
    // testImplementation("org.testcontainers:jdbc:1.19.0")
}
```

**Check available modules:** https://www.testcontainers.org/modules/databases/

### Step 2.3: Create Test Configuration with Testcontainers

**File:** `src/test-integration/kotlin/.../component/{DB}TestConfigFactory.kt`

**Primary approach (Testcontainers - recommended):**

```kotlin
package io.airbyte.integrations.destination.{db}.component

import io.airbyte.cdk.command.MigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.{db}.spec.*
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Singleton
import org.testcontainers.containers.{DB}Container  // e.g., PostgreSQLContainer

@Factory
@Requires(env = ["component"])
class {DB}TestConfigFactory {

    @Singleton
    @Primary
    fun testContainer(): {DB}Container<*> {
        // Example for PostgreSQL:
        val container = PostgreSQLContainer("postgres:15-alpine")
            .withDatabaseName("test")
            .withUsername("test")
            .withPassword("test")

        // Example for MySQL:
        // val container = MySQLContainer("mysql:8.0")
        //     .withDatabaseName("test")

        // Example for generic JDBC:
        // val container = JdbcDatabaseContainer("{db}:latest")

        container.start()
        return container
    }

    @Singleton
    @Primary
    fun testConfig(container: {DB}Container<*>): {DB}Configuration {
        return {DB}Configuration(
            hostname = container.host,
            port = container.firstMappedPort,
            database = container.databaseName,
            username = container.username,
            password = container.password,
        )
    }

    @Singleton
    @Primary
    fun testSpecSupplier(
        config: {DB}Configuration
    ): MigratingConfigurationSpecificationSupplier<{DB}Specification> {
        return object : MigratingConfigurationSpecificationSupplier<{DB}Specification> {
            override fun get() = {DB}Specification()
        }
    }
}
```

**Alternative: Environment variables (for local development)**

```kotlin
@Singleton
@Primary
fun testConfig(): {DB}Configuration {
    return {DB}Configuration(
        hostname = System.getenv("DB_HOSTNAME") ?: "localhost",
        port = System.getenv("DB_PORT")?.toInt() ?: 5432,
        database = System.getenv("DB_DATABASE") ?: "test",
        username = System.getenv("DB_USERNAME") ?: "test",
        password = System.getenv("DB_PASSWORD") ?: "test",
    )
}
```

**Why Testcontainers (recommended)?**
- ✅ Isolated test environment (no conflicts with other tests)
- ✅ Works in CI without setup
- ✅ Reproducible across machines
- ✅ Automatic cleanup
- ✅ No manual database installation needed

**When to use environment variables?**
- Local development with existing database
- Database not supported by Testcontainers
- Debugging against specific database version

### Step 2.4: Create Minimal Test Client

**File:** `src/test-integration/kotlin/.../component/{DB}TestTableOperationsClient.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.table.TableName
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Singleton
import javax.sql.DataSource

@Requires(env = ["component"])
@Singleton
class {DB}TestTableOperationsClient(
    private val dataSource: DataSource,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery("SELECT 1")
            }
        }
    }

    override suspend fun dropNamespace(namespace: String) {
        // Implement in Phase 2
        TODO("Implement in Phase 2")
    }

    override suspend fun insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>
    ) {
        // Implement in Phase 3
        TODO("Implement in Phase 3")
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        // Implement in Phase 3
        TODO("Implement in Phase 3")
    }
}
```

### Step 2.5: Create TableOperationsTest (Minimal)

**File:** `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.component

import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class {DB}TableOperationsTest(
    override val client: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
) : TableOperationsSuite {

    @Test
    override fun `connect to database`() {
        super.`connect to database`()
    }

    // Other tests commented out for now - implement in later phases
    // @Test
    // override fun `create and drop namespaces`() { super.`create and drop namespaces`() }
}
```

### Step 2.6: Validate Connection

```bash
$ ./gradlew :destination-{db}:testComponentConnectToDatabase
```

**Expected new passes:**
```
✓ connect to database
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:**
```
✓ connect to database
```

**Troubleshooting:**
- Connection refused? Check hostname/port in test config
- Authentication failed? Verify username/password
- Database doesn't exist? Create test database first or use Testcontainers
- Timeout? Check firewall/network connectivity

✅ **Checkpoint Complete:** Can connect to database

**You're ready for Phase 3 when:** `connect to database` test passes

---

## Phase 3: Namespace Operations

**Goal:** Create and drop schemas/databases

**Checkpoint:** Can manage namespaces

### Step 3.1: Create SQL Generator (Namespace Methods)

**File:** `client/{DB}SqlGenerator.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.client

import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Singleton

private val log = KotlinLogging.logger {}

fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

@Singleton
class {DB}SqlGenerator {

    fun createNamespace(namespace: String): String {
        // Postgres/MySQL: CREATE SCHEMA
        return "CREATE SCHEMA IF NOT EXISTS ${namespace.quote()}".andLog()

        // Or for databases without schemas:
        return "CREATE DATABASE IF NOT EXISTS ${namespace.quote()}".andLog()
    }

    fun namespaceExists(namespace: String): String {
        // Postgres:
        return """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = '${namespace}'
        """.trimIndent().andLog()

        // Or query your DB's system catalog
    }

    private fun String.quote() = "\"$this\""  // Or backticks, brackets, etc.

    private fun fullyQualifiedName(tableName: TableName) =
        "${tableName.namespace.quote()}.${tableName.name.quote()}"
}
```

### Step 2.2: Create Database Client (Namespace Methods)

**File:** `client/{DB}AirbyteClient.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.client

import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import io.micronaut.context.annotation.Singleton
import javax.sql.DataSource

@Singleton
class {DB}AirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: {DB}SqlGenerator,
    private val config: {DB}Configuration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sqlGenerator.namespaceExists(namespace))
                rs.next()  // Returns true if namespace exists
            }
        }
    }

    private fun execute(sql: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(sql)
            }
        }
    }

    // Stub other methods for now
    override suspend fun createTable(...) = TODO("Phase 3")
    override suspend fun dropTable(...) = TODO("Phase 3")
    override suspend fun tableExists(...) = TODO("Phase 3")
    override suspend fun countTable(...) = TODO("Phase 3")
    override suspend fun getGenerationId(...) = TODO("Phase 3")
    override suspend fun copyTable(...) = TODO("Phase 7")
    override suspend fun overwriteTable(...) = TODO("Phase 6")
    override suspend fun upsertTable(...) = TODO("Phase 9")
    override suspend fun discoverSchema(...) = TODO("Phase 8")
    override fun computeSchema(...) = TODO("Phase 8")
    override suspend fun ensureSchemaMatches(...) = TODO("Phase 8")
    override suspend fun applyChangeset(...) = TODO("Phase 8")
}
```

### Step 2.3: Update Test Client

**File:** Update `{DB}TestTableOperationsClient.kt`

```kotlin
override suspend fun dropNamespace(namespace: String) {
    dataSource.connection.use { connection ->
        connection.createStatement().use { statement ->
            // Postgres/MySQL:
            statement.execute("DROP SCHEMA IF EXISTS \"${namespace}\" CASCADE")

            // Or for databases without schemas:
            statement.execute("DROP DATABASE IF EXISTS `${namespace}`")
        }
    }
}
```

### Step 2.4: Register Client in BeanFactory

**File:** Update `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun client(
    dataSource: DataSource,
    sqlGenerator: {DB}SqlGenerator,
    config: {DB}Configuration,
): {DB}AirbyteClient {
    return {DB}AirbyteClient(dataSource, sqlGenerator, config)
}
```

### Step 2.5: Enable Test in TableOperationsTest

**File:** Update `{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `create and drop namespaces`() {
    super.`create and drop namespaces`()
}
```

### Step 2.6: Validate

```bash
$ ./gradlew :destination-{db}:testComponentCreateAndDropNamespaces
```

**Expected new passes:**
```
✓ create and drop namespaces
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:**
```
✓ connect to database
✓ create and drop namespaces (new)
```

✅ **Checkpoint Complete:** Can manage namespaces

**You're ready for Phase 3 when:** `create and drop namespaces` test passes

---

## Phase 4: Basic Table Operations

**Goal:** Create tables, insert data, count rows

**Checkpoint:** Can perform basic table CRUD

### Step 4.1: Create Column Utilities

**File:** `client/{DB}ColumnUtils.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.client

import io.airbyte.cdk.load.data.*
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}ColumnUtils {

    fun toDialectType(type: AirbyteType): String = when (type) {
        BooleanType -> "BOOLEAN"
        IntegerType -> "BIGINT"
        NumberType -> "DECIMAL(38, 9)"
        StringType -> "VARCHAR"  // or TEXT
        DateType -> "DATE"
        TimeTypeWithTimezone -> "TIME WITH TIME ZONE"
        TimeTypeWithoutTimezone -> "TIME"
        TimestampTypeWithTimezone -> "TIMESTAMP WITH TIME ZONE"
        TimestampTypeWithoutTimezone -> "TIMESTAMP"
        is ArrayType, ArrayTypeWithoutSchema -> "JSONB"  // or TEXT
        is ObjectType, ObjectTypeWithEmptySchema, ObjectTypeWithoutSchema -> "JSONB"
        is UnionType, is UnknownType -> "JSONB"  // or VARCHAR as fallback
        else -> "VARCHAR"
    }

    fun formatColumn(name: String, type: AirbyteType, nullable: Boolean): String {
        val typeDecl = toDialectType(type)
        val nullableDecl = if (nullable) "" else " NOT NULL"
        return "\"$name\" $typeDecl$nullableDecl"
    }
}
```

**Database-specific adjustments:**
- **Snowflake:** `VARCHAR` (no length), `VARIANT` for JSON
- **ClickHouse:** `String`, `Nullable()` wrapper, `DateTime64(3)`
- **MySQL:** `VARCHAR(65535)`, `JSON` type
- **BigQuery:** `STRING`, `JSON`, specific types

### Step 3.2: Add Table Methods to SQL Generator

**File:** Update `{DB}SqlGenerator.kt`

```kotlin
fun createTable(
    stream: DestinationStream,
    tableName: TableName,
    columnMapping: ColumnNameMapping,
    replace: Boolean
): String {
    val replaceClause = if (replace) "OR REPLACE " else ""

    val columnDeclarations = stream.schema.asColumns()
        .filter { (name, _) -> name !in AIRBYTE_META_COLUMNS }
        .map { (name, type) ->
            val mappedName = columnMapping[name]!!
            columnUtils.formatColumn(mappedName, type.type, type.nullable)
        }
        .joinToString(",\n  ")

    return """
        CREATE ${replaceClause}TABLE ${fullyQualifiedName(tableName)} (
          "_airbyte_raw_id" VARCHAR NOT NULL,
          "_airbyte_extracted_at" TIMESTAMP NOT NULL,
          "_airbyte_meta" JSONB NOT NULL,
          "_airbyte_generation_id" BIGINT,
          $columnDeclarations
        )
    """.trimIndent().andLog()
}

fun dropTable(tableName: TableName): String {
    return "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}".andLog()
}

fun countTable(tableName: TableName): String {
    return """
        SELECT COUNT(*) AS count
        FROM ${fullyQualifiedName(tableName)}
    """.trimIndent().andLog()
}

fun getGenerationId(tableName: TableName): String {
    return """
        SELECT "_airbyte_generation_id" AS generation_id
        FROM ${fullyQualifiedName(tableName)}
        LIMIT 1
    """.trimIndent().andLog()
}

private val AIRBYTE_META_COLUMNS = setOf(
    "_airbyte_raw_id",
    "_airbyte_extracted_at",
    "_airbyte_meta",
    "_airbyte_generation_id"
)
```

### Step 3.3: Implement Table Operations in Client

**File:** Update `{DB}AirbyteClient.kt`

```kotlin
override suspend fun createTable(
    stream: DestinationStream,
    tableName: TableName,
    columnNameMapping: ColumnNameMapping,
    replace: Boolean
) {
    execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, replace))
}

override suspend fun dropTable(tableName: TableName) {
    execute(sqlGenerator.dropTable(tableName))
}

override suspend fun tableExists(table: TableName): Boolean {
    return countTable(table) != null
}

override suspend fun countTable(tableName: TableName): Long? =
    try {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sqlGenerator.countTable(tableName))
                if (rs.next()) rs.getLong("count") else 0L
            }
        }
    } catch (e: SQLException) {
        log.debug(e) { "Table ${tableName} does not exist. Returning null." }
        null  // Expected - table doesn't exist
    }

override suspend fun getGenerationId(tableName: TableName): Long {
    try {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sqlGenerator.getGenerationId(tableName))
                if (rs.next()) {
                    rs.getLong("generation_id") ?: 0L
                } else {
                    0L
                }
            }
        }
    } catch (e: SQLException) {
        log.debug(e) { "Failed to retrieve generation ID, returning 0" }
        return 0L
    }
}
```

### Step 3.4: Implement Test Client Insert/Read

**File:** Update `{DB}TestTableOperationsClient.kt`

```kotlin
override suspend fun insertRecords(
    table: TableName,
    records: List<Map<String, AirbyteValue>>
) {
    if (records.isEmpty()) return

    dataSource.connection.use { connection ->
        records.forEach { record ->
            val columns = record.keys.joinToString(", ") { "\"$it\"" }
            val placeholders = record.keys.joinToString(", ") { "?" }
            val sql = """
                INSERT INTO "${table.namespace}"."${table.name}" ($columns)
                VALUES ($placeholders)
            """

            connection.prepareStatement(sql).use { statement ->
                record.values.forEachIndexed { index, value ->
                    setParameter(statement, index + 1, value)
                }
                statement.executeUpdate()
            }
        }
    }
}

override suspend fun readTable(table: TableName): List<Map<String, Any>> {
    val results = mutableListOf<Map<String, Any>>()

    dataSource.connection.use { connection ->
        val sql = "SELECT * FROM \"${table.namespace}\".\"${table.name}\""
        connection.createStatement().use { statement ->
            val rs = statement.executeQuery(sql)
            val metadata = rs.metaData

            while (rs.next()) {
                val row = mutableMapOf<String, Any>()
                for (i in 1..metadata.columnCount) {
                    val columnName = metadata.getColumnName(i)
                    val value = rs.getObject(i)
                    if (value != null) {
                        row[columnName] = value
                    }
                }
                results.add(row)
            }
        }
    }

    return results
}

private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
    when (value) {
        is StringValue -> statement.setString(index, value.value)
        is IntegerValue -> statement.setLong(index, value.value)
        is NumberValue -> statement.setBigDecimal(index, value.value)
        is BooleanValue -> statement.setBoolean(index, value.value)
        is TimestampValue -> statement.setTimestamp(index, Timestamp.from(value.value))
        is DateValue -> statement.setDate(index, Date.valueOf(value.value))
        is ObjectValue -> statement.setString(index, value.toJson())  // JSON as string
        is ArrayValue -> statement.setString(index, value.toJson())   // JSON as string
        is NullValue -> statement.setNull(index, Types.VARCHAR)
        else -> statement.setString(index, value.toString())
    }
}
```

**Note:** For non-JDBC databases, use native client APIs for insert/read

### Step 3.5: Enable Table Tests

**File:** Update `{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `create and drop tables`() {
    super.`create and drop tables`()
}

@Test
override fun `insert records`() {
    super.`insert records`()
}

@Test
override fun `count table rows`() {
    super.`count table rows`()
}
```

### Step 3.6: Validate

```bash
$ ./gradlew :destination-{db}:testComponentCreateAndDropTables \
             :destination-{db}:testComponentInsertRecords \
             :destination-{db}:testComponentCountTableRows
```

**Expected new passes:**
```
✓ create and drop tables
✓ insert records
✓ count table rows
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:**
```
✓ connect to database
✓ create and drop namespaces
✓ create and drop tables (new)
✓ insert records (new)
✓ count table rows (new)
```

✅ **Checkpoint Complete:** Can manage tables and data

**You're ready for Phase 4 when:** All table operation tests pass

---

## Phase 5: Check Operation

**Goal:** Implement --check operation (validates database connection)

**Checkpoint:** Check operation works

### Step 5.1: Create Checker

**File:** `check/{DB}Checker.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.check

import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import io.micronaut.context.annotation.Singleton
import kotlinx.coroutines.runBlocking
import java.util.UUID

@Singleton
class {DB}Checker(
    private val client: {DB}AirbyteClient,
    private val config: {DB}Configuration,
) : DestinationCheckerV2 {

    override fun check() {
        val testNamespace = config.database
        val testTableName = "_airbyte_connection_test_${UUID.randomUUID()}"
        val tableName = TableName(testNamespace, testTableName)

        runBlocking {
            try {
                client.createNamespace(testNamespace)

                val testStream = createTestStream()
                val columnMapping = ColumnNameMapping(mapOf("test_col" to "test_col"))

                client.createTable(testStream, tableName, columnMapping, replace = false)

                val count = client.countTable(tableName)
                require(count == 0L) { "Expected empty table, got $count rows" }

            } finally {
                client.dropTable(tableName)
            }
        }
    }

    private fun createTestStream(): DestinationStream {
        return DestinationStream(
            descriptor = DestinationStream.Descriptor(namespace = config.database, name = "test"),
            importType = DestinationStream.ImportType.APPEND,
            schema = ObjectType(linkedMapOf("test_col" to FieldType(StringType, true))),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 0,
        )
    }
}
```

### Step 5.2: Create Check Integration Test

**File:** `src/test-integration/kotlin/.../check/{DB}CheckTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.{db}.spec.{DB}Specification
import java.nio.file.Path

class {DB}CheckTest :
    CheckIntegrationTest<{DB}Specification>(
        successConfigFilenames = listOf(
            CheckTestConfig(configPath = Path.of("secrets/config.json")),
        ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
```

### Step 5.3: Validate Check Operation

**Via Docker:**
```bash
# Create test config
cat > /tmp/test-config.json << EOF
{
  "hostname": "localhost",
  "port": 5432,
  "database": "test",
  "username": "test",
  "password": "test"
}
EOF

# Run check operation
docker run --rm --network host \
  -v /tmp/test-config.json:/config.json \
  airbyte/destination-{db}:0.1.0 --check --config /config.json
```

**Expected:**
```json
{"type":"CONNECTION_STATUS","connectionStatus":{"status":"SUCCEEDED"}}
```

**Via integration test:**
```bash
$ ./gradlew :destination-{db}:integrationTestCheckSuccessConfigs
```

**Expected:**
```
✓ testSuccessConfigs
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: 8 tests pass
Integration: testSpecOss, testSuccessConfigs pass
```

✅ **Checkpoint Complete:** --check operation works

**You're ready for Phase 6 when:** Check test passes

---

## Next Steps

**Next:** Continue to [3-write-infrastructure.md](./3-write-infrastructure.md) to set up the write operation infrastructure.
