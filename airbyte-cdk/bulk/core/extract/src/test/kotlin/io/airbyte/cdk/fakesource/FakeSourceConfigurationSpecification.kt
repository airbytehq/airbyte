/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.fakesource

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
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/** [ConfigurationSpecification] implementation for a fake source. */
@JsonSchemaTitle("Test Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "database",
            "schemas",
            "tunnel_method",
            "cursor",
        ],
)
@Singleton
@Secondary
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class FakeSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonSchemaDefault("localhost")
    @JsonPropertyDescription("Hostname of the database.")
    var host: String = "localhost"

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("9092")
    @JsonPropertyDescription("Port of the database.")
    var port: Int = 9092

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("Name of the database.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonPropertyDescription("The list of schemas to sync from. Defaults to PUBLIC.")
    @JsonSchemaInject(json = """{"order":4,"minItems":1,"uniqueItems":true}""")
    var schemas: List<String>? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration?) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database," +
            " and if so, which kind of authentication to use.",
    )
    @JsonSchemaInject(json = """{"order":5}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "cursor")
    val cursor = MicronautPropertiesFriendlyCursorConfiguration()

    @JsonIgnore var cursorJson: CursorConfiguration? = null

    @JsonSetter("cursor")
    fun setCursorMethodValue(value: CursorConfiguration?) {
        cursorJson = value
    }

    @JsonGetter("cursor")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":6,"display_type":"radio"}""")
    fun getCursorConfigurationValue(): CursorConfiguration? =
        cursorJson ?: cursor.asCursorConfiguration()

    @JsonProperty("resumable_preferred")
    @JsonSchemaDefault("true")
    @JsonSchemaInject(json = """{"order":7,"display_type":"check"}""")
    var resumablePreferred: Boolean? = true

    @JsonProperty("timeout")
    @JsonSchemaDefault("PT0S")
    @JsonSchemaInject(json = """{"order":8}""")
    var timeout: String? = "PT0S"

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
    JsonSubTypes.Type(value = UserDefinedCursor::class, name = "user_defined"),
    JsonSubTypes.Type(value = CdcCursor::class, name = "cdc"),
)
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface CursorConfiguration

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
data object UserDefinedCursor : CursorConfiguration

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
data object CdcCursor : CursorConfiguration

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfiguration {
    var cursorMethod: String = "user_defined"

    fun asCursorConfiguration(): CursorConfiguration =
        when (cursorMethod) {
            "user_defined" -> UserDefinedCursor
            "cdc" -> CdcCursor
            else -> throw ConfigErrorException("invalid value $cursorMethod")
        }
}
