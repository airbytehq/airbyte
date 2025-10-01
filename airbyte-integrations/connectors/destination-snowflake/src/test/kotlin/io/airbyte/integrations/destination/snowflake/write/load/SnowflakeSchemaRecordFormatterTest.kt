/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.sql.DEFAULT_COLUMNS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeSchemaRecordFormatterTest {

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
            DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() } + listOf(columnName)
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter(columns, snowflakeColumnUtils)
        val formattedValue = formatter.format(record)
        val expectedValue = createExpected(record, columns)
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMissingColumn() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns =
            DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() } + listOf(columnName)
        val record = createRecord(columnName, columnValue)
        val formatter =
            SnowflakeSchemaRecordFormatter(columns + listOf("missing-column"), snowflakeColumnUtils)
        val formattedValue = formatter.format(record)
        val expectedValue = createExpected(record, columns, false)
        assertEquals(expectedValue, formattedValue)
    }
}
