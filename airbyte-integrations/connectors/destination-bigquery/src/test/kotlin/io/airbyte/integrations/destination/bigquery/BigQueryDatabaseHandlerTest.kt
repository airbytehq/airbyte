/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatus
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryDatabaseHandlerTest {
    companion object {
        const val BILLING_ERROR =
            """Billing has not been enabled for this project. Enable billing at https://console.cloud.google.com/billing. DML queries are not allowed in the free tier. Set up a billing account to remove this restriction."""
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
    fun `InterruptedException wrapped in BigQueryException from create is caught and rethrown with message`() {
        val interruptedException = InterruptedException("thread was interrupted")
        val bigQueryException = BigQueryException(0, "interrupted", interruptedException)
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } throws bigQueryException
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        val thrown =
            assertThrows<RuntimeException> { handler.execute(Sql.of("select * from nowhere")) }
        assertEquals(BigQueryUtils.INTERRUPTED_ERROR_MESSAGE, thrown.message)
        assertTrue(thrown.cause is BigQueryException)
        assertTrue(thrown.cause?.cause is InterruptedException)
    }

    @Test
    fun `InterruptedException during job polling is caught and rethrown with message`() {
        val job: Job = mockk {
            every { status } returns
                mockk {
                    // Return RUNNING so the loop calls Thread.sleep, then interrupt the thread
                    every { state } returns JobStatus.State.RUNNING
                }
        }
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } returns job
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        // Interrupt the current thread before execute() enters the polling loop.
        // Thread.sleep will immediately throw InterruptedException.
        Thread.currentThread().interrupt()
        val thrown =
            assertThrows<RuntimeException> { handler.execute(Sql.of("select * from nowhere")) }
        assertEquals(BigQueryUtils.INTERRUPTED_ERROR_MESSAGE, thrown.message)
        assertTrue(thrown.cause is InterruptedException)
    }

    @Test
    fun `non-interrupt BigQueryException from create is rethrown as-is`() {
        val bigQueryException = BigQueryException(500, "server error")
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } throws bigQueryException
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        val thrown =
            assertThrows<BigQueryException> { handler.execute(Sql.of("select * from nowhere")) }
        assertEquals("server error", thrown.message)
    }
}
