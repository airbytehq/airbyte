# Getting Started: Project Setup and Spec Operation

**Prerequisites:** None (start here)

**Summary:** Set up your source connector project and implement the spec operation. After this guide, `./source-{db} spec` returns your connector's configuration schema.

---

## Setup Phase 1: Scaffolding

**Goal:** Empty project structure that builds

**Checkpoint:** Project compiles

### Step 1: Create Directory Structure

```bash
cd airbyte-integrations/connectors
mkdir -p source-{db}/src/main/kotlin/io/airbyte/integrations/source/{db}
mkdir -p source-{db}/src/main/resources
mkdir -p source-{db}/src/test/kotlin/io/airbyte/integrations/source/{db}
```

### Step 2: Create build.gradle

**File:** `source-{db}/build.gradle`

**Reference:** `source-mysql/build.gradle`

```groovy
plugins {
    id 'airbyte-bulk-connector'
    id 'io.airbyte.gradle.docker'
    id 'airbyte-connector-docker-convention'
}

application {
    mainClass = 'io.airbyte.integrations.source.{db}.{DB}Source'
}

airbyteBulkConnector {
    core = 'extract'
    toolkits = ['extract-jdbc']  // Add 'extract-cdc' later if needed
}

dependencies {
    // Database JDBC driver
    implementation 'your.database:jdbc-driver:version'

    // Test dependencies
    testImplementation 'org.testcontainers:{db}'  // If available
}
```

**Key settings:**
- `core = 'extract'` - Source connector (not 'load' for destinations)
- `toolkits = ['extract-jdbc']` - JDBC source toolkit
- Add `'extract-cdc'` toolkit when implementing CDC

### Step 3: Create metadata.yaml

**File:** `source-{db}/metadata.yaml`

```yaml
data:
  connectorType: source
  connectorSubtype: database
  definitionId: your-uuid-here  # Generate with: uuidgen
  dockerImageTag: 0.1.0
  dockerRepository: airbyte/source-{db}
  documentationUrl: https://docs.airbyte.com/integrations/sources/{db}
  githubIssueLabel: source-{db}
  icon: {db}.svg
  license: ELv2
  name: {Database Name}

  connectorBuildOptions:
    baseImage: docker.io/airbyte/java-connector-base:2.0.1@sha256:...

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

  releaseStage: alpha
  supportLevel: community
  tags:
    - language:java

  connectorTestSuitesOptions:
    - suite: unitTests
    - suite: integrationTests

metadataSpecVersion: "1.0"
```

**To find latest base image:**
```bash
grep "baseImage:" airbyte-integrations/connectors/source-*/metadata.yaml | sort | uniq -c | sort -rn | head -3
```

### Step 4: Create Main Entry Point

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}Source.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import io.airbyte.cdk.AirbyteSourceRunner

object {DB}Source {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteSourceRunner.run(*args)
    }
}
```

**That's it!** The CDK framework handles the rest.

### Step 5: Verify Build

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:build
```

**Expected:** Build succeeds (may have warnings about missing components)

**Troubleshooting:**
- Package name mismatches? Verify all files use consistent package
- Missing dependencies? Check `build.gradle`

---

## Setup Phase 2: Spec Operation

**Goal:** Implement `spec` operation (returns connector configuration schema)

**Checkpoint:** Spec operation works

### Step 1: Create Configuration Specification

**Purpose:** Defines the configuration form users fill in Airbyte UI

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceConfigurationSpecification.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

@JsonSchemaTitle("{Database Name} Source Spec")
@JsonPropertyOrder(value = ["host", "port", "database", "username", "password"])
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class {DB}SourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonPropertyDescription("Hostname of the database server.")
    @JsonSchemaInject(json = """{"order":1}""")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonPropertyDescription("Port of the database server.")
    @JsonSchemaInject(json = """{"order":2,"minimum":0,"maximum":65536}""")
    @JsonSchemaDefault("5432")  // Your database's default port
    var port: Int = 5432

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("Name of the database to connect to.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var database: String

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("Username for authentication.")
    @JsonSchemaInject(json = """{"order":4}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("Password for authentication.")
    @JsonSchemaInject(json = """{"order":5,"airbyte_secret":true}""")
    var password: String? = null
}
```

**Key annotations:**
- `@JsonProperty("field_name")` - Field name in JSON
- `@JsonSchemaTitle("Title")` - Label in UI
- `@JsonPropertyDescription("...")` - Help text in UI
- `@JsonSchemaDefault("value")` - Default value
- `@JsonSchemaInject(json = """{"airbyte_secret":true}""")` - Mark as secret

### Step 2: Create Configuration and Factory

**Purpose:** Runtime configuration object your code uses

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceConfiguration.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.time.Duration

/**
 * {Database}-specific implementation of [SourceConfiguration]
 */
data class {DB}SourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    override val checkpointTargetInterval: Duration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
) : JdbcSourceConfiguration {

    override val global: Boolean = false  // Set to true when implementing CDC

    /** Required to inject [{DB}SourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun {db}SourceConfig(
            factory: SourceConfigurationFactory<
                {DB}SourceConfigurationSpecification,
                {DB}SourceConfiguration
            >,
            supplier: ConfigurationSpecificationSupplier<{DB}SourceConfigurationSpecification>,
        ): {DB}SourceConfiguration = factory.make(supplier.get())
    }
}

/**
 * Factory that converts [{DB}SourceConfigurationSpecification] to [{DB}SourceConfiguration]
 */
@Singleton
class {DB}SourceConfigurationFactory :
    SourceConfigurationFactory<{DB}SourceConfigurationSpecification, {DB}SourceConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: {DB}SourceConfigurationSpecification,
    ): {DB}SourceConfiguration {
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }

        // Build JDBC URL format string
        // %s:%d will be replaced with host:port by the framework
        val jdbcUrlFmt = "jdbc:{db}://%s:%d/${pojo.database}"

        return {DB}SourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = null,  // Add SSH tunnel support later
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = setOf(pojo.database),  // Or schema name depending on DB
            checkpointTargetInterval = Duration.ofSeconds(300),
            maxConcurrency = 1,
        )
    }
}
```

**Why two classes?**
- **Specification:** JSON schema annotations, UI metadata, raw input
- **Configuration:** Clean runtime object, validated values, computed properties

### Step 3: Create application.yml

**File:** `src/main/resources/application.yml`

```yaml
airbyte:
  connector:
    data-channel:
      medium: ${DATA_CHANNEL_MEDIUM:STDIO}
      format: ${DATA_CHANNEL_FORMAT:JSONL}
    extract:
      jdbc:
        mode: concurrent
        with-sampling: true
        table-sample-size: 1024
        throughput-bytes-per-second: 10000000
        min-fetch-size: 10
        default-fetch-size: 1024
        max-fetch-size: 1000000000
        memory-capacity-ratio: 0.6
        estimated-record-overhead-bytes: 16
        estimated-field-overhead-bytes: 16
        namespace-kind: CATALOG_AND_SCHEMA  # Or SCHEMA, CATALOG depending on DB
    check:
      jdbc:
        queries:
          - SELECT 1;  # Simple query to validate connection
```

**Key settings:**
- `namespace-kind`: How your database organizes tables
  - `CATALOG_AND_SCHEMA`: catalog.schema.table (SQL Server)
  - `SCHEMA`: schema.table (PostgreSQL)
  - `CATALOG`: catalog.table (MySQL uses database as catalog)
- `check.jdbc.queries`: SQL to validate connection

### Step 4: Run Spec Operation

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run --args='spec'
```

**Expected output:**
```json
{
  "type": "SPEC",
  "spec": {
    "documentationUrl": "https://docs.airbyte.com/integrations/sources/{db}",
    "connectionSpecification": {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "{Database Name} Source Spec",
      "type": "object",
      "required": ["host", "port", "database", "username"],
      "properties": {
        "host": {
          "type": "string",
          "title": "Host",
          "description": "Hostname of the database server.",
          "order": 1
        },
        "port": {
          "type": "integer",
          "title": "Port",
          "description": "Port of the database server.",
          "default": 5432,
          "order": 2
        },
        ...
      }
    },
    "supportsIncremental": true
  }
}
```

**Troubleshooting:**
- **Missing properties?** Check `@JsonProperty` annotations
- **Wrong defaults?** Check `@JsonSchemaDefault` annotations
- **DI errors?** Ensure `@Singleton` and `@ConfigurationProperties` present

### Step 5: Build Docker Image

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:assemble
```

**Verify image:**
```bash
docker images | grep source-{db}
```

**Test in Docker:**
```bash
docker run --rm airbyte/source-{db}:dev spec
```

---

## Adding Advanced Configuration Options

### SSL/Encryption Options

```kotlin
// In ConfigurationSpecification
@JsonProperty("ssl_mode")
@JsonSchemaTitle("SSL Mode")
@JsonPropertyDescription("SSL connection mode.")
@JsonSchemaInject(json = """{"order":6}""")
var sslMode: SslMode = SslMode.PREFER

enum class SslMode {
    @JsonProperty("disable") DISABLE,
    @JsonProperty("prefer") PREFER,
    @JsonProperty("require") REQUIRE,
    @JsonProperty("verify-ca") VERIFY_CA,
    @JsonProperty("verify-full") VERIFY_FULL,
}
```

### SSH Tunnel Support

```kotlin
// In ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration

@JsonIgnore
@ConfigurationBuilder(configurationPrefix = "tunnel_method")
val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

@JsonIgnore
var tunnelMethodJson: SshTunnelMethodConfiguration? = null

@JsonSetter("tunnel_method")
fun setTunnelMethodValue(value: SshTunnelMethodConfiguration) {
    tunnelMethodJson = value
}

@JsonGetter("tunnel_method")
@JsonSchemaTitle("SSH Tunnel Method")
@JsonPropertyDescription("Whether to use SSH tunnel for connection.")
@JsonSchemaInject(json = """{"order":10}""")
fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
    tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()
```

### Replication Method (Standard vs CDC)

```kotlin
// In ConfigurationSpecification
@JsonProperty("replication_method")
@JsonSchemaTitle("Update Method")
@JsonPropertyDescription("How to detect data changes.")
@JsonSchemaInject(json = """{"order":11,"display_type":"radio"}""")
var replicationMethod: ReplicationMethod = ReplicationMethod.Standard

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(value = Standard::class, name = "STANDARD"),
    JsonSubTypes.Type(value = Cdc::class, name = "CDC")
)
sealed interface ReplicationMethod

@JsonSchemaTitle("Standard")
@JsonSchemaDescription("Detect changes using cursor column.")
data object Standard : ReplicationMethod

@JsonSchemaTitle("CDC")
@JsonSchemaDescription("Detect changes using database replication log.")
class Cdc : ReplicationMethod {
    @JsonProperty("initial_wait_seconds")
    @JsonSchemaDefault("300")
    var initialWaitSeconds: Int = 300
}
```

---

## Summary

**What you've built:**
- Project structure that compiles
- Docker image that builds
- `spec` operation that returns configuration schema

**Files created:**
- `build.gradle` - Build configuration
- `metadata.yaml` - Connector metadata
- `{DB}Source.kt` - Entry point
- `{DB}SourceConfigurationSpecification.kt` - Config JSON schema
- `{DB}SourceConfiguration.kt` - Runtime config + factory
- `application.yml` - CDK configuration

**Next:** Continue to [2-schema-discovery.md](./2-schema-discovery.md) to implement `check` and `discover` operations.
