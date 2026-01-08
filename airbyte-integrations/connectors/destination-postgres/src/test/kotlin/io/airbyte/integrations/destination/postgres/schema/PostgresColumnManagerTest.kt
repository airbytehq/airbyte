/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresColumnManagerTest {

    private lateinit var config: PostgresConfiguration
    private lateinit var columnManager: PostgresColumnManager

    @BeforeEach
    fun setUp() {
        config = mockk()
        columnManager = PostgresColumnManager(config)
    }

    @Test
    fun testGetMetaColumnsInSchemaMode() {
        every { config.legacyRawTablesOnly } returns false

        val metaColumns = columnManager.getMetaColumns()

        assertEquals(4, metaColumns.size)
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_RAW_ID))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_META))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_GENERATION_ID))
        assertFalse(metaColumns.contains(COLUMN_NAME_AB_LOADED_AT))
        assertFalse(metaColumns.contains(COLUMN_NAME_DATA))
    }

    @Test
    fun testGetMetaColumnsInRawMode() {
        every { config.legacyRawTablesOnly } returns true

        val metaColumns = columnManager.getMetaColumns()

        assertEquals(6, metaColumns.size)
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_RAW_ID))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_META))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_GENERATION_ID))
        assertTrue(metaColumns.contains(COLUMN_NAME_AB_LOADED_AT))
        assertTrue(metaColumns.contains(COLUMN_NAME_DATA))
    }

    @Test
    fun testGetTableColumnsInSchemaMode() {
        every { config.legacyRawTablesOnly } returns false

        val columnSchema =
            ColumnSchema(
                inputSchema = mapOf("name" to FieldType(StringType, nullable = true)),
                inputToFinalColumnNames = mapOf("name" to "name"),
                finalSchema =
                    linkedMapOf(
                        "id" to ColumnType("bigint", false),
                        "name" to ColumnType("varchar", true),
                        "email" to ColumnType("varchar", false),
                    ),
            )

        val columns = columnManager.getTableColumns(columnSchema)

        // Should return 4 meta columns + 3 user columns = 7
        assertEquals(7, columns.size)

        // Meta columns should come first
        assertEquals(COLUMN_NAME_AB_RAW_ID, columns[0])
        assertEquals(COLUMN_NAME_AB_EXTRACTED_AT, columns[1])
        assertEquals(COLUMN_NAME_AB_META, columns[2])
        assertEquals(COLUMN_NAME_AB_GENERATION_ID, columns[3])

        // User columns should follow
        assertEquals("id", columns[4])
        assertEquals("name", columns[5])
        assertEquals("email", columns[6])
    }

    @Test
    fun testGetTableColumnsInRawMode() {
        every { config.legacyRawTablesOnly } returns true

        val columnSchema =
            ColumnSchema(
                inputSchema = mapOf("name" to FieldType(StringType, nullable = true)),
                inputToFinalColumnNames = mapOf("name" to "name"),
                finalSchema =
                    linkedMapOf(
                        "id" to ColumnType("bigint", false),
                        "name" to ColumnType("varchar", true),
                    ),
            )

        val columns = columnManager.getTableColumns(columnSchema)

        // In raw mode, should only return 6 meta columns (no user columns)
        assertEquals(6, columns.size)
        assertTrue(columns.contains(COLUMN_NAME_AB_RAW_ID))
        assertTrue(columns.contains(COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(columns.contains(COLUMN_NAME_AB_META))
        assertTrue(columns.contains(COLUMN_NAME_AB_GENERATION_ID))
        assertTrue(columns.contains(COLUMN_NAME_AB_LOADED_AT))
        assertTrue(columns.contains(COLUMN_NAME_DATA))

        // User columns should NOT be included
        assertFalse(columns.contains("id"))
        assertFalse(columns.contains("name"))
    }

    @Test
    fun testGetTableColumnsWithEmptyFinalSchema() {
        every { config.legacyRawTablesOnly } returns false

        val columnSchema =
            ColumnSchema(
                inputSchema = emptyMap(),
                inputToFinalColumnNames = emptyMap(),
                finalSchema = emptyMap(),
            )

        val columns = columnManager.getTableColumns(columnSchema)

        // Should only return 4 meta columns
        assertEquals(4, columns.size)
        assertTrue(columns.contains(COLUMN_NAME_AB_RAW_ID))
        assertTrue(columns.contains(COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(columns.contains(COLUMN_NAME_AB_META))
        assertTrue(columns.contains(COLUMN_NAME_AB_GENERATION_ID))
    }

    @Test
    fun testColumnOrderIsPreserved() {
        every { config.legacyRawTablesOnly } returns false

        // Use linkedMapOf to ensure insertion order is preserved
        val columnSchema =
            ColumnSchema(
                inputSchema = emptyMap(),
                inputToFinalColumnNames = emptyMap(),
                finalSchema =
                    linkedMapOf(
                        "z_column" to ColumnType("varchar", true),
                        "a_column" to ColumnType("varchar", true),
                        "m_column" to ColumnType("varchar", true),
                    ),
            )

        val columns = columnManager.getTableColumns(columnSchema)

        // User columns should maintain their order from finalSchema
        assertEquals("z_column", columns[4])
        assertEquals("a_column", columns[5])
        assertEquals("m_column", columns[6])
    }
}
