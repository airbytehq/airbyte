package io.airbyte.cdk.load.model.writer

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.destination_import_mode.DestinationImportMode


data class WritableObject(@JsonProperty("name") val name: String, @JsonProperty("operation") val operation: DestinationImportMode)
