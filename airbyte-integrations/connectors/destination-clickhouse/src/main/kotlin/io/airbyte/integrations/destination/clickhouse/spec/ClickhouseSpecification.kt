/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

sealed class ClickhouseSpecification : ConfigurationSpecification() {
    abstract val hostname: String
    abstract val port: String
    abstract val protocol: ClickhouseConnectionProtocol
    abstract val database: String
    abstract val username: String
    abstract val password: String
    abstract val enableJson: Boolean?
}

@Singleton
@Requires(notEnv = [AIRBYTE_CLOUD_ENV])
class ClickhouseSpecificationOss : ClickhouseSpecification() {
    @get:JsonSchemaTitle("Hostname")
    @get:JsonPropertyDescription("Hostname of the database.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    override val hostname: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("HTTP port of the database. Default(s) HTTP: 8123 — HTTPS: 8443")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"order": 1, "default": "8443"}""")
    override val port: String = "8443"

    @get:JsonSchemaTitle("Protocol")
    @get:JsonPropertyDescription("Protocol for the database connection string.")
    @get:JsonProperty("protocol")
    @get:JsonSchemaInject(json = """{"order": 2, "default": "https"}""")
    override val protocol: ClickhouseConnectionProtocol = ClickhouseConnectionProtocol.HTTPS

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the database.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 3, "default": "default"}""")
    override val database: String = "default"

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to use to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 4, "default": "default"}""")
    override val username: String = "default"

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 5, "airbyte_secret": true}""")
    override val password: String = ""

    @get:JsonSchemaTitle("Enable JSON")
    @get:JsonPropertyDescription(
        "Use the JSON type for Object fields. If disabled, the JSON will be converted to a string."
    )
    @get:JsonProperty("enable_json")
    @get:JsonSchemaInject(json = """{"order": 6, "default": false}""")
    override val enableJson: Boolean? = false
}

@Singleton
@Requires(env = [AIRBYTE_CLOUD_ENV])
open class ClickhouseSpecificationCloud : ClickhouseSpecification() {
    @get:JsonSchemaTitle("Hostname")
    @get:JsonPropertyDescription("Hostname of the database.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    override val hostname: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("HTTP port of the database. Default(s) HTTP: 8123 — HTTPS: 8443")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"order": 1, "default": "8443"}""")
    override val port: String = "8443"

    @get:JsonSchemaTitle("Protocol")
    @get:JsonPropertyDescription("Protocol for the database connection string.")
    @get:JsonProperty("protocol")
    @get:JsonSchemaInject(json = """{"order": 2, "default": "https", "airbyte_hidden": true}""")
    override val protocol: ClickhouseConnectionProtocol = ClickhouseConnectionProtocol.HTTPS

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the database.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 3, "default": "default"}""")
    override val database: String = "default"

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to use to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 4, "default": "default"}""")
    override val username: String = "default"

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 5, "airbyte_secret": true}""")
    override val password: String = ""

    @get:JsonSchemaTitle("Enable JSON")
    @get:JsonPropertyDescription(
        "Use the JSON type when possible. If disabled, the JSON will be converted to a string."
    )
    @get:JsonProperty("enable_json")
    @get:JsonSchemaInject(json = """{"order": 6, "default": false}""")
    override val enableJson: Boolean? = false
}

enum class ClickhouseConnectionProtocol(@get:JsonValue val value: String) {
    HTTP("http"),
    HTTPS("https")
}

@Singleton
class ClickhouseSpecificationExtension : DestinationSpecificationExtension {
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
