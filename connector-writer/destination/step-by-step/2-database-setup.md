# Database Setup: TableOperationsClient & Check

**Prerequisites:** Complete Setup Phase 2 (Spec Operation) from [1-getting-started.md](./1-getting-started.md)

## What You'll Build

After completing this guide, your connector will have:
- Complete `TableOperationsClient` implementation (all database operations)
- Full test coverage via `TableOperationsSuite` (5 tests passing)
- `--check` operation working
- Ready for Infrastructure Phase 1 (Name Generators)

## Phase Overview

This file contains two phases:

1. **Database Phase 1: TableOperationsClient Implementation**
   - Create database connection and operations
   - Implement all namespace and table operations
   - 5 component tests passing

2. **Database Phase 2: Check Operation**
   - Validate database connection and permissions
   - Integration test for `--check` command

---

## Database Phase 1: TableOperationsClient Implementation

**Goal:** Implement complete database operations interface in one cohesive phase

**Why one phase?** TableOperationsClient is a single cohesive interface. Implementing all methods together:
- ✅ Follows natural coding flow (related methods use same patterns)
- ✅ Clear completion criteria (all TableOperationsSuite tests pass)
- ✅ No confusion about "which tests to enable when"
- ✅ Single validation point

**What you'll implement:**
1. **Infrastructure:** DataSource, test setup, SqlGenerator skeleton
2. **Namespace operations:** CREATE/DROP schemas
3. **Table operations:** CREATE/DROP/COUNT tables
4. **Test utilities:** Insert/read for test verification
5. **Full test suite:** All 5 TableOperationsSuite tests

**Checkpoint:** All TableOperationsSuite tests passing (5 tests)

---

### Database Step 1: Create Infrastructure Setup

#### Part A: Create BeanFactory with DataSource

**File:** `{DB}BeanFactory.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.Operation
import io.airbyte.integrations.destination.{db}.spec.*
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Singleton
import javax.sql.DataSource
import com.zaxxer.hikari.HikariDataSource

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
        // Example (ClickHouse):
        // return ClickHouseDataSource(
        //     "http://${config.hostname}:${config.port}/${config.database}",
        //     Properties().apply {
        //         setProperty("user", config.username)
        //         setProperty("password", config.password)
        //     }
        // )
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

**What this does:**
- **configuration:** Loads config from `--config` file
- **dataSource:** Creates connection pool for `--check` and `--write` operations
- **emptyDataSource:** Dummy DataSource for `--spec` operation (no connection needed)

**Database-specific adjustments:**
- **JDBC (Postgres, MySQL):** Use HikariCP as shown
- **Native clients (ClickHouse, BigQuery):** Replace with native client instantiation

#### Part B: Add Testcontainers Dependency

**File:** Update `build.gradle.kts`

```kotlin
dependencies {
    // Existing dependencies...

    // Testcontainers for automated testing (recommended)
    testImplementation("org.testcontainers:testcontainers:1.19.0")
    testImplementation("org.testcontainers:{db}:1.19.0")  // e.g., postgresql, mysql, clickhouse

    // For databases without specific Testcontainers module:
    // testImplementation("org.testcontainers:jdbc:1.19.0")
}
```

**Check available modules:** https://www.testcontainers.org/modules/databases/

#### Part C: Create Test Configuration with Testcontainers

**File:** `src/test-integration/kotlin/.../component/{DB}TestConfigFactory.kt`

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
        //     .withUsername("test")
        //     .withPassword("test")

        // Example for ClickHouse:
        // val container = ClickHouseContainer("clickhouse/clickhouse-server:latest")
        //     .withDatabaseName("test")
        //     .withUsername("default")
        //     .withPassword("")

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

**Alternative: Environment variables** (for local development with existing database)

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
- ✅ Isolated test environment (no conflicts)
- ✅ Works in CI without setup
- ✅ Reproducible across machines
- ✅ Automatic cleanup
- ✅ No manual database installation

**Validate infrastructure setup:**
```bash
$ ./gradlew :destination-{db}:compileKotlin
```

Expected: BUILD SUCCESSFUL

---

### Database Step 2: Create ColumnUtils (Type Mapping)

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

**Database-specific type mapping:**

| Database | String | Integer | Number | JSON | Timestamp | Nullable |
|----------|--------|---------|--------|------|-----------|----------|
| **Postgres** | TEXT | BIGINT | DECIMAL(38,9) | JSONB | TIMESTAMPTZ | NULL suffix |
| **MySQL** | VARCHAR(65535) | BIGINT | DECIMAL(38,9) | JSON | TIMESTAMP | NULL suffix |
| **Snowflake** | VARCHAR | NUMBER(38,0) | FLOAT | VARIANT | TIMESTAMP_TZ | NULL suffix |
| **ClickHouse** | String | Int64 | Decimal(38,9) | String | DateTime64(3) | Nullable() wrapper |
| **BigQuery** | STRING | INT64 | NUMERIC | JSON | TIMESTAMP | nullable field |

**Adjust toDialectType() for your database** - Use table above as reference.

**Validate compilation:**
```bash
$ ./gradlew :destination-{db}:compileKotlin
```

---

### Database Step 3: Create SqlGenerator (All Operations)

**File:** `client/{DB}SqlGenerator.kt`

**Why implement all operations now?** SQL generation is pure logic with no I/O. All methods follow the same pattern (string building + logging). Natural to write together.

```kotlin
package io.airbyte.integrations.destination.{db}.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Singleton

private val log = KotlinLogging.logger {}

// Extension function for SQL logging
fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

@Singleton
class {DB}SqlGenerator(
    private val columnUtils: {DB}ColumnUtils,
) {

    // ========================================
    // NAMESPACE OPERATIONS
    // ========================================

    fun createNamespace(namespace: String): String {
        // Postgres/MySQL: CREATE SCHEMA
        return "CREATE SCHEMA IF NOT EXISTS ${namespace.quote()}".andLog()

        // Or for databases with CREATE DATABASE:
        // return "CREATE DATABASE IF NOT EXISTS ${namespace.quote()}".andLog()
    }

    fun namespaceExists(namespace: String): String {
        // Postgres/MySQL:
        return """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = '$namespace'
        """.trimIndent().andLog()

        // ClickHouse:
        // return """
        //     SELECT name
        //     FROM system.databases
        //     WHERE name = '$namespace'
        // """.trimIndent().andLog()

        // Or query your DB's system catalog
    }

    // ========================================
    // TABLE OPERATIONS
    // ========================================

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

    // ========================================
    // HELPER METHODS
    // ========================================

    private fun String.quote(): String {
        // Postgres/Snowflake: double quotes
        return "\"$this\""

        // MySQL: backticks
        // return "`$this`"

        // SQL Server: square brackets
        // return "[$this]"
    }

    private fun fullyQualifiedName(tableName: TableName): String {
        return "${tableName.namespace.quote()}.${tableName.name.quote()}"
    }

    companion object {
        private val AIRBYTE_META_COLUMNS = setOf(
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id"
        )
    }
}
```

**Key points:**
- **All operations in one file:** Namespace + table operations use same patterns
- **Always call .andLog():** SQL logging is critical for debugging
- **Database-specific quoting:** Adjust quote() method for your database
- **Metadata columns:** Always included, filtered from user columns

**Validate SQL strings (manual check):**
```bash
# Copy-paste generated SQL to your database console
# Verify syntax is correct for your database
```

**Validate compilation:**
```bash
$ ./gradlew :destination-{db}:compileKotlin
```

---

### Database Step 4: Create Client (All Operations)

**File:** `client/{DB}AirbyteClient.kt`

**Why implement all operations now?** Client just delegates to SqlGenerator + executes. Straightforward pattern repeated for each method.

```kotlin
package io.airbyte.integrations.destination.{db}.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Singleton
import java.sql.SQLException
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class {DB}AirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: {DB}SqlGenerator,
    private val config: {DB}Configuration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    // ========================================
    // NAMESPACE OPERATIONS
    // ========================================

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

    // ========================================
    // TABLE OPERATIONS
    // ========================================

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
            log.debug(e) { "Table ${tableName.toPrettyString()} does not exist. Returning null." }
            null  // Expected - table doesn't exist
        }

    override suspend fun getGenerationId(tableName: TableName): Long =
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
            0L
        }

    // ========================================
    // HELPER METHODS
    // ========================================

    private fun execute(sql: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(sql)
            }
        }
    }

    // ========================================
    // STUB METHODS (Implement in later phases)
    // ========================================

    override suspend fun copyTable(
        columnMapping: ColumnNameMapping,
        source: TableName,
        target: TableName
    ) = TODO("Phase 11: Implement copyTable")

    override suspend fun overwriteTable(
        source: TableName,
        target: TableName
    ) = TODO("Phase 10: Implement overwriteTable")

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnMapping: ColumnNameMapping,
        source: TableName,
        target: TableName
    ) = TODO("Phase 13: Implement upsertTable")

    override suspend fun discoverSchema(tableName: TableName) =
        TODO("Phase 12: Implement discoverSchema")

    override fun computeSchema(
        stream: DestinationStream,
        columnMapping: ColumnNameMapping
    ) = TODO("Phase 12: Implement computeSchema")

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnMapping: ColumnNameMapping
    ) = TODO("Phase 12: Implement ensureSchemaMatches")

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: Collection<Pair<String, io.airbyte.cdk.load.table.ColumnType>>,
        changeset: io.airbyte.cdk.load.table.ColumnChangeset
    ) = TODO("Phase 12: Implement applyChangeset")
}
```

**Key points:**
- **Pattern:** All methods delegate to SqlGenerator, then execute SQL
- **Error handling:** countTable returns null if table doesn't exist (expected, not error)
- **Logging:** Use lazy evaluation `log.debug { }` not `log.debug("")`
- **TODO stubs:** Methods for later phases clearly marked

**Register client in BeanFactory:**

**File:** Update `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun client(
    dataSource: DataSource,
    sqlGenerator: {DB}SqlGenerator,
    config: {DB}Configuration,
): TableOperationsClient {
    return {DB}AirbyteClient(dataSource, sqlGenerator, config)
}
```

**Validate compilation:**
```bash
$ ./gradlew :destination-{db}:compileKotlin
```

Expected: BUILD SUCCESSFUL with no errors

---

### Database Step 5: Implement Test Client (Insert/Read for Verification)

**File:** `src/test-integration/kotlin/.../component/{DB}TestTableOperationsClient.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.table.TableName
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Singleton
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.sql.Types
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
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                // Postgres/MySQL:
                statement.execute("DROP SCHEMA IF EXISTS \"${namespace}\" CASCADE")

                // Or for databases with DROP DATABASE:
                // statement.execute("DROP DATABASE IF EXISTS `${namespace}`")
            }
        }
    }

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
}
```

**What this does:**
- **ping():** Validates connection works
- **dropNamespace():** Cleanup after tests
- **insertRecords():** Insert test data for verification
- **readTable():** Read back data to verify writes worked
- **setParameter():** Convert AirbyteValue types to JDBC types

**For non-JDBC databases:** Replace JDBC code with native client API calls.

---

### Database Step 6: Create Full Test Suite

**File:** `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

**Create test file with ALL tests enabled from the start:**

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

    @Test
    override fun `create and drop namespaces`() {
        super.`create and drop namespaces`()
    }

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
}
```

**What each test validates:**
1. **connect to database:** DataSource works, can execute SELECT 1
2. **create and drop namespaces:** Namespace operations (CREATE/DROP SCHEMA)
3. **create and drop tables:** Table operations (CREATE/DROP TABLE)
4. **insert records:** Test client can insert data, client can create tables
5. **count table rows:** COUNT query works, handles empty and non-empty tables

---

### Database Step 7: Validate Full Implementation

**Run all component tests:**

```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected output:**
```
{DB}TableOperationsTest > connect to database PASSED
{DB}TableOperationsTest > create and drop namespaces PASSED
{DB}TableOperationsTest > create and drop tables PASSED
{DB}TableOperationsTest > insert records PASSED
{DB}TableOperationsTest > count table rows PASSED

SpecTest > spec matches expected PASSED

BUILD SUCCESSFUL in 15s
6 tests, 6 passed
```

**Success criteria (ALL must be true):**
- [ ] All 5 TableOperationsSuite tests show "PASSED"
- [ ] No SQL syntax errors in logs
- [ ] No connection errors
- [ ] Test log shows SQL statements (from .andLog())
- [ ] BUILD SUCCESSFUL

---

**If tests FAIL, debug systematically:**

#### Test 1 fails: "connect to database"
**Symptom:** Connection refused, authentication failed, or timeout

**Check:**
1. Testcontainer started? Look for "Container is started" in logs
2. Connection string correct? Check hostname, port in test config
3. Database initialized? Some databases need init time

**Fix:**
```bash
# Verify container is running
$ docker ps | grep {db}

# Check container logs
$ docker logs <container-id>

# Try manual connection
$ {db-cli} -h localhost -p <port> -U test -d test
```

#### Test 2 fails: "create and drop namespaces"
**Symptom:** SQL syntax error on CREATE SCHEMA or namespace query

**Check:**
1. SQL syntax correct for your database? (SCHEMA vs DATABASE)
2. Quoting correct? (double quotes vs backticks)
3. Information schema query correct?

**Fix:**
- Copy SQL from logs
- Run in database console manually
- Adjust SqlGenerator methods

#### Test 3 fails: "create and drop tables"
**Symptom:** SQL syntax error on CREATE TABLE

**Check:**
1. Column type mapping correct? (toDialectType)
2. Metadata columns use correct types?
3. Quoting in fullyQualifiedName correct?

**Fix:**
- Copy CREATE TABLE SQL from logs
- Verify each column type is valid
- Test in database console

#### Test 4 fails: "insert records"
**Symptom:** SQL syntax error on INSERT or type conversion error

**Check:**
1. setParameter() handles all AirbyteValue types?
2. JSON serialization works for ObjectValue/ArrayValue?
3. Timestamp/Date conversions correct?

**Fix:**
- Add logging to setParameter()
- Verify each type converts correctly
- Test with single record first

#### Test 5 fails: "count table rows"
**Symptom:** COUNT query fails or returns wrong value

**Check:**
1. COUNT SQL syntax correct?
2. Handles empty table (returns 0)?
3. Handles non-existent table (returns null)?

**Fix:**
- Test COUNT with empty table manually
- Verify countTable catches SQLException for missing table

---

**Common issues across all tests:**

**Issue: "No bean of type [TableOperationsClient]"**
```
Fix: Check BeanFactory has @Singleton fun client(...): TableOperationsClient
Verify: ./gradlew :destination-{db}:compileKotlin succeeds
```

**Issue: "TODO not yet implemented"**
```
Symptom: Test calls TODO() stub method
Fix: Verify you implemented all methods (not just namespace or table, but BOTH)
Check: Client has no TODO() in methods called by tests
```

**Issue: SQL logged but not executed**
```
Symptom: .andLog() works but SQL doesn't run
Fix: Verify execute() method actually calls statement.execute(sql)
Check: Add logging after execute to confirm it ran
```

---

✅ **Checkpoint:** Complete TableOperationsClient implementation

**What you've achieved:**
- ✅ DataSource connection working
- ✅ Namespace operations (CREATE/DROP/EXISTS)
- ✅ Table operations (CREATE/DROP/COUNT/getGenerationId)
- ✅ All 5 TableOperationsSuite tests passing
- ✅ Ready for Phase 3 (Write Infrastructure)

**What's NOT done yet (later phases):**
- ❌ Schema evolution (Advanced Phase 1)
- ❌ Upsert/dedupe (Advanced Phase 2)
- ❌ Overwrite/truncate (Write Phase 2)
- ❌ Copy operations (Write Phase 3)
- ❌ Write operations (Write Phase 1+)

---

## Database Phase 2: Check Operation

**Goal:** Implement `--check` operation to validate database connection and permissions

**Why separate phase?** Check is a different component (Checker) with integration test validation. Natural checkpoint after basic operations work.

**Checkpoint:** --check operation works

---

### Database Step 1: Create Checker

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
                // 1. Verify namespace exists or can be created
                client.createNamespace(testNamespace)

                // 2. Create test table with Airbyte metadata columns
                val testStream = createTestStream()
                val columnMapping = ColumnNameMapping(mapOf("test_col" to "test_col"))

                client.createTable(testStream, tableName, columnMapping, replace = false)

                // 3. Verify table was created (count should be 0)
                val count = client.countTable(tableName)
                require(count == 0L) { "Expected empty table, got $count rows" }

            } finally {
                // Always cleanup test table
                client.dropTable(tableName)
            }
        }
    }

    private fun createTestStream(): DestinationStream {
        return DestinationStream(
            descriptor = DestinationStream.Descriptor(
                namespace = config.database,
                name = "test"
            ),
            importType = DestinationStream.ImportType.APPEND,
            schema = ObjectType(
                properties = linkedMapOf(
                    "test_col" to FieldType(StringType, nullable = true)
                )
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 0,
        )
    }
}
```

**What check() does:**
1. Creates (or verifies exists) namespace
2. Creates test table with metadata columns
3. Verifies table creation succeeded (count = 0)
4. Cleans up test table

**Why this validates the connection:**
- Tests database connectivity
- Tests CREATE/DROP permissions
- Tests metadata column types work
- Provides clear error messages if permissions missing

---

### Database Step 2: Create Check Integration Test

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

**What this test does:**
- Spawns real connector process (not mocked)
- Runs `--check` operation with real config
- Verifies CONNECTION_STATUS message returned

**Config file location:** `secrets/config.json` (same as manual testing)

---

### Database Step 3: Validate Check Operation

**Run check integration test:**

```bash
$ ./gradlew :destination-{db}:integrationTestCheckSuccessConfigs
```

**Expected output:**
```
{DB}CheckTest > testSuccessConfigs[0] PASSED

BUILD SUCCESSFUL in 5s
```

**Run full test suite (regression check):**

```bash
$ ./gradlew :destination-{db}:integrationTest
```

**Expected tests passing:**
- `SpecTest > spec matches expected` ✅ (from Phase 1)
- `{DB}CheckTest > testSuccessConfigs[0]` ✅ (new in Phase 3)

**Success criteria:**
- [ ] Check test shows "PASSED"
- [ ] Connector log shows "CONNECTION_STATUS" with "status": "SUCCEEDED"
- [ ] No SQL errors in logs
- [ ] Test table cleaned up (check database - should not exist)

**If check test FAILS:**

**Symptom: "Permission denied" or "Access denied"**
```
Fix: Verify database user has CREATE/DROP privileges
Test: Run CREATE SCHEMA manually with test credentials
```

**Symptom: "Table not created" (count != 0)**
```
Fix: Check CREATE TABLE SQL in logs
Verify: Metadata column types are correct for your database
```

**Symptom: Test table not cleaned up**
```
Fix: Check finally block executes even if test fails
Verify: dropTable() doesn't throw exception
```

---

✅ **Checkpoint:** Database Phase 2 complete - Check operation working

**What you've achieved:**
- ✅ Database Phase 1: Complete TableOperationsClient (5 tests passing)
- ✅ Database Phase 2: Check operation validates connection (1 test passing)
- ✅ Total: 6 integration tests passing
- ✅ Ready for Infrastructure Phase 1: Name Generators

---

## Next Steps

**Continue to:** [3-write-infrastructure.md](./3-write-infrastructure.md)

**What's next:**
- Infrastructure Phase 1: Name generators (TableCatalog dependencies)
- Infrastructure Phase 2: Write operation infrastructure (DI setup)
- Write Phase 1+: Business logic (Writer, Aggregate, InsertBuffer)

**Current progress:**
- ✅ Setup Phase 1: Scaffolding
- ✅ Setup Phase 2: Spec operation
- ✅ Database Phase 1: TableOperationsClient (complete)
- ✅ Database Phase 2: Check operation (complete)
- ⏭️ Infrastructure Phase 1-2: Write operations setup (next guide)
