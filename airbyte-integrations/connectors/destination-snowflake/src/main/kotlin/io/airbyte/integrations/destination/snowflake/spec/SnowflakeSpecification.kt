/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
open class SnowflakeSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription(
        "Enter your Snowflake account's <a href=\"https://docs.snowflake.com/en/user-guide/admin-account-identifier.html#using-an-account-locator-as-an-identifier\">locator</a> (in the format <account_locator>.<region>.<cloud>.snowflakecomputing.com)"
    )
    @get:JsonProperty("host")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 0, "examples":["accountname.us-east-2.aws.snowflakecomputing.com", "accountname.snowflakecomputing.com"], "pattern": "^(http(s)?:\\/\\/)?([^./?#]+\\.)?([^./?#]+\\.)?([^./?#]+\\.)?([^./?#]+\\.(snowflakecomputing\\.com|localstack\\.cloud))$",
        "pattern_descriptor": "{account_name}.snowflakecomputing.com or {accountname}.{aws_location}.aws.snowflakecomputing.com"}"""
    )
    val host: String = ""

    @get:JsonSchemaTitle("Role")
    @get:JsonPropertyDescription(
        "Enter the <a href=\"https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles\">role</a> that you want to use to access Snowflake"
    )
    @get:JsonProperty("role")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 1, "examples":["AIRBYTE_ROLE"]}"""
    )
    val role: String = ""

    @get:JsonSchemaTitle("Warehouse")
    @get:JsonPropertyDescription(
        "Enter the name of the <a href=\"https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses\">warehouse</a> that you want to use as a compute cluster"
    )
    @get:JsonProperty("warehouse")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 2, "examples":["AIRBYTE_WAREHOUSE"]}"""
    )
    val warehouse: String = ""

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription(
        "Enter the name of the <a href=\"https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl\">database</a> you want to sync data into"
    )
    @get:JsonProperty("database")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 3, "examples":["AIRBYTE_DATABASE"]}"""
    )
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        "Enter the name of the default <a href=\"https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl\">schema</a>"
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 4, "examples":["AIRBYTE_SCHEMA"]}"""
    )
    val schema: String = ""

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription(
        "Enter the name of the user you want to use to access the database"
    )
    @get:JsonProperty("username")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 5, "examples":["AIRBYTE_USER"]}"""
    )
    val username: String = ""

    @get:JsonSchemaTitle("Authorization Method")
    @get:JsonSchemaDescription("Determines the type of authentication that should be used.")
    @get:JsonProperty("credentials")
    @get:JsonSchemaInject(json = """{"group": "connection", "order":6}""")
    val credentials: CredentialsSpecification? = null

    @get:JsonSchemaTitle("CDC deletion mode")
    @get:JsonPropertyDescription(
        """Whether to execute CDC deletions as hard deletes (i.e. propagate source deletions to the destination), or soft deletes (i.e. leave a tombstone record in the destination). Defaults to hard deletes.""",
    )
    // default hard delete for backwards compatibility
    @get:JsonProperty("cdc_deletion_mode", defaultValue = "Hard delete")
    @get:JsonSchemaInject(
        json = """{"group": "sync_behavior", "order": 5, "always_show": true}""",
    )
    val cdcDeletionMode: CdcDeletionMode? = null

    @get:JsonSchemaTitle(
        """Legacy raw tables""",
    )
    @get:JsonPropertyDescription(
        """Write the legacy "raw tables" format, to enable backwards compatibility with older versions of this connector.""",
    )
    // for compatibility with existing actor configs, we keep the old property name.
    @get:JsonProperty("disable_type_dedupe")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 7}""")
    @Suppress("RedundantNullableReturnType")
    val legacyRawTablesOnly: Boolean? = false

    @get:JsonSchemaTitle("Airbyte Internal Table Dataset Name")
    @get:JsonPropertyDescription(
        """Airbyte will use this dataset for various internal tables. In legacy raw tables mode, the raw tables will be stored in this dataset. Defaults to "airbyte_internal".""",
    )
    @get:JsonProperty("raw_data_schema")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 8}""")
    val internalTableSchema: String? = null

    @get:JsonSchemaTitle("JDBC URL Params")
    @get:JsonPropertyDescription(
        """Enter the additional properties to pass to the JDBC URL string when connecting to the database (formatted as key=value pairs separated by the symbol &). Example: key1=value1&key2=value2&key3=value3""",
    )
    @get:JsonProperty("jdbc_url_params")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 9}""")
    val jdbcUrlParams: String? = null

    @get:JsonSchemaTitle("Data Retention Period (days)")
    @get:JsonPropertyDescription(
        """The number of days of Snowflake Time Travel to enable on the tables. See <a href="https://docs.snowflake.com/en/user-guide/data-time-travel#data-retention-period">Snowflake's documentation</a> for more information. Setting a nonzero value will incur increased storage costs in your Snowflake instance.""",
    )
    @get:JsonProperty("retention_period_days")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 10}""")
    @Suppress("RedundantNullableReturnType")
    val retentionPeriodDays: Int? = 1
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "auth_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = KeyPairAuthSpecification::class, name = "Key Pair Authentication"),
    JsonSubTypes.Type(
        value = UsernamePasswordAuthSpecification::class,
        name = "Username and Password"
    )
)
sealed class CredentialsSpecification(
    @Suppress("PropertyName") @param:JsonProperty("auth_type") val auth_type: Type
) {
    /** Enumeration of possible credential types. */
    enum class Type(@get:JsonValue val authTypeName: String) {
        PRIVATE_KEY("Key Pair Authentication"),
        USERNAME_PASSWORD("Username and Password"),
    }
}

@JsonSchemaTitle("Key Pair Authentication")
@JsonSchemaDescription("Configuration details for the Key Pair Authentication.")
class KeyPairAuthSpecification(
    @get:JsonSchemaTitle("Private Key")
    @get:JsonPropertyDescription(
        """RSA Private key to use for Snowflake connection. See the <a
 href="https://docs.airbyte.com/integrations/destinations/snowflake">docs</a> for more
 information on how to obtain this key."""
    )
    @get:JsonProperty("private_key")
    @get:JsonSchemaInject(json = """{"order": 0, "multiline": true, "airbyte_secret": true}""")
    val privateKey: String = "",
    @get:JsonSchemaTitle("Passphrase")
    @get:JsonPropertyDescription("Passphrase for private key")
    @get:JsonProperty("private_key_password")
    @get:JsonSchemaInject(json = """{"order": 0, "airbyte_secret": true}""")
    val privateKeyPassword: String? = null
) : CredentialsSpecification(Type.PRIVATE_KEY)

@JsonSchemaTitle("Username and Password")
@JsonSchemaDescription("Configuration details for the Username and Password Authentication.")
class UsernamePasswordAuthSpecification(
    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Enter the password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 0, "airbyte_secret": true}""")
    val password: String = ""
) : CredentialsSpecification(Type.USERNAME_PASSWORD)

enum class CdcDeletionMode(@Suppress("unused") @get:JsonValue val cdcDeletionMode: String) {
    HARD_DELETE("Hard delete"),
    SOFT_DELETE("Soft delete"),
}

@Singleton
class SnowflakeSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("connection", "Connection"),
            DestinationSpecificationExtension.Group("sync_behavior", "Sync Behavior"),
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}
