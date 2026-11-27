/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class RedshiftRecordFormatterTest {

    @Test
    fun `format produces values in column order`() {
        val columns = listOf("_airbyte_raw_id", "_airbyte_extracted_at", "name", "age")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val record =
            mapOf(
                "_airbyte_raw_id" to StringValue("abc-123"),
                "_airbyte_extracted_at" to StringValue("2026-01-01T00:00:00Z"),
                "name" to StringValue("Alice"),
                "age" to IntegerValue(BigInteger.valueOf(30)),
            )

        val result = formatter.format(record)

        assertEquals(4, result.size)
        assertEquals("abc-123", result[0])
        assertEquals("2026-01-01T00:00:00Z", result[1])
        assertEquals("Alice", result[2])
        assertEquals("30", result[3])
    }

    @Test
    fun `format returns empty string for missing columns`() {
        val columns = listOf("id", "name", "missing_col")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val record =
            mapOf(
                "id" to IntegerValue(BigInteger.ONE),
                "name" to StringValue("Bob"),
            )

        val result = formatter.format(record)

        assertEquals(3, result.size)
        assertEquals("1", result[0])
        assertEquals("Bob", result[1])
        assertEquals(null, result[2]) // missing non-varchar → null (Redshift auto-nulls)
    }

    @Test
    fun `format handles null values via toCsvValue`() {
        val columns = listOf("col_a", "col_b")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val record =
            mapOf(
                "col_a" to NullValue,
                "col_b" to StringValue("present"),
            )

        val result = formatter.format(record)

        assertEquals(2, result.size)
        assertEquals(null, result[0]) // NullValue in non-varchar → null (Redshift auto-nulls)
        assertEquals("present", result[1])
    }

    @Test
    fun `format serializes objects and arrays as JSON strings`() {
        val columns = listOf("json_obj", "json_arr")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val record =
            mapOf(
                "json_obj" to ObjectValue(linkedMapOf("key" to StringValue("value"))),
                "json_arr" to
                    ArrayValue(listOf(IntegerValue(BigInteger.ONE), IntegerValue(BigInteger.TWO))),
            )

        val result = formatter.format(record)

        assertEquals(2, result.size)
        // ObjectValue and ArrayValue are serialized to JSON strings by toCsvValue
        assertEquals("""{"key":"value"}""", result[0])
        assertEquals("[1,2]", result[1])
    }

    @Test
    fun `format handles boolean and number types`() {
        val columns = listOf("is_active", "price")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val record =
            mapOf(
                "is_active" to BooleanValue(true),
                "price" to NumberValue(BigDecimal("19.99")),
            )

        val result = formatter.format(record)

        assertEquals(2, result.size)
        assertEquals("true", result[0])
        assertEquals("19.99", result[1])
    }

    @Test
    fun `format with empty record returns null for non-varchar columns`() {
        val columns = listOf("a", "b", "c")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val result = formatter.format(emptyMap())

        assertEquals(listOf(null, null, null), result)
    }

    @Test
    fun `format ignores extra fields not in column list`() {
        val columns = listOf("id")
        val formatter = RedshiftSchemaRecordFormatter(columns, emptySet())

        val record =
            mapOf(
                "id" to IntegerValue(BigInteger.ONE),
                "extra_field" to StringValue("should be ignored"),
            )

        val result = formatter.format(record)

        assertEquals(1, result.size)
        assertEquals("1", result[0])
    }
}
