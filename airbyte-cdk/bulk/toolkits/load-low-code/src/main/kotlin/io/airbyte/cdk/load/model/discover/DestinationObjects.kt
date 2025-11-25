/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discover

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import io.airbyte.cdk.load.model.retriever.Retriever

/** Base interface for all destination object types in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = StaticDestinationObjects::class, name = "StaticDestinationObjects"),
    JsonSubTypes.Type(value = DynamicDestinationObjects::class, name = "DynamicDestinationObjects")
)
sealed interface DestinationObjects

/**
 * Configuration for the objects which can be written to by the destination and are known ahead of
 * time and therefore can be defined statically.
 */
data class StaticDestinationObjects(
    @JsonProperty("objects")
    val objects: List<String>, // todo: this needs to be union of String and List<String>
) : DestinationObjects

/**
 * Configuration for the objects which can be written to by the destination that are determined by
 * making requests to the destination API.
 */
data class DynamicDestinationObjects(
    @JsonProperty("retriever") val retriever: Retriever,
    @JsonProperty("name_path")
    val namePath: List<String>? =
        null, // note in PR that empty is potentially okay if all records at top level
) : DestinationObjects
