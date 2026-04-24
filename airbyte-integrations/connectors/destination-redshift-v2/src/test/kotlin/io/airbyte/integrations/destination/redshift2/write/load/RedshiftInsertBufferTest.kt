/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write.load

import com.amazonaws.services.s3.model.ObjectMetadata
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.redshift2.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.config.S3StagingConfiguration
import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.coVerifyOrder
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.slot
import java.math.BigInteger
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
internal class RedshiftInsertBufferTest {

    @MockK lateinit var redshiftClient: RedshiftAirbyteClient

    private val tableName = TableName(namespace = "test_schema", name = "test_table")
    private val columns =
        listOf("_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id", "name")

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
        )

    private lateinit var buffer: RedshiftInsertBuffer

    @BeforeEach
    fun setUp() {
        coEvery { redshiftClient.uploadToS3(any(), any(), any(), any()) } just Runs
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
            redshiftClient.uploadToS3(eq("my-bucket"), any(), any(), any())
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

        coVerify(exactly = 0) { redshiftClient.uploadToS3(any(), any(), any(), any()) }
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
        coVerify { redshiftClient.uploadToS3(any(), any(), capture(dataSlot), any()) }

        // Decompress and verify CSV content
        val csvContent =
            java.util.zip.GZIPInputStream(java.io.ByteArrayInputStream(dataSlot.captured))
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
        coVerify { redshiftClient.uploadToS3(any(), capture(keySlot), any(), any()) }

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
        coVerify { redshiftClient.uploadToS3(any(), capture(keySlot), any(), any()) }

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

        coVerify(exactly = 1) { redshiftClient.uploadToS3(any(), any(), any(), any()) }
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
        coVerify(exactly = 1) { redshiftClient.uploadToS3(any(), any(), any(), any()) }
        coVerify(exactly = 1) { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) }

        assertEquals(0, buffer.recordCount)
    }

    @Test
    fun `upload metadata has correct content type and length`() = runTest {
        buffer.accumulate(
            mapOf("_airbyte_raw_id" to StringValue("x"), "name" to StringValue("y"))
        )
        buffer.flush()

        val metadataSlot = slot<ObjectMetadata>()
        coVerify { redshiftClient.uploadToS3(any(), any(), any(), capture(metadataSlot)) }

        assertEquals("application/gzip", metadataSlot.captured.contentType)
        assertTrue(metadataSlot.captured.contentLength > 0)
    }

    @Test
    fun `buffer can be reused after flush`() = runTest {
        buffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("batch1")))
        buffer.flush()

        buffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("batch2")))
        buffer.flush()

        coVerify(exactly = 2) { redshiftClient.uploadToS3(any(), any(), any(), any()) }
        coVerify(exactly = 2) { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) }
    }

    @Test
    fun `flush propagates exceptions from copyFromS3`() = runTest {
        coEvery { redshiftClient.copyFromS3(any(), any(), any(), any(), any()) } throws
            RuntimeException("COPY failed")

        buffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("x")))

        val exception =
            org.junit.jupiter.api.assertThrows<RuntimeException> { buffer.flush() }
        assertEquals("COPY failed", exception.message)

        // State is reset even after error
        assertEquals(0, buffer.recordCount)
    }

    @Test
    fun `default region used when s3BucketRegion is null`() = runTest {
        val noRegionConfig = s3Config.copy(s3BucketRegion = null)
        val noRegionConfiguration = configuration.copy(uploadingMethod = noRegionConfig)
        val noRegionBuffer =
            RedshiftInsertBuffer(tableName, columns, redshiftClient, noRegionConfiguration)

        noRegionBuffer.accumulate(mapOf("_airbyte_raw_id" to StringValue("x")))
        noRegionBuffer.flush()

        coVerify {
            redshiftClient.copyFromS3(
                tableName = any(),
                s3Path = any(),
                accessKeyId = any(),
                secretAccessKey = any(),
                region = eq("us-east-1"),
            )
        }
    }
}
