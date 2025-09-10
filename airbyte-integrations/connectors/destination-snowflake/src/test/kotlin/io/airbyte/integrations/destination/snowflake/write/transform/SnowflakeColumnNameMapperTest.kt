/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeColumnNameMapperTest {

    @Test
    fun testGetMappedColumnName() {
        val columnName = "test-column-name"
        val stream = mockk<DestinationStream>()
        val mapper = SnowflakeColumnNameMapper()
        val result = mapper.getMappedColumnName(stream = stream, columnName = columnName)
        assertEquals(columnName, result)
    }
}
