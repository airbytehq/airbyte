/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.LoadJobConfiguration
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.write.db.BulkLoader
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingSpecification
import io.airbyte.integrations.destination.bigquery.write.TempUtils
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton

class BigQueryBulkLoader(
    private val storageClient: S3Client,
    private val bigQueryClient: BigQuery,
    private val bigQueryConfiguration: BigqueryConfiguration,
    private val stream: DestinationStream,
) : BulkLoader<S3Object> {
    override suspend fun load(remoteObject: S3Object) {
        val rawTableId = TempUtils.rawTableId(bigQueryConfiguration, stream.descriptor)
        val gcsUri = "gs://${remoteObject.keyWithBucketName}"

        val configuration =
            LoadJobConfiguration.builder(rawTableId, gcsUri)
                .setFormatOptions(FormatOptions.csv())
                .setSchema(BigQueryRecordFormatter.SCHEMA_V2)
                .setWriteDisposition(JobInfo.WriteDisposition.WRITE_APPEND)
                .setJobTimeoutMs(600000L) // 10 min timeout
                .build()

        val loadJob = bigQueryClient.create(JobInfo.of(configuration))

        try {
            BigQueryUtils.waitForJobFinish(loadJob)
        } catch (e: Exception) {
            throw RuntimeException(
                "Failed to load CSV data from $gcsUri to table ${rawTableId.dataset}.${rawTableId.table}: ${e.message}",
                e
            )
        }

        val loadingMethodPostProcessing =
            (bigQueryConfiguration.loadingMethod as GcsStagingSpecification).filePostProcessing
        if (loadingMethodPostProcessing == GcsFilePostProcessing.DELETE) {
            storageClient.delete(remoteObject)
        }
    }

    override fun close() {
        /* Do nothing */
    }
}

class BigqueryConfiguredForBulkLoad : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(BigqueryConfiguration::class.java)
        return config.loadingMethod is GcsStagingConfiguration
    }
}

@Singleton
@Requires(condition = BigqueryConfiguredForBulkLoad::class)
class BigQueryBulkLoaderFactory(
    private val catalog: DestinationCatalog,
    private val storageClient: S3Client,
    private val bigQueryClient: BigQuery,
    private val bigQueryConfiguration: BigqueryConfiguration
) : BulkLoaderFactory<StreamKey, S3Object> {
    override val numPartWorkers: Int = 2
    override val numUploadWorkers: Int = 10
    override val maxNumConcurrentLoads: Int = 1

    override val objectSizeBytes: Long = 200 * 1024 * 1024 // 200 MB
    override val partSizeBytes: Long = 10 * 1024 * 1024 // 10 MB
    override val maxMemoryRatioReservedForParts: Double = 0.6

    override fun create(key: StreamKey, partition: Int): BulkLoader<S3Object> {
        val stream = catalog.getStream(key.stream)
        return BigQueryBulkLoader(storageClient, bigQueryClient, bigQueryConfiguration, stream)
    }
}
