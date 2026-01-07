/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@JsonSchemaTitle("Dev Null Destination Spec V2")
@Singleton
class DevNullV2Specification : ConfigurationSpecification() {
    
    @JsonProperty("mode")
    @JsonSchemaTitle("Operation Mode")
    @JsonPropertyDescription("How the destination should handle records")
    val mode: String = "silent"
    
    @JsonProperty("log_every_n")
    @JsonSchemaTitle("Log Every N Records")
    @JsonPropertyDescription("Log every Nth record (only applies in logging mode)")
    val logEveryN: Int = 1000
}

@Singleton
class DevNullV2SpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes = listOf(
        DestinationSyncMode.OVERWRITE,
        DestinationSyncMode.APPEND,
        DestinationSyncMode.APPEND_DEDUP
    )
    
    override val supportsIncremental = true
}