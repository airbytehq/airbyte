/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
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
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

private val logger = KotlinLogging.logger {}

interface RecordFormatter {
    fun formatRecord(record: DestinationRecordRaw): String
}

class BigqueryBatchStandardInsertsLoader(
    private val bigquery: BigQuery,
    private val writeChannelConfiguration: WriteChannelConfiguration,
    private val job: JobId,
    private val recordFormatter: RecordFormatter,
) : DirectLoader {
    // a TableDataWriteChannel holds (by default) a 15MB buffer in memory.
    // so we start out by writing to a BAOS, which grows dynamically.
    // when the BAOS reaches 15MB, we create the TableDataWriteChannel and switch over
    // to writing to the writechannel directly.
    // invariant: either the buffer is nonnull, or the writer is initialized. They are never both
    // active at the same time.
    // bigquery sets daily limits on how many TableDataWriteChannel jobs you can run,
    // so we can't just flush+close a TableDataWriteChannel as soon as we reach 15MB.
    private var buffer: ByteArrayOutputStream? = ByteArrayOutputStream()
    private lateinit var writer: TableDataWriteChannel

    @SuppressFBWarnings("RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE")
    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val formattedRecord = recordFormatter.formatRecord(record)
        val byteArray =
            "$formattedRecord${System.lineSeparator()}".toByteArray(StandardCharsets.UTF_8)

        if (this::writer.isInitialized) {
            writer.write(ByteBuffer.wrap(byteArray))
        } else {
            buffer!!.write(byteArray)
            // the default chunk size on the TableDataWriteChannel is 15MB,
            // so switch to writing to a real writechannel when we reach that size
            if (buffer!!.size() > 15 * 1024 * 1024) {
                switchToWriteChannel()
            }
        }

        // rely on the CDK to tell us when to finish()
        return DirectLoader.Incomplete
    }

    override suspend fun finish() {
        if (!this::writer.isInitialized) {
            switchToWriteChannel()
        }
        writer.close()
        BigQueryUtils.waitForJobFinish(writer.job)
        val stats = writer.job.reload().getStatistics<JobStatistics.LoadStatistics>()
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

    override fun close() {}

    // Somehow spotbugs thinks that `writer.write(ByteBuffer.wrap(byteArray))` is a redundant null
    // check...
    @SuppressFBWarnings(value = ["RCN_REDUNDANT_NULLCHECK_WOULD_HAVE_BEEN_A_NPE"])
    private fun switchToWriteChannel() {
        writer =
            try {
                bigquery.writer(job, writeChannelConfiguration)
            } catch (e: BigQueryException) {
                if (e.code == HTTP_STATUS_CODE_FORBIDDEN || e.code == HTTP_STATUS_CODE_NOT_FOUND) {
                    throw ConfigErrorException(CONFIG_ERROR_MSG + e)
                } else {
                    throw BigQueryException(e.code, e.message)
                }
            }
        val byteArray = buffer!!.toByteArray()
        // please GC this object :)
        buffer = null
        writer.write(ByteBuffer.wrap(byteArray))
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
    private val bigquery: BigQuery,
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
            tableId = TableId.of(rawTableName.namespace, rawTableName.name + rawTableSuffix)
            schema = BigQueryRecordFormatter.SCHEMA_V2
        } else {
            // Wait for the state store to be populated by the coordinating StreamLoader
            val executionConfig = waitForStateStore(directLoadStreamStateStore!!, streamDescriptor)
            tableId = executionConfig.tableName.toTableId()
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
                .setProject(bigquery.options.projectId)
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
            bigquery,
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
