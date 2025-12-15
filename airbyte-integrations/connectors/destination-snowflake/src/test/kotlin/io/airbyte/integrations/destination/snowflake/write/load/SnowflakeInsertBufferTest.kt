/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

/* Entire test class commented out - needs refactoring for new CDK architecture

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.TableName
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
                snowflakeColumnUtils = snowflakeColumnUtils,
            )
        assertEquals(0, buffer.getAccumulatedRecordCount())
        runBlocking { buffer.accumulate(record) }
        assertEquals(1, buffer.getAccumulatedRecordCount())
    }

    @Test
    fun testFlushToStaging() {
        val tableName = mockk<TableName>(relaxed = true)
        val stagingFile = "stage.csv.gz"
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
                flushLimit = 1,
            )
        runBlocking {
            buffer.accumulate(record)
            buffer.flushTruncateStream()
            coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
            coVerify(exactly = 1) {
                snowflakeAirbyteClient.copyFromStage(tableName, stagingFile)
            }
        }
    }

    @Test
    fun testFlushToNoStaging() {
        val tableName = mockk<TableName>(relaxed = true)
        val column = "columnName"
        val columns = linkedMapOf(column to "NUMBER(38,0)")
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
                flushLimit = 1,
            )
        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
            coVerify(exactly = 1) { snowflakeAirbyteClient.insertRecord(tableName, record) }
        }
    }

    @Test
    fun testFileCreation() {
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
                flushLimit = 1,
            )
        runBlocking {
            buffer.accumulate(record)
            val filepath = buffer.writeToStaging()
            val file = File(filepath).toPath()
            assert(exists(file))
            val lines = mutableListOf<String>()
            GZIPInputStream(file.toFile().inputStream()).use { gzip ->
                BufferedReader(InputStreamReader(gzip)).use { bufferedReader ->
                    bufferedReader.forEachLine { line -> lines.add(line) }
                }
            }
            assertEquals(1, lines.size)
            file.toFile().delete()
        }
    }

    private fun createRecord(column: String): Map<String, AirbyteValue> {
        return mapOf(
            column to IntegerValue(value = 42),
            Meta.COLUMN_NAME_AB_GENERATION_ID to NullValue,
            Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id-1"),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(1234567890),
            Meta.COLUMN_NAME_AB_META to StringValue("meta-data-foo"),
        )
    }
}

*/
