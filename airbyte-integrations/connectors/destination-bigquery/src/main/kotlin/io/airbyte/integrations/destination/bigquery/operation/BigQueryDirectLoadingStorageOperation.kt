/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.operation

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import com.google.common.util.concurrent.RateLimiter
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.SCHEMA_V2
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.util.stream.Stream

private val log = KotlinLogging.logger {}

class BigQueryDirectLoadingStorageOperation(
    bigquery: BigQuery,
    private val bigQueryClientChunkSize: Int?,
    private val bigQueryRecordFormatter: BigQueryRecordFormatter,
    sqlGenerator: BigQuerySqlGenerator,
    destinationHandler: BigQueryDestinationHandler,
    datasetLocation: String
) :
    BigQueryStorageOperation<Stream<PartialAirbyteMessage>>(
        bigquery,
        sqlGenerator,
        destinationHandler,
        datasetLocation,
    ) {
    private val rateLimiter: RateLimiter = RateLimiter.create(0.07)
    companion object {
        private const val HTTP_STATUS_CODE_FORBIDDEN = 403
        private const val HTTP_STATUS_CODE_NOT_FOUND = 404

        private val CONFIG_ERROR_MSG =
            """
            |Failed to write to destination schema.
            |   1. Make sure you have all required permissions for writing to the schema.
            |   2. Make sure that the actual destination schema's location corresponds to location provided in connector's config.
            |   3. Try to change the "Destination schema" from "Mirror Source Structure" (if it's set) tp the "Destination Default" option.
            |More details:
            |""".trimMargin()
    }
    override fun writeToStage(streamId: StreamId, data: Stream<PartialAirbyteMessage>) {
        // TODO: why do we need ratelimiter, and using unstable API from Google's guava
        rateLimiter.acquire()
        val tableId = TableId.of(streamId.rawNamespace, streamId.rawName)
        log.info { "Writing data to table $tableId with schema $SCHEMA_V2" }
        val writeChannel = initWriteChannel(tableId)
        writeChannel.use {
            data.forEach { record ->
                val byteArray =
                    "${bigQueryRecordFormatter.formatRecord(record)} ${System.lineSeparator()}".toByteArray(
                        StandardCharsets.UTF_8,
                    )
                it.write(ByteBuffer.wrap(byteArray))
            }
        }
        log.info { "Writing to channel completed for $tableId" }
        val job = writeChannel.job
        BigQueryUtils.waitForJobFinish(job)
    }

    private fun initWriteChannel(tableId: TableId): TableDataWriteChannel {
        val writeChannelConfiguration =
            WriteChannelConfiguration.newBuilder(tableId)
                .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                .setSchema(SCHEMA_V2)
                .setFormatOptions(FormatOptions.json())
                .build() // new-line delimited json.

        val job =
            JobId.newBuilder()
                .setRandomJob()
                .setLocation(datasetLocation)
                .setProject(bigquery.options.projectId)
                .build()

        val writer: TableDataWriteChannel

        try {
            writer = bigquery.writer(job, writeChannelConfiguration)
        } catch (e: BigQueryException) {
            if (e.code == HTTP_STATUS_CODE_FORBIDDEN || e.code == HTTP_STATUS_CODE_NOT_FOUND) {
                throw ConfigErrorException(CONFIG_ERROR_MSG + e)
            } else {
                throw BigQueryException(e.code, e.message)
            }
        }

        // this this optional value. If not set - use default client's value (15MiG)
        if (bigQueryClientChunkSize != null) {
            writer.setChunkSize(bigQueryClientChunkSize)
        }
        return writer
    }
}
