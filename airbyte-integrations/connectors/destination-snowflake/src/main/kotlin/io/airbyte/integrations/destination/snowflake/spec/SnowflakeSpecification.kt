package io.airbyte.integrations.destination.snowflake.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
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
        json = """{"order": 0, "examples":["accountname.us-east-2.aws.snowflakecomputing.com", "accountname.snowflakecomputing.com"], "pattern": "^(http(s)?:\\/\\/)?([^./?#]+\\.)?([^./?#]+\\.)?([^./?#]+\\.)?([^./?#]+\\.(snowflakecomputing\\.com|localstack\\.cloud))$",
        "pattern_descriptor": "{account_name}.snowflakecomputing.com or {accountname}.{aws_location}.aws.snowflakecomputing.com"}"""
    )
    val host: String = ""

    @get:JsonSchemaTitle("Role")
    @get:JsonPropertyDescription("Enter the <a href=\"https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles\">role</a> that you want to use to access Snowflake")
    @get:JsonProperty("role")
    @get:JsonSchemaInject(json = """{"order": 1, "examples":["AIRBYTE_ROLE"]}""")
    val role: String = ""

    @get:JsonSchemaTitle("Warehouse")
    @get:JsonPropertyDescription("Enter the name of the <a href=\"https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses\">warehouse</a> that you want to use as a compute cluster")
    @get:JsonProperty("warehouse")
    @get:JsonSchemaInject(json = """{"order": 2, "examples":["AIRBYTE_WAREHOUSE"]}""")
    val warehouse: String = ""

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Enter the name of the <a href=\"https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl\">database</a> you want to sync data into")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 3, "examples":["AIRBYTE_DATABASE"]}""")
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription("Enter the name of the default <a href=\"https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl\">schema</a>")
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(json = """{"order": 4, "examples":["AIRBYTE_SCHEMA"]}""")
    val schema: String = ""

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Enter the name of the user you want to use to access the database")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 5, "examples":["AIRBYTE_USER"]}""")
    val username: String = ""
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
