/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class BigqueryBatchStandardInsertsLoaderTest {

    private val oversizedRecord = "record".repeat(3 * 1024 * 1024)
    private val bigquery: BigQuery = mockk()
    private val formatter: RecordFormatter = mockk()
    private val jobId = JobId.newBuilder().setRandomJob().build()
    private val configuration =
        WriteChannelConfiguration.newBuilder(TableId.of("dataset", "table"))
            .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
            .build()

    @ParameterizedTest
    @ValueSource(ints = [403, 404])
    fun `forbidden and not found writer errors remain config errors`(code: Int) {
        val exception = BigQueryException(code, "permission denied")
        every { bigquery.writer(any<JobId>(), any()) } throws exception
        every { formatter.formatRecord(any<DestinationRecordRaw>()) } returns oversizedRecord

        val loader = loader()
        val thrown = assertThrows<ConfigErrorException> { runBlocking { loader.accept(record()) } }

        assertEquals(
            BigqueryBatchStandardInsertsLoaderFactory.CONFIG_ERROR_MSG + exception,
            thrown.message,
        )
        verify(exactly = 1) { bigquery.writer(any<JobId>(), any()) }
    }

    @Test
    fun `retryable writer errors retry and then succeed`() {
        val writer = mockk<TableDataWriteChannel>(relaxed = true)
        every { bigquery.writer(any<JobId>(), any()) } throws
            BigQueryException(503, "backend unavailable") andThenThrows
            BigQueryException(503, "backend unavailable") andThen writer
        every { formatter.formatRecord(any<DestinationRecordRaw>()) } returns oversizedRecord

        val loader = loader(maxOpenAttempts = 5)
        runBlocking { loader.accept(record()) }

        verify(exactly = 3) { bigquery.writer(any<JobId>(), any()) }
    }

    @Test
    fun `writer retries are exhausted as transient error`() {
        val exception = BigQueryException(503, "backend unavailable")
        every { bigquery.writer(any<JobId>(), any()) } throws exception
        every { formatter.formatRecord(any<DestinationRecordRaw>()) } returns oversizedRecord

        val loader = loader(maxOpenAttempts = 4)
        val thrown =
            assertThrows<TransientErrorException> {
                runBlocking { loader.accept(record()) }
            }

        assertEquals(exception, thrown.cause)
        verify(exactly = 4) { bigquery.writer(any<JobId>(), any()) }
    }

    @Test
    fun `non-retryable writer error preserves its cause`() {
        val cause = IllegalStateException("writer failed")
        val exception = BigQueryException(400, "operation failed", cause)
        every { bigquery.writer(any<JobId>(), any()) } throws exception
        every { formatter.formatRecord(any<DestinationRecordRaw>()) } returns oversizedRecord

        val loader = loader()
        val thrown = assertThrows<BigQueryException> { runBlocking { loader.accept(record()) } }

        assertEquals(exception.code, thrown.code)
        assertEquals(exception.message, thrown.message)
        assertEquals(exception, thrown.cause)
        verify(exactly = 1) { bigquery.writer(any<JobId>(), any()) }
    }

    @Test
    fun `interrupted writer error becomes transient error and restores interrupt flag`() {
        Thread.interrupted()
        val interrupted = InterruptedException("thread interrupted")
        val exception =
            BigQueryException(
                500,
                "operation interrupted",
                IllegalStateException("nested cause", interrupted),
            )
        every { bigquery.writer(any<JobId>(), any()) } throws exception
        every { formatter.formatRecord(any<DestinationRecordRaw>()) } returns oversizedRecord

        try {
            val loader = loader()
            val thrown =
                assertThrows<TransientErrorException> { runBlocking { loader.accept(record()) } }

            assertEquals(exception, thrown.cause)
            assertTrue(Thread.currentThread().isInterrupted)
        } finally {
            Thread.interrupted()
        }
    }

    private fun loader(
        maxOpenAttempts: Int = BigqueryBatchStandardInsertsLoader.MAX_OPEN_ATTEMPTS
    ) =
        BigqueryBatchStandardInsertsLoader(
            bigquery,
            configuration,
            jobId,
            formatter,
            sleep = {},
            maxOpenAttempts = maxOpenAttempts,
            jitterMs = { 0 },
        )

    private fun record(): DestinationRecordRaw = mockk()
}
