/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.destination_import_mode

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo

/** Base interface for all record sync modes in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = Append::class, name = "Append"),
    JsonSubTypes.Type(value = Dedupe::class, name = "Dedupe"),
    JsonSubTypes.Type(value = Overwrite::class, name = "Overwrite"),
    JsonSubTypes.Type(value = Update::class, name = "Update"),
    JsonSubTypes.Type(value = SoftDelete::class, name = "SoftDelete"),
)
sealed interface DestinationImportMode

data object Append : DestinationImportMode

data object Overwrite : DestinationImportMode

data object Update : DestinationImportMode

data object SoftDelete : DestinationImportMode

/** Configuration for the Dedupe destination sync mode */
data class Dedupe(
    @JsonProperty("primary_key") val primaryKey: List<List<String>>? = null,
    @JsonProperty("cursor") val cursor: List<String>? = null
) : DestinationImportMode
