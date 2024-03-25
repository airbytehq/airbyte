/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.google.common.collect.AbstractIterator
import io.airbyte.cdk.integrations.debezium.CdcStateHandler
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import java.time.Duration
import java.time.OffsetDateTime
import org.apache.kafka.connect.errors.ConnectException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This class encapsulates CDC change events and adds the required functionality to create
 * checkpoints for CDC replications. That way, if the process fails in the middle of a long sync, it
 * will be able to recover for any acknowledged checkpoint in the next syncs.
 */
class DebeziumStateDecoratingIterator<T>(
    private val changeEventIterator: Iterator<ChangeEventWithMetadata>,
    private val cdcStateHandler: CdcStateHandler,
    private val targetPosition: CdcTargetPosition<T>,
    private val eventConverter: DebeziumEventConverter,
    offsetManager: AirbyteFileOffsetBackingStore,
    private val trackSchemaHistory: Boolean,
    private val schemaHistoryManager: AirbyteSchemaHistoryStorage?,
    checkpointDuration: Duration,
    checkpointRecords: Long
) : AbstractIterator<AirbyteMessage?>(), MutableIterator<AirbyteMessage?> {
    private val offsetManager: AirbyteFileOffsetBackingStore? = offsetManager
    private var isSyncFinished = false

    /**
     * These parameters control when a checkpoint message has to be sent in a CDC integration. We
     * can emit a checkpoint when any of the following two conditions are met.
     *
     * 1. The amount of records in the current loop (`SYNC_CHECKPOINT_RECORDS`) is higher than a
     * threshold defined by `SYNC_CHECKPOINT_RECORDS`.
     *
     * 2. Time between checkpoints (`dateTimeLastSync`) is higher than a `Duration` defined at
     * `SYNC_CHECKPOINT_SECONDS`.
     */
    private val syncCheckpointDuration = checkpointDuration
    private val syncCheckpointRecords = checkpointRecords
    private var dateTimeLastSync: OffsetDateTime? = null
    private var recordsLastSync: Long = 0
    private var recordsAllSyncs: Long = 0
    private var sendCheckpointMessage = false

    /**
     * `checkpointOffsetToSend` is used as temporal storage for the offset that we want to send as
     * message. As Debezium is reading records faster that we process them, if we try to send
     * `offsetManger.read()` offset, it is possible that the state is behind the record we are
     * currently propagating. To avoid that, we store the offset as soon as we reach the checkpoint
     * threshold (time or records) and we wait to send it until we are sure that the record we are
     * processing is behind the offset to be sent.
     */
    private val checkpointOffsetToSend = HashMap<String?, String?>()

    /**
     * `previousCheckpointOffset` is used to make sure we don't send duplicated states with the same
     * offset. Is it possible that the offset Debezium report doesn't move for a period of time, and
     * if we just rely on the `offsetManger.read()`, there is a chance to sent duplicate states,
     * generating an unneeded usage of networking and processing.
     */
    private val initialOffset: HashMap<String?, String?>
    private val previousCheckpointOffset: HashMap<String?, String?>? =
        offsetManager.read() as HashMap<String?, String?>

    /**
     * @param changeEventIterator Base iterator that we want to enrich with checkpoint messages
     * @param cdcStateHandler Handler to save the offset and schema history
     * @param offsetManager Handler to read and write debezium offset file
     * @param eventConverter Handler to transform debezium events into Airbyte messages.
     * @param trackSchemaHistory Set true if the schema needs to be tracked
     * @param schemaHistoryManager Handler to write schema. Needs to be initialized if
     * trackSchemaHistory is set to true
     * @param checkpointDuration Duration object with time between syncs
     * @param checkpointRecords Number of records between syncs
     */
    init {
        this.initialOffset = HashMap(this.previousCheckpointOffset)
        resetCheckpointValues()
    }

    /**
     * Computes the next record retrieved from Source stream. Emits state messages as checkpoints
     * based on number of records or time lapsed.
     *
     * If this method throws an exception, it will propagate outward to the `hasNext` or `next`
     * invocation that invoked this method. Any further attempts to use the iterator will result in
     * an [IllegalStateException].
     *
     * @return [AirbyteStateMessage] containing CDC data or state checkpoint message.
     */
    override fun computeNext(): AirbyteMessage? {
        if (isSyncFinished) {
            return endOfData()
        }

        if (cdcStateHandler.isCdcCheckpointEnabled && sendCheckpointMessage) {
            LOGGER.info("Sending CDC checkpoint state message.")
            val stateMessage = createStateMessage(checkpointOffsetToSend, recordsLastSync)
            previousCheckpointOffset!!.clear()
            previousCheckpointOffset.putAll(checkpointOffsetToSend)
            resetCheckpointValues()
            return stateMessage
        }

        if (changeEventIterator.hasNext()) {
            val event = changeEventIterator.next()

            if (cdcStateHandler.isCdcCheckpointEnabled) {
                if (
                    checkpointOffsetToSend.isEmpty() &&
                        (recordsLastSync >= syncCheckpointRecords ||
                            Duration.between(dateTimeLastSync, OffsetDateTime.now())
                                .compareTo(syncCheckpointDuration) > 0)
                ) {
                    // Using temporal variable to avoid reading teh offset twice, one in the
                    // condition and another in
                    // the assignation
                    try {
                        val temporalOffset = offsetManager!!.read() as HashMap<String?, String?>
                        if (
                            !targetPosition.isSameOffset(previousCheckpointOffset, temporalOffset)
                        ) {
                            checkpointOffsetToSend.putAll(temporalOffset)
                        }
                    } catch (e: ConnectException) {
                        LOGGER.warn(
                            "Offset file is being written by Debezium. Skipping CDC checkpoint in this loop."
                        )
                    }
                }

                if (
                    checkpointOffsetToSend.size == 1 &&
                        changeEventIterator.hasNext() &&
                        !event.isSnapshotEvent
                ) {
                    if (targetPosition.isEventAheadOffset(checkpointOffsetToSend, event)) {
                        sendCheckpointMessage = true
                    } else {
                        LOGGER.info(
                            "Encountered {} records with the same event offset",
                            recordsLastSync
                        )
                    }
                }
            }
            recordsLastSync++
            recordsAllSyncs++
            return eventConverter.toAirbyteMessage(event)
        }

        isSyncFinished = true
        val syncFinishedOffset = offsetManager!!.read() as HashMap<String?, String?>
        if (
            recordsAllSyncs == 0L && targetPosition.isSameOffset(initialOffset, syncFinishedOffset)
        ) {
            // Edge case where no progress has been made: wrap up the
            // sync by returning the initial offset instead of the
            // current offset. We do this because we found that
            // for some databases, heartbeats will cause Debezium to
            // overwrite the offset file with a state which doesn't
            // include all necessary data such as snapshot completion.
            // This is the case for MS SQL Server, at least.
            return createStateMessage(initialOffset, 0)
        }
        return createStateMessage(syncFinishedOffset, recordsLastSync)
    }

    /** Initialize or reset the checkpoint variables. */
    private fun resetCheckpointValues() {
        sendCheckpointMessage = false
        checkpointOffsetToSend.clear()
        recordsLastSync = 0L
        dateTimeLastSync = OffsetDateTime.now()
    }

    /**
     * Creates [AirbyteStateMessage] while updating CDC data, used to checkpoint the state of the
     * process.
     *
     * @return [AirbyteStateMessage] which includes offset and schema history if used.
     */
    private fun createStateMessage(
        offset: Map<String?, String?>?,
        recordCount: Long
    ): AirbyteMessage? {
        if (trackSchemaHistory && schemaHistoryManager == null) {
            throw RuntimeException("Schema History Tracking is true but manager is not initialised")
        }
        if (offsetManager == null) {
            throw RuntimeException("Offset can not be null")
        }

        val message = cdcStateHandler.saveState(offset, schemaHistoryManager?.read())
        message!!.state.withSourceStats(AirbyteStateStats().withRecordCount(recordCount.toDouble()))
        return message
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(DebeziumStateDecoratingIterator::class.java)
    }
}
