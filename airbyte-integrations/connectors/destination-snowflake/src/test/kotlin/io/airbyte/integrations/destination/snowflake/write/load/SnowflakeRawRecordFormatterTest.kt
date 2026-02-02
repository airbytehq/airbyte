/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.schema.model.ColumnSchema
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private val AIRBYTE_COLUMN_TYPES_MAP =
    linkedMapOf(
        COLUMN_NAME_AB_RAW_ID to "VARCHAR(16777216)",
        COLUMN_NAME_AB_EXTRACTED_AT to "TIMESTAMP_TZ(9)",
        COLUMN_NAME_AB_META to "VARIANT",
        COLUMN_NAME_AB_GENERATION_ID to "NUMBER(38,0)",
        COLUMN_NAME_AB_LOADED_AT to "TIMESTAMP_TZ(9)",
        COLUMN_NAME_DATA to "VARIANT",
    )

private fun createRecord(columnName: String, columnValue: String) = buildMap {
    put(columnName, AirbyteValue.from(columnValue))
    put(COLUMN_NAME_AB_EXTRACTED_AT, IntegerValue(System.currentTimeMillis()))
    put(COLUMN_NAME_AB_LOADED_AT, IntegerValue(System.currentTimeMillis()))
    put(COLUMN_NAME_AB_RAW_ID, StringValue("raw-id"))
    put(COLUMN_NAME_AB_GENERATION_ID, IntegerValue(1223))
    put(COLUMN_NAME_AB_META, StringValue("{\"changes\":[],\"syncId\":43}"))
    put("${columnName}Null", NullValue)
}

private fun createExpected(
    record: Map<String, AirbyteValue>,
    columns: Map<String, String>,
    airbyteColumns: List<String>,
) =
    record.entries
        .filter { entry -> airbyteColumns.contains(entry.key) }
        .sortedBy { entry ->
            if (columns.keys.indexOf(entry.key) > -1) columns.keys.indexOf(entry.key)
            else Int.MAX_VALUE
        }
        .map { it.value.toCsvValue() }

internal class SnowflakeRawRecordFormatterTest {

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = AIRBYTE_COLUMN_TYPES_MAP
        val record = createRecord(columnName = columnName, columnValue = columnValue)
        val formatter = SnowflakeRawRecordFormatter()
        // RawRecordFormatter doesn't use columnSchema but still needs one per interface
        val dummyColumnSchema = ColumnSchema(emptyMap(), emptyMap(), emptyMap())
        val formattedValue = formatter.format(record, dummyColumnSchema)
        val expectedValue =
            createExpected(
                record = record,
                columns = columns,
                airbyteColumns = AIRBYTE_COLUMN_TYPES_MAP.keys.toList(),
            ) + listOf("{\"$columnName\":\"$columnValue\"}")
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMigratedFromPreviousVersion() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val record = createRecord(columnName = columnName, columnValue = columnValue)
        val formatter = SnowflakeRawRecordFormatter()
        // RawRecordFormatter doesn't use columnSchema but still needs one per interface
        val dummyColumnSchema = ColumnSchema(emptyMap(), emptyMap(), emptyMap())
        val formattedValue = formatter.format(record, dummyColumnSchema)

        // The formatter outputs in a fixed order regardless of input column order:
        // 1. AB_RAW_ID
        // 2. AB_EXTRACTED_AT
        // 3. AB_META
        // 4. AB_GENERATION_ID
        // 5. AB_LOADED_AT
        // 6. DATA (JSON with remaining columns)
        val expectedValue =
            listOf(
                record[COLUMN_NAME_AB_RAW_ID]!!.toCsvValue(),
                record[COLUMN_NAME_AB_EXTRACTED_AT]!!.toCsvValue(),
                record[COLUMN_NAME_AB_META]!!.toCsvValue(),
                record[COLUMN_NAME_AB_GENERATION_ID]!!.toCsvValue(),
                record[COLUMN_NAME_AB_LOADED_AT]!!.toCsvValue(),
                "{\"$columnName\":\"$columnValue\"}"
            )
        assertEquals(expectedValue, formattedValue)
    }
}
