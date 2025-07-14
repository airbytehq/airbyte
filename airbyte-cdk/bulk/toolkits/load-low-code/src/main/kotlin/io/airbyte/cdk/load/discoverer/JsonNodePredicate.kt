package io.airbyte.cdk.load.discoverer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.interpolation.StringInterpolator
import io.airbyte.cdk.load.interpolation.toInterpolationContext
import java.util.function.Predicate

class JsonNodePredicate(private val condition: String) : Predicate<JsonNode> {
    val interpolator: StringInterpolator = StringInterpolator()

    override fun test(fieldNode: JsonNode): Boolean {
        return interpolator
            .interpolate(condition, mapOf("field" to fieldNode.toInterpolationContext()))
            .toBoolean()
    }
}
