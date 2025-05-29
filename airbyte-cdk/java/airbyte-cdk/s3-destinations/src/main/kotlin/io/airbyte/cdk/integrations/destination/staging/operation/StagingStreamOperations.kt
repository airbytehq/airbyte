/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.staging.operation

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.staging.StagingSerializedBufferFactory
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream
import org.apache.commons.io.FileUtils

class StagingStreamOperations<DestinationState : MinimumDestinationState>(
    private val storageOperation: StorageOperation<SerializableBuffer>,
    destinationInitialStatus: DestinationInitialStatus<DestinationState>,
    private val fileUploadFormat: FileUploadFormat,
    private val destinationColumns: JavaBaseConstants.DestinationColumns,
    disableTypeDedupe: Boolean = false
) :
    AbstractStreamOperation<DestinationState, SerializableBuffer>(
        storageOperation,
        destinationInitialStatus,
        disableTypeDedupe
    ) {

    private val log = KotlinLogging.logger {}
    override fun writeRecordsImpl(
        streamConfig: StreamConfig,
        suffix: String,
        stream: Stream<PartialAirbyteMessage>
    ) {
        val writeBuffer =
            StagingSerializedBufferFactory.initializeBuffer(fileUploadFormat, destinationColumns)

        writeBuffer.use {
            stream.forEach { record: PartialAirbyteMessage ->
                it.accept(
                    record.serialized!!,
                    Jsons.serialize(record.record!!.meta),
                    streamConfig.generationId,
                    record.record!!.emittedAt
                )
            }
            it.flush()
            log.info {
                "Buffer flush complete for stream ${streamConfig.id.originalName} (${FileUtils.byteCountToDisplaySize(it.byteCount)}) to staging"
            }
            if (it.byteCount != 0L) {
                storageOperation.writeToStage(streamConfig, suffix, writeBuffer)
            } else {
                log.info { "Skipping writing to storage since there are no bytes to write" }
            }
        }
    }
}
