/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings

/**
 * Base ConfigurationSpecification for JDBC sources with common properties.
 *
 * Connector-specific implementations should extend this class and add their unique properties (like
 * replication methods, SSL modes, etc.).
 */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
abstract class JdbcSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonPropertyDescription("Hostname of the database.")
    @JsonSchemaInject(json = """{"order":0,"always_show":true}""")
    lateinit var host: String

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":2,"always_show":true}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":3,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("Name of the database.")
    @JsonSchemaInject(json = """{"order":4,"always_show":true}""")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonPropertyDescription(
        "The list of schemas to sync from. " +
            "If not specified, all accessible schemas will be synced. " +
            "The exact meaning depends on the database (schema names, database names, etc.)."
    )
    @JsonSchemaInject(json = """{"order":1,"always_show":true,"group":"optional"}""")
    var schemas: List<String>? = null

    @JsonProperty("table_filters")
    @JsonSchemaTitle("Table Filters")
    @JsonPropertyDescription(
        "Optional filters to include only specific tables from specific schemas. " +
            "Works in combination with the 'Schemas' config above."
    )
    @JsonSchemaInject(json = """{"order":2,"always_show":true,"group":"optional"}""")
    var tableFilters: List<TableFilter>? = emptyList()

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Params")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3)."
    )
    @JsonSchemaInject(json = """{"order":3,"group":"optional"}""")
    var jdbcUrlParams: String? = null

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":4,"group":"optional"}""")
    @JsonSchemaDefault("true")
    @JsonPropertyDescription(
        "When this feature is enabled, during schema discovery the connector " +
            "will query each table or view individually to check access privileges " +
            "and inaccessible tables, views, or columns therein will be removed. " +
            "In large schemas, this might cause schema discovery to take too long, " +
            "in which case it might be advisable to disable this feature.",
    )
    var checkPrivileges: Boolean? = true
}

@JsonSchemaTitle("Table Filter")
@JsonSchemaDescription("Inclusion filter configuration for table selection per schema.")
@JsonPropertyOrder("schema_name", "table_name_patterns")
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class TableFilter {
    @JsonProperty("schema_name", required = true)
    @JsonSchemaTitle("Schema Name")
    @JsonPropertyDescription(
        "The name of the schema to apply this filter to. " +
            "Should match a schema defined in \"Schemas\" field above."
    )
    @JsonSchemaInject(json = """{"order":1,"always_show":true}""")
    lateinit var schemaName: String

    @JsonProperty("table_name_patterns", required = true)
    @JsonSchemaTitle("Table Filter Patterns")
    @JsonPropertyDescription(
        "List of table name patterns to include from this schema. " +
            "Should be a SQL LIKE pattern."
    )
    @JsonSchemaInject(json = """{"order":2,"always_show":true,"minItems":1}""")
    lateinit var patterns: List<String>
}
