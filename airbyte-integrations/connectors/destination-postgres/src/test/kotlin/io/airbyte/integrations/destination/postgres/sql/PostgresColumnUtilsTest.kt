/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresColumnUtilsTest {

    private lateinit var config: PostgresConfiguration
    private lateinit var columnUtils: PostgresColumnUtils

    @BeforeEach
    fun setUp() {
        config = mockk()
        columnUtils = PostgresColumnUtils(config)
    }

    @Test
    fun testDefaultColumns() {
        every { config.legacyRawTablesOnly } returns false
        val columns = columnUtils.defaultColumns()

        assertEquals(4, columns.size)
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_RAW_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_EXTRACTED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_META })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_GENERATION_ID })
        assertFalse(columns.any { it.columnName == COLUMN_NAME_AB_LOADED_AT })
        assertFalse(columns.any { it.columnName == COLUMN_NAME_DATA })
    }

    @Test
    fun testDefaultColumnsForRawTables() {
        every { config.legacyRawTablesOnly } returns true
        val columns = columnUtils.defaultColumns()

        assertEquals(6, columns.size)
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_RAW_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_EXTRACTED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_META })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_GENERATION_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_LOADED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_DATA })
    }

    @Test
    fun testGetTargetColumns() {
        every { config.legacyRawTablesOnly } returns false

        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(IntegerType, nullable = false),
                                "name" to FieldType(StringType, nullable = true)
                            )
                    )
            }
        val columnNameMapping = ColumnNameMapping(mapOf("id" to "targetId"))

        val columns = columnUtils.getTargetColumns(stream, columnNameMapping)

        // Should return default columns (4) + user columns (2) = 6
        assertEquals(6, columns.size)
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_RAW_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_EXTRACTED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_META })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_GENERATION_ID })

        val idColumn = columns.find { it.columnName == "targetId" }!!
        assertEquals("bigint", idColumn.columnTypeName)
        assertFalse(idColumn.nullable)

        val nameColumn = columns.find { it.columnName == "name" }!!
        assertEquals("varchar", nameColumn.columnTypeName)
        assertTrue(nameColumn.nullable)
    }

    @Test
    fun testGetTargetColumnsInRawMode() {
        every { config.legacyRawTablesOnly } returns true

        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(IntegerType, nullable = false),
                                "name" to FieldType(StringType, nullable = true),
                                "email" to FieldType(StringType, nullable = false)
                            )
                    )
            }
        val columnNameMapping = ColumnNameMapping(emptyMap())

        val columns = columnUtils.getTargetColumns(stream, columnNameMapping)

        // Should only return default columns (6 in raw mode), no user columns
        assertEquals(6, columns.size)
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_RAW_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_EXTRACTED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_META })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_GENERATION_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_LOADED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_DATA })
    }

    @Test
    fun testGetTargetColumnsWithEmptySchema() {
        every { config.legacyRawTablesOnly } returns false

        val stream = mockk<DestinationStream> { every { schema } returns ObjectTypeWithEmptySchema }
        val columnNameMapping = ColumnNameMapping(emptyMap())

        val columns = columnUtils.getTargetColumns(stream, columnNameMapping)

        // Should only return default columns
        assertEquals(4, columns.size)
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_RAW_ID })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_EXTRACTED_AT })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_META })
        assertTrue(columns.any { it.columnName == COLUMN_NAME_AB_GENERATION_ID })
    }

    @Test
    fun testGetTargetColumnName() {
        val columnNameMapping = ColumnNameMapping(mapOf("sourceId" to "targetId"))

        assertEquals("targetId", columnUtils.getTargetColumnName("sourceId", columnNameMapping))
        assertEquals("sourceName", columnUtils.getTargetColumnName("sourceName", columnNameMapping))
    }

    @Test
    fun testToDialectTypeMapping() {
        assertEquals("boolean", columnUtils.toDialectType(BooleanType))
        assertEquals("date", columnUtils.toDialectType(DateType))
        assertEquals("bigint", columnUtils.toDialectType(IntegerType))
        assertEquals("decimal", columnUtils.toDialectType(NumberType))
        assertEquals("varchar", columnUtils.toDialectType(StringType))
        assertEquals("time with time zone", columnUtils.toDialectType(TimeTypeWithTimezone))
        assertEquals("time", columnUtils.toDialectType(TimeTypeWithoutTimezone))
        assertEquals(
            "timestamp with time zone",
            columnUtils.toDialectType(TimestampTypeWithTimezone)
        )
        assertEquals("timestamp", columnUtils.toDialectType(TimestampTypeWithoutTimezone))

        assertEquals(
            "jsonb",
            columnUtils.toDialectType(ArrayType(items = FieldType(StringType, false)))
        )
        assertEquals("jsonb", columnUtils.toDialectType(ArrayTypeWithoutSchema))
        assertEquals("jsonb", columnUtils.toDialectType(ObjectType(linkedMapOf())))
        assertEquals("jsonb", columnUtils.toDialectType(ObjectTypeWithEmptySchema))
        assertEquals("jsonb", columnUtils.toDialectType(ObjectTypeWithoutSchema))
        assertEquals("jsonb", columnUtils.toDialectType(UnknownType(mockk<JsonNode>())))
    }

    @Test
    fun testToDialectTypeMappingUnions() {
        val unionWithStruct =
            UnionType(
                options =
                    setOf(
                        StringType,
                        ObjectType(linkedMapOf("field" to FieldType(StringType, nullable = false)))
                    ),
                isLegacyUnion = true
            )
        assertEquals("jsonb", columnUtils.toDialectType(unionWithStruct))

        val unionWithBasicTypes =
            UnionType(options = setOf(StringType, IntegerType), isLegacyUnion = true)
        assertEquals("jsonb", columnUtils.toDialectType(unionWithBasicTypes))
    }
}
