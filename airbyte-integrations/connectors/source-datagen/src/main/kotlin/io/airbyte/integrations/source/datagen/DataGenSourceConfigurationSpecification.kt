/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
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
    private var flavorInternal: FlavorSpec = Incremental // default

    @JsonIgnore
    private var flavorJson: FlavorSpec? = null

    @JsonSetter("flavor")
    fun setFlavor(value: FlavorSpec) {
        flavorJson = value
    }

    @JsonGetter("flavor")
    @JsonSchemaTitle("Data Generation Flavors")
    @JsonSchemaDescription("Different patterns for generating data")
    @JsonSchemaInject(json = """{"default":"incremental","display_type":"radio"}""")
    fun getFlavor(): FlavorSpec = flavorJson ?: flavorInternal

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonSchemaDescription("The number of concurrent jobs or threads to run.")
    @JsonSchemaDefault("1")
    @JsonSchemaInject(json = """{"display_type":"number"}""")
    var concurrency: Int = 1

    // TODO: min 1 max 100 billion
    @JsonProperty("max_records")
    @JsonSchemaTitle("Max Record")
    @JsonSchemaDescription("The maximum number of records to generate.")
    @JsonSchemaInject(json = """{"default":"100"}""")
    var maxRecords: Long = 100
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "data_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = Incremental::class, name = "incremental"),
)
@JsonSchemaTitle("Data Type")
@JsonSchemaDescription("Configures what kind of data is generated for the source.")
sealed interface FlavorSpec

@JsonSchemaTitle("Incremental")
@JsonSchemaDescription(
    "Generates incrementally increasing numerical data for the source.",
)
data object Incremental : FlavorSpec
