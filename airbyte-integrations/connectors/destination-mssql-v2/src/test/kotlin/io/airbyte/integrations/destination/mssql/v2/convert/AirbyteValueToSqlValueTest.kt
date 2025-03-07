/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToJsonBytes
import java.math.BigDecimal
import java.math.BigInteger
import java.sql.Date
import java.sql.Time
import java.sql.Timestamp
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

internal class AirbyteValueToSqlValueTest {

    private val converter = AirbyteValueToSqlValue()

    @Test
    fun testConvertObjectValue() {
        val objectValue =
            ObjectValue(linkedMapOf("id" to IntegerValue(42L), "name" to StringValue("John Doe")))
        val result = converter.convert(objectValue)
        assertEquals(LinkedHashMap::class.java, result?.javaClass)
        assertEquals(mapOf("id" to 42.toBigInteger(), "name" to "John Doe"), result)
    }

    @Test
    fun testConvertArrayValue() {
        val arrayValue = ArrayValue(listOf(StringValue("John Doe"), IntegerValue(42L)))
        val result = converter.convert(arrayValue)
        assertEquals(ArrayList::class.java, result?.javaClass)
        assertEquals(listOf("John Doe", 42.toBigInteger()), result)
    }

    @Test
    fun testConvertDateValue() {
        val dateValue = DateValue("2024-11-18")
        val result = converter.convert(dateValue)
        assertEquals(Date::class.java, result?.javaClass)
        assertEquals(
            dateValue.value.atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli(),
            (result as Date).time
        )
    }

    @Test
    fun testConvertIntegerValue() {
        val intValue = IntegerValue(42)
        val result = converter.convert(intValue)
        assertEquals(BigInteger::class.java, result?.javaClass)
        assertEquals(42.toBigInteger(), result)
    }

    @Test
    fun testConvertNullValue() {
        val nullValue = NullValue
        val result = converter.convert(nullValue)
        assertNull(result)
    }

    @Test
    fun testConvertNumberValue() {
        val numberValue = NumberValue(42.5.toBigDecimal())
        val result = converter.convert(numberValue)
        assertEquals(BigDecimal::class.java, result?.javaClass)
        assertEquals(42.5.toBigDecimal(), result)
    }

    @Test
    fun testConvertStringValue() {
        val stringValue = StringValue("test")
        val result = converter.convert(stringValue)
        assertEquals(String::class.java, result?.javaClass)
        assertEquals("test", result)
    }

    @Test
    fun testConvertTimeValue() {
        val timeValue = TimeWithoutTimezoneValue("12:34:56")
        val result = converter.convert(timeValue)
        assertEquals(Time::class.java, result?.javaClass)
        assertEquals(Time.valueOf(timeValue.value).time, (result as Time).time)
    }

    @Test
    fun testConvertTimestampValue() {
        val timestampValue = TimestampWithTimezoneValue("2024-11-18T12:34:56Z")
        val result = converter.convert(timestampValue)
        assertEquals(Timestamp::class.java, result?.javaClass)
        assertEquals(
            Timestamp.valueOf(timestampValue.value.toLocalDateTime()).time,
            (result as Timestamp).time
        )
    }

    @Test
    fun testConvertUnknownValue() {
        val jsonNode = Jsons.createObjectNode().put("id", "unknownValue")
        val unknownValue = UnknownValue(jsonNode)
        val result = converter.convert(unknownValue)
        assertEquals(ByteArray::class.java, result?.javaClass)
        assertArrayEquals(Jsons.writeValueAsBytes(unknownValue.value), result as ByteArray)
    }

    @Test
    fun testObjectMapToJsonBytes() {
        val objectValue =
            ObjectValue(linkedMapOf("id" to IntegerValue(42L), "name" to StringValue("John Doe")))
        val objectValueMap = converter.convert(objectValue)
        val jsonBytes = objectValueMap?.serializeToJsonBytes()
        assertNotNull(jsonBytes)
        assertArrayEquals(Jsons.writeValueAsBytes(objectValueMap), jsonBytes)
    }
}
