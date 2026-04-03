/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatus
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigQueryDatabaseHandlerTest {
    companion object {
        const val BILLING_ERROR =
            """Billing has not been enabled for this project. Enable billing at https://console.cloud.google.com/billing. DML queries are not allowed in the free tier. Set up a billing account to remove this restriction."""
        const val CUSTOM_QUOTA_ERROR =
            """Custom quota exceeded: Your usage exceeded the custom quota for QueryUsagePerDay, which is set by your administrator. For more information, see https://docs.cloud.google.com/bigquery/cost-controls. To update the limit, go to https://docs.cloud.google.com/bigquery/redirects/increase-query-cost-quota."""
        const val QUOTA_EXCEEDED_ERROR =
            """Quota exceeded: Too many DML statements outstanding against table myproject:mydataset.mytable, limit is 20."""
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
        val handler = BigQueryDatabaseHandler(bq, "location")

        assertThrows<ConfigErrorException> { handler.execute(Sql.of("select * from nowhere")) }
    }

    @Test
    fun `quota exceeded errors are wrapped as ConfigErrorException`() {
        val bqError = BigQueryError(QUOTA_EXCEEDED_ERROR, "loc", QUOTA_EXCEEDED_ERROR)
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
}
