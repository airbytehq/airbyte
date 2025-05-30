package io.airbyte.cdk.load.http

import okio.BufferedSource


data class Response(
    val statusCode: Int,
    val headers: Map<String, List<String>>,  // FIXME I would have assume a type of Map<String, String> here but okhttp3.Response.toMultiMap
    val body: BufferedSource?,
)
