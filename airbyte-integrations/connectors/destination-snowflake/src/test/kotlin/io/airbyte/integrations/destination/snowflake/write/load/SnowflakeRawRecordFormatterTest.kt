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
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.every
import io.mockk.mockk
import java.util.AbstractMap
import kotlin.collections.plus
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

private val AIRBYTE_COLUMN_NAMES =
    DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }.toSet()

internal fun createRecord(columnName: String, columnValue: String) =
    mapOf(
        columnName to AirbyteValue.from(columnValue),
        Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(System.currentTimeMillis()),
        Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id"),
        Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1223),
        Meta.COLUMN_NAME_AB_META to StringValue("{\"changes\":[],\"syncId\":43}"),
        "${columnName}Null" to NullValue
    )

internal fun createExpected(
    record: Map<String, AirbyteValue>,
    columns: List<String>,
    filterMissing: Boolean = true
) =
    record.entries
        .map { entry ->
            if (AIRBYTE_COLUMN_NAMES.contains(entry.key.toSnowflakeCompatibleName()))
                AbstractMap.SimpleEntry(entry.key.toSnowflakeCompatibleName(), entry.value)
            else entry
        }
        .sortedBy { entry ->
            if (columns.indexOf(entry.key) > -1) columns.indexOf(entry.key) else Int.MAX_VALUE
        }
        .filter { (k, _) -> if (filterMissing) columns.contains(k) else true }
        .map { it.value.toCsvValue() }

internal class SnowflakeRawRecordFormatterTest {

    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setup() {
        snowflakeColumnUtils = mockk {
            every { formatColumnName(any(), any()) } answers
                {
                    firstArg<String>().toSnowflakeCompatibleName()
                }
            every { getFormattedDefaultColumnNames(any()) } returns
                DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }
        }
    }

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns =
            DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() } +
                listOf(Meta.COLUMN_NAME_DATA)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(record, columns) + listOf("{\"$columnName\":\"$columnValue\"}")
        assertEquals(expectedValue, formattedValue)
    }
}
