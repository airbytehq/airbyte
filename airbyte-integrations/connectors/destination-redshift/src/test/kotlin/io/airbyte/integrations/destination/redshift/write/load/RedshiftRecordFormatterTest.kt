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
import io.airbyte.integrations.destination.redshift.sql.RedshiftSqlGenerator
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class RedshiftRecordFormatterTest {

    @Test
    fun `format produces values in column order`() {
        val formatter =
            RedshiftSchemaRecordFormatter(
                linkedMapOf(
                    "_airbyte_raw_id" to "varchar(36)",
                    "_airbyte_extracted_at" to "timestamptz",
                    "name" to "varchar(65535)",
                    "age" to "bigint",
                )
            )

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
    fun `format returns sentinel for missing varchar columns and empty for others`() {
        val formatter =
            RedshiftSchemaRecordFormatter(
                linkedMapOf(
                    "id" to "bigint",
                    "name" to "varchar(65535)",
                    "missing_int" to "bigint",
                )
            )

        val record =
            mapOf(
                "id" to IntegerValue(BigInteger.ONE),
                // name and missing_int are both absent
                )

        val result = formatter.format(record)

        assertEquals(3, result.size)
        assertEquals("1", result[0])
        assertEquals(RedshiftSqlGenerator.NULL_SENTINEL, result[1]) // varchar sentinel
        assertEquals("", result[2]) // non-sentinel → empty (auto-null by Redshift)
    }

    @Test
    fun `format uses sentinel for NullValue in varchar columns`() {
        val formatter =
            RedshiftSchemaRecordFormatter(
                linkedMapOf("str_col" to "varchar(65535)", "int_col" to "bigint")
            )

        val record =
            mapOf(
                "str_col" to NullValue,
                "int_col" to NullValue,
            )

        val result = formatter.format(record)

        assertEquals(2, result.size)
        assertEquals(RedshiftSqlGenerator.NULL_SENTINEL, result[0]) // sentinel for varchar null
        assertEquals("", result[1]) // empty for non-sentinel null
    }

    @Test
    fun `format preserves empty strings separately from nulls for varchar columns`() {
        val formatter =
            RedshiftSchemaRecordFormatter(
                linkedMapOf("str_col" to "varchar(65535)", "nullable_str" to "varchar(65535)")
            )

        val record =
            mapOf(
                "str_col" to StringValue(""), // empty string
                "nullable_str" to NullValue, // genuine null
            )

        val result = formatter.format(record)

        assertEquals(2, result.size)
        assertEquals("", result[0]) // empty string preserved
        assertEquals(RedshiftSqlGenerator.NULL_SENTINEL, result[1]) // null → sentinel
    }

    @Test
    fun `format serializes objects and arrays as JSON strings`() {
        val formatter =
            RedshiftSchemaRecordFormatter(linkedMapOf("json_obj" to "super", "json_arr" to "super"))

        val record =
            mapOf(
                "json_obj" to ObjectValue(linkedMapOf("key" to StringValue("value"))),
                "json_arr" to
                    ArrayValue(listOf(IntegerValue(BigInteger.ONE), IntegerValue(BigInteger.TWO))),
            )

        val result = formatter.format(record)

        assertEquals(2, result.size)
        assertEquals("""{"key":"value"}""", result[0])
        assertEquals("[1,2]", result[1])
    }

    @Test
    fun `format handles boolean and number types`() {
        val formatter =
            RedshiftSchemaRecordFormatter(
                linkedMapOf("is_active" to "boolean", "price" to "decimal(38,9)")
            )

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
    fun `format with empty record uses sentinel for varchar columns only`() {
        val formatter =
            RedshiftSchemaRecordFormatter(
                linkedMapOf(
                    "varchar_col" to "varchar(65535)",
                    "int_col" to "bigint",
                    "super_col" to "super",
                )
            )

        val result = formatter.format(emptyMap())

        assertEquals(3, result.size)
        assertEquals(RedshiftSqlGenerator.NULL_SENTINEL, result[0]) // varchar → sentinel
        assertEquals("", result[1]) // int → empty (Redshift auto-nulls)
        assertEquals("", result[2]) // super → empty (Redshift auto-nulls)
    }

    @Test
    fun `format ignores extra fields not in column list`() {
        val formatter = RedshiftSchemaRecordFormatter(linkedMapOf("id" to "bigint"))

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
