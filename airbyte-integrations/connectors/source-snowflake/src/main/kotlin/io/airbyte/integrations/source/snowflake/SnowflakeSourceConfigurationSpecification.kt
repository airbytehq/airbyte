/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

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
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Snowflake source configuration JSON.
 *
 * Use [SnowflakeSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("Snowflake Source Spec")
@JsonPropertyOrder(
    value =
        [
            "credentials",
            "host",
            "role",
            "warehouse",
            "database",
            "schema",
            "jdbc_url_params",
        ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SnowflakeSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("credentials")
    @JsonSchemaTitle("Authorization Method")
    @JsonSchemaInject(json = """{"order":0}""")
    var credentials: CredentialsSpecification? = null

    @JsonProperty("host")
    @JsonSchemaTitle("Server URL")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription(
        "The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com)."
    )
    lateinit var host: String

    @JsonProperty("role")
    @JsonSchemaTitle("Role")
    @JsonPropertyDescription("The role you created for Airbyte to access Snowflake.")
    @JsonSchemaInject(json = """{"order":2}""")
    lateinit var role: String

    @JsonProperty("warehouse")
    @JsonSchemaTitle("Warehouse")
    @JsonPropertyDescription("The warehouse you created for Airbyte to access data.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var warehouse: String

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The database you created for Airbyte to access data.")
    @JsonSchemaInject(json = """{"order":4}""")
    lateinit var database: String

    @JsonProperty("schema")
    @JsonSchemaTitle("Schema")
    @JsonPropertyDescription(
        "The source Snowflake schema tables. Leave empty to access tables from multiple schemas."
    )
    @JsonSchemaInject(json = """{"order":5}""")
    var schema: String? = null

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Params")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3).",
    )
    @JsonSchemaInject(json = """{"order":6}""")
    var jdbcUrlParams: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "cursor")
    val cursor = MicronautPropertiesFriendlyCursorConfigurationSpecification()

    @JsonIgnore
    var cursorJson: IncrementalConfigurationSpecification? =
        UserDefinedCursorConfigurationSpecification

    @JsonSetter("cursor")
    fun setIncrementalConfigurationSpecificationValue(
        value: IncrementalConfigurationSpecification
    ) {
        cursorJson = value
    }

    @JsonGetter("cursor")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":7,"display_type":"radio"}""")
    // We make this nullable to make the old config compatible with this new one. Ideally it
    // shouldn't be null.
    fun getIncrementalConfigurationSpecificationValue(): IncrementalConfigurationSpecification? =
        cursorJson ?: cursor.asIncrementalConfigurationSpecification()

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval")
    @JsonSchemaInject(json = """{"order":8}""")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription("How often (in seconds) a stream should checkpoint, when possible.")
    var checkpointTargetIntervalSeconds: Int? = 300

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonSchemaInject(json = """{"order":9}""")
    @JsonSchemaDefault("1")
    @JsonPropertyDescription("Maximum number of concurrent queries to the database.")
    var concurrency: Int? = 1

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":10}""")
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

// Credentials specifications
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "auth_type")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = KeyPairCredentialsSpecification::class,
        name = "Key Pair Authentication"
    ),
    JsonSubTypes.Type(
        value = UsernamePasswordCredentialsSpecification::class,
        name = "username/password"
    )
)
@JsonSchemaTitle("Authorization Method")
sealed interface CredentialsSpecification

@JsonSchemaTitle("Key Pair Authentication")
@JsonSchemaInject(json = """{"order":1}""")
data class KeyPairCredentialsSpecification(
    @JsonProperty("auth_type")
    @JsonSchemaInject(json = """{"order":0}""")
    val authType: String = "Key Pair Authentication",
    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username you created to allow Airbyte to access the database.")
    @JsonSchemaInject(json = """{"order":1}""")
    val username: String,
    @JsonProperty("private_key")
    @JsonSchemaTitle("Private Key")
    @JsonPropertyDescription(
        "RSA Private key to use for Snowflake connection. See the <a href=\"https://docs.airbyte.com/integrations/sources/snowflake#key-pair-authentication\">docs</a> for more information on how to obtain this key."
    )
    @JsonSchemaInject(json = """{"order":2,"multiline":true,"airbyte_secret":true}""")
    val privateKey: String,
    @JsonProperty("private_key_password")
    @JsonSchemaTitle("Passphrase")
    @JsonPropertyDescription("Passphrase for private key")
    @JsonSchemaInject(json = """{"order":3,"airbyte_secret":true}""")
    val privateKeyPassword: String? = null
) : CredentialsSpecification

@JsonSchemaTitle("Username and Password")
@JsonSchemaInject(json = """{"order":2}""")
data class UsernamePasswordCredentialsSpecification(
    @JsonProperty("auth_type")
    @JsonSchemaInject(json = """{"order":0}""")
    val authType: String = "username/password",
    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username you created to allow Airbyte to access the database.")
    @JsonSchemaInject(json = """{"order":1}""")
    val username: String,
    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":2,"airbyte_secret":true}""")
    val password: String
) : CredentialsSpecification

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "cursor_method")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = UserDefinedCursorConfigurationSpecification::class,
        name = "user_defined",
    ),
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

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfigurationSpecification {
    var cursorMethod: String = "user_defined"

    fun asIncrementalConfigurationSpecification(): IncrementalConfigurationSpecification =
        when (cursorMethod) {
            "user_defined" -> UserDefinedCursorConfigurationSpecification
            else -> throw ConfigErrorException("invalid value $cursorMethod")
        }
}
