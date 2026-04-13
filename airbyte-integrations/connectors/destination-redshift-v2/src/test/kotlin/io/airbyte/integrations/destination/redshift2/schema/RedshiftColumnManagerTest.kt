/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

class RedshiftColumnManagerTest {

    private val columnManager = RedshiftColumnManager()

    @Test
    fun `getMetaColumns returns four columns with correct types`() {
        val metaColumns = columnManager.getMetaColumns()

        assertEquals(4, metaColumns.size)

        assertEquals(
            ColumnType("varchar(36)", false),
            metaColumns[Meta.COLUMN_NAME_AB_RAW_ID],
        )
        assertEquals(
            ColumnType("timestamptz", false),
            metaColumns[Meta.COLUMN_NAME_AB_EXTRACTED_AT],
        )
        assertEquals(
            ColumnType("super", false),
            metaColumns[Meta.COLUMN_NAME_AB_META],
        )
        assertEquals(
            ColumnType("bigint", false),
            metaColumns[Meta.COLUMN_NAME_AB_GENERATION_ID],
        )
    }

    @Test
    fun `getMetaColumns returns all non-nullable`() {
        val metaColumns = columnManager.getMetaColumns()
        metaColumns.values.forEach { columnType ->
            assertFalse(
                columnType.nullable,
                "Meta column ${columnType.type} should be non-nullable",
            )
        }
    }

    @Test
    fun `getMetaColumnNames returns expected set`() {
        val names = columnManager.getMetaColumnNames()

        assertEquals(
            setOf(
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_AB_GENERATION_ID,
            ),
            names,
        )
    }

    @Test
    fun `getTableColumnNames returns meta columns then user columns in order`() {
        val userColumns =
            mapOf(
                "user_name" to ColumnType("varchar(65535)", false),
                "age" to ColumnType("bigint", true),
            )
        val columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = userColumns.keys.associateWith { it },
                finalSchema = userColumns,
                inputSchema = emptyMap(),
            )

        val allColumns = columnManager.getTableColumnNames(columnSchema)

        assertEquals(
            listOf(
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_AB_GENERATION_ID,
                "user_name",
                "age",
            ),
            allColumns,
        )
    }

    @Test
    fun `getGenerationIdColumnName returns correct constant`() {
        assertEquals(Meta.COLUMN_NAME_AB_GENERATION_ID, columnManager.getGenerationIdColumnName())
    }
}
