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
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
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
    fun `403 access denied from job reload is wrapped as ConfigErrorException`() {
        val accessDeniedError =
            BigQueryError("accessDenied", "loc", "Access Denied: Table delete permission denied")
        val job: Job = mockk {
            every { status } returns mockk { every { state } returns JobStatus.State.RUNNING }
            every { reload() } throws
                BigQueryException(
                    403,
                    "Access Denied: Table delete permission denied",
                    accessDeniedError
                )
        }
        val bq: BigQuery = mockk { every { create(any(JobInfo::class), *anyVararg()) } returns job }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<ConfigErrorException> { handler.execute(Sql.of("DELETE FROM table")) }
    }

    @Test
    fun `403 access denied errors are wrapped as ConfigErrorException in executeWithRetries`() {
        val accessDeniedError =
            BigQueryError("accessDenied", "loc", "Access Denied: bigquery.tables.delete denied")
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } throws
                BigQueryException(
                    403,
                    "Access Denied: bigquery.tables.delete denied",
                    accessDeniedError
                )
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<ConfigErrorException> {
            runBlocking { handler.executeWithRetries("DELETE FROM table", numAttempts = 1) }
        }
    }

    @Test
    fun `401 unauthorized errors are wrapped as ConfigErrorException`() {
        val authError = BigQueryError("unauthorized", "loc", "Invalid credentials")
        val job: Job = mockk {
            every { status } returns mockk { every { state } returns JobStatus.State.RUNNING }
            every { reload() } throws BigQueryException(401, "Invalid credentials", authError)
        }
        val bq: BigQuery = mockk { every { create(any(JobInfo::class), *anyVararg()) } returns job }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<ConfigErrorException> { handler.execute(Sql.of("SELECT 1")) }
    }

    @Test
    fun `403 rate limit errors are retried and not wrapped as ConfigErrorException`() {
        val rateLimitError = BigQueryError("rateLimitExceeded", "loc", "Rate limit exceeded")
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } throws
                BigQueryException(403, "Rate limit exceeded", rateLimitError)
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertDoesNotThrow {
            runBlocking {
                handler.executeWithRetries(
                    "SELECT 1",
                    initialDelay = 1,
                    numAttempts = 1,
                    maxDelay = 1
                )
            }
        }
    }

    @Test
    fun `500 internal errors are not wrapped as ConfigErrorException`() {
        val internalError = BigQueryError("internalError", "loc", "Internal error")
        val job: Job = mockk {
            every { status } returns mockk { every { state } returns JobStatus.State.RUNNING }
            every { reload() } throws BigQueryException(500, "Internal error", internalError)
        }
        val bq: BigQuery = mockk { every { create(any(JobInfo::class), *anyVararg()) } returns job }
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<BigQueryException> { handler.execute(Sql.of("SELECT 1")) }
    }
}
