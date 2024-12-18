/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.sql

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
import java.sql.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class AirbyteTypeToSqlTableTest {

    private lateinit var converter: AirbyteTypeToSqlType

    @BeforeEach
    fun setUp() {
        converter = AirbyteTypeToSqlType()
    }

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
        assertEquals(Types.BLOB, result)
    }

    @Test
    fun testConvertArrayType() {
        val arrayType = ArrayType(FieldType(IntegerType, false))
        assertThrows<IllegalArgumentException> { converter.convert(arrayType) }
    }

    @Test
    fun testConvertArrayTypeWithoutSchema() {
        val arrayType = ArrayTypeWithoutSchema
        assertThrows<IllegalArgumentException> { converter.convert(arrayType) }
    }

    @Test
    fun testConvertBooleanType() {
        val booleanType = BooleanType
        val result = converter.convert(booleanType)
        assertEquals(Types.BOOLEAN, result)
    }

    @Test
    fun testConvertDateType() {
        val dateType = DateType
        val result = converter.convert(dateType)
        assertEquals(Types.DATE, result)
    }

    @Test
    fun testConvertIntegerType() {
        val integerType = IntegerType
        val result = converter.convert(integerType)
        assertEquals(Types.BIGINT, result)
    }

    @Test
    fun testConvertNumberType() {
        val numberType = NumberType
        val result = converter.convert(numberType)
        assertEquals(Types.DECIMAL, result)
    }

    @Test
    fun testConvertObjectTypeWithEmptySchema() {
        val objectType = ObjectTypeWithEmptySchema
        val result = converter.convert(objectType)
        assertEquals(Types.BLOB, result)
    }

    @Test
    fun testConvertObjectTypeWithoutSchema() {
        val objectType = ObjectTypeWithoutSchema
        val result = converter.convert(objectType)
        assertEquals(Types.BLOB, result)
    }

    @Test
    fun testConvertStringType() {
        val stringType = StringType
        val result = converter.convert(stringType)
        assertEquals(Types.VARCHAR, result)
    }

    @Test
    fun testConvertTimeTypeWithTimezone() {
        val timeType = TimeTypeWithTimezone
        val result = converter.convert(timeType)
        assertEquals(Types.TIME_WITH_TIMEZONE, result)
    }

    @Test
    fun testConvertTimeTypeWithoutTimezone() {
        val timeType = TimeTypeWithoutTimezone
        val result = converter.convert(timeType)
        assertEquals(Types.TIME, result)
    }

    @Test
    fun testConvertTimestampTypeWithTimezone() {
        val timestampType = TimestampTypeWithTimezone
        val result = converter.convert(timestampType)
        assertEquals(Types.TIMESTAMP_WITH_TIMEZONE, result)
    }

    @Test
    fun testConvertTimestampTypeWithoutTimezone() {
        val timestampType = TimestampTypeWithoutTimezone
        val result = converter.convert(timestampType)
        assertEquals(Types.TIMESTAMP, result)
    }

    @Test
    fun testConvertUnionType() {
        val unionType = UnionType(setOf(StringType, NumberType))
        assertThrows<IllegalArgumentException> { converter.convert(unionType) }
    }

    @Test
    fun testConvertUnknownType() {
        val unknownType = UnknownType(mockk<JsonNode>())
        val result = converter.convert(unknownType)
        assertEquals(Types.LONGVARCHAR, result)
    }

    @Test
    fun testToSqlTable() {
        val primaryKey = "id"
        val nullableColumn = "email"
        val objectType =
            ObjectType(
                linkedMapOf(
                    primaryKey to FieldType(IntegerType, false),
                    "age" to FieldType(IntegerType, false),
                    nullableColumn to FieldType(StringType, true),
                ),
            )
        val primaryKeys = listOf(listOf(primaryKey))
        val table = objectType.toSqlTable(primaryKeys = primaryKeys)

        assertEquals(objectType.properties.size, table.columns.size)
        objectType.properties.forEach { (name, type) ->
            val column = table.columns.find { it.name == name }
            assertNotNull(column)
            assertEquals(converter.convert(type.type), column?.type)
            assertEquals(primaryKey == name, column?.isPrimaryKey)
            assertEquals(nullableColumn == name, column?.isNullable)
        }
    }
}
