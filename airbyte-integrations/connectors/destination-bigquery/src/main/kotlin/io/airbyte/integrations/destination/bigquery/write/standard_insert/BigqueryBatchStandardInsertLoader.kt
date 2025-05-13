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
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.airbyte.cdk.load.write.db.InsertLoaderRequestBuilder
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

// the default chunk size on the TableDataWriteChannel is 15MB.
private const val DEFAULT_CHUNK_SIZE: Long = 15 * 1024 * 1024

class BigqueryStandardInsertsRequest(
    private val baos: ByteArrayOutputStream,
    // TableDataWriteChannel holds a 15MB buffer in memory,
    // so we try to avoid instantiating it for as long as possible.
    // so accept it as a supplier here, and don't invoke the supplier
    // until the CDK tells us we're ready to actually submit the request.
    private val tableWriteChannelSupplier: () -> TableDataWriteChannel,
) : InsertLoaderRequest {
    override suspend fun submit() {
        val writer = tableWriteChannelSupplier()
        writer.use { writer.write(ByteBuffer.wrap(baos.toByteArray())) }
        BigQueryUtils.waitForJobFinish(writer.job)
    }
}

class BigqueryStandardInsertsRequestBuilder(
    private val bigquery: BigQuery,
    private val writeChannelConfiguration: WriteChannelConfiguration,
    private val job: JobId,
) : InsertLoaderRequestBuilder<BigqueryStandardInsertsRequest> {
    private val recordFormatter = BigQueryRecordFormatter()
    private val baos = ByteArrayOutputStream()

    override fun accept(
        record: DestinationRecordRaw,
        maxRequestSizeBytes: Long
    ): InsertLoaderRequestBuilder.InsertAcceptResult<BigqueryStandardInsertsRequest> {
        val formattedRecord = recordFormatter.formatRecord(record)
        val byteArray =
            "$formattedRecord${System.lineSeparator()}".toByteArray(StandardCharsets.UTF_8)
        baos.write(byteArray)
        return if (baos.size() > maxRequestSizeBytes) {
            finish()
        } else {
            InsertLoaderRequestBuilder.NoOutput()
        }
    }

    override fun finish(): InsertLoaderRequestBuilder.Request<BigqueryStandardInsertsRequest> {
        return InsertLoaderRequestBuilder.Request(
            BigqueryStandardInsertsRequest(baos) {
                try {
                    bigquery.writer(job, writeChannelConfiguration)
                } catch (e: BigQueryException) {
                    if (
                        e.code == HTTP_STATUS_CODE_FORBIDDEN || e.code == HTTP_STATUS_CODE_NOT_FOUND
                    ) {
                        throw ConfigErrorException(CONFIG_ERROR_MSG + e)
                    } else {
                        throw BigQueryException(e.code, e.message)
                    }
                }
            }
        )
    }

    override fun close() {
        // do nothing
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

class BigqueryConfiguredForBatchStandardInserts : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(BigqueryConfiguration::class.java)
        return config.loadingMethod is BatchedStandardInsertConfiguration
    }
}

@Requires(condition = BigqueryConfiguredForBatchStandardInserts::class)
@Singleton
class BigqueryBatchStandardInsertsLoader(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val names: TableCatalogByDescriptor,
    private val streamStateStore: StreamStateStore<TypingDedupingExecutionConfig>,
) : InsertLoader<BigqueryStandardInsertsRequest> {
    override val estimatedByteSizePerRequest: Long = DEFAULT_CHUNK_SIZE

    override fun createAccumulator(
        streamDescriptor: DestinationStream.Descriptor,
        partition: Int,
    ): InsertLoaderRequestBuilder<BigqueryStandardInsertsRequest> {
        val rawTableName = names[streamDescriptor]!!.tableNames.rawTableName!!
        val rawTableNameSuffix = streamStateStore.get(streamDescriptor)!!.rawTableSuffix

        val writeChannelConfiguration =
            WriteChannelConfiguration.newBuilder(
                    TableId.of(rawTableName.namespace, rawTableName.name + rawTableNameSuffix)
                )
                .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                .setSchema(BigQueryRecordFormatter.SCHEMA_V2)
                // new-line delimited json.
                .setFormatOptions(FormatOptions.json())
                .build()

        val jobId =
            JobId.newBuilder()
                .setRandomJob()
                .setLocation(config.datasetLocation.region)
                .setProject(bigquery.options.projectId)
                .build()

        return BigqueryStandardInsertsRequestBuilder(
            bigquery,
            writeChannelConfiguration,
            jobId,
        )
    }
}
