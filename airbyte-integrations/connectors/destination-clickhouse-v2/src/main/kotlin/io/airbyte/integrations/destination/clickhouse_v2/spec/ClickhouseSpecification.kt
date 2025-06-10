/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class ClickhouseSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Hostname")
    @get:JsonPropertyDescription("Hostname of the database.")
    @get:JsonProperty("hostname")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val hostname: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("HTTP port of the database. Default(s) HTTP: 8123 — HTTPS: 8443")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"order": 1}""")
    val port: String = "8443"

    @get:JsonSchemaTitle("Protocol")
    @get:JsonPropertyDescription("Protocol for the database connection string.")
    @get:JsonProperty("protocol")
    @get:JsonSchemaInject(json = """{"order": 2, "airbyte_hidden": true, "default": "https"}""")
    val protocol: ClickhouseConnectionProtocol = ClickhouseConnectionProtocol.HTTPS

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the database.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 3}""")
    val database: String = "default"

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to use to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 4}""")
    val username: String = "default"

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 5, "airbyte_secret": true}""")
    val password: String = ""
}

enum class ClickhouseConnectionProtocol(@get:JsonValue val value: String) {
    HTTP("http"),
    HTTPS("https")
}

@Singleton
class ClickhouseV2SpecificationExtension : DestinationSpecificationExtension {
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
