# Table Filtering Implementation Plan for Airbyte CDK

## Overview

This document outlines the approach for implementing table filtering in the Airbyte CDK to enable fine-grained table selection across all source connectors. This implementation is inspired by existing enterprise source implementations and will provide a general-purpose solution for connectors that don't already have schema/database filtering.

## Background

### Existing Implementations

**Enterprise Sources (with `schemas` config):**
- PostgreSQL, MSSQL, Oracle, Redshift - all have a `schemas` array config
- MongoDB - has a `databases` array config
- These already filter at the namespace level (schema/catalog/database)
- Table filtering can be layered on top of this existing filtering

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

### 2. Add to SourceConfiguration Interface

**Location:** `/Users/sophie.c/airbyte/airbyte-cdk/bulk/core/extract/src/main/kotlin/io/airbyte/cdk/command/SourceConfiguration.kt`

```kotlin
interface SourceConfiguration : Configuration, SshTunnelConfiguration {
    // ... existing properties ...

    /**
     * Optional table filtering configuration for fine-grained table selection.
     *
     * If null or empty, no table filtering is applied (all tables are discovered).
     * If specified, only tables matching the patterns within the specified namespaces
     * will be included in discovery.
     *
     * This is intended for sources that don't have namespace-level filtering
     * (e.g., sources without a "schemas" or "databases" config).
     */
    val tableFilters: List<TableFilter>? get() = null
}
```

**Why this approach:**
- Default `null` means opt-in behavior
- Connectors that don't need it won't show it in their spec
- Connectors that want it can override in their ConfigurationSpecification class
- No need to modify every existing connector

### 3. Implement Filtering in JdbcMetadataQuerier

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

/**
 * Converts a SQL LIKE pattern to a Regex pattern.
 * % becomes .*, _ becomes ., and other regex special chars are escaped.
 */
private fun sqlLikeToRegex(likePattern: String): Regex {
    val regexPattern = likePattern
        .replace("\\", "\\\\")  // Escape backslashes first
        .replace(".", "\\.")     // Escape dots
        .replace("*", "\\*")     // Escape asterisks
        .replace("+", "\\+")     // Escape plus
        .replace("?", "\\?")     // Escape question marks
        .replace("(", "\\(")     // Escape parentheses
        .replace(")", "\\)")
        .replace("[", "\\[")     // Escape brackets
        .replace("]", "\\]")
        .replace("{", "\\{")     // Escape braces
        .replace("}", "\\}")
        .replace("^", "\\^")     // Escape caret
        .replace("$", "\\$")     // Escape dollar
        .replace("|", "\\|")     // Escape pipe
        .replace("%", ".*")      // SQL % to regex .*
        .replace("_", ".")       // SQL _ to regex .

    return Regex("^$regexPattern$", RegexOption.IGNORE_CASE)
}
```

### 4. Optional: Add Fallback Filtering in DiscoverOperation

**Location:** `/Users/sophie.c/airbyte/airbyte-cdk/bulk/core/extract/src/main/kotlin/io/airbyte/cdk/discover/DiscoverOperation.kt`

For non-JDBC sources that might benefit from table filtering, we can add a fallback filter in the discover operation itself:

```kotlin
override fun execute() {
    val airbyteStreams = mutableListOf<AirbyteStream>()
    metadataQuerierFactory.session(config).use { metadataQuerier: MetadataQuerier ->
        val namespaces: List<String?> =
            listOf<String?>(null) + metadataQuerier.streamNamespaces()
        for (namespace in namespaces) {
            for (streamID in metadataQuerier.streamNames(namespace)) {
                // Apply table filtering if not already handled by the querier
                if (!shouldIncludeStream(streamID)) {
                    log.info { "Skipping stream '${streamID.name}' in '${namespace ?: ""}' due to table filter configuration." }
                    continue
                }

                val fields: List<Field> = metadataQuerier.fields(streamID)
                if (fields.isEmpty()) {
                    log.info {
                        "Ignoring stream '${streamID.name}' in '${namespace ?: ""}' because no fields were discovered."
                    }
                    continue
                }
                val primaryKey: List<List<String>> = metadataQuerier.primaryKey(streamID)
                val discoveredStream = DiscoveredStream(streamID, fields, primaryKey)
                val airbyteStream: AirbyteStream =
                    airbyteStreamFactory.create(config, discoveredStream)
                airbyteStreams.add(airbyteStream)
            }
        }
    }
    outputConsumer.accept(AirbyteCatalog().withStreams(airbyteStreams))
}

private fun shouldIncludeStream(streamID: StreamIdentifier): Boolean {
    val filters = config.tableFilters
    if (filters.isNullOrEmpty()) {
        return true
    }

    val namespace = streamID.namespace ?: return true
    val patternsForNamespace = filters.filter { it.namespace == namespace }

    if (patternsForNamespace.isEmpty()) {
        return false
    }

    // If no patterns specified, include all tables in this namespace
    if (patternsForNamespace.all { it.tableNamePatterns.isEmpty() }) {
        return true
    }

    // Check if stream name matches any pattern
    val allPatterns = patternsForNamespace.flatMap { it.tableNamePatterns }
    return allPatterns.any { pattern ->
        sqlLikeToRegex(pattern).matches(streamID.name)
    }
}
```

## How Connectors Will Use This

### Connectors WITHOUT existing namespace filtering (e.g., CockroachDB, DB2)

Add the `tableFilters` property to their ConfigurationSpecification:

```kotlin
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class CockroachDbSourceConfigurationSpecification : ConfigurationSpecification() {
    // ... existing properties ...

    @JsonProperty("table_filters")
    @JsonSchemaTitle("Table Filters")
    @JsonPropertyDescription("Optional filters to include only specific tables from specific namespaces.")
    @JsonSchemaInject(json = """{"order":10}""")
    var tableFilters: List<TableFilter>? = null
}
```

Then in their Configuration implementation:

```kotlin
class CockroachDbSourceConfiguration : SourceConfiguration {
    // ... other overrides ...

    override val tableFilters: List<TableFilter>?
        get() = pojo.tableFilters
}
```

### Connectors WITH existing namespace filtering (e.g., PostgreSQL, MSSQL)

**Don't need to do anything!** Their existing `schemas` config provides namespace-level filtering, which is sufficient for most use cases. If they want table-level filtering as well, they can optionally add it following the same pattern above.

## User Experience

### Configuration Example

```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "pass",
  "table_filters": [
    {
      "namespace": "public",
      "table_name_patterns": ["user_%", "account_%"]
    },
    {
      "namespace": "analytics",
      "table_name_patterns": ["fact_%", "dim_%"]
    },
    {
      "namespace": "staging",
      "table_name_patterns": []
    }
  ]
}
```

This configuration would:
- From `public` schema: include only tables starting with `user_` or `account_`
- From `analytics` schema: include only tables starting with `fact_` or `dim_`
- From `staging` schema: include ALL tables (empty patterns list)
- All other schemas would be excluded

### Pattern Matching Examples

| Pattern | Matches | Doesn't Match |
|---------|---------|---------------|
| `user_%` | `user_accounts`, `user_preferences` | `users`, `account_user` |
| `%_temp` | `data_temp`, `staging_temp` | `temp`, `temporary` |
| `prod_%_table` | `prod_user_table`, `prod_order_table` | `prod_users`, `table_prod` |
| `test_` | `test_` (exact match) | `test_data`, `testing` |
| `%` | Everything | Nothing |

## Implementation Steps

1. **Create TableFilter class** in the CDK command package
2. **Add tableFilters property** to SourceConfiguration interface with default null
3. **Implement filtering logic** in JdbcMetadataQuerier.memoizedTableNames
4. **Add helper method** `sqlLikeToRegex` for pattern matching
5. **(Optional)** Add fallback filtering in DiscoverOperation for non-JDBC sources
6. **Test with a connector** that doesn't have namespace filtering (e.g., CockroachDB or DB2)
7. **Document the feature** in CDK documentation

## Testing Strategy

### Unit Tests

1. Test `sqlLikeToRegex` helper with various SQL LIKE patterns
2. Test `applyTableFilters` with different filter configurations
3. Test edge cases: null filters, empty filters, empty patterns

### Integration Tests

1. Test with a JDBC source (e.g., PostgreSQL in test mode)
2. Verify discovery returns only filtered tables
3. Test with multiple namespaces and patterns
4. Test with no filters (should return all tables)
5. Test with empty pattern list (should include all tables in that namespace)

## Backward Compatibility

- **Fully backward compatible** - existing connectors continue to work without changes
- Default value is `null`, so no filtering is applied unless explicitly configured
- Connectors with existing `schemas` config are unaffected
- No breaking changes to existing APIs or interfaces

## Future Enhancements

1. **Exclude patterns**: Add support for exclusion patterns (e.g., "include all EXCEPT temp tables")
2. **Regex patterns**: Add support for full regex in addition to SQL LIKE patterns
3. **Column filtering**: Extend to support column-level filtering within tables
4. **UI improvements**: Better UI for configuring complex filtering rules in Airbyte Cloud/OSS
5. **Performance optimization**: Cache compiled regex patterns for better performance

## Questions & Decisions

### Resolved:
- ✅ Use `namespace` instead of `schema_name` for database-agnostic approach
- ✅ Make it optional with default null to avoid touching existing connectors
- ✅ Implement filtering in JdbcMetadataQuerier where table discovery happens
- ✅ Support SQL LIKE patterns (%, _) for familiarity with SQL users

### To Decide:
- Should we also filter in DiscoverOperation as a fallback for non-JDBC sources?
- Should we support case-sensitive vs case-insensitive matching as a config option?
- Should empty patterns list mean "include all" or "include none"? (Proposal: "include all")

## Compatibility with Enterprise Sources

For enterprise sources that already have table filtering with `schema_name`, this CDK implementation is compatible:
- They can continue using `schema_name` in their own implementations
- The CDK provides the general pattern using `namespace`
- Both can coexist - enterprise sources use their specific implementation, OSS sources use the CDK implementation
- When merging features, enterprise sources can migrate to use `namespace` for consistency