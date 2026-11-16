/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.gax.paging.Page
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
import io.mockk.slot
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class BigQueryDatabaseHandlerTest {
    companion object {
        const val BILLING_ERROR =
            """Billing has not been enabled for this project. Enable billing at https://console.cloud.google.com/billing. DML queries are not allowed in the free tier. Set up a billing account to remove this restriction."""
        const val CUSTOM_QUOTA_ERROR =
            """Custom quota exceeded: Your usage exceeded the custom quota for QueryUsagePerDay, which limits the total data processed by queries in a given day."""
    }

    @Test
    fun `execute sets jobProjectId and location on the JobId`() {
        val jobInfoSlot = slot<JobInfo>()
        val queryStats: JobStatistics.QueryStatistics = mockk {
            every { startTime } returns 0L
            every { endTime } returns 100L
            every { totalBytesProcessed } returns 1024L
            every { totalBytesBilled } returns 1024L
            every { numChildJobs } returns null
        }
        val bq: BigQuery = mockk {
            every { create(capture(jobInfoSlot), *anyVararg()) } returns
                mockk {
                    every { status } returns
                        mockk {
                            every { state } returns JobStatus.State.DONE
                            every { error } returns null
                        }
                    every { reload() } returns this
                    every { getStatistics<JobStatistics.QueryStatistics>() } returns queryStats
                }
        }
        val handler = BigQueryDatabaseHandler(bq, bq, "us-east1", "my-job-project")

        handler.execute(Sql.of("SELECT 1"))

        val capturedJobInfo = jobInfoSlot.captured
        assertEquals("my-job-project", capturedJobInfo.jobId.project)
        assertEquals("us-east1", capturedJobInfo.jobId.location)
        assertTrue(capturedJobInfo.jobId.job?.isNotBlank() == true)
    }

    @Test
    fun `execute lists child jobs using the job project client`() {
        val queryStats: JobStatistics.QueryStatistics = mockk {
            every { startTime } returns 0L
            every { endTime } returns 100L
            every { totalBytesProcessed } returns 1024L
            every { totalBytesBilled } returns 1024L
            every { numChildJobs } returns 1L
        }
        val rootJobId = JobId.of("root-job")
        val rootJob: Job = mockk {
            every { jobId } returns rootJobId
            every { status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns null
                }
            every { reload() } returns this
            every { getStatistics<JobStatistics.QueryStatistics>() } returns queryStats
        }
        val datasetProjectBq: BigQuery = mockk()
        val jobProjectBq: BigQuery = mockk()
        val childJobs: Page<Job> = mockk { every { iterateAll() } returns emptyList() }
        every { datasetProjectBq.create(any<JobInfo>(), *anyVararg()) } returns rootJob
        every { jobProjectBq.listJobs(*anyVararg()) } returns childJobs

        val handler =
            BigQueryDatabaseHandler(
                datasetProjectBq,
                jobProjectBq,
                "location",
                "job-project",
            )

        handler.execute(Sql.of("SELECT 1"))

        verify(exactly = 1) { jobProjectBq.listJobs(*anyVararg()) }
        verify(exactly = 0) { datasetProjectBq.listJobs(*anyVararg()) }
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
        val handler = BigQueryDatabaseHandler(bq, bq, "location", "test-project")

        assertThrows<ConfigErrorException> { handler.execute(Sql.of("select * from nowhere")) }
    }

    @Test
    fun `custom quota exceeded errors are wrapped as ConfigErrorException`() {
        val bqError = BigQueryError(CUSTOM_QUOTA_ERROR, "loc", CUSTOM_QUOTA_ERROR)
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()).status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns bqError
                    every { executionErrors } returns listOf(bqError)
                }
        }
        val handler = BigQueryDatabaseHandler(bq, bq, "location", "test-project")

        assertThrows<ConfigErrorException> { handler.execute(Sql.of("select * from nowhere")) }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `access denied job errors are wrapped with remediation`(executionError: Boolean) {
        val message =
            "Access Denied: Table proj:airbyte_internal.tbl: Permission bigquery.tables.delete denied on table proj:airbyte_internal.tbl (or it may not exist)."
        val bqError = BigQueryError("accessDenied", "loc", message)
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()).status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns
                        if (executionError) BigQueryError("invalidQuery", "loc", "Query failed")
                        else bqError
                    every { executionErrors } returns
                        if (executionError) listOf(bqError) else emptyList()
                }
        }
        val handler = BigQueryDatabaseHandler(bq, bq, "location", "test-project")

        val exception =
            assertThrows<ConfigErrorException> { handler.execute(Sql.of("DROP TABLE tbl")) }

        assertEquals(
            "The BigQuery service account is missing a required permission. $message Grant the service account the BigQuery Data Editor role on the dataset named above, then retry the sync.",
            exception.message,
        )
        assertTrue(exception.cause is BigQueryException)
        assertTrue((exception.cause as BigQueryException).errors.contains(bqError))
    }

    @ParameterizedTest
    @ValueSource(strings = ["rateLimitExceeded", "invalidQuery"])
    fun `other job errors remain BigQueryException`(reason: String) {
        val bqError = BigQueryError(reason, "loc", "Query failed")
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()).status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns bqError
                    every { executionErrors } returns emptyList()
                }
        }
        val handler = BigQueryDatabaseHandler(bq, bq, "location", "test-project")

        val exception = assertThrows<BigQueryException> { handler.execute(Sql.of("SELECT 1")) }

        assertEquals(reason, exception.error.reason)
    }

    @Test
    fun `transient quota exceeded errors are not wrapped as ConfigErrorException`() {
        val transientError = "Quota exceeded: too many DML statements outstanding"
        val bqError = BigQueryError(transientError, "loc", transientError)
        val bq: BigQuery = mockk {
            every { create(any(JobInfo::class), *anyVararg()).status } returns
                mockk {
                    every { state } returns JobStatus.State.DONE
                    every { error } returns bqError
                    every { executionErrors } returns listOf(bqError)
                }
        }
        val handler = BigQueryDatabaseHandler(bq, bq, "location", "test-project")

        assertThrows<BigQueryException> { handler.execute(Sql.of("select * from nowhere")) }
    }
}
