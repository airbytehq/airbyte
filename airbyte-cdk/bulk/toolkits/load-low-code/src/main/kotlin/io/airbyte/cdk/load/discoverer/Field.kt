/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.FieldType
import java.util.function.Predicate

/** Potential improvement: memoize at least isMatchingKey as it will be called multiple times */
class Field(
    private val apiRepresentation: JsonNode,
    namePath: List<String>,
    private val typePath: List<String>,
    matchingKeyPredicate: Predicate<JsonNode>,
    availabilityPredicate: Predicate<JsonNode>,
    requiredPredicate: Predicate<JsonNode>,
    private val typeMapper: Map<String, FieldType>,
) {
    private val name: String = apiRepresentation.extract(namePath).asText()
    private val matchingKey: Boolean = matchingKeyPredicate.test(apiRepresentation)
    private val availability: Boolean = availabilityPredicate.test(apiRepresentation)
    private val required: Boolean = requiredPredicate.test(apiRepresentation)

    fun getName(): String = name

    fun getType(): FieldType {
        val apiType = apiRepresentation.extract(typePath).asText()
        return typeMapper[apiType] ?: throw IllegalStateException("Unknown type $apiType")
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
