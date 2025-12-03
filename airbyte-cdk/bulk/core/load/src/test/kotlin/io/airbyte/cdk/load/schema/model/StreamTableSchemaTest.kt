/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.StringType
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class StreamTableSchemaTest {
    @Test
    fun `getCursor returns mapped column names for dedupe`() {
        val columnSchema =
            ColumnSchema(
                inputSchema = Fixtures.cursorColumns,
                inputToFinalColumnNames = Fixtures.cursorColumnMapping,
                finalSchema = Fixtures.cursorFinalSchema,
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("id")),
                        cursor = listOf("updated_at", "modified_date"),
                    ),
            )

        val result = streamTableSchema.getCursor()

        assertEquals(listOf("updated_at_final", "modified_date_final"), result)
    }

    @Test
    fun `getCursor returns empty list for append`() {
        val columnSchema =
            ColumnSchema(
                inputSchema = mapOf("updated_at" to FieldType(IntegerType, false)),
                inputToFinalColumnNames = mapOf("updated_at" to "updated_at_final"),
                finalSchema = mapOf("updated_at_final" to ColumnType("INTEGER", false)),
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType = Append,
            )

        val result = streamTableSchema.getCursor()

        assertEquals(emptyList<String>(), result)
    }

    @Test
    fun `getPrimaryKey returns mapped column names for dedupe`() {
        val columnSchema =
            ColumnSchema(
                inputSchema = Fixtures.primaryKeyColumns,
                inputToFinalColumnNames = Fixtures.primaryKeyColumnMapping,
                finalSchema = Fixtures.primaryKeyFinalSchema,
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("id"), listOf("user_id", "org_id")),
                        cursor = emptyList()
                    )
            )

        val result = streamTableSchema.getPrimaryKey()

        assertEquals(listOf(listOf("id_final"), listOf("user_id_final", "org_id_final")), result)
    }

    @Test
    fun `getPrimaryKey returns empty list for append`() {
        val columnSchema =
            ColumnSchema(
                inputSchema = mapOf("id" to FieldType(IntegerType, false)),
                inputToFinalColumnNames = mapOf("id" to "id_final"),
                finalSchema = mapOf("id_final" to ColumnType("INTEGER", false))
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType = Append,
            )

        val result = streamTableSchema.getPrimaryKey()

        assertEquals(emptyList<List<String>>(), result)
    }

    @Test
    fun `getFinalColumnName returns mapped name`() {
        val columnSchema =
            ColumnSchema(
                inputSchema =
                    mapOf(
                        "original_name" to FieldType(StringType, false),
                        "another_column" to FieldType(IntegerType, false),
                    ),
                inputToFinalColumnNames =
                    mapOf("original_name" to "mapped_name", "another_column" to "another_mapped"),
                finalSchema =
                    mapOf(
                        "mapped_name" to ColumnType("STRING", false),
                        "another_mapped" to ColumnType("INTEGER", false)
                    )
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType = Append,
            )

        assertEquals("mapped_name", streamTableSchema.getFinalColumnName("original_name"))
        assertEquals("another_mapped", streamTableSchema.getFinalColumnName("another_column"))
    }

    @Test
    fun `handles empty cursor and primary key for dedupe`() {
        val columnSchema =
            ColumnSchema(
                inputSchema = emptyMap(),
                inputToFinalColumnNames = emptyMap(),
                finalSchema = emptyMap()
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType = Dedupe(primaryKey = emptyList(), cursor = emptyList())
            )

        assertEquals(emptyList<String>(), streamTableSchema.getCursor())
        assertEquals(emptyList<List<String>>(), streamTableSchema.getPrimaryKey())
    }

    @Test
    fun `handles complex composite primary key mapping`() {
        val columnSchema =
            ColumnSchema(
                inputSchema = Fixtures.compositeKeyColumns,
                inputToFinalColumnNames = Fixtures.compositeKeyColumnMapping,
                finalSchema = Fixtures.compositeKeyFinalSchema,
            )

        val streamTableSchema =
            StreamTableSchema(
                tableNames = Fixtures.defaultTableNames,
                columnSchema = columnSchema,
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("tenant_id", "region_code", "product_id")),
                        cursor = listOf("tenant_id")
                    )
            )

        assertEquals(
            listOf(listOf("TENANT_ID", "REGION_CODE", "PRODUCT_ID")),
            streamTableSchema.getPrimaryKey()
        )
        assertEquals(listOf("TENANT_ID"), streamTableSchema.getCursor())
    }

    object Fixtures {
        val defaultTableName = TableName("namespace", "table")
        val defaultTableNames = TableNames(finalTableName = defaultTableName)

        val cursorColumns =
            mapOf(
                "updated_at" to FieldType(IntegerType, false),
                "modified_date" to FieldType(StringType, false),
            )

        val cursorColumnMapping =
            mapOf(
                "updated_at" to "updated_at_final",
                "modified_date" to "modified_date_final",
            )

        val cursorFinalSchema =
            mapOf(
                "updated_at_final" to ColumnType("INTEGER", false),
                "modified_date_final" to ColumnType("STRING", false),
            )

        val primaryKeyColumns =
            mapOf(
                "id" to FieldType(IntegerType, false),
                "user_id" to FieldType(IntegerType, false),
                "org_id" to FieldType(IntegerType, false),
            )

        val primaryKeyColumnMapping =
            mapOf(
                "id" to "id_final",
                "user_id" to "user_id_final",
                "org_id" to "org_id_final",
            )

        val primaryKeyFinalSchema =
            mapOf(
                "id_final" to ColumnType("INTEGER", false),
                "user_id_final" to ColumnType("INTEGER", false),
                "org_id_final" to ColumnType("INTEGER", false),
            )

        val compositeKeyColumns =
            mapOf(
                "tenant_id" to FieldType(IntegerType, false),
                "region_code" to FieldType(StringType, false),
                "product_id" to FieldType(IntegerType, false),
            )

        val compositeKeyColumnMapping =
            mapOf(
                "tenant_id" to "TENANT_ID",
                "region_code" to "REGION_CODE",
                "product_id" to "PRODUCT_ID",
            )

        val compositeKeyFinalSchema =
            mapOf(
                "TENANT_ID" to ColumnType("INTEGER", false),
                "REGION_CODE" to ColumnType("STRING", false),
                "PRODUCT_ID" to ColumnType("INTEGER", false),
            )
    }
}
