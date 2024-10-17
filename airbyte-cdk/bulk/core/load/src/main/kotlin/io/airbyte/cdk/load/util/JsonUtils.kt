/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper

fun JsonNode.serializeToString(): String {
    return ObjectMapper().writeValueAsString(this)
}

fun String.deserializeToNode(): JsonNode {
    return ObjectMapper().readTree(this)
}
