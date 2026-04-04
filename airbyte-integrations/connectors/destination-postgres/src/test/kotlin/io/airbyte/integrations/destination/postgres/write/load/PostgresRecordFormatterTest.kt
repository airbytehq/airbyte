/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

internal class PostgresRecordFormatterTest {

    @Test
    fun `stripNullBytes removes null bytes from string`() {
        val input = "abc\u0000def\u0000ghi"
        assertEquals("abcdefghi", input.stripNullBytes())
    }

    @Test
    fun `stripNullBytes returns same string when no null bytes present`() {
        val input = "normal string"
        assertEquals("normal string", input.stripNullBytes())
    }

    @Test
    fun `stripNullBytes handles empty string`() {
        assertEquals("", "".stripNullBytes())
    }

    @Test
    fun `stripNullBytes handles string of only null bytes`() {
        assertEquals("", "\u0000\u0000\u0000".stripNullBytes())
    }

    @Test
    fun `raw formatter strips null bytes from JSON data`() {
        val columns =
            listOf(
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_AB_GENERATION_ID,
                Meta.COLUMN_NAME_AB_LOADED_AT,
                Meta.COLUMN_NAME_DATA,
            )
        val formatter = PostgresRawRecordFormatter(columns)

        val record =
            mapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to StringValue("id-123"),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to StringValue("2026-01-01T00:00:00Z"),
                Meta.COLUMN_NAME_AB_META to StringValue("{}"),
                Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1.toBigInteger()),
                "description" to StringValue("text with\u0000null byte"),
            )

        val result = formatter.format(record)

        // The _airbyte_data column (index 5) should not contain null bytes
        val jsonData = result[5] as String
        assertFalse(jsonData.contains('\u0000'), "JSON data should not contain null bytes")
    }

    @Test
    fun `schema formatter strips null bytes from string values`() {
        val columns = listOf("name", "description")
        val formatter = PostgresSchemaRecordFormatter(columns)

        val record =
            mapOf(
                "name" to StringValue("normal name"),
                "description" to StringValue("contains\u0000null\u0000bytes"),
            )

        val result = formatter.format(record)

        assertEquals("normal name", result[0])
        assertEquals("containsnullbytes", result[1])
    }

    @Test
    fun `schema formatter handles non-string values without modification`() {
        val columns = listOf("id", "name")
        val formatter = PostgresSchemaRecordFormatter(columns)

        val record =
            mapOf(
                "id" to IntegerValue(42.toBigInteger()),
                "name" to StringValue("test"),
            )

        val result = formatter.format(record)

        assertEquals(42.toBigInteger(), result[0])
        assertEquals("test", result[1])
    }
}
