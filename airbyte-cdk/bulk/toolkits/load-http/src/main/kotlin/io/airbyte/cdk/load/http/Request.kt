/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

data class Request(
    val method: RequestMethod,
    val url: String,
    val headers: Map<String, String> = mapOf(),
    val query: Map<String, List<String>> = mapOf(),
    val body: ByteArray? = null,
)
