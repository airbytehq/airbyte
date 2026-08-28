/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.config

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

/** Firebolt destination configuration specification. */
@Singleton
@JsonSchemaTitle("Firebolt Destination Spec")
@JsonIgnoreProperties(ignoreUnknown = true)
open class FireboltSpecification : ConfigurationSpecification() {

    @get:JsonSchemaTitle("Client ID")
    @get:JsonPropertyDescription("The Firebolt service account ID.")
    @get:JsonProperty("client_id")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 0} """)
    val clientId: String = ""

    @get:JsonSchemaTitle("Client Secret")
    @get:JsonPropertyDescription("The secret for the Firebolt service account.")
    @get:JsonProperty("client_secret")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 1, "airbyte_secret": true}""")
    val clientSecret: String = ""

    @get:JsonSchemaTitle("Account")
    @get:JsonPropertyDescription("The Firebolt account name.")
    @get:JsonProperty("account")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 2}""")
    val account: String = ""

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("The Firebolt database to connect to.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 3}""")
    val database: String = ""

    @get:JsonSchemaTitle("Engine")
    @get:JsonPropertyDescription("The Firebolt engine name. If not provided, the default engine is used.")
    @get:JsonProperty("engine")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 4}""")
    val engine: String? = null

    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription("Optional Firebolt API host. Leave blank for the default endpoint.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 5}""")
    val host: String? = null

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription("The default schema tables are written to if the source does not specify a namespace.")
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 6, "examples": ["public"], "default": "public"}""")
    val schema: String = "public"

    @get:JsonSchemaTitle("JDBC URL Params")
    @get:JsonPropertyDescription("Additional properties to pass to the JDBC URL string as key=value pairs separated by '&'.")
    @get:JsonProperty("jdbc_url_params")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 7}""")
    val jdbcUrlParams: String? = null

    @get:JsonSchemaTitle("S3 Staging")
    @get:JsonPropertyDescription("S3 staging configuration for bulk loading via COPY FROM.")
    @get:JsonProperty("s3_staging")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 8}""")
    val s3Staging: S3StagingConfiguration? = null
}

/** Destination specification extension that declares supported sync modes. */
@Singleton
class FireboltSpecificationExtension : DestinationSpecificationExtension {
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
        )
}
