/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlin.io.path.exists
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeInsertBufferTest {

    private lateinit var snowflakeConfiguration: SnowflakeConfiguration

    @BeforeEach
    fun setUp() {
        snowflakeConfiguration = mockk(relaxed = true)
    }

    @Test
    fun testAccumulate() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val columns = listOf(column)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                flushLimit = 1,
            )

        buffer.accumulate(record)

        assertEquals(true, buffer.csvFilePath?.exists())
        assertEquals(1, buffer.recordCount)
    }

    @Test
    fun testAccumulateRaw() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val columns = listOf(column)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                flushLimit = 1,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

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
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                flushLimit = 1,
            )

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
        coVerify(exactly = 1) { snowflakeAirbyteClient.copyFromStage(tableName) }
    }

    @Test
    fun testFlushRaw() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val columns = listOf(column)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                flushLimit = 1,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

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
        val record = createRecord(column1)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                flushLimit = 1,
            )

        runBlocking {
            buffer.accumulate(record)
            assertEquals(
                "test-value${CSV_FORMAT.delimiterString}${CSV_FORMAT.recordSeparator}",
                buffer.csvFilePath?.toFile()?.readText()
            )
            buffer.flush()
            coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
            coVerify(exactly = 1) { snowflakeAirbyteClient.copyFromStage(tableName) }
        }
    }

    @Test
    fun testMissingFieldsRaw() {
        val tableName = mockk<TableName>()
        val column1 = "columnName1"
        val column2 = "columnName2"
        val columns = listOf(column1, column2)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column1)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                flushLimit = 1,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        runBlocking {
            buffer.accumulate(record)
            assertEquals(
                "test-value${CSV_FORMAT.delimiterString}${CSV_FORMAT.recordSeparator}",
                buffer.csvFilePath?.toFile()?.readText()
            )
            buffer.flush()
            coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
            coVerify(exactly = 1) { snowflakeAirbyteClient.copyFromStage(tableName) }
        }
    }

    private fun createRecord(columnName: String) =
        mapOf(
            columnName to AirbyteValue.from("test-value"),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(System.currentTimeMillis()),
            Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id"),
            Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1223),
            Meta.COLUMN_NAME_AB_META to StringValue("{\"changes\":[],\"syncId\":43}"),
            "${columnName}Null" to NullValue
        )
}
