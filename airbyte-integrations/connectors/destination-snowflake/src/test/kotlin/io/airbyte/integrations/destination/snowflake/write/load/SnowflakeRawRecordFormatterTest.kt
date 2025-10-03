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
import io.airbyte.integrations.destination.snowflake.sql.DEFAULT_COLUMNS
import kotlin.collections.plus
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeRawRecordFormatterTest {

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = DEFAULT_COLUMNS.map { it.columnName } + listOf(Meta.COLUMN_NAME_DATA)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeRawRecordFormatter(columns)
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(record, columns) + listOf("{\"$columnName\":\"$columnValue\"}")
        assertEquals(expectedValue, formattedValue)
    }

    private fun createRecord(columnName: String, columnValue: String) =
        mapOf(
            columnName to AirbyteValue.from(columnValue),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(System.currentTimeMillis()),
            Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id"),
            Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1223),
            Meta.COLUMN_NAME_AB_META to StringValue("{\"changes\":[],\"syncId\":43}"),
            "${columnName}Null" to NullValue
        )

    private fun createExpected(record: Map<String, AirbyteValue>, columns: List<String>) =
        record.entries
            .sortedBy { entry ->
                if (columns.indexOf(entry.key) > -1) columns.indexOf(entry.key) else Int.MAX_VALUE
            }
            .filter { (k, _) -> columns.contains(k) }
            .map { it.value.toCsvValue() }
}
