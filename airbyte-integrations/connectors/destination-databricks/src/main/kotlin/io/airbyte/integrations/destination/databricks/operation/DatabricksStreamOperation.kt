/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.operation

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.staging.DatabricksFileBufferFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream
import org.apache.commons.io.FileUtils

/**
 * This is almost identical to
 * [io.airbyte.cdk.integrations.destination.staging.operation.StagingStreamOperations] only
 * difference being the BufferFactory used.
 */
class DatabricksStreamOperation(
    private val storageOperation: StorageOperation<SerializableBuffer>,
    destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>,
    private val fileUploadFormat: FileUploadFormat,
) :
    AbstractStreamOperation<MinimumDestinationState.Impl, SerializableBuffer>(
        storageOperation,
        destinationInitialStatus,
    ) {
    private val log = KotlinLogging.logger {}
    override fun writeRecords(streamConfig: StreamConfig, stream: Stream<PartialAirbyteMessage>) {
        val writeBuffer = DatabricksFileBufferFactory.createBuffer(fileUploadFormat)
        writeBuffer.use {
            stream.forEach { record: PartialAirbyteMessage ->
                it.accept(
                    record.serialized!!,
                    Jsons.serialize(record.record!!.meta),
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
            storageOperation.writeToStage(streamConfig.id, writeBuffer)
        }
    }
}
