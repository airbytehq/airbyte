# Step-by-Step Guide: Building a Dataflow CDK Destination Connector

**Summary:** Paint-by-numbers guide to implementing a destination connector. 14 phases (0-13) with clear tasks, code patterns, and test validation. Build incrementally with quick feedback loops. After Phase 1, --spec works. After Phase 5, --check works. After Phase 7, you have a working append-only connector. Full feature set by Phase 11.

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

### Step 0.4: Create metadata.yaml

**File:** `destination-{db}/metadata.yaml`

```yaml
data:
  connectorType: destination
  connectorSubtype: database
  dockerImageTag: 0.1.0
  dockerRepository: airbyte/destination-{db}
  documentationUrl: https://docs.airbyte.com/integrations/destinations/{db}
  githubIssueLabel: destination-{db}
  icon: {db}.svg  # Add icon file to src/main/resources
  license: ELv2
  name: {Database Name}

  connectorBuildOptions:
    # Use latest Java connector base image
    # Find latest at: https://hub.docker.com/r/airbyte/java-connector-base/tags
    baseImage: docker.io/airbyte/java-connector-base:2.0.3@sha256:119b8506bca069bbc8357a275936c7e2b0994e6947b81f1bf8d6ce9e16db7d47

  connectorIPCOptions:
    dataChannel:
      version: "0.0.2"
      supportedSerialization: ["JSONL", "PROTOBUF"]
      supportedTransport: ["SOCKET", "STDIO"]

  registryOverrides:
    oss:
      enabled: true
    cloud:
      enabled: false  # Set true when ready for Airbyte Cloud

  releaseStage: alpha  # alpha → beta → generally_available
  supportLevel: community
  tags:
    - language:java

  connectorTestSuitesOptions:
    - suite: unitTests
    - suite: integrationTests

metadataSpecVersion: "1.0"
```

**Key fields:**
- `dockerRepository`: Full image name (e.g., `airbyte/destination-{db}`)
- `dockerImageTag`: Version (start with `0.1.0`)
- `baseImage`: Java connector base image (with digest for reproducibility)
- `releaseStage`: Start with `alpha`, promote to `beta` → `generally_available`

**To find latest base image:**
```bash
# Check what other connectors use
grep "baseImage:" airbyte-integrations/connectors/destination-*/metadata.yaml | sort | uniq -c | sort -rn | head -3
```

### Step 0.5: Configure Docker Build in build.gradle.kts

**File:** Update `destination-{db}/build.gradle.kts`

```kotlin
plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")              // Docker build support
    id("airbyte-connector-docker-convention")   // Reads metadata.yaml
}

airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-db")
}

application {
    mainClass = "io.airbyte.integrations.destination.{db}.{DB}DestinationKt"

    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0"
    )
}

dependencies {
    // Database driver
    implementation("your.database:driver:version")
}
```

**What the plugins do:**
- `io.airbyte.gradle.docker`: Provides Docker build tasks
- `airbyte-connector-docker-convention`: Reads metadata.yaml, generates build args

### Step 0.6: Create Main Entry Point

**File:** `destination-{db}/src/main/kotlin/.../​{DB}Destination.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.AirbyteDestinationRunner

fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
```

**That's it!** The framework handles everything else.

### Step 0.7: Verify Build

```bash
$ ./gradlew :destination-{db}:build
```

**Expected:** Build succeeds

**Troubleshooting:**
- Missing dependencies? Check `build.gradle.kts`
- Package name mismatches? Verify all files use consistent package
- Micronaut scanning issues? Ensure `@Singleton` annotations present
- metadata.yaml syntax errors? Validate YAML format

### Step 0.8: Create application-connector.yml

**File:** `src/main/resources/application-connector.yml`

```yaml
# This file is loaded by the connector at runtime (in Docker)
# The platform may override these via environment variables

airbyte:
  destination:
    core:
      # Default type handling
      types:
        unions: DEFAULT
      # Data channel configuration (required)
      data-channel:
        medium: STDIO  # STDIO or SOCKET (platform sets this)
        format: JSONL  # JSONL or PROTOBUF
      # Namespace mapping (required)
      mappers:
        namespace-mapping-config-path: ""  # Empty = no custom mapping (identity)
      # File transfer (required)
      file-transfer:
        enabled: false  # true for cloud storage destinations, false for databases

# Reduce noise in logs
logger:
  levels:
    com.zaxxer.hikari: ERROR
    com.zaxxer.hikari.pool: ERROR
```

**Critical:** Without this file, the connector will crash with DI errors:
```
Failed to inject value for parameter [dataChannelMedium]
Failed to inject value for parameter [namespaceMappingConfigPath]
Failed to inject value for parameter [fileTransferEnabled]
```

**All required properties:**
- ✅ `types.unions`: How to handle union types
- ✅ `data-channel.medium`: STDIO or SOCKET
- ✅ `data-channel.format`: JSONL or PROTOBUF
- ✅ `mappers.namespace-mapping-config-path`: Namespace mapping file path (empty for identity)
- ✅ `file-transfer.enabled`: Whether connector transfers files (false for databases)

### Step 0.9: Build Docker Image

```bash
$ ./gradlew :destination-{db}:assemble
```

**What this does:**
1. Compiles code
2. Runs unit tests
3. Creates distribution TAR
4. Builds Docker image (includes application-connector.yml)

**Expected output:**
```
BUILD SUCCESSFUL
...
> Task :airbyte-integrations:connectors:destination-{db}:dockerBuildx
Building image: airbyte/destination-{db}:0.1.0
```

**Verify image was created:**
```bash
$ docker images | grep destination-{db}
```

**Expected:**
```
airbyte/destination-{db}    0.1.0    abc123def456    2 minutes ago    500MB
```

✅ **Checkpoint Complete:** Docker container builds

**You're ready for Phase 1 when:**
- `./gradlew :destination-{db}:build` succeeds
- `./gradlew :destination-{db}:assemble` creates Docker image

**Note:** Full Docker validation (--spec, --check, --write) will be tested in later phases
with proper integration tests, not manual commands.

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
  destination:
    core:
      data-channel:
        medium: STDIO  # Default for local testing (platform sets this at runtime)
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

## Phase 6: Name Generators & TableCatalog DI

**Goal:** Create name generator beans required for TableCatalog instantiation

**Checkpoint:** Compilation succeeds without DI errors

**📋 Dependency Context:** TableCatalog (auto-instantiated by CDK) requires these three @Singleton beans:
- RawTableNameGenerator
- FinalTableNameGenerator
- ColumnNameGenerator

Without these beans, you'll get **"Error instantiating TableCatalog"** or **"No bean of type [FinalTableNameGenerator]"** errors in Phase 7 write tests.

### Why This Phase Exists (NEW in V2)

⚠️ **CRITICAL:** In V1, name generators were introduced in Phase 7 alongside Writer/Aggregate/Buffer, causing DI errors when testing write initialization.

**V2 approach:** Create name generators NOW as pure infrastructure, before implementing any write logic. This ensures TableCatalog can instantiate when write operation starts.

**Think of it as:** "Building the foundation before adding the house"

### Step 6.1: Create RawTableNameGenerator

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

### Step 6.2: Create FinalTableNameGenerator

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

### Step 6.3: Create ColumnNameGenerator

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

### Step 6.4: Add Name Transformation Helper

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

### Step 6.5: Register TempTableNameGenerator in BeanFactory

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

### Step 6.6: Verify Compilation

```bash
$ ./gradlew :destination-{db}:compileKotlin
```

**Expected:**
```
BUILD SUCCESSFUL
```

**If you see DI errors at this point:**
- Check all three classes have `@Singleton` annotation
- Verify package name matches your connector structure
- Ensure classes implement correct interfaces:
  - `RawTableNameGenerator` (from `io.airbyte.cdk.load.orchestration.db`)
  - `FinalTableNameGenerator` (from `io.airbyte.cdk.load.orchestration.db`)
  - `ColumnNameGenerator` (from `io.airbyte.cdk.load.orchestration.db`)

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: 5 tests pass (Phases 2-5)
Integration: testSpecOss, testSuccessConfigs pass
```

✅ **Checkpoint Complete:** Name generators registered

**Exit Criteria:**
- ✅ `./gradlew :destination-{db}:compileKotlin` succeeds
- ✅ All three name generator classes have `@Singleton` annotation
- ✅ TempTableNameGenerator bean registered in BeanFactory
- ✅ No "No bean of type [FinalTableNameGenerator]" errors

**You're ready for Phase 7 when:** Compilation succeeds without DI errors

---

## Phase 7: Write Operation Infrastructure

**Goal:** Create write operation infrastructure beans (no business logic yet)

**Checkpoint:** Write operation initializes with real catalog (no DI errors)

**📋 Dependency Context:** This phase creates PURE INFRASTRUCTURE:
- WriteOperationV2 (enables --write command)
- DatabaseInitialStatusGatherer (checks existing tables before write)
- ColumnNameMapper (maps column names)

**NO business logic** (Writer/Aggregate/Buffer come in Phase 8)

### Why This Phase Exists (NEW in V2)

⚠️ **CRITICAL:** In V1, WriteOperationV2 was introduced late in Phase 7 (Step 7.9), but it's REQUIRED for write tests to run.

**V2 approach:** Create WriteOperationV2 and supporting infrastructure NOW, test that write operation can INITIALIZE (not write data yet), then add business logic in Phase 8.

**Key insight:** Separate infrastructure DI from business logic DI to catch errors incrementally.

### Step 7.1: Create WriteOperationV2

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

### Step 7.2: Create DatabaseInitialStatusGatherer

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

### Step 7.3: Register DatabaseInitialStatusGatherer in BeanFactory

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

### Step 7.4: Create ColumnNameMapper

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

### Step 7.5: Register AggregatePublishingConfig in BeanFactory

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

### Step 7.6: Create WriteInitializationTest

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

### Step 7.6: Create Test Config File

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

### Step 7.7: Validate WriteInitializationTest

```bash
$ ./gradlew :destination-{db}:integrationTestWriterCanBeInstantiatedWithRealCatalog
```

**Expected:**
```
✓ writer can be instantiated with real catalog
```

**This validates:**
- ✅ RawTableNameGenerator exists and has @Singleton
- ✅ FinalTableNameGenerator exists and has @Singleton
- ✅ ColumnNameGenerator exists and has @Singleton
- ✅ WriteOperationV2 exists (enables --write)
- ✅ DatabaseInitialStatusGatherer bean registered
- ✅ ColumnNameMapper exists and has @Singleton
- ✅ TableCatalog can instantiate with real catalog parsing

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

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: 5 tests pass (Phases 2-5)
Integration: testSpecOss, testSuccessConfigs, writer can be instantiated pass
```

✅ **Checkpoint Complete:** Write operation infrastructure exists

**Exit Criteria:**
- ✅ WriteOperationV2 created with @Primary @Singleton
- ✅ DatabaseInitialStatusGatherer class created
- ✅ DatabaseInitialStatusGatherer bean registered in BeanFactory
- ✅ ColumnNameMapper created with @Singleton
- ✅ WriteInitializationTest passes (writer can be instantiated)
- ✅ No DI errors when write operation initializes

**You're ready for Phase 8 when:** WriteInitializationTest passes

---

## Phase 8: Writer & Append Mode (Business Logic)

**Goal:** Implement actual data writing (Writer, Aggregate, InsertBuffer)

**Checkpoint:** Can write one record end-to-end

**📋 Dependency Context:** Now that infrastructure exists (Phases 6-7), add business logic:
- InsertBuffer (accumulates and flushes records to database)
- Aggregate (processes transformed records)
- AggregateFactory (creates Aggregate instances)
- Writer (orchestrates setup and creates StreamLoaders)

**Key insight:** Infrastructure DI (Phase 7) is separate from business logic DI (Phase 8).
Phase 7 validates "can we start?" Phase 8 validates "can we write data?"

### Why This Phase Structure (REFACTORED in V2)

⚠️ **V1 problem:** Phase 7 contained 13 steps mixing infrastructure + business logic

**V2 approach:**
- Phase 6: Name generators (pure infrastructure)
- Phase 7: Write operation setup (pure infrastructure)
- Phase 8: Write business logic (THIS PHASE)

**Result:** Clear separation, incremental validation, easier debugging

### Step 8.1: Create InsertBuffer

**File:** `write/load/{DB}InsertBuffer.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

/**
 * Accumulates records and flushes to database in batches.
 *
 * NOT a @Singleton - created per-stream by AggregateFactory
 */
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
            // (Optimize in Phase 15: CSV staging, COPY, bulk APIs)
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

**Key points:**
- **NOT @Singleton** - one buffer per stream
- Simple implementation: single-row inserts
- Phase 15 (Optimization) replaces with bulk loading

**Why not @Singleton?**
- Each stream needs its own buffer
- Buffers hold stream-specific state (table name, accumulated records)
- AggregateFactory creates one buffer per stream

### Step 8.2: Add executeInsert() to Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
// Add this method to {DB}AirbyteClient
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
    when (value) {
        is StringValue -> statement.setString(index, value.value)
        is IntegerValue -> statement.setLong(index, value.value)
        is NumberValue -> statement.setBigDecimal(index, value.value)
        is BooleanValue -> statement.setBoolean(index, value.value)
        is TimestampValue -> statement.setTimestamp(index, Timestamp.from(value.value))
        is DateValue -> statement.setDate(index, Date.valueOf(value.value))
        is TimeValue -> statement.setTime(index, Time.valueOf(value.value.toLocalTime()))
        is ObjectValue -> statement.setString(index, value.toJson())  // JSON as string
        is ArrayValue -> statement.setString(index, value.toJson())   // JSON as string
        is NullValue -> statement.setNull(index, Types.VARCHAR)
        else -> statement.setString(index, value.toString())
    }
}
```

**Note:** For non-JDBC databases, use native client APIs (e.g., MongoDB insertOne, ClickHouse native client)

### Step 8.3: Create Aggregate

**File:** `dataflow/{DB}Aggregate.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.{db}.write.load.{DB}InsertBuffer

/**
 * Processes transformed records for a single stream.
 *
 * Dataflow pipeline: Raw record → Transform → RecordDTO → Aggregate.accept() → InsertBuffer
 *
 * NOT a @Singleton - created per-stream by AggregateFactory
 */
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

**What this does:**
- Receives transformed records from CDK dataflow pipeline
- Delegates to InsertBuffer for accumulation
- Implements flush() for end-of-stream flushing

**Dataflow pipeline:**
```
Platform → JSONL records
  ↓
AirbyteMessageDeserializer (CDK)
  ↓
RecordTransformer (CDK, uses ColumnNameMapper from Phase 7)
  ↓
RecordDTO (transformed record with mapped column names)
  ↓
Aggregate.accept()  ← YOUR CODE STARTS HERE
  ↓
InsertBuffer.accumulate()
  ↓
Database
```

### Step 8.4: Create AggregateFactory

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
        // StreamStateStore contains execution config for each stream
        // Config includes table name, column mapping, etc.
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer = {DB}InsertBuffer(
            tableName = tableName,
            client = client,
        )

        return {DB}Aggregate(buffer)
    }
}
```

**What this does:**
- @Factory class provides factory method for creating Aggregates
- create() called once per stream at start of sync
- StreamStateStore provides table name for the stream
- Creates InsertBuffer → Aggregate chain

**Why factory pattern?**
- Aggregate needs per-stream state (table name)
- Can't use constructor injection (dynamic stream list)
- Factory receives StoreKey, looks up stream config, creates Aggregate

### Step 8.5: Create Writer

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

        // Gather initial state (which tables exist, generation IDs, etc.)
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        // Defensive: Handle streams not in catalog (for test compatibility)
        val initialStatus = if (::initialStatuses.isInitialized) {
            initialStatuses[stream] ?: DirectLoadInitialStatus(null, null)
        } else {
            DirectLoadInitialStatus(null, null)
        }

        val tableNameInfo = names[stream]
        val (realTableName, tempTableName, columnNameMapping) = if (tableNameInfo != null) {
            // Stream in catalog - use configured names
            Triple(
                tableNameInfo.tableNames.finalTableName!!,
                tempTableNameGenerator.generate(tableNameInfo.tableNames.finalTableName!!),
                tableNameInfo.columnNameMapping
            )
        } else {
            // Dynamic stream (test-generated) - use descriptor names directly
            val tableName = TableName(
                namespace = stream.mappedDescriptor.namespace ?: "test",
                name = stream.mappedDescriptor.name
            )
            Triple(tableName, tempTableNameGenerator.generate(tableName), ColumnNameMapping(emptyMap()))
        }

        // Phase 8: Append mode only
        // Phase 10: Add truncate mode (minimumGenerationId = generationId)
        // Phase 13: Add dedupe mode (importType is Dedupe)
        return DirectLoadTableAppendStreamLoader(
            stream,
            initialStatus,
            realTableName,
            tempTableName,
            columnNameMapping,
            client,  // TableOperationsClient
            client,  // TableSchemaEvolutionClient
            streamStateStore,
        )
    }
}
```

**What this does:**
- **setup()**: Creates namespaces, gathers initial table state
- **createStreamLoader()**: Creates StreamLoader for each stream
  - AppendStreamLoader: Just insert records (this phase)
  - TruncateStreamLoader: Overwrite table (Phase 10)
  - DedupStreamLoader: Upsert with primary key (Phase 13)

**Defensive pattern (lines 27-52):**
- Handles ConnectorWiringSuite creating dynamic test streams
- Test streams not in TableCatalog → use descriptor names directly
- Prevents NullPointerException in tests

**StreamLoader responsibilities:**
- start(): Create/prepare table
- accept(): Add record to buffer
- complete(): Flush and finalize

**CDK provides implementations:**
- DirectLoadTableAppendStreamLoader
- DirectLoadTableAppendTruncateStreamLoader
- DirectLoadTableDedupStreamLoader
- DirectLoadTableDedupTruncateStreamLoader

### Step 8.6: Create ConnectorWiringSuite Test

**File:** `src/test-integration/kotlin/.../component/{DB}WiringTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.component

import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class {DB}WiringTest(
    override val writer: DestinationWriter,
    override val client: TableOperationsClient,
    override val aggregateFactory: AggregateFactory,
) : ConnectorWiringSuite {

    // Optional: Override test namespace if different from "test"
    // override val testNamespace = "my_database"

    @Test
    override fun `all beans are injectable`() {
        super.`all beans are injectable`()
    }

    @Test
    override fun `writer setup completes`() {
        super.`writer setup completes`()
    }

    @Test
    override fun `can create append stream loader`() {
        super.`can create append stream loader`()
    }

    @Test
    override fun `can write one record`() {
        super.`can write one record`()
    }
}
```

**What ConnectorWiringSuite does:**

**Test 1: `all beans are injectable`**
- Validates all DI beans exist
- Catches missing @Singleton annotations
- Catches circular dependencies

**Test 2: `writer setup completes`**
- Calls Writer.setup()
- Validates namespace creation works
- Catches database connection errors

**Test 3: `can create append stream loader`**
- Calls Writer.createStreamLoader()
- Validates StreamLoader instantiation
- Catches missing StreamLoader dependencies

**Test 4: `can write one record`** ← MOST IMPORTANT
- Creates test stream
- Calls StreamLoader.start() → creates table
- Calls Aggregate.accept() → buffers record
- Calls Aggregate.flush() → writes to database
- Validates record appears in database
- **END-TO-END validation of full write path!**

**Test context:**
- Uses MockDestinationCatalog (fast, no real catalog parsing)
- Uses Testcontainers database
- Component test (not integration test)

**Why MockDestinationCatalog?**
- Fast iteration (no catalog JSON parsing)
- Creates dynamic test streams
- Focuses on write logic, not catalog parsing

### Step 8.7: Validate ConnectorWiringSuite

```bash
$ ./gradlew :destination-{db}:testComponentAllBeansAreInjectable
$ ./gradlew :destination-{db}:testComponentWriterSetupCompletes
$ ./gradlew :destination-{db}:testComponentCanCreateAppendStreamLoader
$ ./gradlew :destination-{db}:testComponentCanWriteOneRecord
```

**Expected new passes:**
```
✓ all beans are injectable
✓ writer setup completes
✓ can create append stream loader
✓ can write one record
```

**The last test (`can write one record`) validates:**
- ✅ Full DI wiring works (Writer, AggregateFactory, Client)
- ✅ Writer.setup() creates namespaces
- ✅ StreamLoader.start() creates tables
- ✅ Aggregate.accept() buffers records
- ✅ InsertBuffer.flush() writes to database
- ✅ **Data actually appears in your database!**

**If `can write one record` FAILS:**

**DI errors:**
→ Check Phase 7 infrastructure (WriteOperationV2, DatabaseInitialStatusGatherer, ColumnNameMapper)
→ Check Phase 6 name generators all have @Singleton

**Table creation errors:**
→ Check TableOperationsClient.createTable() implementation (Phase 4)
→ Check SqlGenerator.createTable() SQL syntax

**Insert errors:**
→ Check InsertBuffer.insertRecord() implementation
→ Check client.executeInsert() and setParameter() logic
→ Check column name mapping

**Record not found in database:**
→ Check buffer.flush() is called
→ Check SQL INSERT statement is correct
→ Query database directly to debug

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:**
```
✓ connect to database (Phase 2)
✓ create and drop namespaces (Phase 3)
✓ create and drop tables (Phase 4)
✓ insert records (Phase 4)
✓ count table rows (Phase 4)
✓ all beans are injectable (Phase 8 - new)
✓ writer setup completes (Phase 8 - new)
✓ can create append stream loader (Phase 8 - new)
✓ can write one record (Phase 8 - new)

Total: 9 component tests passing
```

**Integration test regression:**
```bash
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
✓ testSpecOss (Phase 1)
✓ testSuccessConfigs (Phase 5)
✓ writer can be instantiated with real catalog (Phase 7)

Total: 3 integration tests passing
```

✅ **Checkpoint Complete:** First working sync!

**Exit Criteria:**
- ✅ InsertBuffer created (accumulates and flushes records)
- ✅ Aggregate created (delegates to InsertBuffer)
- ✅ AggregateFactory created with @Factory (creates Aggregates per stream)
- ✅ Writer created with @Singleton (orchestrates setup and StreamLoaders)
- ✅ All ConnectorWiringSuite tests pass
- ✅ `can write one record` test passes (end-to-end validation)
- ✅ Regression tests pass (all previous phases still work)

**You're ready for Phase 9 when:** ConnectorWiringSuite tests pass and you can write data end-to-end

---

## Phase 9: Generation ID Support

**Goal:** Track sync generations for refresh handling

**Checkpoint:** Can retrieve generation IDs

**📋 What's a Generation ID?**
- Unique identifier for each sync run
- Used to distinguish "old data" from "new data" during refreshes
- Stored in `_airbyte_generation_id` column

**When used:**
- Full refresh: minimumGenerationId = generationId (replace all data)
- Incremental: minimumGenerationId = 0 (keep all data)

### Step 9.1: Enable Generation ID Test

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `get generation id`() {
    super.`get generation id`()
}
```

**What this tests:**
- TableOperationsClient.getGenerationId() returns correct value
- Returns 0L for tables without generation ID
- Returns actual generation ID from `_airbyte_generation_id` column

### Step 9.2: Validate

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
✓ connect to database (Phase 2)
✓ create and drop namespaces (Phase 3)
✓ create and drop tables (Phase 4)
✓ insert records (Phase 4)
✓ count table rows (Phase 4)
✓ get generation id (Phase 9 - new)
✓ all beans are injectable (Phase 8)
✓ writer setup completes (Phase 8)
✓ can create append stream loader (Phase 8)
✓ can write one record (Phase 8)

Total: 10 component tests passing
```

✅ **Checkpoint Complete:** Generation ID tracking works

**You're ready for Phase 10 when:** `get generation id` test passes

---

## Phase 10: Overwrite Mode

**Goal:** Support full refresh (replace all data)

**Checkpoint:** Can replace table contents atomically

**📋 How Overwrite Works:**
1. Write new data to temp table
2. Atomically swap temp table with final table
3. Drop old table

**Sync modes:**
- **Append** (Phase 8): INSERT into existing table
- **Overwrite** (Phase 10): SWAP temp table with final table

### Step 10.1: Implement overwriteTable() in SQL Generator

**File:** Update `client/{DB}SqlGenerator.kt`

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

    // Option 3: DROP + RENAME (fallback for most databases)
    return listOf(
        "DROP TABLE IF EXISTS ${fullyQualifiedName(target)}".andLog(),
        "ALTER TABLE ${fullyQualifiedName(source)} RENAME TO ${target.name.quote()}".andLog(),
    )

    // Option 4: BEGIN TRANSACTION + DROP + RENAME + COMMIT (for ACID guarantees)
    return listOf(
        "BEGIN TRANSACTION".andLog(),
        "DROP TABLE IF EXISTS ${fullyQualifiedName(target)}".andLog(),
        "ALTER TABLE ${fullyQualifiedName(source)} RENAME TO ${target.name.quote()}".andLog(),
        "COMMIT".andLog(),
    )
}
```

**Database-specific notes:**
- **Snowflake**: SWAP is atomic and instant (metadata operation)
- **ClickHouse**: EXCHANGE is atomic
- **Postgres/MySQL**: DROP + RENAME requires transaction for atomicity
- **BigQuery**: CREATE OR REPLACE TABLE (different pattern)

### Step 10.2: Implement overwriteTable() in Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun overwriteTable(
    sourceTableName: TableName,
    targetTableName: TableName
) {
    val statements = sqlGenerator.overwriteTable(sourceTableName, targetTableName)
    statements.forEach { execute(it) }
}
```

### Step 10.3: Update Writer for Truncate Mode

**File:** Update `write/{DB}Writer.kt`

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    // Defensive: Handle streams not in catalog (for test compatibility)
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

    // Choose StreamLoader based on sync mode
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

**What changed:**
- Added `when` statement to choose StreamLoader based on `minimumGenerationId`
- `minimumGenerationId = 0`: Append mode (keep old data)
- `minimumGenerationId = generationId`: Truncate mode (replace old data)

**StreamLoader behavior:**
- **AppendStreamLoader**: Writes directly to final table
- **AppendTruncateStreamLoader**: Writes to temp table, then swaps

### Step 10.4: Enable Tests

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `overwrite tables`() {
    super.`overwrite tables`()
}
```

### Step 10.5: Validate

```bash
$ ./gradlew :destination-{db}:testComponentOverwriteTables
```

**Expected new passes:**
```
✓ overwrite tables
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: 11 tests pass (added overwrite tables)
Integration: 3 tests pass (no change)
```

✅ **Checkpoint Complete:** Full refresh mode works

**You're ready for Phase 11 when:** `overwrite tables` test passes

---

## Phase 11: Copy Operation

**Goal:** Support table copying (used internally by some modes)

**Checkpoint:** Can copy data between tables

**📋 When Copy is Used:**
- Dedupe mode: Copy deduplicated data from temp to final
- Some overwrite implementations: Copy instead of swap
- Schema evolution: Copy to new schema

### Step 11.1: Implement copyTable() in SQL Generator

**File:** Update `client/{DB}SqlGenerator.kt`

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

**What this does:**
- Copies all rows from source to target
- Only copies mapped columns (not all columns)
- Preserves data types (SELECT → INSERT)

**Alternative: Include Airbyte metadata columns explicitly:**
```kotlin
fun copyTable(
    columnMapping: ColumnNameMapping,
    source: TableName,
    target: TableName
): String {
    // Include Airbyte metadata + user columns
    val allColumns = listOf(
        "_airbyte_raw_id",
        "_airbyte_extracted_at",
        "_airbyte_meta",
        "_airbyte_generation_id"
    ) + columnMapping.values

    val columnList = allColumns.joinToString(", ") { "\"$it\"" }

    return """
        INSERT INTO ${fullyQualifiedName(target)} ($columnList)
        SELECT $columnList
        FROM ${fullyQualifiedName(source)}
    """.trimIndent().andLog()
}
```

### Step 11.2: Implement copyTable() in Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun copyTable(
    columnNameMapping: ColumnNameMapping,
    sourceTableName: TableName,
    targetTableName: TableName
) {
    execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
}
```

### Step 11.3: Enable Test

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `copy tables`() {
    super.`copy tables`()
}
```

### Step 11.4: Validate

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
```

**Expected:**
```
Component: 12 tests pass (added copy tables)
Integration: 3 tests pass (no change)
```

✅ **Checkpoint Complete:** Copy operation works

**You're ready for Phase 12 when:** `copy tables` test passes

---

## Phase 12: Schema Evolution

**Goal:** Automatically adapt to schema changes

**Checkpoint:** Can add, drop, and modify columns

**📋 Schema Evolution Scenarios:**
1. **Add column**: Source adds new field → add column to destination
2. **Drop column**: Source removes field → drop column from destination (optional)
3. **Change type**: Source changes field type → alter column (with casting)
4. **Change nullability**: Source changes nullable → alter column constraints

### Step 12.1: Implement discoverSchema()

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

### Step 12.2: Implement computeSchema()

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

### Step 12.3: Implement alterTable() - ADD COLUMN

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

### Step 12.4: Implement alterTable() - MODIFY COLUMN

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

### Step 12.5: Implement applyChangeset()

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

### Step 12.6: Implement ensureSchemaMatches()

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

### Step 12.7: Validate Schema Evolution

**Run component tests:**
```bash
$ ./gradlew :destination-{db}:componentTest
```

**Expected:**
```
Component: 12 tests pass (no new tests added - schema evolution tested in integration)
```

**Run integration tests:**
```bash
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Integration: 3 tests pass (existing tests now support schema evolution automatically)
```

**Manual validation:**

If you want to explicitly test schema evolution:

```kotlin
// In integration test or manual testing
// 1. Sync with schema v1 (3 columns)
// 2. Modify source schema to v2 (4 columns - added "age")
// 3. Sync again
// 4. Verify table has 4 columns
```

✅ **Checkpoint Complete:** Schema evolution works

**You're ready for Phase 13 when:** Schema evolution methods implemented and tests pass

---

## Phase 13: Dedupe Mode

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

### Step 13.1: Implement upsertTable() in SQL Generator

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

### Step 13.2: Implement upsertTable() in Client

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

### Step 13.3: Update Writer for Dedupe Mode

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

### Step 13.4: Enable Tests

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `upsert tables`() {
    super.`upsert tables`()
}
```

### Step 13.5: Validate

```bash
$ ./gradlew :destination-{db}:testComponentUpsertTables
```

**Expected new passes:**
```
✓ upsert tables
```

**Regression check:**
```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: 13 tests pass (added upsert tables)
Integration: 3 tests pass (no change)
```

✅ **Checkpoint Complete:** Dedupe mode works!

**You're ready for Phase 14 when:** All core tests pass including upsert

---

## Phase 14: CDC Support (Optional)

**Goal:** Handle source deletions

**Checkpoint:** Can process CDC deletion events

**📋 CDC (Change Data Capture):**
- Tracks INSERT, UPDATE, DELETE operations from source
- Deletion marked with `_ab_cdc_deleted_at` timestamp
- Two modes:
  - **Hard delete**: Remove record from destination
  - **Soft delete**: Keep record with deletion timestamp

### Step 14.1: Add CDC Configuration

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

### Step 14.2: Add CDC Logic to upsertTable()

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

### Step 14.3: Test CDC

CDC tests are typically included in integration tests automatically if you have CDC streams configured. No separate test enablement needed - the framework tests CDC if the stream has `_ab_cdc_deleted_at` column.

### Step 14.4: Validate

```bash
$ ./gradlew :destination-{db}:componentTest
$ ./gradlew :destination-{db}:integrationTest
```

**Expected:**
```
Component: 13 tests pass (no change)
Integration: 3 tests pass (CDC tested automatically if applicable)
```

✅ **Checkpoint Complete:** Full CDC support

**You're ready for Phase 15 when:** CDC logic implemented and tests pass

---

## Phase 15: Optimization & Polish

**Goal:** Production-ready performance

**Not strictly required for functionality, but recommended for production use**

### Step 15.1: Add BasicFunctionalityIntegrationTest (Recommended)

**For production certification, implement comprehensive integration tests.**

📖 **See:** `connector-writer/destination/basic-functionality-test-guide.md`

**What it validates:**
- All Airbyte data types (50+ scenarios)
- Schema evolution (add/drop/modify columns)
- CDC deletions (hard delete, soft delete)
- Type edge cases (large integers, precision, nulls)
- All sync modes comprehensively

**Implementation guide covers:**
- ✅ DataDumper/Cleaner helpers (~200 lines)
- ✅ Test class with all 13 parameters (~100 lines)
- ✅ Parameter explanations for your database
- ✅ Debugging common failures
- ✅ Reference implementations

**Time:** 5-9 hours

**Checkpoint:** `./gradlew :destination-{db}:integrationTest` passes

**Note:** This is complex but provides gold-standard validation. The separate guide keeps this main guide scannable.

### Step 15.2: Optimize Insert Buffer

**Current:** Simple single-row inserts (slow for large datasets)

**Optimizations:**

**Option A: Staging Files (Snowflake pattern)**

**File:** Update `write/load/{DB}InsertBuffer.kt`

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

**Add to Client:**

```kotlin
// Snowflake example
suspend fun putInStage(tableName: TableName, filePath: Path) {
    val stageName = "@%${fullyQualifiedName(tableName)}"
    execute("PUT file://${filePath.toAbsolutePath()} $stageName AUTO_COMPRESS=FALSE")
}

suspend fun copyFromStage(tableName: TableName, fileName: String) {
    val stageName = "@%${fullyQualifiedName(tableName)}"
    execute("""
        COPY INTO ${fullyQualifiedName(tableName)}
        FROM $stageName/$fileName
        FILE_FORMAT = (TYPE = CSV FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 0)
        ON_ERROR = ABORT_STATEMENT
    """.trimIndent())
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

private fun formatCsvValue(value: AirbyteValue): String = when (value) {
    is StringValue -> "\"${value.value.replace("\"", "\"\"")}\""
    is NullValue -> ""
    else -> value.toString()
}
```

**Option C: Batch Prepared Statements**

```kotlin
suspend fun flush() {
    if (buffer.isEmpty()) return

    dataSource.connection.use { connection ->
        val columns = buffer.first().keys.joinToString(", ") { "\"$it\"" }
        val placeholders = buffer.first().keys.joinToString(", ") { "?" }
        val sql = "INSERT INTO $tableName ($columns) VALUES ($placeholders)"

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

### Step 15.2: Add Compression (if using staging)

```kotlin
// GZIP compression (most databases)
val outputStream = GZIPOutputStream(FileOutputStream(csvFile))

// LZ4 compression (ClickHouse)
val outputStream = LZ4FrameOutputStream(FileOutputStream(file))

// Snappy compression (Snowflake internal stages)
val outputStream = SnappyFrameOutputStream(FileOutputStream(file))
```

### Step 15.3: Tune Batch Sizes

```kotlin
class {DB}InsertBuffer(
    private val tableName: TableName,
    private val client: {DB}AirbyteClient,
    private val flushLimit: Int = determineOptimalBatchSize(),
) {
    companion object {
        private fun determineOptimalBatchSize(): Int {
            // Small batches: More frequent flushes, less memory
            // Large batches: Fewer flushes, more memory, better performance

            // Conservative default
            return 1000

            // Aggressive (for fast networks + large memory)
            return 10000

            // Memory-constrained
            return 100
        }
    }
}
```

### Step 15.4: Add Metrics and Monitoring

```kotlin
class {DB}InsertBuffer(
    private val tableName: TableName,
    private val client: {DB}AirbyteClient,
    private val metrics: MetricsReporter,
) {
    suspend fun flush() {
        if (buffer.isEmpty()) return

        val startTime = System.currentTimeMillis()
        try {
            // ... flush logic ...

            val duration = System.currentTimeMillis() - startTime
            metrics.recordFlush(tableName, recordCount, duration)
            log.info { "Flushed $recordCount records in ${duration}ms (${recordCount * 1000 / duration} records/sec)" }
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }
}
```

### Step 15.5: Performance Testing

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

**Benchmarks (typical):**
- Single-row inserts: 100-1,000 records/sec
- Batch inserts: 1,000-10,000 records/sec
- Staging files: 10,000-100,000+ records/sec

✅ **Checkpoint Complete:** Production-ready performance!

**You're ready for production when:**
- Performance meets requirements
- Memory usage acceptable
- Tests pass with large datasets

---

## Understanding Test Contexts

**Why this section matters:** Tests pass but Docker fails? This section explains the three different DI contexts your connector runs in.

### The Three DI Contexts

Your connector runs in 3 different dependency injection contexts, each with different catalog loading and bean requirements:

### 1. Component Test Context

**Annotation:** `@MicronautTest(environments = ["component"])`

**What it is:**
- Unit-style tests for connector components
- Fast iteration (< 1 second per test)
- Isolated from real catalog parsing

**Catalog:** MockDestinationCatalog
- CDK provides MockDestinationCatalog bean
- Streams created dynamically by test code
- No JSON catalog parsing
- No TableCatalog auto-instantiation

**Database:** Testcontainers
- Fresh database per test class
- Automatic cleanup
- No manual setup needed

**Tests that run here:**
- TableOperationsSuite (Phases 2-5)
- ConnectorWiringSuite (Phase 8)

**What this catches:**
- Missing @Singleton annotations on Writer, AggregateFactory, Client
- Circular dependencies
- Database connection errors
- SQL syntax errors
- Business logic bugs

**What this DOESN'T catch:**
- Missing name generators (MockDestinationCatalog bypasses TableCatalog)
- Missing application-connector.yml (uses test config)
- Bean registration errors for TableCatalog dependencies

### 2. Integration Test Context

**No special annotation** - spawns actual connector process

**What it is:**
- Integration tests that spawn real connector subprocess
- Same execution path as Docker
- Full catalog parsing

**Catalog:** REAL catalog from JSON
- Parses JSON catalog file
- Auto-instantiates TableCatalog
- Requires name generators (Phase 6)
- Full DI graph validation

**Tests that run here:**
- SpecTest (Phase 1)
- CheckIntegrationTest (Phase 5)
- WriteInitializationTest (Phase 7)
- BasicFunctionalityIntegrationTest (Phases 8+)

**What this catches:**
- **Missing name generators** (TableCatalog fails to instantiate)
- **Missing WriteOperationV2** (write operation can't start)
- **Missing DatabaseInitialStatusGatherer bean** (Writer DI fails)
- All DI errors that would occur in Docker

**What this DOESN'T catch:**
- application-connector.yml errors (test uses test config)

### 3. Docker Runtime Context

**How it runs:** `docker run airbyte/destination-{db}:0.1.0 --write`

**What it is:**
- Production execution environment
- Real Airbyte platform invocation
- Full configuration from platform

**Catalog:** REAL catalog from platform
- Provided by Airbyte platform
- Auto-instantiates TableCatalog
- Requires name generators (Phase 6)

**Configuration:** application-connector.yml
- ⚠️ CRITICAL: Must exist in src/main/resources/
- Provides data-channel configuration
- Provides namespace-mapping-config-path
- Missing file = DI errors

**Common failure:** Tests pass, Docker fails
- Why: Tests use test config, Docker uses application-connector.yml
- Fix: Create application-connector.yml (Phase 0, Step 0.8)

### Test Progression Strategy

```
Phase 2-5: TableOperationsSuite (component tests)
  ↓ Validates: Database operations work
  ✓ Fast feedback

Phase 6: Name generators created
  ↓ Enables: TableCatalog instantiation

Phase 7: WriteInitializationTest (integration test)
  ↓ Validates: Write operation can initialize with REAL catalog
  ✓ Catches: Missing name generators, WriteOperationV2, bean registrations

Phase 8: ConnectorWiringSuite (component tests)
  ↓ Validates: Full write path with MOCK catalog
  ✓ Fast iteration on business logic

Phase 8+: BasicFunctionalityIntegrationTest
  ↓ Validates: End-to-end with REAL catalog
  ✓ Full connector functionality
```

**Best practice:** Run BOTH
```bash
# Fast iteration (component tests)
$ ./gradlew :destination-{db}:componentTest

# Full validation (integration tests)
$ ./gradlew :destination-{db}:integrationTest
```

---

## Common DI Errors & Fixes

**Quick troubleshooting guide for the most common Dependency Injection errors**

### Error: "Error instantiating TableCatalog" or "No bean of type [FinalTableNameGenerator]"

**What it means:**
- TableCatalog requires name generator beans
- Only happens with real catalog parsing

**Fix:** Create name generators (Phase 6)

**File:** `config/{DB}NameGenerators.kt`

```kotlin
@Singleton
class {DB}FinalTableNameGenerator(...) : FinalTableNameGenerator { ... }

@Singleton
class {DB}RawTableNameGenerator(...) : RawTableNameGenerator { ... }

@Singleton
class {DB}ColumnNameGenerator : ColumnNameGenerator { ... }
```

**Also register in BeanFactory:**
```kotlin
@Singleton
fun tempTableNameGenerator(...): TempTableNameGenerator { ... }
```

---

### Error: "No bean of type [DatabaseInitialStatusGatherer]"

**What it means:**
- Class exists but bean registration missing
- Common mistake in V1 guide

**Fix:** Add bean registration (Phase 7, Step 7.3)

**File:** `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun initialStatusGatherer(
    client: TableOperationsClient,
    tempTableNameGenerator: TempTableNameGenerator,
): DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    return {DB}DirectLoadDatabaseInitialStatusGatherer(client, tempTableNameGenerator)
}
```

---

### Error: "A legal sync requires a declared @Singleton of a type that implements LoadStrategy"

**What it means:**
- Missing WriteOperationV2 bean

**Fix:** Create WriteOperationV2 (Phase 7, Step 7.1)

**File:** `cdk/WriteOperationV2.kt`

```kotlin
@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperationV2(private val d: DestinationLifecycle) : Operation {
    override fun execute() { d.run() }
}
```

---

### Error: "Failed to inject value for parameter [dataChannelMedium]"

**What it means:**
- Missing application-connector.yml
- **Only happens in Docker, NOT in tests**

**Fix:** Create application-connector.yml (Phase 0, Step 0.8)

**File:** `src/main/resources/application-connector.yml`

```yaml
airbyte:
  destination:
    core:
      data-channel:
        medium: STDIO
        format: JSONL
      mappers:
        namespace-mapping-config-path: ""
```

---

### Error: "lateinit property initialStatuses has not been initialized"

**What it means:**
- ConnectorWiringSuite creates dynamic test streams
- Writer needs defensive handling

**Fix:** Make Writer defensive (Phase 8, Step 8.5)

```kotlin
val initialStatus = if (::initialStatuses.isInitialized) {
    initialStatuses[stream] ?: DirectLoadInitialStatus(null, null)
} else {
    DirectLoadInitialStatus(null, null)
}
```

---

## Summary

**Congratulations!** You now have a complete, production-ready destination connector.

**Key improvements in V2:**
- **DI-first approach** prevents "fighting gaps"
- **WriteInitializationTest** catches DI errors early (Phase 7)
- **Explicit bean registration** for DatabaseInitialStatusGatherer
- **Clear test context explanation**
- **Comprehensive DI troubleshooting**

**Test coverage:**
- Component tests: ~13 tests (fast, isolated)
- Integration tests: ~3+ tests (real catalog, catches DI errors)
- All sync modes: append, overwrite, dedupe, CDC

**Next steps:**
1. Review implementation-reference.md for advanced patterns
2. Review coding-standards.md for best practices
3. Consider Phase 15 optimizations for production
4. Submit connector for review

Happy connector building! 🚀
