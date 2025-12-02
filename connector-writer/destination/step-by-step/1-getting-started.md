# Getting Started: Project Setup and Spec Operation

**Prerequisites:** None (start here)

**Summary:** Paint-by-numbers guide to implementing a destination connector. 14 phases (0-13) with clear tasks, code patterns, and test validation. Build incrementally with quick feedback loops. After Phase 1, --spec works. After Phase 5, --check works. After Phase 7, you have a working append-only connector. Full feature set by Phase 11.

**Prerequisites:**
- Familiarity with Kotlin and your target database
- Understanding of dataflow-cdk.md (architecture overview)
- Database credentials or Testcontainers setup

---

## Setup Phase 1: Scaffolding

**Goal:** Empty project structure that builds

**Checkpoint:** Project compiles

### Setup Step 1: Create Directory Structure

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

### Setup Step 2: Create gradle.properties with CDK Version Pin

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

### Setup Step 3: Create build.gradle.kts

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

### Setup Step 4: Create metadata.yaml

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

### Setup Step 5: Configure Docker Build in build.gradle.kts

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

### Setup Step 6: Create Main Entry Point

**File:** `destination-{db}/src/main/kotlin/.../​{DB}Destination.kt`

```kotlin
package io.airbyte.integrations.destination.{db}

import io.airbyte.cdk.AirbyteDestinationRunner

fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
```

**That's it!** The framework handles everything else.

### Setup Step 7: Verify Build

```bash
$ ./gradlew :destination-{db}:build
```

**Expected:** Build succeeds

**Troubleshooting:**
- Missing dependencies? Check `build.gradle.kts`
- Package name mismatches? Verify all files use consistent package
- Micronaut scanning issues? Ensure `@Singleton` annotations present
- metadata.yaml syntax errors? Validate YAML format

### Setup Step 8: Create application-connector.yml

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

### Setup Step 9: Build Docker Image

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

✅ **Checkpoint:** Project compiles and Docker image builds successfully

---

## Setup Phase 2: Spec Operation

**Goal:** Implement --spec operation (returns connector configuration schema)

**Checkpoint:** Spec test passes

### Setup Step 1: Understand Configuration Classes

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

### Setup Step 2: Create Specification Class

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

### Setup Step 3: Create Configuration and Factory

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

### Setup Step 4: Create Specification Extension

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

### Setup Step 5: Configure Documentation URL

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

### Setup Step 6: Create Expected Spec Test File

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

### Setup Step 7: Create Spec Test

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

### Setup Step 8: Generate and Validate Spec

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

### Setup Step 9: Run Spec Test

```bash
$ ./gradlew :destination-{db}:integrationTestSpecOss
```

**Expected:**
```
✓ testSpecOss
```

**Troubleshooting:**
- **Spec operation fails:** Check `application.yml` has documentation-url, verify Specification class has Jackson annotations
- **Spec test fails:** Actual spec doesn't match expected-spec-oss.json - update expected file with correct output

✅ **Checkpoint:** `integrationTestSpecOss` passes, --spec operation returns valid JSON schema

---

## Next Steps

**Next:** Continue to [2-database-setup.md](./2-database-setup.md) to implement database connectivity and the check operation.
