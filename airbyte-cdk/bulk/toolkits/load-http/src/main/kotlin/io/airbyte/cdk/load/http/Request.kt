package io.airbyte.cdk.load.http

data class Request(
    val method: RequestMethod,
    val url: String,
    val headers: Map<String, String> = mapOf(),
    val params: MutableMap<String, Any> = mutableMapOf(),
    val query: MutableMap<String, List<String>> = mutableMapOf(),
    val body: ByteArray? = null,
)
