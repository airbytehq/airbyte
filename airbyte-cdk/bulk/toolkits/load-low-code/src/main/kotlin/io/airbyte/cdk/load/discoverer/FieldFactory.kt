/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteType
import java.util.function.Predicate

class FieldFactory(
    private val namePath: List<String>,
    private val typePath: List<String>,
    private val matchingKeyPredicate: Predicate<JsonNode>,
    private val availabilityPredicate: Predicate<JsonNode>,
    private val requiredPredicate: Predicate<JsonNode>,
    private val typeMapper: Map<String, AirbyteType>,
) {
    fun create(apiRepresentation: JsonNode): Field {
        return Field(
            apiRepresentation,
            namePath,
            typePath,
            matchingKeyPredicate,
            availabilityPredicate,
            requiredPredicate,
            typeMapper,
        )
    }
}
