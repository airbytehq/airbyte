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
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.every
import io.mockk.mockk
import kotlin.collections.LinkedHashMap
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeColumnUtilsTest {

    private lateinit var snowflakeConfiguration: SnowflakeConfiguration
    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setup() {
        snowflakeConfiguration = mockk(relaxed = true)
        snowflakeColumnUtils = SnowflakeColumnUtils(snowflakeConfiguration)
    }

    @Test
    fun testDefaultColumns() {
        assertEquals(DEFAULT_COLUMNS, snowflakeColumnUtils.defaultColumns())
    }

    @Test
    fun testDefaultRawColumns() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        assertEquals(
            DEFAULT_COLUMNS + listOf(RAW_DATA_COLUMN),
            snowflakeColumnUtils.defaultColumns()
        )
    }

    @Test
    fun testGetColumnName() {
        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val columnNames = snowflakeColumnUtils.getColumnNames(columnNameMapping)
        val expectedColumnNames =
            (DEFAULT_COLUMNS.map { it.columnName } + listOf("actual")).joinToString(",") {
                "\"$it\""
            }
        assertEquals(expectedColumnNames, columnNames)
    }

    @Test
    fun testGetRawColumnName() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val columnNames = snowflakeColumnUtils.getColumnNames(columnNameMapping)
        val expectedColumnNames =
            (DEFAULT_COLUMNS.map { it.columnName } + listOf(RAW_DATA_COLUMN.columnName))
                .joinToString(",") { "\"$it\"" }
        assertEquals(expectedColumnNames, columnNames)
    }

    @Test
    fun testGeneratingRawTableColumnsAndTypesNoColumnMapping() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        val columns =
            snowflakeColumnUtils.columnsAndTypes(
                columns = emptyMap(),
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        assertEquals(DEFAULT_COLUMNS.size + 1, columns.size)
        assertEquals(
            "${SnowflakeDataType.VARCHAR.typeName} $NOT_NULL",
            columns.find { it.columnName == RAW_DATA_COLUMN.columnName }?.columnType
        )
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
        assertEquals(
            SnowflakeDataType.VARCHAR.typeName,
            columns.find { it.columnName == columnName }?.columnType
        )
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
        assertEquals(
            SnowflakeDataType.VARCHAR.typeName,
            columns.find { it.columnName == mappedColumnName }?.columnType
        )
    }

    @Test
    fun testToDialectType() {
        assertEquals(
            SnowflakeDataType.BOOLEAN.typeName,
            snowflakeColumnUtils.toDialectType(BooleanType)
        )
        assertEquals(SnowflakeDataType.DATE.typeName, snowflakeColumnUtils.toDialectType(DateType))
        assertEquals(
            SnowflakeDataType.NUMBER.typeName,
            snowflakeColumnUtils.toDialectType(IntegerType)
        )
        assertEquals(
            SnowflakeDataType.FLOAT.typeName,
            snowflakeColumnUtils.toDialectType(NumberType)
        )
        assertEquals(
            SnowflakeDataType.VARCHAR.typeName,
            snowflakeColumnUtils.toDialectType(StringType)
        )
        assertEquals(
            SnowflakeDataType.VARCHAR.typeName,
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
            SnowflakeDataType.VARIANT.typeName,
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
            SnowflakeDataType.VARCHAR.typeName,
            snowflakeColumnUtils.toDialectType(UnknownType(schema = mockk<JsonNode>()))
        )
    }
}
