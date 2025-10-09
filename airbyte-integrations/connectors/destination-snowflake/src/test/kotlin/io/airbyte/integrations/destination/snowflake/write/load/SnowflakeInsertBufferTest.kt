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
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.util.zip.GZIPInputStream
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeInsertBufferTest {

    private lateinit var snowflakeConfiguration: SnowflakeConfiguration
    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setUp() {
        snowflakeConfiguration = mockk(relaxed = true)
        snowflakeColumnUtils = mockk(relaxed = true)
    }

    @Test
    fun testAccumulate() {
        val tableName = mockk<TableName>(relaxed = true)
        val column = "columnName"
        val columns = linkedMapOf(column to "NUMBER(38,0)")
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        buffer.accumulate(record)

        assertEquals(1, buffer.recordCount)
    }

    @Test
    fun testAccumulateRaw() {
        val tableName = mockk<TableName>(relaxed = true)
        val column = "columnName"
        val columns = linkedMapOf(column to "NUMBER(38,0)")
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        buffer.accumulate(record)

        assertEquals(1, buffer.recordCount)
    }

    @Test
    fun testFlush() {
        val tableName = mockk<TableName>(relaxed = true)
        val column = "columnName"
        val columns = linkedMapOf(column to "NUMBER(38,0)")
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        coVerify(exactly = 1) {
            snowflakeAirbyteClient.uploadToStage(tableName, any(), any(), any())
        }
        coVerify(exactly = 1) {
            snowflakeAirbyteClient.copyFromStage(tableName, match { it.endsWith("$CSV_FILE_EXTENSION$FILE_SUFFIX") })
        }
    }

    @Test
    fun testFlushRaw() {
        val tableName = mockk<TableName>(relaxed = true)
        val column = "columnName"
        val columns = linkedMapOf(column to "NUMBER(38,0)")
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        coVerify(exactly = 1) {
            snowflakeAirbyteClient.uploadToStage(tableName, any(), any(), any())
        }
        coVerify(exactly = 1) {
            snowflakeAirbyteClient.copyFromStage(tableName, match { it.endsWith("$CSV_FILE_EXTENSION$FILE_SUFFIX") })
        }
    }

    @Test
    fun testMissingFields() {
        val tableName = mockk<TableName>(relaxed = true)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord("COLUMN1")
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = linkedMapOf("COLUMN1" to "NUMBER(38,0)", "COLUMN2" to "NUMBER(38,0)"),
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        runBlocking {
            buffer.accumulate(record)
            assertEquals("test-value$CSV_FIELD_SEPARATOR$CSV_LINE_DELIMITER", readContents(buffer))
        }
    }

    @Test
    fun testMissingFieldsRaw() {
        val tableName = mockk<TableName>(relaxed = true)
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord("COLUMN1")
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = linkedMapOf("COLUMN1" to "NUMBER(38,0)", "COLUMN2" to "NUMBER(38,0)"),
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        runBlocking {
            buffer.accumulate(record)
            assertEquals("test-value$CSV_FIELD_SEPARATOR$CSV_LINE_DELIMITER", readContents(buffer))
        }
    }

    private fun readContents(buffer: SnowflakeInsertBuffer) =
        GZIPInputStream(buffer.getInputStream(buffer.buffer)).bufferedReader().use { it.readText() }

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
