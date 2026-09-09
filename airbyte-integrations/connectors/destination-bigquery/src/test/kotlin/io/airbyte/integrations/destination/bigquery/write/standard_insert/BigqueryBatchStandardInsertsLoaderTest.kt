/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class BigqueryBatchStandardInsertsLoaderTest {
    private val jobId = JobId.of("test-project", "test-job")
    private val writeChannelConfiguration =
        WriteChannelConfiguration.newBuilder(TableId.of("project", "dataset", "table")).build()
    private val recordFormatter = RecordFormatter { "{\"id\":1}" }

    private fun successfulJob(): Job {
        val stats = mockk<JobStatistics.LoadStatistics>()
        every { stats.outputRows } returns 1L
        every { stats.badRecords } returns 0L
        val status = mockk<JobStatus>()
        every { status.error } returns null
        every { status.state } returns JobStatus.State.DONE
        val job = mockk<Job>(relaxed = true)
        every { job.jobId } returns jobId
        every { job.status } returns status
        every { job.waitFor(*anyVararg()) } returns job
        every { job.reload(*anyVararg()) } returns job
        every { job.getStatistics<JobStatistics.LoadStatistics>() } returns stats
        return job
    }

    private fun writerThatFailsOnClose(code: Int): TableDataWriteChannel {
        val writer = mockk<TableDataWriteChannel>()
        every { writer.write(any<ByteBuffer>()) } answers { firstArg<ByteBuffer>().remaining() }
        every { writer.close() } throws BigQueryException(code, "boom")
        return writer
    }

    private fun successfulWriter(job: Job, captured: StringBuilder): TableDataWriteChannel {
        val writer = mockk<TableDataWriteChannel>()
        every { writer.write(any<ByteBuffer>()) } answers
            {
                val buf = firstArg<ByteBuffer>()
                val bytes = ByteArray(buf.remaining())
                buf.get(bytes)
                captured.append(String(bytes, StandardCharsets.UTF_8))
                bytes.size
            }
        every { writer.close() } returns Unit
        every { writer.job } returns job
        return writer
    }

    private fun loader(bigquery: BigQuery) =
        BigqueryBatchStandardInsertsLoader(
            bigquery,
            writeChannelConfiguration,
            jobId,
            recordFormatter,
            maxUploadAttempts = 3,
            initialRetryDelayMs = 1,
            maxRetryDelayMs = 1,
        )

    @Test
    fun `retries the whole batch after a transient 500 on upload`() = runBlocking {
        val job = successfulJob()
        val uploaded = StringBuilder()
        val bigquery = mockk<BigQuery>()
        every { bigquery.writer(jobId, writeChannelConfiguration) } returnsMany
            listOf(writerThatFailsOnClose(500), successfulWriter(job, uploaded))
        every { bigquery.getJob(jobId) } returns null

        val loader = loader(bigquery)
        loader.accept(mockk<DestinationRecordRaw>())
        loader.accept(mockk<DestinationRecordRaw>())
        loader.finish()

        verify(exactly = 2) { bigquery.writer(jobId, writeChannelConfiguration) }
        assertEquals(
            "{\"id\":1}${System.lineSeparator()}{\"id\":1}${System.lineSeparator()}",
            uploaded.toString(),
        )
    }

    @Test
    fun `reuses the existing load job instead of re-uploading`() = runBlocking {
        val job = successfulJob()
        val bigquery = mockk<BigQuery>()
        every { bigquery.writer(jobId, writeChannelConfiguration) } returns
            writerThatFailsOnClose(503)
        every { bigquery.getJob(jobId) } returns job

        val loader = loader(bigquery)
        loader.accept(mockk<DestinationRecordRaw>())
        loader.finish()

        verify(exactly = 1) { bigquery.writer(jobId, writeChannelConfiguration) }
    }

    @Test
    fun `gives up with a transient error after exhausting attempts`() = runBlocking {
        val bigquery = mockk<BigQuery>()
        every { bigquery.writer(jobId, writeChannelConfiguration) } returns
            writerThatFailsOnClose(500)
        every { bigquery.getJob(jobId) } returns null

        val loader = loader(bigquery)
        loader.accept(mockk<DestinationRecordRaw>())
        assertThrows(TransientErrorException::class.java) { runBlocking { loader.finish() } }

        verify(exactly = 3) { bigquery.writer(jobId, writeChannelConfiguration) }
    }

    @Test
    fun `does not retry non-transient errors`() = runBlocking {
        val bigquery = mockk<BigQuery>()
        every { bigquery.writer(jobId, writeChannelConfiguration) } returns
            writerThatFailsOnClose(400)

        val loader = loader(bigquery)
        loader.accept(mockk<DestinationRecordRaw>())
        val e = assertThrows(BigQueryException::class.java) { runBlocking { loader.finish() } }
        assertEquals(400, e.code)

        verify(exactly = 1) { bigquery.writer(jobId, writeChannelConfiguration) }
    }

    @Test
    fun `maps 403 on writer creation to a config error`() = runBlocking {
        val bigquery = mockk<BigQuery>()
        every { bigquery.writer(jobId, writeChannelConfiguration) } throws
            BigQueryException(403, "forbidden")

        val loader = loader(bigquery)
        loader.accept(mockk<DestinationRecordRaw>())
        assertThrows(ConfigErrorException::class.java) { runBlocking { loader.finish() } }
    }
}
