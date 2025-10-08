/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.destination_import_mode

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo

/** Base interface for all record sync modes in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = Insert::class, name = "Insert"),
    JsonSubTypes.Type(value = Upsert::class, name = "Upsert"),
    JsonSubTypes.Type(value = Update::class, name = "Update"),
    JsonSubTypes.Type(value = SoftDelete::class, name = "SoftDelete"),
)
sealed interface DestinationImportMode

data object Insert : DestinationImportMode

data object Update : DestinationImportMode

data object SoftDelete : DestinationImportMode

data object Upsert : DestinationImportMode
