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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.snowflake.db.SnowflakeColumnNameGenerator
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.every
import io.mockk.mockk
import kotlin.collections.LinkedHashMap
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeColumnUtilsTest {

    private lateinit var snowflakeConfiguration: SnowflakeConfiguration
    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils
    private lateinit var snowflakeColumnNameGenerator: SnowflakeColumnNameGenerator

    @BeforeEach
    fun setup() {
        snowflakeConfiguration = mockk(relaxed = true)
        snowflakeColumnNameGenerator =
            mockk(relaxed = true) {
                every { getColumnName(any()) } answers
                    {
                        val displayName =
                            if (snowflakeConfiguration.legacyRawTablesOnly) firstArg<String>()
                            else firstArg<String>().toSnowflakeCompatibleName()
                        val canonicalName =
                            if (snowflakeConfiguration.legacyRawTablesOnly) firstArg<String>()
                            else firstArg<String>().toSnowflakeCompatibleName()
                        ColumnNameGenerator.ColumnName(
                            displayName = displayName,
                            canonicalName = canonicalName,
                        )
                    }
            }
        snowflakeColumnUtils =
            SnowflakeColumnUtils(snowflakeConfiguration, snowflakeColumnNameGenerator)
    }

    @Test
    fun testDefaultColumns() {
        val expectedDefaultColumns = DEFAULT_COLUMNS
        assertEquals(expectedDefaultColumns, snowflakeColumnUtils.defaultColumns())
    }

    @Test
    fun testDefaultRawColumns() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        val expectedDefaultColumns = DEFAULT_COLUMNS + RAW_COLUMNS

        assertEquals(expectedDefaultColumns, snowflakeColumnUtils.defaultColumns())
    }

    @Test
    fun testGetFormattedDefaultColumnNames() {
        val expectedDefaultColumnNames =
            DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }
        val defaultColumnNames = snowflakeColumnUtils.getFormattedDefaultColumnNames()
        assertEquals(expectedDefaultColumnNames, defaultColumnNames)
    }

    @Test
    fun testGetFormattedDefaultColumnNamesQuoted() {
        val expectedDefaultColumnNames =
            DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName().quote() }
        val defaultColumnNames = snowflakeColumnUtils.getFormattedDefaultColumnNames(true)
        assertEquals(expectedDefaultColumnNames, defaultColumnNames)
    }

    @Test
    fun testGetColumnName() {
        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val columnNames = snowflakeColumnUtils.getColumnNames(columnNameMapping)
        val expectedColumnNames =
            (DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() } + listOf("actual"))
                .joinToString(",") { it.quote() }
        assertEquals(expectedColumnNames, columnNames)
    }

    @Test
    fun testGetRawColumnName() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val columnNames = snowflakeColumnUtils.getColumnNames(columnNameMapping)
        val expectedColumnNames =
            (DEFAULT_COLUMNS.map { it.columnName } + RAW_COLUMNS.map { it.columnName })
                .joinToString(",") { it.quote() }
        assertEquals(expectedColumnNames, columnNames)
    }

    @Test
    fun testGetRawFormattedColumnNames() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true
        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val schemaColumns =
            mapOf(
                "column_one" to FieldType(StringType, true),
                "column_two" to FieldType(IntegerType, true),
                "original" to FieldType(StringType, true),
                CDC_DELETED_AT_COLUMN to FieldType(TimestampTypeWithTimezone, true)
            )
        val expectedColumnNames =
            DEFAULT_COLUMNS.map { it.columnName.quote() } +
                RAW_COLUMNS.map { it.columnName.quote() }

        val columnNames =
            snowflakeColumnUtils.getFormattedColumnNames(
                columns = schemaColumns,
                columnNameMapping = columnNameMapping
            )
        assertEquals(expectedColumnNames.size, columnNames.size)
        assertEquals(expectedColumnNames.sorted(), columnNames.sorted())
    }

    @Test
    fun testGetFormattedColumnNames() {
        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val schemaColumns =
            mapOf(
                "column_one" to FieldType(StringType, true),
                "column_two" to FieldType(IntegerType, true),
                "original" to FieldType(StringType, true),
                CDC_DELETED_AT_COLUMN to FieldType(TimestampTypeWithTimezone, true)
            )
        val expectedColumnNames =
            listOf(
                    "actual",
                    "column_one",
                    "column_two",
                    CDC_DELETED_AT_COLUMN,
                )
                .map { it.quote() } +
                DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName().quote() }
        val columnNames =
            snowflakeColumnUtils.getFormattedColumnNames(
                columns = schemaColumns,
                columnNameMapping = columnNameMapping
            )
        assertEquals(expectedColumnNames.size, columnNames.size)
        assertEquals(expectedColumnNames.sorted(), columnNames.sorted())
    }

    @Test
    fun testGetFormattedColumnNamesNoQuotes() {
        val columnNameMapping = ColumnNameMapping(mapOf("original" to "actual"))
        val schemaColumns =
            mapOf(
                "column_one" to FieldType(StringType, true),
                "column_two" to FieldType(IntegerType, true),
                "original" to FieldType(StringType, true),
                CDC_DELETED_AT_COLUMN to FieldType(TimestampTypeWithTimezone, true)
            )
        val expectedColumnNames =
            listOf(
                "actual",
                "column_one",
                "column_two",
                CDC_DELETED_AT_COLUMN,
            ) + DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }
        val columnNames =
            snowflakeColumnUtils.getFormattedColumnNames(
                columns = schemaColumns,
                columnNameMapping = columnNameMapping,
                quote = false
            )
        assertEquals(expectedColumnNames.size, columnNames.size)
        assertEquals(expectedColumnNames.sorted(), columnNames.sorted())
    }

    @Test
    fun testGeneratingRawTableColumnsAndTypesNoColumnMapping() {
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        val columns =
            snowflakeColumnUtils.columnsAndTypes(
                columns = emptyMap(),
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        assertEquals(DEFAULT_COLUMNS.size + RAW_COLUMNS.size, columns.size)
        assertEquals(
            "${SnowflakeDataType.VARIANT.typeName} $NOT_NULL",
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
            "${SnowflakeDataType.VARCHAR.typeName} $NOT_NULL",
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
            "${SnowflakeDataType.VARCHAR.typeName} $NOT_NULL",
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
            SnowflakeDataType.ARRAY.typeName,
            snowflakeColumnUtils.toDialectType(ArrayType(items = FieldType(StringType, false)))
        )
        assertEquals(
            SnowflakeDataType.ARRAY.typeName,
            snowflakeColumnUtils.toDialectType(ArrayTypeWithoutSchema)
        )
        assertEquals(
            SnowflakeDataType.OBJECT.typeName,
            snowflakeColumnUtils.toDialectType(
                ObjectType(
                    properties = LinkedHashMap(),
                    additionalProperties = false,
                )
            )
        )
        assertEquals(
            SnowflakeDataType.OBJECT.typeName,
            snowflakeColumnUtils.toDialectType(ObjectTypeWithEmptySchema)
        )
        assertEquals(
            SnowflakeDataType.OBJECT.typeName,
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
            SnowflakeDataType.VARIANT.typeName,
            snowflakeColumnUtils.toDialectType(UnknownType(schema = mockk<JsonNode>()))
        )
    }

    @ParameterizedTest
    @CsvSource(
        value =
            [
                "$COLUMN_NAME_DATA, true, \"$COLUMN_NAME_DATA\"",
                "some-other_Column, true, \"SOME-OTHER_COLUMN\"",
                "$COLUMN_NAME_DATA, false, $COLUMN_NAME_DATA",
                "some-other_Column, false, SOME-OTHER_COLUMN",
                "$COLUMN_NAME_DATA, true, \"$COLUMN_NAME_DATA\"",
                "some-other_Column, true, \"SOME-OTHER_COLUMN\"",
            ]
    )
    fun testFormatColumnName(columnName: String, quote: Boolean, expectedFormattedName: String) {
        assertEquals(
            expectedFormattedName,
            snowflakeColumnUtils.formatColumnName(columnName, quote)
        )
    }
}
