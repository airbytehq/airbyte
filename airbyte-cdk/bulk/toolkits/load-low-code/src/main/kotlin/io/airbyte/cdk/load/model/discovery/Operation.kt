/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discovery

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.model.destination_import_mode.DestinationImportMode

/** Base interface for all operation types in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = CompositeOperations::class, name = "CompositeOperations"),
    JsonSubTypes.Type(value = StaticOperation::class, name = "StaticOperation")
)
sealed interface Operation

/**
 * Configuration for destination check operations. Performs a HTTP request to the destination API to
 * check if the configuration is valid.
 */
data class CompositeOperations(@JsonProperty("operations") val operations: List<StaticOperation>) :
    Operation

/**
 * Configuration for destination discovery operations which use a static schema where operations and
 * schema are known at compile time.
 */
data class StaticOperation(
    @JsonProperty("object_name") val objectName: String,
    @JsonProperty("destination_import_mode") val destinationImportMode: DestinationImportMode,
    @JsonProperty("schema") val schema: JsonNode,
    @JsonProperty("matching_keys") val matchingKeys: List<List<String>>? = null,
) : Operation
