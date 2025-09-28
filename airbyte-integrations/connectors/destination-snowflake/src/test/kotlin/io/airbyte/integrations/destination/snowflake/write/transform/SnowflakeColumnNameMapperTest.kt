/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeColumnNameMapperTest {

    @Test
    fun testGetMappedColumnName() {
        val columnName = "tést-column-name"
        val expectedName = "test-column-name"
        val stream = mockk<DestinationStream>()
        val tableCatalog = mockk<TableCatalog>()
        val snowflakeConfiguration = mockk<SnowflakeConfiguration>(relaxed = true)

        // Configure the mock to return the expected mapped column name
        every { tableCatalog.getMappedColumnName(stream, columnName) } returns expectedName

        val mapper = SnowflakeColumnNameMapper(tableCatalog, snowflakeConfiguration)
        val result = mapper.getMappedColumnName(stream = stream, columnName = columnName)
        assertEquals(expectedName, result)
    }

    @Test
    fun testGetMappedColumnNameRawFormat() {
        val columnName = "tést-column-name"
        val stream = mockk<DestinationStream>()
        val tableCatalog = mockk<TableCatalog>()
        val snowflakeConfiguration =
            mockk<SnowflakeConfiguration> { every { legacyRawTablesOnly } returns true }

        val mapper = SnowflakeColumnNameMapper(tableCatalog, snowflakeConfiguration)
        val result = mapper.getMappedColumnName(stream = stream, columnName = columnName)
        assertEquals(columnName, result)
    }
}
