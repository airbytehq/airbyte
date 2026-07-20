/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.coVerifyOrder
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.slot
import java.math.BigInteger
import java.text.SimpleDateFormat
import java.util.*
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
internal class RedshiftInsertBufferTest {

    @MockK lateinit var redshiftClient: RedshiftAirbyteClient

    private val tableName = TableName(namespace = "test_schema", name = "test_table")
    private val columns =
        listOf(
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "name"
        )

    private val s3Config =
        S3StagingConfiguration(
            s3BucketName = "my-bucket",
            s3BucketPath = "staging/data",
            s3BucketRegion = "us-west-2",
            accessKeyId = "AKID",
            secretAccessKey = "SECRET",
            purgeStagingData = true,
        )

    private val configuration =
        RedshiftConfiguration(
            host = "redshift.example.com",
            port = 5439,
            database = "mydb",
            schema = "public",
            username = "admin",
            password = "secret",
            jdbcUrlParams = null,
            uploadingMethod = s3Config,
            tunnelMethod = null,
            dropCascade = false,
        )

    private lateinit var buffer: RedshiftInsertBuffer

    @BeforeEach
    fun setUp() {
        coEvery { redshiftClient.uploadToS3(any(), any(), any()) } just Runs
        coEvery { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) } just Runs
        coEvery { redshiftClient.deleteFromS3(any(), any()) } just Runs

        buffer = RedshiftInsertBuffer(tableName, columns, redshiftClient, configuration)
    }

    @Test
    fun `accumulate and flush uploads to S3 and executes COPY`() = runTest {
        val record =
            mapOf(
                "_airbyte_raw_id" to StringValue("uuid-1"),
                "_airbyte_extracted_at" to StringValue("2026-01-01T00:00:00Z"),
                "_airbyte_meta" to StringValue("{}"),
                "_airbyte_generation_id" to IntegerValue(BigInteger.ZERO),
                "name" to StringValue("Alice"),
            )

        buffer.accumulate(record)
        assertEquals(1, buffer.recordCount)

        buffer.flush()

        // Verify the full pipeline: upload -> COPY -> cleanup
        coVerifyOrder {
            redshiftClient.uploadToS3(eq("my-bucket"), any(), any())
            redshiftClient.copyFromS3(
                tableName = eq(tableName),
                s3Path = match { it.startsWith("s3://my-bucket/staging/data/") },
                accessKeyId = eq("AKID"),
                secretAccessKey = eq("SECRET"),
                region = eq("us-west-2"),
            )
            redshiftClient.deleteFromS3(eq("my-bucket"), any())
        }

        // State is reset after flush
        assertEquals(0, buffer.recordCount)
    }

    @Test
    fun `flush with no data is a no-op`() = runTest {
        buffer.flush()

        coVerify(exactly = 0) { redshiftClient.uploadToS3(any(), any(), any()) }
        coVerify(exactly = 0) { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) }
    }

    @Test
    fun `uploaded data is valid gzip CSV with header`() = runTest {
        val record =
            mapOf(
                "_airbyte_raw_id" to StringValue("id-1"),
                "_airbyte_extracted_at" to StringValue("2026-04-01T12:00:00Z"),
                "_airbyte_meta" to StringValue("{}"),
                "_airbyte_generation_id" to IntegerValue(BigInteger.ONE),
                "name" to StringValue("Bob"),
            )

        buffer.accumulate(record)
        buffer.flush()

        val dataSlot = slot<ByteArray>()
        coVerify { redshiftClient.uploadToS3(any(), any(), capture(dataSlot)) }

        // Decompress and verify CSV content
        val csvContent =
            java.util.zip
                .GZIPInputStream(java.io.ByteArrayInputStream(dataSlot.captured))
                .bufferedReader()
                .readText()

        val lines = csvContent.trim().split("\n")
        assertEquals(2, lines.size, "Expected header + 1 data row")

        // Header row matches column names
        val header = lines[0]
        assertTrue(header.contains("_airbyte_raw_id"), "Header should contain _airbyte_raw_id")
        assertTrue(header.contains("name"), "Header should contain 'name'")

        // Data row has the right values
        val dataRow = lines[1]
        assertTrue(dataRow.contains("id-1"), "Data should contain raw_id value")
        assertTrue(dataRow.contains("Bob"), "Data should contain name value")
    }

    @Test
    fun `S3 key includes bucket path and table info`() = runTest {
        val record = mapOf("_airbyte_raw_id" to StringValue("x"), "name" to StringValue("y"))

        buffer.accumulate(record)
        buffer.flush()

        val keySlot = slot<String>()
        coVerify { redshiftClient.uploadToS3(any(), capture(keySlot), any()) }

        val key = keySlot.captured
        assertTrue(key.startsWith("staging/data/"), "Key should start with bucket path")
        assertTrue(key.contains("test_schema/"), "Key should contain namespace")
        assertTrue(key.contains("test_table/"), "Key should contain table name")
        assertTrue(key.endsWith(".csv.gz"), "Key should end with .csv.gz")
    }

    @Test
    fun `S3 key handles null bucket path`() = runTest {
        val noPrefixConfig = s3Config.copy(s3BucketPath = null)
        val noPrefixConfiguration = configuration.copy(uploadingMethod = noPrefixConfig)
        val bufferNoPrefix =
            RedshiftInsertBuffer(tableName, columns, redshiftClient, noPrefixConfiguration)

        bufferNoPrefix.accumulate(
            mapOf("_airbyte_raw_id" to StringValue("x"), "name" to StringValue("y"))
        )
        bufferNoPrefix.flush()

        val keySlot = slot<String>()
        coVerify { redshiftClient.uploadToS3(any(), capture(keySlot), any()) }

        val key = keySlot.captured
        assertTrue(key.startsWith("test_schema/"), "Key without prefix should start with namespace")
    }

    @Test
    fun `purge staging data is skipped when disabled`() = runTest {
        val noPurgeConfig = s3Config.copy(purgeStagingData = false)
        val noPurgeConfiguration = configuration.copy(uploadingMethod = noPurgeConfig)
        val noPurgeBuffer =
            RedshiftInsertBuffer(tableName, columns, redshiftClient, noPurgeConfiguration)

        noPurgeBuffer.accumulate(
            mapOf("_airbyte_raw_id" to StringValue("x"), "name" to StringValue("y"))
        )
        noPurgeBuffer.flush()

        coVerify(exactly = 1) { redshiftClient.uploadToS3(any(), any(), any()) }
        coVerify(exactly = 1) { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) }
        coVerify(exactly = 0) { redshiftClient.deleteFromS3(any(), any()) }
    }

    @Test
    fun `multiple accumulate calls batch into single flush`() = runTest {
        repeat(5) { i ->
            buffer.accumulate(
                mapOf(
                    "_airbyte_raw_id" to StringValue("id-$i"),
                    "name" to StringValue("name-$i"),
                )
            )
        }
        assertEquals(5, buffer.recordCount)

        buffer.flush()

        // Single upload + COPY for all 5 records
        coVerify(exactly = 1) { redshiftClient.uploadToS3(any(), any(), any()) }
        coVerify(exactly = 1) { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) }

        assertEquals(0, buffer.recordCount)
    }

    @Test
    fun `buffer can be reused after flush`() = runTest {
        buffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("batch1")))
        buffer.flush()

        buffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("batch2")))
        buffer.flush()

        coVerify(exactly = 2) { redshiftClient.uploadToS3(any(), any(), any()) }
        coVerify(exactly = 2) { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) }
    }

    @Test
    fun `flush propagates exceptions from copyFromS3`() = runTest {
        coEvery { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) } throws
            RuntimeException("COPY failed")

        buffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("x")))

        val exception = org.junit.jupiter.api.assertThrows<RuntimeException> { buffer.flush() }
        assertEquals("COPY failed", exception.message)

        // State is reset even after error
        assertEquals(0, buffer.recordCount)
    }

    // ================================================================
    // fileNamePattern tests
    // ================================================================

    @Test
    fun `null fileNamePattern uses default timestamp_uuid format`() {
        // s3Config already has fileNamePattern = null (default)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, configuration)
        val key = buf.buildStagingS3Key()

        assertTrue(key.startsWith("staging/data/test_schema/test_table/"), "Directory prefix")
        assertTrue(key.endsWith(".csv.gz"), "Extension")
        // Default format: {timestamp}_{8-char-uuid}.csv.gz
        val fileName = key.substringAfterLast("/")
        assertTrue(
            fileName.matches(Regex("""\d+_[a-f0-9]{8}\.csv\.gz""")),
            "Default format: $fileName"
        )
    }

    @Test
    fun `blank fileNamePattern uses default format`() {
        val blankPatternConfig = s3Config.copy(fileNamePattern = "   ")
        val blankConfiguration = configuration.copy(uploadingMethod = blankPatternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, blankConfiguration)
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        assertTrue(
            fileName.matches(Regex("""\d+_[a-f0-9]{8}\.csv\.gz""")),
            "Default format for blank: $fileName"
        )
    }

    @Test
    fun `fileNamePattern with date token resolves to yyyy_MM_dd`() {
        val patternConfig = s3Config.copy(fileNamePattern = "{date}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        // Should be like 2026_04_28.csv.gz (auto-appended extension)
        assertTrue(
            fileName.matches(Regex("""\d{4}_\d{2}_\d{2}\.csv\.gz""")),
            "Date format: $fileName"
        )
    }

    @Test
    fun `fileNamePattern with timestamp token resolves to epoch millis`() {
        val patternConfig = s3Config.copy(fileNamePattern = "{timestamp}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)

        val before = System.currentTimeMillis()
        val key = buf.buildStagingS3Key()
        val after = System.currentTimeMillis()

        val fileName = key.substringAfterLast("/")
        assertTrue(fileName.endsWith(".csv.gz"), "Extension present: $fileName")
        val timestampStr = fileName.removeSuffix(".csv.gz")
        val timestamp = timestampStr.toLong()
        assertTrue(timestamp in before..after, "Timestamp in range: $timestamp")
    }

    @Test
    fun `fileNamePattern with format_extension does not double-append`() {
        val patternConfig = s3Config.copy(fileNamePattern = "data_{date}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        // Should NOT have .csv.gz.csv.gz
        assertFalse(fileName.endsWith(".csv.gz.csv.gz"), "No double extension: $fileName")
        assertTrue(fileName.endsWith(".csv.gz"), "Ends with extension: $fileName")
        assertTrue(fileName.startsWith("data_"), "Starts with prefix: $fileName")
    }

    @Test
    fun `fileNamePattern without format_extension auto-appends csv gz`() {
        val patternConfig = s3Config.copy(fileNamePattern = "myfile_{date}_{timestamp}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        assertTrue(fileName.endsWith(".csv.gz"), "Auto-appended extension: $fileName")
        assertTrue(fileName.startsWith("myfile_"), "Prefix preserved: $fileName")
    }

    @Test
    fun `fileNamePattern with part_number increments across flushes`() {
        val patternConfig = s3Config.copy(fileNamePattern = "part_{part_number}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)

        val key1 = buf.buildStagingS3Key()
        val key2 = buf.buildStagingS3Key()
        val key3 = buf.buildStagingS3Key()

        val fileName1 = key1.substringAfterLast("/")
        val fileName2 = key2.substringAfterLast("/")
        val fileName3 = key3.substringAfterLast("/")

        assertEquals("part_0.csv.gz", fileName1)
        assertEquals("part_1.csv.gz", fileName2)
        assertEquals("part_2.csv.gz", fileName3)
    }

    @Test
    fun `fileNamePattern with extended date format`() {
        val patternConfig =
            s3Config.copy(fileNamePattern = "{date:yyyy_MM}_{part_number}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        // Should be like 2026_04_0.csv.gz
        assertTrue(
            fileName.matches(Regex("""\d{4}_\d{2}_\d+\.csv\.gz""")),
            "Extended date format: $fileName"
        )
    }

    @Test
    fun `fileNamePattern with timestamp millis extended placeholder`() {
        val patternConfig = s3Config.copy(fileNamePattern = "{timestamp:millis}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)

        val before = System.currentTimeMillis()
        val key = buf.buildStagingS3Key()
        val after = System.currentTimeMillis()

        val fileName = key.substringAfterLast("/")
        val timestampStr = fileName.removeSuffix(".csv.gz")
        val timestamp = timestampStr.toLong()
        assertTrue(timestamp in before..after, "Millis timestamp in range: $timestamp")
    }

    @Test
    fun `fileNamePattern with timestamp micro extended placeholder`() {
        val patternConfig = s3Config.copy(fileNamePattern = "{timestamp:micro}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)

        val beforeMicro = System.currentTimeMillis() * 1000
        val key = buf.buildStagingS3Key()
        val afterMicro = System.currentTimeMillis() * 1000

        val fileName = key.substringAfterLast("/")
        val microStr = fileName.removeSuffix(".csv.gz")
        val micro = microStr.toLong()
        assertTrue(micro in beforeMicro..afterMicro, "Micro timestamp in range: $micro")
    }

    @Test
    fun `fileNamePattern with spaces are replaced by underscores`() {
        val patternConfig = s3Config.copy(fileNamePattern = "my file {date}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        assertFalse(fileName.contains(" "), "No spaces: $fileName")
        assertTrue(fileName.startsWith("my_file_"), "Spaces replaced: $fileName")
    }

    @Test
    fun `fileNamePattern directory path is always preserved`() {
        val patternConfig =
            s3Config.copy(fileNamePattern = "{date}_{part_number}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)
        val key = buf.buildStagingS3Key()

        // Directory path should still be {bucketPath}/{namespace}/{tableName}/
        assertTrue(
            key.startsWith("staging/data/test_schema/test_table/"),
            "Directory unchanged: $key"
        )
    }

    @Test
    fun `fileNamePattern with all standard tokens combined`() {
        val patternConfig =
            s3Config.copy(fileNamePattern = "{date}_{timestamp}_{part_number}{format_extension}")
        val patternConfiguration = configuration.copy(uploadingMethod = patternConfig)
        val buf = RedshiftInsertBuffer(tableName, columns, redshiftClient, patternConfiguration)

        val before = System.currentTimeMillis()
        val key = buf.buildStagingS3Key()

        val fileName = key.substringAfterLast("/")
        assertTrue(fileName.endsWith(".csv.gz"), "Extension: $fileName")

        val dateFmt =
            SimpleDateFormat("yyyy_MM_dd").apply { timeZone = TimeZone.getTimeZone("UTC") }
        val todayDate = dateFmt.format(before)
        assertTrue(fileName.startsWith(todayDate), "Starts with today's date: $fileName")
        assertTrue(fileName.contains("_0.csv.gz"), "Contains part_number 0: $fileName")
    }
}
