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
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.operation.BigQueryDirectLoadingStorageOperation.Companion.CONFIG_ERROR_MSG
import io.airbyte.integrations.destination.bigquery.operation.BigQueryDirectLoadingStorageOperation.Companion.HTTP_STATUS_CODE_FORBIDDEN
import io.airbyte.integrations.destination.bigquery.operation.BigQueryDirectLoadingStorageOperation.Companion.HTTP_STATUS_CODE_NOT_FOUND
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import jakarta.inject.Singleton
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

class BigqueryDirectLoader(
    private val writer: TableDataWriteChannel,
) : DirectLoader {
    private val recordFormatter = BigQueryRecordFormatter()

    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
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
        // do nothing
    }
}

@Singleton
class BigqueryDirectLoaderFactory(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
) : DirectLoaderFactory<BigqueryDirectLoader> {
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): BigqueryDirectLoader {
        // TODO there was a RateLimiter here for some reason...?
        // TODO we need to handle special chars in stream name/namespace
        val writeChannelConfiguration =
            WriteChannelConfiguration.newBuilder(
                    TableId.of(streamDescriptor.namespace, streamDescriptor.name)
                )
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

        return BigqueryDirectLoader(writer)
    }
}
