/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg_parquet

import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.data.iceberg_parquet.AirbyteValueToIcebergRecord
import io.airbyte.cdk.load.data.iceberg_parquet.toIcebergRecord
import io.airbyte.protocol.models.Jsons
import java.math.BigDecimal
import org.apache.iceberg.Schema
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.NestedField
import org.junit.jupiter.api.Assertions.*
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
        assertThrows<IllegalArgumentException> {
            converter.convert(DateValue("2024-11-18"), Types.DateType.get())
        }
    }

    @Test
    fun `convert handles IntegerValue`() {
        val result = converter.convert(IntegerValue(123L), Types.LongType.get())
        assertEquals(123L, result)
    }

    @Test
    fun `convert handles IntValue`() {
        val result = converter.convert(IntValue(42), Types.IntegerType.get())
        assertEquals(42, result)
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
    fun `convert throws exception for TimeValue`() {
        assertThrows<IllegalArgumentException> {
            converter.convert(TimeValue("12:34:56"), Types.TimeType.get())
        }
    }

    @Test
    fun `convert throws exception for TimestampValue`() {
        assertThrows<IllegalArgumentException> {
            converter.convert(
                TimestampValue("2024-11-18T12:34:56Z"),
                Types.TimestampType.withZone()
            )
        }
    }

    @Test
    fun `convert throws exception for UnknownValue`() {
        assertThrows<IllegalArgumentException> {
            converter.convert(UnknownValue(Jsons.emptyObject()), Types.StringType.get())
        }
    }

    @Test
    fun `toIcebergRecord correctly converts ObjectValue to GenericRecord`() {
        val schema =
            Schema(
                NestedField.required(1, "id", Types.LongType.get()),
                NestedField.optional(2, "name", Types.StringType.get())
            )
        val objectValue =
            ObjectValue(linkedMapOf("id" to IntegerValue(123L), "name" to StringValue("John Doe")))

        val result = objectValue.toIcebergRecord(schema)
        assertEquals(123L, result.getField("id"))
        assertEquals("John Doe", result.getField("name"))
    }

    @Test
    fun `toIcebergRecord ignores fields not in schema`() {
        val schema = Schema(NestedField.required(1, "id", Types.LongType.get()))
        val objectValue =
            ObjectValue(
                linkedMapOf("id" to IntegerValue(123L), "name" to StringValue("Should be ignored"))
            )

        val result = objectValue.toIcebergRecord(schema)
        assertEquals(123L, result.getField("id"))
        assertNull(result.getField("name")) // Not in schema
    }
}
