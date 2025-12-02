/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.Lists
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class IncrementalUtilsTest {
    @Test
    fun testGetCursorField() {
        val stream = Jsons.clone(STREAM)
        stream.cursorField = Lists.newArrayList(UUID_FIELD_NAME)
        Assertions.assertEquals(UUID_FIELD_NAME, IncrementalUtils.getCursorField(stream))
    }

    @Test
    fun testGetCursorFieldNoCursorFieldSet() {
        Assertions.assertThrows(IllegalStateException::class.java) {
            Assertions.assertEquals(UUID_FIELD_NAME, IncrementalUtils.getCursorField(STREAM))
        }
    }

    @Test
    fun testGetCursorFieldCompositCursor() {
        val stream = Jsons.clone(STREAM)
        stream.cursorField = Lists.newArrayList(UUID_FIELD_NAME, "something_else")
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.getCursorField(stream)
        }
    }

    @Test
    fun testGetCursorType() {
        Assertions.assertEquals(
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING,
            IncrementalUtils.getCursorType(STREAM, UUID_FIELD_NAME)
        )
    }

    @Test
    fun testGetCursorType_V1() {
        Assertions.assertEquals(
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING_V1,
            IncrementalUtils.getCursorType(STREAM_V1, UUID_FIELD_NAME)
        )
    }

    @Test
    fun testGetCursorTypeNoProperties() {
        val stream = Jsons.clone(STREAM)
        stream.stream.jsonSchema = Jsons.jsonNode(emptyMap<Any, Any>())
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.getCursorType(stream, UUID_FIELD_NAME)
        }
    }

    @Test
    fun testGetCursorTypeNoCursor() {
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.getCursorType(STREAM, "does not exist")
        }
    }

    @Test
    fun testGetCursorTypeCursorHasNoType() {
        val stream = Jsons.clone(STREAM)
        (stream.stream.jsonSchema["properties"][UUID_FIELD_NAME] as ObjectNode).remove("type")
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.getCursorType(stream, UUID_FIELD_NAME)
        }
    }

    @Test
    fun testCompareCursors() {
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                ABC,
                "def",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING
            ) < 0
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                ABC,
                "def",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING_V1
            ) < 0
        )
        Assertions.assertEquals(
            0,
            IncrementalUtils.compareCursors(
                ABC,
                ABC,
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING
            )
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                "1",
                "2",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NUMBER
            ) < 0
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                "1",
                "2",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.INTEGER_V1
            ) < 0
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                "5000000000",
                "5000000001",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NUMBER
            ) < 0
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                "false",
                "true",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.BOOLEAN
            ) < 0
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                null,
                "def",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING
            ) < 1
        )
        Assertions.assertTrue(
            IncrementalUtils.compareCursors(
                ABC,
                null,
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING
            ) > 0
        )
        Assertions.assertEquals(
            0,
            IncrementalUtils.compareCursors(
                null,
                null,
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING
            )
        )
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.compareCursors(
                "a",
                "a",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.ARRAY
            )
        }
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.compareCursors(
                "a",
                "a",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.OBJECT
            )
        }
        Assertions.assertThrows(IllegalStateException::class.java) {
            IncrementalUtils.compareCursors(
                "a",
                "a",
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NULL
            )
        }
    }

    companion object {
        private const val STREAM_NAME = "shoes"
        private const val UUID_FIELD_NAME = "ascending_inventory_uuid"
        private val STREAM: ConfiguredAirbyteStream =
            CatalogHelpers.createConfiguredAirbyteStream(
                STREAM_NAME,
                null,
                Field.of("ascending_inventory_uuid", JsonSchemaType.STRING)
            )

        private val STREAM_V1: ConfiguredAirbyteStream =
            CatalogHelpers.createConfiguredAirbyteStream(
                STREAM_NAME,
                null,
                Field.of("ascending_inventory_uuid", JsonSchemaType.STRING_V1)
            )
        private const val ABC = "abc"
    }
}
