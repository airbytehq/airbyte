/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import java.util.function.Predicate

/**
 * Represents a property that was extracted from the API with the rules that defines the operation
 * for a specific insertion method.
 *
 * Note that a DiscoveredProperty with be different depending on the insertion method because the
 * rules to determine things like matchingKey and availability will be different.
 */
class DiscoveredProperty(
    apiRepresentation: JsonNode,
    namePath: List<String>,
    typePath: List<String>,
    matchingKeyPredicate: Predicate<JsonNode>,
    availabilityPredicate: Predicate<JsonNode>,
    requiredPredicate: Predicate<JsonNode>,
    private val typeMapper: Map<String, AirbyteType>,
) {
    private val name: String = apiRepresentation.extract(namePath).asText()
    private val apiType = apiRepresentation.extract(typePath).asText()
    private val matchingKey: Boolean = matchingKeyPredicate.test(apiRepresentation)
    private val availability: Boolean = availabilityPredicate.test(apiRepresentation)
    private val required: Boolean = requiredPredicate.test(apiRepresentation)

    fun getName(): String = name

    /**
     * [Nullability has been reverted](https://github.com/airbytehq/airbyte/pull/62854) and there
     * are no plans to move forward so we will consider everything as nullable for now
     */
    fun getType(): FieldType {
        return FieldType(
            typeMapper[apiType] ?: throw IllegalStateException("Unknown type $apiType"),
            nullable = true
        )
    }

    fun isMatchingKey(): Boolean {
        return matchingKey
    }

    fun isAvailable(): Boolean {
        return isMatchingKey() || availability
    }

    fun isRequired(): Boolean {
        return !isMatchingKey() && required
    }
}
