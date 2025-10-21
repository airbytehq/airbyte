# Table Filtering Implementation Plan for Airbyte CDK
TODO: REMOVE BEFORE MERGE

## Overview

This document outlines the approach for implementing table filtering in the Airbyte CDK to enable fine-grained table selection across all source connectors. This implementation is inspired by existing enterprise source implementations and will provide a general-purpose solution for connectors that don't already have schema/database filtering.

## Background

### Connector Architecture

**Modern Connectors (Kotlin-based):**
- Use Kotlin classes extending `ConfigurationSpecification`
- JSON schema is auto-generated from class annotations
- Examples: MySQL, Snowflake, ClickHouse
- Located in: `src/main/kotlin/.../Specification.kt`

### Existing Implementations

**Sources WITHOUT namespace filtering:**
- CockroachDB, DB2, MySQL (potentially), and others
- These sources discover ALL tables in all accessible namespaces
- Need a way to filter specific tables without modifying each connector

### Enterprise Table Filtering Pattern

```kotlin
@JsonSchemaTitle("Table Filter")
@JsonSchemaDescription("Filter configuration for table selection per schema.")
class TableFilter {
    @JsonProperty("schema_name")
    @JsonSchemaTitle("Schema Name")
    lateinit var schemaName: String

    @JsonProperty("table_name_patterns")
    @JsonSchemaTitle("Table Filter Patterns")
    @JsonPropertyDescription("List of filters to be applied to the table names. Should be a SQL LIKE pattern.")
    var patterns: List<String> = emptyList()
}
```

## Proposed Implementation

### 1. Create TableFilter Configuration Class

**Location:** `/Users/sophie.c/airbyte/airbyte-cdk/bulk/core/extract/src/main/kotlin/io/airbyte/cdk/command/TableFilter.kt`

```kotlin
package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings

/**
 * Table filtering configuration for fine-grained table selection during discovery.
 *
 * This filter applies SQL LIKE pattern matching to table names within a specific namespace.
 * The namespace field is database-agnostic and maps to:
 * - Schema name for PostgreSQL, MSSQL, Redshift
 * - Database name for MongoDB, MySQL
 * - Catalog name for Oracle
 * - Catalog.Schema for some databases with both concepts
 */
@JsonSchemaTitle("Table Filter")
@JsonSchemaDescription("Filter configuration for table selection per namespace.")
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
data class TableFilter(
    @JsonProperty("namespace")
    @JsonSchemaTitle("Namespace")
    @JsonPropertyDescription(
        "The namespace to filter on. Depending on the database, this could be a " +
        "schema name, database name, or catalog name."
    )
    @JsonSchemaInject(json = """{"order":1,"always_show":true}""")
    val namespace: String,

    @JsonProperty("table_name_patterns")
    @JsonSchemaTitle("Table Filter Patterns")
    @JsonPropertyDescription(
        "List of SQL LIKE patterns to filter table names. " +
        "Use '%' for wildcard matching (e.g., 'user_%', '%_temp', 'prod_%_table'). " +
        "Empty list means include all tables in the namespace."
    )
    @JsonSchemaInject(json = """{"order":2,"always_show":true}""")
    val tableNamePatterns: List<String> = emptyList()
)
```

**Key Design Decisions:**
- Use `namespace` instead of `schema_name` to be database-agnostic
- Support SQL LIKE patterns (%, _) for flexible matching
- Empty pattern list = include all tables in that namespace
- Made it a data class for immutability and better Kotlin semantics

### 2. Create JdbcSourceConfigurationSpecification Base Class

**Location:** `/Users/sophie.c/airbyte/airbyte-cdk/bulk/toolkits/extract-jdbc/src/main/kotlin/io/airbyte/cdk/command/JdbcSourceConfigurationSpecification.kt`

Create an optional base class for JDBC sources with common database properties:

```kotlin
package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings

/**
 * Base ConfigurationSpecification for JDBC sources with common properties.
 *
 * Connector-specific implementations should extend this class and add
 * their unique properties (like replication methods, SSL modes, etc.).
 */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
abstract class JdbcSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonPropertyDescription("Hostname of the database.")
    @JsonSchemaInject(json = """{"order":0,"always_show":true}""")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonPropertyDescription("Port of the database.")
    @JsonSchemaInject(json = """{"order":1}""")
    abstract var port: Int // Abstract to allow different defaults per connector

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("Name of the database.")
    @JsonSchemaInject(json = """{"order":2,"always_show":true}""")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonPropertyDescription(
        "The list of schemas to sync from. " +
        "If not specified, all accessible schemas will be synced. " +
        "The exact meaning depends on the database (schema names, database names, etc.)."
    )
    @JsonSchemaInject(json = """{"order":3,"always_show":true}""")
    var schemas: List<String>? = null

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("Username to access the database.")
    @JsonSchemaInject(json = """{"order":4,"always_show":true}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("Password associated with the username.")
    @JsonSchemaInject(json = """{"order":5,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Parameters (Advanced)")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
        "formatted as 'key=value' pairs separated by the symbol '&'. " +
        "(example: key1=value1&key2=value2&key3=value3)."
    )
    @JsonSchemaInject(json = """{"order":6}""")
    var jdbcUrlParams: String? = null

    @JsonProperty("table_filters")
    @JsonSchemaTitle("Table Filters (Advanced)")
    @JsonPropertyDescription(
        "Optional filters to include only specific tables from specific schemas. " +
        "Works in combination with the 'Schemas' config above."
    )
    @JsonSchemaInject(json = """{"order":7}""")
    var tableFilters: List<TableFilter>? = null

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":8}""")
    @JsonSchemaDefault("true")
    @JsonPropertyDescription(
        "When enabled, the connector will query each table individually to check access privileges. " +
        "In large schemas, this might slow down schema discovery."
    )
    var checkPrivileges: Boolean? = true
}
```

**Key Benefits:**
- All common JDBC properties in one place
- Connectors extend this class and add only their unique properties
- Consistent ordering and descriptions across all JDBC connectors
- `port` is abstract to allow different default values (3306 for MySQL, 5432 for Postgres, etc.)

### 3. Add to JdbcSourceConfiguration Interface

**Location:** `/Users/sophie.c/airbyte/airbyte-cdk/bulk/toolkits/extract-jdbc/src/main/kotlin/io/airbyte/cdk/command/JdbcSourceConfiguration.kt`

```kotlin
interface JdbcSourceConfiguration : SourceConfiguration {
    // ... existing properties ...

    /**
     * Optional table filtering configuration for fine-grained table selection.
     *
     * If null or empty, no table filtering is applied (all tables are discovered).
     * If specified, only tables matching the patterns within the specified namespaces
     * will be included in discovery.
     *
     * This works in combination with namespace filtering (namespaces config):
     * 1. First, namespaces are filtered (if namespaces config is set)
     * 2. Then, tables within those namespaces are filtered (if tableFilters is set)
     */
    val tableFilters: List<TableFilter>? get() = null
}
```

**Why this approach:**
- Scoped to JDBC sources only (not all sources need table filtering)
- Works naturally with existing `namespaces` property in JdbcSourceConfiguration
- Default `null` means opt-in behavior
- Connectors that don't need it won't show it in their spec
- Connectors that want it can override in their ConfigurationSpecification class
- No need to modify every existing connector

### 4. Implement Filtering in JdbcMetadataQuerier

**Location:** `/Users/sophie.c/airbyte/airbyte-cdk/bulk/toolkits/extract-jdbc/src/main/kotlin/io/airbyte/cdk/discover/JdbcMetadataQuerier.kt`

**Modify the `memoizedTableNames` property (lines 65-95):**

```kotlin
val memoizedTableNames: List<TableName> by lazy {
    log.info { "Querying table names for catalog discovery." }
    try {
        val allTables = mutableSetOf<TableName>()
        val dbmd: DatabaseMetaData = conn.metaData
        for (namespace in config.namespaces + config.namespaces.map { it.uppercase() }) {
            val (catalog: String?, schema: String?) =
                when (constants.namespaceKind) {
                    NamespaceKind.CATALOG -> namespace to null
                    NamespaceKind.SCHEMA -> null to namespace
                    NamespaceKind.CATALOG_AND_SCHEMA -> namespace to namespace
                }
            dbmd.getTables(catalog, schema, null, null).use { rs: ResultSet ->
                while (rs.next()) {
                    allTables.add(
                        TableName(
                            catalog = rs.getString("TABLE_CAT"),
                            schema = rs.getString("TABLE_SCHEM"),
                            name = rs.getString("TABLE_NAME"),
                            type = rs.getString("TABLE_TYPE") ?: "",
                        ),
                    )
                }
            }
        }
        log.info { "Discovered ${allTables.size} table(s) in namespaces ${config.namespaces}." }

        // Apply table filtering if configured
        val filteredTables = applyTableFilters(allTables.toList())

        if (filteredTables.size < allTables.size) {
            log.info { "Table filtering reduced table count from ${allTables.size} to ${filteredTables.size}." }
        }

        return@lazy filteredTables.sortedBy { "${it.namespace()}.${it.name}.${it.type}" }
    } catch (e: Exception) {
        throw RuntimeException("Table name discovery query failed: ${e.message}", e)
    }
}

/**
 * Applies table filtering based on config.tableFilters.
 * If no filters are configured, returns all tables.
 */
private fun applyTableFilters(tables: List<TableName>): List<TableName> {
    val filters = config.tableFilters
    if (filters.isNullOrEmpty()) {
        return tables
    }

    // Group filters by namespace for efficient lookup
    val filtersByNamespace = filters.groupBy { it.namespace }

    return tables.filter { table ->
        val namespace = table.namespace() ?: return@filter true
        val patternsForNamespace = filtersByNamespace[namespace] ?: return@filter false

        // If no patterns specified for this namespace, include all tables
        if (patternsForNamespace.isEmpty() ||
            patternsForNamespace.all { it.tableNamePatterns.isEmpty() }) {
            return@filter true
        }

        // Check if table name matches any pattern
        val allPatterns = patternsForNamespace.flatMap { it.tableNamePatterns }
        allPatterns.any { pattern ->
            sqlLikeToRegex(pattern).matches(table.name)
        }
    }
}
```

## How Connectors Will Use This

### For Modern Kotlin-Based Connectors (e.g., MySQL, Snowflake)

Connectors can now **extend the base class** instead of duplicating common properties:

#### Step 1: Extend JdbcSourceConfigurationSpecification

```kotlin
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class MySqlSourceConfigurationSpecification : JdbcSourceConfigurationSpecification() {

    // Override port with MySQL-specific default
    @JsonProperty("port")
    @JsonSchemaDefault("3306")
    override var port: Int = 3306

    // Add MySQL-specific properties only
    @JsonProperty("ssl_mode")
    @JsonSchemaTitle("SSL Mode")
    @JsonPropertyDescription("SSL connection mode for MySQL")
    @JsonSchemaInject(json = """{"order":10}""")
    var sslMode: SslMode? = null

    @JsonProperty("replication_method")
    @JsonSchemaTitle("Replication Method")
    @JsonPropertyDescription("Method for reading data (Standard or CDC)")
    @JsonSchemaInject(json = """{"order":11}""")
    var replicationMethod: ReplicationMethod? = null

    // ... other MySQL-specific properties ...
}
```

**Benefits:**
- No need to redeclare `host`, `database`, `username`, `password`, etc.
- `schemas` and `table_filters` are automatically included from base class
- Only add connector-specific properties (SSL mode, replication method, etc.)
- Consistent property ordering across all JDBC connectors

#### Step 2: Override in SourceConfiguration Implementation

```kotlin
class MySqlSourceConfiguration(
    val pojo: MySqlSourceConfigurationSpecification
) : JdbcSourceConfiguration {
    // ... other overrides ...

    // Map schemas to namespaces (already defined in base class)
    override val namespaces: Set<String>
        get() = pojo.schemas?.toSet() ?: emptySet()

    // Map table_filters (already defined in base class)
    override val tableFilters: List<TableFilter>?
        get() = pojo.tableFilters
}
```

## Implementation Steps

1. **Create TableFilter class** in the CDK command package
2. **Create JdbcSourceConfigurationSpecification base class** with common JDBC properties
3. **Add tableFilters property** to JdbcSourceConfiguration interface with default null
4. **Implement filtering logic** in JdbcMetadataQuerier.memoizedTableNames
5. **Test with a connector** that doesn't have namespace filtering (e.g., CockroachDB or DB2)
6. **Document the feature** in CDK documentation

## Testing Strategy

### Unit Tests

2. Test `applyTableFilters` with different filter configurations
3. Test edge cases: null filters, empty filters, empty patterns

### Integration Tests

1. Test with a JDBC source (e.g., PostgreSQL in test mode)
2. Verify discovery returns only filtered tables
3. Test with multiple namespaces and patterns
4. Test with no filters (should return all tables)
5. Test with empty pattern list (should include all tables in that namespace)

## Questions & Decisions

### Resolved:
- ✅ Use `namespace` instead of `schema_name` for database-agnostic approach
- ✅ Make it optional with default null to avoid touching existing connectors
- ✅ Implement filtering in JdbcMetadataQuerier where table discovery happens
- ✅ Support SQL LIKE patterns (%, _) for familiarity with SQL users

### To Decide:
- Should empty patterns list mean "include all" or "include none"? (Proposal: "include all")

## Compatibility with Enterprise Sources

For enterprise sources that already have table filtering with `schema_name`, this CDK implementation is compatible:
- They can continue using `schema_name` in their own implementations
- The CDK provides the general pattern using `namespace`
- Both can coexist - enterprise sources use their specific implementation, OSS sources use the CDK implementation
- When merging features, enterprise sources can migrate to use `namespace` for consistency