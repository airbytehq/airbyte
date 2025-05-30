/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.operation

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.staging.DatabricksFileBufferFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream
import org.apache.commons.io.FileUtils
import org.jetbrains.annotations.VisibleForTesting

private val log = KotlinLogging.logger {}

/**
 * This is almost identical to
 * [io.airbyte.cdk.integrations.destination.staging.operation.StagingStreamOperations] only
 * difference being the BufferFactory used.
 */
class DatabricksStreamOperation(
    private val storageOperation: DatabricksStorageOperation,
    destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>,
    private val fileUploadFormat: FileUploadFormat,
    disableTypeDedupe: Boolean,
) :
    AbstractStreamOperation<MinimumDestinationState.Impl, SerializableBuffer>(
        storageOperation,
        destinationInitialStatus,
        disableTypeDedupe = disableTypeDedupe
    ) {
    override fun writeRecordsImpl(
        streamConfig: StreamConfig,
        suffix: String,
        stream: Stream<PartialAirbyteMessage>
    ) {
        writeRecords(fileUploadFormat, streamConfig, suffix, stream, storageOperation)
    }

    companion object {
        /**
         * In tests, we don't necessarily want to instantiate an actual instance of this class
         * because we don't want to run all the setup logic that the constructor includes. So we
         * expose this method for direct use.
         */
        @VisibleForTesting
        fun writeRecords(
            fileUploadFormat: FileUploadFormat,
            streamConfig: StreamConfig,
            suffix: String,
            stream: Stream<PartialAirbyteMessage>,
            storageOperation: DatabricksStorageOperation,
        ) {
            val writeBuffer = DatabricksFileBufferFactory.createBuffer(fileUploadFormat)
            writeBuffer.use {
                stream.forEach { record: PartialAirbyteMessage ->
                    it.accept(
                        record.serialized!!,
                        Jsons.serialize(record.record!!.meta),
                        streamConfig.generationId,
                        record.record!!.emittedAt,
                    )
                }
                it.flush()
                log.info {
                    "Buffer flush complete for stream ${streamConfig.id.originalName} (${
                        FileUtils.byteCountToDisplaySize(
                            it.byteCount,
                        )
                    }) to staging"
                }
                // You might expect that if we write 0 records to the buffer,
                // we end up with a CSV file containing just the header.
                // But in fact, we end up with an empty file,
                // so checking for 0 bytes is a valid way to detect this case.
                // (and of course, we're using a Stream<message>,
                // so checking for nonzero records _before_ we create the buffer
                // is a royal pain)
                if (it.byteCount != 0L) {
                    storageOperation.writeToStage(streamConfig, suffix, writeBuffer)
                } else {
                    log.info { "Skipping writing to storage since there are no bytes to write" }
                }
            }
        }
    }
}
