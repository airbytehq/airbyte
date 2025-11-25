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
    @JsonIgnore private var flavorInternal: FlavorSpec = Incremental // default

    @JsonIgnore private var flavorJson: FlavorSpec? = null

    @JsonSetter("flavor")
    fun setFlavor(value: FlavorSpec) {
        flavorJson = value
    }

    @JsonGetter("flavor")
    @JsonSchemaTitle("Data Generation Type")
    @JsonSchemaDescription("Different patterns for generating data")
    @JsonSchemaInject(json = """{"default":"increment","display_type":"radio"}""")
    fun getFlavor(): FlavorSpec = flavorJson ?: flavorInternal

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Max Concurrency")
    @JsonSchemaDescription(
        "Maximum number of concurrent data generators. Leave empty to let Airbyte optimize performance."
    )
    var concurrency: Int? = null

    @JsonProperty("max_records")
    @JsonSchemaTitle("Max Record")
    @JsonSchemaDescription(
        "The number of record messages to emit from this connector. Min 1. Max 100 billion."
    )
    @JsonSchemaInject(json = """{"default":"100"}""")
    var maxRecords: Long = 100
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "data_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = Incremental::class, name = "increment"),
    JsonSubTypes.Type(value = Types::class, name = "types"),
)
@JsonSchemaTitle("Data Type")
@JsonSchemaDescription("Configures what kind of data is generated for the source.")
sealed interface FlavorSpec

@JsonSchemaTitle("Incremental")
@JsonSchemaDescription(
    "Generates incrementally increasing numerical data for the source.",
)
data object Incremental : FlavorSpec

@JsonSchemaTitle("All Types")
@JsonSchemaDescription(
    "Generates one column of each Airbyte data type.",
)
data object Types : FlavorSpec
