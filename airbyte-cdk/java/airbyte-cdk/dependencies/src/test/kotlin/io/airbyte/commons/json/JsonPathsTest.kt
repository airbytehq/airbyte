/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.jayway.jsonpath.PathNotFoundException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable

internal class JsonPathsTest {
    @Test
    fun testGetValues() {
        Assertions.assertEquals(
            listOf(0, 1, 2),
            JsonPaths.getValues(JSON_NODE, LIST_ALL_QUERY).map { obj: JsonNode -> obj.asInt() }
        )
        Assertions.assertEquals(
            listOf(1),
            JsonPaths.getValues(JSON_NODE, LIST_ONE_QUERY).map { obj: JsonNode -> obj.asInt() }
        )
        Assertions.assertEquals(
            listOf(10),
            JsonPaths.getValues(JSON_NODE, NESTED_FIELD_QUERY).map { obj: JsonNode -> obj.asInt() }
        )
        Assertions.assertEquals(
            JSON_NODE["two"],
            JsonPaths.getValues(JSON_NODE, JSON_OBJECT_QUERY).firstOrNull()
        )
        Assertions.assertEquals(
            emptyList<Any>(),
            JsonPaths.getValues(JSON_NODE, EMPTY_RETURN_QUERY)
        )
    }

    @Test
    fun testGetSingleValue() {
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            JsonPaths.getSingleValue(JSON_NODE, LIST_ALL_QUERY)
        }
        Assertions.assertEquals(
            1,
            JsonPaths.getSingleValue(JSON_NODE, LIST_ONE_QUERY)
                .map { obj: JsonNode -> obj.asInt() }
                .orElse(null)
        )
        Assertions.assertEquals(
            10,
            JsonPaths.getSingleValue(JSON_NODE, NESTED_FIELD_QUERY)
                .map { obj: JsonNode -> obj.asInt() }
                .orElse(null)
        )
        Assertions.assertEquals(
            JSON_NODE["two"],
            JsonPaths.getSingleValue(JSON_NODE, JSON_OBJECT_QUERY).orElse(null)
        )
        Assertions.assertNull(JsonPaths.getSingleValue(JSON_NODE, EMPTY_RETURN_QUERY).orElse(null))
    }

    @Test
    fun testGetPaths() {
        Assertions.assertEquals(
            listOf("$['one'][0]", "$['one'][1]", "$['one'][2]"),
            JsonPaths.getPaths(JSON_NODE, LIST_ALL_QUERY)
        )
        Assertions.assertEquals(
            listOf("$['one'][1]"),
            JsonPaths.getPaths(JSON_NODE, LIST_ONE_QUERY)
        )
        Assertions.assertEquals(
            listOf("$['two']['nested']"),
            JsonPaths.getPaths(JSON_NODE, NESTED_FIELD_QUERY)
        )
        Assertions.assertEquals(
            listOf("$['two']"),
            JsonPaths.getPaths(JSON_NODE, JSON_OBJECT_QUERY)
        )
        Assertions.assertEquals(emptyList<Any>(), JsonPaths.getPaths(JSON_NODE, EMPTY_RETURN_QUERY))
    }

    @Test
    fun testIsPathPresent() {
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            JsonPaths.isPathPresent(JSON_NODE, LIST_ALL_QUERY)
        }
        Assertions.assertTrue(JsonPaths.isPathPresent(JSON_NODE, LIST_ONE_QUERY))
        Assertions.assertTrue(JsonPaths.isPathPresent(JSON_NODE, NESTED_FIELD_QUERY))
        Assertions.assertTrue(JsonPaths.isPathPresent(JSON_NODE, JSON_OBJECT_QUERY))
        Assertions.assertFalse(JsonPaths.isPathPresent(JSON_NODE, EMPTY_RETURN_QUERY))
    }

    @Test
    fun testReplaceAtStringLoud() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[1] = REPLACEMENT_STRING

            val actual =
                JsonPaths.replaceAtStringLoud(JSON_NODE, LIST_ONE_QUERY, REPLACEMENT_STRING)
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtStringLoudEmptyPathThrows() {
        assertOriginalObjectNotModified(JSON_NODE) {
            Assertions.assertThrows(
                PathNotFoundException::class.java,
                Executable {
                    JsonPaths.replaceAtStringLoud(JSON_NODE, EMPTY_RETURN_QUERY, REPLACEMENT_STRING)
                }
            )
        }
    }

    @Test
    fun testReplaceAtString() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[1] = REPLACEMENT_STRING

            val actual = JsonPaths.replaceAtString(JSON_NODE, LIST_ONE_QUERY, REPLACEMENT_STRING)
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtStringEmptyReturnNoOp() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            val actual =
                JsonPaths.replaceAtString(JSON_NODE, EMPTY_RETURN_QUERY, REPLACEMENT_STRING)
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtJsonNodeLoud() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[1] = REPLACEMENT_JSON

            val actual =
                JsonPaths.replaceAtJsonNodeLoud(JSON_NODE, LIST_ONE_QUERY, REPLACEMENT_JSON)
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtJsonNodeLoudEmptyPathThrows() {
        assertOriginalObjectNotModified(JSON_NODE) {
            Assertions.assertThrows(
                PathNotFoundException::class.java,
                Executable {
                    JsonPaths.replaceAtJsonNodeLoud(JSON_NODE, EMPTY_RETURN_QUERY, REPLACEMENT_JSON)
                }
            )
        }
    }

    @Test
    fun testReplaceAtJsonNodeLoudMultipleReplace() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[0] = REPLACEMENT_JSON
            (expected[ONE] as ArrayNode)[1] = REPLACEMENT_JSON
            (expected[ONE] as ArrayNode)[2] = REPLACEMENT_JSON

            val actual =
                JsonPaths.replaceAtJsonNodeLoud(JSON_NODE, LIST_ALL_QUERY, REPLACEMENT_JSON)
            Assertions.assertEquals(expected, actual)
        }
    }

    // todo (cgardens) - this behavior is a little unintuitive, but based on the docs, there's not
    // an
    // obvious workaround. in this case, i would expect this to silently do nothing instead of
    // throwing.
    // for now just documenting it with a test. to avoid this, use the non-loud version of this
    // method.
    @Test
    fun testReplaceAtJsonNodeLoudMultipleReplaceSplatInEmptyArrayThrows() {
        val expected = Jsons.clone(JSON_NODE)
        (expected[ONE] as ArrayNode).removeAll()

        assertOriginalObjectNotModified(expected) {
            Assertions.assertThrows(
                PathNotFoundException::class.java,
                Executable {
                    JsonPaths.replaceAtJsonNodeLoud(expected, "$.one[*]", REPLACEMENT_JSON)
                }
            )
        }
    }

    @Test
    fun testReplaceAtJsonNode() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[1] = REPLACEMENT_JSON

            val actual = JsonPaths.replaceAtJsonNode(JSON_NODE, LIST_ONE_QUERY, REPLACEMENT_JSON)
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtJsonNodeEmptyReturnNoOp() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            val actual =
                JsonPaths.replaceAtJsonNode(JSON_NODE, EMPTY_RETURN_QUERY, REPLACEMENT_JSON)
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAt() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[1] = "1-$['one'][1]"

            val actual =
                JsonPaths.replaceAt(JSON_NODE, LIST_ONE_QUERY) { node: JsonNode, path: String ->
                    Jsons.jsonNode("$node-$path")
                }
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtMultiple() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            (expected[ONE] as ArrayNode)[0] = "0-$['one'][0]"
            (expected[ONE] as ArrayNode)[1] = "1-$['one'][1]"
            (expected[ONE] as ArrayNode)[2] = "2-$['one'][2]"

            val actual =
                JsonPaths.replaceAt(JSON_NODE, LIST_ALL_QUERY) { node: JsonNode, path: String ->
                    Jsons.jsonNode("$node-$path")
                }
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testReplaceAtEmptyReturnNoOp() {
        assertOriginalObjectNotModified(JSON_NODE) {
            val expected = Jsons.clone(JSON_NODE)
            val actual =
                JsonPaths.replaceAt(JSON_NODE, EMPTY_RETURN_QUERY) { node: JsonNode, path: String ->
                    Jsons.jsonNode("$node-$path")
                }
            Assertions.assertEquals(expected, actual)
        }
    }

    companion object {
        private val JSON =
            """
                                     {
                                       "one": [0,1,2],
                                       "two": { "nested": 10}
                                     }
                                     """.trimIndent()
        private val JSON_NODE: JsonNode = Jsons.deserialize(JSON)
        private const val LIST_ALL_QUERY = "$.one[*]"
        private const val LIST_ONE_QUERY = "$.one[1]"
        private const val NESTED_FIELD_QUERY = "$.two.nested"
        private const val JSON_OBJECT_QUERY = "$.two"
        private const val EMPTY_RETURN_QUERY = "$.three"
        private const val REPLACEMENT_STRING = "replaced"
        private val REPLACEMENT_JSON: JsonNode =
            Jsons.deserialize("{ \"replacement\": \"replaced\" }")
        private const val ONE = "one"

        /**
         * For all replacement functions, they should NOT mutate in place. Helper assertion to
         * verify that invariant.
         *
         * @param json
         * - json object used for testing
         * @param runnable
         * - the rest of the test code that does the replacement
         */
        private fun assertOriginalObjectNotModified(json: JsonNode, runnable: Runnable) {
            val originalJsonNode = Jsons.clone(json)
            runnable.run()
            // verify the original object was not mutated.
            Assertions.assertEquals(originalJsonNode, json)
        }
    }
}
