package io.airbyte.cdk.load.http

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.interpolation.toInterpolationContext

/**
 * This class should be used only for responses that can be fully put in memory. Streamable
 * responses like CSV should avoid this implementation to improve memory usage.
 */
class InterpolableResponse(
    private val statusCode: Int,
    private val headers: Map<String, List<String>>,
    val body: JsonNode,
) {
    fun getContext(): Map<String, Any> {
        return mapOf(
            "status_code" to statusCode,
            "headers" to headers,
            "body" to body.toInterpolationContext(),
        )
    }
}
