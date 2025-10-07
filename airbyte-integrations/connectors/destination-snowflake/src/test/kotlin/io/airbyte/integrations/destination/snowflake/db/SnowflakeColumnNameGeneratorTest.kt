/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeColumnNameGeneratorTest {

    @Test
    fun testGetColumnName() {
        val column = "test-column"
        val generator =
            SnowflakeColumnNameGenerator(mockk { every { legacyRawTablesOnly } returns false })
        val columnName = generator.getColumnName(column)
        assertEquals(column.toSnowflakeCompatibleName(), columnName.displayName)
        assertEquals(column.toSnowflakeCompatibleName(), columnName.canonicalName)
    }
}
