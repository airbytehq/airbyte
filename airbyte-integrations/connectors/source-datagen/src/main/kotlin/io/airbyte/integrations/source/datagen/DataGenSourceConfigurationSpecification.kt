/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the DataGen source configuration JSON.
 *
 * Use [DataGenSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@Singleton
class DataGenSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "flavor")
    var catalogType = MicronautPropertiesFriendlyCatalogConfigurationSpecification() // default

    @JsonIgnore private var flavorJson: FlavorSpec? = null

    @JsonSetter("flavor")
    fun setFlavor(value: FlavorSpec) {
        flavorJson = value
    }

    @JsonGetter("flavor")
    @JsonSchemaTitle("Data Generation Flavors")
    @JsonSchemaDescription("Different patterns for generating data")
    @JsonSchemaInject(json = """{"order":1,"default":"continuous","display_type":"dropdown"}""")
    fun getFlavor(): FlavorSpec = flavorJson ?: catalogType.asCursorMethodConfiguration()

    @JsonProperty("max_records")
    @JsonSchemaTitle("Max Record")
    @JsonSchemaDescription(
        "The number of record messages to emit from this connector. Min 1. Max 100 billion."
    )
    @JsonSchemaInject(json = """{"order":2,"default":"100","minimum": 1,"maximum": 100000000000}""")
    var maxRecords: Long = 100

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Max Concurrent Queries to Database")
    @JsonSchemaDescription(
        "Maximum number of concurrent queries to the database. Leave empty to let Airbyte optimize performance."
    )
    @JsonSchemaInject(json = """{"order":3}""")
    var concurrency: Int? = null

    @JsonProperty("duplicate_record")
    @JsonSchemaTitle("Record Duplicates")
    @JsonSchemaDescription(
        "Whether we should emit duplicate records."
    )
    @JsonSchemaInject(json = """{"order":5,"default":false}""")
    var duplicateProportion: Boolean = false

}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "data_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = Incremental::class, name = "continuous"),
)
@JsonSchemaTitle("Feed Type")
@JsonSchemaDescription("Configures what kind of data is generated for the source.")
sealed interface FlavorSpec

@JsonSchemaTitle("Single Schema")
class Incremental: FlavorSpec{
    @JsonProperty("stream_name")
    @JsonSchemaDescription("Name of the data stream.")
    @JsonSchemaInject(json = """{"default": "data_stream"}""")
    var streamName: String = "data_stream"

    @JsonProperty("stream_schema")
    @JsonSchemaDescription("A JSON schema for the stream.")
    @JsonSchemaInject(json = """{"default": "{\"type\": \"object\", \"properties\": {\"id\": {\"airbyte_type\": \"integer\"}, {\"type\": \"number\"}}"}"}""")
    val streamSchema: String = "{ \"type\": \"object\", \"properties\": { \"column1\": { \"type\": \"string\" } } }"
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.flavor")
class MicronautPropertiesFriendlyCatalogConfigurationSpecification {
    var method: String = "Single Schema"

    fun asCursorMethodConfiguration(): FlavorSpec =
        when (method) {
            "Single Schema" -> Incremental()
            // "CDC" -> Cdc()
            else -> throw ConfigErrorException("invalid value $method")
        }
}
