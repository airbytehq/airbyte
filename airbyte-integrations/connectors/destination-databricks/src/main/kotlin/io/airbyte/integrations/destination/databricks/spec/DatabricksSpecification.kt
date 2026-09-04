/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.spec

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
open class DatabricksSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Server Hostname")
    @get:JsonPropertyDescription(
        "Enter your Databricks workspace <a href=\"https://docs.databricks.com/en/integrations/compute-details.html\">server hostname</a> (e.g., abc-12345678-wxyz.cloud.databricks.com). You can find this in your cluster or SQL warehouse connection details."
    )
    @get:JsonProperty("hostname")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 1, "examples": ["abc-12345678-wxyz.cloud.databricks.com"]}"""
    )
    val hostname: String = ""

    @get:JsonSchemaTitle("HTTP Path")
    @get:JsonPropertyDescription(
        "Enter the <a href=\"https://docs.databricks.com/en/integrations/compute-details.html\">HTTP path</a> for your Databricks SQL warehouse or cluster. You can find this in the connection details of your compute resource."
    )
    @get:JsonProperty("http_path")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 2, "examples": ["sql/1.0/warehouses/0000-1111111-abcd90"]}"""
    )
    val httpPath: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription(
        "Enter the port number for the Databricks cluster connection. The default port is 443 (HTTPS)."
    )
    @get:JsonProperty("port")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 9, "default": "443", "examples": ["443"]}""",
    )
    val port: String? = "443"

    @get:JsonSchemaTitle("Databricks Unity Catalog Name")
    @get:JsonPropertyDescription(
        "Enter the name of the <a href=\"https://docs.databricks.com/en/data-governance/unity-catalog/index.html\">Unity Catalog</a> that you want to sync data into."
    )
    @get:JsonProperty("database")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 3, "examples": ["AIRBYTE_DATABASE"]}"""
    )
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        """Enter the name of the default <a href="https://docs.databricks.com/en/sql/language-manual/sql-ref-schema.html">schema</a> where tables will be written. If not specified, "default" will be used."""
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 4, "default": "default", "examples": ["AIRBYTE_SCHEMA"]}""",
    )
    val schema: String? = "default"

    @get:JsonSchemaTitle("CDC deletion mode")
    @get:JsonPropertyDescription(
        """Whether to execute CDC deletions as hard deletes (i.e. propagate source deletions to the destination), or soft deletes (i.e. leave a tombstone record in the destination). Defaults to hard deletes.""",
    )
    @get:JsonProperty("cdc_deletion_mode", defaultValue = "Hard delete")
    @get:JsonSchemaInject(json = """{"group": "sync_behavior", "order": 7, "always_show": true}""")
    val cdcDeletionMode: CdcDeletionMode? = null

    @get:JsonSchemaTitle("Authentication")
    @get:JsonSchemaDescription(
        "Determines the type of authentication used to connect to Databricks. OAuth2 is recommended for production use."
    )
    @get:JsonProperty("authentication")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 5}""")
    val authentication: DatabricksAuthSpecification = OAuthSpecification()

    @get:JsonSchemaTitle("Purge Staging Files and Tables")
    @get:JsonPropertyDescription(
        "Whether to delete staging files and tables after data has been loaded. Disable this option for debugging purposes."
    )
    @get:JsonProperty("purge_staging_data")
    @get:JsonSchemaInject(json = """{"group": "sync_behavior", "order": 8, "default": true}""")
    @Suppress("RedundantNullableReturnType")
    val purgeStagingData: Boolean? = true

    @get:JsonSchemaTitle("Agree to the Databricks JDBC Driver Terms & Conditions")
    @get:JsonPropertyDescription(
        """You must agree to the Databricks JDBC Driver <a href="https://databricks.com/jdbc-odbc-driver-license">Terms & Conditions</a> to use this connector.""",
    )
    @get:JsonProperty("accept_terms")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 6, "default": false}""")
    val acceptTerms: Boolean = false
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "auth_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = OAuthSpecification::class, name = "OAUTH"),
    JsonSubTypes.Type(value = PersonalAccessTokenSpecification::class, name = "BASIC"),
)
sealed class DatabricksAuthSpecification(
    @Suppress("PropertyName") @param:JsonProperty("auth_type") val auth_type: Type
) {
    /** Enumeration of possible authentication types. */
    enum class Type(@get:JsonValue val authTypeName: String) {
        OAUTH("OAUTH"),
        BASIC("BASIC"),
    }
}

@JsonSchemaTitle("OAuth2 (Recommended)")
@JsonSchemaDescription("Authentication using OAuth2 client credentials.")
class OAuthSpecification(
    @get:JsonSchemaTitle("Client ID")
    @get:JsonPropertyDescription(
        "Enter the OAuth2 client ID for your Databricks <a href=\"https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html\">service principal</a>."
    )
    @get:JsonProperty("client_id")
    @get:JsonSchemaInject(json = """{"order": 1}""")
    val clientId: String = "",
    @get:JsonSchemaTitle("Secret")
    @get:JsonPropertyDescription("Enter the OAuth2 secret associated with the client ID.")
    @get:JsonProperty("secret")
    @get:JsonSchemaInject(json = """{"order": 2, "airbyte_secret": true}""")
    val secret: String = "",
) : DatabricksAuthSpecification(Type.OAUTH)

@JsonSchemaTitle("Personal Access Token")
@JsonSchemaDescription("Authentication using a personal access token.")
class PersonalAccessTokenSpecification(
    @get:JsonSchemaTitle("Personal Access Token")
    @get:JsonPropertyDescription(
        "Enter your Databricks <a href=\"https://docs.databricks.com/en/dev-tools/auth/pat.html\">personal access token</a>."
    )
    @get:JsonProperty("personal_access_token")
    @get:JsonSchemaInject(json = """{"order": 1, "airbyte_secret": true}""")
    val personalAccessToken: String = "",
) : DatabricksAuthSpecification(Type.BASIC)

/** Determines how CDC deletions are handled at the destination. */
enum class CdcDeletionMode(@get:JsonValue val cdcDeletionMode: String) {
    HARD_DELETE("Hard delete"),
    SOFT_DELETE("Soft delete"),
}

@Singleton
class DatabricksSpecificationExtension : DestinationSpecificationExtension {
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
        )
}
