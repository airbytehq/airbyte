/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.formatter.ProtoToBigQueryStandardInsertRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.toPrettyString
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoaderFactory.Companion.CONFIG_ERROR_MSG
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoaderFactory.Companion.HTTP_STATUS_CODE_FORBIDDEN
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoaderFactory.Companion.HTTP_STATUS_CODE_NOT_FOUND
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.BufferedOutputStream
import java.io.OutputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import kotlin.math.min
import kotlinx.coroutines.delay

private val logger = KotlinLogging.logger {}

interface RecordFormatter {
    fun formatRecord(record: DestinationRecordRaw): String
}

class BigqueryBatchStandardInsertsLoader(
    private val bigquery: BigQuery,
    private val writeChannelConfiguration: WriteChannelConfiguration,
    private val job: JobId,
    private val recordFormatter: RecordFormatter,
    private val maxUploadAttempts: Int = DEFAULT_MAX_UPLOAD_ATTEMPTS,
    private val initialRetryDelayMs: Long = DEFAULT_INITIAL_RETRY_DELAY_MS,
    private val maxRetryDelayMs: Long = DEFAULT_MAX_RETRY_DELAY_MS,
) : DirectLoader {
    // Records are spilled to a local file rather than streamed straight into a
    // TableDataWriteChannel, so that the whole batch can be re-uploaded if BigQuery's resumable
    // upload endpoint returns a transient error partway through.
    // bigquery sets daily limits on how many load jobs you can run, so we upload one file per
    // batch instead of flushing a TableDataWriteChannel every few MB.
    private val spillFile: Path = Files.createTempFile("bigquery-standard-inserts-", ".jsonl")
    private val spillOutput: OutputStream =
        BufferedOutputStream(Files.newOutputStream(spillFile), SPILL_BUFFER_SIZE_BYTES)

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val formattedRecord = recordFormatter.formatRecord(record)
        val byteArray =
            "$formattedRecord${System.lineSeparator()}".toByteArray(StandardCharsets.UTF_8)
        spillOutput.write(byteArray)

        // rely on the CDK to tell us when to finish()
        return DirectLoader.Incomplete
    }

    override suspend fun finish() {
        spillOutput.close()
        val loadJob =
            try {
                uploadWithRetries()
            } finally {
                Files.deleteIfExists(spillFile)
            }
        BigQueryUtils.waitForJobFinish(loadJob)
        val stats = loadJob.reload().getStatistics<JobStatistics.LoadStatistics>()
        logger.info {
            "Finished loading data into table ${writeChannelConfiguration.destinationTable.toPrettyString()}. ${stats.outputRows} rows loaded; ${stats.badRecords} bad records."
        }
        if (stats.badRecords > 0) {
            // This should be impossible: the load job uses the default setting of maxBadRecords=0,
            // so the job is supposed to fail if there were any bad records.
            throw RuntimeException(
                "${writeChannelConfiguration.destinationTable.toPrettyString()}: Nonzero bad records detected: ${stats.badRecords}"
            )
        }
    }

    override fun close() {
        spillOutput.close()
        Files.deleteIfExists(spillFile)
    }

    /**
     * Uploads the spill file to BigQuery as a single load job, retrying on transient errors from
     * the resumable upload endpoint.
     *
     * Every attempt reuses the same [JobId]. BigQuery job IDs are unique per project, so if a
     * previous attempt's upload actually completed (and the load job was created) we detect that via
     * [BigQuery.getJob] and wait for that job instead of re-submitting the data, which avoids
     * duplicate loads.
     */
    private suspend fun uploadWithRetries(): Job {
        var retryDelayMs = initialRetryDelayMs
        var lastException: BigQueryException? = null
        for (attempt in 1..maxUploadAttempts) {
            if (attempt > 1) {
                val existingJob = bigquery.getJob(job)
                if (existingJob != null) {
                    logger.info {
                        "Load job ${job.job} already exists after a failed upload attempt; waiting for it instead of re-uploading."
                    }
                    return existingJob
                }
            }
            try {
                return uploadOnce()
            } catch (e: BigQueryException) {
                if (!isRetryableUploadError(e)) {
                    throw e
                }
                lastException = e
                logger.warn(e) {
                    "Transient BigQuery error (HTTP ${e.code}) while uploading batch to ${writeChannelConfiguration.destinationTable.toPrettyString()} (attempt $attempt/$maxUploadAttempts). Sleeping ${retryDelayMs}ms and retrying."
                }
                if (attempt < maxUploadAttempts) {
                    val withJitter = retryDelayMs + (1000 * Math.random()).toLong()
                    delay(withJitter)
                    retryDelayMs = min(retryDelayMs * 2, maxRetryDelayMs)
                }
            }
        }
        throw TransientErrorException(
            "BigQuery batch upload failed with HTTP ${lastException!!.code} after $maxUploadAttempts attempts.",
            lastException,
        )
    }

    private fun uploadOnce(): Job {
        val writer: TableDataWriteChannel =
            try {
                bigquery.writer(job, writeChannelConfiguration)
            } catch (e: BigQueryException) {
                if (e.code == HTTP_STATUS_CODE_FORBIDDEN || e.code == HTTP_STATUS_CODE_NOT_FOUND) {
                    throw ConfigErrorException(CONFIG_ERROR_MSG + e)
                } else {
                    throw e
                }
            }
        Files.newInputStream(spillFile).use { input ->
            val chunk = ByteArray(UPLOAD_CHUNK_SIZE_BYTES)
            while (true) {
                val read = input.read(chunk)
                if (read < 0) break
                writer.write(ByteBuffer.wrap(chunk, 0, read))
            }
        }
        writer.close()
        return writer.job
    }

    companion object {
        const val DEFAULT_MAX_UPLOAD_ATTEMPTS = 5
        const val DEFAULT_INITIAL_RETRY_DELAY_MS = 5_000L
        const val DEFAULT_MAX_RETRY_DELAY_MS = 60_000L
        private const val SPILL_BUFFER_SIZE_BYTES = 1024 * 1024
        private const val UPLOAD_CHUNK_SIZE_BYTES = 1024 * 1024
        private const val HTTP_STATUS_CODE_TOO_MANY_REQUESTS = 429

        fun isRetryableUploadError(e: BigQueryException): Boolean =
            e.code >= 500 || e.code == HTTP_STATUS_CODE_TOO_MANY_REQUESTS || e.isRetryable
    }
}

class BigqueryConfiguredForBatchStandardInserts : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(BigqueryConfiguration::class.java)
        return config.loadingMethod is BatchedStandardInsertConfiguration
    }
}

@Requires(condition = BigqueryConfiguredForBatchStandardInserts::class)
@Singleton
class BigqueryBatchStandardInsertsLoaderFactory(
    private val catalog: DestinationCatalog,
    @Named("jobProjectBigquery") private val jobProjectBigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val tableCatalog: TableCatalogByDescriptor,
    private val typingDedupingStreamStateStore: StreamStateStore<TypingDedupingExecutionConfig>?,
    private val directLoadStreamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>?,
    @Named("dataChannelFormat") private val dataChannelFormat: DataChannelFormat
) : DirectLoaderFactory<BigqueryBatchStandardInsertsLoader> {
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int,
    ): BigqueryBatchStandardInsertsLoader {
        val tableId: TableId
        val schema: Schema
        val tableNameInfo = tableCatalog[streamDescriptor]!!
        if (config.legacyRawTablesOnly) {
            val rawTableName = tableNameInfo.tableNames.rawTableName!!
            // Wait for the state store to be populated by the coordinating StreamLoader
            val rawTableSuffix =
                waitForStateStore(typingDedupingStreamStateStore!!, streamDescriptor).rawTableSuffix
            tableId =
                TableId.of(
                    config.projectId,
                    rawTableName.namespace,
                    rawTableName.name + rawTableSuffix,
                )
            schema = BigQueryRecordFormatter.SCHEMA_V2
        } else {
            // Wait for the state store to be populated by the coordinating StreamLoader
            val executionConfig = waitForStateStore(directLoadStreamStateStore!!, streamDescriptor)
            tableId =
                TableId.of(
                    config.projectId,
                    executionConfig.tableName.namespace,
                    executionConfig.tableName.name,
                )
            schema =
                BigQueryRecordFormatter.getDirectLoadSchema(
                    catalog.getStream(streamDescriptor),
                    tableNameInfo.columnNameMapping,
                )
        }
        val writeChannelConfiguration =
            WriteChannelConfiguration.newBuilder(tableId)
                .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                .setSchema(schema)
                // new-line delimited json.
                .setFormatOptions(FormatOptions.json())
                .build()

        val jobId =
            JobId.newBuilder()
                .setRandomJob()
                .setLocation(config.datasetLocation.region)
                .setProject(config.jobProjectId)
                .build()

        val formatter: RecordFormatter =
            when (dataChannelFormat) {
                DataChannelFormat.PROTOBUF -> {
                    ProtoToBigQueryStandardInsertRecordFormatter(
                        catalog.getStream(streamDescriptor).airbyteValueProxyFieldAccessors,
                        tableNameInfo.columnNameMapping,
                        catalog.getStream(streamDescriptor),
                        legacyRawTablesOnly = config.legacyRawTablesOnly,
                    )
                }
                else -> {
                    BigQueryRecordFormatter(
                        tableNameInfo.columnNameMapping,
                        legacyRawTablesOnly = config.legacyRawTablesOnly,
                    )
                }
            }

        return BigqueryBatchStandardInsertsLoader(
            jobProjectBigquery,
            writeChannelConfiguration,
            jobId,
            formatter,
        )
    }

    private fun <S> waitForStateStore(
        stateStore: StreamStateStore<S>,
        streamDescriptor: DestinationStream.Descriptor
    ): S {
        // Poll the state store until it's populated by the coordinating StreamLoader thread
        var attempts = 0
        val maxAttempts = 60 * 60 // 1 hour

        while (attempts < maxAttempts) {
            val state = stateStore.get(streamDescriptor)
            if (state != null) {
                return state
            }

            Thread.sleep(1000)
            attempts++
        }

        throw RuntimeException(
            "Timeout waiting for StreamStateStore to be populated for stream $streamDescriptor. This indicates a coordination issue between workers.",
        )
    }

    companion object {
        const val HTTP_STATUS_CODE_FORBIDDEN = 403
        const val HTTP_STATUS_CODE_NOT_FOUND = 404

        val CONFIG_ERROR_MSG =
            """
            |Failed to write to destination schema.
            |   1. Make sure you have all required permissions for writing to the schema.
            |   2. Make sure that the actual destination schema's location corresponds to the location provided in the connector's config.
            |   3. Try to change the "Destination schema" from "Mirror Source Structure" (if it's set) to the "Destination Default" option.
            |More details:
            |""".trimMargin()
    }
}
