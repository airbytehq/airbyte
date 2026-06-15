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
    @get:JsonPropertyDescription("Databricks Cluster Server Hostname.")
    @get:JsonProperty("hostname")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 2, "examples": ["abc-12345678-wxyz.cloud.databricks.com"]}"""
    )
    val hostname: String = ""

    @get:JsonSchemaTitle("HTTP Path")
    @get:JsonPropertyDescription("Databricks Cluster HTTP Path.")
    @get:JsonProperty("http_path")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 3, "examples": ["sql/1.0/warehouses/0000-1111111-abcd90"]}"""
    )
    val httpPath: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("Databricks Cluster Port.")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(
        json = """{"group": "advanced", "order": 4, "default": "443", "examples": ["443"]}"""
    )
    val port: String = "443"

    @get:JsonSchemaTitle("Databricks Unity Catalog Name")
    @get:JsonPropertyDescription("The name of the unity catalog for the database")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 5}""")
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        """The default schema tables are written. If not specified otherwise, the "default" will be used."""
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(
        json =
            """{"group": "advanced", "order": 6, "default": "default", "examples": ["default"]}"""
    )
    val schema: String = "default"

    @get:JsonSchemaTitle("CDC deletion mode")
    @get:JsonPropertyDescription(
        """Whether to execute CDC deletions as hard deletes (i.e. propagate source deletions to the destination), or soft deletes (i.e. leave a tombstone record in the destination). Defaults to hard deletes.""",
    )
    @get:JsonProperty("cdc_deletion_mode", defaultValue = "Hard delete")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 7, "always_show": true}""")
    val cdcDeletionMode: CdcDeletionMode? = null

    @get:JsonSchemaTitle("Authentication")
    @get:JsonSchemaDescription("Authentication mechanism for Staging files and running queries")
    @get:JsonProperty("authentication")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 8}""")
    val authentication: DatabricksAuthSpecification? = null

    @get:JsonSchemaTitle("Purge Staging Files and Tables")
    @get:JsonPropertyDescription("Default to 'true'. Switch it to 'false' for debugging purpose.")
    @get:JsonProperty("purge_staging_data")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 9, "default": true}""")
    @Suppress("RedundantNullableReturnType")
    val purgeStagingData: Boolean? = true

    @get:JsonSchemaTitle("Agree to the Databricks JDBC Driver Terms & Conditions")
    @get:JsonPropertyDescription(
        """You must agree to the Databricks JDBC Driver <a href="https://databricks.com/jdbc-odbc-driver-license">Terms & Conditions</a> to use this connector.""",
    )
    @get:JsonProperty("accept_terms")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 10, "default": false}""")
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
    enum class Type(@get:JsonValue val authTypeName: String) {
        OAUTH("OAUTH"),
        BASIC("BASIC"),
    }
}

@JsonSchemaTitle("OAuth2 (Recommended)")
@JsonSchemaDescription("Authentication using OAuth2 client credentials.")
class OAuthSpecification(
    @get:JsonSchemaTitle("Client ID")
    @get:JsonProperty("client_id")
    @get:JsonSchemaInject(json = """{"order": 1}""")
    val clientId: String = "",
    @get:JsonSchemaTitle("Secret")
    @get:JsonProperty("secret")
    @get:JsonSchemaInject(json = """{"order": 2, "airbyte_secret": true}""")
    val secret: String = "",
) : DatabricksAuthSpecification(Type.OAUTH)

@JsonSchemaTitle("Personal Access Token")
@JsonSchemaDescription("Authentication using a personal access token.")
class PersonalAccessTokenSpecification(
    @get:JsonSchemaTitle("Personal Access Token")
    @get:JsonProperty("personal_access_token")
    @get:JsonSchemaInject(json = """{"order": 1, "airbyte_secret": true}""")
    val personalAccessToken: String = "",
) : DatabricksAuthSpecification(Type.BASIC)

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
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}
