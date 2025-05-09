/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

class BigqueryBatchStandardInsertsLoader(
    private val writer: TableDataWriteChannel,
) : DirectLoader {
    private val recordFormatter = BigQueryRecordFormatter()

    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        // TODO there was a RateLimiter here for some reason...?
        val formattedRecord = recordFormatter.formatRecord(record)
        val byteArray =
            "$formattedRecord${System.lineSeparator()}".toByteArray(StandardCharsets.UTF_8)
        writer.write(ByteBuffer.wrap(byteArray))
        return DirectLoader.Incomplete
    }

    override fun finish() {
        writer.close()
        BigQueryUtils.waitForJobFinish(writer.job)
    }

    override fun close() {
        if (writer.isOpen) {
            writer.close()
        }
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
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : DirectLoaderFactory<BigqueryBatchStandardInsertsLoader> {
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int,
    ): BigqueryBatchStandardInsertsLoader {
        val tableName = streamStateStore.get(streamDescriptor)!!.tableName
        val writeChannelConfiguration =
            WriteChannelConfiguration.newBuilder(TableId.of(tableName.namespace, tableName.name))
                .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                .setSchema(BigQueryRecordFormatter.SCHEMA_V2)
                .setFormatOptions(FormatOptions.json())
                .build() // new-line delimited json.

        val job =
            JobId.newBuilder()
                .setRandomJob()
                .setLocation(config.datasetLocation.region)
                .setProject(bigquery.options.projectId)
                .build()

        val writer =
            try {
                bigquery.writer(job, writeChannelConfiguration)
            } catch (e: BigQueryException) {
                if (e.code == HTTP_STATUS_CODE_FORBIDDEN || e.code == HTTP_STATUS_CODE_NOT_FOUND) {
                    throw ConfigErrorException(CONFIG_ERROR_MSG + e)
                } else {
                    throw BigQueryException(e.code, e.message)
                }
            }

        return BigqueryBatchStandardInsertsLoader(writer)
    }

    companion object {
        const val HTTP_STATUS_CODE_FORBIDDEN = 403
        const val HTTP_STATUS_CODE_NOT_FOUND = 404

        val CONFIG_ERROR_MSG =
            """
            |Failed to write to destination schema.
            |   1. Make sure you have all required permissions for writing to the schema.
            |   2. Make sure that the actual destination schema's location corresponds to location provided in connector's config.
            |   3. Try to change the "Destination schema" from "Mirror Source Structure" (if it's set) tp the "Destination Default" option.
            |More details:
            |""".trimMargin()
    }
}
