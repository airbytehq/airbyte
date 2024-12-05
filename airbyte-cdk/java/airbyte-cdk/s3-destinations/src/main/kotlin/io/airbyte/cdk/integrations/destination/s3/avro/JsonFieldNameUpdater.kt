/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.commons.json.Jsons

/**
 * This helper class is for testing only. It tracks the original and standardized names, and revert
 * them when necessary, so that the tests can correctly compare the generated json with the original
 * input.
 */
class JsonFieldNameUpdater(standardizedNames: Map<String, String>) {
    // A map from original name to standardized name.
    private val standardizedNames: Map<String, String> = ImmutableMap.copyOf(standardizedNames)

    fun getJsonWithOriginalFieldNames(input: JsonNode): JsonNode {
        if (standardizedNames.size == 0) {
            return input
        }
        var jsonString = Jsons.serialize(input)
        for ((key, value) in standardizedNames) {
            jsonString = jsonString.replace(quote(value).toRegex(), quote(key))
        }
        return Jsons.deserialize(jsonString)
    }

    override fun toString(): String {
        return standardizedNames.toString()
    }

    companion object {
        private fun quote(input: String): String {
            return "\"" + input + "\""
        }
    }
}
