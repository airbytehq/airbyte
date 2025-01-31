/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.operation

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.LoadJobConfiguration
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.GcsNameTransformer
import io.airbyte.cdk.integrations.destination.gcs.GcsStorageOperations
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import org.joda.time.DateTime
import org.joda.time.DateTimeZone

private val log = KotlinLogging.logger {}

class BigQueryGcsStorageOperation(
    private val gcsStorageOperations: GcsStorageOperations,
    private val gcsConfig: GcsDestinationConfig,
    private val gcsNameTransformer: GcsNameTransformer,
    private val keepStagingFiles: Boolean,
    bigquery: BigQuery,
    sqlGenerator: BigQuerySqlGenerator,
    destinationHandler: BigQueryDestinationHandler
) :
    BigQueryStorageOperation<SerializableBuffer>(
        bigquery,
        sqlGenerator,
        destinationHandler,
        datasetLocation = gcsConfig.bucketRegion!!
    ) {
    private val connectionId = UUID.randomUUID()
    private val syncDateTime = DateTime.now(DateTimeZone.UTC)
    override fun prepareStage(streamId: StreamId, suffix: String, replace: Boolean) {
        super.prepareStage(streamId, suffix, replace)
        // prepare staging bucket
        // TODO should this also use the suffix?
        log.info { "Creating bucket ${gcsConfig.bucketName}" }
        gcsStorageOperations.createBucketIfNotExists()
    }

    override fun cleanupStage(streamId: StreamId) {
        if (keepStagingFiles) return

        val stagingRootPath = stagingRootPath(streamId)
        log.info { "Cleaning up staging path at $stagingRootPath" }
        gcsStorageOperations.dropBucketObject(stagingRootPath)
    }

    override fun writeToStage(
        streamConfig: StreamConfig,
        suffix: String,
        data: SerializableBuffer
    ) {
        val stagedFileName: String =
            uploadRecordsToStage(streamConfig.id, suffix, data, streamConfig.generationId)
        copyIntoTableFromStage(streamConfig.id, suffix, stagedFileName)
    }

    private fun uploadRecordsToStage(
        streamId: StreamId,
        suffix: String,
        buffer: SerializableBuffer,
        generationId: Long,
    ): String {
        val objectPath: String = stagingFullPath(streamId)
        log.info {
            "Uploading records to for ${streamId.rawNamespace}.${streamId.rawName}$suffix to path $objectPath"
        }
        return gcsStorageOperations.uploadRecordsToBucket(
            buffer,
            streamId.rawNamespace,
            objectPath,
            generationId
        )
    }

    private fun copyIntoTableFromStage(streamId: StreamId, suffix: String, stagedFileName: String) {
        val tableId = tableId(streamId, suffix)
        val stagingPath = stagingFullPath(streamId)
        val fullFilePath = "gs://${gcsConfig.bucketName}/$stagingPath$stagedFileName"
        log.info { "Uploading records from file $fullFilePath to target Table $tableId" }
        val configuration =
            LoadJobConfiguration.builder(tableId, fullFilePath)
                .setFormatOptions(FormatOptions.csv())
                .setSchema(BigQueryRecordFormatter.SCHEMA_V2)
                .setWriteDisposition(JobInfo.WriteDisposition.WRITE_APPEND)
                .setJobTimeoutMs(600000L) // 10 min
                .build()

        val loadJob: Job = this.bigquery.create(JobInfo.of(configuration))
        log.info {
            "[${loadJob.jobId}] Created a new job to upload record(s) to target table $tableId: $loadJob"
        }
        try {
            BigQueryUtils.waitForJobFinish(loadJob)
            log.info {
                "[${loadJob.jobId}] Target table $tableId is successfully appended with staging files"
            }
        } catch (e: BigQueryException) {
            throw RuntimeException(
                String.format(
                    "[%s] Failed to upload staging files to destination table %s",
                    loadJob.jobId,
                    tableId
                ),
                e
            )
        } catch (e: InterruptedException) {
            throw RuntimeException(
                String.format(
                    "[%s] Failed to upload staging files to destination table %s",
                    loadJob.jobId,
                    tableId
                ),
                e
            )
        }
    }

    private fun stagingFullPath(streamId: StreamId): String {
        return gcsNameTransformer.applyDefaultCase(
            String.format(
                "%s%s/%02d/%02d/%02d/%s/",
                stagingRootPath(streamId),
                syncDateTime.year().get(),
                syncDateTime.monthOfYear().get(),
                syncDateTime.dayOfMonth().get(),
                syncDateTime.hourOfDay().get(),
                connectionId
            )
        )
    }

    private fun stagingRootPath(streamId: StreamId): String {
        return gcsNameTransformer.applyDefaultCase(
            String.format(
                "%s/%s_%s/",
                gcsConfig.bucketPath,
                gcsNameTransformer.convertStreamName(streamId.rawNamespace),
                gcsNameTransformer.convertStreamName(streamId.rawName)
            )
        )
    }
}
