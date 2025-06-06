package io.airbyte.cdk.load.http

import java.io.InputStream


data class Response(
    val statusCode: Int,
    val headers: Map<String, List<String>>,
    val body: InputStream?,
)
