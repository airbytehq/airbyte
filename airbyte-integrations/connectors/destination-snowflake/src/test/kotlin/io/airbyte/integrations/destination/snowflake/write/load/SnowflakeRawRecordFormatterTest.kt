/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.sql.DEFAULT_COLUMNS
import io.airbyte.integrations.destination.snowflake.sql.RAW_COLUMNS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.every
import io.mockk.mockk
import java.util.AbstractMap
import kotlin.collections.plus
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

private val AIRBYTE_COLUMN_NAMES =
    DEFAULT_COLUMNS.map { it.columnName } + RAW_COLUMNS.map { it.columnName }

internal fun createRecord(columnName: String, columnValue: String, rawFormat: Boolean = false) =
    buildMap {
        put(columnName, AirbyteValue.from(columnValue))
        put(Meta.COLUMN_NAME_AB_EXTRACTED_AT, IntegerValue(System.currentTimeMillis()))
        if (rawFormat) {
            put(Meta.COLUMN_NAME_AB_LOADED_AT, IntegerValue(System.currentTimeMillis()))
        }
        put(Meta.COLUMN_NAME_AB_RAW_ID, StringValue("raw-id"))
        put(Meta.COLUMN_NAME_AB_GENERATION_ID, IntegerValue(1223))
        put(Meta.COLUMN_NAME_AB_META, StringValue("{\"changes\":[],\"syncId\":43}"))
        put("${columnName}Null", NullValue)
    }

internal fun createExpected(
    record: Map<String, AirbyteValue>,
    columns: List<String>,
    airbyteColumns: List<String>,
    filterMissing: Boolean = true,
    formatColumnName: Boolean = true,
) =
    record.entries
        .associate {
            val key = if (formatColumnName) formatColumnName(it.key) else it.key
            key to it.value
        }
        .map { entry ->
            if (airbyteColumns.contains(entry.key)) AbstractMap.SimpleEntry(entry.key, entry.value)
            else entry
        }
        .sortedBy { entry ->
            if (columns.indexOf(entry.key) > -1) columns.indexOf(entry.key) else Int.MAX_VALUE
        }
        .filter { (k, _) -> if (filterMissing) columns.contains(k) else true }
        .map { it.value.toCsvValue() }

internal fun formatColumnName(name: String) = name.toSnowflakeCompatibleName()

internal class SnowflakeRawRecordFormatterTest {

    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setup() {
        snowflakeColumnUtils = mockk {
            every { formatColumnName(any(), any()) } answers { firstArg<String>() }
            every { getFormattedDefaultColumnNames(any()) } returns AIRBYTE_COLUMN_NAMES
        }
    }

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = AIRBYTE_COLUMN_NAMES
        val record =
            createRecord(columnName = columnName, columnValue = columnValue, rawFormat = true)
        val formatter = SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(
                record = record,
                columns = columns,
                airbyteColumns = AIRBYTE_COLUMN_NAMES,
                formatColumnName = false
            ) + listOf("{\"$columnName\":\"$columnValue\"}")
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMigratedFromPreviousVersion() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns =
            listOf(
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_LOADED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_DATA,
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_GENERATION_ID
            )
        val record =
            createRecord(columnName = columnName, columnValue = columnValue, rawFormat = true)
        val formatter = SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(
                    record = record,
                    columns = columns,
                    airbyteColumns = AIRBYTE_COLUMN_NAMES,
                    formatColumnName = false
                )
                .toMutableList()
        expectedValue.add(
            columns.indexOf(Meta.COLUMN_NAME_DATA),
            "{\"$columnName\":\"$columnValue\"}"
        )
        assertEquals(expectedValue, formattedValue)
    }
}
