/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.BufferedReader
import java.io.File
import java.io.InputStreamReader
import java.util.zip.GZIPInputStream
import kotlin.io.path.exists
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
                flushLimit = 1,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        buffer.accumulate(record)

        assertEquals(true, buffer.csvFilePath?.exists())
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
                flushLimit = 1,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        buffer.accumulate(record)

        assertEquals(true, buffer.csvFilePath?.exists())
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
                flushLimit = 1,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
        coVerify(exactly = 1) {
            snowflakeAirbyteClient.copyFromStage(
                tableName,
                match { it.endsWith("$CSV_FILE_EXTENSION$FILE_SUFFIX") }
            )
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
                flushLimit = 1,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
        coVerify(exactly = 1) {
            snowflakeAirbyteClient.copyFromStage(
                tableName,
                match { it.endsWith("$CSV_FILE_EXTENSION$FILE_SUFFIX") }
            )
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
                flushLimit = 1,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        runBlocking {
            buffer.accumulate(record)
            buffer.csvWriter?.flush()
            buffer.csvWriter?.close()
            assertEquals(
                "test-value$CSV_FIELD_SEPARATOR$CSV_LINE_DELIMITER",
                readFromCsvFile(buffer.csvFilePath!!.toFile())
            )
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
                flushLimit = 1,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        every { snowflakeConfiguration.legacyRawTablesOnly } returns true

        runBlocking {
            buffer.accumulate(record)
            buffer.csvWriter?.flush()
            buffer.csvWriter?.close()
            assertEquals(
                "test-value$CSV_FIELD_SEPARATOR$CSV_LINE_DELIMITER",
                readFromCsvFile(buffer.csvFilePath!!.toFile())
            )
        }
    }

    private fun readFromCsvFile(file: File) =
        GZIPInputStream(file.inputStream()).use { input ->
            val reader = BufferedReader(InputStreamReader(input))
            reader.readText()
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
