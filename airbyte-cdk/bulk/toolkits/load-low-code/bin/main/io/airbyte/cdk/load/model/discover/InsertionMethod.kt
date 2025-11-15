/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discover

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.destination_import_mode.DestinationImportMode

/**
 * Component that defines the details of a specific operation will perform the insertion such as
 * sync mode and field predicates.
 *
 * Note: The `availability_predicate` and `required_predicate` are currently marked as required
 * fields. We suspect that they can be optional fields with assumed default behavior:
 * - availability_predicate: Defaults to always available `Predicate { _ -> true }`
 * - required_predicate: Defaults to all fields are not required `Predicate { _ -> false }`
 *
 * Even though we know what sensible defaults should be and could make these optional, we are
 * leaving them required because it is easier later down the line to make a required field optional
 * instead of vice versa which would be breaking. We can change this later to improve DX.
 */
data class InsertionMethod(
    @JsonProperty("type") val type: String = "InsertionMethod",
    @JsonProperty("destination_import_mode") val destinationImportMode: DestinationImportMode,
    @JsonProperty("availability_predicate")
    val availabilityPredicate: String, // See above about why this is required
    @JsonProperty("matching_key_predicate") val matchingKeyPredicate: String? = null,
    @JsonProperty("required_predicate")
    val requiredPredicate: String, // See above about why this is required
)
