/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

import io.airbyte.cdk.load.interpolation.StringInterpolator

class HttpRequester(
    private val client: HttpClient,
    private val method: RequestMethod,
    private val url: String,
) {
    private val interpolator = StringInterpolator()

    fun send(interpolationContext: Map<String, Any> = emptyMap()): Response {
        return client.send(
            Request(
                method = method,
                url = interpolator.interpolate(url, interpolationContext)
                // TODO eventually support the following
                //        val headers: Map<String, String> = mapOf(),
                //        val query: Map<String, List<String>> = mapOf(),
                //        val body: ByteArray? = null,
                )
        )
    }
}
