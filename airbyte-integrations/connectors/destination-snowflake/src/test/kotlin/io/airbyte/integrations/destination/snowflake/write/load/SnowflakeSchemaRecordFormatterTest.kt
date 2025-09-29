/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.integrations.destination.snowflake.sql.DEFAULT_COLUMNS
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeSchemaRecordFormatterTest {

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = DEFAULT_COLUMNS.map { it.columnName } + listOf(columnName)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter(columns)
        val formattedValue = formatter.format(record)
        val expectedValue = createExpected(record, columns)
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMissingColumn() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = DEFAULT_COLUMNS.map { it.columnName } + listOf(columnName)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter(columns + listOf("missing-column"))
        val formattedValue = formatter.format(record)
        val expectedValue = createExpected(record, columns, false)
        assertEquals(expectedValue, formattedValue)
    }
}
