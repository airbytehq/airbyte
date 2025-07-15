/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import java.util.function.Predicate

class Field(
    private val apiRepresentation: JsonNode,
    namePath: List<String>,
    private val typePath: List<String>,
    matchingKeyPredicate: Predicate<JsonNode>,
    availabilityPredicate: Predicate<JsonNode>,
    requiredPredicate: Predicate<JsonNode>,
    private val typeMapper: Map<String, AirbyteType>,
) {
    private val name: String = apiRepresentation.extract(namePath).asText()
    private val matchingKey: Boolean = matchingKeyPredicate.test(apiRepresentation)
    private val availability: Boolean = availabilityPredicate.test(apiRepresentation)
    private val required: Boolean = requiredPredicate.test(apiRepresentation)

    fun getName(): String = name

    /**
     * [Nullability has been reverted](https://github.com/airbytehq/airbyte/pull/62854) and there are no plans to move forward so we will consider everything as nullable for now
     */
    fun getType(): FieldType {
        val apiType = apiRepresentation.extract(typePath).asText()
        return FieldType(typeMapper[apiType] ?: throw IllegalStateException("Unknown type $apiType"), nullable = true)
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
