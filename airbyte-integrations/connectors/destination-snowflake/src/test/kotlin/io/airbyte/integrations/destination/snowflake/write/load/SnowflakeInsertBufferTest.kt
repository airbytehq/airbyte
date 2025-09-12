/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeInsertBufferTest {

    @Test
    fun testAccumulate() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val columns = listOf(column)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = mapOf(column to AirbyteValue.from("test-value"))
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
            )

        buffer.accumulate(record)

        assertEquals(1, buffer.recordQueue.size)
    }

    @Test
    fun testFlush() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val columns = listOf(column)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = mapOf(column to AirbyteValue.from("test-value"))
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
            )

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
        coVerify(exactly = 1) { snowflakeAirbyteClient.copyFromStage(tableName) }
    }
}
