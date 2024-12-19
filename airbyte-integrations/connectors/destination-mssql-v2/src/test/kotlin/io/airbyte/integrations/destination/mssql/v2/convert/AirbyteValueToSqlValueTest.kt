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
import io.airbyte.cdk.load.data.TimeStringUtility.toLocalDate
import io.airbyte.cdk.load.data.TimeStringUtility.toLocalDateTime
import io.airbyte.cdk.load.data.TimeStringUtility.toOffset
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.integrations.destination.mssql.v2.model.SqlColumn
import io.airbyte.integrations.destination.mssql.v2.model.SqlTable
import java.math.BigDecimal
import java.math.BigInteger
import java.sql.Date
import java.sql.Time
import java.sql.Timestamp
import java.sql.Types
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
            toLocalDate(dateValue.value).atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli(),
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
        val timeValue = TimeValue("12:34:56")
        val result = converter.convert(timeValue)
        assertEquals(Time::class.java, result?.javaClass)
        assertEquals(Time.valueOf(toOffset(timeValue.value)).time, (result as Time).time)
    }

    @Test
    fun testConvertTimestampValue() {
        val timestampValue = TimestampValue("2024-11-18T12:34:56Z")
        val result = converter.convert(timestampValue)
        assertEquals(Timestamp::class.java, result?.javaClass)
        assertEquals(
            Timestamp.valueOf(toLocalDateTime(timestampValue.value)).time,
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
    fun testToSqlValue() {
        val sqlTable =
            SqlTable(
                listOf(
                    SqlColumn(
                        name = "id",
                        type = Types.INTEGER,
                        isPrimaryKey = true,
                        isNullable = false
                    ),
                    SqlColumn(
                        name = "name",
                        type = Types.VARCHAR,
                        isPrimaryKey = false,
                        isNullable = true
                    ),
                    SqlColumn(
                        name = "meta",
                        type = Types.BLOB,
                        isPrimaryKey = false,
                        isNullable = false
                    ),
                    SqlColumn(
                        name = "items",
                        type = Types.BLOB,
                        isPrimaryKey = false,
                        isNullable = false
                    )
                )
            )
        val objectValue =
            ObjectValue(
                linkedMapOf(
                    "id" to IntegerValue(123L),
                    "name" to StringValue("John Doe"),
                    "meta" to
                        ObjectValue(
                            linkedMapOf(
                                "sync_id" to IntegerValue(123L),
                                "changes" to
                                    ObjectValue(
                                        linkedMapOf(
                                            "change" to StringValue("insert"),
                                            "reason" to StringValue("reason"),
                                        )
                                    )
                            )
                        ),
                    "items" to ArrayValue(listOf(StringValue("item1"), StringValue("item2")))
                )
            )

        val sqlValue = objectValue.toSqlValue(sqlTable)

        assertEquals(sqlTable.columns.size, sqlValue.values.size)
        assertEquals(
            BigInteger::class.java,
            sqlValue.values.find { it.name == "id" }?.value?.javaClass
        )
        assertEquals(123.toBigInteger(), sqlValue.values.find { it.name == "id" }?.value)
        assertEquals(
            String::class.java,
            sqlValue.values.find { it.name == "name" }?.value?.javaClass
        )
        assertEquals("John Doe", sqlValue.values.find { it.name == "name" }?.value)
        assertEquals(
            ByteArray::class.java,
            sqlValue.values.find { it.name == "meta" }?.value?.javaClass
        )
        assertArrayEquals(
            mapOf(
                    "sync_id" to 123.toBigInteger(),
                    "changes" to
                        mapOf(
                            "change" to "insert",
                            "reason" to "reason",
                        )
                )
                .serializeToJsonBytes(),
            sqlValue.values.find { it.name == "meta" }?.value as ByteArray
        )
        assertEquals(
            ByteArray::class.java,
            sqlValue.values.find { it.name == "items" }?.value?.javaClass
        )
        assertArrayEquals(
            listOf("item1", "item2").serializeToJsonBytes(),
            sqlValue.values.find { it.name == "items" }?.value as ByteArray
        )
    }

    @Test
    fun testToSqlValueIgnoresFieldsNotInTable() {
        val sqlTable =
            SqlTable(
                listOf(
                    SqlColumn(
                        name = "id",
                        type = Types.INTEGER,
                        isPrimaryKey = true,
                        isNullable = false
                    ),
                )
            )
        val objectValue =
            ObjectValue(
                linkedMapOf(
                    "id" to IntegerValue(123L),
                    "name" to StringValue("Should be ignored"),
                )
            )

        val sqlValue = objectValue.toSqlValue(sqlTable)
        assertEquals(sqlTable.columns.size, sqlValue.values.size)
        assertEquals(
            BigInteger::class.java,
            sqlValue.values.find { it.name == "id" }?.value?.javaClass
        )
        assertEquals(123.toBigInteger(), sqlValue.values.find { it.name == "id" }?.value)
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
