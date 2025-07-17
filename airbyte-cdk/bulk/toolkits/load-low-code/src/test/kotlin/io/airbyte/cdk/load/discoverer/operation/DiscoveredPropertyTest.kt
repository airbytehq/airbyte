/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.util.Jsons
import java.util.function.Predicate
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DiscoveredPropertyTest {

    companion object {
        val NAME_PATH = "name"
        val A_NAME = "a-name"
        val TYPE_PATH = "name"
        val A_TYPE = "type"
        val AN_API_REPRESENTATION = Jsons.objectNode().put(NAME_PATH, A_NAME).put(TYPE_PATH, A_TYPE)
        val ANY_PREDICATE: Predicate<JsonNode> = Predicate { _ -> false }
        val FALSE_PREDICATE: Predicate<JsonNode> = Predicate { _ -> false }
        val TRUE_PREDICATE: Predicate<JsonNode> = Predicate { _ -> true }
    }

    @Test
    internal fun `test given name path does not exist when init then throw illegal argument exception`() {
        assertFailsWith<IllegalArgumentException> {
            aProperty(
                apiRepresentation = AN_API_REPRESENTATION,
                namePath = listOf("invalid name path"),
            )
        }
    }

    @Test
    internal fun `test given type path does not exist when init then throw illegal argument exception`() {
        assertFailsWith<IllegalArgumentException> {
            aProperty(
                apiRepresentation = AN_API_REPRESENTATION,
                typePath = listOf("invalid type path"),
            )
        }
    }

    @Test
    internal fun `test given unknown type when getType then throw illegal argument exception`() {
        val property =
            aProperty(
                apiRepresentation = AN_API_REPRESENTATION.put(TYPE_PATH, "unknown type"),
                typePath = listOf(TYPE_PATH),
                typeMapper = mapOf(A_TYPE to StringType),
            )
        assertFailsWith<IllegalStateException> { property.getType() }
    }

    @Test
    internal fun `test given not a matching key when isMatchingKey then return false`() {
        val property = aProperty(matchingKeyPredicate = FALSE_PREDICATE)
        assertFalse(property.isMatchingKey())
    }

    @Test
    internal fun `test given matching key when isMatchingKey then return true`() {
        val property = aProperty(matchingKeyPredicate = TRUE_PREDICATE)
        assertTrue(property.isMatchingKey())
    }

    @Test
    internal fun `test given is matching key when isAvailable then return true`() {
        val property =
            aProperty(
                matchingKeyPredicate = TRUE_PREDICATE,
                availabilityPredicate = FALSE_PREDICATE,
            )
        assertTrue(property.isAvailable())
    }

    @Test
    internal fun `test given availability is true when isAvailable then return true`() {
        val property =
            aProperty(
                matchingKeyPredicate = FALSE_PREDICATE,
                availabilityPredicate = TRUE_PREDICATE,
            )
        assertTrue(property.isAvailable())
    }

    @Test
    internal fun `test given not matching key nor available when isAvailable then return false`() {
        val property =
            aProperty(
                matchingKeyPredicate = FALSE_PREDICATE,
                availabilityPredicate = FALSE_PREDICATE,
            )
        assertFalse(property.isAvailable())
    }

    @Test
    internal fun `test given matching key and required when isRequired then return false`() {
        val property =
            aProperty(
                matchingKeyPredicate = TRUE_PREDICATE,
                requiredPredicate = TRUE_PREDICATE,
            )
        assertFalse(property.isRequired())
    }

    @Test
    internal fun `test given not matching key but not required when isRequired then return false`() {
        val property =
            aProperty(
                matchingKeyPredicate = FALSE_PREDICATE,
                requiredPredicate = FALSE_PREDICATE,
            )
        assertFalse(property.isRequired())
    }

    @Test
    internal fun `test given not matching key and required when isRequired then return true`() {
        val property =
            aProperty(
                matchingKeyPredicate = FALSE_PREDICATE,
                requiredPredicate = TRUE_PREDICATE,
            )
        assertTrue(property.isRequired())
    }

    private fun aProperty(
        apiRepresentation: JsonNode = AN_API_REPRESENTATION,
        namePath: List<String> = listOf(NAME_PATH),
        typePath: List<String> = listOf(TYPE_PATH),
        matchingKeyPredicate: Predicate<JsonNode> = ANY_PREDICATE,
        availabilityPredicate: Predicate<JsonNode> = ANY_PREDICATE,
        requiredPredicate: Predicate<JsonNode> = ANY_PREDICATE,
        typeMapper: Map<String, AirbyteType> = mapOf(A_TYPE to StringType),
    ): DiscoveredProperty {
        return DiscoveredProperty(
            apiRepresentation,
            namePath,
            typePath,
            matchingKeyPredicate,
            availabilityPredicate,
            requiredPredicate,
            typeMapper
        )
    }
}
