# Schema Discovery: Check and Discover Operations

**Prerequisites:** Complete [1-getting-started.md](./1-getting-started.md)

**Summary:** Implement schema discovery to enable `check` and `discover` operations. After this guide, your connector can validate connections and discover available tables/columns.

---

## Discovery Phase 1: Check Operation

**Goal:** Validate database connection

**Checkpoint:** `check` operation works

### Step 1: Understand Check Operation

The `check` operation:
1. Parses configuration JSON
2. Establishes database connection
3. Executes validation query
4. Returns success or failure with message

**CDK provides:** `JdbcCheckQueries` executes queries defined in `application.yml`

### Step 2: Configure Check Queries

**File:** Update `src/main/resources/application.yml`

```yaml
airbyte:
  connector:
    # ... existing config ...
    check:
      jdbc:
        queries:
          # Simple query to validate connection
          - SELECT 1;
          # Or database-specific validation
          # - SELECT 1 FROM dual;  # Oracle
          # - SELECT 1 FROM DUAL WHERE 1 = 0;  # MySQL
```

### Step 3: Test Check Operation

Create a test config file:

**File:** `secrets/config.json` (gitignored)

```json
{
  "host": "localhost",
  "port": 5432,
  "database": "testdb",
  "username": "testuser",
  "password": "testpass"
}
```

**Run check:**
```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='check --config secrets/config.json'
```

**Expected success:**
```json
{
  "type": "CONNECTION_STATUS",
  "connectionStatus": {
    "status": "SUCCEEDED"
  }
}
```

**Expected failure (wrong credentials):**
```json
{
  "type": "CONNECTION_STATUS",
  "connectionStatus": {
    "status": "FAILED",
    "message": "Authentication failed..."
  }
}
```

---

## Discovery Phase 2: Metadata Querier

**Goal:** Implement schema discovery (tables, columns, primary keys)

**Checkpoint:** MetadataQuerier returns schema information

### Step 1: Understand MetadataQuerier

The CDK provides `JdbcMetadataQuerier` which uses JDBC metadata APIs. You wrap it to add database-specific behavior:

```kotlin
interface MetadataQuerier {
    fun streamNamespaces(): List<String>           // List schemas/databases
    fun streamNames(namespace: String?): List<StreamIdentifier>  // List tables
    fun fields(streamID: StreamIdentifier): List<Field>          // List columns
    fun primaryKey(streamID: StreamIdentifier): List<List<String>>  // Get PK columns
    fun extraChecks()                              // Additional validation (CDC prereqs)
}
```

### Step 2: Create Source Operations (FieldTypeMapper)

**Purpose:** Map database types to Airbyte field types

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceOperations.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class {DB}SourceOperations : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator {

    /**
     * Map database column metadata to Airbyte field type.
     * This determines how values are read from ResultSet and serialized to JSON.
     */
    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType {
        return when (val type = c.type) {
            is SystemType -> leafType(type)
            else -> PokemonFieldType  // Fallback for unknown types
        }
    }

    /**
     * Map database type name to specific field type.
     * Adjust for your database's type names.
     */
    private fun leafType(type: SystemType): JdbcFieldType<*> {
        return when (type.typeName.uppercase()) {
            // Boolean
            "BOOLEAN", "BOOL", "BIT" -> BooleanFieldType

            // Integer types
            "TINYINT", "SMALLINT", "INT2" -> ShortFieldType
            "INTEGER", "INT", "INT4", "MEDIUMINT" -> IntFieldType
            "BIGINT", "INT8" -> LongFieldType

            // Decimal types
            "FLOAT", "REAL", "FLOAT4" -> FloatFieldType
            "DOUBLE", "DOUBLE PRECISION", "FLOAT8" -> DoubleFieldType
            "DECIMAL", "NUMERIC" -> {
                if (type.scale == 0) BigIntegerFieldType else BigDecimalFieldType
            }

            // String types
            "CHAR", "VARCHAR", "TEXT", "CLOB",
            "CHARACTER VARYING", "NCHAR", "NVARCHAR" -> StringFieldType

            // Date/Time types
            "DATE" -> LocalDateFieldType
            "TIME", "TIME WITHOUT TIME ZONE" -> LocalTimeFieldType
            "TIMESTAMP", "DATETIME", "TIMESTAMP WITHOUT TIME ZONE" -> LocalDateTimeFieldType
            "TIMESTAMPTZ", "TIMESTAMP WITH TIME ZONE" -> OffsetDateTimeFieldType

            // Binary types
            "BYTEA", "BLOB", "BINARY", "VARBINARY", "RAW" -> BinaryStreamFieldType

            // JSON type
            "JSON", "JSONB" -> StringFieldType  // Or JsonFieldType if available

            // Fallback
            else -> PokemonFieldType
        }
    }

    /**
     * Generate SQL query from query specification.
     * Called by partition implementations to build SELECT statements.
     */
    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    // SQL generation helpers (implement based on your DB's SQL dialect)
    // See MySqlSourceOperations for full implementation
}
```

**Key field types:**
| JdbcFieldType | Airbyte Type | Java Type |
|---------------|--------------|-----------|
| `BooleanFieldType` | boolean | Boolean |
| `ShortFieldType` | integer | Short |
| `IntFieldType` | integer | Int |
| `LongFieldType` | integer | Long |
| `FloatFieldType` | number | Float |
| `DoubleFieldType` | number | Double |
| `BigDecimalFieldType` | number | BigDecimal |
| `StringFieldType` | string | String |
| `LocalDateFieldType` | string (date) | LocalDate |
| `LocalTimeFieldType` | string (time) | LocalTime |
| `LocalDateTimeFieldType` | string (timestamp) | LocalDateTime |
| `OffsetDateTimeFieldType` | string (timestamp_with_timezone) | OffsetDateTime |
| `BinaryStreamFieldType` | string (base64) | InputStream |
| `PokemonFieldType` | string | Any (toString) |

### Step 3: Create Metadata Querier

**Purpose:** Wrap JdbcMetadataQuerier with database-specific behavior

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceMetadataQuerier.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/**
 * Wraps [JdbcMetadataQuerier] with {Database}-specific behavior.
 */
class {DB}SourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {

    /**
     * Additional validation checks.
     * Override to add CDC prerequisite checks.
     */
    override fun extraChecks() {
        base.extraChecks()
        // Add CDC checks here when implementing CDC:
        // if (base.config.global) {
        //     validateCdcPrerequisites()
        // }
    }

    /**
     * Return fields for a stream.
     * Override if you need to modify column discovery.
     */
    override fun fields(streamID: StreamIdentifier): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        if (table !in base.memoizedColumnMetadata) return listOf()
        return base.memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    /**
     * Return available namespaces (schemas/databases).
     */
    override fun streamNamespaces(): List<String> =
        base.config.namespaces.toList()

    /**
     * Return streams (tables) in a namespace.
     */
    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        base.memoizedTableNames
            .filter { matchesNamespace(it, streamNamespace) }
            .map { StreamDescriptor().withName(it.name).withNamespace(streamNamespace) }
            .map(StreamIdentifier::from)

    /**
     * Find table by stream identifier.
     */
    fun findTableName(streamID: StreamIdentifier): TableName? =
        base.memoizedTableNames.find {
            it.name == streamID.name && matchesNamespace(it, streamID.namespace)
        }

    /**
     * Check if table matches namespace.
     * Adjust based on your DB's namespace model:
     * - schema.table: use it.schema
     * - catalog.table: use it.catalog
     * - catalog.schema.table: use both
     */
    private fun matchesNamespace(table: TableName, namespace: String?): Boolean =
        (table.schema ?: table.catalog) == namespace

    /**
     * Factory for creating MetadataQuerier instances.
     */
    @Singleton
    @Primary
    class Factory(
        val constants: DefaultJdbcConstants,
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
        val checkQueries: JdbcCheckQueries,
    ) : MetadataQuerier.Factory<{DB}SourceConfiguration> {

        override fun session(config: {DB}SourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            val base = JdbcMetadataQuerier(
                constants,
                config,
                selectQueryGenerator,
                fieldTypeMapper,
                checkQueries,
                jdbcConnectionFactory,
            )
            return {DB}SourceMetadataQuerier(base)
        }
    }
}
```

### Step 4: Test with Testcontainers (Optional but Recommended)

**File:** `src/test/kotlin/io/airbyte/integrations/source/{db}/{DB}ContainerFactory.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import org.testcontainers.containers.{DB}Container
import org.testcontainers.utility.DockerImageName

object {DB}ContainerFactory {

    fun create(): {DB}Container<*> {
        return {DB}Container(DockerImageName.parse("{db}:latest"))
            .withDatabaseName("testdb")
            .withUsername("testuser")
            .withPassword("testpass")
    }
}
```

---

## Discovery Phase 3: Discover Operation

**Goal:** Return catalog of available streams

**Checkpoint:** `discover` operation returns streams with correct schema

### Step 1: Understand Discover Operation

The `discover` operation:
1. Connects to database
2. Queries schema catalog for tables
3. For each table, queries columns and types
4. Builds AirbyteCatalog with streams

**CDK provides:** Most of this automatically via MetadataQuerier

### Step 2: Test Discover Operation

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='discover --config secrets/config.json'
```

**Expected output:**
```json
{
  "type": "CATALOG",
  "catalog": {
    "streams": [
      {
        "name": "users",
        "namespace": "public",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": { "type": "integer" },
            "name": { "type": "string" },
            "created_at": { "type": "string", "format": "date-time" }
          }
        },
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_primary_key": [["id"]]
      }
    ]
  }
}
```

### Step 3: Verify Type Mapping

Create a test table with various types:

```sql
CREATE TABLE type_test (
    id INTEGER PRIMARY KEY,
    bool_col BOOLEAN,
    int_col INTEGER,
    bigint_col BIGINT,
    float_col FLOAT,
    decimal_col DECIMAL(10,2),
    varchar_col VARCHAR(255),
    text_col TEXT,
    date_col DATE,
    time_col TIME,
    timestamp_col TIMESTAMP,
    timestamptz_col TIMESTAMP WITH TIME ZONE,
    json_col JSON,
    binary_col BYTEA
);
```

Run discover and verify all columns have correct types:

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='discover --config secrets/config.json' | jq '.catalog.streams[] | select(.name=="type_test")'
```

**Troubleshooting:**
- **Missing tables?** Check namespace configuration
- **Wrong types?** Adjust `leafType()` in SourceOperations
- **Missing columns?** Check column privileges

---

## Adding Primary Key Discovery

### Custom Primary Key Query (If JDBC Metadata Doesn't Work)

Some databases need custom queries for primary key discovery:

```kotlin
class {DB}SourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {

    /**
     * Memoized primary keys for all tables.
     * Override if JDBC metadata doesn't work for your database.
     */
    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<PrimaryKeyRow>()
        val schemas = streamNamespaces()

        val sql = """
            SELECT table_schema, table_name, column_name, ordinal_position
            FROM information_schema.key_column_usage
            WHERE table_schema IN (${schemas.joinToString { "'$it'" }})
              AND constraint_name = 'PRIMARY'
            ORDER BY table_schema, table_name, ordinal_position
        """.trimIndent()

        base.conn.createStatement().use { stmt ->
            stmt.executeQuery(sql).use { rs ->
                while (rs.next()) {
                    results.add(PrimaryKeyRow(
                        tableSchema = rs.getString("table_schema"),
                        tableName = rs.getString("table_name"),
                        columnName = rs.getString("column_name"),
                        position = rs.getInt("ordinal_position"),
                    ))
                }
            }
        }

        results
            .groupBy { findTableName(StreamIdentifier.from(
                StreamDescriptor().withName(it.tableName).withNamespace(it.tableSchema)
            )) }
            .mapNotNull { (table, rows) ->
                if (table == null) return@mapNotNull null
                val pkColumns = rows.sortedBy { it.position }.map { listOf(it.columnName) }
                table to pkColumns
            }
            .toMap()
    }

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> {
        val table = findTableName(streamID) ?: return listOf()
        return memoizedPrimaryKeys[table] ?: listOf()
    }

    private data class PrimaryKeyRow(
        val tableSchema: String,
        val tableName: String,
        val columnName: String,
        val position: Int,
    )
}
```

---

## Adding CDC Prerequisite Checks

When you implement CDC later, add validation in `extraChecks()`:

```kotlin
override fun extraChecks() {
    base.extraChecks()

    if (base.config.global) {  // CDC mode
        // Example for MySQL:
        validateVariable("log_bin", "ON")
        validateVariable("binlog_format", "ROW")
        validateVariable("binlog_row_image", "FULL")
        validateReplicationPrivileges()
    }
}

private fun validateVariable(variable: String, expectedValue: String) {
    val sql = "SHOW VARIABLES WHERE Variable_name = '$variable'"
    base.conn.createStatement().use { stmt ->
        stmt.executeQuery(sql).use { rs ->
            if (!rs.next()) {
                throw ConfigErrorException("Could not query variable $variable")
            }
            val actualValue = rs.getString("Value")
            if (!actualValue.equals(expectedValue, ignoreCase = true)) {
                throw ConfigErrorException(
                    "Variable '$variable' should be '$expectedValue', but is '$actualValue'"
                )
            }
        }
    }
}

private fun validateReplicationPrivileges() {
    try {
        base.conn.createStatement().execute("SHOW MASTER STATUS")
    } catch (e: SQLException) {
        throw ConfigErrorException(
            "Please grant REPLICATION CLIENT privilege for CDC mode."
        )
    }
}
```

---

## Summary

**What you've built:**
- `check` operation validates database connection
- `discover` operation returns available streams with schemas
- Type mapping from database types to Airbyte types
- Primary key discovery

**Files created/modified:**
- `{DB}SourceOperations.kt` - Type mapping (FieldTypeMapper)
- `{DB}SourceMetadataQuerier.kt` - Schema discovery
- `application.yml` - Check query configuration

**Key interfaces implemented:**
- `JdbcMetadataQuerier.FieldTypeMapper` - Type mapping
- `SelectQueryGenerator` - SQL generation (partial)
- `MetadataQuerier.Factory` - Creates querier instances

**Next:** Continue to [3-full-refresh.md](./3-full-refresh.md) to implement the `read` operation for full refresh sync.
