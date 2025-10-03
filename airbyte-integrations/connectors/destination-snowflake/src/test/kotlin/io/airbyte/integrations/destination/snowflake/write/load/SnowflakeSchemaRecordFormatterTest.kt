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

private val AIRBYTE_COLUMNS = DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }

internal class SnowflakeSchemaRecordFormatterTest {

    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setup() {
        snowflakeColumnUtils = mockk {
            every { formatColumnName(any(), any()) } answers
                {
                    firstArg<String>().toSnowflakeCompatibleName()
                }
            every { getFormattedDefaultColumnNames(any()) } returns AIRBYTE_COLUMNS
        }
    }

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = AIRBYTE_COLUMNS + listOf(columnName.toSnowflakeCompatibleName())
        val record = createRecord(columnName, columnValue)
        val formatter = SnowflakeSchemaRecordFormatter(columns, snowflakeColumnUtils)
        val formattedValue = formatter.format(record)
        val expectedValue = createExpected(record, columns, AIRBYTE_COLUMNS)
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMissingColumn() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns = AIRBYTE_COLUMNS + listOf(columnName.toSnowflakeCompatibleName())
        val record = createRecord(columnName, columnValue)
        val formatter =
            SnowflakeSchemaRecordFormatter(
                columns + listOf("missing-column".toSnowflakeCompatibleName()),
                snowflakeColumnUtils
            )
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(
                record = record,
                columns = columns,
                airbyteColumns = AIRBYTE_COLUMNS,
                filterMissing = false
            )
        assertEquals(expectedValue, formattedValue)
    }
}
