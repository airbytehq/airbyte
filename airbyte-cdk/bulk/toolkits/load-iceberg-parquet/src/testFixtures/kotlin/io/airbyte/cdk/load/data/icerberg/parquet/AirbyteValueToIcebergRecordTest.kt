/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.iceberg.parquet.AirbyteValueToIcebergRecord
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import org.apache.iceberg.Schema
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.NestedField
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class AirbyteValueToIcebergRecordTest {

    private val converter = AirbyteValueToIcebergRecord()

    @Test
    fun `convert handles ObjectValue`() {
        val schema =
            Schema(
                NestedField.required(1, "id", Types.LongType.get()),
                NestedField.optional(2, "name", Types.StringType.get())
            )
        val objectValue =
            ObjectValue(linkedMapOf("id" to IntegerValue(42L), "name" to StringValue("John Doe")))

        val result = converter.convert(objectValue, schema.asStruct()) as GenericRecord
        assertEquals(42L, result.getField("id"))
        assertEquals("John Doe", result.getField("name"))
    }

    @Test
    fun `convert throws exception for ObjectValue mapped to non-StructType`() {
        val schemaType = Types.StringType.get()
        val objectValue = ObjectValue(linkedMapOf("id" to IntegerValue(42L)))

        assertThrows<IllegalArgumentException> { converter.convert(objectValue, schemaType) }
    }

    @Test
    fun `convert handles ArrayValue`() {
        val arrayType = Types.ListType.ofRequired(1, Types.LongType.get())
        val arrayValue = ArrayValue(listOf(IntegerValue(1L), IntegerValue(2L), IntegerValue(3L)))

        val result = converter.convert(arrayValue, arrayType) as List<*>
        assertEquals(listOf(1L, 2L, 3L), result)
    }

    @Test
    fun `convert throws exception for ArrayValue mapped to non-ListType`() {
        val schemaType = Types.StringType.get()
        val arrayValue = ArrayValue(listOf(IntegerValue(1L), IntegerValue(2L)))

        assertThrows<IllegalArgumentException> { converter.convert(arrayValue, schemaType) }
    }

    @Test
    fun `convert handles BooleanValue`() {
        val result = converter.convert(BooleanValue(true), Types.BooleanType.get())
        assertEquals(true, result)
    }

    @Test
    fun `convert throws exception for DateValue`() {
        val result =
            converter.convert(DateValue(LocalDate.parse("2024-11-18")), Types.DateType.get())
        assertEquals(LocalDate.parse("2024-11-18"), result)
    }

    @Test
    fun `convert handles IntegerValue`() {
        val result = converter.convert(IntegerValue(123L), Types.LongType.get())
        assertEquals(123L, result)
    }

    @Test
    fun `convert handles NullValue`() {
        val result = converter.convert(NullValue, Types.StringType.get())
        assertNull(result)
    }

    @Test
    fun `convert handles NumberValue`() {
        val result =
            converter.convert(NumberValue(BigDecimal.valueOf(123.45)), Types.DoubleType.get())
        assertEquals(123.45, result)
    }

    @Test
    fun `convert handles StringValue`() {
        val result = converter.convert(StringValue("test string"), Types.StringType.get())
        assertEquals("test string", result)
    }

    @Test
    fun `convert handles TimeNtzValue`() {
        val result =
            converter.convert(
                TimeWithoutTimezoneValue(LocalTime.parse("12:34:56")),
                Types.TimeType.get()
            )
        assertEquals(LocalTime.parse("12:34:56"), result)
    }

    @Test
    fun `convert handles TimeTzValue`() {
        val result =
            converter.convert(
                TimeWithTimezoneValue(OffsetTime.parse("12:34:56Z")),
                Types.TimeType.get()
            )
        // Note LocalTime here. Iceberg+Parquet doesn't have a dedicated timetz type.
        assertEquals(LocalTime.parse("12:34:56"), result)
    }

    @Test
    fun `convert handles TimestampNtzValue`() {
        val result =
            converter.convert(
                TimestampWithoutTimezoneValue(LocalDateTime.parse("2024-11-18T12:34:56")),
                Types.TimestampType.withoutZone()
            )
        assertEquals(LocalDateTime.parse("2024-11-18T12:34:56"), result)
    }

    @Test
    fun `convert handles TimestampTzValue`() {
        val result =
            converter.convert(
                TimestampWithTimezoneValue(OffsetDateTime.parse("2024-11-18T12:34:56Z")),
                Types.TimestampType.withZone()
            )
        assertEquals(OffsetDateTime.parse("2024-11-18T12:34:56Z"), result)
    }
}
