/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeSchemaRecordFormatterTest {

    private fun createColumnSchema(userColumns: Map<String, String>): ColumnSchema {
        val finalSchema = linkedMapOf<String, ColumnType>()
        val inputToFinalColumnNames = mutableMapOf<String, String>()
        val inputSchema = mutableMapOf<String, FieldType>()

        // Add user columns
        userColumns.forEach { (name, type) ->
            val finalName = name.toSnowflakeCompatibleName()
            finalSchema[finalName] = ColumnType(type, true)
            inputToFinalColumnNames[name] = finalName
            inputSchema[name] = FieldType(StringType, nullable = true)
        }

        return ColumnSchema(
            inputToFinalColumnNames = inputToFinalColumnNames,
            finalSchema = finalSchema,
            inputSchema = inputSchema
        )
    }

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val userColumns = mapOf(columnName to "VARCHAR(16777216)")
        val columnSchema = createColumnSchema(userColumns)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter()
        val formattedValue = formatter.format(record, columnSchema)
        val expectedValue =
            createExpected(
                record = record,
                columnSchema = columnSchema,
            )
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingVariant() {
        val columnName = "test-column-name"
        val columnValue = "{\"test\": \"test-value\"}"
        val userColumns = mapOf(columnName to "VARIANT")
        val columnSchema = createColumnSchema(userColumns)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter()
        val formattedValue = formatter.format(record, columnSchema)
        val expectedValue =
            createExpected(
                record = record,
                columnSchema = columnSchema,
            )
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMissingColumn() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val userColumns =
            mapOf(columnName to "VARCHAR(16777216)", "missing-column" to "VARCHAR(16777216)")
        val columnSchema = createColumnSchema(userColumns)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter()
        val formattedValue = formatter.format(record, columnSchema)
        val expectedValue =
            createExpected(
                record = record,
                columnSchema = columnSchema,
                filterMissing = false,
            )
        assertEquals(expectedValue, formattedValue)
    }

    private fun createRecord(columnName: String, columnValue: String) = buildMap {
        put(columnName.toSnowflakeCompatibleName(), AirbyteValue.from(columnValue))
        put(COLUMN_NAME_AB_EXTRACTED_AT, IntegerValue(System.currentTimeMillis()))
        put(COLUMN_NAME_AB_RAW_ID, StringValue("raw-id"))
        put(COLUMN_NAME_AB_GENERATION_ID, IntegerValue(1223))
        put(COLUMN_NAME_AB_META, StringValue("{\"changes\":[],\"syncId\":43}"))
        put("${columnName}Null".toSnowflakeCompatibleName(), NullValue)
    }

    private fun createExpected(
        record: Map<String, AirbyteValue>,
        columnSchema: ColumnSchema,
        filterMissing: Boolean = true,
    ): List<Any> {
        val columns = columnSchema.finalSchema.keys.toList()
        val result = mutableListOf<Any>()

        // Add meta columns first in the expected order
        result.add(record[COLUMN_NAME_AB_RAW_ID]?.toCsvValue() ?: "")
        result.add(record[COLUMN_NAME_AB_EXTRACTED_AT]?.toCsvValue() ?: "")
        result.add(record[COLUMN_NAME_AB_META]?.toCsvValue() ?: "")
        result.add(record[COLUMN_NAME_AB_GENERATION_ID]?.toCsvValue() ?: "")

        // Add user columns
        val userColumns =
            columns.filterNot { col ->
                listOf(
                        COLUMN_NAME_AB_RAW_ID.toSnowflakeCompatibleName(),
                        COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName(),
                        COLUMN_NAME_AB_META.toSnowflakeCompatibleName(),
                        COLUMN_NAME_AB_GENERATION_ID.toSnowflakeCompatibleName()
                    )
                    .contains(col)
            }

        userColumns.forEach { columnName ->
            val value = record[columnName] ?: if (!filterMissing) NullValue else null
            if (value != null || !filterMissing) {
                result.add(value?.toCsvValue() ?: "")
            }
        }

        return result
    }
}
