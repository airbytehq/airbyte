/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryDatabaseHandlerTest {
    companion object {
        const val BILLING_ERROR =
            """Billing has not been enabled for this project. Enable billing at https://console.cloud.google.com/billing. DML queries are not allowed in the free tier. Set up a billing account to remove this restriction."""
        const val TRANSIENT_TIMEOUT_MESSAGE = "Request timed out. Please try again."
        const val CONCURRENT_UPDATE_MESSAGE =
            "Transaction is aborted due to concurrent update against table proj:ds.tbl. Transaction ID: ABC. Blocking job: XYZ"
        const val SYNTAX_ERROR_MESSAGE = "Syntax error: Unexpected keyword SELECT at [1:1]"
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

    // region: helper-function unit tests

    @Test
    fun `isTransientError matches request-timeout message`() {
        val err = BigQueryError(TRANSIENT_TIMEOUT_MESSAGE, "loc", TRANSIENT_TIMEOUT_MESSAGE)
        assertTrue(BigQueryDatabaseHandler.isTransientError(listOf(err)))
    }

    @Test
    fun `isTransientError matches concurrent-update message`() {
        val err = BigQueryError(CONCURRENT_UPDATE_MESSAGE, "loc", CONCURRENT_UPDATE_MESSAGE)
        assertTrue(BigQueryDatabaseHandler.isTransientError(listOf(err)))
    }

    @Test
    fun `isTransientError does not match syntax error`() {
        val err = BigQueryError(SYNTAX_ERROR_MESSAGE, "loc", SYNTAX_ERROR_MESSAGE)
        assertFalse(BigQueryDatabaseHandler.isTransientError(listOf(err)))
    }

    @Test
    fun `isTransientException classifies isRetryable as transient`() {
        val e = mockk<BigQueryException>()
        every { e.isRetryable } returns true
        every { e.code } returns 503
        every { e.message } returns null
        every { e.errors } returns emptyList()
        assertTrue(BigQueryDatabaseHandler.isTransientException(e))
    }

    @Test
    fun `isTransientException classifies message-based timeout as transient`() {
        val e = mockk<BigQueryException>()
        every { e.isRetryable } returns false
        every { e.code } returns 0
        every { e.message } returns TRANSIENT_TIMEOUT_MESSAGE
        every { e.errors } returns emptyList()
        assertTrue(BigQueryDatabaseHandler.isTransientException(e))
    }

    @Test
    fun `isTransientException classifies 5xx as transient`() {
        val e = mockk<BigQueryException>()
        every { e.isRetryable } returns false
        every { e.code } returns 503
        every { e.message } returns "Service unavailable"
        every { e.errors } returns emptyList()
        assertTrue(BigQueryDatabaseHandler.isTransientException(e))
    }

    @Test
    fun `isTransientException does not classify syntax error as transient`() {
        val e = mockk<BigQueryException>()
        every { e.isRetryable } returns false
        every { e.code } returns 400
        every { e.message } returns SYNTAX_ERROR_MESSAGE
        every { e.errors } returns
            listOf(BigQueryError(SYNTAX_ERROR_MESSAGE, "loc", SYNTAX_ERROR_MESSAGE))
        assertFalse(BigQueryDatabaseHandler.isTransientException(e))
    }

    // endregion

    // region: end-to-end retry behavior through execute(sql)

    @Test
    fun `execute retries when job status reports transient timeout and succeeds on retry`() {
        val transientError =
            BigQueryError(TRANSIENT_TIMEOUT_MESSAGE, "loc", TRANSIENT_TIMEOUT_MESSAGE)

        // First two attempts return a DONE job with a transient timeout error; 3rd returns clean.
        val failingJob: Job = mockk {
            every { status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns transientError
                    every { executionErrors } returns listOf(transientError)
                }
        }
        val successfulJob: Job = mockk {
            every { status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns null
                    every { executionErrors } returns emptyList()
                }
            every { getStatistics<JobStatistics.QueryStatistics>() } returns
                mockk {
                    every { endTime } returns 2L
                    every { startTime } returns 1L
                    every { totalBytesProcessed } returns 0L
                    every { totalBytesBilled } returns 0L
                    every { numChildJobs } returns null
                }
            every { jobId } returns mockk { every { job } returns "successful-job" }
        }
        val bq: BigQuery = mockk()
        every { bq.create(any(JobInfo::class), *anyVararg()) } returnsMany
            listOf(failingJob, failingJob, successfulJob)

        val handler = BigQueryDatabaseHandler(bq, "location")
        handler.execute(Sql.of("merge into foo using bar on foo.id = bar.id"))

        verify(exactly = 3) { bq.create(any(JobInfo::class), *anyVararg()) }
    }

    @Test
    fun `execute retries when BigQuery create throws transient exception then succeeds`() {
        val transientException = mockk<BigQueryException>()
        every { transientException.isRetryable } returns true
        every { transientException.code } returns 503
        every { transientException.message } returns "Service unavailable"
        every { transientException.errors } returns emptyList()
        every { transientException.reason } returns null

        val successfulJob: Job = mockk {
            every { status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns null
                    every { executionErrors } returns emptyList()
                }
            every { getStatistics<JobStatistics.QueryStatistics>() } returns
                mockk {
                    every { endTime } returns 2L
                    every { startTime } returns 1L
                    every { totalBytesProcessed } returns 0L
                    every { totalBytesBilled } returns 0L
                    every { numChildJobs } returns null
                }
            every { jobId } returns mockk { every { job } returns "successful-job" }
        }

        val bq: BigQuery = mockk()
        every { bq.create(any(JobInfo::class), *anyVararg()) } throws
            transientException andThen
            successfulJob

        val handler = BigQueryDatabaseHandler(bq, "location")
        handler.execute(Sql.of("select 1"))

        verify(exactly = 2) { bq.create(any(JobInfo::class), *anyVararg()) }
    }

    @Test
    fun `execute fails fast on non-transient job-status error without retrying`() {
        val syntaxError = BigQueryError(SYNTAX_ERROR_MESSAGE, "loc", SYNTAX_ERROR_MESSAGE)
        val failingJob: Job = mockk {
            every { status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns syntaxError
                    every { executionErrors } returns listOf(syntaxError)
                }
        }
        val bq: BigQuery = mockk()
        every { bq.create(any(JobInfo::class), *anyVararg()) } returns failingJob

        val handler = BigQueryDatabaseHandler(bq, "location")
        val thrown =
            assertThrows<BigQueryException> { handler.execute(Sql.of("select invalid syntax")) }

        assertTrue(
            thrown.message!!.contains("Syntax error") ||
                thrown.errors.any { it.message.contains("Syntax error") },
            "Expected a syntax-error BigQueryException; got ${thrown.message}"
        )
        verify(exactly = 1) { bq.create(any(JobInfo::class), *anyVararg()) }
    }

    @Test
    fun `execute throws after exhausting all transient-retry attempts`() {
        val transientError =
            BigQueryError(CONCURRENT_UPDATE_MESSAGE, "loc", CONCURRENT_UPDATE_MESSAGE)
        val failingJob: Job = mockk {
            every { status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns transientError
                    every { executionErrors } returns listOf(transientError)
                }
        }
        val bq: BigQuery = mockk()
        every { bq.create(any(JobInfo::class), *anyVararg()) } returns failingJob

        val handler = BigQueryDatabaseHandler(bq, "location")
        val thrown =
            assertThrows<BigQueryException> { handler.execute(Sql.of("merge into foo ...")) }

        assertTrue(
            thrown.errors.any { it.message.contains("Transaction is aborted") },
            "Expected final exception to preserve the transient concurrent-update error"
        )
        assertEquals(
            BigQueryDatabaseHandler.TRANSIENT_RETRY_MAX_ATTEMPTS,
            5,
            "Playbook specifies 5 max attempts"
        )
        verify(exactly = BigQueryDatabaseHandler.TRANSIENT_RETRY_MAX_ATTEMPTS) {
            bq.create(any(JobInfo::class), *anyVararg())
        }
    }

    // endregion
}
