/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.interpolation.StringInterpolator
import io.airbyte.cdk.load.interpolation.toInterpolationContext
import java.util.function.Predicate

/** A convenient wrapper in order to evaluate DiscoveredProperties */
class JsonNodePredicate(private val condition: String, private val nodeKey: String = "property") :
    Predicate<JsonNode> {
    val interpolator: StringInterpolator = StringInterpolator()

    override fun test(propertyNode: JsonNode): Boolean {
        return interpolator
            .interpolate(condition, mapOf(nodeKey to propertyNode.toInterpolationContext()))
            .toBoolean()
    }
}
