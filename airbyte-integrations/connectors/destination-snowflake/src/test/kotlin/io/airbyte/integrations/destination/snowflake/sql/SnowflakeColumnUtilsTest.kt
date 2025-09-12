/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

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
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.mockk.mockk
import kotlin.collections.LinkedHashMap
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeColumnUtilsTest {

    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setup() {
        snowflakeColumnUtils = SnowflakeColumnUtils()
    }

    @Test
    fun testGeneratingColumnsAndTypesNoColumnMapping() {
        val columnName = "test-column"
        val fieldType = FieldType(StringType, false)
        val declaredColumns = mapOf(columnName to fieldType)

        val columns =
            snowflakeColumnUtils.columnsAndTypes(
                columns = declaredColumns,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        assertEquals(DEFAULT_COLUMNS.size + 1, columns.size)
        assertEquals("VARCHAR", columns.find { it.columnName == columnName }?.columnType)
    }

    @Test
    fun testGeneratingColumnsAndTypesWithColumnMapping() {
        val columnName = "test-column"
        val mappedColumnName = "mapped-column-name"
        val fieldType = FieldType(StringType, false)
        val declaredColumns = mapOf(columnName to fieldType)
        val columnNameMapping = ColumnNameMapping(mapOf(columnName to mappedColumnName))

        val columns =
            snowflakeColumnUtils.columnsAndTypes(
                columns = declaredColumns,
                columnNameMapping = columnNameMapping
            )
        assertEquals(DEFAULT_COLUMNS.size + 1, columns.size)
        assertEquals("VARCHAR", columns.find { it.columnName == mappedColumnName }?.columnType)
    }

    @Test
    fun testToDialectType() {
        assertEquals(
            SnowflakeDataType.BOOLEAN.typeName,
            snowflakeColumnUtils.toDialectType(BooleanType)
        )
        assertEquals(SnowflakeDataType.DATE.typeName, snowflakeColumnUtils.toDialectType(DateType))
        assertEquals(
            SnowflakeDataType.INTEGER.typeName,
            snowflakeColumnUtils.toDialectType(IntegerType)
        )
        assertEquals(
            SnowflakeDataType.NUMBER.typeName,
            snowflakeColumnUtils.toDialectType(NumberType)
        )
        assertEquals(
            SnowflakeDataType.VARCHAR.typeName,
            snowflakeColumnUtils.toDialectType(StringType)
        )
        assertEquals(
            SnowflakeDataType.TIME.typeName,
            snowflakeColumnUtils.toDialectType(TimeTypeWithTimezone)
        )
        assertEquals(
            SnowflakeDataType.TIME.typeName,
            snowflakeColumnUtils.toDialectType(TimeTypeWithoutTimezone)
        )
        assertEquals(
            SnowflakeDataType.TIMESTAMP_TZ.typeName,
            snowflakeColumnUtils.toDialectType(TimestampTypeWithTimezone)
        )
        assertEquals(
            SnowflakeDataType.TIMESTAMP_NTZ.typeName,
            snowflakeColumnUtils.toDialectType(TimestampTypeWithoutTimezone)
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(ArrayType(items = FieldType(StringType, false)))
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(ArrayTypeWithoutSchema)
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(
                ObjectType(
                    properties = LinkedHashMap(),
                    additionalProperties = false,
                )
            )
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(ObjectTypeWithEmptySchema)
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(ObjectTypeWithoutSchema)
        )
        assertEquals(
            SnowflakeDataType.VARCHAR.typeName,
            snowflakeColumnUtils.toDialectType(
                UnionType(
                    options = setOf(StringType),
                    isLegacyUnion = true,
                )
            )
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(
                UnionType(
                    options = emptySet(),
                    isLegacyUnion = false,
                )
            )
        )
        assertEquals(
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(UnknownType(schema = mockk<JsonNode>()))
        )
    }
}
