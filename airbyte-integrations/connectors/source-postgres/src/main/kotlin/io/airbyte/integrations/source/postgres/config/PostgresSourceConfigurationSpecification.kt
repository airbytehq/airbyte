/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.config

import com.fasterxml.jackson.annotation.JsonAnyGetter
import com.fasterxml.jackson.annotation.JsonAnySetter
import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaArrayWithUniqueItems
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Postgres source configuration JSON.
 *
 * Use [PostgresSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("Postgres Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "username",
            "password",
            "schemas",
            "jdbc_url_params",
            "encryption",
            "tunnel_method",
            "cursor",
        ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class PostgresSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("5432")
    @JsonPropertyDescription("Port of the database. Defaults to 5432.")
    var port: Int = 5432

    @JsonProperty("database")
    @JsonSchemaTitle("Database Name")
    @JsonPropertyDescription("The name of the database to connect to.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var database: String

    @JsonProperty("username")
    @JsonSchemaTitle("User")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":5,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonPropertyDescription(
        "The list of schemas to sync from. Defaults to public. Case sensitive."
    )
    @JsonSchemaInject(json = """{"order":6,"always_show":true,"uniqueItems":true}""")
    var schemas: List<String>? = listOf("public")

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Params")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3).",
    )
    @JsonSchemaInject(json = """{"order":7}""")
    var jdbcUrlParams: String? = null

    // TODO: SSL config maps to JDBC parameters

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, " +
            "and if so, which kind of authentication to use.",
    )
    @JsonSchemaInject(json = """{"order":9}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "cursor")
    val cursor = MicronautPropertiesFriendlyCursorConfigurationSpecification()

    @JsonIgnore var cursorJson: IncrementalConfigurationSpecification? = null

    @JsonSetter("cursor")
    fun setIncrementalConfigurationSpecificationValue(
        value: IncrementalConfigurationSpecification
    ) {
        cursorJson = value
    }

    @JsonGetter("cursor")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":10,"display_type":"radio"}""")
    fun getIncrementalConfigurationSpecificationValue(): IncrementalConfigurationSpecification =
        cursorJson ?: cursor.asIncrementalConfigurationSpecification()

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval")
    @JsonSchemaInject(json = """{"order":11}""")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription("How often (in seconds) a stream should checkpoint, when possible.")
    var checkpointTargetIntervalSeconds: Int? = 300

    @JsonProperty("max_db_connections")
    @JsonSchemaTitle("Max Concurrent Queries to Database")
    @JsonSchemaInject(json = """{"order":12}""")
    @JsonPropertyDescription(
        "Maximum number of concurrent queries to the database. Leave empty to let Airbyte optimize performance."
    )
    var max_db_connections: Int? = null

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":13}""")
    @JsonSchemaDefault("true")
    @JsonPropertyDescription(
        "When this feature is enabled, during schema discovery the connector " +
            "will query each table or view individually to check access privileges " +
            "and inaccessible tables, views, or columns therein will be removed. " +
            "In large schemas, this might cause schema discovery to take too long, " +
            "in which case it might be advisable to disable this feature.",
    )
    var checkPrivileges: Boolean? = true

    @JsonIgnore var additionalPropertiesMap = mutableMapOf<String, Any>()

    @JsonAnyGetter fun getAdditionalProperties(): Map<String, Any> = additionalPropertiesMap

    @JsonAnySetter
    fun setAdditionalProperty(
        name: String,
        value: Any,
    ) {
        additionalPropertiesMap[name] = value
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "cursor_method")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = UserDefinedCursorConfigurationSpecification::class,
        name = "user_defined"
    ),
    JsonSubTypes.Type(value = CdcCursorConfigurationSpecification::class, name = "cdc"),
)
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface IncrementalConfigurationSpecification

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/" +
        "#user-defined-cursor\">cursor column</a> chosen when configuring a connection " +
        "(e.g. created_at, updated_at).",
)
data object UserDefinedCursorConfigurationSpecification : IncrementalConfigurationSpecification

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using Postgres's <a href=" +
        "\"https://docs.airbyte.com/integrations/connectors/source-postgres#getting-started\"" +
        "> change data capture feature</a>. This must be enabled on your database.",
)
class CdcCursorConfigurationSpecification : IncrementalConfigurationSpecification {

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC Position Behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value in the mined logs. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss.",
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(
        json = """{"order":1,"enum":["Fail sync","Re-sync data"],"always_show":true}"""
    )
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC events.",
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":2,"min":4,"max":24,"always_show":true}""")
    var initialLoadTimeoutHours: Int? = 8

    @JsonProperty("debezium_shutdown_timeout_seconds")
    @JsonSchemaTitle("Debezium Engine Shutdown Timeout in Seconds (Advanced)")
    @JsonPropertyDescription(
        "The amount of time to allow the Debezium Engine to shut down, in seconds.",
    )
    @JsonSchemaDefault("60")
    @JsonSchemaInject(json = """{"order":3,"min":1,"max":3600,"always_show":true}""")
    var debeziumShutdownTimeoutSeconds: Int? = 60
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfigurationSpecification {
    var cursorMethod: String = "user_defined"
    var invalidCdcCursorPositionBehavior: String? = null
    var initialLoadTimeoutHours: Int? = null
    var debeziumShutdownTimeoutSeconds: Int? = null

    fun asIncrementalConfigurationSpecification(): IncrementalConfigurationSpecification =
        when (cursorMethod) {
            "user_defined" -> UserDefinedCursorConfigurationSpecification
            "cdc" ->
                CdcCursorConfigurationSpecification().also {
                    it.invalidCdcCursorPositionBehavior = invalidCdcCursorPositionBehavior
                    it.initialLoadTimeoutHours = initialLoadTimeoutHours
                    it.debeziumShutdownTimeoutSeconds = debeziumShutdownTimeoutSeconds
                }
            else -> throw ConfigErrorException("invalid value $cursorMethod")
        }
}
