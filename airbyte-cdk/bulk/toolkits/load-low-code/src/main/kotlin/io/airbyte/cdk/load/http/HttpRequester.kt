/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

class HttpRequester(
    private val client: HttpClient,
    private val method: RequestMethod,
    private val url: String,
) {

    fun send(): Response {
        return client.send(
            Request(
                method = method,
                url = url
                // TODO eventually support the following
                //        val headers: Map<String, String> = mapOf(),
                //        val query: Map<String, List<String>> = mapOf(),
                //        val body: ByteArray? = null,
                )
        )
    }
}
