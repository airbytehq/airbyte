/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

/**
 * The object which is mapped to the MySQL source configuration JSON.
 *
 * Use [MySqlSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@Singleton
class DataGenSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonSchemaTitle("Data Generation Flavors")
    @JsonSchemaDescription("Different patterns for generating data")
    sealed interface FlavorConfig {

        @JsonProperty("run_duration")
        @JsonSchemaTitle("Run Duration")
        @JsonSchemaInject(json = """{"order":1}""")
        @JsonSchemaDefault("8")
        @JsonPropertyDescription("The duration to run the data generation for before timeout.")
        val runDuration: Int

        @JsonSchemaTitle("Incremental")
        @JsonSchemaDescription("Generate data with incremental patterns and change tracking")
        data object Incremental: FlavorConfig

    }
}

//
