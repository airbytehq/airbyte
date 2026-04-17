/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryDatabaseHandlerTest {
    companion object {
        const val BILLING_ERROR =
            """Billing has not been enabled for this project. Enable billing at https://console.cloud.google.com/billing. DML queries are not allowed in the free tier. Set up a billing account to remove this restriction."""

        const val CONCURRENT_UPDATE_ERROR =
            "Transaction is aborted due to concurrent update against table " +
                "prod8b61f23e:vsa_action_network.users. Transaction ID: 69eec352-0000-2e43-afcc-10d9a2134b26."
    }

    @Test
    fun `billing errors are wrapped as ConfigErrorException`() {
        val bqError = BigQueryError(BILLING_ERROR, "loc", BILLING_ERROR)
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()).status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns bqError
                    every { executionErrors } returns listOf(bqError)
                }
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<ConfigErrorException> { handler.execute(Sql.of("select * from nowhere")) }
    }

    @Test
    fun `isConcurrentUpdateError matches by top-level message`() {
        val e = BigQueryException(400, CONCURRENT_UPDATE_ERROR)

        assertTrue(BigQueryDatabaseHandler.isConcurrentUpdateError(e))
    }

    @Test
    fun `isConcurrentUpdateError matches by nested error message`() {
        val bqError = BigQueryError("invalidQuery", "US", CONCURRENT_UPDATE_ERROR)
        val e = BigQueryException(listOf(bqError))

        assertTrue(BigQueryDatabaseHandler.isConcurrentUpdateError(e))
    }

    @Test
    fun `isConcurrentUpdateError does not match unrelated errors`() {
        val unrelated = BigQueryError("invalidQuery", "US", "Syntax error near something")

        assertFalse(BigQueryDatabaseHandler.isConcurrentUpdateError(BigQueryException(400, "boom")))
        assertFalse(BigQueryDatabaseHandler.isConcurrentUpdateError(BigQueryException(listOf(unrelated))))
    }

    @Test
    fun `execute retries on concurrent-update error then succeeds`() {
        val concurrentUpdateError =
            BigQueryError("invalidQuery", "US", CONCURRENT_UPDATE_ERROR)
        val failingJob: Job =
            mockk(relaxed = true) {
                every { status } returns
                    mockk {
                        every { state } returns JobStatus.State.DONE
                        every { error } returns concurrentUpdateError
                        every { executionErrors } returns listOf(concurrentUpdateError)
                    }
                every { reload() } returns this
            }
        val statistics: JobStatistics.QueryStatistics =
            mockk(relaxed = true) {
                every { startTime } returns 0L
                every { endTime } returns 1L
                every { totalBytesProcessed } returns 0L
                every { totalBytesBilled } returns 0L
                every { numChildJobs } returns null
            }
        val successJob: Job =
            mockk(relaxed = true) {
                every { status } returns
                    mockk {
                        every { state } returns JobStatus.State.DONE
                        every { error } returns null
                    }
                every { reload() } returns this
                every { jobId } returns JobId.of("job-success")
                every { getStatistics<JobStatistics.QueryStatistics>() } returns statistics
            }
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } returnsMany
                listOf(failingJob, failingJob, successJob)
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        handler.execute(Sql.of("MERGE target USING source ON target.id = source.id"))

        // Three submission attempts: two aborted, one successful.
        verify(exactly = 3) { bq.create(any(JobInfo::class), *anyVararg()) }
    }

    @Test
    fun `execute rethrows concurrent-update error after exhausting retries`() {
        val concurrentUpdateError =
            BigQueryError("invalidQuery", "US", CONCURRENT_UPDATE_ERROR)
        val failingJob: Job =
            mockk(relaxed = true) {
                every { status } returns
                    mockk {
                        every { state } returns JobStatus.State.DONE
                        every { error } returns concurrentUpdateError
                        every { executionErrors } returns listOf(concurrentUpdateError)
                    }
                every { reload() } returns this
            }
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } returns failingJob
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        val thrown =
            assertThrows<BigQueryException> {
                handler.execute(Sql.of("MERGE target USING source ON target.id = source.id"))
            }
        assertTrue(
            thrown.message?.contains("Transaction is aborted due to concurrent update") == true,
            "Expected the concurrent-update error to propagate, got: ${thrown.message}",
        )
        // Five total submission attempts, matching CONCURRENT_UPDATE_MAX_ATTEMPTS.
        verify(exactly = 5) { bq.create(any(JobInfo::class), *anyVararg()) }
    }

    @Test
    fun `execute does not retry on non-concurrent-update errors`() {
        val otherError = BigQueryError("invalidQuery", "US", "Syntax error near something")
        val failingJob: Job =
            mockk(relaxed = true) {
                every { status } returns
                    mockk {
                        every { state } returns JobStatus.State.DONE
                        every { error } returns otherError
                        every { executionErrors } returns listOf(otherError)
                    }
                every { reload() } returns this
            }
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } returns failingJob
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<BigQueryException> { handler.execute(Sql.of("select * from nowhere")) }
        verify(exactly = 1) { bq.create(any(JobInfo::class), *anyVararg()) }
    }
}
