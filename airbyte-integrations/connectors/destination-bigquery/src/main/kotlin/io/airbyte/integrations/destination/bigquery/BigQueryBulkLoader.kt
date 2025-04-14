/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.write.db.BulkLoader
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.write.TempUtils
import jakarta.inject.Singleton

class BigQueryBulkLoader(
    private val bigQueryClient: BigQuery,
    private val bigQueryConfiguration: BigqueryConfiguration,
    private val stream: DestinationStream,
) : BulkLoader<S3Object> {
    override suspend fun load(remoteObject: S3Object) {
        val rawTableId = TempUtils.rawTableId(bigQueryConfiguration, stream.descriptor)

        // Create a temporary external table pointing to the JSONL file
        val createExternalTableSql =
            """
            CREATE OR REPLACE EXTERNAL TABLE `${rawTableId.dataset}.temp_external_table`
            OPTIONS (
              format = 'NEWLINE_DELIMITED_JSON',
              uris = ['gs://${remoteObject.keyWithBucketName}']
            )
            """.trimIndent()

        // Execute the external table creation
        val createTableJob =
            bigQueryClient
                .create(
                    JobInfo.newBuilder(
                            QueryJobConfiguration.newBuilder(createExternalTableSql)
                                .setUseLegacySql(false)
                                .build()
                        )
                        .build()
                )
                .waitFor()

        if (createTableJob.status.error != null) {
            throw RuntimeException(
                "Failed to create external table: ${createTableJob.status.error}"
            )
        }

        // Insert data from external table to destination table
        val insertSql =
            """
            INSERT INTO `${rawTableId.dataset}.${rawTableId.table}`
            SELECT * FROM `${rawTableId.dataset}.temp_external_table`
            """.trimIndent()

        val insertJob =
            bigQueryClient
                .create(
                    JobInfo.newBuilder(
                            QueryJobConfiguration.newBuilder(insertSql)
                                .setUseLegacySql(false)
                                .build()
                        )
                        .build()
                )
                .waitFor()

        if (insertJob.status.error != null) {
            throw RuntimeException("Failed to insert data: ${insertJob.status.error}")
        }

        // Drop the temporary table
        val dropTableSql =
            """
            DROP TABLE `${rawTableId.dataset}.temp_external_table`
            """.trimIndent()

        val dropTableJob =
            bigQueryClient
                .create(
                    JobInfo.newBuilder(
                            QueryJobConfiguration.newBuilder(dropTableSql)
                                .setUseLegacySql(false)
                                .build()
                        )
                        .build()
                )
                .waitFor()

        if (dropTableJob.status.error != null) {
            throw RuntimeException("Failed to drop temporary table: ${dropTableJob.status.error}")
        }
    }

    override fun close() {
        /* Do nothing */
    }
}

@Singleton
class BigQueryBulkLoaderFactory(
    private val catalog: DestinationCatalog,
    private val bigQueryClient: BigQuery,
    private val bigQueryConfiguration: BigqueryConfiguration
) : BulkLoaderFactory<StreamKey, S3Object> {
    override val maxNumConcurrentLoads: Int = 1
    override fun create(key: StreamKey, partition: Int): BulkLoader<S3Object> {
        val stream = catalog.getStream(key.stream)
        return BigQueryBulkLoader(bigQueryClient, bigQueryConfiguration, stream)
    }
}
