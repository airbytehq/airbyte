/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.google.cloud.RetryOption
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.LoadJobConfiguration
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

class BigQueryBulkLoaderTest {
    @Test
    fun `allows nullable fields to be added during append load jobs`() = runBlocking {
        var configuration: LoadJobConfiguration? = null
        val bigQueryClient =
            mockk<BigQuery> {
                every {
                    create(
                        match<JobInfo> { jobInfo ->
                            configuration = jobInfo.getConfiguration<LoadJobConfiguration>()
                            true
                        },
                        *anyVararg()
                    )
                } returns job()
            }
        val storageClient = mockk<GcsClient>(relaxed = true)
        val schema =
            Schema.of(com.google.cloud.bigquery.Field.of("new_field", StandardSQLTypeName.STRING))
        val tableId = TableId.of("dataset", "table")
        val storageConfig =
            GcsClientConfiguration(
                "bucket",
                "path",
                GcsHmacKeyConfiguration("access-key", "secret-key"),
                "US"
            )
        val loader =
            BigQueryBulkLoader(
                storageClient,
                bigQueryClient,
                bigqueryConfiguration(),
                tableId,
                schema
            )

        loader.load(GcsBlob("staged.csv", storageConfig))

        assertEquals(JobInfo.WriteDisposition.WRITE_APPEND, configuration!!.writeDisposition)
        assertSame(schema, configuration!!.schema)
        assertEquals(
            listOf(JobInfo.SchemaUpdateOption.ALLOW_FIELD_ADDITION),
            configuration!!.schemaUpdateOptions
        )
    }

    private fun bigqueryConfiguration(): BigqueryConfiguration {
        val gcsConfig =
            GcsClientConfiguration(
                "bucket",
                "path",
                GcsHmacKeyConfiguration("access-key", "secret-key"),
                "US"
            )
        return BigqueryConfiguration(
            projectId = "project",
            datasetLocation = BigqueryRegion.US,
            datasetId = "dataset",
            loadingMethod = GcsStagingConfiguration(gcsConfig, GcsFilePostProcessing.KEEP),
            credentialsJson = null,
            cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            internalTableDataset = "airbyte_internal",
            legacyRawTablesOnly = false
        )
    }

    private fun job(): Job {
        val stats =
            mockk<JobStatistics.LoadStatistics> {
                every { outputRows } returns 1L
                every { badRecords } returns 0
            }
        return mockk {
            every { jobId } returns JobId.of("project", "job")
            every { status } returns mockk { every { error } returns null }
            every { waitFor(any<RetryOption>()) } returns this
            every { reload().getStatistics<JobStatistics.LoadStatistics>() } returns stats
        }
    }
}
