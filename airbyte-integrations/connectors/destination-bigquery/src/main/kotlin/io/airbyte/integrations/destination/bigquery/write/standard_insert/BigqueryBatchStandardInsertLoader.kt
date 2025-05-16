/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoaderFactory.Companion.CONFIG_ERROR_MSG
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoaderFactory.Companion.HTTP_STATUS_CODE_FORBIDDEN
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoaderFactory.Companion.HTTP_STATUS_CODE_NOT_FOUND
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

class BigqueryBatchStandardInsertsLoader(
    private val bigquery: BigQuery,
    private val writeChannelConfiguration: WriteChannelConfiguration,
    private val job: JobId,
    private val recordFormatter: BigQueryRecordFormatter,
) : DirectLoader {
    private val buffer = ByteArrayOutputStream()

    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        // TODO there was a RateLimiter here for some reason...?
        val formattedRecord = recordFormatter.formatRecord(record)
        val byteArray =
            "$formattedRecord${System.lineSeparator()}".toByteArray(StandardCharsets.UTF_8)
        buffer.write(byteArray)
        // the default chunk size on the TableDataWriteChannel is 15MB,
        // so just terminate when we get there.
        if (buffer.size() > 15 * 1024 * 1024) {
            finish()
            return DirectLoader.Complete
        } else {
            return DirectLoader.Incomplete
        }
    }

    override fun finish() {
        // this object holds a 15MB buffer in memory.
        // we shouldn't initialize that until we actually need it,
        // so just do it in finish.
        // this minimizes the time we're occupying that chunk of memory.
        val writer: TableDataWriteChannel =
            try {
                bigquery.writer(job, writeChannelConfiguration)
            } catch (e: BigQueryException) {
                if (e.code == HTTP_STATUS_CODE_FORBIDDEN || e.code == HTTP_STATUS_CODE_NOT_FOUND) {
                    throw ConfigErrorException(CONFIG_ERROR_MSG + e)
                } else {
                    throw BigQueryException(e.code, e.message)
                }
            }
        writer.use { writer.write(ByteBuffer.wrap(buffer.toByteArray())) }
        BigQueryUtils.waitForJobFinish(writer.job)
    }

    override fun close() {}
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
            val rawTableSuffix =
                typingDedupingStreamStateStore!!.get(streamDescriptor)!!.rawTableSuffix
            tableId = TableId.of(rawTableName.namespace, rawTableName.name + rawTableSuffix)
            schema = BigQueryRecordFormatter.SCHEMA_V2
        } else {
            tableId = directLoadStreamStateStore!!.get(streamDescriptor)!!.tableName.toTableId()
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

        return BigqueryBatchStandardInsertsLoader(
            bigquery,
            writeChannelConfiguration,
            jobId,
            BigQueryRecordFormatter(legacyRawTablesOnly = config.legacyRawTablesOnly),
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
