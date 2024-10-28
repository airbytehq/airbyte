/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.comparator

import com.fasterxml.jackson.databind.JsonNode
import java.util.function.Function

object ComparatorUtils {
    fun getActualValueByExpectedKey(
        expectedKey: String?,
        actualJsonNode: JsonNode,
        nameResolver: Function<String?, List<String?>>
    ): JsonNode? {
        for (actualKey in nameResolver.apply(expectedKey)) {
            if (actualJsonNode.has(actualKey)) {
                return actualJsonNode[actualKey]
            }
        }
        return null
    }
}
