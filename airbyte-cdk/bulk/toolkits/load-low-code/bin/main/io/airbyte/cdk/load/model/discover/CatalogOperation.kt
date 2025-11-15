/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discover

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.model.destination_import_mode.DestinationImportMode
import io.airbyte.cdk.load.model.retriever.Retriever

/** Base interface for all operation types in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = CompositeCatalogOperations::class,
        name = "CompositeCatalogOperations"
    ),
    JsonSubTypes.Type(value = DynamicCatalogOperation::class, name = "DynamicCatalogOperation"),
    JsonSubTypes.Type(value = StaticCatalogOperation::class, name = "StaticCatalogOperation")
)
sealed interface CatalogOperation

/**
 * Configuration for destination check operations. Performs a HTTP request to the destination API to
 * check if the configuration is valid.
 */
data class CompositeCatalogOperations(
    @JsonProperty("operations") val operations: List<CatalogOperation>
) : CatalogOperation

/**
 * Configuration for destination discovery operations which use a static schema where operations and
 * schema are known at compile time.
 */
data class StaticCatalogOperation(
    @JsonProperty("object_name") val objectName: String,
    @JsonProperty("destination_import_mode") val destinationImportMode: DestinationImportMode,
    @JsonProperty("schema") val schema: JsonNode,
    @JsonProperty("matching_keys") val matchingKeys: List<List<String>>? = null,
) : CatalogOperation

/**
 * Configuration for destination discovery operations which use a dynamic schema where operations
 * and schema are derived by accessing the API
 */
data class DynamicCatalogOperation(
    @JsonProperty("objects") val objects: DestinationObjects,
    @JsonProperty("schema") val schema: SchemaConfiguration,
    @JsonProperty("schema_retriever") val schemaRetriever: Retriever? = null,
    @JsonProperty("insertion_methods") val insertionMethods: List<InsertionMethod>,
) : CatalogOperation
