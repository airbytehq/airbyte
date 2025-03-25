/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class AirbyteTypeToMsqlTypeTest {

    private val converter = AirbyteTypeToMssqlType()

    @Test
    fun testConvertObjectType() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true),
                ),
            )
        val result = converter.convert(objectType)
        assertEquals(MssqlType.TEXT, result)
    }

    @Test
    fun testConvertArrayType() {
        val arrayType = ArrayType(FieldType(IntegerType, false))
        val result = converter.convert(arrayType)
        assertEquals(MssqlType.TEXT, result)
    }

    @Test
    fun testConvertArrayTypeWithoutSchema() {
        val arrayType = ArrayTypeWithoutSchema
        val result = converter.convert(arrayType)
        assertEquals(MssqlType.TEXT, result)
    }

    @Test
    fun testConvertBooleanType() {
        val booleanType = BooleanType
        val result = converter.convert(booleanType)
        assertEquals(MssqlType.BIT, result)
    }

    @Test
    fun testConvertDateType() {
        val dateType = DateType
        val result = converter.convert(dateType)
        assertEquals(MssqlType.DATE, result)
    }

    @Test
    fun testConvertIntegerType() {
        val integerType = IntegerType
        val result = converter.convert(integerType)
        assertEquals(MssqlType.BIGINT, result)
    }

    @Test
    fun testConvertNumberType() {
        val numberType = NumberType
        val result = converter.convert(numberType)
        assertEquals(MssqlType.DECIMAL, result)
    }

    @Test
    fun testConvertObjectTypeWithEmptySchema() {
        val objectType = ObjectTypeWithEmptySchema
        val result = converter.convert(objectType)
        assertEquals(MssqlType.TEXT, result)
    }

    @Test
    fun testConvertObjectTypeWithoutSchema() {
        val objectType = ObjectTypeWithoutSchema
        val result = converter.convert(objectType)
        assertEquals(MssqlType.TEXT, result)
    }

    @Test
    fun testConvertStringType() {
        val stringType = StringType
        val result = converter.convert(stringType)
        assertEquals(MssqlType.VARCHAR, result)
    }

    @Test
    fun testConvertIndexedStringType() {
        val stringType = StringType
        val result = converter.convert(stringType, isIndexed = true)
        assertEquals(MssqlType.VARCHAR_INDEX, result)
    }

    @Test
    fun testConvertTimeTypeWithTimezone() {
        val timeType = TimeTypeWithTimezone
        val result = converter.convert(timeType)
        assertEquals(MssqlType.DATETIMEOFFSET, result)
    }

    @Test
    fun testConvertTimeTypeWithoutTimezone() {
        val timeType = TimeTypeWithoutTimezone
        val result = converter.convert(timeType)
        assertEquals(MssqlType.TIME, result)
    }

    @Test
    fun testConvertTimestampTypeWithTimezone() {
        val timestampType = TimestampTypeWithTimezone
        val result = converter.convert(timestampType)
        assertEquals(MssqlType.DATETIMEOFFSET, result)
    }

    @Test
    fun testConvertTimestampTypeWithoutTimezone() {
        val timestampType = TimestampTypeWithoutTimezone
        val result = converter.convert(timestampType)
        assertEquals(MssqlType.DATETIME, result)
    }

    @Test
    fun testConvertUnionType() {
        val unionType = UnionType(setOf(StringType, NumberType))
        val result = converter.convert(unionType)
        assertEquals(MssqlType.TEXT, result)
    }

    @Test
    fun testConvertUnknownType() {
        val unknownType = UnknownType(mockk<JsonNode>())
        val result = converter.convert(unknownType)
        assertEquals(MssqlType.TEXT, result)
    }
}
