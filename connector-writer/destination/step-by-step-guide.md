# Step-by-Step Guide: Building a Dataflow CDK Destination Connector

**Summary:** Paint-by-numbers guide to implementing a destination connector. Each phase has clear tasks, code patterns, and test validation. Build incrementally with quick feedback loops. After Phase 1, you have --spec working. After Phase 6, you'll have a working append-only connector. Full feature set complete by Phase 10.

**Prerequisites:**
- Familiarity with Kotlin and your target database
- Understanding of dataflow-cdk.md (architecture overview)
- Database credentials or Testcontainers setup

---

## Phase 0: Scaffolding

**Goal:** Empty project structure that builds

**Checkpoint:** Project compiles

### Step 0.1: Create Directory Structure

```bash
cd airbyte-integrations/connectors
mkdir -p destination-{db}/src/main/kotlin/io/airbyte/integrations/destination/{db}
mkdir -p destination-{db}/src/test/kotlin/io/airbyte/integrations/destination/{db}
mkdir -p destination-{db}/src/test-integration/kotlin/io/airbyte/integrations/destination/{db}
```

**Create subdirectories:**

```bash
cd destination-{db}/src/main/kotlin/io/airbyte/integrations/destination/{db}
mkdir check client config dataflow spec write
mkdir write/load write/transform
```

### Step 0.2: Create gradle.properties with CDK Version Pin

**File:** `destination-{db}/gradle.properties`

```properties
# Pin to latest stable Bulk CDK version
# Check airbyte-cdk/bulk/version.properties for latest
cdkVersion=0.1.76
```

**IMPORTANT:** Always use a pinned version for production connectors.

**When to use `cdkVersion=local`:**
- Only when actively developing CDK features
- For faster iteration when modifying CDK code
- Switch back to pinned version before merging

**To upgrade CDK version later:**
```bash
./gradlew destination-{db}:upgradeCdk --cdkVersion=0.1.76
```

### Step 0.3: Create build.gradle.kts

**File:** `destination-{db}/build.gradle.kts`

**Reference:** `destination-snowflake/build.gradle.kts` or `destination-clickhouse/build.gradle.kts`

```kotlin
plugins {
    id("airbyte-bulk-connector")
}

airbyteBulkConnector {
    core = "load"              // For destinations
    toolkits = listOf("load-db")  // Database toolkit
}

dependencies {
    // Database driver
    implementation("your.database:driver:version")

    // Add other specific dependencies as needed
}
```

**How it works:**
- The `airbyte-bulk-connector` plugin reads `cdkVersion` from `gradle.properties`
- If `cdkVersion=0.1.76`: Resolves Maven artifacts `io.airbyte.bulk-cdk:bulk-cdk-core-load:0.1.76`
- If `cdkVersion=local`: Uses project references `:airbyte-cdk:bulk:core:load`
- Automatically adds CDK dependencies, Micronaut, test fixtures

**No need to manually declare CDK dependencies** - the plugin handles it

### Step 0.4: Create Main Entry Point

**File:** `destination-{db}/src/main/kotlin/.../​{DB}Destination.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.AirbyteDestinationRunner

fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
```

**That's it!** The framework handles everything else.

### Step 0.5: Verify Build

```bash
$ ./gradlew :destination-{db}:build
```

**Expected:** Build succeeds

**Troubleshooting:**
- Missing dependencies? Check `build.gradle.kts`
- Package name mismatches? Verify all files use consistent package
- Micronaut scanning issues? Ensure `@Singleton` annotations present

✅ **Checkpoint Complete:** Project compiles

**You're ready for Phase 1 when:** `./gradlew :destination-{db}:build` succeeds

---

## Phase 1: Spec Operation

**Goal:** Implement --spec operation (returns connector configuration schema)

**Checkpoint:** Spec test passes

### Step 1.1: Understand Configuration Classes

**Two classes work together for configuration:**

| Class | Purpose | Used By |
|-------|---------|---------|
| `{DB}Specification` | Defines UI form schema (what users see) | Spec operation (generates JSON schema) |
| `{DB}Configuration` | Runtime config object (what your code uses) | Check and Write operations |

**Flow:**
```
User fills UI form
  ↓
Platform sends JSON matching Specification schema
  ↓
ConfigurationFactory parses JSON → Configuration object
  ↓
Your code uses Configuration object
```

### Step 1.2: Create Specification Class

**Purpose:** Defines the configuration form users fill in Airbyte UI

**File:** `spec/{DB}Specification.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.Singleton

@Singleton
open class {DB}Specification : ConfigurationSpecification() {
    @get:JsonProperty("hostname")
    @get:JsonPropertyDescription("Hostname of the database server")
    val hostname: String = ""

    @get:JsonProperty("port")
    @get:JsonPropertyDescription("Port of the database server")
    val port: Int = 5432  // Your DB's default port

    @get:JsonProperty("database")
    @get:JsonPropertyDescription("Name of the database")
    val database: String = ""

    @get:JsonProperty("username")
    @get:JsonPropertyDescription("Username for authentication")
    val username: String = ""

    @get:JsonProperty("password")
    @get:JsonPropertyDescription("Password for authentication")
    val password: String = ""
}
```

**Key annotations:**
- `@JsonProperty("field_name")` - Field name in JSON
- `@JsonPropertyDescription("...")` - Help text in UI
- `@JsonSchemaTitle("Title")` - Label in UI (optional, defaults to property name)
- `@JsonSchemaInject(json = """{"airbyte_secret": true}""")` - Mark as secret (passwords, API keys)

### Step 1.3: Create Configuration and Factory

**Purpose:** Runtime configuration object your code actually uses

**File:** `spec/{DB}Configuration.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Singleton

// Runtime configuration (used by your code)
data class {DB}Configuration(
    val hostname: String,
    val port: Int,
    val database: String,
    val username: String,
    val password: String,
) : DestinationConfiguration()

// Factory: Converts Specification → Configuration
@Singleton
class {DB}ConfigurationFactory :
    DestinationConfigurationFactory<{DB}Specification, {DB}Configuration> {

    override fun makeWithoutExceptionHandling(
        pojo: {DB}Specification
    ): {DB}Configuration {
        return {DB}Configuration(
            hostname = pojo.hostname,
            port = pojo.port,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
        )
    }
}
```

**Why two classes?**
- **Specification:** JSON schema annotations, defaults, UI metadata
- **Configuration:** Clean runtime object, validated values, no Jackson overhead
- **Factory:** Validation and transformation layer between them

**Simple rule:**
- Specification = What users configure
- Configuration = What your code uses

### Step 1.4: Create Specification Extension

**Purpose:** Declares what sync modes your connector supports

**File:** `spec/{DB}SpecificationExtension.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.spec

import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}SpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true

    // Optional: Group configuration fields in UI
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("connection", "Connection"),
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}
```

### Step 1.5: Configure Documentation URL

**File:** `src/main/resources/application.yml`

```yaml
airbyte:
  connector:
    metadata:
      documentation-url: 'https://docs.airbyte.com/integrations/destinations/{db}'
```

**Or in build.gradle.kts (alternative):**

```kotlin
airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-db")

    // Optional: override documentation URL
    // documentationUrl = "https://docs.airbyte.com/integrations/destinations/{db}"
}
```

**Default:** If not specified, uses placeholder URL

### Step 1.6: Create Expected Spec Test File

**File:** `src/test-integration/resources/expected-spec-oss.json`

```json
{
  "documentationUrl": "https://docs.airbyte.com/integrations/destinations/{db}",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "{DB} Destination Spec",
    "type": "object",
    "required": [
      "hostname",
      "port",
      "database",
      "username",
      "password"
    ],
    "properties": {
      "hostname": {
        "type": "string",
        "title": "Hostname",
        "description": "Hostname of the database server"
      },
      "port": {
        "type": "integer",
        "title": "Port",
        "description": "Port of the database server"
      },
      "database": {
        "type": "string",
        "title": "Database",
        "description": "Name of the database"
      },
      "username": {
        "type": "string",
        "title": "Username",
        "description": "Username for authentication"
      },
      "password": {
        "type": "string",
        "title": "Password",
        "description": "Password for authentication",
        "airbyte_secret": true
      }
    },
    "groups": [
      {"id": "connection", "title": "Connection"},
      {"id": "advanced", "title": "Advanced"}
    ]
  },
  "supportsIncremental": true,
  "supportsNormalization": false,
  "supportsDBT": false,
  "supported_destination_sync_modes": [
    "overwrite",
    "append",
    "append_dedup"
  ]
}
```

**Note:** This file is a snapshot of expected output. Generate it by:
1. Running spec operation manually
2. Copying output to this file
3. Using it for regression testing

### Step 1.7: Create Spec Test

**File:** `src/test-integration/kotlin/.../spec/{DB}SpecTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.spec

import io.airbyte.cdk.load.spec.SpecTest

class {DB}SpecTest : SpecTest()
```

**What this tests:**
- Spec operation executes without errors
- Returns valid JSON schema
- Matches expected-spec-oss.json (snapshot test)
- If Cloud-specific: Matches expected-spec-cloud.json

### Step 1.8: Generate and Validate Spec

**Run spec operation to generate the JSON schema:**

```bash
$ ./gradlew :destination-{db}:run --args='--spec'
```

**Expected output (stdout):**
```json
{
  "type": "SPEC",
  "spec": {
    "documentationUrl": "https://docs.airbyte.com/integrations/destinations/{db}",
    "connectionSpecification": { ... },
    "supportsIncremental": true,
    "supported_destination_sync_modes": ["overwrite", "append", "append_dedup"]
  }
}
```

**Copy the `spec` object** (not the outer wrapper) to:

```bash
# Create resources directory
mkdir -p src/test-integration/resources

# Manually copy the "spec" portion to this file:
# src/test-integration/resources/expected-spec-oss.json
```

**Tip:** Use `jq` to format: `./gradlew :destination-{db}:run --args='--spec' | jq .spec > expected-spec-oss.json`

### Step 1.9: Run Spec Test

```bash
$ ./gradlew :destination-{db}:integrationTestSpecOss
```

**Expected:**
```
✓ testSpecOss
```

**Troubleshooting:**
- **Spec operation fails:**
  - Check `application.yml` has documentation-url
  - Verify Specification class has proper Jackson annotations
  - Check SpecificationExtension is a `@Singleton`

- **Spec test fails:**
  - Actual spec doesn't match expected-spec-oss.json
  - Run `--spec` manually to see what's generated
  - Update expected-spec-oss.json with correct output
  - Ensure JSON formatting matches (no trailing commas, consistent order)

✅ **Checkpoint Complete:** Spec operation works

**You're ready for Phase 2 when:** `./gradlew :destination-{db}:integrationTestSpecOss` passes

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

## Phase 5: Generation ID Support

**Goal:** Track sync generations for refresh handling

**Checkpoint:** Can retrieve generation IDs

### Step 4.1: Enable Test

**File:** Update `{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `get generation id`() {
    super.`get generation id`()
}
```

### Step 4.2: Validate

```bash
$ ./gradlew :destination-{db}:testComponentGetGenerationId
```

**Expected new passes:**
```
✓ get generation id
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:**
```
✓ connect to database
✓ create and drop namespaces
✓ create and drop tables
✓ insert records
✓ count table rows
✓ get generation id (new)
```

✅ **Checkpoint Complete:** Generation ID tracking works

**You're ready for Phase 5 when:** `get generation id` test passes

---

## Phase 6: Append Mode - First Working Sync

**Goal:** Run a complete sync in append mode

**Checkpoint:** Can sync data end-to-end (simplest mode)

### Step 5.1: Create Name Generators

**File:** `config/{DB}NameGenerators.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.config

import io.airbyte.cdk.load.orchestration.db.*
import io.airbyte.integrations.destination.{db}.spec.{DB}Configuration
import io.micronaut.context.annotation.Singleton

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

// Helper
private fun String.toDbCompatible(): String {
    // Snowflake: uppercase
    return this.uppercase()

    // ClickHouse/Postgres: lowercase or preserve
    return this.lowercase()

    // Or apply database-specific rules (replace special chars, etc.)
}
```

### Step 5.2: Register Name Generators in BeanFactory

**File:** Update `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun tempTableNameGenerator(config: {DB}Configuration): TempTableNameGenerator {
    return DefaultTempTableNameGenerator(
        internalNamespace = config.database  // Or config.internalSchema if you have one
    )
}

// FinalTableNameGenerator and ColumnNameGenerator auto-discovered by Micronaut
```

### Step 5.3: Create Insert Buffer

**File:** `write/load/{DB}InsertBuffer.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

class {DB}InsertBuffer(
    private val tableName: TableName,
    private val client: {DB}AirbyteClient,
    private val flushLimit: Int = 1000,
) {
    private val buffer = mutableListOf<Map<String, AirbyteValue>>()
    private var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        buffer.add(recordFields)
        recordCount++

        if (recordCount >= flushLimit) {
            kotlinx.coroutines.runBlocking { flush() }
        }
    }

    suspend fun flush() {
        if (buffer.isEmpty()) return

        try {
            log.info { "Flushing $recordCount records to ${tableName}..." }

            // Simple multi-row INSERT for now
            // (Optimize in later iterations: CSV staging, COPY, bulk APIs)
            buffer.forEach { record ->
                insertRecord(tableName, record)
            }

            log.info { "Finished flushing $recordCount records" }
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }

    private suspend fun insertRecord(
        tableName: TableName,
        record: Map<String, AirbyteValue>
    ) {
        val columns = record.keys.joinToString(", ") { "\"$it\"" }
        val placeholders = record.keys.joinToString(", ") { "?" }
        val sql = """
            INSERT INTO "${tableName.namespace}"."${tableName.name}" ($columns)
            VALUES ($placeholders)
        """

        client.executeInsert(sql, record.values.toList())
    }
}
```

**Add to Client:**

```kotlin
// In {DB}AirbyteClient.kt
fun executeInsert(sql: String, values: List<AirbyteValue>) {
    dataSource.connection.use { connection ->
        connection.prepareStatement(sql).use { statement ->
            values.forEachIndexed { index, value ->
                setParameter(statement, index + 1, value)
            }
            statement.executeUpdate()
        }
    }
}

private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
    // Same as in TestTableOperationsClient
}
```

### Step 5.4: Create Aggregate

**File:** `dataflow/{DB}Aggregate.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.{db}.write.load.{DB}InsertBuffer

class {DB}Aggregate(
    private val buffer: {DB}InsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
```

### Step 5.5: Create Aggregate Factory

**File:** `dataflow/{DB}AggregateFactory.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.orchestration.db.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.state.StoreKey
import io.airbyte.cdk.load.state.StreamStateStore
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.airbyte.integrations.destination.{db}.write.load.{DB}InsertBuffer
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Singleton

@Factory
class {DB}AggregateFactory(
    private val client: {DB}AirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    @Singleton
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer = {DB}InsertBuffer(
            tableName = tableName,
            client = client,
        )

        return {DB}Aggregate(buffer)
    }
}
```

### Step 5.6: Create Initial Status Gatherer

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

### Step 5.7: Create Column Name Mapper

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

### Step 5.8: Create Writer

**File:** `write/{DB}Writer.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.*
import io.airbyte.cdk.load.state.StreamStateStore
import io.airbyte.cdk.load.table.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}Writer(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val client: {DB}AirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {

    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        // Create all namespaces
        names.values
            .map { it.tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { client.createNamespace(it) }

        // Gather initial state
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val tableNames = names[stream]!!.tableNames
        val realTableName = tableNames.finalTableName!!
        val tempTableName = tempTableNameGenerator.generate(realTableName)
        val columnNameMapping = names[stream]!!.columnNameMapping

        return when (stream.minimumGenerationId) {
            0L -> DirectLoadTableAppendStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                client,  // TableOperationsClient
                client,  // TableSchemaEvolutionClient
                streamStateStore,
            )
            else -> TODO("Implement truncate modes in Phase 6")
        }
    }
}
```

### Step 5.9: Create Checker

**File:** `check/{DB}Checker.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.check

import io.airbyte.cdk.load.check.DestinationCheckerV2
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
        val testNamespace = config.database  // Or config.schema
        val testTable = "_airbyte_connection_test_${UUID.randomUUID()}"

        runBlocking {
            try {
                client.createNamespace(testNamespace)

                // Create simple test stream
                val testStream = createTestStream()
                val tableName = TableName(testNamespace, testTable)
                val columnMapping = createTestColumnMapping()

                client.createTable(testStream, tableName, columnMapping, replace = false)

                val count = client.countTable(tableName)
                require(count == 0L) { "Expected empty table, got $count rows" }

            } finally {
                client.dropTable(TableName(testNamespace, testTable))
            }
        }
    }

    private fun createTestStream(): DestinationStream {
        // Minimal stream for testing
        // See SnowflakeChecker or ClickhouseChecker for example
    }

    private fun createTestColumnMapping(): ColumnNameMapping {
        // Minimal mapping for test
    }
}
```

### Step 5.10: Create WriteOperationV2

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

### Step 5.11: Create Integration Test

**File:** `src/test-integration/kotlin/.../{DB}AppendTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Test
import java.nio.file.Path

class {DB}AppendTest : BasicFunctionalityIntegrationTest() {
    override val configPath: Path = Path.of("secrets/config.json")
    // Or use Testcontainers config

    @Test
    override fun testAppend() {
        super.testAppend()
    }
}
```

### Step 5.12: Validate

```bash
$ ./gradlew :destination-{db}:testComponentGetGenerationId
```

**Expected new passes:**
```
✓ get generation id
```

**Full sync test:**
```bash
$ ./gradlew :destination-{db}:integrationTestAppend
```

**Expected:**
```
✓ testAppend
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:** All 6 component tests pass

✅ **Checkpoint Complete:** First working sync! 🎉

**You're ready for Phase 6 when:** `testAppend()` integration test passes

---

## Phase 7: Overwrite Mode

**Goal:** Support full refresh (replace all data)

**Checkpoint:** Can replace table contents atomically

### Step 6.1: Implement overwriteTable() in SQL Generator

**File:** Update `{DB}SqlGenerator.kt`

```kotlin
fun overwriteTable(source: TableName, target: TableName): List<String> {
    // Option 1: SWAP (Snowflake)
    return listOf(
        "ALTER TABLE ${fullyQualifiedName(target)} SWAP WITH ${fullyQualifiedName(source)}".andLog(),
        "DROP TABLE IF EXISTS ${fullyQualifiedName(source)}".andLog(),
    )

    // Option 2: EXCHANGE (ClickHouse)
    return listOf(
        "EXCHANGE TABLES ${fullyQualifiedName(target)} AND ${fullyQualifiedName(source)}".andLog(),
        "DROP TABLE IF EXISTS ${fullyQualifiedName(source)}".andLog(),
    )

    // Option 3: DROP + RENAME (fallback)
    return listOf(
        "DROP TABLE IF EXISTS ${fullyQualifiedName(target)}".andLog(),
        "ALTER TABLE ${fullyQualifiedName(source)} RENAME TO ${target.name.quote()}".andLog(),
    )
}
```

### Step 6.2: Implement overwriteTable() in Client

**File:** Update `{DB}AirbyteClient.kt`

```kotlin
override suspend fun overwriteTable(
    sourceTableName: TableName,
    targetTableName: TableName
) {
    val statements = sqlGenerator.overwriteTable(sourceTableName, targetTableName)
    statements.forEach { execute(it) }
}
```

### Step 6.3: Update Writer for Truncate Mode

**File:** Update `{DB}Writer.kt`

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    val initialStatus = initialStatuses[stream]!!
    val tableNames = names[stream]!!.tableNames
    val realTableName = tableNames.finalTableName!!
    val tempTableName = tempTableNameGenerator.generate(realTableName)
    val columnNameMapping = names[stream]!!.columnNameMapping

    return when (stream.minimumGenerationId) {
        0L -> DirectLoadTableAppendStreamLoader(
            stream, initialStatus, realTableName, tempTableName,
            columnNameMapping, client, client, streamStateStore
        )
        stream.generationId -> DirectLoadTableAppendTruncateStreamLoader(
            stream, initialStatus, realTableName, tempTableName,
            columnNameMapping, client, client, streamStateStore
        )
        else -> throw SystemErrorException("Hybrid refresh not supported")
    }
}
```

### Step 6.4: Enable Tests

**File:** Update `{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `overwrite tables`() {
    super.`overwrite tables`()
}
```

**File:** Update `{DB}AppendTest.kt` (or create new test file)

```kotlin
@Test
override fun testTruncate() {
    super.testTruncate()
}
```

### Step 6.5: Validate

```bash
$ ./gradlew :destination-{db}:testComponentOverwriteTables
```

**Expected new passes:**
```
✓ overwrite tables
```

**Integration test:**
```bash
$ ./gradlew :destination-{db}:integrationTestTruncate
```

**Expected:**
```
✓ testTruncate
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: All 7 tests pass
Integration: testAppend, testTruncate pass
```

✅ **Checkpoint Complete:** Full refresh mode works

**You're ready for Phase 7 when:** `overwrite tables` and `testTruncate()` pass

---

## Phase 8: Copy Operation

**Goal:** Support table copying (used internally by some modes)

**Checkpoint:** Can copy data between tables

### Step 7.1: Implement copyTable() in SQL Generator

**File:** Update `{DB}SqlGenerator.kt`

```kotlin
fun copyTable(
    columnMapping: ColumnNameMapping,
    source: TableName,
    target: TableName
): String {
    val columnList = columnMapping.values.joinToString(", ") { "\"$it\"" }

    return """
        INSERT INTO ${fullyQualifiedName(target)} ($columnList)
        SELECT $columnList
        FROM ${fullyQualifiedName(source)}
    """.trimIndent().andLog()
}
```

### Step 7.2: Implement copyTable() in Client

**File:** Update `{DB}AirbyteClient.kt`

```kotlin
override suspend fun copyTable(
    columnNameMapping: ColumnNameMapping,
    sourceTableName: TableName,
    targetTableName: TableName
) {
    execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
}
```

### Step 7.3: Enable Test

**File:** Update `{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `copy tables`() {
    super.`copy tables`()
}
```

### Step 7.4: Validate

```bash
$ ./gradlew :destination-{db}:testComponentCopyTables
```

**Expected new passes:**
```
✓ copy tables
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: All 8 tests pass
Integration: testAppend, testTruncate pass
```

✅ **Checkpoint Complete:** Copy operation works

**You're ready for Phase 8 when:** `copy tables` test passes

---

## Phase 9: Schema Evolution

**Goal:** Automatically adapt to schema changes

**Checkpoint:** Can add, drop, and modify columns

### Step 8.1: Implement discoverSchema()

**File:** Update `{DB}AirbyteClient.kt`

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
                    .takeWhile { it != '(' }  // Strip precision
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
- **Snowflake:** `DESCRIBE TABLE`
- **Postgres/MySQL:** `information_schema.columns`
- **ClickHouse:** Client API `getTableSchema()` or `system.columns`

### Step 8.2: Implement computeSchema()

**File:** Update `{DB}AirbyteClient.kt`

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

### Step 8.3: Implement alterTable() - ADD COLUMN

**File:** Update `{DB}SqlGenerator.kt`

```kotlin
fun alterTable(
    tableName: TableName,
    columnsToAdd: Map<String, ColumnType>,
    columnsToDrop: Map<String, ColumnType>,
    columnsToChange: Map<String, ColumnTypeChange>,
): Set<String> {
    val statements = mutableSetOf<String>()

    // ADD COLUMN (implement first - simplest)
    columnsToAdd.forEach { (name, type) ->
        statements.add(
            "ALTER TABLE ${fullyQualifiedName(tableName)} ADD COLUMN \"$name\" ${type.type}".andLog()
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
        // See Step 8.4 for implementation
    }

    return statements
}
```

### Step 8.4: Implement alterTable() - MODIFY COLUMN

**Add to alterTable():**

```kotlin
columnsToChange.forEach { (name, typeChange) ->
    when {
        // Safe: NOT NULL → NULL
        !typeChange.originalType.nullable && typeChange.newType.nullable -> {
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} ALTER COLUMN \"$name\" DROP NOT NULL".andLog()
            )
        }

        // Unsafe: Type change - use temp column approach
        typeChange.originalType.type != typeChange.newType.type -> {
            val tempColumn = "${name}_${UUID.randomUUID()}"

            // 1. Add temp
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} ADD COLUMN \"$tempColumn\" ${typeChange.newType.type}".andLog()
            )

            // 2. Cast and copy
            statements.add(
                "UPDATE ${fullyQualifiedName(tableName)} SET \"$tempColumn\" = CAST(\"$name\" AS ${typeChange.newType.type})".andLog()
            )

            // 3. Rename original to backup
            val backupColumn = "${tempColumn}_backup"
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

        // Unsafe: NULL → NOT NULL (skip)
        else -> {
            log.info { "Skipping change from nullable to non-nullable for column $name" }
        }
    }
}
```

**Alternative: Table Recreation (ClickHouse pattern for PK changes):**

See `implementation-reference.md` for full recreation approach

### Step 8.5: Implement applyChangeset()

**File:** Update `{DB}AirbyteClient.kt`

```kotlin
override suspend fun applyChangeset(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    tableName: TableName,
    expectedColumns: TableColumns,
    columnChangeset: ColumnChangeset,
) {
    if (columnChangeset.isNoop()) return

    log.info { "Summary of table alterations:" }
    log.info { "Added columns: ${columnChangeset.columnsToAdd}" }
    log.info { "Dropped columns: ${columnChangeset.columnsToDrop}" }
    log.info { "Modified columns: ${columnChangeset.columnsToChange}" }

    val statements = sqlGenerator.alterTable(
        tableName,
        columnChangeset.columnsToAdd,
        columnChangeset.columnsToDrop,
        columnChangeset.columnsToChange,
    )

    statements.forEach { execute(it) }
}
```

### Step 8.6: Implement ensureSchemaMatches()

**File:** Update `{DB}AirbyteClient.kt`

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
        applyChangeset(stream, columnNameMapping, tableName, expectedSchema.columns, changeset)
    }
}
```

### Step 8.7: Add Schema Evolution Test

**File:** Update integration test

```kotlin
@Test
override fun testAppendSchemaEvolution() {
    super.testAppendSchemaEvolution()
}
```

### Step 8.8: Validate

```bash
$ ./gradlew :destination-{db}:integrationTestAppendSchemaEvolution
```

**Expected new passes:**
```
✓ testAppendSchemaEvolution
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: All 8 tests pass
Integration: testAppend, testTruncate, testAppendSchemaEvolution pass
```

✅ **Checkpoint Complete:** Schema evolution works

**You're ready for Phase 9 when:** `testAppendSchemaEvolution()` passes

---

## Phase 10: Dedupe Mode

**Goal:** Support primary key deduplication

**Checkpoint:** Can deduplicate by primary key with "last write wins"

### Step 9.1: Implement upsertTable() in SQL Generator

**Option A: MERGE Statement (Snowflake, SQL Server, BigQuery)**

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

    // Deduplication CTE
    val dedupCte = if (pkColumns.isNotEmpty()) {
        val cursorColumn = if (importType.cursor.isNotEmpty()) {
            columnNameMapping[importType.cursor.first()]!!
        } else {
            "_airbyte_extracted_at"
        }

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
        "SELECT * FROM ${fullyQualifiedName(source)}"
    }

    // Primary key match condition
    val pkMatch = pkColumns.joinToString(" AND ") { col ->
        """(target."$col" = source."$col" OR (target."$col" IS NULL AND source."$col" IS NULL))"""
    }

    // Cursor comparison (for UPDATE condition)
    val cursorComparison = if (importType.cursor.isNotEmpty()) {
        val cursor = columnNameMapping[importType.cursor.first()]!!
        """
        (
          target."$cursor" < source."$cursor"
          OR (target."$cursor" = source."$cursor" AND target."_airbyte_extracted_at" < source."_airbyte_extracted_at")
          OR (target."$cursor" IS NULL AND source."$cursor" IS NOT NULL)
        )
        """
    } else {
        """target."_airbyte_extracted_at" < source."_airbyte_extracted_at""""
    }

    // Column assignments for UPDATE
    val columnAssignments = allColumns.joinToString(",\n  ") { col ->
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

    val columnList = allColumns.joinToString(", ") { "\"$it\"" }
    val updateAssignments = allColumns
        .filter { it !in pkColumns }  // Don't update PK
        .joinToString(", ") { "\"$it\" = EXCLUDED.\"$it\"" }

    // 1. Dedupe in temp table first
    val dedupSql = """
        CREATE TEMP TABLE deduped AS
        SELECT * FROM (
          SELECT *, ROW_NUMBER() OVER (
            PARTITION BY ${pkColumns.joinToString(", ") { "\"$it\"" }}
            ORDER BY "_airbyte_extracted_at" DESC
          ) AS rn
          FROM ${fullyQualifiedName(source)}
        ) WHERE rn = 1
    """.trimIndent().andLog()

    // 2. Upsert
    val upsertSql = """
        INSERT INTO ${fullyQualifiedName(target)} ($columnList)
        SELECT $columnList FROM deduped
        ON CONFLICT (${pkColumns.joinToString(", ") { "\"$it\"" }})
        DO UPDATE SET $updateAssignments
    """.trimIndent().andLog()

    // 3. Cleanup
    val cleanupSql = "DROP TABLE deduped".andLog()

    return listOf(dedupSql, upsertSql, cleanupSql)
}
```

**Option C: Separate DELETE + INSERT (fallback)**

```kotlin
fun upsertTable(...): List<String> {
    // 1. Dedupe
    // 2. Delete existing records with matching PKs
    val deleteSql = """
        DELETE FROM ${fullyQualifiedName(target)}
        WHERE (${pkColumns.joinToString(", ") { "\"$it\"" }})
        IN (SELECT ${pkColumns.joinToString(", ") { "\"$it\"" }} FROM deduped)
    """.trimIndent().andLog()

    // 3. Insert all from deduped
    val insertSql = """
        INSERT INTO ${fullyQualifiedName(target)}
        SELECT * FROM deduped
    """.trimIndent().andLog()

    return listOf(dedupCte, deleteSql, insertSql, cleanup)
}
```

### Step 9.2: Implement upsertTable() in Client

**File:** Update `{DB}AirbyteClient.kt`

```kotlin
override suspend fun upsertTable(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    sourceTableName: TableName,
    targetTableName: TableName
) {
    val sql = sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)

    // Single statement (MERGE)
    execute(sql)

    // Or multiple statements (INSERT ON CONFLICT, DELETE+INSERT)
    // sql.forEach { execute(it) }
}
```

### Step 9.3: Update Writer for Dedupe Mode

**File:** Update `{DB}Writer.kt`

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    val initialStatus = initialStatuses[stream]!!
    val tableNames = names[stream]!!.tableNames
    val realTableName = tableNames.finalTableName!!
    val tempTableName = tempTableNameGenerator.generate(realTableName)
    val columnNameMapping = names[stream]!!.columnNameMapping

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

### Step 9.4: Enable Tests

**File:** Update `{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `upsert tables`() {
    super.`upsert tables`()
}
```

**File:** Update integration test

```kotlin
@Test
override fun testDedupe() {
    super.testDedupe()
}
```

### Step 9.5: Validate

```bash
$ ./gradlew :destination-{db}:testComponentUpsertTables
```

**Expected new passes:**
```
✓ upsert tables
```

**Integration test:**
```bash
$ ./gradlew :destination-{db}:integrationTestDedupe
```

**Expected:**
```
✓ testDedupe
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: All 9 tests pass
Integration: testAppend, testTruncate, testAppendSchemaEvolution, testDedupe pass
```

✅ **Checkpoint Complete:** Full connector functionality! 🎉

**You're ready for Phase 10 when:** All core tests pass

---

## Phase 11: CDC Support (Optional)

**Goal:** Handle source deletions

**Checkpoint:** Can process CDC deletion events

### Step 10.1: Add CDC Configuration

**File:** Update `{DB}Specification.kt`

```kotlin
@get:JsonProperty("cdc_deletion_mode")
@get:JsonPropertyDescription(
    """Whether to execute CDC deletions as hard deletes (propagate source deletions)
    or soft deletes (leave tombstone record). Defaults to hard deletes."""
)
val cdcDeletionMode: CdcDeletionMode? = null

enum class CdcDeletionMode(@get:JsonValue val value: String) {
    HARD_DELETE("Hard delete"),
    SOFT_DELETE("Soft delete"),
}
```

**File:** Update `{DB}Configuration.kt`

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

### Step 10.2: Add CDC Logic to upsertTable()

**File:** Update `{DB}SqlGenerator.kt`

```kotlin
fun upsertTable(...): String {
    val hasCdc = stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)
    val isHardDelete = config.cdcDeletionMode == CdcDeletionMode.HARD_DELETE

    val cdcDeleteClause = if (hasCdc && isHardDelete) {
        """
        WHEN MATCHED AND source."_ab_cdc_deleted_at" IS NOT NULL
             AND $cursorComparison THEN DELETE
        """
    } else {
        ""
    }

    val cdcSkipInsertClause = if (hasCdc && isHardDelete) {
        "AND source.\"_ab_cdc_deleted_at\" IS NULL"
    } else {
        ""
    }

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
- DELETE clause must come **before** UPDATE
- Must check cursor (only delete if deletion is newer)
- Skip INSERT for deleted records
- Soft delete: No special clauses (just upsert the deletion record)

### Step 10.3: Test CDC

**File:** Integration test (already in BasicFunctionalityIntegrationTest)

Tests automatically run if you configure:

```kotlin
override val dedupBehavior = DedupBehavior(
    DedupBehavior.CdcDeletionMode.HARD_DELETE
)
```

### Step 10.4: Validate

```bash
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
✓ testAppend
✓ testTruncate
✓ testAppendSchemaEvolution
✓ testDedupe
✓ CDC tests (automatic in testDedupe if dedupBehavior configured)
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:** All tests pass

✅ **Checkpoint Complete:** Full CDC support

---

## Phase 12: Optimization & Polish

**Goal:** Production-ready performance

**Not strictly required for functionality, but recommended**

### Step 11.1: Optimize Insert Buffer

**Current:** Simple single-row inserts (slow for large datasets)

**Optimizations:**

**Option A: Staging Files (Snowflake pattern)**

```kotlin
class {DB}InsertBuffer(
    private val tableName: TableName,
    private val client: {DB}AirbyteClient,
) {
    private var csvWriter: CsvWriter? = null
    private var csvFilePath: Path? = null
    private var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (csvWriter == null) {
            csvFilePath = Files.createTempFile("airbyte_", ".csv.gz")
            csvWriter = CsvWriter(GZIPOutputStream(csvFilePath!!.toFile().outputStream()))
        }

        csvWriter!!.writeRecord(recordFields)
        recordCount++
    }

    suspend fun flush() {
        csvFilePath?.let { filePath ->
            try {
                csvWriter?.close()

                // Stage file
                client.putInStage(tableName, filePath)

                // Bulk load
                client.copyFromStage(tableName, filePath.fileName.toString())

                log.info { "Flushed $recordCount records via staging" }
            } finally {
                filePath.deleteIfExists()
                csvWriter = null
                csvFilePath = null
                recordCount = 0
            }
        }
    }
}
```

**Option B: COPY FROM STDIN (Postgres)**

```kotlin
suspend fun flush() {
    if (buffer.isEmpty()) return

    val copyManager = CopyManager(connection as BaseConnection)
    val csvData = buffer.joinToString("\n") { record ->
        record.values.joinToString(",") { formatCsvValue(it) }
    }

    val sql = "COPY ${tableName} FROM STDIN WITH (FORMAT CSV)"
    copyManager.copyIn(sql, StringReader(csvData))

    buffer.clear()
}
```

**Option C: Batch Prepared Statements**

```kotlin
suspend fun flush() {
    if (buffer.isEmpty()) return

    dataSource.connection.use { connection ->
        val sql = "INSERT INTO $tableName VALUES (${placeholders})"
        connection.prepareStatement(sql).use { statement ->
            buffer.forEach { record ->
                record.values.forEachIndexed { index, value ->
                    setParameter(statement, index + 1, value)
                }
                statement.addBatch()
            }
            statement.executeBatch()
        }
    }

    buffer.clear()
}
```

### Step 11.2: Add Compression (if using staging)

```kotlin
// GZIP compression
val outputStream = GZIPOutputStream(FileOutputStream(csvFile))

// LZ4 compression (ClickHouse)
val outputStream = LZ4FrameOutputStream(FileOutputStream(file))
```

### Step 11.3: Performance Testing

**Test with large datasets:**

```kotlin
@Test
fun testLargeDataset() {
    val largeRecordSet = generateRecords(count = 100_000)
    runSync(config, stream, largeRecordSet)

    val finalCount = client.countTable(tableName)
    assertEquals(100_000, finalCount)
}
```

**Measure:**
- Records per second
- Memory usage
- Temp file sizes
- Network transfer (if staging)

---

## Testing Strategy Summary

### Test Pyramid

```
Integration Tests (BasicFunctionalityIntegrationTest)
  ├─ testAppend()
  ├─ testTruncate()
  ├─ testAppendSchemaEvolution()
  └─ testDedupe() (includes CDC)

Component Tests (TableOperationsSuite)
  ├─ connect to database
  ├─ create and drop namespaces
  ├─ create and drop tables
  ├─ insert records
  ├─ count table rows
  ├─ get generation id
  ├─ overwrite tables
  ├─ copy tables
  └─ upsert tables

Unit Tests
  ├─ SQL Generator tests (no database)
  ├─ Configuration Factory tests
  └─ Column Utils tests
```

### Validation Commands at Each Phase

| Phase | New Tests | Full Suite |
|-------|-----------|------------|
| 0 | `./gradlew :destination-{db}:build` | N/A |
| 1 | `testComponentConnectToDatabase` | `componentTest` |
| 2 | `testComponentCreateAndDropNamespaces` | `componentTest` |
| 3 | `testComponentCreateAndDropTables`, `testComponentInsertRecords`, `testComponentCountTableRows` | `componentTest` |
| 4 | `testComponentGetGenerationId` | `componentTest` |
| 5 | `integrationTestAppend` | `componentTest` + `integrationTest` |
| 6 | `testComponentOverwriteTables`, `integrationTestTruncate` | `componentTest` + `integrationTest` |
| 7 | `testComponentCopyTables` | `componentTest` + `integrationTest` |
| 8 | `integrationTestAppendSchemaEvolution` | `componentTest` + `integrationTest` |
| 9 | `testComponentUpsertTables`, `integrationTestDedupe` | `componentTest` + `integrationTest` |
| 10 | Automatic in dedupe tests | `componentTest` + `integrationTest` |

---

## Troubleshooting Guide

### Common Issues by Phase

**Phase 1: Can't connect**
- Check hostname/port in config
- Verify database is running
- Check firewall rules
- Verify credentials

**Phase 2: Can't create namespace**
- Check permissions: `GRANT CREATE ON DATABASE`
- Verify SQL syntax for your database
- Check if namespace already exists

**Phase 3: Table creation fails**
- Check column type mapping
- Verify quoting (quotes, backticks, brackets)
- Check for reserved keywords
- Validate NOT NULL constraints

**Phase 5: Integration test fails**
- Check all components registered in BeanFactory
- Verify ColumnNameMapper uses TableCatalog
- Check InsertBuffer writes to correct table from streamStateStore
- Validate Aggregate delegates to buffer

**Phase 8: Schema evolution fails**
- Verify discoverSchema() filters Airbyte columns
- Check type comparison (strip precision)
- Validate ALTER TABLE syntax
- Test with simple schema change first (ADD COLUMN)

**Phase 9: Dedupe fails**
- Verify primary key extraction
- Check MERGE/UPSERT syntax
- Validate cursor comparison logic
- Test with simple PK first (single column)

### Debug Checklist

- [ ] Check logs for generated SQL
- [ ] Verify column name mapping (case sensitivity)
- [ ] Run component tests individually
- [ ] Check database error messages
- [ ] Verify table exists/doesn't exist as expected
- [ ] Check for null values in PK columns
- [ ] Validate generation IDs are set correctly

---

## Next Steps After Completion

### Production Readiness

- [ ] Add comprehensive error messages
- [ ] Implement performance optimizations (staging, compression)
- [ ] Add connection pooling configuration
- [ ] Add timeout configuration
- [ ] Handle all database-specific edge cases
- [ ] Add logging throughout
- [ ] Document database-specific requirements

### Advanced Features

- [ ] Support for database-specific types (arrays, JSON variants)
- [ ] Custom transformation logic
- [ ] Advanced schema evolution (rename columns, complex types)
- [ ] Soft delete mode for CDC
- [ ] Performance tuning (batch sizes, parallelism)

### Documentation

- [ ] Add connector README with setup instructions
- [ ] Document configuration options
- [ ] Add troubleshooting guide
- [ ] Document performance characteristics
- [ ] Add example configurations

---

## Time Estimates

| Phase | Tasks | Estimated Time | Cumulative |
|-------|-------|----------------|------------|
| 0. Scaffolding | Setup project structure | 1-2 hours | 2h |
| 1. Connectivity | Connection setup | 1-2 hours | 4h |
| 2. Namespaces | Create/drop schemas | 1-2 hours | 6h |
| 3. Tables | CRUD operations | 2-3 hours | 9h |
| 4. Generation IDs | Track generations | 0.5 hour | 9.5h |
| 5. Append Mode | First working sync | 3-4 hours | 13.5h |
| 6. Overwrite | Table replacement | 1-2 hours | 15.5h |
| 7. Copy | Copy operation | 0.5-1 hour | 16.5h |
| 8. Schema Evolution | Adapt to changes | 2-3 hours | 19.5h |
| 9. Dedupe | Primary key handling | 3-4 hours | 23.5h |
| 10. CDC (optional) | Deletion handling | 1-2 hours | 25.5h |
| 11. Optimization | Performance tuning | 4-8 hours | 33.5h |

**Total:** ~3-5 days for experienced developer

**Minimum viable:** Through Phase 9 (~24 hours)

---

## Success Criteria

### Phase 5 Success: Working Connector (Append Only)
```bash
$ ./gradlew :destination-{db}:integrationTestAppend
✓ testAppend
```
**Can:** Sync data in append mode, handle schema evolution

### Phase 9 Success: Full-Featured Connector
```bash
$ ./gradlew :destination-{db}:integrationTest
✓ testAppend
✓ testTruncate
✓ testAppendSchemaEvolution
✓ testDedupe
```
**Can:** All sync modes, schema evolution, deduplication

### Production Ready
```bash
$ ./gradlew :destination-{db}:test :destination-{db}:componentTest :destination-{db}:integrationTest
```
**All tests pass:** Unit + Component + Integration

---

## Quick Reference: What to Implement Each Phase

| Phase | SQL Generator | Client | Test Client | Other |
|-------|---------------|--------|-------------|-------|
| 0 | - | - | - | Config, BeanFactory, entry point |
| 1 | - | - | `ping()` | DataSource setup |
| 2 | `createNamespace()` | `createNamespace()`, `namespaceExists()` | `dropNamespace()` | - |
| 3 | `createTable()`, `dropTable()`, `countTable()`, `getGenerationId()` | Same + `tableExists()`, `getGenerationId()` | `insertRecords()`, `readTable()` | ColumnUtils |
| 4 | ✓ (done in Phase 3) | ✓ (done in Phase 3) | - | - |
| 5 | - | - | - | InsertBuffer, Aggregate, Writer, Checker, NameGenerators |
| 6 | `overwriteTable()` | `overwriteTable()` | - | Update Writer |
| 7 | `copyTable()` | `copyTable()` | - | - |
| 8 | `alterTable()` | `discoverSchema()`, `computeSchema()`, `ensureSchemaMatches()`, `applyChangeset()` | - | - |
| 9 | `upsertTable()` | `upsertTable()` | - | Update Writer |
| 10 | Update `upsertTable()` with CDC | - | - | Update Configuration |

**Core effort:** Phases 3, 5, 8, 9 (SQL generation, buffering, schema evolution, deduplication)
