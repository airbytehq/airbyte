/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.airbyte.cdk.integrations.debezium.CdcStateHandler
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import org.apache.kafka.connect.errors.ConnectException

private val LOGGER = KotlinLogging.logger {}

class DebeziumMessageProducer<T>(
    private val cdcStateHandler: CdcStateHandler,
    targetPosition: CdcTargetPosition<T>,
    eventConverter: DebeziumEventConverter,
    offsetManager: AirbyteFileOffsetBackingStore?,
    schemaHistoryManager: Optional<AirbyteSchemaHistoryStorage>
) : SourceStateMessageProducer<ChangeEventWithMetadata> {
    /**
     * `checkpointOffsetToSend` is used as temporal storage for the offset that we want to send as
     * message. As Debezium is reading records faster that we process them, if we try to send
     * `offsetManger.read()` offset, it is possible that the state is behind the record we are
     * currently propagating. To avoid that, we store the offset as soon as we reach the checkpoint
     * threshold (time or records) and we wait to send it until we are sure that the record we are
     * processing is behind the offset to be sent.
     */
    private val checkpointOffsetToSend = HashMap<String, String>()

    /**
     * `previousCheckpointOffset` is used to make sure we don't send duplicated states with the same
     * offset. Is it possible that the offset Debezium report doesn't move for a period of time, and
     * if we just rely on the `offsetManger.read()`, there is a chance to sent duplicate states,
     * generating an unneeded usage of networking and processing.
     */
    private val initialOffset: HashMap<String, String>
    private val previousCheckpointOffset: HashMap<String, String>
    private val offsetManager: AirbyteFileOffsetBackingStore?
    private val targetPosition: CdcTargetPosition<T>
    private val schemaHistoryManager: Optional<AirbyteSchemaHistoryStorage>

    private var shouldEmitStateMessage = false

    private val eventConverter: DebeziumEventConverter

    init {
        this.targetPosition = targetPosition
        this.eventConverter = eventConverter
        this.offsetManager = offsetManager
        if (offsetManager == null) {
            throw RuntimeException("Offset manager cannot be null")
        }
        this.schemaHistoryManager = schemaHistoryManager
        this.previousCheckpointOffset = offsetManager.read() as HashMap<String, String>
        this.initialOffset = HashMap(this.previousCheckpointOffset)
    }

    override fun generateStateMessageAtCheckpoint(
        stream: ConfiguredAirbyteStream?
    ): AirbyteStateMessage {
        LOGGER.info { "Sending CDC checkpoint state message." }
        val stateMessage = createStateMessage(checkpointOffsetToSend)
        previousCheckpointOffset.clear()
        previousCheckpointOffset.putAll(checkpointOffsetToSend)
        checkpointOffsetToSend.clear()
        shouldEmitStateMessage = false
        return stateMessage
    }

    /**
     * @param stream
     * @param message
     * @return
     */
    override fun processRecordMessage(
        stream: ConfiguredAirbyteStream?,
        message: ChangeEventWithMetadata
    ): AirbyteMessage {
        if (checkpointOffsetToSend.isEmpty()) {
            try {
                val temporalOffset = offsetManager!!.read()
                if (!targetPosition.isSameOffset(previousCheckpointOffset, temporalOffset)) {
                    checkpointOffsetToSend.putAll(temporalOffset)
                }
            } catch (e: ConnectException) {
                LOGGER.warn {
                    "Offset file is being written by Debezium. Skipping CDC checkpoint in this loop."
                }
            }
        }

        if (checkpointOffsetToSend.size == 1 && !message.isSnapshotEvent) {
            if (targetPosition.isEventAheadOffset(checkpointOffsetToSend, message)) {
                shouldEmitStateMessage = true
            }
        }

        return eventConverter.toAirbyteMessage(message)
    }

    override fun createFinalStateMessage(stream: ConfiguredAirbyteStream?): AirbyteStateMessage {
        val syncFinishedOffset = offsetManager!!.read()
        if (targetPosition.isSameOffset(initialOffset, syncFinishedOffset)) {
            // Edge case where no progress has been made: wrap up the
            // sync by returning the initial offset instead of the
            // current offset. We do this because we found that
            // for some databases, heartbeats will cause Debezium to
            // overwrite the offset file with a state which doesn't
            // include all necessary data such as snapshot completion.
            // This is the case for MS SQL Server, at least.
            return createStateMessage(initialOffset)
        }
        return createStateMessage(syncFinishedOffset)
    }

    override fun shouldEmitStateMessage(stream: ConfiguredAirbyteStream?): Boolean {
        return shouldEmitStateMessage
    }

    /**
     * Creates [AirbyteStateMessage] while updating CDC data, used to checkpoint the state of the
     * process.
     *
     * @return [AirbyteStateMessage] which includes offset and schema history if used.
     */
    private fun createStateMessage(offset: Map<String, String>): AirbyteStateMessage {
        val message =
            cdcStateHandler
                .saveState(
                    offset,
                    schemaHistoryManager
                        .map { obj: AirbyteSchemaHistoryStorage -> obj.read() }
                        .orElse(null)
                )!!
                .state
        return message
    }

    companion object {}
}
