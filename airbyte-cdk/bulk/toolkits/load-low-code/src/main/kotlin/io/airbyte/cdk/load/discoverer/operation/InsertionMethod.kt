/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.AirbyteType
import java.util.function.Predicate

/**
 * Describes the information related to how data is inserted in an object.
 *
 * Note that if matchingKeyPredicate is provided, it needs to return `true` to at least one of the
 * properties. If this is not the case, the insertion method for this object will not be returned as
 * part of the discover command. If not provided, it means that it is expected not to have matching
 * keys.
 */
class InsertionMethod(
    private val importType: ImportType,
    private val namePath: List<String>,
    private val typePath: List<String>,
    private val matchingKeyPredicate: Predicate<JsonNode>?,
    private val availabilityPredicate: Predicate<JsonNode>,
    private val requiredPredicate: Predicate<JsonNode>,
    private val typeMapper: Map<String, AirbyteType>,
) {
    fun getImportType(): ImportType = importType

    fun createProperty(apiRepresentation: JsonNode): DiscoveredProperty {
        return DiscoveredProperty(
            apiRepresentation,
            namePath,
            typePath,
            matchingKeyPredicate ?: Predicate { _ -> false },
            availabilityPredicate,
            requiredPredicate,
            typeMapper,
        )
    }

    fun requiresMatchingKey(): Boolean {
        return matchingKeyPredicate != null
    }
}
