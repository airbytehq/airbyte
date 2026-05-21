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
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler.Companion.INTERRUPTED_FINAL_TABLE_UPDATE_MESSAGE
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertTrue
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
    fun `interrupted job reload is wrapped as transient error`() {
        val status: JobStatus = mockk { every { state } returns JobStatus.State.RUNNING }
        val job: Job = mockk {
            every { this@mockk.status } returns status
            every { reload() } throws
                BigQueryException(0, "java.lang.InterruptedException", InterruptedException())
        }
        val bq: BigQuery = mockk { every { create(any(JobInfo::class), *anyVararg()) } returns job }
        val handler = BigQueryDatabaseHandler(bq, "location")

        try {
            val e =
                assertThrows<TransientErrorException> {
                    handler.execute(Sql.of("select * from nowhere"))
                }

            assertEquals(INTERRUPTED_FINAL_TABLE_UPDATE_MESSAGE, e.message)
            assertTrue(Thread.currentThread().isInterrupted)
        } finally {
            Thread.interrupted()
        }
    }

    @Test
    fun `interrupted job creation is wrapped as transient error`() {
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()) } throws
                BigQueryException(0, "java.lang.InterruptedException", InterruptedException())
        }
        val handler = BigQueryDatabaseHandler(bq, "location")

        try {
            val e =
                assertThrows<TransientErrorException> {
                    handler.execute(Sql.of("select * from nowhere"))
                }

            assertEquals(INTERRUPTED_FINAL_TABLE_UPDATE_MESSAGE, e.message)
            assertTrue(Thread.currentThread().isInterrupted)
        } finally {
            Thread.interrupted()
        }
    }
}
