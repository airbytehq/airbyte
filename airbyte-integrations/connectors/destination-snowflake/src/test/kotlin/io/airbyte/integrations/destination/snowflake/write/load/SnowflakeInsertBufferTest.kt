/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.mockk.coVerify
import io.mockk.mockk
import kotlin.io.path.exists
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

        assertEquals(true, buffer.csvFilePath?.exists())
        assertEquals(1, buffer.recordCount)
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

    @Test
    fun testMissingFields() {
        val tableName = mockk<TableName>()
        val column1 = "columnName1"
        val column2 = "columnName2"
        val columns = listOf(column1, column2)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = mapOf(column1 to AirbyteValue.from("test-value"))
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
            )

        runBlocking {
            buffer.accumulate(record)
            println("${buffer.csvFilePath?.toFile()?.readText()}")
            assertEquals(
                "test-value${CSV_FORMAT.delimiterString}${CSV_FORMAT.recordSeparator}",
                buffer.csvFilePath?.toFile()?.readText()
            )
            buffer.flush()
            coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
            coVerify(exactly = 1) { snowflakeAirbyteClient.copyFromStage(tableName) }
        }
    }
}
