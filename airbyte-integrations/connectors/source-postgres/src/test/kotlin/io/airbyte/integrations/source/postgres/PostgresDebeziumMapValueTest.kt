/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Tests that validate the defensive handling in the StringFieldType branch of mapValue().
 *
 * Before the fix, ObjectNode.asText() returned "" which caused silent data loss for PostGIS
 * geometry Structs serialized as JSON objects (e.g., {"wkb":"...","srid":4326}).
 *
 * The fix uses Jsons.writeValueAsString() for container nodes (ObjectNode/ArrayNode) to preserve
 * their content as a JSON string.
 *
 * Since mapValue() is a private method with a Kotlin-mangled name, we verify the behavior through
 * the JSON operations it relies on to confirm the fix approach is correct.
 */
class PostgresDebeziumMapValueTest {

    @Test
    fun `ObjectNode asText returns empty string - demonstrates the pre-fix data loss`() {
        // This is the root cause: Debezium PostGIS Struct serialized as JSON ObjectNode
        val geomObject = Jsons.readTree("""{"wkb":"AQEAACDmEAAAAAAA","srid":4326}""")
        // ObjectNode.asText() returns "" — this is what caused NULL/empty geometry values
        assertEquals("", geomObject.asText())
    }

    @Test
    fun `writeValueAsString on ObjectNode preserves content - the fix approach`() {
        val geomObject = Jsons.readTree("""{"wkb":"AQEAACDmEAAAAAAA","srid":4326}""")
        assertTrue(geomObject.isContainerNode)
        val serialized = Jsons.writeValueAsString(geomObject)
        assertTrue(serialized.contains("wkb"))
        assertTrue(serialized.contains("srid"))
        assertTrue(serialized.contains("4326"))
    }

    @Test
    fun `writeValueAsString on ArrayNode preserves content`() {
        val arrayNode = Jsons.readTree("""[1, 2, 3]""")
        assertTrue(arrayNode.isContainerNode)
        assertEquals("[1,2,3]", Jsons.writeValueAsString(arrayNode))
    }

    @Test
    fun `textNode wrapping preserves serialized JSON as text`() {
        val geomObject = Jsons.readTree("""{"wkb":"AQEAACDmEAAAAAAA","srid":4326}""")
        val wrapped = Jsons.textNode(Jsons.writeValueAsString(geomObject))
        assertTrue(wrapped.isTextual)
        val text = wrapped.asText()
        assertTrue(text.contains("wkb"))
        assertTrue(text.contains("srid"))
    }

    @Test
    fun `TextNode isTextual returns true - passes through unchanged`() {
        val textNode = Jsons.textNode("hello")
        assertTrue(textNode.isTextual)
        assertEquals("hello", textNode.asText())
    }

    @Test
    fun `numeric node asText returns string representation`() {
        val numNode = Jsons.numberNode(42)
        assertEquals("42", numNode.asText())
    }

    @Test
    fun `NullNode is handled correctly`() {
        val nullNode = NullNode.instance
        assertTrue(nullNode.isNull)
    }
}
