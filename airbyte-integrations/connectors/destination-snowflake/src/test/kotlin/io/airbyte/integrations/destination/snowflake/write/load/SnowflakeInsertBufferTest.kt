/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference
import java.util.zip.GZIPInputStream
import kotlin.io.path.exists
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeInsertBufferTest {

    private lateinit var snowflakeConfiguration: SnowflakeConfiguration
    private lateinit var columnManager: SnowflakeColumnManager
    private lateinit var columnSchema: ColumnSchema
    private lateinit var snowflakeRecordFormatter: SnowflakeRecordFormatter

    @BeforeEach
    fun setUp() {
        snowflakeConfiguration = mockk(relaxed = true)
        snowflakeRecordFormatter = SnowflakeSchemaRecordFormatter()
        columnManager =
            mockk(relaxed = true) {
                every { getMetaColumns() } returns
                    linkedMapOf(
                        "_AIRBYTE_RAW_ID" to ColumnType("VARCHAR", false),
                        "_AIRBYTE_EXTRACTED_AT" to ColumnType("TIMESTAMP_TZ", false),
                        "_AIRBYTE_META" to ColumnType("VARIANT", false),
                        "_AIRBYTE_GENERATION_ID" to ColumnType("NUMBER", true)
                    )
                every { getTableColumnNames(any()) } returns
                    listOf(
                        "_AIRBYTE_RAW_ID",
                        "_AIRBYTE_EXTRACTED_AT",
                        "_AIRBYTE_META",
                        "_AIRBYTE_GENERATION_ID",
                        "columnName"
                    )
            }
    }

    @Test
    fun testAccumulate() {
        val tableName = TableName(namespace = "test", name = "table")
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("NUMBER", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
            )
        assertEquals(0, buffer.recordCount)
        runBlocking { buffer.accumulate(record) }
        assertEquals(1, buffer.recordCount)
    }

    @Test
    fun testFlushToStaging() {
        val tableName = TableName(namespace = "test", name = "table")
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("NUMBER", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
                flushLimit = 1,
            )
        val expectedColumnNames =
            listOf(
                "_AIRBYTE_RAW_ID",
                "_AIRBYTE_EXTRACTED_AT",
                "_AIRBYTE_META",
                "_AIRBYTE_GENERATION_ID",
                "columnName"
            )
        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
            coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
            coVerify(exactly = 1) {
                snowflakeAirbyteClient.copyFromStage(tableName, any(), expectedColumnNames)
            }
        }
    }

    @Test
    fun testFlushToNoStaging() {
        val tableName = TableName(namespace = "test", name = "table")
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("NUMBER", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        every { snowflakeConfiguration.legacyRawTablesOnly } returns true
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
                flushLimit = 1,
            )
        val expectedColumnNames =
            listOf(
                "_AIRBYTE_RAW_ID",
                "_AIRBYTE_EXTRACTED_AT",
                "_AIRBYTE_META",
                "_AIRBYTE_GENERATION_ID",
                "columnName"
            )
        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
            // In legacy raw mode, it still uses staging
            coVerify(exactly = 1) { snowflakeAirbyteClient.putInStage(tableName, any()) }
            coVerify(exactly = 1) {
                snowflakeAirbyteClient.copyFromStage(tableName, any(), expectedColumnNames)
            }
        }
    }

    @Test
    fun testFileCreation() {
        val tableName = TableName(namespace = "test", name = "table")
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("NUMBER", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = createRecord(column)
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
                flushLimit = 1,
            )
        runBlocking {
            buffer.accumulate(record)
            // The csvFilePath is internal, we can access it for testing
            val filepath = buffer.csvFilePath
            assertNotNull(filepath)
            val file = filepath!!.toFile()
            assert(file.exists())
            // Close the writer to ensure all data is flushed
            buffer.csvWriter?.close()
            val lines = mutableListOf<String>()
            GZIPInputStream(file.inputStream()).use { gzip ->
                BufferedReader(InputStreamReader(gzip)).use { bufferedReader ->
                    bufferedReader.forEachLine { line -> lines.add(line) }
                }
            }
            assertEquals(1, lines.size)
            file.delete()
        }
    }

    @Test
    fun testCsvFieldsWithTrailingWhitespaceUseExistingUnquotedCsvBehaviorByDefault() {
        val tableName = TableName(namespace = "test", name = "table")
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("VARCHAR", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record =
            mapOf(
                column.uppercase() to StringValue("hello   "),
                Meta.COLUMN_NAME_AB_GENERATION_ID to NullValue,
                Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id-1"),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(1234567890),
                Meta.COLUMN_NAME_AB_META to StringValue("meta-data-foo"),
            )
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
                flushLimit = 1,
            )
        runBlocking {
            buffer.accumulate(record)
            val filepath = buffer.csvFilePath
            assertNotNull(filepath)
            val file = filepath!!.toFile()
            buffer.csvWriter?.close()

            val lines = mutableListOf<String>()
            GZIPInputStream(file.inputStream()).use { gzip ->
                BufferedReader(InputStreamReader(gzip)).use { bufferedReader ->
                    bufferedReader.forEachLine { line -> lines.add(line) }
                }
            }

            assertEquals(1, lines.size)
            assertTrue(
                lines[0].endsWith(",hello   "),
                "Default CSV output should stay unquoted so existing Snowflake TRIM_SPACE behavior is unchanged"
            )
            file.delete()
        }
    }

    @Test
    fun `Snowflake PUT and COPY run on the caller's dispatcher thread`() {
        val tableName = TableName(namespace = "test", name = "table")
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("NUMBER", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val putThreadName = AtomicReference<String>()
        val copyThreadName = AtomicReference<String>()
        val snowflakeAirbyteClient =
            mockk<SnowflakeAirbyteClient>(relaxed = true) {
                every { putInStage(any(), any()) } answers
                    {
                        putThreadName.set(Thread.currentThread().name)
                    }
                every { copyFromStage(any(), any(), any()) } answers
                    {
                        copyThreadName.set(Thread.currentThread().name)
                    }
            }
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
            )
        val callerDispatcher =
            Executors.newSingleThreadExecutor { Thread(it, "caller-flush") }.asCoroutineDispatcher()
        try {
            runBlocking(callerDispatcher) {
                buffer.accumulate(createRecord(column))
                buffer.flush()
            }
        } finally {
            callerDispatcher.close()
        }
        // Coroutine debug mode may suffix the thread name with " @coroutine#N".
        assertTrue(putThreadName.get().startsWith("caller-flush"))
        assertTrue(copyThreadName.get().startsWith("caller-flush"))
    }

    @Test
    fun `concurrent flushes never exceed the caller dispatcher parallelism`() {
        val column = "columnName"
        columnSchema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf(column to column.uppercase()),
                finalSchema = mapOf(column.uppercase() to ColumnType("NUMBER", true)),
                inputSchema = mapOf(column to FieldType(StringType, nullable = true))
            )
        val inFlight = AtomicInteger(0)
        val maxInFlight = AtomicInteger(0)
        val snowflakeAirbyteClient =
            mockk<SnowflakeAirbyteClient>(relaxed = true) {
                every { putInStage(any(), any()) } answers
                    {
                        inFlight.incrementAndGet()
                        maxInFlight.updateAndGet { max -> maxOf(max, inFlight.get()) }
                        Thread.sleep(50)
                        inFlight.decrementAndGet()
                    }
                every { copyFromStage(any(), any(), any()) } answers
                    {
                        inFlight.incrementAndGet()
                        maxInFlight.updateAndGet { max -> maxOf(max, inFlight.get()) }
                        Thread.sleep(50)
                        inFlight.decrementAndGet()
                    }
            }
        val buffers =
            (1..20).map { i ->
                SnowflakeInsertBuffer(
                    tableName = TableName(namespace = "test", name = "table_$i"),
                    snowflakeClient = snowflakeAirbyteClient,
                    snowflakeConfiguration = snowflakeConfiguration,
                    columnSchema = columnSchema,
                    columnManager = columnManager,
                    snowflakeRecordFormatter = snowflakeRecordFormatter,
                )
            }
        val callerDispatcher = Executors.newFixedThreadPool(2).asCoroutineDispatcher()
        try {
            runBlocking {
                withTimeout(30_000) {
                    buffers.forEach { it.accumulate(createRecord(column)) }
                    coroutineScope { buffers.map { launch(callerDispatcher) { it.flush() } } }
                }
            }
        } finally {
            callerDispatcher.close()
        }
        assertTrue(
            maxInFlight.get() <= 2,
            "Expected at most 2 concurrent JDBC calls, saw ${maxInFlight.get()}"
        )
        coVerify(exactly = 20) { snowflakeAirbyteClient.putInStage(any(), any()) }
        coVerify(exactly = 20) { snowflakeAirbyteClient.copyFromStage(any(), any(), any()) }
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
