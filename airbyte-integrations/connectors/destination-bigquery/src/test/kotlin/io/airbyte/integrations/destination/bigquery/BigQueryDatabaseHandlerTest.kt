/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.gax.paging.Page
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
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
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryDatabaseHandlerTest {
    companion object {
        const val BILLING_ERROR =
            """Billing has not been enabled for this project. Enable billing at https://console.cloud.google.com/billing. DML queries are not allowed in the free tier. Set up a billing account to remove this restriction."""
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
}
