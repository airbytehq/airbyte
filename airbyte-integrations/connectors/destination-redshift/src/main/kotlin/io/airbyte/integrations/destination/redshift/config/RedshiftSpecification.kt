/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.config

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSetter
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.ConfigurationBuilder
import jakarta.inject.Singleton

/**
 * Redshift destination specification. Supports backward compatibility with legacy configurations
 * via @JsonIgnoreProperties.
 */
@Singleton
@JsonSchemaTitle("Redshift Destination Spec")
@JsonIgnoreProperties(ignoreUnknown = true)
open class RedshiftSpecification : ConfigurationSpecification() {

    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription(
        "Enter your Redshift Cluster Endpoint (must include the cluster-id, region and end with .redshift.amazonaws.com)"
    )
    @get:JsonProperty("host")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 1, "examples":["my-cluster.abc123xyz.us-east-1.redshift.amazonaws.com"], "pattern": "^[^\\s/?#]+\\.redshift(-serverless)?\\.amazonaws\\.com$", "pattern_descriptor": "{cluster-id}.{random}.{region}.redshift.amazonaws.com"}"""
    )
    val host: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("Enter your Database Port")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 2, "minimum": 0, "maximum": 65536, "examples": ["5439"], "default": 5439}"""
    )
    val port: Int = 5439

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription(
        "Enter the name of the user you want to use to access the database"
    )
    @get:JsonProperty("username")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 3, "examples":["airbyte_user"]}"""
    )
    val username: String = ""

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Enter the password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 4, "airbyte_secret": true}""")
    val password: String = ""

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription(
        "Enter the name of the <a href=\"https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_DATABASE.html\">database</a> you want to sync data into"
    )
    @get:JsonProperty("database")
    @get:JsonSchemaInject(
        json = """{"group": "connection", "order": 5, "examples":["airbyte_database"]}"""
    )
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        "Enter the name of the default <a href=\"https://docs.aws.amazon.com/redshift/latest/dg/r_Schemas_and_tables.html\">schema</a> tables are written to if the source does not specify a namespace. Unless specifically configured, the usual value for this field is \"public\"."
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 6, "examples": ["public"], "default": "public"}"""
    )
    val schema: String = "public"

    @get:JsonSchemaTitle("JDBC URL Params")
    @get:JsonPropertyDescription(
        """Enter the additional properties to pass to the JDBC URL string when connecting to the database (formatted as key=value pairs separated by the symbol &). Example: key1=value1&key2=value2&key3=value3""",
    )
    @get:JsonProperty("jdbc_url_params")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 7}""")
    val jdbcUrlParams: String? = null

    @get:JsonSchemaTitle(
        "Drop tables and columns with CASCADE. (WARNING! Risk of unrecoverable data loss)"
    )
    @get:JsonPropertyDescription(
        "WARNING! This will delete all data in all dependent objects " +
            "(views, etc.) including during schema evolution of columns. Use with caution. This option is intended for usecases which can " +
            "easily rebuild the dependent objects."
    )
    @get:JsonProperty("drop_cascade")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 8, "default": false}""")
    val dropCascade: Boolean? = false

    @get:JsonSchemaTitle("Uploading Method")
    @get:JsonPropertyDescription("The way data will be uploaded to Redshift.")
    @get:JsonProperty("uploading_method")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 9, "display_type": "radio"}""")
    val uploadingMethod: S3StagingConfiguration? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore
    var tunnelMethodJson: SshTunnelMethodConfiguration? = null
        private set

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration?) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, and if so, which kind of authentication to use."
    )
    @JsonSchemaInject(json = """{"group": "connection", "order": 10}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()
}

/** Destination specification extension that declares the supported sync modes. */
@Singleton
class RedshiftSpecificationExtension : DestinationSpecificationExtension {
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
