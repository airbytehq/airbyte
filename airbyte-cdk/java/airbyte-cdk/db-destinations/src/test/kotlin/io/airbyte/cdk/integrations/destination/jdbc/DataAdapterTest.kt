/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import java.util.function.Function
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class DataAdapterTest {
    private val testData: JsonNode =
        Jsons.deserialize(
            "{\"attr1\" : \"CCC\", \"obj1\" : [{\"sub1\" : \"BBB\"}, {\"sub1\" : \"CCC\"}]}"
        )
    private val replaceCCCFunction = Function { jsonNode: JsonNode ->
        if (jsonNode.isTextual) {
            val textValue = jsonNode.textValue().replace("CCC".toRegex(), "FFF")
            return@Function Jsons.jsonNode<String>(textValue)
        } else return@Function jsonNode
    }

    @Test
    fun checkSkipAll() {
        val data = testData.deepCopy<JsonNode>()
        val adapter = DataAdapter({ jsonNode: JsonNode? -> false }, replaceCCCFunction)
        adapter.adapt(data)

        Assertions.assertEquals(testData, data)
    }

    @Test
    fun checkSkip() {
        val data = testData.deepCopy<JsonNode>()
        val adapter =
            DataAdapter(
                { jsonNode: JsonNode ->
                    jsonNode.isTextual && jsonNode.textValue().contains("BBB")
                },
                replaceCCCFunction
            )
        adapter.adapt(data)

        Assertions.assertEquals(testData, data)
    }

    @Test
    fun checkAdapt() {
        val data = testData.deepCopy<JsonNode>()
        val adapter =
            DataAdapter(
                { jsonNode: JsonNode ->
                    jsonNode.isTextual && jsonNode.textValue().contains("CCC")
                },
                replaceCCCFunction
            )
        adapter.adapt(data)
        println(data)

        Assertions.assertNotEquals(testData, data)
        assert(
            data.findValues("sub1").stream().anyMatch { jsonNode: JsonNode ->
                jsonNode.isTextual && jsonNode.textValue() == "FFF"
            }
        )
        assert(
            data.findValues("attr1").stream().anyMatch { jsonNode: JsonNode ->
                jsonNode.isTextual && jsonNode.textValue() == "FFF"
            }
        )
    }
}
