/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons

fun JsonNode.serializeToString(): String {
    return Jsons.writeValueAsString(this)
}

fun String.deserializeToNode(): JsonNode {
    return Jsons.readTree(this)
}
